import sys
import os
from dash import Dash
import dash_bootstrap_components as dbc
from flask_session import Session
from flask_login import LoginManager

from dash_apps.config import Config
from dash_apps.auth.routes import auth_bp

def create_app():
    """
    Crée et configure l'application Dash et le serveur Flask sous-jacent
    """
    # Configuration de base pour Dash
    app = Dash(
        __name__, 
        external_stylesheets=[
            dbc.themes.BOOTSTRAP, 
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
        ],
        suppress_callback_exceptions=True,
        url_base_pathname='/'
    )
    server = app.server

    # Configuration du serveur Flask sous-jacent
    server.config['SECRET_KEY'] = Config.SECRET_KEY
    server.config['SESSION_TYPE'] = 'filesystem'
    server.config['SESSION_PERMANENT'] = True

    # Initialiser Flask-Session
    Session(server)
    
    # Enregistrer le blueprint d'authentification
    server.register_blueprint(auth_bp, url_prefix='/auth')

    return app, server
