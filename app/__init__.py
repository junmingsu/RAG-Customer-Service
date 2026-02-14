from flask import Flask, session
from config import config
import secrets

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    from app.controllers.main_controller import main_bp
    from app.controllers.chat_controller import chat_bp
    from app.controllers.admin_controller import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    
    @app.before_request
    def before_request():
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(16)
    
    return app