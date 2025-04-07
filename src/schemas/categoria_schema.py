# src/schemas/categoria_schema.py
from marshmallow import Schema, fields, validate
from src.models.Categorias import Categoria
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class CategoriaSchema(SQLAlchemyAutoSchema):
    nombre = fields.String(required=True, validate=validate.Length(min=2, max=50))
    icono = fields.String(required=True, validate=validate.Length(min=1, max=10))
    is_default = fields.Boolean()
    user_id = fields.Integer(allow_none=True)

    class Meta:
        model = Categoria
        load_instance = True
        include_fk = True
