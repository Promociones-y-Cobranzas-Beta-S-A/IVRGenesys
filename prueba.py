from flask import Flask, render_template, request, jsonify
import mysql.connector
import time

app = Flask(__name__)


# Clave API esperada
API_KEY_VALID = "CobranzasBeta"

def validar_api_key():
    api_key = request.headers.get('apikey')
    if api_key != API_KEY_VALID:
        return jsonify({"error": "Clave API no válida"}), 401
    return None  # Si la clave API es válida, continúa con la solicitud
    

@app.route('/')
def index():
    return render_template('index.html')

def emitir_audio(audio):
    print(f"Emitir audio: {audio}")

def conectar_base_datos():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="desarrollo_ivr"
        )
        print("Conexión exitosa a la base de datos")
        return conexion
    except mysql.connector.Error as err:
        print(f"Error en la base de datos: {err}")
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
        print(f"Resultado de la consulta: {resultado_query}")
        
        # Si encontramos un resultado, lo devolvemos
        if resultado_query:
            cursor.fetchall()  # Limpiar cualquier resultado pendiente
            return "success", resultado_query[0]
        
        # Si no encontramos resultados y el tiempo de espera ha pasado
        if time.time() - inicio > timeout:
            print(f"Tiempo de espera excedido después de {time.time() - inicio} segundos")
            return "timeout", None

        return "not_found", None

    except mysql.connector.Error as err:
        print(f"Error en la base de datos: {err}")
        return None, None
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.route('/consultar_cedula', methods=['GET'])
def consultar_identificacion_especifica():
    identificacion_a_consultar = request.args.get('cedula')

    if not identificacion_a_consultar:
        return jsonify({"error": "La identificación es requerida"}), 400

    if not identificacion_a_consultar.isdigit():
        emitir_audio("Audio Identificación no válida")
        return jsonify({"error": "Identificación no válida, debe ser numérica"}), 400

    print(f"Consulta recibida con identificación: {identificacion_a_consultar}")

    resultado, nombre_titular = consultar_base_datos_con_timeout(identificacion_a_consultar, timeout=5)

    if resultado == "timeout":
        emitir_audio("Audio Problemas Técnicos")
        return jsonify({"error": "Tiempo de espera excedido"}), 408
    elif resultado == "success" and nombre_titular:
        emitir_audio("Audio Transferir a Cola")
        emitir_audio(f"Audio Bienvenida {nombre_titular}")
        return jsonify({
            "identificacion": identificacion_a_consultar,
            "nombre_titular": nombre_titular
        }), 200
    else:
        emitir_audio("Audio Identificación incorrecta")
        return jsonify({"error": "Identificación incorrecta"}), 404

@app.route('/crear_usuario', methods=['POST'])
def crear_usuario():
    data = request.json
    identificacion = data.get('identificacion')
    nombre_titular = data.get('nombre_titular')

    if not identificacion or not nombre_titular:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    conexion = conectar_base_datos()
    if not conexion:
        return jsonify({"error": "Error de conexión a la base de datos"}), 500

    try:
        cursor = conexion.cursor()
        consulta = "INSERT INTO `asignación - 202411` (IDENTIFICACION, `NOMBRE TITULAR`) VALUES (%s, %s)"
        cursor.execute(consulta, (identificacion, nombre_titular))
        conexion.commit()
        return jsonify({"mensaje": "Usuario creado exitosamente"}), 201
    except mysql.connector.Error as err:
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
            return jsonify({"mensaje": "Usuario actualizado exitosamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except mysql.connector.Error as err:
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
            return jsonify({"mensaje": "Usuario eliminado exitosamente"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al eliminar: {err}"}), 500
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
