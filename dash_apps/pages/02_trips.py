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
            html.Div(id="trip-details-panel")
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
    prevent_initial_call='initial_duplicate'
)
def get_page_info_on_page_load(n_clicks, url_search, current_page, selected_trip):
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
                print(f"\n[DEBUG] Page trouvée pour le trajet {trip_id}: {new_page}")
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
     Input("trips-status-filter", "value")],
    [State("trips-filter-store", "data")],
    prevent_initial_call=True
)
def update_trip_filters(search_text, date_from, date_to, single_date, date_filter_type, 
                       date_sort, status, current_filters):
    """Met à jour les filtres de recherche des trajets"""
    
    # Construction du dictionnaire de filtres
    filters = {
        "text": search_text or "",
        "date_from": date_from,
        "date_to": date_to,
        "single_date": single_date,
        "date_filter_type": date_filter_type or "range",
        "date_sort": date_sort or "desc",
        "status": status or "all"
    }
    
    # Ne déclencher une mise à jour que si les filtres ont vraiment changé
    if filters != current_filters:
        print(f"Filtres trajets mis à jour: {filters}")
        return filters
    
    raise PreventUpdate


@callback(
    Output("trips-current-page", "data", allow_duplicate=True),
    Input("trips-filter-store", "data"),
    prevent_initial_call=True
)
def reset_trip_page_on_filter_change(filters):
    """Réinitialise la page à 1 lorsque les filtres changent"""
    # Toujours revenir à la page 1 quand un filtre change
    return 1


@callback(
    [Output("trips-filter-store", "data", allow_duplicate=True),
     Output("trips-search-input", "value")],
    Input("trips-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_trip_filters(n_clicks):
    """Réinitialise tous les filtres et vide la barre de recherche"""
    return {}, ""


@callback(
    Output("trips-active-filters", "children"),
    Input("trips-filter-store", "data"),
)
def display_active_trip_filters(filters):
    """Affiche les filtres actifs sous forme de badges"""
    return render_active_trip_filters(filters)


@callback(
    Output("main-trips-content", "children"),
    [Input("trips-current-page", "data"),
     Input("trips-filter-store", "data"),
     Input("refresh-trips-btn", "n_clicks")],
    [State("selected-trip-id", "data")],
    prevent_initial_call=False
)
def render_trips_table_pagination(current_page, filters, refresh_clicks, selected_trip):
    """Rendu du tableau des trajets avec pagination côté serveur"""
    print(f"\n[DEBUG] render_trips_table_pagination")
    print(f"current_page {current_page}")
    
    # Déterminer le déclencheur
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else "initial"
    print(f"Trigger: {trigger_id}")
    print(f"Filters: {filters}")
    
    # Valeurs par défaut
    current_page = current_page or 1
    filters = filters or {}
    page_size = Config.USERS_TABLE_PAGE_SIZE
    page_index = current_page - 1  # Convertir en 0-based pour le repository
    
    # Préparer les paramètres de filtrage pour le repository
    filter_params = {}
    
    if filters.get("text"):
        filter_params["text"] = filters["text"]
    
    # Gestion des filtres de date
    if filters.get("date_filter_type") == "after" and filters.get("single_date"):
        filter_params["date_filter_type"] = "after"
        filter_params["single_date"] = filters["single_date"]
    elif filters.get("date_filter_type") == "before" and filters.get("single_date"):
        filter_params["date_filter_type"] = "before"
        filter_params["single_date"] = filters["single_date"]
    else:
        if filters.get("date_from"):
            filter_params["date_from"] = filters["date_from"]
        if filters.get("date_to"):
            filter_params["date_to"] = filters["date_to"]
    
    # Tri par date
    if filters.get("date_sort"):
        filter_params["date_sort"] = filters["date_sort"]
    
    # Filtre statut
    if filters.get("status") and filters["status"] != "all":
        filter_params["status"] = filters["status"]
    
    # Récupérer uniquement les trajets de la page courante avec filtres (pagination côté serveur)
    result = TripRepository.get_trips_paginated(page_index, page_size, filters=filter_params)
    trips = result.get("trips", [])
    total_trips = result.get("total_count", 0)
    
    # Calculer le nombre de pages
    page_count = math.ceil(total_trips / page_size) if total_trips > 0 else 1
    
    # Vérifier si la page courante est valide
    if current_page > page_count and page_count > 0:
        current_page = page_count
    
    # Créer le tableau personnalisé
    table_component = render_custom_trips_table(
        trips, 
        current_page, 
        total_trips, 
        selected_trip_id=selected_trip if isinstance(selected_trip, str) else (selected_trip.get("trip_id") if selected_trip else None)
    )
    
    # Message informatif
    if total_trips == 0:
        message = dbc.Alert("Aucun trajet trouvé avec les critères de recherche actuels.", color="info")
        return [message, table_component]
    else:
        info_message = html.P(
            f"Affichage de {len(trips)} trajets sur {total_trips} au total (page {current_page}/{page_count})",
            className="text-muted small mb-3"
        )
        return [info_message, table_component]


@callback(
    Output("trip-details-panel", "children"),
    Input("selected-trip-id", "data"),
    prevent_initial_call=False
)
def render_trip_details(selected_trip):
    """Affiche les détails du trajet sélectionné"""
    print(f"\n[DEBUG] render_trip_details")
    print(f"selected_trip {selected_trip}")
    
    if not selected_trip:
        return html.Div()
    
    # Gérer le cas où selected_trip est une string (trip_id) ou un dict
    if isinstance(selected_trip, str):
        trip_id = selected_trip
    elif isinstance(selected_trip, dict) and selected_trip.get("trip_id"):
        trip_id = selected_trip["trip_id"]
    else:
        return html.Div()
    
    # Utiliser la fonction existante pour créer le layout des détails
    return create_trip_details_layout(trip_id, None)


# Exporter le layout pour l'application principale
layout = get_layout()
