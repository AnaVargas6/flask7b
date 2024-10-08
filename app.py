from flask import Flask, render_template, request, jsonify, make_response
import pusher
import mysql.connector
import datetime
import pytz

# Configuración de la conexión a la base de datos
con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)

app = Flask(__name__)

# Función para cerrar la conexión si está abierta
def close_connection():
    if con.is_connected():
        con.close()

# Ruta principal
@app.route("/")
def index():
    close_connection()  # Cierra la conexión antes de cargar la página
    return render_template("app.html")

# Ruta de alumnos
@app.route("/alumnos")
def alumnos():
    close_connection()
    return render_template("alumnos.html")

# Ruta para guardar alumnos
@app.route("/alumnos/guardar", methods=["POST"])
def alumnos_guardar():
    close_connection()
    matricula = request.form["txtMatriculaFA"]
    nombreapellido = request.form["txtNombreApellidoFA"]

    return f"Matrícula {matricula} Nombre y Apellido {nombreapellido}"

# Función para notificar actualización de contacto
def notificar_actualizacion_contacto(args):
    pusher_client = pusher.Pusher(
        app_id="1714541",
        key="2df86616075904231311",
        secret="2f91d936fd43d8e85a1a",
        cluster="us2",
        ssl=True
    )
    pusher_client.trigger("canalRegistrosContacto", "registroContacto", args)

# Ruta para buscar contactos
@app.route("/buscar")
def buscar():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    cursor.execute("""
    SELECT Id_Contacto, Correo_Electronico, Nombre, Asunto FROM tst0_contacto
    ORDER BY Id_Contacto DESC
    LIMIT 10 OFFSET 0
    """)
    registros = cursor.fetchall()
    close_connection()

    return make_response(jsonify(registros))

# Ruta para guardar contactos
@app.route("/guardar", methods=["POST"])
def guardar():
    if not con.is_connected():
        con.reconnect()

    id = request.form["id"]
    correo_electronico = request.form["correo_electronico"]
    nombre = request.form["nombre"]
    asunto = request.form["asunto"]
    
    cursor = con.cursor()

    if id:
        sql = """
        UPDATE tst0_contacto SET
        Correo_Electronico = %s,
        Nombre = %s,
        Asunto = %s
        WHERE Id_Contacto = %s
        """
        val = (correo_electronico, nombre, asunto, id)
    else:
        sql = """
        INSERT INTO tst0_contacto (Correo_Electronico, Nombre, Asunto)
                        VALUES (%s, %s, %s)
        """
        val = (correo_electronico, nombre, asunto)
    
    cursor.execute(sql, val)
    con.commit()
    close_connection()

    # Notificar la actualización
    args = {"mensaje": "Contacto actualizado"}
    notificar_actualizacion_contacto(args)

    return make_response(jsonify({}))

# Ruta para editar contactos
@app.route("/editar", methods=["GET"])
def editar():
    if not con.is_connected():
        con.reconnect()

    id = request.args["id"]

    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT Id_Contacto, Correo_Electronico, Nombre, Asunto FROM tst0_contacto
    WHERE Id_Contacto = %s
    """
    val = (id,)
    cursor.execute(sql, val)
    registros = cursor.fetchall()
    close_connection()

    return make_response(jsonify(registros))

# Ruta para eliminar contactos
@app.route("/eliminar", methods=["POST"])
def eliminar():
    if not con.is_connected():
        con.reconnect()

    id = request.form["id"]

    cursor = con.cursor(dictionary=True)
    sql = """
    DELETE FROM tst0_contacto
    WHERE Id_Contacto = %s
    """
    val = (id,)
    cursor.execute(sql, val)
    con.commit()
    close_connection()

    # Notificar la eliminación
    args = {"mensaje": "Contacto eliminado"}
    notificar_actualizacion_contacto(args)

    return make_response(jsonify({}))
