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
from dash_apps.services.map_trips_cache_service import map_trips_cache
from dash_apps.utils.map_trips_transformer import MapTripsTransformer
import polyline as polyline_lib

# Import dash app instance to check if callbacks already exist
import dash
from dash import callback_context


def _get_last_trips(n=5):
    """Fetch last n trips using MapCacheService with fallback to TripsCacheService.
    Optimized for map page with caching.
    """
    try:
        # Essayer d'abord le cache spécifique à la map
        trips = MapCacheService.get_cached_trips(int(n or 5))
        if trips:
            return trips
        
        # Fallback: TripsCacheService avec tri par date décroissante
        filter_params = {
            "creation_sort": "desc"
        }
        result = TripsCacheService.get_trips_page_result(page_index=0, page_size=int(n or 5), filter_params=filter_params)
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
        _TRIPS = _get_last_trips(5)
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
            cached_count = settings.get('trip_count', 5)
            return str(cached_count)
        except Exception:
            return "5"
    
    try:
        current = int(current_value)
    except Exception:
        current = 5
    
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
    """
    Callback optimisé utilisant MapPolylineRenderer pour le rendu des polylines.
    Configuration externalisée et logique simplifiée.
    """
    import os
    from dash_apps.utils.map_polyline_renderer import map_polyline_renderer
    from dash_apps.infrastructure.repositories.supabase_trip_repository import SupabaseTripRepository
    from dash_apps.utils.callback_logger import CallbackLogger
    
    debug_enabled = os.getenv('DEBUG_MAP', 'False').lower() == 'true'
    logger = CallbackLogger()
    
    if debug_enabled:
        logger.log_callback("map_geojson_start", {
            "count": count,
            "selected_ids_count": len(selected_ids or [])
        }, status="INFO", extra_info="Starting map GeoJSON generation")
    
    # Validation du compteur
    try:
        count = int(count)
    except Exception:
        count = 0
    if not _TRIPS or count <= 0:
        if debug_enabled:
            logger.log_callback("map_geojson_empty", {
                "trips_available": len(_TRIPS) if _TRIPS else 0,
                "count": count
            }, status="WARNING", extra_info="Returning empty GeoJSON - no trips or invalid count")
        return json.dumps({"type": "FeatureCollection", "features": []})
    
    count = max(1, min(int(count), len(_TRIPS)))
    visible_trips = _TRIPS[:count]
    
    if debug_enabled:
        logger.log_callback("map_trips_prepared", {
            "total_trips": len(_TRIPS),
            "visible_trips": count,
            "selected_count": len(selected_ids or [])
        }, status="INFO", extra_info="Trips prepared for rendering")
    
    # Callback pour récupérer les polylines manquantes
    def fetch_missing_polyline(trip_id: str) -> dict:
        try:
            if debug_enabled:
                logger.log_callback("fetch_polyline_start", {
                    "trip_id": str(trip_id)[:8]
                }, status="INFO", extra_info="Fetching missing polyline from Supabase")
            repo = SupabaseTripRepository()
            full_trip = repo.get_trip(trip_id)
            result = full_trip if isinstance(full_trip, dict) else {}
            if debug_enabled:
                logger.log_callback("fetch_polyline_success", {
                    "trip_id": str(trip_id)[:8],
                    "has_data": bool(result),
                    "has_polyline": bool(result.get('polyline'))
                }, status="SUCCESS", extra_info="Polyline fetch completed")
            return result
        except Exception as e:
            if debug_enabled:
                logger.log_callback("fetch_polyline_error", {
                    "trip_id": str(trip_id)[:8],
                    "error": str(e)
                }, status="ERROR", extra_info="Failed to fetch polyline from Supabase")
            return {}
    
    # Utiliser le renderer optimisé
    result = map_polyline_renderer.render_trips_geojson(
        trips=visible_trips,
        selected_trip_ids=selected_ids or [],
        fetch_missing_polyline_callback=fetch_missing_polyline
    )
    
    if debug_enabled:
        logger.log_callback("map_geojson_complete", {
            "result_length": len(result),
            "has_features": '"features":[]' not in result
        }, status="SUCCESS", extra_info="Map GeoJSON generation completed")
    
    return result

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
    prevent_initial_call=True,  # Éviter l'appel initial inutile
)
def update_detail_visibility(selected_trip_id):
    if selected_trip_id:
        print(f"[MAP_CALLBACK] update_detail_visibility called with: {selected_trip_id}")
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
    print(f"[MAP_CALLBACK] render_side_panel called with trip_id: {selected_trip_id}, visible: {detail_visible}")
    
    # Fallback texte si rien
    if not detail_visible or not selected_trip_id:
        return html.Div([
            html.Div([
                html.I(className="fas fa-mouse-pointer me-2"),
                html.Span("Cliquez sur un trajet sur la carte pour voir les détails")
            ], className="text-muted text-center py-5")
        ])
    
    # Utiliser le service de cache des trajets pour récupérer les détails
    try:
        from dash_apps.services.trips_cache_service import TripsCacheService
        print(f"[MAP_CALLBACK] Récupération des détails du trajet via TripsCacheService: {selected_trip_id}")
        
        # Récupérer le panneau de détails du trajet avec toutes les infos du conducteur
        trip_details_panel = TripsCacheService.get_trip_details_panel(selected_trip_id)
        
        if trip_details_panel:
            return html.Div([
                html.H5([
                    html.I(className="fas fa-route me-2"),
                    f"Détails du trajet"
                ], className="mb-3"),
                trip_details_panel
            ])
        else:
            return html.Div([
                html.Div([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    html.Span(f"Trajet {selected_trip_id[:8]}... non trouvé")
                ], className="text-warning text-center py-3")
            ])
            
    except Exception as e:
        print(f"[MAP_CALLBACK] Erreur lors de la récupération des détails: {e}")
        return html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-circle me-2"),
                html.Span(f"Erreur lors du chargement des détails: {str(e)}")
            ], className="text-danger text-center py-3")
        ])




