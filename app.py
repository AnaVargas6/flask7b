# python.exe -m venv .venv
# cd .venv/Scripts
# activate.bat
# py -m ensurepip --upgrade

from flask import Flask

from flask import render_template
from flask import request
from flask import jsonify, make_response

import pusher

import mysql.connector
import datetime
import pytz

con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)

app = Flask(__name__)

@app.route("/")
def index():
    con.close()

    return render_template("app.html")

@app.route("/alumnos")
def alumnos():
    con.close()

    return render_template("alumnos.html")

@app.route("/alumnos/guardar", methods=["POST"])
def alumnosGuardar():
    con.close()
    matricula      = request.form["txtMatriculaFA"]
    nombreapellido = request.form["txtNombreApellidoFA"]

    return f"Matrícula {matricula} Nombre y Apellido {nombreapellido}"

# Código usado en las prácticas
def notificarActualizacionTemperaturaHumedad():
    pusher_client = pusher.Pusher(
        app_id="1714541",
        key="2df86616075904231311",
        secret="2f91d936fd43d8e85a1a",
        cluster="us2",
        ssl=True
    )

    pusher_client.trigger("canalRegistrosContacto", "registroContacto", args)

@app.route("/buscar")
def buscar():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    cursor.execute("""
    SELECT Id_Contacto, Correo_Electronica, Nombre, Asunto FROM tst0_contacto
    ORDER BY Id_Contacto DESC
    LIMIT 10 OFFSET 0
    """)
    registros = cursor.fetchall()

    con.close()

    return make_response(jsonify(registros))

@app.route("/guardar", methods=["POST"])
def guardar():
    if not con.is_connected():
        con.reconnect()

    id          = request.form["id"]
    correo_electronico = request.form["correo_electronico"]
    nombre     = request.form["nombre"]
     asunto     = request.form["asunto"]
    
    cursor = con.cursor()

    if id:
        sql = """
        UPDATE tst0_contacto SET
        Correo_Electronico = %s,
        Nombre     = %s
        Asunto     = %s
        WHERE Id_Contacto = %s
        """
        val = (correo_electronico, nombre, asunto, id)
    else:
        sql = """
        INSERT INTO tst0_contacto (Correo_Electronico, Nombre, Asunto)
                        VALUES (%s,          %s,      %s)
        """
        val =                  (correo_electronico, nombre, asunto)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

    notificarActualizacionContacto()

    return make_response(jsonify({}))

@app.route("/editar", methods=["GET"])
def editar():
    if not con.is_connected():
        con.reconnect()

    id = request.args["id"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    SELECT Id_Contacto, Correo_Electronico, Nombre , Asunto FROM tst0_Contacto
    WHERE Id_Contacto = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

@app.route("/eliminar", methods=["POST"])
def eliminar():
    if not con.is_connected():
        con.reconnect()

    id = request.form["id"]

    cursor = con.cursor(dictionary=True)
    sql    = """
    DELETE FROM tst0_contacto
    WHERE Id_Contacto = %s
    """
    val    = (id,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    notificarActualizacionContacto()

    return make_response(jsonify({}))
