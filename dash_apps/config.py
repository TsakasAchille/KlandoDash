import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement depuis .env
# Chercher le fichier .env à la racine du projet
env_path = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).joinpath('.env')
load_dotenv(dotenv_path=env_path)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO if os.environ.get('DASH_DEBUG', 'False').lower() == 'true' else logging.WARNING,
    format='%(asctime)s %(levelname)s %(message)s'
)

# Fonction helper pour OAuth redirect URI
def _get_oauth_redirect_uri():
    # Si OAUTH_REDIRECT_URI est défini explicitement, l'utiliser
    if os.environ.get('OAUTH_REDIRECT_URI'):
        return os.environ.get('OAUTH_REDIRECT_URI')
    
    # Sinon, détecter l'environnement
    if os.environ.get('RENDER'):  # Variable d'environnement Render
        return 'https://klandodash.onrender.com/auth/login/google/callback'
    else:
        return 'http://localhost:8050/auth/login/google/callback'

# Configuration de base
class Config(object):
    # Clé secrète pour les sessions
    SECRET_KEY = os.environ.get('SECRET_KEY', 'une-cle-secrete-par-defaut-a-changer')
    
    # Configuration OAuth Google
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # Configuration Admin (obligatoire via .env)
    try:
        ADMIN_USERNAME = os.environ['ADMIN_USERNAME']
    except KeyError:
        raise RuntimeError("Missing ADMIN_USERNAME in environment (.env)")
    try:
        ADMIN_PASSWORD = os.environ['APP_PASSWORD']
    except KeyError:
        raise RuntimeError("Missing APP_PASSWORD in environment (.env)")
    
    # URL de redirection pour OAuth - doit correspondre exactement à celle configurée dans la Google Cloud Console
    OAUTH_REDIRECT_URI = _get_oauth_redirect_uri()
    
    # Liste des emails autorisés - ceux configurés comme utilisateurs de test dans Google Cloud Console
    # Cette liste doit correspondre exactement aux utilisateurs de test configurés dans Google OAuth Console
    AUTHORIZED_EMAILS = os.environ.get('AUTHORIZED_EMAILS', '').split(',') if os.environ.get('AUTHORIZED_EMAILS') else []
    
    # Base de données - PostgreSQL (Supabase) ou SQLite (fallback)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration Supabase pour l'API REST
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')  # Pour les opérations admin
    
    # Mode de connexion à la base de données
    # 'auto': Utilise l'API REST si disponible, sinon PostgreSQL
    # 'postgres': Force l'utilisation de PostgreSQL directe
    # 'rest': Force l'utilisation de l'API REST Supabase
    CONNECTION_MODE = os.environ.get('CONNECTION_MODE', 'rest').lower()  # REST par défaut
    
    # Forcer l'utilisation de l'API REST (pour compatibilité)
    FORCE_REST_API = True  # Toujours utiliser REST
    
    # Configuration des tables et pagination
    USERS_TABLE_PAGE_SIZE = 5

    # MapLibre configuration
    # Prefer MAPLIBRE_STYLE_URL; fallback to MAP_API_URL for backward compatibility
    MAPLIBRE_STYLE_URL = os.environ.get('MAPLIBRE_STYLE_URL')
    
    
    # Mode d'affichage - embed pour iframe ou normal pour HTML complet
    USE_EMBED_MODE = os.environ.get('USE_EMBED_MODE', 'false').lower() == 'true'
    
    @classmethod
    def use_rest_api(cls):
        """Détermine si l'application doit utiliser l'API REST au lieu de la connexion directe"""
        return True
