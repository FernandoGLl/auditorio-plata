import os, oracledb

pool = oracledb.create_pool(
    user=os.getenv("DB_USER", "system"),
    password=os.getenv("DB_PASSWORD", "Cambia-esto"),
    dsn=os.getenv("DB_DSN", "localhost:1521/FREEPDB1"),
    min=4, max=20, increment=2,
)