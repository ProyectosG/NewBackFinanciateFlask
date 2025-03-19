# src/models/Ingresos.py
from datetime import datetime
from datetime import date 
from src.app import db

class Ingreso(db.Model):
    __tablename__ = 'ingresos'  # Especifica explícitamente el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.String(255))
    fecha = db.Column(db.Date, default=date.today)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'monto': self.monto,
            'descripcion': self.descripcion,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'usuario_id': self.usuario_id,
            'categoria_id': self.categoria_id,
        }