from dash_apps.auth.models import User
from dash_apps.auth.oauth import setup_oauth
from dash_apps.config import Config
from flask_login import LoginManager

def init_auth(app):
    """
    Initialise l'authentification pour l'application Flask/Dash
    """
    # Initialiser LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = '/login'
    
    # Configurer la protection par session pour les routes d'API
    login_manager.session_protection = "strong"
    
    # Callback pour charger l'utilisateur depuis l'ID dans la session
    @login_manager.user_loader
    def load_user(user_id):
        try:
            # Charger l'utilisateur depuis la session
            if 'user_email' in flask_session and flask_session.get('user_id') == user_id:
                return User(
                    id=user_id,
                    email=flask_session.get('user_email'),
                    name=flask_session.get('user_name'),
                    profile_pic=flask_session.get('profile_pic')
                )
        except Exception as e:
            if _debug_mode:
                print(f"Erreur lors du chargement de l'utilisateur depuis la session: {e}")
        return None
    
    # Initialiser OAuth pour Google
    setup_oauth(app)

    return login_manager
