from dash import html, dcc, callback, Output, Input
from flask import session
from flask_login import logout_user

def create_logout_button(text="Se déconnecter", color="danger", className="mt-2", icon=True):
    """
    Crée un bouton de déconnexion avec gestion de redirection via Dash callbacks
    plutôt que par les routes Flask standards qui sont interceptées par Dash.
    """
    button_content = []
    
    if icon:
        button_content.append(html.I(className="fas fa-sign-out-alt me-2"))
    
    button_content.append(text)
    
    return html.Div([
        html.Button(
            button_content,
            id="logout-button",
            className=f"btn btn-{color} {className}",
            n_clicks=0
        ),
        dcc.Location(id="logout-redirect", refresh=True)
    ])

# Callback pour gérer la déconnexion et la redirection
@callback(
    Output("logout-redirect", "pathname"),
    Input("logout-button", "n_clicks"),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    """
    Déconnecte l'utilisateur et renvoie vers la page de login
    quand le bouton de déconnexion est cliqué.
    """
    if n_clicks > 0:
        # Déconnecter l'utilisateur via Flask-Login
        logout_user()
        
        # Effacer la session
        session.clear()
        
        # Rediriger vers la page de login (avec Dash)
        return "/login"
    
    return ""
