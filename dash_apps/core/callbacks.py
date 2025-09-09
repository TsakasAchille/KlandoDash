from dash import Input, Output, State, callback_context, no_update
import logging
from flask_login import current_user
from flask import session
from dash_apps.auth.simple_auth import render_user_menu
from dash_apps.core.page_manager import get_page_layout
from dash_apps.core.auth_manager import handle_logout
from dash_apps.utils.admin_db_rest import is_admin
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
            try:
                logging.getLogger(__name__).info("[LOGOUT] Triggered from %s", pathname)
            except Exception:
                pass
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
        is_user_admin = session.get('is_admin', False)
        if user_email and is_user_admin:
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
            logging.getLogger(__name__).info("[PAGE] Show login page for pathname=%s", pathname)
            return login_layout
            
        # Pour les autres pages, vérifier l'authentification
        if not current_user.is_authenticated:
            # L'utilisateur n'est pas authentifié, rediriger vers la page de login
            logging.getLogger(__name__).info("[AUTH] Not authenticated, redirecting to login for pathname=%s", pathname)
            return login_layout
        
        # L'authentification Google OAuth suffit - pas besoin de double vérification
    
        # L'utilisateur est authentifié et autorisé, afficher la page demandée
        if pathname in ["/", "/trips", "/users", "/stats", "/support", "/admin", "/user-profile", "/driver-validation", "/map", "/simple-map", "/test-map", "/maplibre-simple"]:
            # Obtenir le layout de la page demandée
            page_layout = get_page_layout(pathname)
            if page_layout:
                logging.getLogger(__name__).info("[PAGE] Rendering page %s (layout found)", pathname)
                return page_layout() if callable(page_layout) else page_layout
            else:
                # Page non trouvée dans les layouts chargés
                logging.getLogger(__name__).warning("[PAGE][404] Layout not found for pathname=%s", pathname)
                return html.Div([
                    html.H3("404 - Page non trouvée", className="text-danger"),
                    html.P(f"La page '{pathname}' n'existe pas."),
                    dbc.Button("Retour à l'accueil", href="/", color="primary")
                ], className="p-5")
        else:
            # Page non reconnue
            logging.getLogger(__name__).warning("[PAGE][404] Unknown pathname requested: %s", pathname)
            return html.Div([
                html.H3("404 - Page non trouvée", className="text-danger"),
                html.P(f"La page '{pathname}' n'existe pas."),
                dbc.Button("Retour à l'accueil", href="/", color="primary")
            ], className="p-5")

    # --- Floating bubble chatbot window control ---
    @app.callback(
        Output("chatbot-window", "className"),
        Output("chatbot-window", "style"),
        Input("open-chatbot-bubble", "n_clicks"),
        Input("minimize-chatbot-window", "n_clicks"),
        State("chatbot-window", "className"),
        State("chatbot-window", "style"),
        prevent_initial_call=True,
    )
    def control_chatbot_window(n_open, n_min, class_name, style):
        ctx = callback_context
        if style is None:
            style = {}
        if not class_name:
            class_name = "chatbot-window"
        if not ctx.triggered:
            return class_name, style
        trig = ctx.triggered_id

        # Ensure base class
        base = "chatbot-window"
        classes = set(class_name.split()) if class_name else {base}
        classes.add(base)

        if trig == "open-chatbot-bubble":
            classes.add("show")
            style.update({"display": "block"})
            return " ".join(sorted(classes)), style
        elif trig == "minimize-chatbot-window":
            # Minimize should hide the window and return to bubble
            classes.discard("show")
            style.update({"display": "none"})
            return " ".join(sorted(classes)), style
        return class_name, style

    # --- Auto open chatbot once per session ---
    @app.callback(
        Output("chatbot-window", "className", allow_duplicate=True),
        Output("chatbot-window", "style", allow_duplicate=True),
        Output("chatbot-welcome-store", "data"),
        Input("chatbot-autoopen-init", "n_intervals"),
        State("chatbot-welcome-store", "data"),
        State("chatbot-window", "className"),
        State("chatbot-window", "style"),
        prevent_initial_call=True,
    )
    def auto_open_chatbot(_tick, stored, class_name, style):
        # Open only once per session
        if stored:
            return no_update, no_update, stored
        if style is None:
            style = {}
        base = "chatbot-window"
        classes = set((class_name or base).split())
        classes.add(base)
        classes.add("show")
        classes.discard("minimized")
        style.update({"display": "block"})
        return " ".join(sorted(classes)), style, {"auto_opened": True}
