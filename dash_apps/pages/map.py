import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_apps.config import Config
import logging

logger = logging.getLogger(__name__)

def create_maplibre_simple():
    """MapLibre simple - utilise seulement les assets automatiques de Dash"""
    
    # Récupérer l'URL du style depuis la config (avec clé API Firebase)
    maplibre_style_url = Config.MAPLIBRE_STYLE_URL
    print("[LAYOUT] create_maplibre_simple called with style URL: %s", maplibre_style_url)
    return html.Div([
        html.H3("🔧 DEBUG: Fonction create_maplibre_simple appelée"),
        html.P(f"Style URL: {maplibre_style_url}"),
        html.Div(
            id="maplibre-map",
            style={
                "height": "500px",
                "width": "100%",
                "border": "2px solid red",
                "backgroundColor": "#f0f0f0"
            },
            **{"data-style-url": maplibre_style_url}  # Passer l'URL via attribut HTML
        ),
        html.P("🔧 DEBUG: Container créé avec data-style-url")
    ])


def get_layout():
    """Génère le layout de la page de carte avec des IDs uniquement pour cette page"""
    print("[LAYOUT] get_layout called for map page")
    return dbc.Container([
        html.H2("Carte - BETA testing", style={"marginTop": "20px", "marginBottom": "16px"}),
        html.P("Vue d'ensemble géographique", className="text-muted"),
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
                        id="map-trip-display", 
                        value="1", 
                        readonly=True, 
                        style={"textAlign": "center", "width": "80px"}
                    ),
                    dbc.Button("+", id="map-trip-inc", color="secondary", outline=True),
                ])
            ], md=12)
        ], className="mb-2"),
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
                             "height": "80vh",
                             "overflow": "auto"
                         })
            ], md=3)
        ]),
    ], fluid=True)


# Définir le layout comme CALLABLE pour exécuter get_layout au rendu (après config logging)
def layout():
    return get_layout()

# L'enregistrement se fera automatiquement par Dash Pages lors de la découverte des modules
