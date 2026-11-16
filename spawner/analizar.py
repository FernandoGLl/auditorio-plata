import sys, pandas as pd

df = pd.read_csv(sys.argv[1])
df["ms"] = (df["respuesta"] - df["envio"]) * 1000
duracion = df["respuesta"].max() - df["envio"].min()
exitos = (df["estado"] == "EXITO").sum()

print(df["estado"].value_counts().to_string())
print(f"Duración total: {duracion:.1f} s")
print(f"Boletos por segundo: {exitos / duracion:.2f}")
print(f"Tiempo de respuesta promedio: {df['ms'].mean():.0f} ms")
print(f"Máximo: {df['ms'].max():.0f} ms")
print(f"Folios duplicados: {df['folio'].dropna().duplicated().sum()}")
print("Meta 100 en 60 s:", "CUMPLIDA" if exitos >= 100 and duracion <= 60 else "NO cumplida")