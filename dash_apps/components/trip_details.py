import dash_bootstrap_components as dbc
from dash import html
import pandas as pd
from dash_apps.components.trip_map import render_trip_map
from dash_apps.components.trip_stats import render_trip_stats
from dash_apps.components.trip_passengers import render_trip_passengers
from dash_apps.utils.db_utils import get_trip_passengers
from src.core.database import get_session, User
import jinja2
import os


def render_trip_card_html(trip_data):
    """
    Génère le HTML pour la card de détail du trajet en utilisant le template Jinja2.
    
    Args:
        trip_data: dictionnaire contenant les informations du trajet
    Returns:
        HTML généré à partir du template
    """
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('trip_details_template.jinja2')
    return template.render(trip=trip_data)


def trip_details_layout(selected_trip, trips_data):
    """
    Affiche le bloc détaillé pour un trajet sélectionné (détails, stats, carte, passagers), stylé avec les cards Klando.
    Args:
        selected_trip: DataFrame row (iloc[0]) du trajet sélectionné
        trips_data: liste de dicts (tous les trajets)
    Returns:
        dbc.Row
    """
    # Convertir le DataFrame row en dictionnaire si ce n'est pas déjà fait
    if hasattr(selected_trip, 'to_dict'):
        trip_dict = selected_trip.to_dict()
    else:
        trip_dict = dict(selected_trip)
    
    # Génération du HTML pour la card de détail du trajet en utilisant Jinja
    trip_html = render_trip_card_html(trip_dict)
    
    # Création du composant Dash en utilisant la technique qui fonctionne bien pour trip_map
    details_card = html.Div(
        html.Iframe(
            srcDoc=trip_html,
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
        style={
            'backgroundColor': 'white',
            'borderRadius': '28px',
            'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
            'padding': '15px',
            'overflow': 'hidden',
            'margin': '5px'
        }
    )

    # Rendu de la carte sans debug info
    trip_map = render_trip_map(selected_trip)

    # Notre composant trip_stats est déjà un iframe avec le template, pas besoin de l'encapsuler
    trip_stats = render_trip_stats(selected_trip)

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
    # Utilisation directe du composant trip_passengers avec son propre style cohérent
    trip_passengers = render_trip_passengers(passengers_list)

    return dbc.Row([
        dbc.Col([
            html.Div(details_card, style={"marginBottom": "20px"}),
            html.Div(trip_stats)
        ], md=4, xs=12, style={"paddingRight": "20px"}),
        dbc.Col([
            html.Div(trip_map, style={"marginBottom": "20px"}) if trip_map else html.Div("Aucune carte générée (polyline absente ou invalide)", style={"color": "#B00", "marginBottom": "20px"}),
            html.Div(trip_passengers)
        ], md=8, xs=12, style={"paddingLeft": "20px"})
    ], className="g-4 align-items-stretch mb-4", style={"margin": "0px"})
