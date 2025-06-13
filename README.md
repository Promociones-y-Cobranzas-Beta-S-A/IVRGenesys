# 📞 DESARROLLO IVR

API RESTful en Python (Flask) para la gestión de usuarios, consultas y cargas masivas en sistemas IVR, con registro de logs diarios, validación exhaustiva y exportación flexible.

---

## 🚀 Descripción

Este proyecto proporciona una API robusta para automatizar procesos de atención IVR a través de endpoints seguros y eficientes. Permite consultar usuarios, administrar registros (CRUD), cargar datos masivamente desde CSV y llevar seguimiento exhaustivo de actividad mediante logs diarios.

---

## 📁 Estructura del Proyecto

```
DESARROLLO IVR/
│
├── __pycache__/           # Archivos compilados de Python
│   └── app.cpython-313.pyc
│
├── formato/               # Utilidades para exportación de datos
│   ├── exportar.py
│   └── exportarjson.py
├── templates/             # Plantillas HTML (en desarrollo)
│
├── app.py                 # Script principal de la API
├── app.wsgi               # Configuración para despliegue WSGI
├── prueba.py              # Script para pruebas
└── README.md              # Documentación del proyecto
```

---

## ✨ Funcionalidades

- **API RESTful con Flask:**  
  Consulta, creación, actualización y eliminación de usuarios.
- **Carga masiva de datos:**  
  Endpoint para subir archivos CSV y poblar la base de datos.
- **Logs diarios:**  
  Registro exhaustivo de cada solicitud, errores y actividad relevante, organizados por fecha.
- **Validación estricta:**  
  Comprobación de datos de entrada, autenticación por API key, y manejo robusto de errores.
- **Exportaciones:**  
  Utilidades para exportar datos en varios formatos (`formato/exportar.py`, `formato/exportarjson.py`).
- **Despliegue seguro:**  
  Listo para correr bajo HTTPS y compatible con servidores WSGI.

---

## 🛡️ Seguridad

- **Autenticación API:**  
  Todas las rutas sensibles requieren header `apikey: CobranzasBeta`.
- **Permisos y cifrado:**  
  Soporta despliegue con SSL/TLS (ver ejemplo en `app.py`).

---

## 🛠️ Instalación y Ejecución

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/jduran1002/IVRGenesys.git
   cd "DESARROLLO IVR"
   ```

2. **Instala las dependencias:**
   _(Asegúrate de tener un archivo `requirements.txt` con Flask, mysql-connector-python y cualquier otra dependencia)_

   ```bash
   pip install -r requirements.txt
   ```

3. **Configura tu base de datos MySQL**  
   (Ajusta credenciales en `app.py` según tu entorno).

4. **Ejecuta la API en modo seguro:**
   ```bash
   python app.py
   ```
   _(Por defecto escucha en `https://0.0.0.0:443/` usando los certificados especificados)_

---

## 🌐 Endpoints Principales

- `GET /consultar_cedula?cedula=...`  
  Consulta nombre del titular asociado a la identificación.
- `POST /crear_usuario`  
  Crea un nuevo usuario (JSON: `identificacion`, `nombre_titular`).
- `PUT /actualizar_usuario/<identificacion>`  
  Actualiza el nombre del titular.
- `DELETE /eliminar_usuario/<identificacion>`  
  Elimina registro por identificación.
- `POST /subir_archivo`  
  Carga masiva de usuarios desde CSV (campo: `archivo`).

---

## 🗒️ Notas

- Los errores y eventos quedan registrados en la carpeta `logs/` bajo subcarpetas por fecha.
- La carpeta `templates/` está reservada para futuras integraciones de vistas HTML.
- Los scripts en `formato/` pueden ser utilizados para exportar datos desde la base.

---

## 👨‍💻 Autor

**Juan David Durán Lerma**  
📧 jdduran@cobranzasbeta.com.co

---

## 🤝 Contribuciones

¡Se aceptan sugerencias y mejoras! Abre un issue o pull request para participar.
