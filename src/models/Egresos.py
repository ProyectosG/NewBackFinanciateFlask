# src/models/Egresos.py
from datetime import datetime
from datetime import date 
from src.app import db  # Asegúrate de que esta línea esté aquí

class Egreso(db.Model):
    __tablename__ = 'egresos'  # Especifica explícitamente el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(255))
    fecha = db.Column(db.Date, default=date.today)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    plan_ahorro_id = db.Column(db.Integer, db.ForeignKey('planes_ahorro.id'), nullable=True)

    plan_ahorro = db.relationship('PlanAhorro', back_populates='egresos', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'monto': self.monto,
            'descripcion': self.descripcion,
            'fecha': self.fecha.isoformat(),
            'usuario_id': self.usuario_id,
            'categoria_id': self.categoria_id,
            'plan_ahorro_id': self.plan_ahorro_id,
        }
