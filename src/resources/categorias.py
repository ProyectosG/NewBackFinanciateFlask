# src/resources/categorias.py

from flask import Blueprint, request, jsonify
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models import db, Categoria, Ingreso, Egreso
from src.schemas.categoria_schema import CategoriaSchema
from .default_categories import default_categories
from sqlalchemy import exists
from marshmallow import ValidationError

categorias_bp = Blueprint('categorias', __name__, url_prefix='/api/categorias')

categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)



# GET: Traer todas las categorías (default + del usuario)
@categorias_bp.route('/traertodas', methods=['GET'])
@jwt_required()
def listar_categorias():
    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"msg": "Token inválido o expirado"}), 401

    # Obtener categorías predeterminadas
    default = Categoria.query.filter_by(is_default=True).all()

    # Obtener categorías asociadas al usuario
    personales = Categoria.query.filter_by(user_id=user_id).all()

    # Combinar las listas de categorías (predeterminadas + personales)
    all_categorias = sorted(default + personales, key=lambda c: c.nombre)

    # Convertir manualmente los objetos a diccionarios
    categorias_list = []
    for categoria in all_categorias:
        categoria_dict = {
            'id': categoria.id,
            'nombre': categoria.nombre,
            'icono': categoria.icono,
            'is_default': categoria.is_default,
            #'user_id': categoria.user_id,
            'created_at': categoria.created_at.isoformat()  # Convertir a string
        }
        categorias_list.append(categoria_dict)

    # Retornar las categorías como una respuesta JSON
    return jsonify(categorias_list), 200




# POST: Crear nueva categoría
@categorias_bp.route('/categoria', methods=['POST'])
@jwt_required()
def crear_categoria():
    user_id = get_jwt_identity()
    try:
        data = categoria_schema.load(request.get_json())  # <-- validación automática
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    # Verificar duplicado (esto sigue igual)
    if Categoria.query.filter_by(nombre=data['nombre'], user_id=user_id).first():
        return jsonify({'error': 'La categoría ya existe'}), 400

    nueva_categoria = Categoria(
        nombre=data['nombre'],
        icono=data['icono'],
        user_id=user_id,
        is_default=False
    )

    db.session.add(nueva_categoria)
    db.session.commit()
    return categoria_schema.jsonify(nueva_categoria), 201


# DELETE: Eliminar una categoría
@categorias_bp.route('/categoria', methods=['DELETE'])
@jwt_required()
def eliminar_categoria():
    data = request.get_json()
    categoria_id = data.get('id')
    categoria = Categoria.query.get(categoria_id)

    if not categoria:
        return jsonify({'error': 'Categoría no encontrada'}), 404

    if categoria.is_default:
        return jsonify({'error': 'No se puede eliminar una categoría por defecto'}), 400

    ingresos = Ingreso.query.filter_by(categoria_id=categoria_id).count()
    egresos = Egreso.query.filter_by(categoria_id=categoria_id).count()

    if ingresos > 0 or egresos > 0:
        return jsonify({
            'error': 'La categoría está relacionada con movimientos',
            'detalles': {
                'ingresos': ingresos,
                'egresos': egresos
            }
        }), 400

    db.session.delete(categoria)
    db.session.commit()
    return jsonify({'msg': 'Categoría eliminada correctamente'}), 200

# DELETE: Eliminar todas las categorías del usuario (si no están relacionadas)
@categorias_bp.route('/eliminartodas', methods=['DELETE'])
@jwt_required()
def eliminar_todas_las_categorias():
    user_id = get_jwt_identity()
    categorias = Categoria.query.filter_by(user_id=user_id).all()

    if not categorias:
        return jsonify({'msg': 'No hay categorías para eliminar'}), 200

    no_usadas = []
    usadas = []

    for cat in categorias:
        ingresos = Ingreso.query.filter_by(categoria_id=cat.id).count()
        egresos = Egreso.query.filter_by(categoria_id=cat.id).count()

        if ingresos == 0 and egresos == 0:
            no_usadas.append(cat)
        else:
            usadas.append({
                'id': cat.id,
                'nombre': cat.nombre,
                'ingresos': ingresos,
                'egresos': egresos
            })

    for cat in no_usadas:
        db.session.delete(cat)

    db.session.commit()

    return jsonify({
        'msg': f'{len(no_usadas)} categorías eliminadas.',
        'comprometidas': usadas
    }), 200

# POST: Insertar categorías por defecto
@categorias_bp.route('/default', methods=['POST'])
def insertar_categorias_por_defecto():
    try:
        for cat in default_categories:
            exists_query = Categoria.query.filter_by(nombre=cat['nombre'], is_default=True).first()
            if not exists_query:
                nueva = Categoria(
                    nombre=cat['nombre'],
                    icono=cat['icono'],
                    is_default=True,
                    user_id=None
                )
                db.session.add(nueva)
        db.session.commit()
        return jsonify({'msg': 'Categorías por defecto insertadas'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al insertar', 'detalles': str(e)}), 500
