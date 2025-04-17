# src/resources/usuarios.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models import db, Usuario
from src.schemas.usuario_schema import UsuarioRegistroSchema, UsuarioLoginSchema, UsuarioRespuestaSchema,UsuarioConfiguracionSchema
from sqlalchemy import exists
from datetime import timedelta
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



