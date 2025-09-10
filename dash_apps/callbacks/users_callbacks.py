"""Callbacks pour la page Users"""

import dash
from dash import callback, Input, Output, State, callback_context, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash_apps.components.users_table import render_custom_users_table
from dash_apps.components.user_profile import render_user_profile
from dash_apps.components.user_stats import render_user_stats
from dash_apps.components.user_trips import render_user_trips
from dash_apps.components.user_search_widget import render_search_widget, render_active_filters
from dash_apps.repositories.repository_factory import RepositoryFactory
from dash_apps.services.redis_cache import redis_cache
from dash_apps.services.users_cache_service import UsersCacheService
from dash_apps.services.user_panels_preloader import UserPanelsPreloader

# Utiliser la factory pour obtenir le repository approprié
user_repository = RepositoryFactory.get_user_repository()

# Helper de log standardisé pour tous les callbacks (compatible Python < 3.10)
def log_callback(name, inputs, states=None):
    def _short_str(s):
        try:
            s = str(s)
            return f"{s[:4]}…{s[-4:]}" if len(s) > 14 else s
        except:
            return str(s)[:20]
    
    def _clean_dict(d):
        if not isinstance(d, dict):
            return d
        clean = {}
        for k, v in d.items():
            if v in (None, ""):
                continue
            if isinstance(v, str) and v == "all":
                continue
            if isinstance(v, (int, float, bool)):
                clean[k] = v
            else:
                clean[k] = _short_str(v)
        return clean
    
    try:
        import json
        sep = "=" * 74
        print(f"\n{sep}")
        print(f"[CB] {name}")
        print("Inputs:")
        for k, v in inputs.items():
            if isinstance(v, dict):
                v = _clean_dict(v)
                print(f"  - {k}: {json.dumps(v, ensure_ascii=False)}")
            else:
                print(f"  - {k}: {_short_str(v)}")
        if states:
            print("States:")
            for k, v in states.items():
                if isinstance(v, dict):
                    v = _clean_dict(v)
                    print(f"  - {k}: {json.dumps(v, ensure_ascii=False)}")
                else:
                    print(f"  - {k}: {_short_str(v)}")
        print(sep)
    except Exception:
        pass


@callback(
    Output("users-current-page", "data"),
    Output("selected-user-uid", "data", allow_duplicate=True),
    Output("users-filter-store", "data", allow_duplicate=True),
    Input("refresh-users-btn", "n_clicks"),
    Input("users-url", "search"),  # Ajout de l'URL comme input
    State("users-current-page", "data"),
    State("selected-user-uid", "data"),
    State("users-filter-store", "data"),
    prevent_initial_call=True
)
def get_page_info_on_page_load(n_clicks, url_search, current_page, selected_user, current_filters):
    log_callback(
        "get_page_info_on_page_load",
        {"n_clicks": n_clicks, "url_search": url_search},
        {"current_page": current_page, "selected_user": selected_user, "current_filters": current_filters}
    )
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Si l'URL a changé, traiter la sélection d'utilisateur
    if triggered_id == "users-url" and url_search:
        import urllib.parse
        params = urllib.parse.parse_qs(url_search.lstrip('?'))
        uid_list = params.get('uid')
        
        if uid_list:
            selected_uid = uid_list[0]
            user_from_url = {"uid": selected_uid}
            
            # Appliquer automatiquement un filtre de recherche sur l'uid
            # Cela affichera uniquement cet utilisateur et il sera sélectionné automatiquement
            filter_with_uid = {
                "text": selected_uid  # Utiliser l'uid comme filtre de recherche
            }
            
            print(f"[URL_SELECTION] Application du filtre pour l'utilisateur: {selected_uid}")
            return 1, user_from_url, filter_with_uid
    # Si refresh a été cliqué
    if triggered_id == "refresh-users-btn" and n_clicks is not None:
        return 1, selected_user, current_filters
    
    # Pour le chargement initial ou autres cas
    if current_page is None or not isinstance(current_page, (int, float)):
        return 1, selected_user, current_filters
        
    return current_page, selected_user, current_filters


