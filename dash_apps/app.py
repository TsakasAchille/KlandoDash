import sys
import os

# Ajouter le répertoire racine du projet au PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dash import Dash, html, dcc, Input, Output, callback_context
import dash_bootstrap_components as dbc
from dash_apps.config import Config
from flask import session, redirect
from flask_login import LoginManager, current_user, login_required

# Importer notre module d'authentification personnalisé
from dash_apps.auth.oauth import setup_oauth, google_login, google_callback
from dash_apps.auth.models import User

# Configuration de base pour Dash
app = Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'],
    suppress_callback_exceptions=True,
    url_base_pathname='/'
)
server = app.server

# Configuration du serveur Flask sous-jacent
server.config['SECRET_KEY'] = Config.SECRET_KEY
server.config['SESSION_TYPE'] = 'filesystem'
server.config['SESSION_PERMANENT'] = True

# Initialisation de Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

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
                tags=session.get('tags', '')
            )
    except Exception as e:
        print(f"Erreur lors du chargement de l'utilisateur: {e}")
    return None

# Configurer notre système OAuth personnalisé
setup_oauth(server)

# Utiliser notre module d'authentification simple
from dash_apps.simple_auth import init_auth, is_valid_klando_user, render_user_menu
from dash_apps.components.logout_component import create_logout_button

# Initialiser l'authentification sur le serveur
init_auth(server)

# Layout principal de l'application
app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    
    # Barre latérale fixe
    dbc.Row([
        # Sidebar navigation
        dbc.Col([
            html.Div([
                html.H3("KlandoDash", className="mt-4 mb-4", style={"color": "#730200", "fontFamily": "Gliker, Arial, sans-serif"}),
                dbc.Nav([
                    dbc.NavLink("Utilisateurs", href="/users", active="exact", id="nav-users", className="mb-2"),
                    dbc.NavLink("Trajets", href="/trips", active="exact", id="nav-trips", className="mb-2"),
                    dbc.NavLink("Statistiques", href="/stats", active="exact", id="nav-stats", className="mb-2"),
                    dbc.NavLink("Support", href="/support", active="exact", id="nav-support", className="mb-2"),
                    # Temporairement désactivé car incompatible avec le nouveau système d'authentification
                    # dbc.NavLink("Membres", href="/members", active="exact", id="nav-members", className="mb-2"),
                ], vertical=True, pills=True, className="sidebar-nav"),
                
                html.Div([
                    html.Hr(),
                    html.Div(id="user-info-sidebar")
                ], className="mt-auto mb-3")
                
            ], style={
                "position": "fixed", 
                "top": 0, 
                "left": 0, 
                "height": "100vh", 
                "width": "220px", 
                "background": "#f8f9fa", 
                "padding": "24px 12px 0 12px", 
                "borderRight": "2px solid #eee", 
                "zIndex": 1000,
                "display": "flex",
                "flexDirection": "column",
                "justifyContent": "space-between"
            })
        ], width=2, style={"padding": 0, "maxWidth": "220px"}),
        
        # Contenu principal
        dbc.Col([
            html.Div(id="main-content", style={"marginLeft": "12px", "marginRight": "12px"})
        ], width=10)
    ], className="g-0")
], fluid=True, style={"height": "100vh"})

# Importations pour la gestion des pages
import os
import importlib.util
import sys

# Dictionnaire pour stocker les layouts de page
page_layouts = {}

# Fonction pour charger une page depuis un fichier Python
def load_page_from_file(file_name, page_name):
    """Charge une page à partir d'un fichier Python et retourne son layout"""
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'pages', file_name)
        if not os.path.exists(file_path):
            print(f"Fichier non trouvé: {file_path}")
            return None
            
        # Définir un nom de module unique
        module_name = f"page_{file_name.replace('.py', '')}_module"
        
        # Charger le module via spec_from_file_location
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        page_module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = page_module
        spec.loader.exec_module(page_module)
        
        # Vérifier si le layout existe
        if hasattr(page_module, 'layout'):
            print(f"Page chargée: {page_name} ({file_name})")
            return page_module.layout
        else:
            print(f"Pas de layout dans {file_name}")
            return None
    except Exception as e:
        print(f"Erreur de chargement de {file_name}: {str(e)}")
        return None

# Page d'exemple pour la page utilisateurs
page_layouts['/users'] = load_page_from_file('01_users.py', 'Utilisateurs')

# Page d'exemple pour la page stats
page_layouts['/stats'] = load_page_from_file('03_stats.py', 'Statistiques')

# Page d'exemple pour la page support
page_layouts['/support'] = load_page_from_file('04_support.py', 'Support')

# Page d'exemple pour la page membres - temporairement désactivée car incompatible avec le nouveau système d'authentification
# page_layouts['/members'] = load_page_from_file('05_members.py', 'Membres')

