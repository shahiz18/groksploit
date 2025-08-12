from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()
db = SQLAlchemy()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1000))
API_URL = "https://api.groq.com/openai/v1/chat/completions"


def create_app():
    app = Flask(__name__)

    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///AI_log.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Blueprints
    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Create DB tables
    with app.app_context():
        from .models import Log
        db.create_all()

    return app
