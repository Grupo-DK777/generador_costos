from flask import Flask
from .routes import main_blueprint
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Registrar el Blueprint
    app.register_blueprint(main_blueprint)

    return app
