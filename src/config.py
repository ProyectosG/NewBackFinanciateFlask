import os
from dotenv import load_dotenv

# Cargar las variables de entorno del archivo .env
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  # Cambia a algo más seguro
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  # URL de conexión de Render
