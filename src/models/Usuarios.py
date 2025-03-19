from src.app import db
from datetime import datetime
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

# Modelo de Usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'  # Especifica explícitamente el nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre_usuario = db.Column(db.String(50), nullable=False, unique=True)
    correo = db.Column(db.String(120), nullable=False, unique=True)
    contrasena_hash = db.Column(db.String(128), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    capital_inicial = db.Column(db.Float, nullable=True, default=0.00)
    capital_actual = db.Column(db.Float, nullable=True, default=0.00)
    moneda = db.Column(db.String(10), nullable=True, default=None)  # Moneda del usuario

    ingresos = db.relationship('Ingreso', backref='usuario', lazy=True)
    egresos = db.relationship('Egreso', backref='usuario', lazy=True)
    planes_ahorro = db.relationship('PlanAhorro', backref='usuario', lazy=True)
    fondos_emergencia = db.relationship('FondoEmergencia', lazy=True, back_populates='usuario')
    suscripciones = db.relationship('Suscripcion', backref='usuario', lazy=True)
    alertas = db.relationship('Alerta', backref='usuario', lazy=True)

    def establecer_contrasena(self, contrasena):
        """Encripta la contraseña usando SHA-256 y la trunca a 80 caracteres."""
        sha256_hash = hashlib.sha256(contrasena.encode('utf-8')).hexdigest()
        self.contrasena_hash = sha256_hash[:80]  # Asegurarnos de que no sobrepase los 80 caracteres

    def verificar_contrasena(self, contrasena):
        """Verifica si la contraseña ingresada es correcta comparándola con la encriptada."""
        sha256_hash = hashlib.sha256(contrasena.encode('utf-8')).hexdigest()
        return self.contrasena_hash == sha256_hash[:80]  # Comparar solo los primeros 80 caracteres

    def to_dict(self):
        """Convierte el objeto Usuario en un diccionario."""
        return {
            'id': self.id,
            'nombre_usuario': self.nombre_usuario,
            'correo': self.correo,
            'capital_inicial': self.capital_inicial,
            'capital_actual': self.capital_actual,
            'moneda': self.moneda,
            'creado_en': self.creado_en.isoformat()  # Convertir a formato ISO 8601
        }

    def calcular_totales(self):
        """Calcula los totales de ingresos y egresos del usuario."""
        total_ingresos = sum(ingreso.monto for ingreso in self.ingresos)
        total_egresos = sum(egreso.monto for egreso in self.egresos)
        return {
            "capital_inicial": self.capital_inicial,
            "total_ingresos": total_ingresos,
            "total_egresos": total_egresos,
            "capital_actual": self.capital_actual,
        }
