from dash import Input, Output, callback_context, no_update
from flask_login import current_user
from flask import session
from dash_apps.simple_auth import render_user_menu, is_valid_klando_user
from dash_apps.core.page_manager import get_page_layout
from dash_apps.core.auth_manager import handle_logout
from dash_apps.utils.admin_db import is_admin
import dash_bootstrap_components as dbc
from dash import html

# Importer le layout de la page de login
from dash_apps.auth.login_layout import login_layout

def register_callbacks(app):
    """
    Enregistre tous les callbacks de l'application
    """
    # Callback pour gérer la déconnexion
    @app.callback(
        Output('redirect-logout', 'pathname'),
        Input('url', 'pathname')
    )
    def logout_callback(pathname):
        """Gère la redirection après déconnexion"""
        if pathname == '/logout' or pathname == '/auth/logout':
            return handle_logout()
        # Dans les autres cas, ne pas faire de redirection
        return no_update

    # Callback pour afficher le menu utilisateur
    @app.callback(
        Output("user-info-sidebar", "children"),
        Input("url", "pathname")
    )
    def update_user_menu(pathname):
        """Mettre à jour le menu utilisateur selon l'état d'authentification"""
        if current_user.is_authenticated:
            return render_user_menu(current_user)
        else:
            return html.Div([
                dbc.Button("Se connecter", href="/login", color="primary", size="sm")
            ])
            
    # Callback pour afficher ou masquer le lien d'administration
    @app.callback(
        Output("admin-nav-container", "style"),
        Input("url", "pathname")
    )
    def toggle_admin_link(pathname):
        """Affiche ou masque le lien d'administration selon les droits de l'utilisateur"""
        # Vérifier si l'utilisateur est connecté et admin
        user_email = session.get('user_email', None)
        if user_email and is_admin(user_email):
            return {"display": "block"}  # Afficher le lien
        else:
            return {"display": "none"}  # Masquer le lien

    # Callback pour afficher la page demandée dans le contenu principal
    @app.callback(
        Output("main-content", "children"),
        [Input("url", "pathname")]
    )
    def display_page(pathname):
        """
        Affiche la page demandée ou redirige vers la page de login si non authentifié
        """
        # Si c'est la page de login, afficher directement
        if pathname == "/login":
            return login_layout
            
        # Pour les autres pages, vérifier l'authentification
        if not current_user.is_authenticated:
            # L'utilisateur n'est pas authentifié, rediriger vers la page de login
            return login_layout
        
        # Vérifier si l'utilisateur est un utilisateur Klando valide
        if not is_valid_klando_user(current_user):
            return html.Div([
                html.H3("Accès refusé", className="text-danger"),
                html.P("Seuls les utilisateurs avec une adresse email @klando-sn.com sont autorisés."),
                dbc.Button("Retour à la page de connexion", href="/logout", color="primary")
            ], className="p-5")
        
        # L'utilisateur est authentifié, afficher la page demandée
        if pathname in ["/", "/trips", "/users", "/stats", "/support", "/admin", "/user-profile", "/driver-validation"]:
            # Obtenir le layout de la page demandée
            page_layout = get_page_layout(pathname)
            if page_layout:
                return page_layout() if callable(page_layout) else page_layout
            else:
                # Page non trouvée dans les layouts chargés
                return html.Div([
                    html.H3("404 - Page non trouvée", className="text-danger"),
                    html.P(f"La page '{pathname}' n'existe pas."),
                    dbc.Button("Retour à l'accueil", href="/", color="primary")
                ], className="p-5")
        else:
            # Page non reconnue
            return html.Div([
                html.H3("404 - Page non trouvée", className="text-danger"),
                html.P(f"La page '{pathname}' n'existe pas."),
                dbc.Button("Retour à l'accueil", href="/", color="primary")
            ], className="p-5")
