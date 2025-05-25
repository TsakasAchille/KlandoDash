from dash import html, dcc
import dash_bootstrap_components as dbc
from jinja2 import Environment, FileSystemLoader
import os
import pandas as pd
import numpy as np
import json
import plotly.express as px

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
    """Génère le contenu de l'onglet Vue générale avec les statistiques globales"""
    if not trips_data:
        return dbc.Alert("Aucune donnée à afficher.", color="warning")
        
    import pandas as pd
    import numpy as np
    import json
    from jinja2 import Environment, FileSystemLoader
    from pathlib import Path
    from flask import render_template_string
    
    # Création d'un DataFrame pour le traitement
    df = pd.DataFrame(trips_data)
    
    # Calcul des métriques
    total_trips = len(df)
    
    # Distance totale et moyenne (si la colonne existe)
    if "distance" in df.columns:
        # Filtrer les valeurs NaN/None
        df_clean = df.dropna(subset=["distance"])
        
        if len(df_clean) > 0:
            total_distance = round(df_clean["distance"].sum(), 1)
            avg_distance = round(df_clean["distance"].mean(), 1)
            distance_data = df_clean["distance"].tolist()
            
            # Vérifier qu'il reste des données valides
            if distance_data and all(isinstance(d, (int, float)) for d in distance_data) and len(set(distance_data)) > 1:
                distance_bins = np.histogram_bin_edges(distance_data, bins=10).tolist()
            else:
                # Fallback si données insuffisantes
                distance_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
                distance_data = distance_data or []
        else:
            # Aucune donnée valide
            total_distance = 0
            avg_distance = 0
            distance_data = []
            distance_bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    else:
        total_distance = "N/A"
        avg_distance = "N/A"
        distance_data = []
        distance_bins = []
    
    # Total passagers (si la colonne existe)
    if "seats_booked" in df.columns:
        # Filtrer les valeurs NaN/None
        df_clean = df.dropna(subset=["seats_booked"])
        
        if len(df_clean) > 0:
            total_passengers = int(df_clean["seats_booked"].sum())
            
            # Générer le comptage des passagers de manière sécurisée
            try:
                passenger_counts = df_clean["seats_booked"].value_counts().reset_index()
                passenger_counts.columns = ["passengers", "count"]
                passenger_counts = passenger_counts.sort_values("passengers").to_dict('records')
            except Exception as e:
                print(f"Erreur lors du comptage des passagers: {e}")
                passenger_counts = []
        else:
            total_passengers = 0
            passenger_counts = []
    else:
        total_passengers = "N/A"
        passenger_counts = []
    
    # Préparation des données pour le template
    context = {
        "total_trips": total_trips,
        "total_distance": total_distance,
        "avg_distance": avg_distance,
        "total_passengers": total_passengers,
        "distance_data": json.dumps(distance_data),
        "distance_bins": json.dumps(distance_bins),
        "passenger_counts": passenger_counts
    }
    
    # Chargement et rendu du template
    templates_folder = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(templates_folder))
    template = env.get_template("stats_general_template.jinja2")
    rendered_html = template.render(**context)
    
    # Affichage dans un iframe
    return html.Iframe(
        srcDoc=rendered_html,
        style={"width": "100%", "height": "800px", "border": "none", "overflow": "hidden"}
    )

   