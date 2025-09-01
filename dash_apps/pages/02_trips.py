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
from dash_apps.components.trip_details_layout import create_trip_details_layout
from dash_apps.components.trip_search_widget import render_trip_search_widget, render_active_trip_filters
from dash_apps.repositories.trip_repository import TripRepository
from dash_apps.services.redis_cache import redis_cache
from dash_apps.services.trips_cache_service import TripsCacheService


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


def find_trip_page_index(trip_id, page_size):
    """Trouve l'index de page sur lequel se trouve le trajet avec l'ID donné
    
    Args:
        trip_id: ID du trajet à trouver
        page_size: Taille de chaque page
        
    Returns:
        Index de la page (0-based) ou None si non trouvé
    """
    try:
        # Utiliser la méthode optimisée du repository pour trouver la position du trajet
        position = TripRepository.get_trip_position(trip_id)
        
        if position is not None:
            # Calculer l'index de page (0-based)
            page_index = position // page_size
            # Ajouter des logs détaillés
            print(f"Trajet {trip_id} trouvé à la position {position} (selon le repository)")
            print(f"Taille de page: {page_size}")
            print(f"Calcul page: {position} // {page_size} = {page_index}")
            print(f"Page calculée (0-based): {page_index}, (1-based): {page_index + 1}")
            return page_index
        
        print(f"Trajet {trip_id} non trouvé dans le repository")
        return None
    except Exception as e:
        print(f"Erreur lors de la recherche de page pour le trajet {trip_id}: {str(e)}")
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
        ], width=6),
        dbc.Col([
            dcc.Loading(
                children=html.Div(id="trip-stats-panel"),
                type="default"
            )
        ], width=6)
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

