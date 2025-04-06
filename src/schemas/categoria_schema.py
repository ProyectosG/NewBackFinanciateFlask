from marshmallow import Schema, fields, validates, ValidationError

class CategoriaSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True)
    icono = fields.Str(required=True)
    is_default = fields.Boolean(default=False)
    usuario_id = fields.Int(required=False)

    @validates('nombre')
    def validate_nombre(self, value):
        if len(value) < 3:
            raise ValidationError('El nombre de la categoría debe tener al menos 3 caracteres.')
        if len(value) > 50:
            raise ValidationError('El nombre de la categoría no puede tener más de 50 caracteres.')
    
    @validates('icono')
    def validate_icono(self, value):
        if len(value) < 3:
            raise ValidationError('El ícono debe tener al menos 3 caracteres.')
        if len(value) > 10:
            raise ValidationError('El ícono no puede tener más de 10 caracteres.')

    def to_dict(self, obj):
        """
        Método para convertir el objeto Categoria en un diccionario.
        """
        return {
            'id': obj.id,
            'nombre': obj.nombre,
            'icono': obj.icono,
            'is_default': obj.is_default,
            'usuario_id': obj.usuario_id
        }
