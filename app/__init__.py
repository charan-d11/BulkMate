from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from app.config.config import Config
from app.common.logger import logger
from app.common.custom_exception import CustomException

logger.info("Initializing Flask application and extensions...") 
db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    try:
        app = Flask(__name__)
        app.config.from_object(Config)

        # Initialize extensions
        db.init_app(app)
        bcrypt.init_app(app)
        
        # Register blueprints
        from app.routes import auth, chat, meals, dashboard
        app.register_blueprint(auth.bp)
        app.register_blueprint(chat.bp)
        app.register_blueprint(meals.bp)
        app.register_blueprint(dashboard.bp)

        # ✅ Root route — redirects to login
        from flask import redirect, url_for

        @app.route('/')
        def index():
            return redirect(url_for('auth.login'))
        logger.info("Flask application initialized successfully.")
        return app
    except Exception as e:
        logger.error(f"Error initializing Flask application: {e}")
        raise CustomException("An error occurred while initializing the Flask application.", e)