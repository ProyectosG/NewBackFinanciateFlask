# src/models/PlanAhorros.py
from datetime import datetime
from datetime import date 
from src.app import db

class PlanAhorro(db.Model):
    __tablename__ = 'planes_ahorro'  # Especifica explícitamente el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre_plan = db.Column(db.String(255))
    fecha_inicio = db.Column(db.Date, default=date.today)
    monto_inicial = db.Column(db.Float, default=0.0)
    fecha_objetivo = db.Column(db.Date, default=date.today)
    monto_objetivo = db.Column(db.Float, nullable=False)
    monto_acumulado = db.Column(db.Float, default=0.0)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    egresos = db.relationship('Egreso', back_populates='plan_ahorro', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre_plan': self.nombre_plan,
            'monto_inicial': self.monto_inicial,
            'monto_objetivo': self.monto_objetivo,
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'fecha_objetivo': self.fecha_objetivo.isoformat(),
            'monto_acumulado': self.monto_acumulado,
            'usuario_id': self.usuario_id,
        }