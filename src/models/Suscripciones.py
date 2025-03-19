#archivo src/models/Suscripciones.py
from src.app import db
from datetime import datetime
from datetime import date 

class Suscripcion(db.Model):
    __tablename__ = 'suscripciones'  # Especifica explícitamente el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    costo = db.Column(db.Float, nullable=False)
    frecuencia = db.Column(db.String(50), nullable=False)
    fecha_inicio = db.Column(db.Date, default=date.today, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'costo': self.costo,
            'frecuencia': self.frecuencia,
            'fecha_inicio': self.fecha_inicio.isoformat(),
            'usuario_id': self.usuario_id,
        }