def create_driver_card(driver_id, departure_name, destination_name, departure_datetime, passenger_price):
    """Crée une carte pour afficher les informations du conducteur"""
    if not driver_id:
        return dbc.Card([
            dbc.CardBody([
                html.H6([
                    html.I(className="fas fa-user-slash me-2"),
                    "Conducteur"
                ], className="card-title"),
                html.P("Informations non disponibles", className="text-muted mb-0")
            ])
        ], className="mb-3")
    
    # Récupérer les informations du conducteur via render_user_summary
    try:
        driver_info = render_user_summary(driver_id)
        return dbc.Card([
            dbc.CardBody([
                html.H6([
                    html.I(className="fas fa-user-tie me-2"),
                    "Conducteur"
                ], className="card-title mb-3"),
                driver_info
            ])
        ], className="mb-3")
    except Exception:
        return dbc.Card([
            dbc.CardBody([
                html.H6([
                    html.I(className="fas fa-user-tie me-2"),
                    "Conducteur"
                ], className="card-title"),
                html.P(f"ID: {driver_id}", className="mb-0")
            ])
        ], className="mb-3")


def create_passengers_card(trip_id, seats_booked, seats_available):
    """Crée une carte pour afficher les informations des passagers"""
    return dbc.Card([
        dbc.CardBody([
            html.H6([
                html.I(className="fas fa-users me-2"),
                "Passagers"
            ], className="card-title mb-3"),
            html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H4(str(seats_booked), className="text-primary mb-0"),
                            html.Small("Réservées", className="text-muted")
                        ], className="text-center")
                    ], width=6),
                    dbc.Col([
                        html.Div([
                            html.H4(str(seats_available), className="text-success mb-0"),
                            html.Small("Disponibles", className="text-muted")
                        ], className="text-center")
                    ], width=6)
                ])
            ]),
            html.Hr(),
            html.Div([
                html.Small([
                    html.I(className="fas fa-info-circle me-1"),
                    f"Total: {seats_booked + seats_available} places"
                ], className="text-muted")
            ])
        ])
    ], className="mb-3")


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
