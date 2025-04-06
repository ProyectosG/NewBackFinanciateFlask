# src/models/__init__.py

from src.app import db

# Importar modelos aquí si querés tener acceso directo al usarlos en otras partes
from .Categorias import Categoria
from .Usuarios import Usuario
from .Ingresos import Ingreso
from .Egresos import Egreso
