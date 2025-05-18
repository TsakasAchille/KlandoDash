"""
Utilitaires de gestion des utilisateurs pour KlandoDash
"""
from flask import session
from flask_login import current_user

def is_valid_klando_user():
    """
    Vérifie si l'utilisateur est authentifié (plus de vérification de domaine)
    """
    try:
        # Vérification principale via Flask-Login
        if not current_user.is_authenticated:
            return False
        
        # Accepter tout utilisateur authentifié
        return True
    except Exception:
        # Fallback avec la session
        return session.get('logged_in', False)

def render_user_menu():
    """
    Affiche le menu utilisateur à partir des informations de Flask-Login
    """
    from dash import html
    import dash_bootstrap_components as dbc
    
    # Vérifier si l'utilisateur est authentifié avec Flask-Login
    try:
        is_authenticated = current_user.is_authenticated
    except:
        is_authenticated = False
    
    if not is_authenticated:
        return dbc.NavItem(dbc.Button("Se connecter", color="primary", href="/auth/login", className="ms-2"))

    # Récupérer les données utilisateur
    try:
        username = getattr(current_user, 'name', None)
        email = getattr(current_user, 'email', None)
        profile_pic_url = getattr(current_user, 'profile_pic', None)
    except:
        # Fallback: utiliser les données de session si Flask-Login échoue
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
                dbc.DropdownMenuItem([html.I(className="fas fa-sign-out-alt me-2"), "Se déconnecter"], href="/auth/logout"),
            ],
            nav=True,
            in_navbar=True,
            label=html.Div([
                profile_pic,
                html.Span(display_name, style={"maxWidth": "120px", "overflow": "hidden", "textOverflow": "ellipsis", "whiteSpace": "nowrap"})
            ], style={"display": "flex", "alignItems": "center"}),
        )
    ])
