from flask import Flask, render_template, request, jsonify
import mysql.connector
import time
import csv
import io
import os
import logging
from datetime import datetime

app = Flask(__name__)

# Clave API esperada
API_KEY_VALID = "CobranzasBeta"

# Configuración de logs
def configurar_logs():
    fecha_actual = datetime.now().strftime('%Y-%m-%d')
    carpeta_logs = f"./logs/{fecha_actual}"
    if not os.path.exists(carpeta_logs):
        os.makedirs(carpeta_logs)

    archivo_log = os.path.join(carpeta_logs, f"{fecha_actual}.log")
    logging.basicConfig(
        filename=archivo_log,
        level=logging.DEBUG,  # Cambiado a DEBUG para maximizar el nivel de detalle
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Sistema iniciado y configuración de logs completada.")

configurar_logs()

def registrar_log(mensaje, nivel="info"):
    if nivel.lower() == "info":
        logging.info(mensaje)
    elif nivel.lower() == "error":
        logging.error(mensaje)
    elif nivel.lower() == "warning":
        logging.warning(mensaje)
    elif nivel.lower() == "debug":
        logging.debug(mensaje)
    else:
        logging.info(mensaje)

def validar_api_key():
    api_key = request.headers.get('apikey')
    if api_key != API_KEY_VALID:
        registrar_log("Clave API no válida", "warning")
        return jsonify({"error": "Clave API no válida"}), 401
    return None  # Si la clave API es válida, continúa con la solicitud

@app.route('/')
def index():
    registrar_log("Acceso a la página principal")
    return render_template('index.html')

def emitir_audio(audio):
    registrar_log(f"Emitir audio: {audio}")
    print(f"Emitir audio: {audio}")

def conectar_base_datos():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="desarrollo_ivr"
        )
        registrar_log("Conexión exitosa a la base de datos")
        return conexion
    except mysql.connector.Error as err:
        registrar_log(f"Error en la conexión a la base de datos: {err}", "error")
        return None

def consultar_base_datos_con_timeout(identificacion, timeout=10):
    conexion = conectar_base_datos()
    if not conexion:
        return None, None

    try:
        cursor = conexion.cursor()
        consulta = "SELECT `NOMBRE TITULAR` FROM `asignación - 202411` WHERE IDENTIFICACION = %s"
        
        # Establecemos un límite de tiempo
        inicio = time.time()
        cursor.execute(consulta, (identificacion,))
        resultado_query = cursor.fetchone()
        registrar_log(f"Consulta ejecutada para identificación {identificacion}: {resultado_query}")
        
        # Si encontramos un resultado, lo devolvemos
        if resultado_query:
            cursor.fetchall()  # Limpiar cualquier resultado pendiente
            return "success", resultado_query[0]
        
        # Si no encontramos resultados y el tiempo de espera ha pasado
        if time.time() - inicio > timeout:
            registrar_log(f"Tiempo de espera excedido para identificación {identificacion} después de {time.time() - inicio} segundos", "warning")
            return "timeout", None

        return "not_found", None

    except mysql.connector.Error as err:
        registrar_log(f"Error en la consulta a la base de datos: {err}", "error")
        return None, None
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.route('/consultar_cedula', methods=['GET'])
def consultar_identificacion_especifica():
    identificacion_a_consultar = request.args.get('cedula')

    registrar_log(f"Solicitud recibida: consultar_cedula con parámetros: {request.args}", "info")

    if not identificacion_a_consultar:
        registrar_log("Error: No se proporcionó la identificación en la solicitud", "warning")
        return jsonify({"error": "La identificación es requerida"}), 400

    if not identificacion_a_consultar.isdigit():
        emitir_audio("Audio Identificación no válida")
        registrar_log(f"Error: Identificación no válida (debe ser numérica): {identificacion_a_consultar}", "warning")
        return jsonify({"error": "Identificación no válida, debe ser numérica"}), 400

    registrar_log(f"Consulta iniciada con identificación: {identificacion_a_consultar}", "info")

    resultado, nombre_titular = consultar_base_datos_con_timeout(identificacion_a_consultar, timeout=5)

    if resultado == "timeout":
        emitir_audio("Audio Problemas Técnicos")
        registrar_log(f"Consulta TIMEOUT para identificación: {identificacion_a_consultar}", "warning")
        return jsonify({"error": "Tiempo de espera excedido"}), 408
    elif resultado == "success" and nombre_titular:
        emitir_audio("Audio Transferir a Cola")
        emitir_audio(f"Audio Bienvenida {nombre_titular}")
        registrar_log(f"Consulta exitosa. Identificación: {identificacion_a_consultar}, Titular: {nombre_titular}", "info")
        return jsonify({
            "identificacion": identificacion_a_consultar,
            "nombre_titular": nombre_titular,
            "Estado": "Cédula encontrada"
        }), 200
    else:
        emitir_audio("Audio Identificación incorrecta")
        registrar_log(f"Identificación no encontrada: {identificacion_a_consultar}", "info")
        return jsonify({
            "identificacion": identificacion_a_consultar,
            "Estado": "Cédula no encontrada"
        }), 404


