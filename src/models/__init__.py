from flask_sqlalchemy import SQLAlchemy
# Instanciar la base de datos
db = SQLAlchemy()

from .usuario_schema import UsuarioSchema
from .categoria_schema import CategoriaSchema
