rm -rf migrations  # Borra la carpeta de migraciones
flask --app src.app:create_app db init  # Reinicia las migraciones
flask --app src.app:create_app db migrate -m "Migración inicial"
flask --app src.app:create_app db upgrade