@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    data = request.json
    identificacion = data.get('identificacion')
    nombre_titular = data.get('nombre_titular')

    if not identificacion or not nombre_titular:
        registrar_log("Error: Faltan campos obligatorios para crear usuario", "warning")
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    conexion = conectar_base_datos()
    if not conexion:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conexion.cursor()
        consulta = "INSERT INTO `asignación - 202411` (IDENTIFICACION, `NOMBRE TITULAR`) VALUES (%s, %s)"
        cursor.execute(consulta, (identificacion, nombre_titular))
        conexion.commit()
        registrar_log(f"Usuario creado con éxito: {identificacion}, {nombre_titular}")
        return jsonify({"mensaje": "Usuario creado exitosamente"}), 201
    except mysql.connector.Error as err:
        registrar_log(f"Error al crear usuario: {err}", "error")
        return jsonify({"error": f"Error al insertar: {err}"}), 500
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.route('/actualizar_usuario/<identificacion>', methods=['PUT'])
def actualizar_usuario(identificacion):
    data = request.json
    nombre_titular = data.get('nombre_titular')

    if not nombre_titular:
        registrar_log("Error: Falta el campo obligatorio 'nombre_titular' para actualizar usuario", "warning")
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    conexion = conectar_base_datos()
    if not conexion:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conexion.cursor()
        consulta = "UPDATE `asignación - 202411` SET `NOMBRE TITULAR` = %s WHERE IDENTIFICACION = %s"
        cursor.execute(consulta, (nombre_titular, identificacion))
        conexion.commit()
        if cursor.rowcount > 0:
            registrar_log(f"Usuario actualizado: {identificacion} -> {nombre_titular}")
            return jsonify({"mensaje": "Usuario actualizado exitosamente"}), 200
        else:
            registrar_log(f"Usuario no encontrado para actualizar: {identificacion}", "warning")
            return jsonify({"error": "Usuario no encontrado"}), 404
    except mysql.connector.Error as err:
        registrar_log(f"Error al actualizar usuario: {err}", "error")
        return jsonify({"error": f"Error al actualizar: {err}"}), 500
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.route('/eliminar_usuario/<identificacion>', methods=['DELETE'])
def eliminar_usuario(identificacion):
    conexion = conectar_base_datos()
    if not conexion:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conexion.cursor()
        consulta = "DELETE FROM `asignación - 202411` WHERE IDENTIFICACION = %s"
        cursor.execute(consulta, (identificacion,))
        conexion.commit()
        if cursor.rowcount > 0:
            registrar_log(f"Usuario eliminado: {identificacion}")
            return jsonify({"mensaje": "Usuario eliminado exitosamente"}), 200
        else:
            registrar_log(f"Usuario no encontrado para eliminar: {identificacion}", "warning")
            return jsonify({"error": "Usuario no encontrado"}), 404
    except mysql.connector.Error as err:
        registrar_log(f"Error al eliminar usuario: {err}", "error")
        return jsonify({"error": f"Error al eliminar: {err}"}), 500
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.route('/subir_archivo', methods=['POST'])
def subir_archivo():
    if 'archivo' not in request.files:
        registrar_log("Error: No se encontró el archivo en la solicitud", "warning")
        return jsonify({"error": "No se encontró el archivo"}), 400

    archivo = request.files['archivo']
    if archivo.filename == '':
        registrar_log("Error: No se seleccionó ningún archivo", "warning")
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400

    if archivo and archivo.filename.lower().endswith('.csv'):
        conexion = conectar_base_datos()
        if not conexion:
            return jsonify({"error": "Error de conexión a la base de datos"}), 500

        try:
            cursor = conexion.cursor()
            # Eliminar todos los registros de la tabla
            cursor.execute("DELETE FROM `asignación - 202411`")
            conexion.commit()
            registrar_log("Registros antiguos eliminados de la tabla")

            contenido = archivo.read().decode('utf-8')
            csv_reader = csv.reader(io.StringIO(contenido))
            columnas = next(csv_reader)  # Obtener los nombres de las columnas

            # Construir la consulta de inserción dinámica
            columnas_sql = ", ".join(f"`{col}`" for col in columnas)
            placeholders = ", ".join(["%s"] * len(columnas))
            consulta = f"INSERT INTO `asignación - 202411` ({columnas_sql}) VALUES ({placeholders})"

            for fila in csv_reader:
                cursor.execute(consulta, fila)

            conexion.commit()
            registrar_log(f"Archivo procesado y datos insertados exitosamente: {archivo.filename}")
            return jsonify({"mensaje": "Archivo subido y datos insertados exitosamente"}), 201
        except mysql.connector.Error as err:
            registrar_log(f"Error al procesar el archivo CSV: {err}", "error")
            return jsonify({"error": f"Error al insertar: {err}"}), 500
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()
    else:
        registrar_log("Error: Formato de archivo no soportado, solo se admite CSV", "warning")
        return jsonify({"error": "Formato de archivo no soportado, solo se admite CSV"}), 400

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=443, ssl_context=('C:/xampp/apache/conf/ssl.crt/wilcard.pem', 
                                                 'C:/xampp/apache/conf/ssl.key/wilcardpycb.key'))