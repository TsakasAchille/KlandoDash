from dash import html
import dash_bootstrap_components as dbc
from jinja2 import Environment, FileSystemLoader
import os
from dash_apps.utils.data_schema import get_trips_for_user
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
        user: Données de l'utilisateur (dict)
    """
    if user is None:
        return None
        
    # Extraire l'UID des données utilisateur
    user_id = user.get('uid')
    
    db_error = False
    try:
        # Récupérer les stats via notre nouveau module data_schema
        print(f"[STATS] Chargement trajets pour {user_id[:8]}... depuis DB")
        driver_trips_df = get_trips_for_user(user_id, as_driver=True, as_passenger=False)
        passenger_trips_df = get_trips_for_user(user_id, as_driver=False, as_passenger=True)
        print(f"[STATS] {len(driver_trips_df)} trajets conducteur, {len(passenger_trips_df)} trajets passager")
        
        # Calculer les statistiques
        total_trips_count = len(driver_trips_df) + len(passenger_trips_df)
        driver_trips_count = len(driver_trips_df)
        passenger_trips_count = len(passenger_trips_df)
        # Calcul de la distance totale - vérifie si la colonne 'distance' existe
        driver_distance = driver_trips_df['distance'].sum() if 'distance' in driver_trips_df.columns and not driver_trips_df.empty else 0
        passenger_distance = passenger_trips_df['distance'].sum() if 'distance' in passenger_trips_df.columns and not passenger_trips_df.empty else 0
        total_distance = driver_distance + passenger_distance
    except Exception as e:
        import traceback
        print(f"Erreur lors de la récupération des statistiques utilisateur: {str(e)}")
        print(traceback.format_exc())
        # Valeurs par défaut en cas d'erreur
        total_trips_count = 0
        driver_trips_count = 0
        passenger_trips_count = 0
        total_distance = 0
        db_error = True
    
    # Préparer les données pour le template
    stats_data = {
        'total_trips': total_trips_count,
        'driver_trips': driver_trips_count,
        'passenger_trips': passenger_trips_count,
        'total_distance': total_distance,
        'db_error': db_error
    }
    
    # Rendu du template HTML avec Jinja2
    html_content = user_stats_template.render(
        stats=stats_data
    )
    
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
