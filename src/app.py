#src/app.py
from flask import Flask
from src.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import click
from flask.cli import with_appcontext


# Instanciamos la base de datos y las migraciones
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # Cargar la configuración
    app.config.from_object('src.config.Config')

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    #CORS(app)  # Permitir solicitudes de todos los orígenes
    #CORS(app, origins=["https://app-financiate-front.onrender.com"], supports_credentials=True)
    CORS(app, resources={r"/api/*": {"origins": "https://app-financiate-front.onrender.com"}}, supports_credentials=True)



    # Importar los modelos (esto es clave)
    from src.models.Usuarios import Usuario
    from src.models.Categorias import Categoria
    from src.models.Alertas import Alerta
    from src.models.Egresos import Egreso
    from src.models.FondoEmergencias import FondoEmergencia
    from src.models.Ingresos import Ingreso
    from src.models.PlanAhorros import PlanAhorro
    from src.models.Suscripciones import Suscripcion
    
    # Registrar los blueprints
    from src.resources.usuarios import usuarios_bp
    from src.resources.categorias import categorias_bp
    from src.resources.fondos_emergencia import fondos_emergencia_bp
    from src.resources.planahorro import plandeahorro_bp
    from src.resources.ingresos import ingresos_bp
    from src.resources.egresos import egresos_bp

    app.register_blueprint(usuarios_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(fondos_emergencia_bp)
    app.register_blueprint(plandeahorro_bp)
    app.register_blueprint(ingresos_bp)
    app.register_blueprint(egresos_bp)
    
    # Registrar comandos personalizados
    app.cli.add_command(create_db)

    return app

@click.command(name='create_db')
@with_appcontext
def create_db():
    db.drop_all()
    db.create_all()
    print("Base de datos reiniciada correctamente")