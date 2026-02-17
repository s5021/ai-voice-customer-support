from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.models import init_db
def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)
    # Enable CORS
    CORS(app)
    # Initialize database
    init_db(app)
    # Register blueprints
    from app.routes import api
    app.register_blueprint(api)
    return app
