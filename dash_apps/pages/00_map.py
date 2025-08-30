from dash import html
import dash_bootstrap_components as dbc
from dash_apps.config import Config


def create_maplibre_container(style_height="80vh"):
    style_url = Config.MAPLIBRE_STYLE_URL or "https://demotiles.maplibre.org/globe.json"
    api_key = Config.MAPLIBRE_API_KEY or ""
    return html.Div(
        id="home-maplibre",
        className="maplibre-container",
        **{"data-style-url": style_url, "data-api-key": api_key},
        style={
            "height": style_height,
            "width": "100%",
            "borderRadius": "12px",
            "overflow": "hidden",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
        }
    )


layout = dbc.Container([
    html.H2("Carte", style={"marginTop": "20px", "marginBottom": "16px"}),
    html.P("Vue d'ensemble géographique (style JSON MapLibre)", className="text-muted"),
    create_maplibre_container(),
], fluid=True)
