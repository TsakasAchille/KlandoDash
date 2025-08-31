from flask_login import LoginManager, current_user, login_required, logout_user
from flask import session
from dash_apps.auth.models import User
from dash_apps.auth.oauth import setup_oauth
from dash_apps.auth.simple_auth import init_auth

def setup_authentication(server):
    """
    Configure tout le système d'authentification pour l'application
    """
    # Initialisation de Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(server)
    login_manager.login_view = '/login'
    
    # Configurer le système OAuth personnalisé
    setup_oauth(server)
    
    # Initialiser l'authentification simple sur le serveur
    init_auth(server)
    
    # Définir le user loader pour Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        # Charger l'utilisateur à partir des données en session
        try:
            # Vérifier si l'utilisateur existe dans la session
            if 'user_email' in session and session.get('user_id') == user_id:
                return User(
                    id=user_id,
                    email=session.get('user_email'),
                    name=session.get('user_name'),
                    profile_pic=session.get('profile_pic'),
                    tags=session.get('tags', ''),
                    admin=session.get('is_admin', False)
                )
        except Exception as e:
            print(f"Erreur lors du chargement de l'utilisateur: {e}")
        return None
    
    return login_manager

def handle_logout():
    """
    Gère la déconnexion de l'utilisateur
    """
    logout_user()
    session.clear()
    return '/login'
