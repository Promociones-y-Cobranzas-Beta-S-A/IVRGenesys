import pandas as pd

# Paso 1: Leer el archivo CSV
csv_file = r'C:\Users\jduran\Documents\Desarrollo IVR\formato\Asignación - 202411.csv'

df = pd.read_csv(csv_file)

# Paso 2: Crear las sentencias SQL
# Obtener los nombres de las columnas
columns = df.columns.tolist()

# Crear la plantilla de la sentencia INSERT
insert_statement_template = "INSERT INTO `asignación - 202411` ({}) VALUES ({});\n"

# Crear un archivo para guardar las sentencias SQL
sql_file = 'archivo_de_salida.sql'  # Cambia esta ruta si lo deseas

with open(sql_file, 'w', encoding='utf-8') as f:
    # Escribir la cabecera de la tabla (columnas)
    f.write(f"-- Sentencias SQL para insertar los datos del CSV\n")
    
    for index, row in df.iterrows():
        # Crear los valores para cada fila
        values = tuple(row)
        
        # Crear la sentencia SQL de la fila
        insert_statement = insert_statement_template.format(
            ', '.join([f"`{col}`" for col in columns]),  # Escapar las columnas con backticks
            ', '.join(f"'{str(value)}'" if value is not None else 'NULL' for value in values)
        )
        
        # Escribir la sentencia en el archivo SQL
        f.write(insert_statement)

print(f"El archivo SQL ha sido creado exitosamente: {sql_file}")
