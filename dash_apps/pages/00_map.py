from dash import html, dcc, Input, Output, State, callback, ClientsideFunction
import dash
import json
import dash_bootstrap_components as dbc
from dash import dash_table
from dash_apps.components.map_trips_table import render_map_trips_table
from dash_apps.components.user_profile import render_user_profile, render_user_summary
from dash_apps.config import Config
from dash_apps.repositories.repository_factory import RepositoryFactory
import polyline as polyline_lib


def _trip_to_option(trip):
    try:
        label = f"{trip.departure_name or '-'} → {trip.destination_name or '-'}"
        return {"label": label, "value": trip.trip_id}
    except Exception:
        return {"label": trip.trip_id, "value": trip.trip_id}




def create_maplibre_container(style_height="80vh"):
    style_url = Config.MAPLIBRE_STYLE_URL or "https://demotiles.maplibre.org/globe.json"
    api_key = Config.MAPLIBRE_API_KEY or ""
    return html.Div(
        id="home-maplibre",
        className="maplibre-container",
        **{"data-style-url": style_url, "data-api-key": api_key, "data-selected-trip-id": ""},
        style={
            "height": style_height,
            "width": "100%",
            "borderRadius": "12px",
            "overflow": "hidden",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
        }
    )


# Keep the selected trip id in a DOM attribute so MapLibre JS can re-apply highlight after reload
@callback(
    Output("home-maplibre", "data-selected-trip-id"),
    Input("map-click-trip-id", "data"),
    prevent_initial_call=False,
)
def expose_selected_trip_to_dom(selected_trip_id):
    return selected_trip_id or ""


def _get_last_trips(n=10):
    # Fetch last n trips using REST repository
    try:
        trip_repository = RepositoryFactory.get_trip_repository()
        trips = trip_repository.list_trips(limit=n)
        return trips
    except Exception as e:
        print(f"Warning: Could not load trips data: {e}")
        return []


def _get_trips_options():
    """Lazy load trips options to avoid database connection at import time"""
    trips = _get_last_trips(10)
    return [_trip_to_option(t) for t in trips]


# Initialize as empty, will be populated when needed
_TRIPS = []
_OPTIONS = []

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
            "Trip_ID": getattr(t, 'trip_id', '-') or '-',
        })
    return rows


