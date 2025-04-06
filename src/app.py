from flask import Flask
from src.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

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
    CORS(app, origins=["https://reliable-sorbet-07d22a.netlify.app"], supports_credentials=True)


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

    app.register_blueprint(usuarios_bp)
    app.register_blueprint(categorias_bp)
    



    return app
