# src/models/FondoEmergencia.py
from datetime import datetime
from src.app import db

class FondoEmergencia(db.Model):
    __tablename__ = 'fondos_emergencia'  # Especifica explícitamente el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    monto_actual = db.Column(db.Float, default=0.0)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    razon = db.Column(db.String(255), nullable=False)
    usuario = db.relationship('Usuario', back_populates='fondos_emergencia', lazy=True)