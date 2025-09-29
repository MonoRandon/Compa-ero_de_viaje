
from flask import Blueprint, render_template, redirect, request, session, flash
from app.models.viajes import Viaje

# Blueprint para viajes
viajes_bp = Blueprint('trips', __name__)

# Leer todos los viajes (Dashboard)
@viajes_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    user_id = session['user_id']
    viajes_propios_unidos = Viaje.viajes_creados_o_unidos(user_id)
    viajes_otros = Viaje.viajes_de_otros(user_id)
    # Para cada viaje propio/unido, marcar si es creador o unido (acceso por diccionario)
    viajes_info = []
    for v in viajes_propios_unidos:
        es_creador = Viaje.es_creador(user_id, v['id'])
        esta_unido = Viaje.usuario_esta_unido(user_id, v['id'])
        v['es_creador'] = es_creador
        v['esta_unido'] = esta_unido
        viajes_info.append(v)
    return render_template('dashboard.html', viajes_info=viajes_info, viajes_otros=viajes_otros)
# Unirse a un viaje de otro usuario
@viajes_bp.route('/unir/<int:viaje_id>', methods=['POST'])
def unirse_viaje(viaje_id):
    if 'user_id' not in session:
        return redirect('/')
    user_id = session['user_id']
    if not Viaje.usuario_esta_unido(user_id, viaje_id):
        Viaje.unirse_a_viaje(user_id, viaje_id)
        flash('Te has unido al viaje.')
    else:
        flash('Ya estás unido a este viaje.')
    return redirect('/dashboard')

# Cancelar unión a un viaje
@viajes_bp.route('/cancelar_union/<int:viaje_id>', methods=['POST'])
def cancelar_union(viaje_id):
    if 'user_id' not in session:
        return redirect('/')
    user_id = session['user_id']
    if Viaje.usuario_esta_unido(user_id, viaje_id):
        Viaje.cancelar_union(user_id, viaje_id)
        flash('Has cancelado tu participación en el viaje.')
    else:
        flash('No estabas unido a este viaje.')
    return redirect('/dashboard')

# Mostrar formulario para crear viaje
@viajes_bp.route('/agregarviaje')
def add_trip():
    return render_template('agregar_viaje.html')

# Crear viaje
@viajes_bp.route('/crearviaje', methods=['POST'])
def crear_viaje():
    if not Viaje.validar_viaje(request.form):
        return redirect('/agregarviaje')
    data = {
        'destino': request.form['destino'],
        'descripcion': request.form['descripcion'],
        'fecha_de_viaje_desde': request.form['fecha_de_viaje_desde'],
        'hora_inicio': request.form.get('hora_inicio') or None,
        'fecha_de_viaje_a': request.form['fecha_de_viaje_a'],
        'hora_fin': request.form.get('hora_fin') or None,
        'usuario_id': session['user_id']
    }
    nuevo_id = Viaje.guardar(data)
    # Unir automáticamente al usuario al viaje creado
    if nuevo_id:
        Viaje.unirse_a_viaje(session['user_id'], nuevo_id)
    return redirect('/dashboard')

# Leer viaje por id (ver detalles)
@viajes_bp.route('/vista/<int:viaje_id>')
def ver_viaje(viaje_id):
    if 'user_id' not in session:
        return redirect('/')
    viaje = Viaje.obtener_por_id({'id': viaje_id})
    usuarios_unidos = Viaje.obtener_usuarios_unidos(viaje_id)
    # Excluir al creador del viaje de la lista de unidos
    usuarios_unidos = [u for u in usuarios_unidos if u['id'] != viaje.usuario_id]
    return render_template('ver_viaje.html', viaje=viaje, usuarios_unidos=usuarios_unidos)

# Mostrar formulario para editar viaje
@viajes_bp.route('/editarviaje/<int:viaje_id>')
def editar_viaje_form(viaje_id):
    viaje = Viaje.obtener_por_id({'id': viaje_id})
    return render_template('agregar_viaje.html', viaje=viaje)

# Actualizar viaje
@viajes_bp.route('/actualizarviaje/<int:viaje_id>', methods=['POST'])
def actualizar_viaje(viaje_id):
    if not Viaje.validar_viaje(request.form):
        return redirect(f'/editarviaje/{viaje_id}')
    data = {
        'id': viaje_id,
        'destino': request.form['destino'],
        'descripcion': request.form['descripcion'],
        'fecha_de_viaje_desde': request.form['fecha_de_viaje_desde'],
        'hora_inicio': request.form.get('hora_inicio') or None,
        'fecha_de_viaje_a': request.form['fecha_de_viaje_a'],
        'hora_fin': request.form.get('hora_fin') or None
    }
    Viaje.actualizar(data)
    flash('Viaje actualizado correctamente')
    return redirect('/dashboard')

# Eliminar viaje
@viajes_bp.route('/borrarviaje/<int:viaje_id>', methods=['POST'])
def borrar_viaje(viaje_id):
    user_id = session['user_id']
    if Viaje.es_creador(user_id, viaje_id):
        Viaje.borrar({'id': viaje_id})
        flash('Viaje eliminado')
    else:
        flash('Solo el creador puede eliminar el viaje.')
    return redirect('/dashboard')
