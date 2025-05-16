import dash_bootstrap_components as dbc
from dash import html
import pandas as pd
from dash_apps.components.trip_map import render_trip_map
from dash_apps.components.trip_stats import render_trip_stats
from dash_apps.components.trip_passengers import render_trip_passengers
from dash_apps.utils.db_utils import get_trip_passengers
from src.core.database import get_session, User


def trip_details_layout(selected_trip, trips_data):
    """
    Affiche le bloc détaillé pour un trajet sélectionné (détails, stats, carte, passagers), stylé avec les cards Klando.
    Args:
        selected_trip: DataFrame row (iloc[0]) du trajet sélectionné
        trips_data: liste de dicts (tous les trajets)
    Returns:
        dbc.Row
    """
    fields = [
        ("Départ", selected_trip.get("departure_name", "-")),
        ("Destination", selected_trip.get("destination_name", "-")),
        ("Date", selected_trip.get("departure_date", "-")),
        ("Heure de départ", selected_trip.get("departure_schedule", "-")),
        ("Conducteur (ID)", selected_trip.get("driver_id", "-")),
    ]
    details_card = dbc.Card([
        dbc.CardHeader("Détails du trajet sélectionné", className="klando-card-header"),
        dbc.CardBody([
            html.Ul([
                html.Li([
                    html.Span(label + " : ", className="klando-label"),
                    html.Span(str(value), className="klando-value")
                ], style={"marginBottom": "2px", "fontSize": "1.15em"})
                for label, value in fields
            ], style={"listStyle": "none", "padding": 0, "margin": 0})
        ], className="klando-card-body")
    ], className="klando-card mb-4")

    trip_map = render_trip_map(selected_trip)
    polyline_val = selected_trip.get("trip_polyline", None)
    debug_polyline = html.Div([
        html.Small("trip_polyline : ", style={"fontWeight": "bold"}),
        html.Code(str(polyline_val))
    ], style={"marginTop": "8px", "color": "#999"})

    trip_stats = render_trip_stats(selected_trip)
    if hasattr(trip_stats, "type") and trip_stats.type == "Card":
        trip_stats = trip_stats  # déjà une Card custom
    else:
        trip_stats = dbc.Card([
            dbc.CardHeader("Statistiques du trajet", className="klando-card-header"),
            dbc.CardBody([trip_stats], className="klando-card-body")
        ], className="klando-card mb-4")

    # Récupération SQL des passagers
    trip_id = selected_trip.get("trip_id")
    passenger_ids = get_trip_passengers(trip_id)
    if not passenger_ids:
        passengers_list = []
    else:
        with get_session() as session:
            users = session.query(User).filter(User.uid.in_(passenger_ids)).all()
            users_df = pd.DataFrame([u.to_dict() for u in users]) if users else pd.DataFrame()
        passengers_list = users_df.to_dict("records") if not users_df.empty else []
    trip_passengers = render_trip_passengers(passengers_list)
    if hasattr(trip_passengers, "type") and trip_passengers.type == "Card":
        trip_passengers = trip_passengers  # déjà une Card custom
    else:
        trip_passengers = dbc.Card([
            dbc.CardHeader("Passagers & Réservations", className="klando-card-header"),
            dbc.CardBody([trip_passengers], className="klando-card-body")
        ], className="klando-card mb-4")

    return dbc.Row([
        dbc.Col([
            details_card,
            trip_stats
        ], md=4, xs=12),
        dbc.Col([
            html.Div(trip_map) if trip_map else html.Div("Aucune carte générée (polyline absente ou invalide)", style={"color": "#B00"}),
            html.Div([
                html.Small("trip_polyline : ", style={"fontWeight": "bold"}),
                html.Code(str(polyline_val))
            ], style={"marginTop": "8px", "color": "#B00", "fontSize": "12px"}) if polyline_val else None,
            trip_passengers
        ], md=8, xs=12)
    ], className="g-3 align-items-stretch mb-4")
