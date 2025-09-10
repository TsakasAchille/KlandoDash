import math
import json
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from dash_apps.config import Config
# Import du nouveau composant personnalisé à la place du DataTable
from dash_apps.components.trips_table_custom import render_custom_trips_table
from dash_apps.components.trip_search_widget import render_trip_search_widget, render_active_trip_filters
from dash_apps.repositories.repository_factory import RepositoryFactory
from dash_apps.services.redis_cache import redis_cache
from dash_apps.services.trips_cache_service import TripsCacheService

# L'enregistrement se fera dans app_factory après la création de l'app

# Utiliser la factory pour obtenir le repository approprié
trip_repository = RepositoryFactory.get_trip_repository()


# Helper de log standardisé pour tous les callbacks (compatible Python < 3.10)
def log_callback(name, inputs, states=None):
    def _short_str(s):
        try:
            s = str(s)
        except Exception:
            return s
        if len(s) > 14:
            return f"{s[:4]}…{s[-4:]}"
        return s

    def _clean(value):
        # Nettoyage récursif: supprime None, "", et valeurs par défaut "all"
        if isinstance(value, dict):
            cleaned = {}
            for k, v in value.items():
                if v is None or v == "":
                    continue
                if isinstance(v, str) and v == "all":
                    continue
                # Flatten pour selected_trip
                if k in ("selected_trip", "selected_trip_id") and isinstance(v, dict) and "trip_id" in v:
                    cleaned["selected_trip_id"] = _short_str(v.get("trip_id"))
                    continue
                cleaned[k] = _clean(v)
            return cleaned
        if isinstance(value, list):
            return [_clean(v) for v in value if v is not None and v != ""]
        if isinstance(value, str):
            return _short_str(value)
        return value

    def _kv_lines(dct):
        if not dct:
            return ["  (none)"]
        lines = []
        for k, v in dct.items():
            try:
                if isinstance(v, (dict, list)):
                    v_str = json.dumps(v, ensure_ascii=False)
                else:
                    v_str = str(v)
            except Exception:
                v_str = str(v)
            lines.append(f"  - {k}: {v_str}")
        return lines

    try:
        c_inputs = _clean(inputs)
        c_states = _clean(states or {})
        sep = "=" * 74
        print("\n" + sep)
        print(f"[CB] {name}")
        print("Inputs:")
        for line in _kv_lines(c_inputs):
            print(line)
        print("States:")
        for line in _kv_lines(c_states):
            print(line)
        print(sep)
    except Exception:
        sep = "=" * 74
        print("\n" + sep)
        print(f"[CB] {name}")
        print(f"Inputs: {inputs}")
        print(f"States: {states or {}}")
        print(sep)


def find_trip_page_index_from_cache(trip_id, page_size, filter_params=None):
    """Trouve l'index de page en parcourant le cache existant (évite l'appel DB)
    
    Args:
        trip_id: ID du trajet à trouver
        page_size: Taille de chaque page
        filter_params: Paramètres de filtrage actuels
        
    Returns:
        Index de la page (0-based) ou None si non trouvé
    """
    try:
        # Parcourir les pages en cache pour trouver le trajet
        max_pages_to_check = 10  # Limiter la recherche pour éviter la lenteur
        
        for page_index in range(max_pages_to_check):
            cache_key = redis_cache.make_trips_page_key(page_index, page_size, filter_params or {})
            
            # Vérifier d'abord le cache local
            if cache_key in TripsCacheService._local_cache:
                cached_data = TripsCacheService._local_cache[cache_key]
                trips = cached_data.get("trips", [])
                
                # Chercher le trajet dans cette page
                for trip in trips:
                    trip_id_in_cache = trip.get("trip_id") if isinstance(trip, dict) else getattr(trip, "trip_id", None)
                    if str(trip_id_in_cache) == str(trip_id):
                        print(f"[CACHE_SEARCH] Trajet {trip_id} trouvé en page {page_index} (cache local)")
                        return page_index
            
            # Vérifier le cache Redis si pas trouvé en local
            cached_data = redis_cache.get_json_by_key(cache_key)
            if cached_data:
                trips = cached_data.get("trips", [])
                for trip in trips:
                    trip_id_in_cache = trip.get("trip_id") if isinstance(trip, dict) else getattr(trip, "trip_id", None)
                    if str(trip_id_in_cache) == str(trip_id):
                        print(f"[CACHE_SEARCH] Trajet {trip_id} trouvé en page {page_index} (cache Redis)")
                        return page_index
        
        print(f"[CACHE_SEARCH] Trajet {trip_id} non trouvé dans les {max_pages_to_check} premières pages en cache")
        return None
    except Exception as e:
        print(f"[CACHE_SEARCH] Erreur lors de la recherche: {str(e)}")
        return None



def get_layout():
    """Génère le layout de la page trajets avec des IDs uniquement pour cette page"""
    return dbc.Container([
    dcc.Location(id="trips-url", refresh=False),
    dcc.Store(id="trips-current-page", storage_type="session", data=1),  # State pour stocker la page courante (persistant)
    dcc.Store(id="selected-trip-id", storage_type="session", data=None, clear_data=False),  # Store pour l'ID du trajet sélectionné (persistant)
    dcc.Store(id="url-trip-parameters", storage_type="memory", data=None),  # Store temporaire pour les paramètres d'URL
    dcc.Store(id="selected-trip-from-url", storage_type="memory", data=None),  # State pour la sélection depuis l'URL
    dcc.Store(id="trips-filter-store", storage_type="session", data={}, clear_data=False),  # Store pour les filtres de recherche
    # Interval pour déclencher la lecture des paramètres d'URL au chargement initial (astuce pour garantir l'exécution)
    dcc.Interval(id='trips-url-init-trigger', interval=100, max_intervals=1),  # Exécute une seule fois au chargement
  
    html.H2("Dashboard trajets", style={"marginTop": "20px"}),
    dbc.Row([
        dbc.Col([], width=9),
        dbc.Col([
            dbc.Button("🔄 Rafraîchir les données", id="refresh-trips-btn", color="primary", className="mb-2")
        ], width=3)
    ]),
    html.Div(id="refresh-trips-message"),
    # Widget de recherche
    render_trip_search_widget(),
    # Affichage des filtres actifs
    html.Div(id="trips-active-filters"),
    dbc.Row([
        dbc.Col([
            # Conteneur vide qui sera rempli par le callback render_trips_table_callback
            html.Div(id="main-trips-content")
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                children=html.Div(id="trip-details-panel"),
                type="default"
            )
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                children=html.Div(id="trip-passengers-panel"),
                type="default"
            )
        ], width=12)
    ])
], fluid=True)



# Note: Le store trips-page-store n'est plus utilisé pour stocker tous les trajets
# car nous utilisons maintenant un chargement à la demande page par page

# Les callbacks sont maintenant dans callbacks/trips_callbacks.py
from dash_apps.callbacks import trips_callbacks


# Exporter le layout pour l'application principale
layout = get_layout()
