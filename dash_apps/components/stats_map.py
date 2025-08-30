import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash_apps.config import Config

def render_stats_map(trips_data):
    """
    Rend la carte des statistiques des trajets en utilisant des composants Dash
    
    Args:
        trips_data: Données des trajets sous forme de liste de dictionnaires
    
    Returns:
        Un composant Dash pour afficher la carte des statistiques
    """
    if not trips_data:
        return html.Div("Aucune donnée de trajet disponible")
    
    # Convertir en DataFrame
    trips_df = pd.DataFrame(trips_data)
    
    # Vérifier si les colonnes de coordonnées sont disponibles
    has_coordinates = all(col in trips_df.columns for col in ['departure_latitude', 'departure_longitude', 'destination_latitude', 'destination_longitude'])
    
    # Si les colonnes ont les anciens noms, les renommer pour compatibilité
    if not has_coordinates and all(col in trips_df.columns for col in ['departure_lat', 'departure_lng', 'destination_lat', 'destination_lng']):
        trips_df = trips_df.copy()
        # Créer un mapping des anciens noms vers les nouveaux noms
        column_mapping = {
            'departure_lat': 'departure_latitude',
            'departure_lng': 'departure_longitude',
            'destination_lat': 'destination_latitude',
            'destination_lng': 'destination_longitude'
        }
        # Renommer les colonnes
        trips_df.rename(columns=column_mapping, inplace=True)
        has_coordinates = True
    
    # Calculer les métriques de la carte
    total_trips = len(trips_df)
    total_distance = trips_df['distance'].sum() if 'distance' in trips_df.columns else 0
    
    # Métriques de la carte
    map_metrics = [
        html.Div([
            html.H4("Métriques de trajet", className="card-title"),
            html.Div([
                html.P([html.Strong("Nombre total de trajets: "), f"{total_trips}"]),
                html.P([html.Strong("Distance totale parcourue: "), f"{total_distance:.0f} km"]),
            ])
        ], className="card-body")
    ]
    
    map_metrics_card = dbc.Card(map_metrics, className="mb-4", style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})
    
    # Filtres pour la carte
    filter_card = dbc.Card([
        dbc.CardBody([
            html.H4("Options d'affichage", className="card-title"),
            dbc.Row([
                dbc.Col([
                    html.Label("Nombre maximum de trajets à afficher:"),
                    dcc.Slider(
                        id="stats-map-max-trips-slider",
                        min=1,
                        max=50,
                        value=10,
                        marks={i: str(i) for i in range(0, 51, 10)},
                        step=1
                    ),
                ], width=12),
                dbc.Col([
                    html.Label("Couches supplémentaires:"),
                    dcc.Checklist(
                        id="stats-map-show-heat",
                        options=[{"label": " Bulles densité destinations", "value": "heat"}],
                        value=["heat"],
                        inputStyle={"marginRight": "6px"},
                        labelStyle={"marginRight": "16px"}
                    ),
                ], width=12),
            ], className="mb-3"),
        ])
    ], className="mb-4", style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})
    
    # Conteneur MapLibre (style JSON, pas de tuiles PNG)
    map_container = html.Div(
        id="stats-map-iframe-container",
        children=create_maplibre_container(style_height="600px"),
        style={"height": "600px", "width": "100%", "borderRadius": "8px", "overflow": "hidden", "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"}
    )
    
    # Tableau récapitulatif des trajets
    summary_table = create_trips_summary_table(trips_df)
    
    # Layout final
    return html.Div([
        html.H3("Carte des trajets", className="mb-4"),
        map_metrics_card,
        filter_card,
        map_container,
        html.H4("Détails des trajets", className="mt-4 mb-3"),
        summary_table
    ])

@callback(
    Output("stats-map-iframe-container", "children"),
    Input("stats-map-max-trips-slider", "value"),
    Input("stats-map-show-heat", "value"),
    Input("stats-trips-store", "data")
)
def update_map_display(max_trips, heat_values, trips_data):
    """
    Met à jour l'affichage de la carte. Pour l'instant, MapLibre n'utilise pas ces options côté client.
    """
    # On renvoie simplement le conteneur MapLibre; l'initialisation se fait côté client via JS
    return create_maplibre_container(style_height="600px")

def create_maplibre_container(style_height="600px"):
    """
    Crée le conteneur pour une carte MapLibre GL initialisée côté client.
    Utilise Config.MAPLIBRE_STYLE_URL (FireStore) et ajoute la clé API aux URLs de base.
    """
    style_url = Config.MAPLIBRE_STYLE_URL or "https://demotiles.maplibre.org/globe.json"
    api_key = Config.MAPLIBRE_API_KEY or ""
    return html.Div(
        id="maplibre-stats-map",
        className="maplibre-container",
        **{"data-style-url": style_url, "data-api-key": api_key},
        style={
            "height": style_height,
            "width": "100%",
            "borderRadius": "8px",
            "overflow": "hidden",
        }
    )

def create_trips_summary_table(trips_df):
    """
    Crée un tableau récapitulatif des trajets
    
    Args:
        trips_df: DataFrame contenant les données des trajets
    
    Returns:
        Un composant Dash pour afficher le tableau récapitulatif
    """
    if trips_df.empty:
        return html.Div("Aucune donnée de trajet disponible")
    
    # Sélectionner les colonnes pertinentes si elles existent
    display_columns = []
    for col in ['departure_name', 'destination_name', 'distance', 'passenger_price', 'departure_date']:
        if col in trips_df.columns:
            display_columns.append(col)
    
    if display_columns:
        summary_df = trips_df[display_columns]
    else:
        # Si aucune colonne spécifique n'est disponible, utiliser toutes les colonnes
        summary_df = trips_df
    
    # Limiter aux 10 premiers trajets pour la lisibilité
    summary_df = summary_df.head(10)
    
    # Créer le tableau avec dbc
    table_header = [html.Thead(html.Tr([html.Th(col.replace('_', ' ').title()) for col in summary_df.columns]))]
    table_body = [html.Tbody([html.Tr([html.Td(str(summary_df.iloc[i][col])) for col in summary_df.columns]) for i in range(len(summary_df))])]
    
    table = dbc.Table(table_header + table_body, bordered=True, hover=True, responsive=True, striped=True)
    
    return html.Div([table], style={"overflowX": "auto"})
