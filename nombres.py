import pandas as pd
import random
from pathlib import Path

# Ruta relativa al proyecto (ajustada correctamente)
BASE_DIR = Path(__file__).resolve().parents[2]
ruta_excel = BASE_DIR /'python'/ 'API'/ 'data' / 'Capacitacion' / 'hombres.xlsx'

# Leer Excel
df = pd.read_excel(ruta_excel)

# Asegurarte de limpiar espacios en nombres de columnas (por si acaso)
df.columns = df.columns.str.strip().str.lower()

# Elegir un nombre y apellido1 de la misma fila
fila = df.sample(n=1).iloc[0]

nombre = fila['nombre']
apellido1 = fila['apellido1']

# Elegir un apellido2 diferente de forma aleatoria
# (asegura que no sea el mismo que apellido1)
apellidos_disponibles = df['apellido2'].dropna().unique().tolist()
apellido2 = random.choice([a for a in apellidos_disponibles if a != apellido1])

# Crear nombre completo
nombre_completo = f"{nombre} {apellido1} {apellido2}"

print(nombre_completo)
