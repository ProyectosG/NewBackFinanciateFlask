from flask import Blueprint, request, jsonify
from src.models import db, Egreso,Usuario
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import date
#------------------------------------------
egresos_bp = Blueprint('egresos', __name__,url_prefix ="/api/egresos")
#-----------------------------------------


# CRUD para Egreso
@egresos_bp.route('/', methods=['GET'])
@jwt_required()
def obtener_egresos(payload):
    usuario_id = int(get_jwt_identity())

    try:    
        # Filtrar los egresos por el id del usuario autenticado
        egresos = Egreso.query.filter_by(usuario_id=usuario_id).all()
        
        # Formatear los egresos como una lista de diccionarios
        egresos_serializados = [
            {
                "id": egreso.id,
                "monto": egreso.monto,
                "descripcion": egreso.descripcion,
                "fecha": egreso.fecha.isoformat(),
                "categoria_id": egreso.categoria_id,
                "usuario_id": egreso.usuario_id
            }
            for egreso in egresos
        ]

        return jsonify(egresos_serializados), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




#----------------------------------------------------------------------------------------
# Ruta para crear un EGRESO
@egresos_bp.route('/agrega_egreso', methods=['POST'])
@jwt_required()
def crear_egreso():
    data = request.get_json()
    usuario_id = int(get_jwt_identity())
    # Validar que todos los campos requeridos estén presentes
    if not data or not all(k in data for k in ('monto', 'descripcion', 'fecha', 'categoria_id')):
        return jsonify({'msg': 'Datos incompletos'}), 400

    try:
        # Convertir fecha desde el formato ISO 8601
        fecha = date.fromisoformat(data['fecha'])
    except ValueError:
        return jsonify({'msg': 'Formato de fecha inválido. Debe ser YYYY-MM-DD.'}), 400

    nuevo_egreso = Egreso(
        monto=data['monto'],
        descripcion=data['descripcion'],
        fecha=fecha,
        usuario_id=usuario_id,
        categoria_id=data['categoria_id']
    )
    db.session.add(nuevo_egreso)

    # Obtener el usuario para actualizar su capital_actual
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Actualizar el capital_actual RESTANDO el monto del depósito
    usuario.capital_actual -=  float(data['monto'])

    db.session.commit()
    return jsonify({'msg': 'Egreso creado exitosamente'}), 201