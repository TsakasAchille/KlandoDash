"""
Module d'authentification simple pour KlandoDash
"""
from dash_apps.config import Config
from dash_apps.auth.models import User
from flask import session, redirect, render_template, request, flash
from flask_login import login_user, logout_user, current_user

def init_auth(server):
    """Configure les routes d'authentification sur le serveur Flask"""
    
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
        from flask import render_template
        return render_template('login.html')
    
    @server.route('/admin-login', methods=['POST'])
    def admin_login():
        """Authentification admin"""
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Vérifier les identifiants admin
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            # Créer un utilisateur admin
            admin_user = User(
                id='admin',
                email='admin@klando-sn.com',  # Email fictif
                name='Administrateur',
                admin=True
            )
            
            # Connecter l'utilisateur admin
            login_user(admin_user, remember=True)
            
            # Stocker les informations dans la session
            session['logged_in'] = True
            session['user_id'] = 'admin'
            session['user_email'] = 'admin@klando-sn.com'
            session['user_name'] = 'Administrateur'
            session['is_admin'] = True
            session.modified = True
            
            return redirect('/')
        else:
            return redirect('/login')
    
    @server.route('/auth/login')
    def google_login():
        """Route pour l'authentification Google"""
        from dash_apps.auth.oauth import google_login as oauth_google_login
        return oauth_google_login()
    
    @server.route('/auth/login/google/callback')
    def google_callback():
        """Route de callback pour l'authentification Google"""
        from dash_apps.auth.oauth import google_callback as oauth_google_callback
        return oauth_google_callback()
    
    @server.route('/logout')
    def logout():
        """Route de déconnexion - gérée par le callback dans app.py"""
        # La déconnexion est maintenant gérée par un callback Dash dans app.py
        # Cette route existe uniquement pour compatibilité
        logout_user()
        session.clear()
        # Retourne un message simple, la redirection sera gérée par Dash
        return 'Déconnexion en cours...'
        
    @server.route('/auth/logout')
    def auth_logout():
        """Route alternative de déconnexion - gérée par le callback dans app.py"""
        # La déconnexion est maintenant gérée par un callback Dash dans app.py
        return logout()
    
    @server.before_request
    def protect_pages():
        """Protection de toutes les pages sauf celles d'authentification"""
        # Liste des chemins publics (non protégés)
        public_paths = ['/login', '/admin-login', '/auth/login', '/auth/login/google/callback', '/logout', '/auth/logout']
        
        # Vérifier si l'utilisateur est authentifié
        if not current_user.is_authenticated:
            if request.path not in public_paths and not request.path.startswith('/assets/') \
               and not request.path.startswith('/_dash'):
                return redirect('/login')


def is_valid_klando_user():
    """Vérifie si l'utilisateur est authentifié (plus de vérification de domaine)"""
    try:
        # Tout utilisateur authentifié par Google est valide
        # Plus de vérification de domaine, Google Cloud gère les autorisations
        return current_user.is_authenticated
    except Exception:
        # Fallback avec la session
        return session.get('logged_in', False)


def render_user_menu():
    """Affiche le menu utilisateur à partir des informations de Flask-Login"""
    import dash_bootstrap_components as dbc
    from dash import html
    
    # Vérifier si l'utilisateur est authentifié avec Flask-Login
    try:
        is_authenticated = current_user.is_authenticated
    except:
        is_authenticated = False
    
    if not is_authenticated:
        return dbc.NavItem(dbc.Button("Se connecter", color="primary", href="/login", className="ms-2"))

    # Récupérer les données utilisateur
    try:
        username = getattr(current_user, 'name', None)
        email = getattr(current_user, 'email', None)
        profile_pic_url = getattr(current_user, 'profile_pic', None)
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