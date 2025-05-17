from flask import Flask, send_from_directory
from .config import Config
from .extensions import db, migrate
from .routes.user_routes import user_bp
from .models import *  # importa todos los modelos

import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(user_bp, url_prefix='/api/users')

    return app
