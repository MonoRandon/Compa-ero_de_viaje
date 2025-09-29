
from app.config.mysqlconnection import MySQLConnection
from flask import flash

class Usuario:
    def __init__(self, data):
        self.id = data.get('id')
        self.nombre = data.get('nombre')
        self.apellido = data.get('apellido')
        self.email = data.get('email')
        self.password = data.get('password')

    # Crear usuario
    @classmethod
    def guardar(cls, data):
        query = """
        INSERT INTO usuarios (nombre, apellido, email, password) VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s);
        """
        return MySQLConnection('compañero_de_viaje_db').query_db(query, data)

    # Leer usuario por email
    @classmethod
    def obtener_por_email(cls, data):
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        resultado = MySQLConnection('compañero_de_viaje_db').query_db(query, data)
        if resultado:
            return cls(resultado[0])
        return None

    # Leer usuario por id
    @classmethod
    def obtener_por_id(cls, data):
        query = "SELECT * FROM usuarios WHERE id = %(id)s;"
        resultado = MySQLConnection('compañero_de_viaje_db').query_db(query, data)
        if resultado:
            return cls(resultado[0])
        return None

    # Actualizar usuario
    @classmethod
    def actualizar(cls, data):
        query = """
        UPDATE usuarios SET nombre=%(nombre)s, apellido=%(apellido)s, email=%(email)s WHERE id=%(id)s;
        """
        return MySQLConnection('compañero_de_viaje_db').query_db(query, data)

    # Eliminar usuario
    @classmethod
    def borrar(cls, data):
        query = "DELETE FROM usuarios WHERE id = %(id)s;"
        return MySQLConnection('compañero_de_viaje_db').query_db(query, data)

    # Validar registro
    @classmethod
    def validar_registro(cls, form):
        import re
        is_valid = True
        # Validar nombre
        if len(form['nombre']) < 3:
            flash('El nombre debe tener al menos 3 caracteres.', 'registro')
            is_valid = False
        # Validar apellido
        if len(form['apellido']) < 3:
            flash('El apellido debe tener al menos 3 caracteres.', 'registro')
            is_valid = False
        # Validar email formato
        email_regex = r'^\S+@\S+\.\S+$'
        if not re.match(email_regex, form['email']):
            flash('Email inválido.', 'registro')
            is_valid = False
        # Validar email único
        if cls.obtener_por_email({'email': form['email']}):
            flash('El email ya está registrado.', 'registro')
            is_valid = False
        # Validar password
        if len(form['password']) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'registro')
            is_valid = False
        # Validar confirmación de password
        if 'confirmar' in form and form['password'] != form['confirmar']:
            flash('Las contraseñas no coinciden.', 'registro')
            is_valid = False
        return is_valid
        if len(form['apellido']) < 3:
            flash('El apellido debe tener al menos 3 caracteres.', 'registro')
            is_valid = False
        if not form['email']:
            flash('El email es obligatorio.', 'registro')
            is_valid = False
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", form['email']):
            flash('El email no es válido.', 'registro')
            is_valid = False
        else:
            # Validar que el email no esté repetido
            from app.models.usuario import Usuario
            if Usuario.obtener_por_email({'email': form['email']}):
                flash('El email ya está registrado.', 'registro')
                is_valid = False
        if len(form['password']) < 8:
            flash('La contraseña debe tener al menos 8 caracteres.', 'registro')
            is_valid = False
        if form['password'] != form.get('confirmar', 'Error'):
            flash('Las contraseñas no coinciden.', 'registro')
            is_valid = False
        return is_valid
