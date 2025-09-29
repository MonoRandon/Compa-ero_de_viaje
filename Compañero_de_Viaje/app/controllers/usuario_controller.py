
from flask import Blueprint, render_template, redirect, request, session, flash, url_for
from app.models.usuario import Usuario
from flask import Flask

app = Flask(__name__, template_folder='app/templates')
# Blueprint para usuarios
usuario_bp = Blueprint('usuario', __name__)

# Mostrar formulario de registro y login
@usuario_bp.route('/')
def index():
    return render_template('index.html')

# Crear usuario (Registro)
@usuario_bp.route('/register', methods=['POST'])
def crear_usuario():
    if not Usuario.validar_registro(request.form):
        print('Registro fallido, datos inválidos:', dict(request.form))
        return redirect('/')
    data = {
        'nombre': request.form['nombre'],
        'apellido': request.form['apellido'],
        'email': request.form['email'],
        'password': request.form['password']
    }
    print('Intentando guardar usuario:', data)
    resultado = Usuario.guardar(data)
    print('Resultado de guardar usuario:', resultado)
    flash('Registro exitoso. Ahora inicia sesión para continuar.', 'login')
    return redirect('/')


# Leer usuario (Login)
@usuario_bp.route('/login', methods=['POST'])
def login_usuario():
    email = request.form['email'].strip()
    password = request.form['password'].strip()
    usuario = Usuario.obtener_por_email({'email': email})
    print('DEBUG LOGIN:')
    print('Email recibido:', email)
    print('Password recibido:', password)
    if usuario:
        print('Usuario encontrado:', usuario.email)
        print('Password en BD:', usuario.password)
    if not usuario or usuario.password != password:
        flash('Credenciales inválidas', 'login')
        return redirect('/')
    session['user_id'] = usuario.id
    flash('Inicio de sesión exitoso.', 'login')
    return redirect('/dashboard')

# Actualizar usuario (Ejemplo: actualizar perfil)
@usuario_bp.route('/actualizar', methods=['POST'])
def actualizar_usuario():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id'],
        'nombre': request.form['nombre'],
        'apellido': request.form['apellido'],
        'email': request.form['email']
    }
    Usuario.actualizar(data)
    flash('Perfil actualizado correctamente')
    return redirect('/dashboard')

# Eliminar usuario 
@usuario_bp.route('/borrar', methods=['POST'])
def eliminar_usuario():
    if 'user_id' not in session:
        return redirect('/')
    Usuario.borrar({'id': session['user_id']})
    session.clear()
    flash('Cuenta eliminada')
    return redirect('/')

# Cerrar sesión
@usuario_bp.route('/logout')
def cerrar_sesion():
    session.clear()
    flash('Sesión cerrada correctamente. Por favor inicia sesión de nuevo.', 'login')
    return redirect('/')
