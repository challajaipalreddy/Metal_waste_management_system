import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Database configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'metal_waste_db')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    
    # Secret key for session management
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Other configurations
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true' 