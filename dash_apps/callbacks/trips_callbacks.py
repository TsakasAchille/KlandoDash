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
from dash_apps.services.trip_details_cache_service import TripDetailsCache
from dash_apps.services.trip_driver_cache_service import TripDriverCache
from dash_apps.layouts.trip_detail_layout import TripDetailLayout
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.settings import load_json_config, get_jinja_template

# Utiliser la factory pour obtenir le repository approprié
trip_repository = RepositoryFactory.get_trip_repository()


# Use the enhanced callback logger
def log_callback(name, inputs, states=None):
    """Wrapper for backward compatibility with enhanced logging"""
    CallbackLogger.log_callback(name, inputs, states)



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
    # Vérifier si le debug des trajets est activé
    import os
    debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
    
    if debug_trips:
        CallbackLogger.log_callback(
            "get_page_info_on_page_load",
            {"n_clicks": n_clicks, "url_search": url_search},
            {"current_page": current_page, "selected_trip": selected_trip, "current_filters": current_filters},
            status="INFO",
            extra_info="Page initialization"
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
            
            # Appliquer automatiquement un filtre de recherche sur le trip_id
            # Cela affichera uniquement ce trajet et il sera sélectionné automatiquement
            filter_with_trip_id = {
                "text": selected_trip_id  # Utiliser le trip_id comme filtre de recherche
            }
            
            if debug_trips:
                CallbackLogger.log_api_call("URL_SELECTION", 
                    {"trip_id": selected_trip_id, "filter_applied": True}, 
                    status="SUCCESS")
            # Retourner directement le trip_id string, pas un dict
            return 1, selected_trip_id, filter_with_trip_id
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
    # Vérifier si le debug des trajets est activé
    import os
    debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
    
    if debug_trips:
        CallbackLogger.log_callback("show_refresh_trips_message", {"n_clicks": n_clicks})
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
    # Vérifier si le debug des trajets est activé
    import os
    debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
    
    if debug_trips:
        CallbackLogger.log_callback("toggle_trip_filters_collapse", {"n_clicks": n_clicks}, {"is_open": is_open})
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
    # Vérifier si le debug des trajets est activé
    import os
    debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
    
    if debug_trips:
        CallbackLogger.log_callback(
            "update_trip_filters",
            {"search_text": search_text, "status": status, "has_signalement": has_signalement},
            extra_info="Applying filters"
        )
    
    # Construction du dictionnaire de filtres - ne pas forcer les valeurs par défaut
    filters = {}
    
    # N'ajouter que les filtres qui ont une valeur explicite
    if search_text:
        filters["text"] = search_text
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    if single_date:
        filters["single_date"] = single_date
    if date_filter_type:
        filters["date_filter_type"] = date_filter_type
    if date_sort:
        filters["date_sort"] = date_sort
    if status and status != "all":
        filters["status"] = status
    if has_signalement:
        filters["has_signalement"] = True
    
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
    # Compact log for simple reset
    # Vérifier si le debug des trajets est activé
    import os
    debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
    
    if filters and debug_trips:
        CallbackLogger.log_callback("reset_trip_page_on_filter_change", {"filters": filters})
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
    # Vérifier si le debug des trajets est activé
    import os
    debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
    
    if debug_trips:
        CallbackLogger.log_callback("reset_trip_filters", {"n_clicks": n_clicks})
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
    # Only log if filters are not empty
    # Vérifier si le debug des trajets est activé
    import os
    debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
    
    if filters and debug_trips:
        CallbackLogger.log_callback("display_active_trip_filters", {"filters": filters})
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
    # Vérifier si le debug des trajets est activé
    import os
    debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
    
    if debug_trips:
        CallbackLogger.log_callback(
            "render_trips_table",
            {"current_page": current_page, "refresh_clicks": refresh_clicks, "filters": filters, "selected_trip": selected_trip},
            status="INFO",
            extra_info=f"Page {current_page}"
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
    if debug_trips:
        CallbackLogger.log_cache_operation(
            "get_trips_page_result", 
            f"page_{page_index}_size_{page_size}", 
            details={"force_reload": force_reload, "filters": len(filter_params)}
        )
    
    result = TripsCacheService.get_trips_page_result(
        page_index, page_size, filter_params, force_reload
    )
    
    # Utiliser directement les données optimisées du repository
    trips = result.get("trips", [])
    total_trips = result.get("total_count", 0)
    
    if debug_trips:
        CallbackLogger.log_api_call(
            "TRIPS_DATA_LOADED", 
            {"trips_count": len(trips), "total_count": total_trips, "page": current_page},
            status="SUCCESS" if trips else "WARNING"
        )

    # Auto-sélection du premier trajet si aucun n'est sélectionné
   
    # Calculer le nombre de pages
    page_count = math.ceil(total_trips / page_size) if total_trips > 0 else 1
    
    # Validation stricte de la page courante
    if current_page > page_count and page_count > 0:
        if debug_trips:
            CallbackLogger.log_api_call("PAGINATION_REDIRECT", 
                {"from_page": current_page, "to_page": page_count, "reason": "page_too_high"}, 
                status="WARNING")
        current_page = page_count
    elif current_page < 1:
        if debug_trips:
            CallbackLogger.log_api_call("PAGINATION_REDIRECT", 
                {"from_page": current_page, "to_page": 1, "reason": "page_too_low"}, 
                status="WARNING")
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
    [Output("trip-details-panel", "children"),
     Output("trip-stats-panel", "children")],
    Input("selected-trip-id", "data"),
    prevent_initial_call=False
)
def render_trip_details_and_stats_panel(selected_trip_id):
    # Vérifier si le debug des trajets est activé
    import os
    debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
    
    if debug_trips:
        CallbackLogger.log_callback(
            "render_trip_details_panel",
            {"selected_trip_id": selected_trip_id},
            status="INFO",
            extra_info="Loading trip details"
        )
    
    # Si pas d'ID, retourner des panneaux vides
    if not selected_trip_id:
        if debug_trips:
            CallbackLogger.log_callback(
                "render_trip_details_panel", 
                {"selected_trip_id": "None"}, 
                status="WARNING", 
                extra_info="No trip selected"
            )
        return html.Div(), html.Div()

    # 1. Récupérer les données via le service de cache
    data = TripDetailsCache.get_trip_details_data(selected_trip_id)
    
    # 2. Si pas de données, retourner des panels d'erreur
    if not data:
        error_panel = TripDetailLayout.render_error_panel(
            "Impossible de récupérer les données du trajet."
        )
        return error_panel, error_panel
    print("____________________________________________________________________________________________________")
    print("data")
    print(data)
    print("____________________________________________________________________________________________________")
    # 3. Charger la configuration complète
    config = load_json_config('trip_details_config.json')
    
    # 4. Générer les panneaux avec la nouvelle configuration séparée
    details_style_config = config.get('trip_details', {}).get('details_template_style', {})
    
    # Paramètres pour l'iframe (conteneur externe)
    iframe_height = details_style_config.get('height', '500px')
    iframe_width = details_style_config.get('width', '100%')
    iframe_min_height = details_style_config.get('min_height', '400px')
    
    # Paramètres pour la card interne (template Jinja2)
    details_card_height = details_style_config.get('card_height', '350px')
    details_card_width = details_style_config.get('card_width', '100%')
    details_card_min_height = details_style_config.get('card_min_height', '300px')
    
    # Debug pour vérifier les valeurs
    if debug_trips:
        CallbackLogger.log_callback(
            "template_config_debug_details", 
            {
                "iframe_height": iframe_height,
                "iframe_width": iframe_width,
                "iframe_min_height": iframe_min_height,
                "card_height": details_card_height,
                "card_width": details_card_width,
                "card_min_height": details_card_min_height,
                "full_config": details_style_config
            }, 
            status="INFO", 
            extra_info="Trip details template configuration values (iframe + card)"
        )
    
    # 5. Générer le panneau DETAILS avec template dynamique
    details_template = get_jinja_template('trip_details_template.jinja2')
    details_html_content = details_template.render(
        trip=data,
        config=config.get('trip_details', {}),
        layout={
            'card_height': details_card_height,
            'card_width': details_card_width,
            'card_min_height': details_card_min_height
        }
    )
    
    details_panel = html.Div([
        html.Iframe(
            srcDoc=details_html_content,
            style={
                "width": iframe_width,
                "height": iframe_height,
                "minHeight": iframe_min_height,
                "border": "none",
                "borderRadius": "12px"
            }
        )
    ])
    
    # 6. Générer le panneau STATS avec template dynamique et sa propre configuration
    stats_style_config = config.get('trip_details', {}).get('stats_template_style', {})
    
    # Paramètres spécifiques pour le panneau stats
    stats_iframe_height = stats_style_config.get('height', '500px')
    stats_iframe_width = stats_style_config.get('width', '100%')
    stats_iframe_min_height = stats_style_config.get('min_height', '400px')
    
    stats_card_height = stats_style_config.get('card_height', '350px')
    stats_card_width = stats_style_config.get('card_width', '100%')
    stats_card_min_height = stats_style_config.get('card_min_height', '300px')
    
    stats_template = get_jinja_template('trip_stats_template.jinja2')
    stats_html_content = stats_template.render(
        trip=data,
        config=config.get('trip_details', {}).get('trip_stats', {}),
        layout={
            'card_height': stats_card_height,
            'card_width': stats_card_width,
            'card_min_height': stats_card_min_height
        }
    )
    
    stats_panel = html.Div([
        html.Iframe(
            srcDoc=stats_html_content,
            style={
                "width": stats_iframe_width,
                "height": stats_iframe_height,
                "minHeight": stats_iframe_min_height,
                "border": "none",
                "borderRadius": "12px"
            }
        )
    ])
        
    # 6. Retourner les deux panneaux
    return details_panel, stats_panel


@callback(
    Output("trip-driver-panel", "children"),
    [Input("selected-trip-id", "data")],
    prevent_initial_call=True
)
def render_trip_driver_panel(selected_trip_id):
    # Vérifier si le debug des trajets est activé
    import os
    debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
    debug_trips = True

    print("selected_trip_id", selected_trip_id)
    if debug_trips:
        CallbackLogger.log_callback(
            "render_trip_driver_panel", 
            {"selected_trip_id": selected_trip_id}, 
            status="INFO", 
            extra_info="Driver panel rendering"
        )

    # Si aucun trajet sélectionné, retourner un div vide
    if not selected_trip_id:
        if debug_trips:
            CallbackLogger.log_callback(
                "render_trip_driver_panel", 
                {"selected_trip_id": "None"}, 
                status="WARNING", 
                extra_info="No trip selected"
            )
        return html.Div()

    # 1. Récupérer les données conducteur via le service de cache spécialisé
    data = TripDriverCache.get_trip_driver_data(selected_trip_id)
    
    # 2. Si pas de données, retourner un panel d'erreur
    if not data:
        error_panel = TripDetailLayout.render_error_panel(
            "Impossible de récupérer les données du conducteur."
        )
        return error_panel
    
    # 3. Charger la configuration complète
    config = load_json_config('trip_driver_config.json')
    
    # 4. Générer le panneau DRIVER avec la nouvelle configuration séparée
    driver_style_config = config.get('trip_driver', {}).get('template_style', {})
    
    # Paramètres pour l'iframe (conteneur externe)
    iframe_height = driver_style_config.get('height', '500px')
    iframe_width = driver_style_config.get('width', '100%')
    iframe_min_height = driver_style_config.get('min_height', '400px')
    
    # Paramètres pour la card interne (template Jinja2)
    driver_card_height = driver_style_config.get('card_height', '400px')
    driver_card_width = driver_style_config.get('card_width', '100%')
    driver_card_min_height = driver_style_config.get('card_min_height', '300px')
    
    # Debug pour vérifier les valeurs
    if debug_trips:
        CallbackLogger.log_callback(
            "template_config_debug", 
            {
                "iframe_height": iframe_height,
                "iframe_width": iframe_width,
                "iframe_min_height": iframe_min_height,
                "card_height": driver_card_height,
                "card_width": driver_card_width,
                "card_min_height": driver_card_min_height,
                "full_config": driver_style_config
            }, 
            status="INFO", 
            extra_info="Template configuration values (iframe + card)"
        )
        
    # 5. Générer le panneau DRIVER avec template dynamique
    driver_template = get_jinja_template('trip_driver_template_dynamic.jinja2')
    driver_html_content = driver_template.render(
        trip=data,
        config=config.get('trip_driver', {}),
        layout={
            'card_height': driver_card_height,
            'card_width': driver_card_width,
            'card_min_height': driver_card_min_height
        }
    )
    
    driver_panel = html.Div([
        html.Iframe(
            srcDoc=driver_html_content,
            style={
                "width": iframe_width,
                "height": iframe_height,
                "minHeight": iframe_min_height,
                "border": "none",
                "borderRadius": "12px"
            }
        )
    ])
        
    return driver_panel


@callback(
    Output("trip-passengers-panel", "children"),
    [Input("selected-trip-id", "data")],
    prevent_initial_call=True
)
def render_trip_passengers_panel(selected_trip_id):
    # Vérifier si le debug des trajets est activé
    import os
    debug_trips = os.getenv('DEBUG_TRIPS', 'False').lower() == 'true'
    
    if debug_trips:
        CallbackLogger.log_callback(
            "render_trip_passengers_panel",
            {"selected_trip_id": selected_trip_id},
            status="INFO",
            extra_info="Loading passengers"
        )
    
    # Read-Through pattern: le cache service gère tout
    return TripsCacheService.get_trip_passengers_panel(selected_trip_id)
