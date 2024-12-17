from app import app, db
from models import Notificacion
from sqlalchemy import inspect

def add_notificaciones_table():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            if 'notificaciones' not in inspector.get_table_names():
                Notificacion.__table__.create(db.engine)
                print("Tabla notificaciones creada exitosamente")
            else:
                print("La tabla notificaciones ya existe")
                
        except Exception as e:
            print(f"Error al crear la tabla: {str(e)}")
            raise e

if __name__ == "__main__":
    try:
        add_notificaciones_table()
    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")