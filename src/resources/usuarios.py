# src/resources/usuarios.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models import db, Usuario,Ingreso,Egreso
from src.schemas.usuario_schema import UsuarioRegistroSchema, UsuarioLoginSchema, UsuarioRespuestaSchema,UsuarioConfiguracionSchema
from sqlalchemy import exists
from datetime import timedelta,datetime,timezone
from marshmallow import ValidationError


usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')

registro_schema = UsuarioRegistroSchema()
login_schema = UsuarioLoginSchema()
respuesta_schema = UsuarioRespuestaSchema()
config_schema = UsuarioConfiguracionSchema()

# Registrar nuevo usuario
@usuarios_bp.route('/signup', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    errores = registro_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    if db.session.query(exists().where(Usuario.correo == data['correo'])).scalar():
        return jsonify({"msg": "Correo ya registrado"}), 400

    if db.session.query(exists().where(Usuario.nombre_usuario == data['nombre_usuario'])).scalar():
        return jsonify({"msg": "Nombre de usuario ya registrado"}), 400

    nuevo_usuario = Usuario(
        nombre_usuario=data['nombre_usuario'],
        correo=data['correo']
    )
    nuevo_usuario.establecer_contrasena(data['contrasena'])
    db.session.add(nuevo_usuario)
    db.session.commit()

    return respuesta_schema.dump(nuevo_usuario), 201

# Login de usuario
@usuarios_bp.route('/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    errores = login_schema.validate(data)
    if errores:
        return jsonify({"errores": errores}), 400

    usuario = Usuario.query.filter_by(correo=data['correo']).first()
    if not usuario or not usuario.verificar_contrasena(data['contrasena']):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    token = create_access_token(identity=str(usuario.id), expires_delta=timedelta(days=7))

    return jsonify({"token": token, "usuario": respuesta_schema.dump(usuario)}), 200


#asignar los valores iniciales a un usuario creado pero que se loguea por primera vez.
#es decir que su capital inicial y su moneda esten vacios.
@usuarios_bp.route('/config-inicial', methods=['PUT'])
@jwt_required()
def config_local():
    data = request.get_json()
    try:
        datos_validos = config_schema.load(data)
    except ValidationError as err:
        return jsonify({"errores": err.messages}), 400


    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    

    usuario.capital_inicial = datos_validos['capital_inicial']
    usuario.capital_actual = datos_validos['capital_inicial']
    usuario.moneda = datos_validos['moneda']


    db.session.commit()

    return jsonify({"msg": "Configuración local actualizada"}), 200     






# Obtener perfil (protegido)
@usuarios_bp.route('/perfil', methods=['GET'])
@jwt_required()
def perfil_usuario():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify(respuesta_schema.dump(usuario)), 200



#---------------------------------------------------
# Ruta para obtener los totales de un usuario por ID
@usuarios_bp.route('/totales', methods=['GET'])
@jwt_required()
def obtener_totales_usuario():
    # El 'id' del usuario ya está disponible a través de 'TOKEN
    usuario_id = int(get_jwt_identity());
    usuario = Usuario.query.get(usuario_id);
    
    # Calcula los totales usando la función del modelo
    totales = usuario.calcular_totales()

    # Retorna los totales como JSON
    return jsonify({
        'capital_inicial': totales.get('capital_inicial', 0),
        'total_ingresos': totales.get('total_ingresos', 0),
        'total_egresos': totales.get('total_egresos', 0),
        'capital_actual': totales.get('capital_actual', 0)
    })

#-----------------------------------------------

# CRUP para Reportes
@usuarios_bp.route('/reportes', methods=['GET'])
@jwt_required()
def obtener_reportes():
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get(usuario_id)
    
    ingresos = Ingreso.query.filter_by(usuario_id=usuario_id).all()
    egresos = Egreso.query.filter_by(usuario_id=usuario_id).all()

    reportes = [
        {
            "id": ingreso.id,
            "monto": ingreso.monto,
            "descripcion": ingreso.descripcion,
            "fecha": ingreso.fecha,
            "tipo": "ingreso"
        } for ingreso in ingresos
    ] + [
        {
            "id": egreso.id,
            "monto": egreso.monto,
            "descripcion": egreso.descripcion,
            "fecha": egreso.fecha,
            "tipo": "egreso"
        } for egreso in egresos
    ]

    reportes_ordenados = sorted(reportes, key=lambda x: x['fecha'], reverse=True)
    return jsonify(reportes_ordenados), 200


#---------------------------------------------------
@usuarios_bp.route('/datosmensuales', methods=['POST'])
@jwt_required()
def obtener_datos_mensuales():

    usuario_id = int(get_jwt_identity())

    
    try:
        data = request.get_json()  # Los datos ahora se esperan en el cuerpo de la solicitud
        meses = data.get("meses", [])
        

        if not meses or not isinstance(meses, list):
             return jsonify({"error": "Por favor, envía un arreglo válido de meses."}), 400
        
        # Diccionario para convertir nombres de meses a números
        meses_a_numeros = {
            "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4,
            "Mayo": 5, "Junio": 6, "Julio": 7, "Agosto": 8,
            "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
        }

        # Preparar respuesta
        resultado = []

        for mes in meses:
             mes_numero = meses_a_numeros.get(mes.capitalize())
             if mes_numero is None:
                 return jsonify({"error": f"El mes '{mes}' no es válido."}), 400

            # Filtrar ingresos y egresos por usuario, mes y año actual
             ingresos_mes = db.session.query(db.func.sum(Ingreso.monto)).filter(
                 db.extract('month', Ingreso.fecha) == mes_numero,
                 db.extract('year', Ingreso.fecha) == datetime.now().year,
                 Ingreso.usuario_id == usuario_id
             ).scalar() or 0

             egresos_mes = db.session.query(db.func.sum(Egreso.monto)).filter(
                 db.extract('month', Egreso.fecha) == mes_numero,
                 db.extract('year', Egreso.fecha) == datetime.now().year,
                 Egreso.usuario_id == usuario_id
             ).scalar() or 0

            # Añadir al resultado
             resultado.append({
                 "mes": mes,
                 "ingresos": ingresos_mes,
                 "egresos": egresos_mes
             })
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

