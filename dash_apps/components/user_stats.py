from dash import html
import dash_bootstrap_components as dbc
from jinja2 import Environment, FileSystemLoader
import os
from src.data_processing.processors.trip_processor import TripProcessor
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
        user: Dictionnaire de données utilisateur
    """
    if user is None:
        return None
        
    user_id = user.get('uid') or user.get('id')
    if not user_id:
        return dbc.Alert("Impossible de trouver l'identifiant de l'utilisateur", color="warning")
    
    db_error = False
    try:
        # Récupérer les stats via TripProcessor
        trip_processor = TripProcessor()
        all_trips_df = trip_processor.get_all_user_trips(str(user_id))
        passenger_trips_df = trip_processor.get_trips_for_passenger(str(user_id))
        
        # Calculer les statistiques
        total_trips_count = len(all_trips_df)
        driver_trips_count = len(all_trips_df[all_trips_df['role']=='driver']) if 'role' in all_trips_df.columns else 0
        passenger_trips_count = len(passenger_trips_df)
        total_distance = all_trips_df['trip_distance'].sum() if 'trip_distance' in all_trips_df.columns and not all_trips_df.empty else 0
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
