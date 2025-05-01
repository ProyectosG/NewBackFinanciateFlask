from flask import Blueprint, request, jsonify
from src.models import db, Suscripcion, Egreso, Usuario, Categoria
from flask_jwt_extended import jwt_required,get_jwt_identity
from datetime import date

# Crear el Blueprint para las rutas de suscripciones
suscripciones_bp = Blueprint('suscripciones', __name__,url_prefix = "/api/suscripcion")

# ------------------------------------------------------
# Ruta para obtener todas las suscripciones de un usuario
@suscripciones_bp.route('/', methods=['GET'])
@jwt_required()
def obtener_suscripciones():
    usuario_id = int(get_jwt_identity())

    suscripciones = Suscripcion.query.filter_by(usuario_id=usuario_id).all()
    response = [suscripcion.to_dict() for suscripcion in suscripciones]
    return jsonify(response), 200

# ------------------------------------------------------
# Ruta para crear una nueva suscripción
@suscripciones_bp.route('/', methods=['POST'])
@jwt_required()
def crear_suscripcion():
    usuario_id = int(get_jwt_identity())
    
    data = request.get_json()

    required_fields = ['nombre', 'costo', 'frecuencia', 'fecha_inicio']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({"error": f"Faltan los siguientes campos: {', '.join(missing_fields)}"}), 400

    try:
        nueva_suscripcion = Suscripcion(
            nombre=data['nombre'],
            costo=data['costo'],
            frecuencia=data['frecuencia'],
            fecha_inicio=date.fromisoformat(data['fecha_inicio']),
            usuario_id=usuario_id
        )

        db.session.add(nueva_suscripcion)
        db.session.commit()

        return jsonify({
            "msg": "Suscripción creada exitosamente",
            "suscripcion": nueva_suscripcion.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error interno al crear la suscripción"}), 500

# ------------------------------------------------------
# Ruta para eliminar una suscripción existente
@suscripciones_bp.route('/', methods=['DELETE'])
@jwt_required()
def eliminar_suscripcion():
    usuario_id = int(get_jwt_identity())
    
    data = request.get_json()
    id_suscripcion = data.get('id')

    suscripcion = Suscripcion.query.get_or_404(id_suscripcion)
    if suscripcion.usuario_id != usuario_id:
        return jsonify({"error": "No tienes permiso para eliminar esta suscripción"}), 403

    db.session.delete(suscripcion)
    db.session.commit()
    return jsonify({'msg': 'Suscripción eliminada exitosamente'}), 200

# ------------------------------------------------------
# Ruta para registrar el pago de una suscripción como egreso
@suscripciones_bp.route('/pagos', methods=['POST'])
@jwt_required()
def pagar_suscripcion():
    usuario_id =int(get_jwt_identity())
    
    data = request.get_json()
    suscripcion_id = data.get('id')

    suscripcion = Suscripcion.query.get(suscripcion_id)
    if not suscripcion or suscripcion.usuario_id != usuario_id:
        return jsonify({"error": "Suscripción no encontrada o no autorizada"}), 404

    try:
        categoria = Categoria.query.filter_by(nombre="Suscripciones").first()
        if not categoria:
            return jsonify({"error": "Categoría 'Suscripciones' no definida"}), 500

        nuevo_egreso = Egreso(
            monto=suscripcion.costo,
            descripcion=f"Pago de suscripción: {suscripcion.nombre}",
            fecha=date.today(),
            usuario_id=usuario_id,
            categoria_id=categoria.id
        )

        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        usuario.capital_actual -= suscripcion.costo

        db.session.add(nuevo_egreso)
        db.session.commit()

        return jsonify({
            "msg": "Pago registrado exitosamente",
            "egreso": nuevo_egreso.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al registrar el pago: {str(e)}"}), 500