# src/schemas/categoria_schema.py

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from src.models.Categorias import Categoria

class CategoriaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Categoria
        load_instance = True
        include_fk = True  # Para incluir user_id
