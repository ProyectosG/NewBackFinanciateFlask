# src/models/Alertas.py
from src.app import db  # Asegúrate de que esta línea esté aquí
from datetime import datetime  

class Alerta(db.Model):
    __tablename__ = 'alertas'  # Especifica explícitamente el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    mensaje = db.Column(db.String(255), nullable=False)
    leida = db.Column(db.Boolean, default=False)
    creada_en = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    # Relación inversa con Usuario
    usuario = db.relationship('Usuario', backref='alertas', lazy=True)
