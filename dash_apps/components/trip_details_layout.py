from dash import html
import dash_bootstrap_components as dbc
import pandas as pd

from dash_apps.components.trip_stats import render_trip_stats
from dash_apps.components.trip_map import render_trip_map
from dash_apps.components.trip_passengers import render_trip_passengers
from dash_apps.components.trip_driver import render_trip_driver
from dash_apps.utils.db_utils import get_trip_passengers
from src.core.database import get_session, User
from dash_apps.components.trip_details import render_trip_card_html

# Styles globaux pour une cohérence visuelle
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '28px',
    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
    'padding': '15px',
    'overflow': 'hidden',
    'marginBottom': '16px'
}

COLUMN_STYLE = {
    'padding': '12px'  # Padding uniforme pour les colonnes
}

# Espacement entre les composants
SPACING_STYLE = {"marginBottom": "16px"}

def create_trip_details_layout(selected_trip_id, trips_data):
    """
    Crée le layout des détails d'un trajet sélectionné.
    
    Args:
        selected_trip_id: ID du trajet sélectionné
        trips_data: Données des trajets
        
    Returns:
        Un composant Dash à afficher
    """
    # Validation des données d'entrée
    if selected_trip_id is None or trips_data is None or len(trips_data) == 0:
        return dbc.Alert(f"Veuillez sélectionner un trajet dans le tableau.", color="info")
    
    trips_df = pd.DataFrame(trips_data)
    
    # Vérification de la validité des données
    if 'trip_id' not in trips_df.columns:
        return dbc.Alert("Erreur: la colonne 'trip_id' est absente dans les données.", color="danger")
    
    # Gestion du type de l'ID du trajet
    selected_trip_id_type = type(trips_df['trip_id'].iloc[0]) if not trips_df.empty else None
    if selected_trip_id_type and selected_trip_id_type != type(selected_trip_id):
        try:
            if selected_trip_id_type == int:
                selected_trip_id = int(selected_trip_id)
            elif selected_trip_id_type == str:
                selected_trip_id = str(selected_trip_id)
        except:
            pass
    
    # Récupération du trajet sélectionné
    selected_trip = trips_df[trips_df["trip_id"] == selected_trip_id]
    if selected_trip.empty:
        return dbc.Alert(f"Trajet introuvable. ID: {selected_trip_id}", color="danger")
    
    trip_row = selected_trip.iloc[0]
    
    # Récupération des passagers
    trip_id = trip_row.get("trip_id")
    passenger_ids = get_trip_passengers(trip_id)
    if not passenger_ids:
        passengers_list = []
    else:
        with get_session() as session:
            users = session.query(User).filter(User.uid.in_(passenger_ids)).all()
            users_df = pd.DataFrame([u.to_dict() for u in users]) if users else pd.DataFrame()
        passengers_list = users_df.to_dict("records") if not users_df.empty else []
    
    # Génération des composants
    trip_details_card = html.Div(
        html.Iframe(
            srcDoc=render_trip_card_html(trip_row),
            style={
                'width': '100%',
                'height': '600px',
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            sandbox='allow-scripts',
        ),
        style=CARD_STYLE
    )
    
    trip_stats_component = render_trip_stats(trip_row)
    trip_map_component = render_trip_map(trip_row)
    trip_passengers_component = render_trip_passengers(passengers_list)
    trip_driver_component = render_trip_driver(trip_row)
    
    # Construction du layout en réutilisant les composants directement
    return dbc.Row([
        dbc.Col([
            # Détails du trajet avec espacement
            html.Div(trip_details_card, style=SPACING_STYLE),
            # Conducteur du trajet
            html.Div(trip_driver_component, style=SPACING_STYLE),
            # Statistiques du trajet
            trip_stats_component,
        ], md=4, xs=12, style=COLUMN_STYLE),
        dbc.Col([
            # Carte du trajet avec espacement
            html.Div(
                trip_map_component if trip_map_component else 
                html.Div(
                    "Carte non disponible pour ce trajet.", 
                    style={"padding": "30px", "textAlign": "center", "color": "#666", 
                          "backgroundColor": "white", "borderRadius": "28px", 
                          "boxShadow": "rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px",
                          "padding": "15px"}
                ),
                style=SPACING_STYLE
            ),
            # Liste des passagers
            trip_passengers_component
        ], md=8, xs=12, style=COLUMN_STYLE)
    ], className="align-items-stretch", style={"margin": "8px 0"})
