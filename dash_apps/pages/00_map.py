from dash import html, dcc, Input, Output, callback
import json
import dash_bootstrap_components as dbc
from dash import dash_table
from dash_apps.components.map_trips_table import render_map_trips_table
from dash_apps.config import Config
from dash_apps.repositories.trip_repository import TripRepository
import polyline as polyline_lib


def _trip_to_option(trip):
    try:
        label = f"{trip.departure_name or '-'} → {trip.destination_name or '-'}"
        return {"label": label, "value": trip.trip_id}
    except Exception:
        return {"label": trip.trip_id, "value": trip.trip_id}


def _polyline_to_geojson(p):
    try:
        if isinstance(p, bytes):
            p = p.decode('utf-8')
        coords_latlon = polyline_lib.decode(p)  # [(lat, lon), ...]
        # GeoJSON expects [lon, lat]
        coords_lonlat = [[lon, lat] for (lat, lon) in coords_latlon]
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": coords_lonlat},
                    "properties": {},
                }
            ],
        }
    except Exception:
        return None


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


def _get_last_trips(n=10):
    # Fetch last n trips using repository (ordered by created_at desc by default)
    data = TripRepository.get_trips_paginated(page=0, page_size=n)
    trips = data.get("trips", []) if isinstance(data, dict) else []
    return trips


_TRIPS = _get_last_trips(10)
_OPTIONS = [_trip_to_option(t) for t in _TRIPS]

def _shorten(text, n=28):
    try:
        s = str(text)
    except Exception:
        s = ""
    return s if len(s) <= n else s[: n - 1] + "…"

_MARKS = None  # We'll use a simple numeric slider (count of last trips)

def _trips_to_table_rows(trips):
    rows = []
    for i, t in enumerate(trips, start=1):
        rows.append({
            "#": i,
            "Départ": getattr(t, 'departure_name', '-') or '-',
            "Arrivée": getattr(t, 'destination_name', '-') or '-',
            "TripID": getattr(t, 'trip_id', '-') or '-',
        })
    return rows


layout = dbc.Container([
    html.H2("Carte", style={"marginTop": "20px", "marginBottom": "16px"}),
    html.P("Vue d'ensemble géographique (style JSON MapLibre)", className="text-muted"),
    dbc.Row([
        dbc.Col([
            html.Label("Nombre de derniers trajets à afficher"),
            dcc.Slider(
                id="map-trip-count",
                min=1 if _TRIPS else 0,
                max=len(_TRIPS) if _TRIPS else 0,
                step=1,
                value=min(3, len(_TRIPS)) if _TRIPS else 0,
                updatemode="mouseup",
                tooltip={"placement": "bottom", "always_visible": False},
                included=False,
            )
        ], md=12)
    ], className="mb-2"),
    dbc.Row([
        dbc.Col([
            # Tableau compact spécifique à la page Carte, avec lien "Voir trajet"
            render_map_trips_table(_TRIPS)
        ], md=12)
    ], className="mb-3"),
    create_maplibre_container(),
], fluid=True)


@callback(
    Output("home-maplibre", "data-geojson"),
    Input("map-trip-count", "value"),
)
def update_map_geojson(count):
    if not _TRIPS or not count or count <= 0:
        return None
    count = max(1, min(int(count), len(_TRIPS)))
    features = []
    for trip in _TRIPS[:count]:
        p = getattr(trip, 'polyline', None)
        if not p:
            continue
        try:
            if isinstance(p, bytes):
                p = p.decode('utf-8')
            coords_latlon = polyline_lib.decode(p)  # [(lat, lon), ...]
            coords_lonlat = [[lon, lat] for (lat, lon) in coords_latlon]
            features.append({
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coords_lonlat},
                "properties": {"trip_id": getattr(trip, 'trip_id', None)},
            })
            if coords_lonlat:
                start = coords_lonlat[0]
                end = coords_lonlat[-1]
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": start},
                    "properties": {"role": "start", "trip_id": getattr(trip, 'trip_id', None)},
                })
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": end},
                    "properties": {"role": "end", "trip_id": getattr(trip, 'trip_id', None)},
                })
        except Exception:
            continue
    if not features:
        return None
    collection = {"type": "FeatureCollection", "features": features}
    return json.dumps(collection)
