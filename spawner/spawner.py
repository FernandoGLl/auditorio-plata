import argparse, threading, queue, time, random, csv, os, requests

p = argparse.ArgumentParser()
p.add_argument("--url", default="http://localhost:8000")
p.add_argument("--modo", default="seguro", choices=["seguro", "inseguro"])
p.add_argument("--total", type=int, default=100)
p.add_argument("--hilos", type=int, default=20)
p.add_argument("--ventana", type=float, default=60)
p.add_argument("--simultaneas", type=int, default=10)
p.add_argument("--patron", default="uniforme", choices=["uniforme", "aleatorio", "rafagas"])
a = p.parse_args()

# Instante programado (en segundos desde el arranque) de cada solicitud
if a.patron == "uniforme":
    horarios = [j * a.ventana / a.total for j in range(a.total)]
elif a.patron == "aleatorio":
    horarios = sorted(random.uniform(0, a.ventana) for _ in range(a.total))
else:  # ráfagas de 10 solicitudes
    n_raf = max(1, a.total // 10)
    horarios = [(j // 10) * a.ventana / n_raf for j in range(a.total)]

t0 = [0.0]
barrera = threading.Barrier(a.hilos, action=lambda: t0.__setitem__(0, time.time()))
sem = threading.Semaphore(a.simultaneas)
cola = queue.Queue()
lock = threading.Lock()
stats = {"EXITO": 0, "RECHAZO": 0, "ERROR": 0}
tiempos = []

def spawner(k):
    barrera.wait()                                    # BARRERA
    for j in range(k, a.total, a.hilos):
        espera = t0[0] + horarios[j] - time.time()    # control de tasa
        if espera > 0:
            time.sleep(espera)
        with sem:                                     # SEMÁFORO
            envio = time.time()
            folio, estado, pdf = None, "ERROR", None
            try:
                r = requests.post(f"{a.url}/boleto", params={"modo": a.modo}, timeout=10)
                if r.status_code == 200:
                    folio, estado = r.json()["folio"], "EXITO"
                    if a.modo == "seguro":
                        pdf = requests.get(a.url + r.json()["pdf"], timeout=10).content
                elif r.status_code == 409:
                    estado = "RECHAZO"
            except requests.RequestException:
                estado = "ERROR"                      # no detiene al hilo
            resp = time.time()
        with lock:                                    # MUTEX
            stats[estado] += 1
            tiempos.append(resp - envio)
        cola.put((threading.current_thread().name, envio, resp, folio, estado, pdf))  # PRODUCTOR

def consumidor():                                     # CONSUMIDOR
    with open(f"bitacora_{a.modo}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["hilo", "envio", "respuesta", "folio", "estado"])
        while True:
            item = cola.get()
            if item is None:
                break
            hilo, e, r, folio, estado, pdf = item
            w.writerow([hilo, e, r, folio, estado])
            if pdf:
                with open(f"boletos/boleto_{folio}.pdf", "wb") as g:
                    g.write(pdf)

if __name__ == "__main__":
    os.makedirs("boletos", exist_ok=True)
    c = threading.Thread(target=consumidor)
    c.start()
    hilos = [threading.Thread(target=spawner, args=(k,), name=f"spawner-{k}") for k in range(a.hilos)]
    ini = time.time()
    for h in hilos: h.start()
    for h in hilos: h.join()
    cola.put(None)
    c.join()
    dur = time.time() - ini
    prom = sum(tiempos) / len(tiempos) if tiempos else 0
    print(f"Duración: {dur:.1f}s | {stats} | {stats['EXITO']/dur:.2f} boletos/s | "
          f"respuesta promedio: {prom*1000:.0f} ms")
    print("Meta 100 en 60s:", "CUMPLIDA" if stats["EXITO"] >= 100 and dur <= 60 else "NO cumplida")