from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu-clave-secreta-aqui')
    
    # Configuración de SQL Server usando pyodbc
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://lindell:1234567l@software2.mssql.somee.com/software2?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    
    # Configuración adicional de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_TIMEOUT = 10
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_size': 5
    }


"""class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'tu-clave-secreta-aqui')
    
    # Configuración de SQL Server para base de datos local
    #SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://LAPTOP-LN995LSI@localhost:1433/software2?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://localhost/LAPTOP-LN995LSI?driver=ODBC+Driver+17+for+SQL+Server;Trusted_Connection=yes"

    # Configuración adicional de SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_TIMEOUT = 10
    SQLALCHEMY_POOL_RECYCLE = 280
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_size': 5
    }"""