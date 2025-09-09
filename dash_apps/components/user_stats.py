from dash import html
from jinja2 import Template
from dash_apps.services.users_cache_service import UsersCacheService
import dash_bootstrap_components as dbc
from jinja2 import Environment, FileSystemLoader
import os
from dash_apps.utils.data_schema_rest import get_trips_for_user
import pandas as pd

# Initialisation de Jinja2 pour le template des statistiques utilisateur
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir))
user_stats_template = env.get_template("user_stats_template.jinja2")

# Styles communs pour une cohérence visuelle avec la page trajets
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '28px',
    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
    'padding': '0px',  # Padding géré par le template
    'overflow': 'hidden',
    'marginBottom': '16px'
}

def render_user_stats(user):
    """
    Affiche les statistiques de l'utilisateur en utilisant un template Jinja2.
    
    Args:
        user: Données de l'utilisateur (dict) - peut être les stats directement ou un objet utilisateur
    """
    if user is None:
        return None
    
    print(f"[STATS_DEBUG] render_user_stats appelé avec user type: {type(user)}")
    print(f"[STATS_DEBUG] Clés disponibles: {list(user.keys()) if isinstance(user, dict) else 'N/A'}")
        
    # Déterminer si on a les stats directement ou un objet utilisateur
    db_error = False
    
    # Cas 1: Les données sont les stats directement (nouveau système REST)
    if 'total_trips' in user and 'driver_trips_count' in user:
        print(f"[STATS_DEBUG] Stats directes détectées")
        stats = user
        user_id = "unknown"  # L'ID n'est pas nécessaire pour le rendu
    # Cas 2: Les stats sont dans un sous-objet 'stats' (ancien système)
    elif 'stats' in user:
        print(f"[STATS_DEBUG] Stats dans sous-objet détectées")
        stats = user['stats']
        user_id = user.get('uid', 'unknown')
        if UsersCacheService._debug_mode:
            print(f"[STATS] Stats récupérées du cache pour {user_id[:8] if len(user_id) > 8 else user_id}...")
    # Cas 3: Objet utilisateur sans stats - fallback (ne devrait plus arriver avec le nouveau système)
    else:
        user_id = user.get('uid', 'unknown')
        print(f"[STATS_DEBUG] Fallback: pas de stats trouvées pour {user_id}")
        # Ne plus essayer de charger depuis la DB, utiliser des valeurs par défaut
        db_error = True
        stats = {
            'total_trips': 0,
            'driver_trips_count': 0,
            'passenger_trips_count': 0,
            'total_distance': 0.0
        }
        print(f"[STATS_DEBUG] Utilisation des stats par défaut")
    
    # Extraire les statistiques
    total_trips_count = stats['total_trips']
    driver_trips_count = stats['driver_trips_count']
    passenger_trips_count = stats['passenger_trips_count']
    total_distance = stats['total_distance']
    
    # Préparer les données pour le template
    stats_data = {
        'total_trips': total_trips_count,
        'driver_trips': driver_trips_count,
        'passenger_trips': passenger_trips_count,
        'total_distance': total_distance,
        'db_error': db_error
    }
    
    print(f"[STATS_DEBUG] Stats finales pour template: {stats_data}")
    
    # Rendu du template HTML avec Jinja2
    html_content = user_stats_template.render(
        stats=stats_data
    )
    
    print(f"[STATS_DEBUG] Template rendu avec succès, taille: {len(html_content)} caractères")
    
    # Afficher le template dans un iframe comme pour les autres composants
    return html.Div(
        html.Iframe(
            srcDoc=html_content,
            style={
                'width': '100%',
                'height': '360px',  # Hauteur adaptative pour les statistiques
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            sandbox='allow-scripts allow-top-navigation',
        ),
        style=CARD_STYLE
    )
