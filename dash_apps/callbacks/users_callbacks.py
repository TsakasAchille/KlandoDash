"""Callbacks pour la page Users"""

import os
import dash
from dash import html, dcc, Input, Output, State, callback, callback_context
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash.exceptions as de
from dash_apps.components.users_table import render_custom_users_table
from dash_apps.components.user_profile import render_user_profile
from dash_apps.components.user_stats import render_user_stats
from dash_apps.components.user_trips import render_user_trips
from dash_apps.components.user_search_widget import render_search_widget, render_active_filters
from dash_apps.services.users_table_service import UsersTableService
from dash_apps.services.user_details_cache_service import UserDetailsCache
from dash_apps.services.user_stats_cache_service import UserStatsCache
from dash_apps.services.user_profile_cache_service import UserProfileCache
from dash_apps.services.user_trips_service import UserTripsService
from dash_apps.layouts.user_detail_layout import UserDetailLayout
from dash_apps.layouts.user_profile_layout import UserProfileLayout
from dash_apps.utils.settings import load_json_config, get_jinja_template
from dash_apps.utils.callback_logger import CallbackLogger

# Fonction utilitaire pour debug logging unifié
def debug_log_users(event_name, data=None, status="INFO", extra_info=""):
    """Log debug pour les callbacks users avec DEBUG_USERS"""
    debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
    if debug_users:
        CallbackLogger.log_callback(
            event_name,
            data or {},
            status=status,
            extra_info=extra_info
        )


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
    debug_log_users(
        "get_page_info_on_page_load",
        {"n_clicks": n_clicks, "url_search": url_search[:50] if url_search else None, "current_page": current_page},
        "INFO",
        "Page load callback triggered"
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
            
            # Cela affichera uniquement cet utilisateur et il sera sélectionné automatiquement
            filter_with_uid = {
                "text": selected_uid  # Utiliser l'uid comme filtre de recherche
            }
            
            debug_log_users(
                "user_selected_from_url",
                {"uid": selected_uid[:8] if selected_uid else None},
                "INFO",
                "User selected from URL parameter"
            )
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
    debug_log_users("show_refresh_users_message", {"n_clicks": n_clicks})
    return dbc.Alert("Données utilisateurs rafraîchies!", color="success", dismissable=True)


@callback(
    Output("users-advanced-filters-collapse", "is_open"),
    Input("users-advanced-filters-btn", "n_clicks"),
    State("users-advanced-filters-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_advanced_filters(n_clicks, is_open):
    """Ouvre ou ferme le panneau des filtres avancés"""
    debug_log_users("toggle_advanced_filters", {"n_clicks": n_clicks, "is_open": is_open})
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
    debug_log_users(
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
        "INFO",
        "Updating user filters"
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
    CallbackLogger.log_callback("reset_page_on_filter_change", {"filters": filters}, status="INFO", extra_info="Page reset due to filter change")
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
    Input("users-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_all_filters(n_clicks):
    """Efface tous les filtres"""
    debug_log_users("clear_all_filters", {"n_clicks": n_clicks})
    return ({}, "", None, None, None, "desc", "all", "all", "all", "all", 3)


@callback(
    Output("users-active-filters", "children"),
    Input("users-filter-store", "data"),
)
def update_active_filters_display(filters):
    """Met à jour l'affichage des filtres actifs"""
    debug_log_users(
        "update_active_filters_display",
        {"filters_count": len(filters) if filters else 0},
        "INFO",
        "Updating active filters display"
    )
    return render_active_filters(filters)


@callback(
    Output("main-users-content", "children"),
    [Input("users-current-page", "data"),
     Input("refresh-users-btn", "n_clicks"),
     Input("users-filter-store", "data"),
     Input("selected-user-uid", "data")],
    prevent_initial_call=False
)
def update_users_table(current_page, refresh_clicks, filters, selected_user):
    """Met à jour le tableau des utilisateurs"""
    debug_log_users(
        "update_users_table",
        {"current_page": current_page, "refresh_clicks": refresh_clicks, "filters_count": len(filters) if filters else 0},
        "INFO",
        "Updating users table"
    )
    
    # Valeurs par défaut
    if current_page is None:
        current_page = 1
    if filters is None:
        filters = {}
    
    try:
        # Récupérer les utilisateurs avec pagination via le nouveau service
        result = UsersTableService.get_users_page(
            page=current_page,
            page_size=5,
            filters=filters
        )
        
        users = result.get('users', [])
        total_count = result.get('total_count', 0)
        total_pages = result.get('total_pages', 1)
        
        print(f"[USERS][FETCH] page_index={current_page-1} users={len(users)} total={total_count} refresh={refresh_clicks is not None}")
        
        if not users:
            info_message = dbc.Alert(
                "Aucun utilisateur trouvé avec les critères de recherche actuels.",
                color="info",
                className="mt-3"
            )
            return info_message
        
        # Créer le tableau personnalisé
        table_component = render_custom_users_table(
            users_data=users,
            current_page=current_page,
            page_count=total_pages,
            total_users=total_count,
            selected_uid=selected_user
        )
        
        print(f"[TABLE] {len(users)} utilisateurs chargés")
        return table_component
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la récupération des utilisateurs: {e}")
        error_message = dbc.Alert(
            f"Erreur lors du chargement des utilisateurs: {str(e)}",
            color="danger",
            className="mt-3"
        )
        return error_message


@callback(
    Output("selected-user-uid", "data", allow_duplicate=True),
    [Input("users-filter-store", "data")],
    prevent_initial_call=True
)
def auto_select_user_on_filter(filters):
    """Auto-sélectionne un utilisateur quand le filtre retourne exactement un résultat"""
    if not filters:
        raise PreventUpdate
    
    debug_log_users(
        "auto_select_user_on_filter",
        {"filters_count": len(filters) if filters else 0},
        "INFO",
        "Checking for auto-selection"
    )
    
    try:
        # Récupérer les utilisateurs avec les filtres appliqués
        result = UsersTableService.get_users_page(
            page=1,
            page_size=5,
            filters=filters
        )
        
        total_count = result.get('total_count', 0)
        users = result.get('users', [])
        
        # Auto-sélection si exactement un utilisateur trouvé
        if total_count == 1 and len(users) == 1:
            user_uid = users[0].get('uid')
            if user_uid:
                debug_log_users(
                    "auto_select_user",
                    {"user_uid": user_uid, "total_count": total_count},
                    "INFO",
                    "Auto-selecting single user from filter result"
                )
                return user_uid
    
    except Exception as e:
        debug_log_users(
            "auto_select_user_on_filter",
            {"error": str(e)},
            "ERROR",
            "Error in auto-selection"
        )
    
    raise PreventUpdate


@callback(
    Output("user-details-panel", "children"),
    [Input("selected-user-uid", "data")],
    prevent_initial_call=True
)
def render_user_details_panel(selected_user):
    """Met à jour le panneau de détails de l'utilisateur sélectionné"""
    debug_log_users(
        "update_user_details",
        {"selected_user": str(selected_user)[:8] if selected_user else None},
        "INFO",
        "Updating user details panel"
    )
    
    if not selected_user:
        return "Sélectionnez un utilisateur pour voir ses détails."
    
    # Extract UID from dictionary if needed
    if isinstance(selected_user, dict) and 'uid' in selected_user:
        uid_value = selected_user['uid']
    else:
        uid_value = selected_user
    
    if not uid_value:
        return "UID utilisateur non valide."
    
    debug_log_users(
        "user_details_load_start",
        {"uid": str(uid_value)[:8] if uid_value else None},
        "INFO",
        "Loading user details"
    )
    
    try:
        # 1. Récupérer les données utilisateur via le cache
        user_data = UserDetailsCache.get_user_details_data(uid_value)
        
        # 2. Vérifier si les données sont disponibles
        if not user_data:
            error_panel = UserDetailLayout.render_error_panel(
                "Impossible de récupérer les données utilisateur."
            )
            return error_panel
        
        # 3. Charger la configuration complète
        config = load_json_config('user_details_config.json')
        
        # 4. Générer le panneau USER DETAILS avec la nouvelle configuration
        details_style_config = config.get('user_details', {}).get('template_style', config.get('template_style', {}))
        
        # Paramètres pour l'iframe (conteneur externe)
        iframe_height = details_style_config.get('height', '600px')
        iframe_width = details_style_config.get('width', '100%')
        iframe_min_height = details_style_config.get('min_height', '400px')
        
        # Paramètres pour la card interne (template Jinja2)
        details_card_height = details_style_config.get('card_height', '550px')
        details_card_width = details_style_config.get('card_width', '100%')
        
        # Debug pour vérifier les valeurs
        debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
        if debug_users:
            CallbackLogger.log_callback(
                "user_details_template_config_debug", 
                {
                    "iframe_height": iframe_height,
                    "iframe_width": iframe_width,
                    "iframe_min_height": iframe_min_height,
                    "card_height": details_card_height,
                    "card_width": details_card_width,
                    "full_config": details_style_config
                }, 
                status="INFO", 
                extra_info="User details template configuration values (iframe + card)"
            )
            
        # 5. Générer le panneau USER DETAILS avec template dynamique
        user_template = get_jinja_template('user_profile_template.jinja2')
        user_html_content = user_template.render(
            user=user_data,
            config=config.get('user_details', {}),
            layout={
                'card_height': details_card_height,
                'card_width': details_card_width
            }
        )
        
        user_panel = html.Div([
            html.Iframe(
                srcDoc=user_html_content,
                style={
                    "width": iframe_width,
                    "height": iframe_height,
                    "minHeight": iframe_min_height,
                    "border": "none",
                    "borderRadius": "12px"
                }
            )
        ])
        
        if debug_users:
            CallbackLogger.log_callback(
                "user_details_panel_generated",
                {"uid": str(uid_value)[:8] if uid_value else 'None'},
                status="SUCCESS",
                extra_info="User details panel generated with Jinja2 template"
            )
        
        return user_panel
        
    except Exception as e:
        debug_log_users(
            "user_details_load_error",
            {"uid": str(uid_value)[:8] if uid_value else None, "error": str(e)},
            "ERROR",
            "Failed to load user details"
        )
        # Retourner un panneau d'erreur simple
        return html.Div([
            html.H4("Erreur de chargement", className="text-danger"),
            html.P(f"Impossible de charger les détails de l'utilisateur: {str(e)}")
        ], className="alert alert-danger")


@callback(
    Output("user-stats-panel", "children"),
    [Input("selected-user-uid", "data")],
    prevent_initial_call=True
)
def update_user_stats(selected_user):
    debug_log_users(
        "update_user_stats",
        {"selected_user": str(selected_user)[:8] if selected_user else None},
        "INFO",
        "Updating user stats panel"
    )
    
    if not selected_user:
        return html.Div("Sélectionnez un utilisateur pour voir ses statistiques.", className="text-muted")
    
    # Extract UID from dictionary if needed
    if isinstance(selected_user, dict) and 'uid' in selected_user:
        uid_value = selected_user['uid']
    else:
        uid_value = selected_user
    
    if not uid_value:
        return html.Div("UID utilisateur non valide.", className="text-danger")
    
    debug_log_users(
        "user_stats_load_start",
        {"uid": str(uid_value)[:8] if uid_value else None},
        "INFO",
        "Loading user statistics"
    )
    
    try:
        # Get real user statistics from database
        user_stats = UserStatsCache.get_user_stats(uid_value)
        
        if user_stats is None:
            debug_log_users(
                "user_stats_no_data",
                {"uid": str(uid_value)[:8] if uid_value else None},
                "WARNING",
                "No user stats found"
            )
            return html.Div("Impossible de calculer les statistiques utilisateur.", className="text-warning")
        
        # Charger la configuration pour les stats (template style only)
        config = load_json_config('user_stats_config.json')
        template_config = config.get('template_style', {})
        
        # Configuration des dimensions
        stats_card_height = template_config.get('card_height', '350px')
        stats_card_width = template_config.get('card_width', '100%')
        iframe_height = template_config.get('height', '400px')
        iframe_width = template_config.get('width', '100%')
        iframe_min_height = template_config.get('min_height', '300px')
        
        debug_users = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
        if debug_users:
            CallbackLogger.log_callback(
                "user_stats_real_data_debug",
                {
                    "uid": str(uid_value)[:8],
                    "stats": user_stats,
                    "template_config": template_config
                },
                status="INFO",
                extra_info="Real user stats loaded from database"
            )
        
        # Générer le HTML avec le template Jinja2 en utilisant les vraies statistiques
        template = get_jinja_template('user_stats_template.jinja2')
        user_html_content = template.render(
            stats=user_stats,  # Use real stats from database
            config=config.get('user_stats', {}),
            layout={
                'card_height': stats_card_height,
                'card_width': stats_card_width
            }
        )
        
        user_panel = html.Div([
            html.Iframe(
                srcDoc=user_html_content,
                style={
                    "width": iframe_width,
                    "height": iframe_height,
                    "minHeight": iframe_min_height,
                    "border": "none",
                    "borderRadius": "12px"
                }
            )
        ])
        
        # debug_users déjà défini plus haut dans la fonction
        if debug_users:
            CallbackLogger.log_callback(
                "user_stats_panel_generated",
                {"uid": str(uid_value)[:8] if uid_value else 'None'},
                status="SUCCESS",
                extra_info="User stats panel generated with Jinja2 template"
            )
        
        return user_panel
        
    except Exception as e:
        debug_log_users(
            "user_stats_load_error",
            {"uid": str(uid_value)[:8] if uid_value else None, "error": str(e)},
            "ERROR",
            "Failed to load user statistics"
        )
        # Retourner un panneau d'erreur simple
        return html.Div([
            html.H4("Erreur de chargement", className="text-danger"),
            html.P(f"Impossible de charger les statistiques de l'utilisateur: {str(e)}")
        ], className="alert alert-danger")

@callback(
    Output("user-trips-panel", "children"),
    [Input("selected-user-uid", "data")],
    prevent_initial_call=True
)
def update_user_trips(selected_user):
    debug_log_users(
        "update_user_trips",
        {"selected_user": str(selected_user)[:8] if selected_user else None},
        "INFO",
        "Updating user trips panel"
    )
    
    if not selected_user:
        return "Sélectionnez un utilisateur pour voir ses trajets."
    
    # Extract UID from dictionary if needed
    if isinstance(selected_user, dict) and 'uid' in selected_user:
        uid_value = selected_user['uid']
    else:
        uid_value = selected_user
    
    if not uid_value:
        return "UID utilisateur non valide."
    
    debug_log_users(
        "user_trips_load_start",
        {"uid": str(uid_value)[:8] if uid_value else None},
        "INFO",
        "Loading user trips"
    )
    
    try:
        # Utiliser le nouveau service de trajets utilisateur
        trips_data = UserTripsService.get_user_trips(uid_value)
        if trips_data and trips_data.get('trips'):
            # Convertir les données en DataFrame pour render_user_trips
            import pandas as pd
            trips_df = pd.DataFrame(trips_data['trips'])
            
            # Utiliser le composant existant pour le rendu
            return render_user_trips(user_id=uid_value, data=trips_df)
        else:
            return dbc.Alert("Aucun trajet trouvé pour cet utilisateur.", color="info")
    except Exception as e:
        debug_log_users(
            "user_trips_load_error",
            {"uid": str(uid_value)[:8] if uid_value else None, "error": str(e)},
            "ERROR",
            "Failed to load user trips"
        )
        return dbc.Alert(f"Erreur lors du chargement des trajets: {str(e)}", color="danger")

