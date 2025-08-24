import os
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement depuis .env
# Chercher le fichier .env à la racine du projet
env_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).joinpath('.env')
load_dotenv(dotenv_path=env_path)

# Configuration de base
class Config(object):
    # Clé secrète pour les sessions
    SECRET_KEY = os.environ.get('SECRET_KEY', 'une-cle-secrete-par-defaut-a-changer')
    
    # Configuration OAuth Google
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Configuration Admin
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('APP_PASSWORD', 'KLANDO2K25')
    
    # URL de redirection pour OAuth - doit correspondre exactement à celle configurée dans la Google Cloud Console
    # Si vous utilisez un port différent ou un nom de domaine différent, modifiez cette valeur
    OAUTH_REDIRECT_URI = os.environ.get('OAUTH_REDIRECT_URI', 'http://localhost:8050/auth/login/google/callback')
    
    # Liste des emails autorisés - ceux configurés comme utilisateurs de test dans Google Cloud Console
    # Cette liste doit correspondre exactement aux utilisateurs de test configurés dans Google OAuth Console
    AUTHORIZED_EMAILS = os.environ.get('AUTHORIZED_EMAILS', '').split(',') if os.environ.get('AUTHORIZED_EMAILS') else []
    
    # Base de données SQLite pour les utilisateurs
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration des tables et pagination
    USERS_TABLE_PAGE_SIZE = 5
