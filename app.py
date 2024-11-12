from flask import Flask, render_template, request, jsonify, make_response
import pusher
import mysql.connector
from flask_cors import CORS, cross_origin

# Configuración de la base de datos
con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)


# Inicializar la aplicación Flask
app = Flask(__name__)
CORS(app)
# Configurar Pusher
pusher_client = pusher.Pusher(
     app_id='1766036',
     key='252e6abbd99ae9de9d15',
     secret='8e19ebe8863460415a3f',
    cluster='us2',
    ssl=True
    )

def notificarActualizacionTelefonoArchivo():
    pusher_client.trigger("canalContactos", "registroContacto", {})

# Página principal
@app.route("/")
def index():
     #return render_template("Formulario.html")
      return render_template("app.html")

# Ruta para buscar pagos en la base de datos
@app.route("/buscar")
def buscar():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    cursor.execute("""
    SELECT Id_Contacto, Correo_Electronico, Nombre,Asunto FROM tst0_contacto 
    ORDER BY Id_Contacto DESC
    LIMIT 10 OFFSET 0
    """)
    
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

# Ruta para registrar un nuevo pago y activar el evento Pusher
@app.route("/registrar", methods=["POST"])
def registrar():
    if not con.is_connected():
        con.reconnect()

    id = request.form.get("id")
    Correo_Electronico = request.form.get("Correo_Electronico")
    Nombre = request.form.get("Nombre")
    Asunto = request.form.get("Asunto")
    
    cursor = con.cursor()

    if id:
        sql = """
        UPDATE tst0_contacto SET
        Correo_Electronico = %s,
        Nombre = %s
        Asunto = %s
        WHERE Id_Contacto = %s
        """
        val = (Correo_Electronico, Nombre,Asunto, id)
    else:
        sql = """
        INSERT INTO tst0_contacto (Correo_Electronico, Nombre,Asunto)
        VALUES (%s, %s, %s)
        """
        val = (Correo_Electronico, Nombre,Asunto)
    
    cursor.execute(sql, val)
    con.commit()
    cursor.close()

    notificarActualizacionTelefonoArchivo()
    return make_response(jsonify({}))

# Ruta para editar un registro existente
@app.route("/editar", methods=["GET"])
def editar():
    if not con.is_connected():
        con.reconnect()

    id = request.args.get("id")

    cursor = con.cursor(dictionary=True)
    sql = """
    SELECT Id_Contacto, Correo_Electronico, Nombre,Asunto FROM tst0_contacto
    WHERE Id_Contacto = %s
    """
    val = (id,)

    cursor.execute(sql, val)
    registros = cursor.fetchall()
    con.close()

    return make_response(jsonify(registros))

# Ruta para eliminar un registro
@app.route("/eliminar", methods=["POST"])
def eliminar():
    if not con.is_connected():
        con.reconnect()

    id = request.form.get("id")

    cursor = con.cursor()
    sql = """
    DELETE FROM tst0_contacto
    WHERE Id_Contacto = %s
    """
    val = (id,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    notificarActualizacionTelefonoArchivo()

    return make_response(jsonify({}))

# Iniciar la aplicación
if __name__ == "__main__":
    app.run(debug=True)
