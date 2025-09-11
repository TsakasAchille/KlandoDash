import math
import json
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from dash_apps.config import Config
from dash_apps.components.trips_table_custom import render_custom_trips_table
from dash_apps.components.trip_search_widget import render_trip_search_widget, render_active_trip_filters
from dash_apps.repositories.repository_factory import RepositoryFactory
from dash_apps.services.redis_cache import redis_cache
from dash_apps.services.trips_cache_service import TripsCacheService

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


@callback(
    Output("trips-current-page", "data"),
    Output("selected-trip-id", "data", allow_duplicate=True),
    Output("trips-filter-store", "data", allow_duplicate=True),
    Input("refresh-trips-btn", "n_clicks"),
    Input("trips-url", "search"),  # Ajout de l'URL comme input
    State("trips-current-page", "data"),
    State("selected-trip-id", "data"),
    State("trips-filter-store", "data"),
    prevent_initial_call=True
)
def get_page_info_on_page_load(n_clicks, url_search, current_page, selected_trip, current_filters):
    log_callback(
        "get_page_info_on_page_load",
        {"n_clicks": n_clicks, "url_search": url_search},
        {"current_page": current_page, "selected_trip": selected_trip, "current_filters": current_filters}
    )
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Si l'URL a changé, traiter la sélection de trajet
    if triggered_id == "trips-url" and url_search:
        import urllib.parse
        params = urllib.parse.parse_qs(url_search.lstrip('?'))
        trip_id_list = params.get('trip_id')
        
        if trip_id_list:
            selected_trip_id = trip_id_list[0]
            trip_from_url = {"trip_id": selected_trip_id}
            
            # Appliquer automatiquement un filtre de recherche sur le trip_id
            # Cela affichera uniquement ce trajet et il sera sélectionné automatiquement
            filter_with_trip_id = {
                "text": selected_trip_id  # Utiliser le trip_id comme filtre de recherche
            }
            
            print(f"[URL_SELECTION] Application du filtre pour le trajet: {selected_trip_id}")
            return 1, trip_from_url, filter_with_trip_id
    # Si refresh a été cliqué
    if triggered_id == "refresh-trips-btn" and n_clicks is not None:
        return 1, selected_trip, current_filters
    
    # Pour le chargement initial ou autres cas
    if current_page is None or not isinstance(current_page, (int, float)):
        return 1, selected_trip, current_filters
        
    return current_page, selected_trip, current_filters


