import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'govassist_super_secret_key_129847')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    PARENT_DIR = os.path.dirname(BASE_DIR)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(PARENT_DIR, 'data', 'govassist.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Uploads
    UPLOAD_FOLDER = os.path.join(PARENT_DIR, 'data', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Vector store path
    VECTORSTORE_PATH = os.path.join(PARENT_DIR, 'vectorstore', 'faiss_index')
    
    # Ensure folders exist
    os.makedirs(os.path.dirname(os.path.join(PARENT_DIR, 'data', 'govassist.db')), exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(PARENT_DIR, 'vectorstore'), exist_ok=True)
