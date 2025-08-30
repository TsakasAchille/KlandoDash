from dash import html, dcc, Input, Output, callback
import json
import dash_bootstrap_components as dbc
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

_MARKS = {i: _shorten(o["label"]) for i, o in enumerate(_OPTIONS)} if _OPTIONS else {}


layout = dbc.Container([
    html.H2("Carte", style={"marginTop": "20px", "marginBottom": "16px"}),
    html.P("Vue d'ensemble géographique (style JSON MapLibre)", className="text-muted"),
    dbc.Row([
        dbc.Col([
            dcc.Slider(
                id="map-trip-index",
                min=0,
                max=max(0, len(_OPTIONS) - 1),
                step=1,
                value=0 if _OPTIONS else None,
                marks=_MARKS,
                updatemode="mouseup",
                tooltip={"placement": "bottom", "always_visible": False},
                included=False,
            )
        ], md=12)
    ], className="mb-3"),
    create_maplibre_container(),
], fluid=True)


@callback(
    Output("home-maplibre", "data-geojson"),
    Input("map-trip-index", "value"),
)
def update_map_geojson(selected_index):
    if selected_index is None:
        return None
    if not _TRIPS or selected_index < 0 or selected_index >= len(_TRIPS):
        return None
    trip = _TRIPS[selected_index]
    p = getattr(trip, 'polyline', None)
    if not p:
        return None
    gj = _polyline_to_geojson(p)
    # enrich with start/end points if possible from the polyline
    try:
        if isinstance(p, bytes):
            p = p.decode('utf-8')
        coords_latlon = polyline_lib.decode(p)
        if coords_latlon:
            start = coords_latlon[0]
            end = coords_latlon[-1]
            start_pt = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [start[1], start[0]]}, "properties": {"role": "start"}}
            end_pt = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [end[1], end[0]]}, "properties": {"role": "end"}}
            if gj and gj.get("features") is not None:
                gj["features"].extend([start_pt, end_pt])
    except Exception:
        pass
    return json.dumps(gj) if gj else None
