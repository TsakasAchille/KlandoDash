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
        """Afficher la page de login"""
        if current_user.is_authenticated:
            return redirect('/')
        
        # Rendre directement le HTML sans complexité
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>KlandoDash - Connexion</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            <style>
                body {
                    background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
                    min-height: 100vh;
                    padding: 0 12px;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                }
                .login-container {
                    max-width: 450px;
                    margin: 0 auto;
                    padding-top: 80px;
                    text-align: center;
                }
                .brand {
                    color: #730200;
                    font-family: 'Arial', sans-serif;
                    margin-bottom: 30px;
                    font-size: 42px;
                    letter-spacing: 1px;
                    font-weight: bold;
                }
                .card {
                    border-radius: 8px;
                    border: none;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08);
                    background-color: white;
                }
                .btn-google {
                    border-radius: 4px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .version {
                    opacity: 0.6;
                }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1 class="brand">KLANDO</h1>
                <h2 class="mb-3" style="color: #505050; font-weight: 500;">Bienvenue sur KlandoDash</h2>
                <p class="text-muted mb-4">Connectez-vous pour accéder à l'application</p>
                
                <div class="card shadow mb-4">
                    <div class="card-body">
                        <h4 class="card-title mb-4" style="color: #464646; font-weight: 500;">Authentification</h4>
                        
                        <ul class="nav nav-tabs mb-4" id="loginTabs" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="google-tab" data-bs-toggle="tab" data-bs-target="#google" 
                                        type="button" role="tab" aria-selected="true">Google</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="admin-tab" data-bs-toggle="tab" data-bs-target="#admin" 
                                        type="button" role="tab" aria-selected="false">Admin</button>
                            </li>
                        </ul>
                        
                        <div class="tab-content" id="loginTabsContent">
                            <div class="tab-pane fade show active" id="google" role="tabpanel" aria-labelledby="google-tab">
                                <a href="/auth/login" style="text-decoration: none;">
                                    <button class="btn btn-danger btn-lg w-100 mb-3 btn-google">
                                        <i class="fab fa-google me-2"></i>
                                        Se connecter avec Google
                                    </button>
                                </a>
                                
                                <div class="text-center">
                                    <span class="badge bg-success rounded-pill mt-2">Tous les comptes Google sont autorisés</span>
                                </div>
                            </div>
                            
                            <div class="tab-pane fade" id="admin" role="tabpanel" aria-labelledby="admin-tab">
                                <form method="POST" action="/admin-login">
                                    <div class="mb-3">
                                        <label for="admin-username" class="form-label text-start d-block">Nom d'utilisateur</label>
                                        <input type="text" class="form-control" id="admin-username" name="username" required>
                                    </div>
                                    <div class="mb-3">
                                        <label for="admin-password" class="form-label text-start d-block">Mot de passe</label>
                                        <input type="password" class="form-control" id="admin-password" name="password" required>
                                    </div>
                                    <button type="submit" class="btn btn-primary btn-lg w-100">
                                        <i class="fas fa-lock me-2"></i>
                                        Connexion Admin
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
                
                <p class="mt-4 text-muted small version">KlandoDash v1.0</p>
            </div>
            
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """
    
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
    """Vérifie si l'utilisateur est authentifié"""
    try:
        # Vérification principale via Flask-Login
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
