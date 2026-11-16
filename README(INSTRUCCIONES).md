# auditorio-plata
Repositorio para servidor y spawner

# Auditorio Plata - Boletos gratuitos

Aplicación web que emite boletos PDF con QR (folio, fecha y hora) para el
"Concierto Navideño" (aforo 20,000), con un spawner concurrente para pruebas.

**URL:** https://TU-URL-PUBLICA

## Requisitos
Python 3.10+, Docker Desktop, Git

## Instalación
1. Base de datos:
   docker run -d --name oracle-free -p 1521:1521 -e ORACLE_PWD=TU_CLAVE container-registry.oracle.com/database/free:latest
   (esperar "DATABASE IS READY TO USE!" en `docker logs oracle-free`)
2. Crear tablas:
   docker cp sql/schema.sql oracle-free:/tmp/schema.sql
   docker exec -it oracle-free sqlplus system/TU_CLAVE@//localhost:1521/FREEPDB1 "@/tmp/schema.sql"
3. Servidor:
   cd servidor; python -m venv venv; venv\Scripts\activate; pip install -r requirements.txt
   $env:DB_USER="system"; $env:DB_PASSWORD="TU_CLAVE"; $env:DB_DSN="localhost:1521/FREEPDB1"
   uvicorn main:app --port 8000
4. Spawner:
   cd spawner; python -m venv venv; venv\Scripts\activate; pip install -r requirements.txt
   python spawner.py --url http://localhost:8000 --total 100 --ventana 55

## Opciones del spawner
--modo seguro|inseguro, --total, --hilos, --ventana, --simultaneas,
--patron uniforme|aleatorio|rafagas, --sinpdf, --limpiar

## Estructura
servidor/ (API y página), spawner/ (cliente concurrente), sql/ (scripts), docs/ (diagramas, reporte, evidencia)
