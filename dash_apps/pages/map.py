import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_apps.config import Config
import logging

logger = logging.getLogger(__name__)

def create_maplibre_simple():
    """MapLibre simple - container seul avec style Firebase via data-style-url"""
    
    # Récupérer l'URL du style depuis la config (avec clé API Firebase)
    maplibre_style_url = Config.MAPLIBRE_STYLE_URL
    return html.Div(
        id="maplibre-map",
        style={
            "height": "70vh",
            "width": "100%",
        },
        **{"data-style-url": maplibre_style_url}
    )


def get_layout():
    """Génère le layout de la page Map avec composants requis pour callbacks JS/Python"""
    return dbc.Container([
        html.H2("Carte", style={"marginTop": "20px", "marginBottom": "16px"}),
        dbc.Row([
            dbc.Col([
                dbc.InputGroup([
                    dbc.Input(id="map-trip-input", type="number", placeholder="Numéro trajet", value=1),
                    dbc.Button("Charger", id="map-load-trip", color="primary"),
                ])
            ], md=6)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("-", id="map-trip-dec", color="secondary", outline=True),
                    dbc.Input(
                        id="map-trip-count", 
                        value="1", 
                        readonly=True, 
                        style={"textAlign": "center", "width": "80px"}
                    ),
                    dbc.Button("+", id="map-trip-inc", color="secondary", outline=True),
                ])
            ], md=12)
        ], className="mb-2"),
        # Bridge components requis par map_callbacks.py et mapbridge.js
        dcc.Store(id="map-selected-trips"),
        dcc.Store(id="map-hover-trip-id"),
        dcc.Store(id="map-click-trip-id"),
        dcc.Store(id="map-detail-visible"),
        dcc.Interval(id="map-event-poll", interval=800, n_intervals=0),
        html.Div(id="home-maplibre", style={"display": "none"}),
        dbc.Row([
            dbc.Col([
                html.Div(id="map-trips-table-container")
            ], md=12)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                create_maplibre_simple()
            ], md=9),
            dbc.Col([
                html.Div(id="map-side-panel", children=html.Div("Sélectionnez un trajet sur la carte"),
                         style={
                             "backgroundColor": "white",
                             "borderRadius": "12px",
                             "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
                             "padding": "12px",
                             "height": "70vh",
                             "overflow": "auto"
                         })
            ], md=3)
        ]),
    ], fluid=True)


# Définir le layout comme CALLABLE pour exécuter get_layout au rendu (après config logging)
def layout():
    return get_layout()

# Enregistrer les callbacks de la page Map via import (même pattern que trips.py)
from dash_apps.callbacks import map_callbacks  # noqa: F401

# L'enregistrement se fera automatiquement par Dash Pages lors de la découverte des modules
