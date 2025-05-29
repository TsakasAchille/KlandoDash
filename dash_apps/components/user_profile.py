from dash import html
import dash_bootstrap_components as dbc
from jinja2 import Environment, FileSystemLoader
import os

# Initialisation de Jinja2 pour le template de profil utilisateur
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir))
user_profile_template = env.get_template("user_profile_template.jinja2")

# Styles communs pour une cohérence visuelle avec la page trajets
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '28px',
    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
    'padding': '0px',  # Padding géré par le template
    'overflow': 'hidden',
    'marginBottom': '16px'
}

def render_user_profile(user):
    """
    Affiche le profil de l'utilisateur en utilisant un template Jinja2.
    
    Args:
        user: Dictionnaire de données utilisateur
    """
    if user is None:
        return None
        
    # Rendu du template HTML avec Jinja2
    html_content = user_profile_template.render(
        user=user
    )
    
    # Afficher le template dans un iframe comme pour les autres composants
    return html.Div(
        html.Iframe(
            srcDoc=html_content,
            style={
                'width': '100%',
                'height': '800px',  # Hauteur augmentée pour éviter la coupure
                'overflowY': 'scroll',  # Scroll vertical autorisé
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            sandbox='allow-scripts allow-top-navigation',
        ),
        style=CARD_STYLE
    )
