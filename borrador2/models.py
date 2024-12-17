from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    usuario_id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    celular = db.Column(db.String(20))
    email = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    def get_id(self):
        return str(self.usuario_id)
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Rol(db.Model):
    __tablename__ = 'roles'
    
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)

class Reporte(db.Model):
    __tablename__ = 'reportes'
    
    reporte_id = db.Column(db.Integer, primary_key=True)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    tipo_contaminacion = db.Column(db.String(50), nullable=False)
    imagen_data = db.Column(db.LargeBinary)
    imagen_tipo = db.Column(db.String(50))
    fecha_reporte = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), nullable=False)
    trabajador_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), nullable=True)
    
    creador = db.relationship('Usuario', foreign_keys=[usuario_id], backref='reportes_creados')
    trabajador = db.relationship('Usuario', foreign_keys=[trabajador_id], backref='reportes_atendidos')
    
    fecha_atencion = db.Column(db.DateTime)
    fecha_solucion = db.Column(db.DateTime)
    notas_solucion = db.Column(db.Text)

class AccionReporte(db.Model):
    __tablename__ = 'acciones_reporte'
    
    accion_id = db.Column(db.Integer, primary_key=True)
    reporte_id = db.Column(db.Integer, db.ForeignKey('reportes.reporte_id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), nullable=False)
    tipo_accion = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    imagen_data = db.Column(db.LargeBinary)
    imagen_tipo = db.Column(db.String(50))
    fecha_accion = db.Column(db.DateTime, default=datetime.utcnow)

    reporte = db.relationship('Reporte', backref='acciones')
    usuario = db.relationship('Usuario', backref='acciones_realizadas')

class Notificacion(db.Model):
    __tablename__ = 'notificaciones'
    
    notificacion_id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), nullable=False)
    reporte_id = db.Column(db.Integer, db.ForeignKey('reportes.reporte_id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    leida = db.Column(db.Boolean, default=False)
    
    usuario = db.relationship('Usuario', backref='notificaciones')
    reporte = db.relationship('Reporte', backref='notificaciones')

class Puntuacion(db.Model):
    __tablename__ = 'puntuaciones'
    
    puntuacion_id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), nullable=False)
    asignado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), nullable=False)
    puntos = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], backref='puntuaciones_recibidas')
    asignado_por = db.relationship('Usuario', foreign_keys=[asignado_por_id], backref='puntuaciones_otorgadas')