layout = dbc.Container([
    html.H2("Carte - BETA testing", style={"marginTop": "20px", "marginBottom": "16px"}),
    html.P("Vue d'ensemble géographique", className="text-muted"),
    # Stores interactivité
    dcc.Store(id="map-selected-trips", storage_type="session", data=[]),
    dcc.Store(id="map-hover-trip-id", data=None),
    dcc.Store(id="map-click-trip-id", data=None, storage_type="session"),
    dcc.Store(id="map-detail-visible", data=False, storage_type="session"),
    dcc.Interval(id="map-event-poll", interval=800, n_intervals=0),
    dbc.Row([
        dbc.Col([
            html.Label("Nombre de derniers trajets à afficher"),
            dbc.InputGroup([
                dbc.Button("−", id="map-trip-dec", color="secondary", outline=True),
                dcc.Input(
                    id="map-trip-count",
                    type="number",
                    min=0,
                    max=100,
                    step=1,
                    value=3,
                    persistence=True,
                    persistence_type="session",
                    style={"width": "90px", "textAlign": "center"}
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


@callback(
    Output("map-trip-count", "value"),
    Input("map-trip-inc", "n_clicks"),
    Input("map-trip-dec", "n_clicks"),
    State("map-trip-count", "value"),
    prevent_initial_call=True,
)
def adjust_map_trip_count(n_inc, n_dec, current):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    trigger = ctx.triggered[0]["prop_id"].split(".")[0]
    total = len(_TRIPS) if _TRIPS else 0
    if total <= 0:
        return 0
    current = int(current or 0)
    if trigger == "map-trip-inc":
        new_val = current + 1
    elif trigger == "map-trip-dec":
        new_val = current - 1
    else:
        raise dash.exceptions.PreventUpdate
    # clamp
    new_val = max(1, min(new_val, total))
    return new_val

@callback(
    Output("home-maplibre", "data-geojson"),
    Input("map-trip-count", "value"),
    Input("map-selected-trips", "data"),
)
def update_map_geojson(count, selected_ids):
    if not _TRIPS or not count or count <= 0:
        return None
    count = max(1, min(int(count), len(_TRIPS)))
    # If there is a selection, use it; else default to last N trips
    visible_trips = _TRIPS[:count]
    # If nothing is selected, show none (do not default to all)
    selected_set = set(selected_ids or [])
    features = []
    # Palette de couleurs pour différencier les trajets simultanés
    palette = [
        "#4281ec",  # bleu
        "#e74c3c",  # rouge
        "#27ae60",  # vert
        "#f1c40f",  # jaune
        "#8e44ad",  # violet
        "#16a085",  # sarcelle
        "#d35400",  # orange
        "#2c3e50",  # bleu sombre
    ]
    filtered = [t for t in visible_trips if getattr(t, 'trip_id', None) in selected_set]
    for idx, trip in enumerate(filtered):
        p = getattr(trip, 'polyline', None)
        if not p:
            continue
        try:
            if isinstance(p, bytes):
                p = p.decode('utf-8')
            coords_latlon = polyline_lib.decode(p)  # [(lat, lon), ...]
            coords_lonlat = [[lon, lat] for (lat, lon) in coords_latlon]
            # propriétés enrichies pour interactions
            props = {
                "trip_id": getattr(trip, 'trip_id', None),
                "color": palette[idx % len(palette)],
                "driver_id": getattr(trip, 'driver_id', None),
                "driver_name": getattr(trip, 'driver_name', None) if hasattr(trip, 'driver_name') else None,
                "seats_booked": getattr(trip, 'seats_booked', None),
                "seats_available": getattr(trip, 'seats_available', None),
                "passenger_price": getattr(trip, 'passenger_price', None),
                "distance": getattr(trip, 'distance', None),
                "departure_name": getattr(trip, 'departure_name', None),
                "destination_name": getattr(trip, 'destination_name', None),
                "departure_schedule": str(getattr(trip, 'departure_schedule', '') or ''),
            }
            features.append({
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": coords_lonlat},
                "properties": props,
            })
            if coords_lonlat:
                start = coords_lonlat[0]
                end = coords_lonlat[-1]
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": start},
                    "properties": {
                        "role": "start",
                        "trip_id": props["trip_id"],
                        "color": props["color"],
                    },
                })
                features.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": end},
                    "properties": {
                        "role": "end",
                        "trip_id": props["trip_id"],
                        "color": props["color"],
                    },
                })
                # point milieu pour icône voiture
                try:
                    mid = coords_lonlat[len(coords_lonlat)//2]
                    features.append({
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": mid},
                        "properties": {
                            "role": "car",
                            "trip_id": props["trip_id"],
                            "color": props["color"],
                        },
                    })
                except Exception:
                    pass
        except Exception:
            continue
    if not features:
        # Send empty collection to clear previously rendered polylines
        return json.dumps({"type": "FeatureCollection", "features": []})
    collection = {"type": "FeatureCollection", "features": features}
    return json.dumps(collection)


# Render the table with checkboxes reflecting current selection
@callback(
    Output("map-trips-table-container", "children"),
    Input("map-trip-count", "value"),
    Input("map-selected-trips", "data"),
    Input("map-click-trip-id", "data"),
)
def render_map_table(count, selected_ids, active_trip_id):
    if not _TRIPS or not count or count <= 0:
        return render_map_trips_table([], selected_ids or [])
    count = max(1, min(int(count), len(_TRIPS)))
    trips = _TRIPS[:count]
    return render_map_trips_table(trips, selected_ids or [], active_id=active_trip_id)


@callback(
    Output("map-selected-trips", "data"),
    Input("map-trip-count", "value"),
    Input({"type": "map-trip-check", "index": dash.ALL}, "value"),
    State({"type": "map-trip-check", "index": dash.ALL}, "id"),
    State("map-selected-trips", "data"),
    prevent_initial_call=False,
)
def sync_selection(count, checkbox_values, checkbox_ids, prev_selected):
    # If no trips or invalid count => empty selection
    if not _TRIPS or not count or count <= 0:
        return []
    count = max(1, min(int(count), len(_TRIPS)))

    # If checkboxes are not in the DOM yet, try to preserve previous selection (session)
    if not checkbox_ids:
        visible = {getattr(t, 'trip_id', None) for t in _TRIPS[:count] if getattr(t, 'trip_id', None)}
        if prev_selected:
            # Keep only those still visible
            return [sid for sid in prev_selected if sid in visible]
        # Fallback: select first 3 trips by default (or all if less than 3)
        default_trips = [getattr(t, 'trip_id', None) for t in _TRIPS[:min(3, count)] if getattr(t, 'trip_id', None)]
        return default_trips

    # If checkboxes exist, compute selection from their values
    selected = []
    checkbox_values = checkbox_values or []
    for v, id_obj in zip(checkbox_values, checkbox_ids):
        try:
            if v and isinstance(id_obj, dict):
                selected.append(id_obj.get("index"))
        except Exception:
            continue
    # Safety: limit to visible last N trips
    visible = {getattr(t, 'trip_id', None) for t in _TRIPS[:count] if getattr(t, 'trip_id', None)}
    return [sid for sid in selected if sid in visible]


# --- Clientside bridge: poll window.__map_events and update Stores ---
dash.clientside_callback(
    ClientsideFunction(namespace="mapbridge", function_name="poll"),
    Output("map-hover-trip-id", "data"),
    Output("map-click-trip-id", "data"),
    Input("map-event-poll", "n_intervals"),
)


@callback(
    Output("map-click-trip-id", "data", allow_duplicate=True),
    Output("map-detail-visible", "data", allow_duplicate=True),
    Input("map-selected-trips", "data"),
    Input("map-trip-count", "value"),
    State("map-click-trip-id", "data"),
    prevent_initial_call=True,
)
def clear_click_when_trip_set_changes(selected_ids, count, current_selected_id):
    # Clear only if the current selected trip is no longer in the visible selection (or none selected)
    selected_ids = selected_ids or []
    if (not selected_ids) or (current_selected_id and current_selected_id not in selected_ids):
        return None, False
    # Otherwise, keep current state
    return dash.no_update, dash.no_update


# Keep a separate visibility flag in session that decides whether to show details
@callback(
    Output("map-detail-visible", "data"),
    Input("map-click-trip-id", "data"),
    prevent_initial_call=False,
)
def update_detail_visibility(selected_trip_id):
    return bool(selected_trip_id)


@callback(
    Output("map-side-panel", "children"),
    Input("map-click-trip-id", "data"),
    Input("map-detail-visible", "data"),
    prevent_initial_call=False,
)
def render_side_panel(selected_trip_id, detail_visible):
    # Fallback texte si rien
    if not detail_visible or not selected_trip_id:
        return html.Div("Sélectionnez un trajet sur la carte")
    # Retrouver le trajet
    trip = next((t for t in _TRIPS if getattr(t, 'trip_id', None) == selected_trip_id), None)
    if not trip:
        return html.Div([html.Strong("Trajet:"), html.Span(f" {selected_trip_id}")])
    # Afficher un résumé compact du conducteur à gauche
    driver_id = getattr(trip, 'driver_id', None)
    if driver_id:
        return render_user_summary(driver_id)
    # Fallback minimal si pas de driver_id
    return html.Div([html.Strong("Trajet:"), html.Span(f" {selected_trip_id}")])