# Page principale: la page trajets (version sans conflit de callbacks)
page_layouts['/'] = load_page_from_file('trips_page.py', 'Accueil/Trajets')
page_layouts['/trips'] = page_layouts['/']

# Pages de déconnexion désactivées dans Dash, gérées par Flask
# Utiliser directement les boutons qui pointent vers /logout
# La redirection se fait via le template HTML

# Callback pour afficher le menu utilisateur
@app.callback(
    Output("user-info-sidebar", "children"),
    Input("url", "pathname")
)
def update_user_menu(pathname):
    """Mettre à jour le menu utilisateur selon l'état d'authentification"""
    # Vérifier si l'utilisateur est authentifié
    from flask_login import current_user
    
    if not current_user.is_authenticated:
        from dash import no_update
        return dbc.Button("Se connecter", color="primary", href="/auth/login", className="ms-2")
    
    # Vérifier le domaine de l'email
    if not is_valid_klando_user():
        # Déconnecter l'utilisateur si email non valide
        from dash_apps.components.logout_component import create_logout_button
        return html.Div([
            html.P("Accès réservé aux emails @klando-sn.com", className="text-danger"),
            create_logout_button("Se déconnecter", "danger", "mt-2", False)
        ])
    
    # Utilisateur valide, afficher le menu normal
    return render_user_menu()

# Callback pour afficher la page demandée dans le contenu principal
@app.callback(
    Output("main-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    """Affiche la page demandée dans le contenu principal"""
    # Vérifier l'authentification avec Flask-Login
    try:
        is_authenticated = current_user.is_authenticated
    except:
        # Fallback avec la session
        is_authenticated = session.get('logged_in', False)
    
    # URLs spéciales pour l'authentification qui ne nécessitent pas d'authentification
    auth_urls = ["/auth/login", "/auth/logout", "/auth/login/google/callback", "/login", "/logout"]
    if any(pathname.startswith(url) for url in auth_urls):
        # Retourner un contenu vide pour ces routes spéciales
        return html.Div()
    
    # Rediriger vers login si non authentifié
    if not is_authenticated:
        return dbc.Alert(
            [
                html.H4("Authentification requise", className="alert-heading"),
                html.P("Vous devez vous connecter pour accéder à cette application."),
                html.Hr(),
                dbc.Button("Se connecter", color="primary", href="/auth/login", className="mt-3")
            ],
            color="info",
            className="my-5",
            style={
                "maxWidth": "500px", 
                "margin": "80px auto", 
                "borderRadius": "8px", 
                "boxShadow": "0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08)",
                "backgroundColor": "white"
            }
        )
    
    # Vérifier le domaine email
    if not is_valid_klando_user():
        return dbc.Alert(
            [
                html.H4("Accès restreint", className="alert-heading"),
                html.P("Seuls les utilisateurs avec une adresse email @klando-sn.com sont autorisés à accéder à cette application."),
                html.Hr(),
                create_logout_button("Se déconnecter", "danger", "mt-3", False)
            ],
            color="danger",
            className="my-5",
            style={
                "maxWidth": "550px", 
                "margin": "80px auto", 
                "borderRadius": "8px", 
                "boxShadow": "0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08)",
                "backgroundColor": "white"
            }
        )
    
    # Normaliser le chemin pour éviter les problèmes de slash
    if pathname != '/' and pathname.endswith('/'):
        pathname = pathname[:-1]
    
    # Afficher le chemin demandé pour débogage
    print(f"URL demandée: {pathname}")
    
    # Chercher la page dans notre dictionnaire de layouts
    if pathname in page_layouts and page_layouts[pathname] is not None:
        layout = page_layouts[pathname]
        # Si c'est une fonction, l'exécuter
        if callable(layout):
            return layout()
        # Sinon, le retourner directement
        return layout
    
    # Si la page n'est pas trouvée, afficher une alerte dans le style Klando (fond blanc, ombres subtiles)
    return dbc.Alert(
        [
            html.H4("Page non trouvée", className="alert-heading", style={"color": "#505050"}),
            html.P(f"La page '{pathname}' n'existe pas ou n'est pas accessible."),
            html.Hr(),
            html.P("Veuillez sélectionner une page dans le menu de gauche.", className="mb-0"),
            dbc.Button(
                [html.I(className="fas fa-home me-2"), "Accueil"],
                href="/",
                color="primary",
                outline=True,
                className="mt-3"
            )
        ],
        color="light",
        className="my-4 p-4",
        style={
            "maxWidth": "600px", 
            "margin": "30px auto", 
            "borderRadius": "8px", 
            "boxShadow": "0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08)",
            "border": "none",
            "backgroundColor": "white"
        }
    )

if __name__ == "__main__":
    app.run(debug=True)
