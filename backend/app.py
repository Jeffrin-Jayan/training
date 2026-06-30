import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import db
from seed import seed_database

# Blueprints
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.schemes import schemes_bp
from routes.pdf_search import pdf_search_bp
from routes.ocr import ocr_bp
from routes.voice import voice_bp
from routes.complaints import complaints_bp
from routes.office_finder import office_finder_bp
from routes.dashboard import dashboard_bp
from routes.notifications import notifications_bp
from routes.admin import admin_bp
from routes.life_events import life_events_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for all routes (necessary for Streamlit client integration)
    CORS(app)
    
    # Initialize DB
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(schemes_bp, url_prefix='/api/schemes')
    app.register_blueprint(pdf_search_bp, url_prefix='/api/pdf')
    app.register_blueprint(ocr_bp, url_prefix='/api/ocr')
    app.register_blueprint(voice_bp, url_prefix='/api/voice')
    app.register_blueprint(complaints_bp, url_prefix='/api/complaints')
    app.register_blueprint(office_finder_bp, url_prefix='/api/offices')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(life_events_bp, url_prefix='/api/life_events')
    
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy", "service": "GovAssist Backend API"}), 200
        
    # Setup database tables and seed
    with app.app_context():
        db.create_all()
        seed_database(app)
        
    return app

if __name__ == '__main__':
    app = create_app()
    # Runs on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
