from app import app, db
from models import Rol, Usuario
from sqlalchemy import text

def init_database():
    with app.app_context():
        try:
            # Eliminar restricciones y tablas usando SQL Server específico
            sql_commands = [
                """
                DECLARE @SQL NVARCHAR(MAX) = '';
                
                -- Deshabilitar todas las restricciones FK
                SELECT @SQL = @SQL + 'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id))
                    + '.' + QUOTENAME(OBJECT_NAME(parent_object_id)) 
                    + ' NOCHECK CONSTRAINT ' + QUOTENAME(name) + ';'
                FROM sys.foreign_keys;
                
                -- Eliminar todas las restricciones FK
                SELECT @SQL = @SQL + 'ALTER TABLE ' + QUOTENAME(OBJECT_SCHEMA_NAME(parent_object_id))
                    + '.' + QUOTENAME(OBJECT_NAME(parent_object_id)) 
                    + ' DROP CONSTRAINT ' + QUOTENAME(name) + ';'
                FROM sys.foreign_keys;
                
                EXEC sp_executesql @SQL;
                
                -- Eliminar tablas
                DROP TABLE IF EXISTS reportes;
                DROP TABLE IF EXISTS usuarios;
                DROP TABLE IF EXISTS roles;
                """
            ]
            
            for command in sql_commands:
                db.session.execute(text(command))
            db.session.commit()
            print("Tablas y restricciones eliminadas exitosamente")
            
            # Crear todas las tablas nuevamente
            db.create_all()
            print("Tablas creadas exitosamente")
            
            # Crear roles básicos
            roles = [
                Rol(role_name='admin'),
                Rol(role_name='trabajador'),
                Rol(role_name='usuario')
            ]
            db.session.add_all(roles)
            db.session.commit()
            print("Roles creados exitosamente")

            # Crear usuario admin
            admin = Usuario(
                nombres='Administrador',
                apellidos='Sistema',
                dni='00000000',
                celular='999999999',
                email='admin@sistema.com',
                username='admin',
                role_id=1
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Usuario admin creado exitosamente")
            print("Username: admin")
            print("Password: admin")

        except Exception as e:
            print(f"Error específico: {str(e)}")
            db.session.rollback()
            raise e

if __name__ == "__main__":
    try:
        init_database()
        print("Base de datos inicializada correctamente")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {str(e)}")