import os, io, time, hmac, hashlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from db import pool
from pdf_utils import generar_pdf

SECRET = os.getenv("SECRET", "cambia-esto").encode()
app = FastAPI(title="Auditorio Plata")

def firmar(folio: int) -> str:
    return hmac.new(SECRET, str(folio).encode(), hashlib.sha256).hexdigest()

@app.post("/boleto")
def pedir_boleto(modo: str = "seguro"):
    conn = pool.acquire()
    try:
        cur = conn.cursor()
        if modo == "inseguro":
            # SIN sincronización: leer -> pensar -> escribir (condición de carrera)
            cur.execute("SELECT NVL(MAX(folio),0) FROM boletos_inseguro")
            folio = cur.fetchone()[0] + 1
            cur.execute("SELECT aforo, boletos_emitidos FROM eventos_inseguro WHERE id_evento=1")
            aforo, emitidos = cur.fetchone()
            time.sleep(0.01)  # amplifica la ventana de la carrera
            if emitidos >= aforo:
                raise HTTPException(409, "Aforo lleno")
            cur.execute("INSERT INTO boletos_inseguro(folio,id_evento) VALUES(:1,1)", [folio])
            cur.execute("UPDATE eventos_inseguro SET boletos_emitidos=:1 WHERE id_evento=1", [emitidos + 1])
            conn.commit()
            return {"folio": folio}
        # CON sincronización: bloqueo de fila + secuencia + transacción
        cur.execute("SELECT aforo, boletos_emitidos FROM eventos WHERE id_evento=1 FOR UPDATE")
        aforo, emitidos = cur.fetchone()
        if emitidos >= aforo:
            conn.rollback()
            raise HTTPException(409, "Aforo lleno")
        cur.execute("SELECT seq_folio.NEXTVAL FROM dual")
        folio = cur.fetchone()[0]
        cur.execute("INSERT INTO boletos(folio,id_evento,hash_firma) VALUES(:1,1,:2)",
                    [folio, firmar(folio)])
        cur.execute("UPDATE eventos SET boletos_emitidos = boletos_emitidos + 1 WHERE id_evento=1")
        conn.commit()
        return {"folio": folio, "pdf": f"/boleto/{folio}/pdf"}
    finally:
        pool.release(conn)

@app.get("/boleto/{folio}/pdf")
def descargar_pdf(folio: int):
    with pool.acquire() as conn:
        cur = conn.cursor()
        cur.execute("SELECT fecha_emision, hash_firma FROM boletos WHERE folio=:1", [folio])
        fila = cur.fetchone()
    if not fila:
        raise HTTPException(404, "Boleto no existe")
    pdf = generar_pdf(folio, fila[0], fila[1])
    return StreamingResponse(io.BytesIO(pdf), media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="boleto_{folio}.pdf"'})

@app.get("/estado")
def estado():
    with pool.acquire() as conn:
        cur = conn.cursor()
        cur.execute("SELECT aforo, boletos_emitidos FROM eventos WHERE id_evento=1")
        aforo, emitidos = cur.fetchone()
    return {"aforo": aforo, "emitidos": emitidos, "restantes": aforo - emitidos}

@app.get("/validar/{folio}")
def validar(folio: int):
    with pool.acquire() as conn:
        cur = conn.cursor()
        cur.execute("SELECT fecha_emision, hash_firma FROM boletos WHERE folio=:1", [folio])
        fila = cur.fetchone()
    if not fila:
        return {"valido": False, "folio": folio}
    ok = hmac.compare_digest(firmar(folio), fila[1])
    return {"valido": ok, "folio": folio, "fecha": fila[0].strftime("%Y-%m-%d %H:%M:%S")}

# La página web (debe ir al final, después de las rutas de la API)
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"),
                           html=True), name="static")