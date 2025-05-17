from dash import html
import dash_bootstrap_components as dbc
from jinja2 import Environment, FileSystemLoader
import os
import pandas as pd
import numpy as np
import json

# Initialisation de Jinja2 pour le template
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir))
stats_general_template = env.get_template("stats_general_template.jinja2")

# Styles communs
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '28px',
    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
    'padding': '0px',
    'overflow': 'hidden',
    'marginBottom': '16px'
}

def render_stats_general(trips_data):
    """
    Affiche les statistiques générales des trajets en utilisant un template Jinja2.
    
    Args:
        trips_data: Données des trajets (liste de dictionnaires ou DataFrame)
    
    Returns:
        dash.html.Div: Composant Dash contenant les statistiques générales
    """
    if not trips_data:
        # Rendu du template HTML avec Jinja2 sans données de trajet
        html_content = stats_general_template.render(
            total_trips="N/A",
            total_distance="N/A",
            avg_distance="N/A",
            total_passengers="N/A",
            distance_data=[],
            distance_bins=[],
            passenger_counts=[]
        )
        
        # Afficher le template dans un iframe
        return html.Div(
            html.Iframe(
                srcDoc=html_content,
                style={
                    'width': '100%',
                    'height': '600px',
                    'border': 'none',
                    'overflow': 'hidden',
                    'backgroundColor': 'transparent',
                    'borderRadius': '18px'
                },
                id='stats-general-iframe',
                sandbox='allow-scripts',
            ),
            style=CARD_STYLE
        )
    
    # Convertir en DataFrame si nécessaire
    if isinstance(trips_data, list):
        trips_df = pd.DataFrame(trips_data)
    else:
        trips_df = trips_data
    
    # Calculer les métriques
    total_trips = len(trips_df)
    
    # Traiter les distances
    if 'trip_distance' in trips_df.columns:
        total_distance = round(trips_df['trip_distance'].sum(), 1)
        avg_distance = round(trips_df['trip_distance'].mean(), 1)
        distance_data = trips_df['trip_distance'].tolist()
        
        # Créer des bins pour l'histogramme
        max_distance = trips_df['trip_distance'].max()
        bin_size = max_distance / 20 if max_distance > 0 else 1
        distance_bins = list(np.arange(0, max_distance + bin_size, bin_size))
    else:
        total_distance = "N/A"
        avg_distance = "N/A"
        distance_data = []
        distance_bins = []
    
    # Traiter les passagers
    if 'passenger_count' in trips_df.columns:
        total_passengers = int(trips_df['passenger_count'].sum())
        
        # Préparer les données pour le graphique des passagers
        passenger_counts_series = trips_df['passenger_count'].value_counts().sort_index()
        passenger_counts = [
            {"passengers": str(passengers), "count": count} 
            for passengers, count in passenger_counts_series.items()
        ]
    else:
        total_passengers = "N/A"
        passenger_counts = []
    
    # Rendu du template HTML avec Jinja2
    html_content = stats_general_template.render(
        total_trips=total_trips,
        total_distance=total_distance,
        avg_distance=avg_distance,
        total_passengers=total_passengers,
        distance_data=json.dumps(distance_data),
        distance_bins=json.dumps(distance_bins),
        passenger_counts=passenger_counts
    )
    
    # Afficher le template dans un iframe
    return html.Div(
        html.Iframe(
            srcDoc=html_content,
            style={
                'width': '100%',
                'height': '600px',
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            id='stats-general-iframe',
            sandbox='allow-scripts',
        ),
        style=CARD_STYLE
    )
