from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from models import db, Usuario, Rol, Reporte, AccionReporte, Notificacion, Puntuacion
from config import Config
from datetime import datetime
from flask import send_file
from io import BytesIO

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar la base de datos y el login manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if current_user.role_id != 1:  # Si no es admin
            flash('No tienes permiso para acceder a esta página')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Ruta principal
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role_id == 1:
            return redirect(url_for('admin_panel'))
        elif current_user.role_id == 2:
            return redirect(url_for('trabajador_panel'))
        return redirect(url_for('ver_mis_reportes'))
    return redirect(url_for('login'))
# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.activo:
            login_user(user)
            # Redirigir según el rol del usuario
            if user.role_id in [1, 2]:  # Si es admin o trabajador
                return redirect(url_for('admin_panel'))
            else:  # Si es usuario normal
                return redirect(url_for('index'))
        flash('Usuario o contraseña incorrectos')
    return render_template('auth/login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        try:
            nuevo_usuario = Usuario(
                nombres=request.form.get('nombres'),
                apellidos=request.form.get('apellidos'),
                dni=request.form.get('dni'),
                celular=request.form.get('celular'),
                email=request.form.get('email'),
                username=request.form.get('username'),
                role_id=3  # Usuario normal
            )
            nuevo_usuario.set_password(request.form.get('password'))
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('Registro exitoso. Por favor inicia sesión.')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error en el registro: {str(e)}')
    
    return render_template('auth/registro.html')

@app.route('/registrar-trabajador', methods=['POST'])
@login_required
def registrar_trabajador():
    if current_user.role_id != 1:  # Solo admin puede registrar trabajadores
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        try:
            nuevo_trabajador = Usuario(
                nombres=request.form.get('nombres'),
                apellidos=request.form.get('apellidos'),
                dni=request.form.get('dni'),
                celular=request.form.get('celular'),
                email=request.form.get('email'),
                username=request.form.get('username'),
                role_id=2  # Rol trabajador
            )
            nuevo_trabajador.set_password(request.form.get('password'))
            
            db.session.add(nuevo_trabajador)
            db.session.commit()
            flash('Trabajador registrado exitosamente')
            return redirect(url_for('admin_panel'))  # Actualizado aquí
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar trabajador: {str(e)}')
            return redirect(url_for('admin_panel'))
        
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Rutas de reportes
@app.route('/crear-reporte', methods=['GET', 'POST'])
@login_required
def crear_reporte():
    if request.method == 'POST':
        try:
            # Asegurarnos que el usuario_id sea el del usuario actual
            nuevo_reporte = Reporte(
                latitud=float(request.form.get('latitud')),
                longitud=float(request.form.get('longitud')),
                descripcion=request.form.get('descripcion'),
                tipo_contaminacion=request.form.get('tipo_contaminacion'),
                usuario_id=current_user.usuario_id,  # Aseguramos que sea el usuario actual
                imagen_data=request.files['imagen'].read() if 'imagen' in request.files else None,
                imagen_tipo=request.files['imagen'].content_type if 'imagen' in request.files else None
            )
            
            db.session.add(nuevo_reporte)
            db.session.commit()
            flash('Reporte creado exitosamente')
            return redirect(url_for('ver_mis_reportes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear el reporte: {str(e)}')
    
    return render_template('reportes/crear_reporte.html')
# Ruta para mostrar las imágenes
@app.route('/imagen-reporte/<int:reporte_id>')
def imagen_reporte(reporte_id):
    reporte = Reporte.query.get_or_404(reporte_id)
    if reporte.imagen_data:
        return send_file(
            BytesIO(reporte.imagen_data),
            mimetype=reporte.imagen_tipo
        )
    return 'No hay imagen', 404

# Ruta para ver la imagen de una acción
@app.route('/imagen-accion/<int:accion_id>')
@login_required
def imagen_accion(accion_id):
    accion = AccionReporte.query.get_or_404(accion_id)
    if accion.imagen_data:
        return send_file(
            BytesIO(accion.imagen_data),
            mimetype=accion.imagen_tipo
        )
    return 'No hay imagen', 404

@app.route('/mis-reportes')
@login_required
def ver_mis_reportes():  # Cambié el nombre de la función
    reportes = Reporte.query.filter_by(usuario_id=current_user.usuario_id)\
        .order_by(Reporte.fecha_reporte.desc()).all()
    return render_template('reportes/mis_reportes.html', reportes=reportes)


@app.route('/admin/panel')
@login_required
@admin_required  # Solo necesitamos este decorador
def admin_panel():
    reportes = Reporte.query.order_by(Reporte.fecha_reporte.desc()).all()
    usuarios = Usuario.query.filter_by(role_id=3).all()  # Usuarios normales
    trabajadores = Usuario.query.filter_by(role_id=2).all()  # Trabajadores
    
    return render_template('admin/panel_admin.html', 
                         reportes=reportes,
                         usuarios=usuarios,
                         trabajadores=trabajadores)

@app.route('/trabajador/panel')
@login_required
def trabajador_panel():
    if current_user.role_id != 2:
        flash('No tienes permiso para acceder a esta página')
        return redirect(url_for('index'))
    
    # Obtener reportes asignados al trabajador
    reportes_asignados = Reporte.query.filter_by(
        trabajador_id=current_user.usuario_id
    ).order_by(Reporte.fecha_reporte.desc()).all()
    
    # Obtener reportes pendientes (sin asignar)
    reportes_pendientes = Reporte.query.filter_by(
        estado='pendiente',
        trabajador_id=None
    ).order_by(Reporte.fecha_reporte.desc()).all()
    
    return render_template('trabajador/trabajador_panel.html',
                         reportes_pendientes=reportes_pendientes,
                         reportes_asignados=reportes_asignados)

@app.route('/admin/trabajadores')
@login_required
def admin_trabajadores():
    if current_user.role_id != 1:  # Solo admin
        flash('No tienes permiso para acceder a esta página')
        return redirect(url_for('index'))
    
    # Obtener el filtro del query string
    filtro = request.args.get('filtro', 'activos')  # Por defecto muestra activos
    
    # Aplicar filtro
    query = Usuario.query.filter_by(role_id=2)  # Solo trabajadores
    if filtro == 'activos':
        query = query.filter_by(activo=True)
    elif filtro == 'inactivos':
        query = query.filter_by(activo=False)
    # Si filtro es 'todos', no aplicamos filtro adicional
    
    trabajadores = query.all()
    return render_template('admin/trabajadores.html', trabajadores=trabajadores, filtro_actual=filtro)

@app.route('/admin/editar-trabajador/<int:trabajador_id>', methods=['GET', 'POST'])
@login_required
def editar_trabajador(trabajador_id):
    if current_user.role_id != 1:
        flash('No tienes permiso para acceder a esta página')
        return redirect(url_for('index'))
    
    trabajador = Usuario.query.get_or_404(trabajador_id)
    if request.method == 'POST':
        try:
            trabajador.nombres = request.form.get('nombres')
            trabajador.apellidos = request.form.get('apellidos')
            trabajador.dni = request.form.get('dni')
            trabajador.celular = request.form.get('celular')
            trabajador.email = request.form.get('email')
            
            # Si se proporcionó una nueva contraseña
            nueva_password = request.form.get('password')
            if nueva_password:
                trabajador.set_password(nueva_password)
            
            db.session.commit()
            flash('Trabajador actualizado exitosamente')
            return redirect(url_for('admin_trabajadores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar trabajador: {str(e)}')
    
    return render_template('admin/editar_trabajador.html', trabajador=trabajador)

@app.route('/admin/toggle-estado-trabajador/<int:trabajador_id>', methods=['POST'])
@login_required
def toggle_estado_trabajador(trabajador_id):
    if current_user.role_id != 1:
        return redirect(url_for('index'))
    
    trabajador = Usuario.query.get_or_404(trabajador_id)
    try:
        trabajador.activo = not trabajador.activo
        db.session.commit()
        estado = "activado" if trabajador.activo else "desactivado"
        flash(f'Trabajador {estado} exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar estado del trabajador: {str(e)}')
    
    return redirect(url_for('admin_trabajadores'))

@app.route('/atender-reporte/<int:reporte_id>', methods=['POST'])
@login_required
def atender_reporte(reporte_id):
    if current_user.role_id not in [1, 2]:
        return redirect(url_for('index'))
        
    reporte = Reporte.query.get_or_404(reporte_id)
    
    # Verificar que el reporte no esté ya atendido
    if reporte.estado != 'pendiente':
        flash('Este reporte ya está siendo atendido')
        return redirect(url_for('admin_panel'))
    
    try:
        reporte.estado = 'en_proceso'
        reporte.trabajador_id = current_user.usuario_id  # Asignar al trabajador actual
        reporte.fecha_atencion = datetime.utcnow()
        
        db.session.commit()
        
        # Crear notificación para el usuario
        crear_notificacion(
            usuario_id=reporte.usuario_id,
            reporte_id=reporte_id,
            tipo='reporte_en_proceso',
            mensaje=f'Tu reporte ha sido asignado a {current_user.nombres} {current_user.apellidos}'
        )
        
        flash('Reporte marcado como en proceso')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar el reporte: {str(e)}')
    
    return redirect(url_for('admin_panel'))

@app.route('/agregar-accion/<int:reporte_id>', methods=['POST'])
@login_required
def agregar_accion(reporte_id):
    if current_user.role_id not in [1, 2]:
        return redirect(url_for('index'))
        
    reporte = Reporte.query.get_or_404(reporte_id)
    descripcion = request.form.get('descripcion')
    
    try:
        # Agregar la acción
        accion = AccionReporte(
            reporte_id=reporte_id,
            usuario_id=current_user.usuario_id,
            tipo_accion='comentario',
            descripcion=descripcion
        )
        db.session.add(accion)
        
        # Crear notificación
        mensaje = f"Se ha agregado un nuevo comentario en tu reporte: '{descripcion[:100]}...'"
        crear_notificacion(
            usuario_id=reporte.usuario_id,
            reporte_id=reporte_id,
            tipo='nuevo_comentario',
            mensaje=mensaje
        )
        
        db.session.commit()
        flash('Acción registrada exitosamente')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar la acción: {str(e)}')
    
    return redirect(url_for('admin_panel'))

@app.route('/marcar-solucionado/<int:reporte_id>', methods=['POST'])
@login_required
def marcar_solucionado(reporte_id):
    if current_user.role_id not in [1, 2]:
        return redirect(url_for('index'))
        
    reporte = Reporte.query.get_or_404(reporte_id)
    notas = request.form.get('notas_solucion')
    
    try:
        reporte.estado = 'solucionado'
        reporte.fecha_solucion = datetime.utcnow()
        reporte.notas_solucion = notas
        
        # Crear notificación
        mensaje = f"Tu reporte ha sido marcado como solucionado. Notas: {notas}"
        crear_notificacion(
            usuario_id=reporte.usuario_id,
            reporte_id=reporte_id,
            tipo='reporte_solucionado',
            mensaje=mensaje
        )
        
        db.session.commit()
        flash('Reporte marcado como solucionado')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar el reporte: {str(e)}')
    
    return redirect(url_for('admin_panel'))

@app.route('/reportes-usuario/<int:usuario_id>')
@login_required
def ver_reportes_usuario(usuario_id):
    if current_user.role_id not in [1, 2] and current_user.usuario_id != usuario_id:
        flash('No tienes permiso para ver estos reportes')
        return redirect(url_for('index'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    reportes = Reporte.query.filter_by(
        usuario_id=usuario_id
    ).order_by(Reporte.fecha_reporte.desc()).all()
    
    return render_template(
        'reportes/reportes_usuario.html',
        reportes=reportes,
        usuario=usuario
    )

# ruta para ver un reporte específico
@app.route('/reporte/<int:reporte_id>')
@login_required
def ver_reporte(reporte_id):
    reporte = Reporte.query.get_or_404(reporte_id)
    
    # Verificar permisos
    if current_user.role_id not in [1, 2] and reporte.usuario_id != current_user.usuario_id:
        flash('No tienes permiso para ver este reporte')
        return redirect(url_for('index'))
    
    return render_template('reportes/ver_reporte.html', reporte=reporte)

@app.route('/ranking')
@login_required
def ranking_usuarios():
    # Consulta para obtener usuarios con sus puntuaciones
    usuarios_con_puntos = db.session.query(
        Usuario.usuario_id,
        Usuario.nombres,
        Usuario.apellidos,
        Usuario.dni,
        Usuario.celular,
        Usuario.email,
        Usuario.username,
        db.func.coalesce(db.func.sum(Puntuacion.puntos), 0).label('total_puntos')
    ).outerjoin(
        Puntuacion, Usuario.usuario_id == Puntuacion.usuario_id
    ).filter(
        Usuario.role_id == 3  # Solo usuarios normales
    ).group_by(
        Usuario.usuario_id,
        Usuario.nombres,
        Usuario.apellidos,
        Usuario.dni,
        Usuario.celular,
        Usuario.email,
        Usuario.username
    ).order_by(
        db.desc('total_puntos')
    ).all()

    # Obtener historial de puntuaciones para cada usuario
    historiales = {}
    for usuario in db.session.query(Usuario).filter_by(role_id=3):
        historiales[usuario.usuario_id] = db.session.query(
            Puntuacion
        ).filter_by(
            usuario_id=usuario.usuario_id
        ).order_by(
            Puntuacion.fecha.desc()
        ).all()

    return render_template('ranking.html', 
                           ranking=usuarios_con_puntos,
                           historiales=historiales)


@app.route('/notificaciones')
@login_required
def ver_notificaciones():
    # Obtener notificaciones del usuario ordenadas por fecha
    notificaciones = Notificacion.query.filter_by(
        usuario_id=current_user.usuario_id
    ).order_by(Notificacion.fecha.desc()).all()
    
    return render_template('notificaciones/panel.html', notificaciones=notificaciones)

@app.route('/marcar-notificacion-leida/<int:notificacion_id>')
@login_required
def marcar_notificacion_leida(notificacion_id):
    notificacion = Notificacion.query.get_or_404(notificacion_id)
    if notificacion.usuario_id == current_user.usuario_id:
        notificacion.leida = True
        db.session.commit()
    return redirect(url_for('ver_notificaciones'))

@app.route('/marcar-todas-leidas')
@login_required
def marcar_todas_leidas():
    Notificacion.query.filter_by(
        usuario_id=current_user.usuario_id,
        leida=False
    ).update({Notificacion.leida: True})
    db.session.commit()
    return redirect(url_for('ver_notificaciones'))

# Función auxiliar para obtener el conteo de notificaciones no leídas
def get_notificaciones_no_leidas():
    return Notificacion.query.filter_by(
        usuario_id=current_user.usuario_id,
        leida=False
    ).count()

# Hacer disponible el conteo de notificaciones en todos los templates
@app.context_processor
def utility_processor():
    def notificaciones_no_leidas():
        if current_user.is_authenticated:
            return Notificacion.query.filter_by(
                usuario_id=current_user.usuario_id,
                leida=False
            ).count()
        return 0
    return dict(notificaciones_no_leidas=notificaciones_no_leidas,
                enumerate=enumerate)  # Agregamos enumerate aquí.
                
def crear_notificacion(usuario_id, reporte_id, tipo, mensaje):
    """Función auxiliar para crear notificaciones"""
    notificacion = Notificacion(
        usuario_id=usuario_id,
        reporte_id=reporte_id,
        tipo=tipo,
        mensaje=mensaje
    )
    db.session.add(notificacion)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear notificación: {str(e)}")

@app.context_processor
def utility_processor():
    def notificaciones_no_leidas():
        if current_user.is_authenticated:
            return Notificacion.query.filter_by(
                usuario_id=current_user.usuario_id,
                leida=False
            ).count()
        return 0
    return dict(notificaciones_no_leidas=notificaciones_no_leidas)

# En app.py
@app.route('/asignar-puntos/<int:usuario_id>', methods=['POST'])
@login_required
def asignar_puntos(usuario_id):
    # Verificar que solo admin y trabajadores puedan asignar puntos
    if current_user.role_id not in [1, 2]:
        flash('No tienes permiso para asignar puntos')
        return redirect(url_for('ranking_usuarios'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    puntos = int(request.form.get('puntos', 0))
    motivo = request.form.get('motivo', '')
    
    try:
        nueva_puntuacion = Puntuacion(
            usuario_id=usuario_id,
            asignado_por_id=current_user.usuario_id,
            puntos=puntos,
            motivo=motivo
        )
        db.session.add(nueva_puntuacion)
        db.session.commit()
        flash(f'Se han asignado {puntos} puntos a {usuario.nombres} {usuario.apellidos}')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al asignar puntos: {str(e)}')
    
    return redirect(url_for('ranking_usuarios'))

@app.route('/mapa-reportes')
@login_required
def mapa_reportes():
    # Obtener usuarios (suponiendo que tienes un modelo llamado Usuario)
    usuarios = db.session.query(Usuario).filter_by(role_id=3).all()

    # Obtener reportes
    reportes = db.session.query(Reporte).all()

    return render_template('reportes/mapa_reportes.html', usuarios=usuarios, reportes=reportes)

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Tablas creadas exitosamente!")
        except Exception as e:
            print("Error creando las tablas:", str(e))
    app.run(debug=True)
