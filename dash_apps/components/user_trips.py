from dash import html
import dash_bootstrap_components as dbc
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
from dash_apps.utils.data_schema import get_trips_for_user
import datetime

# Initialisation de Jinja2 pour le template des trajets utilisateur
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir))
user_trips_template = env.get_template("user_trips_template.jinja2")

# Fonction pour formater les dates
def format_date(value):
    if isinstance(value, (datetime.datetime, pd.Timestamp)):
        return value.strftime("%d/%m/%Y %H:%M")
    return str(value)

# Styles communs pour une cohérence visuelle
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '28px',
    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
    'padding': '0px',
    'overflow': 'hidden',
    'marginBottom': '16px'
}

def render_user_trips(uid):
    """
    Affiche les trajets effectués par l'utilisateur en utilisant un template Jinja2.
    
    Args:
        uid: Identifiant de l'utilisateur
    """
    if uid is None:
        return None
    
    # Importer UserRepository ici pour éviter les imports circulaires
    from dash_apps.repositories.user_repository import UserRepository
    
    # Vérifier que l'utilisateur existe
    user = UserRepository.get_user_by_id(uid)
    if user is None:
        return dbc.Alert(f"Utilisateur introuvable (UID: {uid})", color="warning")
        
    user_id = uid  # Utiliser directement l'UID fourni
    
    db_error = False
    trips_data = []
    
    try:
        # Récupérer les trajets via notre nouveau module data_schema
        driver_trips_df = get_trips_for_user(str(user_id), as_driver=True)
        passenger_trips_df = get_trips_for_user(str(user_id), as_passenger=True)
        
        # Préparation des données pour les trajets en tant que conducteur
        if not driver_trips_df.empty and 'trip_id' in driver_trips_df.columns:
            for _, trip in driver_trips_df.iterrows():
                trip_dict = trip.to_dict()
                
                # Formater les dates
                if 'departure_schedule' in trip_dict:
                    trip_dict['departure_schedule'] = format_date(trip_dict['departure_schedule'])
                if 'created_at' in trip_dict:
                    trip_dict['created_at'] = format_date(trip_dict['created_at'])  
                
                trip_dict['role'] = 'driver'  # Marquer comme conducteur
                trips_data.append(trip_dict)
        
        # Préparation des données pour les trajets en tant que passager
        if not passenger_trips_df.empty and 'trip_id' in passenger_trips_df.columns:
            for _, trip in passenger_trips_df.iterrows():
                if any(d.get('trip_id') == trip['trip_id'] for d in trips_data):
                    # Éviter les doublons (si l'utilisateur est à la fois conducteur et passager)
                    continue
                trip_dict = trip.to_dict()
                
                # Formater les dates
                if 'departure_schedule' in trip_dict:
                    trip_dict['departure_schedule'] = format_date(trip_dict['departure_schedule'])
                if 'created_at' in trip_dict:
                    trip_dict['created_at'] = format_date(trip_dict['created_at'])  
                    
                trip_dict['role'] = 'passenger'  # Marquer comme passager
                trips_data.append(trip_dict)
                
    except Exception as e:
        import traceback
        print(f"Erreur lors de la récupération des trajets utilisateur: {str(e)}")
        print(traceback.format_exc())
        db_error = True
    
    # Trier par date de départ (du plus récent au plus ancien)
    try:
        trips_data = sorted(trips_data, key=lambda x: x.get('departure_schedule', ''), reverse=True)
    except Exception:
        # En cas d'erreur de tri, continuer avec l'ordre actuel
        pass
    
    # Rendu du template HTML avec Jinja2
    html_content = user_trips_template.render(
        trips=trips_data,
        db_error=db_error
    )
    
    # Afficher le template dans un iframe
    return html.Div(
        html.Iframe(
            srcDoc=html_content,
            style={
                'width': '100%',
                'height': '500px',  # Hauteur adaptative pour la liste des trajets
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            sandbox='allow-scripts allow-top-navigation',
        ),
        style=CARD_STYLE
    )
