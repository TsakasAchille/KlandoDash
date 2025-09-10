import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_apps.config import Config

def create_maplibre_container(style_height="80vh"):
    """Crée le conteneur MapLibre avec la configuration appropriée"""
    # Utiliser MAPLIBRE_STYLE_URL qui contient maintenant l'URL complète avec clé API
    style_url = Config.MAPLIBRE_STYLE_URL #or "https://demotiles.maplibre.org/globe.json"
    
    return html.Div(
        id="home-maplibre",
        className="maplibre-container",
        **{"data-style-url": style_url, "data-selected-trip-id": ""},
        style={
            "height": style_height,
            "width": "100%",
            "borderRadius": "12px",
            "overflow": "hidden",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)"
        }
    )


def get_layout():
    """Génère le layout de la page de carte avec des IDs uniquement pour cette page"""
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
                create_maplibre_container()
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


# Définir le layout au niveau du module pour Dash Pages
layout = get_layout()

# L'enregistrement se fera automatiquement par Dash Pages lors de la découverte des modules
