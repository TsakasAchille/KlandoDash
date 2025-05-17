from dash import html
import dash_bootstrap_components as dbc
from src.data_processing.processors.trip_processor import TripProcessor
import pandas as pd

def render_user_stats(user):
    if user is None:
        return None
    user_id = user.get('uid') or user.get('id')
    if not user_id:
        return dbc.Alert("Impossible de trouver l'identifiant de l'utilisateur", color="warning")
    # Récupérer les stats via TripProcessor
    trip_processor = TripProcessor()
    all_trips_df = trip_processor.get_all_user_trips(str(user_id))
    passenger_trips_df = trip_processor.get_trips_for_passenger(str(user_id))
    total_trips_count = len(all_trips_df)
    driver_trips_count = len(all_trips_df[all_trips_df['role']=='driver']) if 'role' in all_trips_df.columns else 0
    passenger_trips_count = len(passenger_trips_df)
    total_distance = all_trips_df['trip_distance'].sum() if 'trip_distance' in all_trips_df.columns and not all_trips_df.empty else 0
    # Layout
    stats_items = [
        ("Trajets effectués (total)", total_trips_count),
        ("Trajets en tant que conducteur", driver_trips_count),
        ("Trajets en tant que passager", passenger_trips_count),
        ("Distance totale", f"{total_distance:.1f} km")
    ]
    return dbc.Card([
        dbc.CardHeader("Statistiques utilisateur"),
        dbc.CardBody([
            html.Ul([
                html.Li(f"{label} : {value}") for label, value in stats_items
            ])
        ])
    ], className="klando-card")
