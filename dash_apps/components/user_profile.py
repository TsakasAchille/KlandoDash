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

def render_user_profile(uid):
    """
    Affiche le profil de l'utilisateur en utilisant un template Jinja2.
    
    Args:
        uid: Identifiant de l'utilisateur
    """
    if uid is None:
        return None
    
    # Importer UserRepository ici pour éviter les imports circulaires
    from dash_apps.repositories.user_repository import UserRepository
    
    # Récupérer l'utilisateur depuis le repository
    user = UserRepository.get_user_by_id(uid)
    if user is None:
        return dbc.Alert(f"Utilisateur introuvable (UID: {uid})", color="warning")
    
    # Convertir l'objet UserSchema en dictionnaire pour le template Jinja2
    if hasattr(user, "model_dump"):
        # Pour Pydantic v2
        user_dict = user.model_dump()
    elif hasattr(user, "dict"):
        # Pour Pydantic v1
        user_dict = user.dict()
    else:
        # Fallback pour les objets non-Pydantic
        user_dict = {k: getattr(user, k) for k in dir(user) if not k.startswith('_') and not callable(getattr(user, k))}
    
    # S'assurer que toutes les variables utilisées dans le template ont des valeurs par défaut
    # Préparer les valeurs par défaut
    defaults = {
        "rating": 0, 
        "rating_count": 0,
        "display_name": "",
        "name": "",
        "first_name": "",
        "email": "",
        "phone": "", 
        "phone_number": "",
        "birth": "",
        "bio": "",
        "gender": "",
        "role": "",
        "created_time": "", 
        "updated_at": ""
    }
    
    # Appliquer les valeurs par défaut
    for key, default_value in defaults.items():
        if key not in user_dict or user_dict[key] is None:
            user_dict[key] = default_value
    
    # Extraire les variables spécifiques pour le template
    rating = user_dict.get("rating", 0)
    rating_count = user_dict.get("rating_count", 0)
        
    # Rendu du template HTML avec Jinja2
    html_content = user_profile_template.render(
        user=user_dict,
        rating=rating,
        votes=rating_count
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