@callback(
    Output("trips-current-page", "data"),
    Output("selected-trip-id", "data", allow_duplicate=True),
    Input("refresh-trips-btn", "n_clicks"),
    Input("trips-url", "search"),  # Ajout de l'URL comme input
    State("trips-current-page", "data"),
    State("selected-trip-id", "data"),
    prevent_initial_call=True
)
def get_page_info_on_page_load(n_clicks, url_search, current_page, selected_trip):
    log_callback(
        "get_page_info_on_page_load",
        {"n_clicks": n_clicks, "url_search": url_search},
        {"current_page": current_page, "selected_trip": selected_trip}
    )
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Si l'URL a changé, traiter la sélection de trajet
    if triggered_id == "trips-url" and url_search:
        import urllib.parse
        params = urllib.parse.parse_qs(url_search.lstrip('?'))
        trip_id_list = params.get('trip_id')
        
        if trip_id_list:
            trip_from_url = {"trip_id": trip_id_list[0]}
            # On va chercher sur quelle page se trouve le trajet
            trip_id = trip_id_list[0]
            page_index = find_trip_page_index(trip_id, Config.USERS_TABLE_PAGE_SIZE)
            if page_index is not None:
                # Convertir en 1-indexed pour l'interface
                new_page = page_index + 1
                return new_page, trip_from_url
            else:
                return current_page, trip_from_url
    # Si refresh a été cliqué
    if triggered_id == "refresh-trips-btn" and n_clicks is not None:
        return 1, selected_trip
    
    # Pour le chargement initial ou autres cas
    if current_page is None or not isinstance(current_page, (int, float)):
        return 1, selected_trip
        
    return current_page, selected_trip

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
    [Input("trips-search-input", "value"),
     Input("trips-creation-date-filter", "start_date"),
     Input("trips-creation-date-filter", "end_date"),
     Input("trips-single-date-filter", "date"),
     Input("trips-date-filter-type", "value"),
     Input("trips-date-sort-filter", "value"),
     Input("trips-status-filter", "value"),
     Input("trips-has-signalement-filter", "value")],
    [State("trips-filter-store", "data")],
    prevent_initial_call=True
)
def update_trip_filters(search_text, date_from, date_to, single_date, date_filter_type, 
                       date_sort, status, has_signalement, current_filters):
    """Met à jour les filtres de recherche des trajets"""
    log_callback(
        "update_trip_filters",
        {
            "search_text": search_text,
            "date_from": date_from,
            "date_to": date_to,
            "single_date": single_date,
            "date_filter_type": date_filter_type,
            "date_sort": date_sort,
            "status": status,
            "has_signalement": has_signalement,
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
    Output("selected-trip-id", "data", allow_duplicate=True),
    [Input("trips-current-page", "data"),
     Input("trips-filter-store", "data"),
     Input("refresh-trips-btn", "n_clicks")],
    [State("selected-trip-id", "data")],
    prevent_initial_call=True
)
def render_trips_table(current_page, filters, refresh_clicks, selected_trip):
    """Callback pour le rendu du tableau des trajets avec auto-sélection du premier trajet"""
    log_callback(
        "render_trips_table",
        {"current_page": current_page, "refresh_clicks": refresh_clicks, "filters": filters},
        {"selected_trip": selected_trip}
    )
    
    # Configuration pagination
    page_size = Config.USERS_TABLE_PAGE_SIZE
    
    # Si la page n'est pas spécifiée, utiliser la page 1 par défaut
    if not isinstance(current_page, (int, float)):
        current_page = 1  # Défaut à 1 (pagination commence à 1)
    
    # Convertir la page en index 0-based pour l'API
    page_index = current_page - 1 if current_page > 0 else 0
    
    # Préparer les filtres pour le repository
    filter_params = {}
    
    # Ajouter le filtre texte s'il existe
    if filters and filters.get("text"):
        filter_params["text"] = filters.get("text")
        
    # Ajouter les filtres de date s'ils existent
    if filters and (filters.get("date_from") or filters.get("date_to") or filters.get("single_date")):
        filter_params["date_from"] = filters.get("date_from")
        filter_params["date_to"] = filters.get("date_to")
        filter_params["date_filter_type"] = filters.get("date_filter_type")
        filter_params["single_date"] = filters.get("single_date")
        
    # Ajouter le tri par date s'il est défini
    if filters and filters.get("date_sort"):
        filter_params["date_sort"] = filters.get("date_sort")
        
    # Ajouter les filtres de statut et signalement s'ils sont différents de "all"
    if filters and filters.get("status") and filters.get("status") != "all":
        filter_params["status"] = filters.get("status")
        
    if filters and filters.get("has_signalement"):
        filter_params["has_signalement"] = filters.get("has_signalement")

    # Déterminer si on force le rechargement (bouton refresh)
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    force_reload = (triggered_id == "refresh-trips-btn" and refresh_clicks is not None)

    # Utiliser le service de cache centralisé
    print(f"[TABLE] Chargement page {current_page} (index {page_index}), force_reload={force_reload}")
    
    result = TripsCacheService.get_trips_page_result(
        page_index, page_size, filter_params, force_reload
    )
    
    # Extraire les données nécessaires pour le tableau
    trips, total_trips, table_rows_data = TripsCacheService.extract_table_data(result)
    print(f"[TABLE] {len(trips)} trajets chargés")

    # Auto-sélection du premier trajet si aucun n'est sélectionné
    new_selected_trip = selected_trip
    if not selected_trip and table_rows_data and len(table_rows_data) > 0:
        # Sélectionner automatiquement le premier trajet de la page
        first_trip = table_rows_data[0]
        if isinstance(first_trip, dict) and first_trip.get("trip_id"):
            new_selected_trip = first_trip["trip_id"]
            print(f"[AUTO-SELECT] Premier trajet sélectionné automatiquement: {new_selected_trip}")
        elif hasattr(first_trip, "trip_id"):
            new_selected_trip = first_trip.trip_id
            print(f"[AUTO-SELECT] Premier trajet sélectionné automatiquement: {new_selected_trip}")

    # Calculer le nombre de pages
    page_count = math.ceil(total_trips / page_size) if total_trips > 0 else 1
    
    # Vérifier si la page courante est valide
    if current_page > page_count and page_count > 0:
        current_page = page_count

    # Rendu de la table avec les données pré-calculées
    table_component = render_custom_trips_table(
        table_rows_data, 
        current_page=current_page,
        total_trips=total_trips,
        selected_trip_id=new_selected_trip if isinstance(new_selected_trip, str) else (getattr(new_selected_trip, "trip_id", None) if new_selected_trip else None)
    )

    # Préchargement intelligent des panneaux pour les trajets visibles
    if table_rows_data and len(table_rows_data) > 0:
        visible_trip_ids = [row.get("trip_id") for row in table_rows_data[:5] if isinstance(row, dict) and row.get("trip_id")]
        if visible_trip_ids:
            try:
                TripsCacheService.preload_trip_panels(visible_trip_ids, ['details'])  # Précharger détails seulement
            except Exception as e:
                print(f"[PRELOAD] Erreur préchargement: {e}")
    
    # Message informatif
    if total_trips == 0:
        message = dbc.Alert("Aucun trajet trouvé avec les critères de recherche actuels.", color="info")
        return [message, table_component], new_selected_trip
    else:
        info_message = html.P(
            f"Affichage de {len(trips)} trajets sur {total_trips} au total (page {current_page}/{page_count})",
            className="text-muted small mb-3"
        )
        return [info_message, table_component], new_selected_trip


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
    Output("trip-stats-panel", "children"),
    [Input("selected-trip-id", "data")],
    prevent_initial_call=True
)
def render_trip_stats_panel(selected_trip):
    """Callback séparé pour le rendu du panneau statistiques trajet avec cache HTML"""
    log_callback(
        "render_trip_stats_panel",
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
    return TripsCacheService.get_trip_stats_panel(trip_id_value)


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


# Exporter le layout pour l'application principale
layout = get_layout()
