import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_apps.config import Config
import logging

logger = logging.getLogger(__name__)

# Importer les callbacks AVANT la définition du layout
from dash_apps.callbacks import map_callbacks  # noqa: F401

def create_maplibre_simple():
    """MapLibre simple - container avec style de la config et fallback automatique"""
    
    # Utiliser le style de la config en premier, avec fallback automatique en cas d'erreur CORS
    maplibre_style_url = Config.MAPLIBRE_STYLE_URL or "https://demotiles.maplibre.org/style.json"
    maplibre_api_key = Config.MAPLIBRE_API_KEY or ""
    
    return html.Div(
        id="maplibre-map",
        style={
            "height": "70vh",
            "width": "100%",
        },
        **{
            "data-style-url": maplibre_style_url,
            "data-api-key": maplibre_api_key
        }
    )


def get_layout():
    """Génère le layout de la page Map avec composants requis pour callbacks JS/Python"""
    # Avertissement si le style MapLibre n'est pas configuré
    style_warning = None
    try:
        if not Config.MAPLIBRE_STYLE_URL:
            style_warning = dbc.Alert(
                "MAPLIBRE_STYLE_URL non défini dans la configuration. La carte utilisera un style vide.",
                color="warning",
                className="mb-2",
            )
    except Exception:
        # En cas d'erreur d'accès à la config, ne bloque pas l'affichage
        style_warning = dbc.Alert(
            "Impossible de lire MAPLIBRE_STYLE_URL (voir logs)",
            color="warning",
            className="mb-2",
        )

    return dbc.Container([
        html.H2("Carte", style={"marginTop": "20px", "marginBottom": "16px"}),
        style_warning if style_warning else html.Div(),
        dbc.Row([
            dbc.Col([
                html.Div()
            ], md=6)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("-", id="map-trip-dec", color="secondary", outline=True),
                    dbc.Input(
                        id="map-trip-count", 
                        value="5", 
                        readonly=True, 
                        style={"textAlign": "center", "width": "80px"}
                    ),
                    dbc.Button("+", id="map-trip-inc", color="secondary", outline=True),
                ])
            ], md=12)
        ], className="mb-2"),
        # Bridge components requis par map_callbacks.py et mapbridge.js
        dcc.Store(id="map-selected-trips", storage_type="session", data=[]),
        dcc.Store(id="map-hover-trip-id", storage_type="memory", data=None),
        dcc.Store(id="map-click-trip-id", storage_type="memory", data=None),
        dcc.Store(id="map-detail-visible", storage_type="session", data=False),
        dcc.Interval(id="map-event-poll", interval=5000, n_intervals=0),  # Réduit à 5s pour moins de charge
        html.Div(id="home-maplibre", style={"display": "none"}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Tableau des trajets", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Loading(html.Div(id="map-trips-table-container"), type="default")
                    ])
                ], className="shadow-sm")
            ], md=12)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Carte interactive", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Loading(create_maplibre_simple(), type="default")
                    ], style={"padding": "0"})
                ], className="shadow-sm")
            ], md=9),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("Détails du trajet", className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="map-side-panel", children=[
                            html.Div([
                                html.I(className="fas fa-mouse-pointer me-2"),
                                html.Span("Cliquez sur un trajet sur la carte pour voir les détails")
                            ], className="text-muted text-center py-5")
                        ])
                    ], style={"height": "60vh", "overflow": "auto"})
                ], className="shadow-sm")
            ], md=3)
        ]),
    ], fluid=True)


# Définir le layout comme CALLABLE pour exécuter get_layout au rendu (après config logging)
def layout():
    return get_layout()

# L'enregistrement des callbacks se fait automatiquement via l'import en haut du fichier
