"""
Module d'authentification simple pour KlandoDash
"""
from flask import render_template_string, request, redirect, session, url_for, flash
from dash_apps.auth.admin_auth import handle_admin_login_request
from dash_apps.auth.oauth import google_callback
from dash_apps.auth.models import User
from dash_apps.config import Config
from flask import render_template, redirect, request, flash
from flask_login import login_user, logout_user, current_user
import os

# Mode debug pour les logs (désactivé en production)
_debug_mode = os.getenv('DASH_DEBUG', 'False').lower() == 'true'

def init_auth(server):
    """Configure les routes d'authentification sur le serveur Flask"""
    if _debug_mode:
        print("=== INIT_AUTH APPELÉ ===")
        print(f"Server: {server}")
    
    @server.route('/login')
    def login_page():
        """Afficher la page de login en utilisant le template login.html"""
        # Si l'utilisateur est déjà connecté, rediriger vers la page d'accueil
        if current_user.is_authenticated:
            return redirect('/')
        
        # Vérifier s'il y a un message d'erreur dans la session
        auth_error = session.get('auth_error')
        if auth_error:
            flash(auth_error, 'danger')
            session.pop('auth_error', None)  # Effacer le message après l'avoir utilisé
            session.modified = True
        
        # Utiliser le template login.html qui inclut déjà la gestion des messages flash
        return render_template('login.html')
    
    # Routes OAuth et admin supprimées - toutes gérées par le Blueprint dans routes.py
    
    @server.route('/logout')
    def logout():
        """Route de déconnexion locale uniquement"""
        logout_user()
        session.clear()
        return 'Déconnexion en cours...'
    
    @server.before_request
    def protect_pages():
        """Protection de toutes les pages sauf celles d'authentification"""
        # Liste des chemins publics (non protégés)
        public_paths = [
            '/login',
            '/admin-login',
            '/auth/admin-login',
            '/auth/login',
            '/auth/login/google/callback',
            '/logout',
            '/auth/logout',
            '/proxy/map',  # Proxy MapLibre doit être accessible sans auth
        ]
        
       
        
        # Vérifier si l'utilisateur est authentifié
        if not current_user.is_authenticated:
            # Autoriser toutes les routes d'authentification
            if request.path.startswith('/auth/'):
                return None
            if (
                request.path not in public_paths
                and not request.path.startswith('/assets/')
                and not request.path.startswith('/_dash')
                and not request.path.startswith('/proxy/')  # Exempter tous les endpoints de proxy
            ):
              
                return redirect('/login')



def render_user_menu(user=None):
    """Affiche le menu utilisateur à partir des informations de Flask-Login"""
    import dash_bootstrap_components as dbc
    from dash import html
    
    # Utiliser l'utilisateur passé en paramètre ou current_user si non spécifié
    user_to_display = user if user is not None else current_user
    
    # Vérifier si l'utilisateur est authentifié avec Flask-Login
    try:
        is_authenticated = user_to_display.is_authenticated
    except:
        is_authenticated = False
    
    if not is_authenticated:
        return dbc.NavItem(dbc.Button("Se connecter", color="primary", href="/login", className="ms-2"))

    # Récupérer les données utilisateur
    try:
        username = getattr(user_to_display, 'name', None)
        email = getattr(user_to_display, 'email', None)
        profile_pic_url = getattr(user_to_display, 'profile_pic', None)
    except:
        # Fallback: utiliser les données de session
        username = session.get('user_name')
        email = session.get('user_email')
        profile_pic_url = session.get('profile_pic')
    
    # Créer l'image de profil si disponible
    profile_pic = None
    if profile_pic_url:
        profile_pic = html.Img(
            src=profile_pic_url,
            style={
                "width": "32px", 
                "height": "32px", 
                "borderRadius": "50%", 
                "marginRight": "10px",
                "border": "1px solid #ddd"
            }
        )
    
    # Nom d'affichage
    display_name = username or email or "Utilisateur authentifié"
    
    # Menu utilisateur avec options
    return dbc.NavItem([
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem(f"Connecté en tant que {display_name}", header=True),
                dbc.DropdownMenuItem(f"Email: {email}", header=True, style={"fontStyle": "italic", "fontSize": "0.8rem"}),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem([html.I(className="fas fa-user me-2"), "Profil"], href="#"),
                dbc.DropdownMenuItem([html.I(className="fas fa-shield-alt me-2"), "Administrateur"], href="/admin"),
                dbc.DropdownMenuItem([html.I(className="fas fa-sign-out-alt me-2"), "Se déconnecter"], href="/logout"),
            ],
            nav=True,
            in_navbar=True,
            label=html.Div([
                profile_pic,
                html.Span(display_name, style={"maxWidth": "120px", "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"})
            ], style={"display": "flex", "alignItems": "center"}),
        )
    ])