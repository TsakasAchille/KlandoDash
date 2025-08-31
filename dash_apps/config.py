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
    # Détection automatique de l'environnement (production vs développement)
    def _get_oauth_redirect_uri():
        # Si OAUTH_REDIRECT_URI est défini explicitement, l'utiliser
        if os.environ.get('OAUTH_REDIRECT_URI'):
            return os.environ.get('OAUTH_REDIRECT_URI')
        
        # Sinon, détecter l'environnement
        if os.environ.get('RENDER'):  # Variable d'environnement Render
            return 'https://klandodash.onrender.com/auth/login/google/callback'
        else:
            return 'http://localhost:8050/auth/login/google/callback'
    
    OAUTH_REDIRECT_URI = _get_oauth_redirect_uri()
    
    # Liste des emails autorisés - ceux configurés comme utilisateurs de test dans Google Cloud Console
    # Cette liste doit correspondre exactement aux utilisateurs de test configurés dans Google OAuth Console
    AUTHORIZED_EMAILS = os.environ.get('AUTHORIZED_EMAILS', '').split(',') if os.environ.get('AUTHORIZED_EMAILS') else []
    
    # Base de données SQLite pour les utilisateurs
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration des tables et pagination
    USERS_TABLE_PAGE_SIZE = 5

    # MapLibre configuration
    # Prefer MAPLIBRE_STYLE_URL; fallback to MAP_API_URL for backward compatibility
    MAPLIBRE_STYLE_URL = os.environ.get('MAPLIBRE_STYLE_URL') or os.environ.get('MAP_API_URL', '')
    MAPLIBRE_API_KEY = os.environ.get('MAPLIBRE_API_KEY', '')      # if required to be passed in base URLs
    
    # Mode d'affichage - embed pour iframe ou normal pour HTML complet
    USE_EMBED_MODE = os.environ.get('USE_EMBED_MODE', 'false').lower() == 'true'
