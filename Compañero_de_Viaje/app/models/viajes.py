
from app.config.mysqlconnection import MySQLConnection
from flask import flash

class Viaje:
    # Saber si un usuario está unido a un viaje
    @staticmethod
    def usuario_esta_unido(usuario_id, viaje_id):
        query = "SELECT * FROM usuarios_unidos WHERE usuario_id = %(usuario_id)s AND viaje_id = %(viaje_id)s;"
        res = MySQLConnection('compañero_de_viaje_db').query_db(query, {'usuario_id': usuario_id, 'viaje_id': viaje_id})
        return bool(res)

    # Saber si un usuario es el creador de un viaje
    @staticmethod
    def es_creador(usuario_id, viaje_id):
        query = "SELECT * FROM viajes WHERE id = %(viaje_id)s AND usuario_id = %(usuario_id)s;"
        res = MySQLConnection('compañero_de_viaje_db').query_db(query, {'usuario_id': usuario_id, 'viaje_id': viaje_id})
        return bool(res)

    @staticmethod
    def obtener_usuarios_unidos(viaje_id):
        query = '''
        SELECT u.* FROM usuarios_unidos uu
        JOIN usuarios u ON uu.usuario_id = u.id
        WHERE uu.viaje_id = %(viaje_id)s
        '''
        return MySQLConnection('compañero_de_viaje_db').query_db(query, {'viaje_id': viaje_id})

