from dash import html, dcc, Input, Output, callback
from flask_login import logout_user
from flask import session

def create_dash_logout_page():
    """
    Crée une page de déconnexion Dash qui fonctionne avec le système de routage de Dash.
    Utilise dcc.Location pour la redirection côté client qui est la méthode recommandée
    pour les applications Dash.
    """
    layout = html.Div([
        html.Div([
            html.H2("Déconnexion réussie", className="mb-3"),
            html.P("Vous avez été déconnecté de KlandoDash."),
            html.P("Vous allez être redirigé vers la page de connexion..."),
            html.Div(className="spinner-border text-primary mt-3", role="status", children=[
                html.Span("Chargement...", className="visually-hidden")
            ]),
            html.P(["Si vous n'êtes pas redirigé automatiquement, ", 
                   html.A("cliquez ici", href="/login")], className="mt-3")
        ], className="logout-box p-4 text-center bg-white rounded shadow", 
        style={"maxWidth": "450px", "margin": "auto"}),
        
        # Composant de redirection Dash
        dcc.Location(id="logout-redirect", refresh=True)
    ], className="d-flex align-items-center justify-content-center", 
       style={
           "minHeight": "100vh",
           "background": "linear-gradient(to bottom, #f8f9fa, #e9ecef)",
           "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
       })
    
    return layout

# Callback pour effectuer la déconnexion et rediriger
@callback(
    Output("logout-redirect", "pathname", allow_duplicate=True),
    Input("logout-redirect", "pathname"),
    prevent_initial_call=True
)
def perform_logout(pathname):
    """
    Déconnecte l'utilisateur et renvoie vers la page de login.
    Ce callback s'exécute automatiquement quand la page est chargée.
    """
    # Déconnecter l'utilisateur via Flask-Login
    logout_user()
    
    # Effacer la session
    session.clear()
    
    # Rediriger vers la page de login (avec Dash)
    return "/login"
