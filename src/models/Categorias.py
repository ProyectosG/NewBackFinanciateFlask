#src/models/Categorias.py
from datetime import datetime
from src.app import db

class Categoria(db.Model):
    __tablename__ = 'categorias'  # Especifica explícitamente el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    icono = db.Column(db.String(10), nullable=False, unique=True)
    is_default = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    egresos = db.relationship('Egreso', backref='categoria', lazy=True)
    ingresos = db.relationship('Ingreso', backref='categoria', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'icono': self.icono,
            'is_default': self.is_default,
            'usuario_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }