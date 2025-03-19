from flask import Blueprint, request, jsonify
from ..models.Usuarios import Usuario, db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Missing fields"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user:
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Missing fields"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        token = user.generate_token()
        return jsonify(access_token=token), 200

    return jsonify({"msg": "Invalid credentials"}), 401
