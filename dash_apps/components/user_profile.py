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
        user: Données de l'utilisateur (dict)
    """
    print(f"[DEBUG] render_user_profile appelé avec user type: {type(user)}")
    
    if user is None:
        print(f"[ERROR] Utilisateur non trouvé (None)")
        return dbc.Alert("Utilisateur non trouvé.", color="danger")
    
    # Convertir l'objet UserSchema en dictionnaire pour le template Jinja2
    try:
        if hasattr(user, "model_dump"):
            # Pour Pydantic v2
            print(f"[DEBUG] Conversion Pydantic v2 (model_dump)")
            user_dict = user.model_dump()
        elif hasattr(user, "dict"):
            # Pour Pydantic v1
            print(f"[DEBUG] Conversion Pydantic v1 (dict)")
            user_dict = user.dict()
        elif isinstance(user, dict):
            # Si c'est déjà un dict (préchargé), l'utiliser tel quel
            print(f"[DEBUG] Utilisation du dictionnaire existant")
            user_dict = user
        else:
            # Fallback pour les objets non-Pydantic
            print(f"[DEBUG] Conversion objet custom en dict")
            user_dict = {k: getattr(user, k) for k in dir(user) if not k.startswith('_') and not callable(getattr(user, k))}
        
        print(f"[DEBUG] user_dict généré avec {len(user_dict)} clés")
    except Exception as e:
        print(f"[ERROR] Erreur conversion utilisateur: {e}")
        user_dict = {}
    
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
    
    # Vérifier spécifiquement la photo de profil
    if 'photo_url' in user_dict:
        print(f"[DEBUG] Photo URL trouvée dans les données: {user_dict['photo_url']}")
    else:
        print(f"[DEBUG] Aucune photo_url trouvée dans les données utilisateur")
        # Chercher des champs alternatifs
        for field in ['avatar', 'profile_picture', 'picture', 'image', 'avatar_url']:
            if field in user_dict and user_dict[field]:
                print(f"[DEBUG] Champ alternatif trouvé pour la photo: {field}")
                user_dict['photo_url'] = user_dict[field]
                break
    
    # Extraire les variables spécifiques pour le template
    rating = user_dict.get("rating", 0)
    rating_count = user_dict.get("rating_count", 0)
        
    # Rendu du template HTML avec Jinja2
    try:
        # Extraction des valeurs pour le template
        rating = user_dict.get("rating", 0)
        rating_count = user_dict.get("rating_count", 0)
        
        print(f"[DEBUG] Tentative de rendu du template avec {len(user_dict)} clés, rating={rating}, votes={rating_count}")
        
        # Si user_dict est vide ou contient trop peu d'informations, ajouter un message
        if not user_dict or len(user_dict) < 2:
            print(f"[WARNING] user_dict vide ou incomplet: {user_dict}")
            return dbc.Alert("Données utilisateur insuffisantes ou corrompues.", color="warning")
        
        html_content = user_profile_template.render(
            user=user_dict,
            rating=rating,
            votes=rating_count
        )
        print(f"[DEBUG] Template rendu avec succès, taille HTML: {len(html_content)} caractères")
        
        # Afficher le template dans un iframe comme pour les autres composants
        iframe = html.Iframe(
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
        )
        
        result = html.Div(iframe, style=CARD_STYLE)
        print(f"[DEBUG] Panneau utilisateur généré avec succès")
        return result
        
    except Exception as e:
        print(f"[ERROR] Erreur lors du rendu du template: {e}")
        return dbc.Alert(f"Erreur lors de l'affichage du profil utilisateur: {e}", color="danger")


def render_user_summary(uid):
    """
    Résumé compact du conducteur: nom, note, uid, téléphone, email, genre, validation.
    """
    if uid is None:
        return None

    # Import local pour éviter les imports circulaires
    from dash_apps.repositories.user_repository import UserRepository

    user = UserRepository.get_user_by_id(uid)
    if user is None:
        return dbc.Alert(f"Utilisateur introuvable (UID: {uid})", color="warning")

    # Normaliser en dict
    if hasattr(user, "model_dump"):
        data = user.model_dump()
    elif hasattr(user, "dict"):
        data = user.dict()
    else:
        data = {k: getattr(user, k) for k in dir(user) if not k.startswith('_') and not callable(getattr(user, k))}

    # Champs utilisés
    uid_val = data.get("uid") or "-"
    display_name = data.get("display_name") or data.get("first_name") or data.get("name") or "-"
    email = data.get("email") or "-"
    phone = data.get("phone_number") or data.get("phone") or "-"
    gender = data.get("gender") or "-"
    rating = data.get("rating") if data.get("rating") is not None else 0
    rating_count = data.get("rating_count") if data.get("rating_count") is not None else 0
    validated = data.get("is_driver_doc_validated")
    photo_url = data.get("photo_url") or ""
    validated_badge = (
        dbc.Badge("Validé", color="success", className="ms-1") if validated else dbc.Badge("Non validé", color="secondary", className="ms-1")
    )

    return dbc.Card([
        dbc.CardBody([
            # Header: photo + button under it (left) and name/badge/rating (right)
            html.Div([
                html.Div([
                    html.Img(
                        src=photo_url,
                        style={
                            "width": "64px", "height": "64px", "borderRadius": "50%",
                            "objectFit": "cover", "backgroundColor": "#f2f2f2"
                        }
                    ) if photo_url else html.Div(style={
                        "width": "64px", "height": "64px", "borderRadius": "50%",
                        "backgroundColor": "#e9ecef"
                    }),
                    dbc.Button(
                        "Voir profil",
                        color="primary",
                        size="sm",
                        href=f"/users?uid={uid_val}",
                        external_link=False,
                        className="mt-2 w-100"
                    )
                ], className="d-flex flex-column align-items-center", style={"flex": "0 0 80px", "minWidth": "80px"}),
                html.Div([
                    html.Div([html.Strong(display_name), validated_badge], className="d-flex align-items-center gap-2"),
                    html.Div([
                        html.Span("Note: "), html.Strong(f"{rating:.1f}"), html.Span(f"  ({rating_count} avis)")
                    ], className="text-muted")
                ], style={"flex": "1 1 auto"})
            ], className="d-flex align-items-start gap-3 mb-3"),

            # Details list
            html.Div([
                html.Div([html.Strong("UID: "), html.Span(uid_val)]),
                html.Div([html.Strong("Email: "), html.Span(email)]),
                html.Div([html.Strong("Téléphone: "), html.Span(phone)]),
                html.Div([html.Strong("Genre: "), html.Span(gender)]),
            ], className="small"),
        ])
    ], style={**CARD_STYLE, "padding": "12px"})
