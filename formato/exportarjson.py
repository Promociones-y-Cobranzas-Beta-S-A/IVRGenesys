import pandas as pd

# Paso 1: Leer el archivo CSV
csv_file = r'C:\Users\jduran\Documents\Desarrollo IVR\formato\Asignación - 202411.csv'

# Leer el archivo CSV en un DataFrame
df = pd.read_csv(csv_file)

# Paso 2: Convertir el DataFrame a JSON
# El método 'to_json' puede tomar diferentes parámetros como orientación (orient='records') para que sea más fácil de leer
json_file = r'C:\Users\jduran\Documents\Desarrollo IVR\formato\Asignación - 202411.json'

# Convertir y guardar en un archivo JSON
df.to_json(json_file, orient='records', lines=True)

print(f"El archivo JSON ha sido creado exitosamente: {json_file}")