@callback( 
    Output("refresh-users-message", "children"),
    Input("refresh-users-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_refresh_users_message(n_clicks):
    log_callback("show_refresh_users_message", {"n_clicks": n_clicks}, {})
    return dbc.Alert("Données utilisateurs rafraîchies!", color="success", dismissable=True)


@callback(
    Output("users-advanced-filters-collapse", "is_open"),
    Input("users-advanced-filters-btn", "n_clicks"),
    State("users-advanced-filters-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_advanced_filters(n_clicks, is_open):
    """Ouvre ou ferme le panneau des filtres avancés"""
    log_callback("toggle_advanced_filters", {"n_clicks": n_clicks}, {"is_open": is_open})
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output("users-filter-store", "data"),
    Input("users-apply-filters-btn", "n_clicks"),
    State("users-search-input", "value"),
    State("users-registration-date-filter", "start_date"),
    State("users-registration-date-filter", "end_date"),
    State("users-date-filter-type", "value"),
    State("users-single-date-filter", "date"),
    State("users-date-sort-filter", "value"),
    State("users-role-filter", "value"),
    State("users-driver-validation-filter", "value"),
    State("users-gender-filter", "value"),
    State("users-rating-operator-filter", "value"),
    State("users-rating-value-filter", "value"),
    State("users-filter-store", "data"),
    prevent_initial_call=True
)
def update_filters(
    n_clicks, search_text, date_from, date_to, date_filter_type, single_date, date_sort, role, driver_validation, gender, rating_operator, rating_value, current_filters
):
    """Met à jour les filtres de recherche lorsque l'utilisateur clique sur 'Appliquer'"""
    log_callback(
        "update_filters",
        {
            "n_clicks": n_clicks,
            "search_text": search_text,
            "date_from": date_from,
            "date_to": date_to,
            "date_filter_type": date_filter_type,
            "single_date": single_date,
            "date_sort": date_sort,
            "role": role,
            "driver_validation": driver_validation,
            "gender": gender,
            "rating_operator": rating_operator,
            "rating_value": rating_value
        },
        {"current_filters": current_filters}
    )
    
    if n_clicks is None:
        raise PreventUpdate
    
    new_filters = {}
    
    # Filtre de recherche textuelle
    if search_text and search_text.strip():
        new_filters["text"] = search_text.strip()
    
    # Filtres de date
    if date_filter_type == "range" and date_from and date_to:
        new_filters["date_from"] = date_from
        new_filters["date_to"] = date_to
    elif date_filter_type == "single" and single_date:
        new_filters["single_date"] = single_date
    
    # Tri par date
    if date_sort and date_sort != "desc":
        new_filters["date_sort"] = date_sort
    
    # Filtre par rôle
    if role and role != "all":
        new_filters["role"] = role
    
    # Filtre par validation conducteur
    if driver_validation and driver_validation != "all":
        new_filters["driver_validation"] = driver_validation
    
    # Filtre par genre
    if gender and gender != "all":
        new_filters["gender"] = gender
    
    # Filtre par note
    if rating_operator and rating_operator != "all" and rating_value is not None:
        new_filters["rating_operator"] = rating_operator
        new_filters["rating_value"] = rating_value
    
    return new_filters


@callback(
    Output("users-current-page", "data", allow_duplicate=True),
    Input("users-filter-store", "data"),
    prevent_initial_call=True
)
def reset_page_on_filter_change(filters):
    """Remet la page à 1 quand les filtres changent"""
    log_callback("reset_page_on_filter_change", {"filters": filters}, {})
    return 1


@callback(
    [Output("users-filter-store", "data", allow_duplicate=True),
     Output("users-search-input", "value"),
     Output("users-registration-date-filter", "start_date"),
     Output("users-registration-date-filter", "end_date"),
     Output("users-single-date-filter", "date"),
     Output("users-date-sort-filter", "value"),
     Output("users-role-filter", "value"),
     Output("users-driver-validation-filter", "value"),
     Output("users-gender-filter", "value"),
     Output("users-rating-operator-filter", "value"),
     Output("users-rating-value-filter", "value")],
    Input("users-clear-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_all_filters(n_clicks):
    """Efface tous les filtres"""
    log_callback("clear_all_filters", {"n_clicks": n_clicks}, {})
    return ({}, "", None, None, None, "desc", "all", "all", "all", "all", 3)


@callback(
    Output("users-active-filters", "children"),
    Input("users-filter-store", "data"),
)
def update_active_filters_display(filters):
    """Met à jour l'affichage des filtres actifs"""
    log_callback("update_active_filters_display", {"filters": filters}, {})
    return render_active_filters(filters)


@callback(
    [Output("main-users-content", "children")],
    [Input("users-current-page", "data"),
     Input("refresh-users-btn", "n_clicks"),
     Input("users-filter-store", "data")],
    prevent_initial_call=False
)
def update_users_table(current_page, refresh_clicks, filters):
    """Met à jour le tableau des utilisateurs"""
    log_callback(
        "update_users_table",
        {"current_page": current_page, "refresh_clicks": refresh_clicks, "filters": filters},
        {}
    )
    
    # Valeurs par défaut
    if current_page is None:
        current_page = 1
    if filters is None:
        filters = {}
    
    try:
        # Récupérer les utilisateurs avec pagination
        result = user_repository.get_users_paginated(
            page=current_page,
            page_size=5,
            filters=filters
        )
        
        users = result.get('users', [])
        total_count = result.get('total', 0)
        total_pages = result.get('total_pages', 1)
        
        print(f"[USERS][FETCH] page_index={current_page-1} users={len(users)} total={total_count} refresh={refresh_clicks is not None}")
        
        if not users:
            info_message = dbc.Alert(
                "Aucun utilisateur trouvé avec les critères de recherche actuels.",
                color="info",
                className="mt-3"
            )
            return [info_message]
        
        # Précharger les panneaux pour tous les utilisateurs de la page
        UsersCacheService.preload_user_panels([user.get('uid') for user in users if user.get('uid')])
        
        # Créer le tableau personnalisé
        table_component = render_custom_users_table(
            users_data=users,
            current_page=current_page,
            page_count=total_pages,
            total_users=total_count
        )
        
        print(f"[TABLE] {len(users)} utilisateurs chargés")
        return [table_component]
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la récupération des utilisateurs: {e}")
        error_message = dbc.Alert(
            f"Erreur lors du chargement des utilisateurs: {str(e)}",
            color="danger",
            className="mt-3"
        )
        return [error_message]


@callback(
    Output("user-details-panel", "children"),
    [Input("selected-user-uid", "data")],
    prevent_initial_call=True
)
def update_user_details(selected_user):
    """Met à jour le panneau de détails de l'utilisateur sélectionné"""
    log_callback("update_user_details", {"selected_user": selected_user}, {})
    
    if not selected_user:
        return "Sélectionnez un utilisateur pour voir ses détails."
    
    # Extraire l'UID selon le format
    if isinstance(selected_user, dict):
        uid_value = selected_user.get('uid')
    elif isinstance(selected_user, str):
        uid_value = selected_user
    else:
        uid_value = str(selected_user)
    
    if not uid_value:
        return "UID utilisateur non valide."
    
    print(f"[USER_DETAILS] Chargement des détails pour l'utilisateur: {uid_value}")
    
    # Utiliser le service de cache pour récupérer le panneau de profil
    return UsersCacheService.get_user_profile_panel(uid_value)


@callback(
    Output("user-stats-panel", "children"),
    [Input("selected-user-uid", "data")],
    prevent_initial_call=True
)
def update_user_stats(selected_user):
    """Met à jour le panneau de statistiques de l'utilisateur sélectionné"""
    log_callback("update_user_stats", {"selected_user": selected_user}, {})
    
    if not selected_user:
        return "Sélectionnez un utilisateur pour voir ses statistiques."
    
    # Extraire l'UID selon le format
    if isinstance(selected_user, dict):
        uid_value = selected_user.get('uid')
    elif isinstance(selected_user, str):
        uid_value = selected_user
    else:
        uid_value = str(selected_user)
    
    if not uid_value:
        return "UID utilisateur non valide."
    
    print(f"[USER_STATS] Chargement des statistiques pour l'utilisateur: {uid_value}")
    
    # Utiliser le service de cache pour récupérer le panneau de statistiques
    return UsersCacheService.get_user_stats_panel(uid_value)


@callback(
    Output("user-trips-panel", "children"),
    [Input("selected-user-uid", "data")],
    prevent_initial_call=True
)
def update_user_trips(selected_user):
    """Met à jour le panneau de trajets de l'utilisateur sélectionné"""
    log_callback("update_user_trips", {"selected_user": selected_user}, {})
    
    if not selected_user:
        return "Sélectionnez un utilisateur pour voir ses trajets."
    
    # Extraire l'UID selon le format
    if isinstance(selected_user, dict):
        uid_value = selected_user.get('uid')
    elif isinstance(selected_user, str):
        uid_value = selected_user
    else:
        uid_value = str(selected_user)
    
    if not uid_value:
        return "UID utilisateur non valide."
    
    print(f"[USER_TRIPS] Chargement des trajets pour l'utilisateur: {uid_value}")
    
    # Utiliser le service de cache pour récupérer le panneau de trajets
    return UsersCacheService.get_user_trips_panel(uid_value)