@callback(
    Output("refresh-trips-message", "children"),
    Input("refresh-trips-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_refresh_trips_message(n_clicks):
    log_callback("show_refresh_trips_message", {"n_clicks": n_clicks}, {})
    return dbc.Alert("Données des trajets rafraîchies!", 
                     color="success", 
                     dismissable=True,
                     duration=4000)


@callback(
    Output("trips-advanced-filters-collapse", "is_open"),
    [Input("trips-advanced-filters-btn", "n_clicks")],
    [State("trips-advanced-filters-collapse", "is_open")]
)
def toggle_trip_filters_collapse(n_clicks, is_open):
    """Toggle l'affichage des filtres avancés pour les trajets"""
    log_callback("toggle_trip_filters_collapse", {"n_clicks": n_clicks}, {"is_open": is_open})
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output("trips-filter-store", "data", allow_duplicate=True),
    Input("trips-apply-filters-btn", "n_clicks"),
    [State("trips-search-input", "value"),
     State("trips-creation-date-filter", "start_date"),
     State("trips-creation-date-filter", "end_date"),
     State("trips-single-date-filter", "date"),
     State("trips-date-filter-type", "value"),
     State("trips-date-sort-filter", "value"),
     State("trips-status-filter", "value"),
     State("trips-has-signalement-filter", "value"),
     State("trips-filter-store", "data")],
    prevent_initial_call=True
)
def update_trip_filters(n_clicks, search_text, date_from, date_to, single_date, date_filter_type, 
                       date_sort, status, has_signalement, current_filters):
    """Met à jour les filtres de recherche des trajets"""
    log_callback(
        "update_trip_filters",
        {
            "n_clicks": n_clicks,
            "search_text": search_text,
            "date_from": date_from,
            "date_to": date_to,
            "single_date": single_date,
            "date_filter_type": date_filter_type,
            "date_sort": date_sort,
            "status": status,
            "has_signalement": has_signalement
        },
        {"current_filters": current_filters}
    )
    
    # Construction du dictionnaire de filtres
    filters = {
        "text": search_text or "",
        "date_from": date_from,
        "date_to": date_to,
        "single_date": single_date,
        "date_filter_type": date_filter_type or "range",
        "date_sort": date_sort or "desc",
        "status": status or "all",
        "has_signalement": bool(has_signalement)
    }
    
    # Ne déclencher une mise à jour que si les filtres ont vraiment changé
    if filters != current_filters:
        return filters
    
    raise PreventUpdate


@callback(
    Output("trips-current-page", "data", allow_duplicate=True),
    Input("trips-filter-store", "data"),
    prevent_initial_call=True
)
def reset_trip_page_on_filter_change(filters):
    """Réinitialise la page à 1 lorsque les filtres changent"""
    log_callback("reset_trip_page_on_filter_change", {"filters": filters}, {})
    # Toujours revenir à la page 1 quand un filtre change
    return 1


@callback(
    [
        Output("trips-filter-store", "data", allow_duplicate=True),
        Output("trips-search-input", "value"),
        Output("trips-creation-date-filter", "start_date"),
        Output("trips-creation-date-filter", "end_date"),
        Output("trips-single-date-filter", "date"),
        Output("trips-date-filter-type", "value"),
        Output("trips-date-sort-filter", "value"),
        Output("trips-status-filter", "value"),
        Output("trips-has-signalement-filter", "value"),
    ],
    Input("trips-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_trip_filters(n_clicks):
    """Réinitialise tous les filtres et vide la barre de recherche"""
    log_callback("reset_trip_filters", {"n_clicks": n_clicks}, {})
    # Valeurs par défaut
    return (
        {},              # trips-filter-store
        "",             # search input
        None,            # date range start
        None,            # date range end
        None,            # single date
        "range",        # date filter type
        "desc",         # date sort
        "all",          # status
        False,           # has signalement
    )


@callback(
    Output("trips-active-filters", "children"),
    Input("trips-filter-store", "data"),
)
def display_active_trip_filters(filters):
    """Affiche les filtres actifs sous forme de badges"""
    log_callback("display_active_trip_filters", {"filters": filters}, {})
    return render_active_trip_filters(filters)


@callback(
    Output("main-trips-content", "children"),
    [Input("trips-current-page", "data"),
     Input("trips-filter-store", "data"),
     Input("refresh-trips-btn", "n_clicks"),
     Input("selected-trip-id", "data")],  # Ajout pour restaurer la sélection
    prevent_initial_call=False
)
def render_trips_table(current_page, filters, refresh_clicks, selected_trip):
    """Callback pour le rendu du tableau des trajets avec persistance de sélection"""
    log_callback(
        "render_trips_table",
        {"current_page": current_page, "refresh_clicks": refresh_clicks, "filters": filters, "selected_trip": selected_trip}
    )
    
    # Configuration pagination
    page_size = Config.USERS_TABLE_PAGE_SIZE
    
    # Si la page n'est pas spécifiée, utiliser la page 1 par défaut
    if not isinstance(current_page, (int, float)):
        current_page = 1  # Défaut à 1 (pagination commence à 1)
    
    # Convertir la page en index 0-based pour l'API
    page_index = current_page - 1 if current_page > 0 else 0
    
    # Préparer les filtres pour le repository (optimisé)
    filter_params = {}
    if filters:
        # Copier tous les filtres valides en une seule passe
        valid_keys = ["text", "date_from", "date_to", "date_filter_type", "single_date", "date_sort", "has_signalement"]
        filter_params.update({k: v for k, v in filters.items() if k in valid_keys and v})
        
        # Traitement spécial pour le statut (exclure "all")
        if filters.get("status") and filters["status"] != "all":
            filter_params["status"] = filters["status"]

    # Déterminer si on force le rechargement (bouton refresh)
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    force_reload = (triggered_id == "refresh-trips-btn" and refresh_clicks is not None)

    # Utiliser le service de cache centralisé
    print(f"[TABLE] Chargement page {current_page} (index {page_index}), force_reload={force_reload}")
    
    result = TripsCacheService.get_trips_page_result(
        page_index, page_size, filter_params, force_reload
    )
    
    # Utiliser directement les données optimisées du repository
    trips = result.get("trips", [])
    total_trips = result.get("total_count", 0)
    print(f"[TABLE] {len(trips)} trajets chargés, total_count={total_trips}")

    # Auto-sélection du premier trajet si aucun n'est sélectionné
   
    # Calculer le nombre de pages
    page_count = math.ceil(total_trips / page_size) if total_trips > 0 else 1
    
    # Validation stricte de la page courante
    if current_page > page_count and page_count > 0:
        print(f"[PAGINATION] Page {current_page} invalide, redirection vers page {page_count}")
        current_page = page_count
    elif current_page < 1:
        print(f"[PAGINATION] Page {current_page} invalide, redirection vers page 1")
        current_page = 1
    
    # Si on arrive sur une page vide (pas de trajets), revenir à la page précédente
    # Cette logique est maintenant gérée par la validation de pagination ci-dessus
    # Rendu de la table avec les données pré-calculées
    table_component = render_custom_trips_table(
        trips, 
        current_page=current_page,
        total_trips=total_trips,
        selected_trip_id=selected_trip  # Passer la sélection depuis le store
    )

    # Message informatif
    if total_trips == 0:
        message = dbc.Alert("Aucun trajet trouvé avec les critères de recherche actuels.", color="info")
        return [message, table_component]
    else:
        page_count = math.ceil(total_trips / page_size) if total_trips > 0 else 1
        info_message = html.P(
            f"Affichage de {len(trips)} trajets sur {total_trips} au total (page {current_page}/{page_count})",
            className="text-muted small mb-3"
        )
        return [info_message, table_component]


@callback(
    Output("trip-details-panel", "children"),
    Input("selected-trip-id", "data"),
    prevent_initial_call=True
)
def render_trip_details_panel(selected_trip):
    """Callback séparé pour le rendu du panneau détails trajet avec cache HTML"""
    log_callback(
        "render_trip_details_panel",
        {"selected_trip": selected_trip},
        {}
    )
    
    # Panneau vide par défaut
    details_panel = html.Div()
    
    # Extraire l'ID si c'est un dict
    trip_id_value = None
    if selected_trip:
        if isinstance(selected_trip, dict):
            trip_id_value = getattr(selected_trip, "trip_id", None) if hasattr(selected_trip, "trip_id") else selected_trip.get("trip_id")
        else:
            trip_id_value = selected_trip
    
    # Si pas d'ID, retourner un panneau vide
    if not trip_id_value:
        return details_panel

    # Read-Through pattern: le cache service gère tout
   
    return TripsCacheService.get_trip_details_panel(trip_id_value)


@callback(
    Output("trip-passengers-panel", "children"),
    [Input("selected-trip-id", "data")],
    prevent_initial_call=True
)
def render_trip_passengers_panel(selected_trip):
    """Callback séparé pour le rendu du panneau passagers trajet avec cache HTML"""
    log_callback(
        "render_trip_passengers_panel",
        {"selected_trip": selected_trip},
        {}
    )
    
    # Extraire l'ID si c'est un dict
    trip_id_value = None
    if selected_trip:
        if isinstance(selected_trip, dict):
            trip_id_value = getattr(selected_trip, "trip_id", None) if hasattr(selected_trip, "trip_id") else selected_trip.get("trip_id")
        else:
            trip_id_value = selected_trip
    
    # Read-Through pattern: le cache service gère tout
    return TripsCacheService.get_trip_passengers_panel(trip_id_value)
