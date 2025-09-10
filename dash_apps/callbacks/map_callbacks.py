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
from dash_apps.services.trips_cache_service import TripsCacheService
from dash_apps.services.map_cache_service import MapCacheService
import polyline as polyline_lib

# Import dash app instance to check if callbacks already exist
import dash
from dash import callback_context


def _get_last_trips(n=10):
    """Fetch last n trips using MapCacheService with fallback to TripsCacheService.
    Optimized for map page with caching.
    """
    try:
        # Essayer d'abord le cache spécifique à la map
        trips = MapCacheService.get_cached_trips(int(n or 10))
        if trips:
            return trips
        
        # Fallback: TripsCacheService
        result = TripsCacheService.get_trips_page_result(page_index=0, page_size=int(n or 10), filter_params={})
        trips = result.get("trips", [])
        return trips if isinstance(trips, list) else []
    except Exception as e:
        print(f"[MAP_CALLBACKS] Cache fetch failed, fallback to direct repo: {e}")
        try:
            trip_repository = RepositoryFactory.get_trip_repository()
            trips = trip_repository.list_trips(limit=n)
            return trips
        except Exception as e2:
            print(f"[MAP_CALLBACKS] Warning: Could not load trips data: {e2}")
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
    prevent_initial_call=False,  # Permettre l'appel initial pour charger depuis le cache
)
def update_trip_count(inc_clicks, dec_clicks, current_value):
    ctx = callback_context
    
    # Si pas de déclencheur (appel initial), charger depuis le cache
    if not ctx.triggered:
        try:
            settings = MapCacheService.load_map_settings()
            cached_count = settings.get('trip_count', 10)
            return str(cached_count)
        except Exception:
            return "10"
    
    try:
        current = int(current_value)
    except Exception:
        current = 10
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "map-trip-inc":
        new_value = min(current + 1, len(_TRIPS) if _TRIPS else 50)  # Max 50 si pas de trips
    elif button_id == "map-trip-dec":
        new_value = max(current - 1, 1)
    else:
        new_value = current
    
    # Sauvegarder le nouveau count dans le cache
    MapCacheService.save_map_settings(new_value)
    
    return str(new_value)


@callback(
    Output("home-maplibre", "data-geojson"),
    Input("map-trip-count", "value"),
    Input("map-selected-trips", "data"),
)
def update_map_geojson(count, selected_ids):
    # Coercion robuste du compteur
    try:
        count = int(count)
    except Exception:
        count = 0
    if not _TRIPS or count <= 0:
        return None
    count = max(1, min(int(count), len(_TRIPS)))
    # If there is a selection, use it; else default to last N trips
    visible_trips = _TRIPS[:count]
    # If nothing is selected, show none (do not default to all)
    # Normalize selected IDs to strings for robust comparison
    selected_set = {str(s) for s in (selected_ids or [])}
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
        if trip_id is None:
            continue
        if str(trip_id) in selected_set:
            filtered.append(t)
    for idx, trip in enumerate(filtered):
        # Handle both dict and object formats and ensure polyline is available
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

        # If polyline is missing, fetch full trip details on-demand
        if not p and trip_id:
            try:
                repo = RepositoryFactory.get_trip_repository()
                full = repo.get_trip(trip_id)
                if isinstance(full, dict):
                    p = full.get('polyline') or p
                    driver_id = full.get('driver_id', driver_id)
                    driver_name = full.get('driver_name', driver_name)
                    seats_booked = full.get('seats_booked', seats_booked)
                    seats_available = full.get('seats_available', seats_available)
                    passenger_price = full.get('passenger_price', passenger_price)
                    distance = full.get('distance', distance)
                    departure_name = full.get('departure_name', departure_name)
                    destination_name = full.get('destination_name', destination_name)
                    departure_schedule = str(full.get('departure_schedule', departure_schedule) or '')
            except Exception as _e:
                # Silent fallback: if we can't fetch details, skip this trip
                pass
        
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
    try:
        count = int(count)
    except Exception:
        count = 0
    if not _TRIPS or count <= 0:
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
    prevent_initial_call=True,  # Évite le déclenchement initial inutile
)
def sync_selection(count, checkbox_values, checkbox_ids, prev_selected):
    # If no trips or invalid count => empty selection
    try:
        count = int(count)
    except Exception:
        count = 0
    if not _TRIPS or count <= 0:
        return []
    count = max(1, min(int(count), len(_TRIPS)))

    # If checkboxes are not in the DOM yet, try to load from cache first
    if not checkbox_ids:
        visible = {getattr(t, 'trip_id', None) if not isinstance(t, dict) else t.get('trip_id', None) for t in _TRIPS[:count]}
        
        # Essayer de charger les sélections depuis le cache
        cached_selections = MapCacheService.load_selected_trips()
        if cached_selections:
            # Garder seulement celles qui sont encore visibles
            valid_cached = [sid for sid in cached_selections if sid in visible]
            if valid_cached:
                return valid_cached
        
        # Fallback: utiliser prev_selected ou sélection par défaut
        if prev_selected:
            return [sid for sid in prev_selected if sid in visible]
        return list(visible)[:3]

    # Extract trip IDs from checkbox IDs
    trip_ids = [cb_id["index"] for cb_id in checkbox_ids]
    
    # Determine which checkboxes are checked
    selected_trip_ids = []
    for i, is_checked in enumerate(checkbox_values or []):
        if is_checked and i < len(trip_ids):
            selected_trip_ids.append(trip_ids[i])
    
    # Sauvegarder les sélections dans le cache pour persistance
    MapCacheService.save_selected_trips(selected_trip_ids)
    
    return selected_trip_ids


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
    if not selected_trip_id:
        return False
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


def register_callbacks():
    """Force l'enregistrement des callbacks si nécessaire"""
    try:
        # Vérifier si l'app Dash existe
        from dash import get_app
        app = get_app()
        print(f"[MAP_CALLBACKS] App trouvée avec {len(app.callback_map)} callbacks enregistrés")
        
        # Vérifier si nos callbacks sont présents
        required_outputs = [
            'map-trips-table-container.children',
            'map-selected-trips.data', 
            'map-detail-visible.data',
            'map-side-panel.children',
            'home-maplibre.data-geojson'
        ]
        
        missing = [output for output in required_outputs if output not in app.callback_map]
        if missing:
            print(f"[MAP_CALLBACKS] ATTENTION: Callbacks manquants: {missing}")
        else:
            print("[MAP_CALLBACKS] Tous les callbacks requis sont enregistrés")
            
    except Exception as e:
        print(f"[MAP_CALLBACKS] Erreur vérification callbacks: {e}")

# Enregistrer immédiatement si possible, sinon attendre
try:
    register_callbacks()
except Exception:
    print("[MAP_CALLBACKS] Callbacks seront vérifiés plus tard")

print("[MAP_CALLBACKS] Module callbacks map chargé")