# --- NUEVAS FUNCIONES PARA DASHBOARD Y UNIRSE/CANCELAR ---
    @classmethod
    def viajes_creados_o_unidos(cls, usuario_id):
        from datetime import timedelta
        query = '''
        SELECT v.id, v.destino, v.descripcion, v.fecha_de_viaje_desde, v.hora_inicio, v.fecha_de_viaje_a, v.hora_fin, v.usuario_id, v.created_at, v.updated_at, u.nombre as planificador_nombre, u.apellido as planificador_apellido
        FROM viajes v
        JOIN usuarios u ON v.usuario_id = u.id
        WHERE v.usuario_id = %(usuario_id)s
        UNION
        SELECT v.id, v.destino, v.descripcion, v.fecha_de_viaje_desde, v.hora_inicio, v.fecha_de_viaje_a, v.hora_fin, v.usuario_id, v.created_at, v.updated_at, u.nombre as planificador_nombre, u.apellido as planificador_apellido
        FROM viajes v
        JOIN usuarios u ON v.usuario_id = u.id
        JOIN usuarios_unidos uu ON v.id = uu.viaje_id
        WHERE uu.usuario_id = %(usuario_id)s
        '''
        resultados = MySQLConnection('compañero_de_viaje_db').query_db(query, {'usuario_id': usuario_id})
        viajes = []
        ids_vistos = set()
        for row in resultados or []:
            d = dict(row)
            if d['id'] in ids_vistos:
                continue
            ids_vistos.add(d['id'])
            for campo in ['hora_inicio', 'hora_fin']:
                valor = d.get(campo)
                if isinstance(valor, timedelta):
                    total_seconds = int(valor.total_seconds())
                    horas = total_seconds // 3600
                    minutos = (total_seconds % 3600) // 60
                    d[campo] = f"{horas:02d}:{minutos:02d}"
                elif valor is not None:
                    d[campo] = str(valor)[:5]
            viajes.append(d)
        return viajes

    @classmethod
    def viajes_de_otros(cls, usuario_id):
        from datetime import timedelta
        query = '''
        SELECT v.id, v.destino, v.descripcion, v.fecha_de_viaje_desde, v.hora_inicio, v.fecha_de_viaje_a, v.hora_fin, v.usuario_id, v.created_at, v.updated_at, u.nombre as planificador_nombre, u.apellido as planificador_apellido
        FROM viajes v
        JOIN usuarios u ON v.usuario_id = u.id
        WHERE v.id NOT IN (
            SELECT viaje_id FROM usuarios_unidos WHERE usuario_id = %(usuario_id)s
        )
        '''
        resultados = MySQLConnection('compañero_de_viaje_db').query_db(query, {'usuario_id': usuario_id})
        viajes = []
        for row in resultados or []:
            d = dict(row)
            for campo in ['hora_inicio', 'hora_fin']:
                valor = d.get(campo)
                if isinstance(valor, timedelta):
                    total_seconds = int(valor.total_seconds())
                    horas = total_seconds // 3600
                    minutos = (total_seconds % 3600) // 60
                    d[campo] = f"{horas:02d}:{minutos:02d}"
                elif valor is not None:
                    d[campo] = str(valor)[:5]
            viajes.append(d)
        return viajes

    @staticmethod
    def unirse_a_viaje(usuario_id, viaje_id):
        query = "INSERT INTO usuarios_unidos (usuario_id, viaje_id) VALUES (%(usuario_id)s, %(viaje_id)s);"
        return MySQLConnection('compañero_de_viaje_db').query_db(query, {'usuario_id': usuario_id, 'viaje_id': viaje_id})

    @staticmethod
    def cancelar_union(usuario_id, viaje_id):
        query = "DELETE FROM usuarios_unidos WHERE usuario_id = %(usuario_id)s AND viaje_id = %(viaje_id)s;"
        return MySQLConnection('compañero_de_viaje_db').query_db(query, {'usuario_id': usuario_id, 'viaje_id': viaje_id})
    def __init__(self, data):
        self.id = data.get('id')
        self.destino = data.get('destino')
        self.descripcion = data.get('descripcion')
        self.fecha_de_viaje_desde = data.get('fecha_de_viaje_desde')
        self.hora_inicio = data.get('hora_inicio')
        self.fecha_de_viaje_a = data.get('fecha_de_viaje_a')
        self.hora_fin = data.get('hora_fin')
        self.usuario_id = data.get('usuario_id')

    # Crear viaje
    @classmethod
    def guardar(cls, data):
        query = """
        INSERT INTO viajes (destino, descripcion, fecha_de_viaje_desde, hora_inicio, fecha_de_viaje_a, hora_fin, usuario_id)
        VALUES (%(destino)s, %(descripcion)s, %(fecha_de_viaje_desde)s, %(hora_inicio)s, %(fecha_de_viaje_a)s, %(hora_fin)s, %(usuario_id)s);
        """
        return MySQLConnection('compañero_de_viaje_db').query_db(query, data)

    # Leer viaje por id
    @classmethod
    def obtener_por_id(cls, data):
        query = "SELECT * FROM viajes WHERE id = %(id)s;"
        resultado = MySQLConnection('compañero_de_viaje_db').query_db(query, data)
        if resultado:
            return cls(resultado[0])
        return None

    # Leer todos los viajes
    @classmethod
    def obtener_todo(cls):
        query = "SELECT * FROM viajes;"
        resultados = MySQLConnection('compañero_de_viaje_db').query_db(query)
        return [cls(row) for row in resultados] if resultados else []

    # Actualizar viaje
    @classmethod
    def actualizar(cls, data):
        query = """
        UPDATE viajes SET destino=%(destino)s, descripcion=%(descripcion)s, fecha_de_viaje_desde=%(fecha_de_viaje_desde)s, hora_inicio=%(hora_inicio)s, fecha_de_viaje_a=%(fecha_de_viaje_a)s, hora_fin=%(hora_fin)s 
        WHERE id=%(id)s;
        """
        return MySQLConnection('compañero_de_viaje_db').query_db(query, data)

    # Eliminar viaje
    @classmethod
    def borrar(cls, datos):
        query = "DELETE FROM viajes WHERE id = %(id)s;"
        return MySQLConnection('compañero_de_viaje_db').query_db(query, datos)

    # Validar viaje
    @staticmethod
    def validar_viaje(form):
        from datetime import datetime
        is_valid = True
        if not form['destino']:
            flash('El destino es obligatorio.', 'viaje')
            is_valid = False
        if not form['descripcion']:
            flash('La descripción es obligatoria.', 'viaje')
            is_valid = False
        if not form['fecha_de_viaje_desde'] or not form['fecha_de_viaje_a']:
            flash('Las fechas de viaje son obligatorias.', 'viaje')
            is_valid = False
        else:
            try:
                fecha_desde = datetime.strptime(form['fecha_de_viaje_desde'], '%Y-%m-%d')
                fecha_a = datetime.strptime(form['fecha_de_viaje_a'], '%Y-%m-%d')
                if fecha_a < fecha_desde:
                    flash('La fecha de fin debe ser posterior a la de inicio.', 'viaje')
                    is_valid = False
                if fecha_desde < datetime.now():
                    flash('La fecha de inicio debe ser futura.', 'viaje')
                    is_valid = False
            except Exception:
                flash('Formato de fecha inválido.', 'viaje')
                is_valid = False
        return is_valid
