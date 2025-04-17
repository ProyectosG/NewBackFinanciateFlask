# src/schemas/categoria_schema.py
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate
from src.models.Categorias import Categoria

class CategoriaSchema(SQLAlchemyAutoSchema):
    nombre = fields.String(required=True, validate=validate.Length(min=2, max=50))
    icono = fields.String(required=True, validate=validate.Length(min=1, max=10))
    is_default = fields.Boolean()
    user_id = fields.Integer(allow_none=True)

    class Meta:
        model = Categoria
        include_fk = True

# Instancia para uso
categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)
