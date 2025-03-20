from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.Usuarios import Usuario
from src.models.Ingresos import Ingreso
from src.models.Egresos import Egreso
from src import db
from marshmallow import ValidationError
from src.schemas.usuario_schema import UsuarioSchema




#Definios el blueprint para usuarios
usuarios_bp = Blueprint('usuarios',__name__,url_prefix= '/api/usuarios')

# CRUD para Usuario
@usuarios_bp.route('/signup',methods=['POST'])
@cross_origin(origins=["https://reliable-sorbet-07d22a.netlify.app"])  # Asegurar CORS aquí también
def signup():

    try:
       usuario_schema = UsuarioSchema()  # Instancia de la clase
       data = usuario_schema.load(request.get_json())  # Carga y valida los datos
    except ValidationError as err:
        return jsonify(err.messages), 400   
       
    if Usuario.query.filter((Usuario.nombre_usuario == data['nombre_usuario']) | (Usuario.correo == data['correo'])).first():
        return jsonify({'msg': 'El usuario o correo ya existe'}), 400   
    
    nuevo_usuario = Usuario(
        nombre_usuario=data['nombre_usuario'],
        correo=data['correo'],
        capital_inicial=None,
        moneda=None
    )

    nuevo_usuario.establecer_contrasena(data['contrasena'])
    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({'msg': 'Usuario creado exitosamente'}), 201

# Ruta para obtener todos los usuarios (GET)
@usuarios_bp.route('', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.query.all()  # Obtener todos los usuarios
    usuarios_list = []
    
    for usuario in usuarios:
        usuarios_list.append({
            'id': usuario.id,
            'nombre_usuario': usuario.nombre_usuario,
            'correo': usuario.correo
        })
    
    return jsonify(usuarios_list), 200

#-------------------------------

# Ruta para login (POST)
@usuarios_bp.route('/login', methods=['POST'])
def login():
    # Obtener las credenciales del usuario (correo y contraseña)
    data = request.get_json()
    
    # Validar si los datos necesarios están presentes
    if not data or 'correo' not in data or 'contrasena' not in data:
        return jsonify({"message": "Faltan datos requeridos"}), 400

    usuario = Usuario.query.filter_by(correo=data['correo']).first()  # Buscar el usuario por correo

    # Verificar si el usuario existe y si la contraseña es correcta
    if usuario and usuario.verificar_contrasena(data['contrasena']):  
        # Crear el token JWT con la identidad del usuario
        access_token = create_access_token(identity=usuario.id)
        
        # Convertir el usuario a diccionario si necesitas enviarlo en la respuesta
        usuario_dict = usuario.to_dict()  

        return jsonify({
            "access_token": access_token,
            "usuario": usuario_dict
        }), 200  # Retornar el token JWT y datos del usuario

    return jsonify({"message": "Correo o contraseña incorrectos"}), 401
    

# -----------------------------------------
# OBTENER TODOS LOS USUARIOS (Solo admin)
# -----------------------------------------
@usuarios_bp.route('/', methods=['GET'])
@jwt_required()  # Requiere autenticación
def obtener_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([{
        'id': u.id,
        'nombre_usuario': u.nombre_usuario,
        'correo': u.correo,
        'capital_inicial': u.capital_inicial,
        'moneda': u.moneda
    } for u in usuarios]), 200

# -----------------------------------------
# ACTUALIZAR USUARIO AUTENTICADO
# -----------------------------------------
@usuarios_bp.route('/', methods=['PUT'])
@jwt_required()
def actualizar_usuario():
    usuario_id = get_jwt_identity()  # Obtener ID del usuario autenticado
    usuario = Usuario.query.get_or_404(usuario_id)

    data = request.get_json()
    
    if 'correo' in data:
        usuario.correo = data['correo']
        
    if 'capital_inicial' in data:
        usuario.capital_inicial = data['capital_inicial']
        usuario.capital_actual = data['capital_inicial']

    if 'moneda' in data:
        usuario.moneda = data['moneda']

    db.session.commit()
    return jsonify({'msg': 'Usuario actualizado exitosamente'}), 200

# -----------------------------------------
# OBTENER UN USUARIO ESPECÍFICO POR ID
# -----------------------------------------
@usuarios_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def obtener_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return jsonify({
        'id': usuario.id,
        'nombre_usuario': usuario.nombre_usuario,
        'correo': usuario.correo,
        'capital_inicial': usuario.capital_inicial,
        'moneda': usuario.moneda
    }), 200

# -----------------------------------------
# ELIMINAR USUARIO AUTENTICADO
# -----------------------------------------
@usuarios_bp.route('/', methods=['DELETE'])
@jwt_required()
def eliminar_usuario():
    usuario_id = get_jwt_identity()  # Obtener ID del usuario autenticado
    usuario = Usuario.query.get_or_404(usuario_id)

    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'msg': 'Usuario eliminado exitosamente'}), 200

# -----------------------------------------
# OBTENER TOTALES DEL USUARIO AUTENTICADO
# -----------------------------------------
@usuarios_bp.route('/totales', methods=['GET'])
@jwt_required()
def obtener_totales_usuario():
    usuario_id = get_jwt_identity()

    usuario = Usuario.query.get_or_404(usuario_id)
    
    totales = usuario.calcular_totales()

    return jsonify({
        'capital_inicial': totales.get('capital_inicial', 0),
        'total_ingresos': totales.get('total_ingresos', 0),
        'total_egresos': totales.get('total_egresos', 0),
        'capital_actual': totales.get('capital_actual', 0)
    }), 200

# -----------------------------------------
# OBTENER REPORTES DEL USUARIO AUTENTICADO
# -----------------------------------------
@usuarios_bp.route('/reportes', methods=['GET'])
@jwt_required()
def obtener_reportes():
    usuario_id = get_jwt_identity()

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

    return jsonify(reportes), 200