from flask import Flask
from app.controllers.usuario_controller import usuario_bp
from app.controllers.viajes_controller import viajes_bp

import os
def create_app():
	ruta_templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'templates')
	app = Flask(__name__, template_folder=ruta_templates)
	app.secret_key = 'SuperLlaveSecreta >:)'
	app.register_blueprint(usuario_bp)
	app.register_blueprint(viajes_bp)
	return app
