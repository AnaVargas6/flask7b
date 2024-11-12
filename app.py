<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js" integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script>
    <script src="https://js.pusher.com/8.2.0/pusher.min.js"></script>
    <title>App Contacto</title>
</head>
<body>
    <div class="container">
        <h1>Lista de Contactos</h1>

        <!-- Formulario para agregar o editar contacto -->
        <form id="formContacto">
            <input type="hidden" id="id_contacto" name="id_contacto">
            <div class="mb-3">
                <label for="Correo_Electronico" class="form-label">Correo Electrónico</label>
                <input type="email" class="form-control" id="Correo_Electronico" name="Correo_Electronico" required>
            </div>
            <div class="mb-3">
                <label for="Nombre" class="form-label">Nombre</label>
                <input type="text" class="form-control" id="Nombre" name="Nombre" required>
            </div>
            <div class="mb-3">
                <label for="Asunto" class="form-label">Asunto</label>
                <input type="text" class="form-control" id="Asunto" name="Asunto" required>
            </div>
            <button type="submit" class="btn btn-success">Guardar</button>
            <button id="btnActualizar" class="btn btn-primary ms-2">Actualizar</button>
        </form>

        <!-- Tabla para mostrar los contactos -->
        <table class="table table-sm mt-3">
            <thead>
                <tr>
                    <th>Id Contacto</th>
                    <th>Correo Electrónico</th>
                    <th>Nombre</th>
                    <th>Asunto</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody id="tbodyContactos"></tbody>
        </table>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>

    <script>
        window.addEventListener("load", function (event) {
            function buscar() {
                $.get("/buscar", function (respuesta) {
                    $("#tbodyContactos").html("");
                    respuesta.data.forEach(function(contacto) {
                        $("#tbodyContactos").append(`<tr>
                            <td>${contacto[0]}</td>
                            <td>${contacto[1]}</td>
                            <td>${contacto[2]}</td>
                            <td>${contacto[3]}</td>
                            <td>
                                <button class="btn btn-warning btn-sm" onclick="editar(${contacto[0]}, '${contacto[1]}', '${contacto[2]}', '${contacto[3]}')">Editar</button>
                                <button class="btn btn-danger btn-sm" onclick="eliminar(${contacto[0]})">Eliminar</button>
                            </td>
                        </tr>`);
                    });
                });
            }

            buscar();

            Pusher.logToConsole = true;
            var pusher = new Pusher("252e6abbd99ae9de9d15", {
                cluster: "us3"
            });

            var channel = pusher.subscribe("canalContactos");

            channel.bind("registroContacto", function (contacto) {
                $("#tbodyContactos").prepend(`<tr>
                    <td>${contacto.Id_Contacto}</td>
                    <td>${contacto.Correo_Electronico}</td>
                    <td>${contacto.Nombre}</td>
                    <td>${contacto.Asunto}</td>
                    <td>
                        <button class="btn btn-warning btn-sm" onclick="editar(${contacto.Id_Contacto}, '${contacto.Correo_Electronico}', '${contacto.Nombre}', '${contacto.Asunto}')">Editar</button>
                        <button class="btn btn-danger btn-sm" onclick="eliminar(${contacto.Id_Contacto})">Eliminar</button>
                    </td>
                </tr>`);
            });

            channel.bind("modificarContacto", function (contacto) {
                buscar();
            });

            channel.bind("eliminarContacto", function (data) {
                buscar();
            });

            window.editar = function(id, Correo_Electronico, Nombre, Asunto) {
                $("#id_contacto").val(id);
                $("#Correo_Electronico").val(Correo_Electronico);
                $("#Nombre").val(Nombre);
                $("#Asunto").val(Asunto);
            };

            $("#formContacto").submit(function(event) {
                event.preventDefault();
                var formData = $(this).serialize();
                var id_contacto = $("#id_contacto").val();

                if (id_contacto) {
                    $.post("/modificar", formData, function() {
                        buscar();
                        $("#formContacto")[0].reset();
                    });
                } else {
                    // Usa POST para el registro en vez de GET
                    $.post("/registrar", formData, function() {
                        buscar();
                        $("#formContacto")[0].reset();
                    });
                }
            });

            window.eliminar = function(id) {
                if (confirm("¿Estás seguro de que deseas eliminar este contacto?")) {
                    $.post("/eliminar", { id_contacto: id }, function() {
                        buscar();
                    });
                }
            };
        });
    </script>    
</body>
</html>
