"""
Callbacks pour la page Map
"""

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

# Flag to prevent multiple callback registrations
_CALLBACKS_REGISTERED = False

# Import dash app instance to check if callbacks already exist
import dash
from dash import callback_context


def _get_last_trips(n=10):
    # Fetch last n trips using REST repository
    try:
        trip_repository = RepositoryFactory.get_trip_repository()
        trips = trip_repository.list_trips(limit=n)
        return trips
    except Exception as e:
        print(f"Warning: Could not load trips data: {e}")
        return []


def _trip_to_option(trip):
    try:
        # Handle both dict and object formats
        if isinstance(trip, dict):
            departure = trip.get('departure_name', '-') or '-'
            destination = trip.get('destination_name', '-') or '-'
            trip_id = trip.get('trip_id', 'N/A')
        else:
            departure = getattr(trip, 'departure_name', '-') or '-'
            destination = getattr(trip, 'destination_name', '-') or '-'
            trip_id = getattr(trip, 'trip_id', 'N/A')
        
        label = f"{departure} → {destination}"
        return {"label": label, "value": trip_id}
    except Exception:
        trip_id = trip.get('trip_id', 'N/A') if isinstance(trip, dict) else getattr(trip, 'trip_id', 'N/A')
        return {"label": str(trip_id), "value": trip_id}


# Initialize trips data
_TRIPS = []
_OPTIONS = []

def _initialize_trips_data():
    """Initialize trips data when module loads"""
    global _TRIPS, _OPTIONS
    try:
        _TRIPS = _get_last_trips(10)
        _OPTIONS = [_trip_to_option(t) for t in _TRIPS]
        print(f"[MAP_CALLBACKS] Initialized {len(_TRIPS)} trips for map page")
    except Exception as e:
        print(f"[MAP_CALLBACKS] Warning: Could not initialize trips data: {e}")
        _TRIPS = []
        _OPTIONS = []

# Initialize data when module loads
_initialize_trips_data()


# Keep the selected trip id in a DOM attribute so MapLibre JS can re-apply highlight after reload
@callback(
    Output("home-maplibre", "data-selected-trip-id"),
    Input("map-click-trip-id", "data"),
    prevent_initial_call=False,
)
def expose_selected_trip_to_dom(selected_trip_id):
    return selected_trip_id or ""


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
    # Handle both dict and object formats for filtering
    filtered = []
    for t in visible_trips:
        if isinstance(t, dict):
            trip_id = t.get('trip_id', None)
        else:
            trip_id = getattr(t, 'trip_id', None)
        if trip_id in selected_set:
            filtered.append(t)
    for idx, trip in enumerate(filtered):
        # Handle both dict and object formats
        if isinstance(trip, dict):
            p = trip.get('polyline', None)
            trip_id = trip.get('trip_id', None)
            driver_id = trip.get('driver_id', None)
            driver_name = trip.get('driver_name', None)
            seats_booked = trip.get('seats_booked', None)
            seats_available = trip.get('seats_available', None)
            passenger_price = trip.get('passenger_price', None)
            distance = trip.get('distance', None)
            departure_name = trip.get('departure_name', None)
            destination_name = trip.get('destination_name', None)
            departure_schedule = str(trip.get('departure_schedule', '') or '')
        else:
            p = getattr(trip, 'polyline', None)
            trip_id = getattr(trip, 'trip_id', None)
            driver_id = getattr(trip, 'driver_id', None)
            driver_name = getattr(trip, 'driver_name', None) if hasattr(trip, 'driver_name') else None
            seats_booked = getattr(trip, 'seats_booked', None)
            seats_available = getattr(trip, 'seats_available', None)
            passenger_price = getattr(trip, 'passenger_price', None)
            distance = getattr(trip, 'distance', None)
            departure_name = getattr(trip, 'departure_name', None)
            destination_name = getattr(trip, 'destination_name', None)
            departure_schedule = str(getattr(trip, 'departure_schedule', '') or '')
        
        if not p:
            continue
        try:
            if isinstance(p, bytes):
                p = p.decode('utf-8')
            coords_latlon = polyline_lib.decode(p)  # [(lat, lon), ...]
            coords_lonlat = [[lon, lat] for (lat, lon) in coords_latlon]
            # propriétés enrichies pour interactions
            props = {
                "trip_id": trip_id,
                "color": palette[idx % len(palette)],
                "driver_id": driver_id,
                "driver_name": driver_name,
                "seats_booked": seats_booked,
                "seats_available": seats_available,
                "passenger_price": passenger_price,
                "distance": distance,
                "departure_name": departure_name,
                "destination_name": destination_name,
                "departure_schedule": departure_schedule,
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
        visible = {getattr(t, 'trip_id', None) if not isinstance(t, dict) else t.get('trip_id', None) for t in _TRIPS[:count]}
        if prev_selected:
            # Keep only those still visible
            return [sid for sid in prev_selected if sid in visible]
        # Fallback: select first 3 trips by default (or all if less than 3)
        default_trips = []
        for t in _TRIPS[:min(3, count)]:
            if isinstance(t, dict):
                trip_id = t.get('trip_id', None)
            else:
                trip_id = getattr(t, 'trip_id', None)
            if trip_id:
                default_trips.append(trip_id)
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
    visible = set()
    for t in _TRIPS[:count]:
        if isinstance(t, dict):
            trip_id = t.get('trip_id', None)
        else:
            trip_id = getattr(t, 'trip_id', None)
        if trip_id:
            visible.add(trip_id)
    return [sid for sid in selected if sid in visible]


# --- Clientside bridge: poll window.__map_events and update Stores ---
dash.clientside_callback(
    ClientsideFunction(namespace="mapbridge", function_name="poll"),
    Output("map-hover-trip-id", "data"),
    Output("map-click-trip-id", "data"),
    Input("map-event-poll", "n_intervals"),
    prevent_initial_call=True,
)


# Note: Removed clear_click_when_trip_set_changes callback to avoid conflict with clientside callback
# The clientside callback handles map-click-trip-id updates from MapLibre events


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
    trip = None
    for t in _TRIPS:
        if isinstance(t, dict):
            if t.get('trip_id', None) == selected_trip_id:
                trip = t
                break
        else:
            if getattr(t, 'trip_id', None) == selected_trip_id:
                trip = t
                break
    
    if not trip:
        return html.Div([html.Strong("Trajet:"), html.Span(f" {selected_trip_id}")])
    
    # Afficher un résumé compact du conducteur à gauche
    if isinstance(trip, dict):
        driver_id = trip.get('driver_id', None)
    else:
        driver_id = getattr(trip, 'driver_id', None)
    
    if driver_id:
        return render_user_summary(driver_id)
    # Fallback minimal si pas de driver_id
    return html.Div([html.Strong("Trajet:"), html.Span(f" {selected_trip_id}")])


print("[MAP_CALLBACKS] Callbacks de la page Map enregistrés")
