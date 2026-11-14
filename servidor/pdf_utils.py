import io, qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def generar_pdf(folio, fecha, firma) -> bytes:
    texto = (f"AUDITORIO PLATA|folio={folio}|fecha={fecha:%Y-%m-%d}"
             f"|hora={fecha:%H:%M:%S}|sig={firma[:16]}")
    img = qrcode.make(texto)
    qr_buf = io.BytesIO()
    img.save(qr_buf, format="PNG")
    qr_buf.seek(0)

    out = io.BytesIO()
    c = canvas.Canvas(out)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(60, 790, "Auditorio Plata")
    c.setFont("Helvetica", 14)
    c.drawString(60, 760, "Concierto Navideño")
    c.drawString(60, 735, f"Folio: {folio:06d}")
    c.drawString(60, 710, f"Emitido: {fecha:%Y-%m-%d %H:%M:%S}")
    c.drawImage(ImageReader(qr_buf), 60, 480, 200, 200)
    c.setFont("Helvetica", 9)
    c.drawString(60, 465, "Boleto gratuito. Presenta este QR en la entrada.")
    c.save()
    return out.getvalue()