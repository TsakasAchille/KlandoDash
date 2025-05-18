from authlib.integrations.flask_client import OAuth
from dash_apps.config import Config
from flask import redirect, url_for, session, flash, request
from flask_login import login_user, logout_user
from dash_apps.auth.models import User
import secrets
import os

# OAuth configuration
oauth = OAuth()

# Configuration OAuth pour Google - s'assurer qu'elle est correctement initialisée
oauth = OAuth()

def setup_oauth(app):
    """
    Configure l'authentification OAuth avec les clu00e9s d'API Google
    """
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=Config.GOOGLE_CLIENT_ID,
        client_secret=Config.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

def google_login():
    """
    Démarre le processus d'authentification Google
    """
    # Générer un state aléatoire pour la sécurité
    state = secrets.token_hex(16)
    session['_google_authlib_state_'] = state
    
    # Rediriger vers Google pour l'authentification
    redirect_uri = Config.OAUTH_REDIRECT_URI
    return oauth.google.authorize_redirect(redirect_uri)

def google_callback():
    """
    Fonction de callback après l'authentification Google
    """
    try:
        # Récupérer le token d'accès
        token = oauth.google.authorize_access_token()
        
        # Récupérer les informations de l'utilisateur
        resp = oauth.google.get('https://www.googleapis.com/oauth2/v3/userinfo')
        user_info = resp.json()
        email = user_info.get('email', '')
        name = user_info.get('name', '')
        picture = user_info.get('picture', '')
        user_id = user_info.get('sub', '')  # Google unique ID
        
        # Tous les emails sont autorisés maintenant
        # Pas de vérification de domaine
        
        # Sans base de données, on crée un User en mémoire
        user = User(
            id=user_id,
            email=email,
            name=name,
            profile_pic=picture,
            tags=''
        )
        
        # Connecter l'utilisateur avec remember=True pour maintenir la session plus longtemps
        login_user(user, remember=True)
        
        # Stockage dans la session
        session['logged_in'] = True
        session['user_id'] = user_id
        session['user_email'] = email
        session['user_name'] = name
        session['profile_pic'] = picture
        session.modified = True
        
        return redirect('/')
        
    except Exception as e:
        flash(f"Erreur d'authentification: {str(e)}", "danger")
        print(f"ERREUR OAUTH: {str(e)}")  # Log dans la console
        return redirect('/login')

def logout():
    """
    Déconnexion de l'utilisateur
    """
    logout_user()
    session.pop('logged_in', None)
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.modified = True
    
    return redirect('/login')
