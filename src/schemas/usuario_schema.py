from marshmallow import validates,ValidationError,fields,Schema

class UsuarioSchema(Schema):
    nombre_usuario = fields.Str(required=True)
    correo = fields.Email(required=True)
    contrasena = fields.Str(required=True)
    
    @validates('nombre_usuario')
    def validate_nombre_usuario(self,value):
        if len(value) < 4:
            raise ValidationError('El nombre de usuario debe tener al menos 4 caracteres')  
        if len(value) > 50:
            raise ValidationError('El nombre de usuario no puede tener más de 50 caracteres')
        
UsuarioSchema
    