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

def render_user_trips(user):
    """
    Affiche les trajets effectués par l'utilisateur en utilisant un template Jinja2.
    
    Args:
        user: Données de l'utilisateur (dict)
    """
    if user is None:
        return None
    
    # Extraire l'UID des données utilisateur
    uid = user.get('uid')
    user_id = uid
    
    db_error = False
    trips_data = []
    
    try:
        # Utiliser la nouvelle fonction optimisée pour récupérer tous les trajets en une seule requête
        print(f"[TRIPS] Chargement trajets optimisés pour {user_id[:8]}... depuis DB")
        from dash_apps.utils.data_schema import get_user_trips_with_role
        
        trips_df = get_user_trips_with_role(str(user_id), limit=50)  # Limiter à 50 trajets récents
        print(f"[TRIPS] {len(trips_df)} trajets récupérés (optimisé)")
        
        # Préparation des données pour l'affichage
        if not trips_df.empty and 'trip_id' in trips_df.columns:
            for _, trip in trips_df.iterrows():
                trip_dict = trip.to_dict()
                
                # Formater les dates
                if 'departure_schedule' in trip_dict:
                    trip_dict['departure_schedule'] = format_date(trip_dict['departure_schedule'])
                if 'created_at' in trip_dict:
                    trip_dict['created_at'] = format_date(trip_dict['created_at'])  
                
                # Le rôle est déjà inclus dans la requête optimisée
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
