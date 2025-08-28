import math
import json
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback, Input, Output, State
from dash.exceptions import PreventUpdate
from dash_apps.config import Config
# Import du nouveau composant personnalisé à la place du DataTable
from dash_apps.components.users_table import render_custom_users_table
from dash_apps.components.user_profile import render_user_profile
from dash_apps.components.user_stats import render_user_stats
from dash_apps.components.user_trips import render_user_trips
from dash_apps.components.user_search_widget import render_search_widget, render_active_filters
from dash_apps.repositories.user_repository import UserRepository


def find_user_page_index(uid, page_size):
    """Trouve l'index de page sur lequel se trouve l'utilisateur avec l'UID donné
    
    Args:
        uid: UID de l'utilisateur à trouver
        page_size: Taille de chaque page
        
    Returns:
        Index de la page (0-based) ou None si non trouvé
    """
    try:
        # Utiliser la méthode optimisée du repository pour trouver la position de l'utilisateur
        position = UserRepository.get_user_position(uid)
        
        if position is not None:
            # Calculer l'index de page (0-based)
            page_index = position // page_size
            # Ajouter des logs détaillés
            print(f"Utilisateur {uid} trouvé à la position {position} (selon le repository)")
            print(f"Taille de page: {page_size}")
            print(f"Calcul page: {position} // {page_size} = {page_index}")
            print(f"Page calculée (0-based): {page_index}, (1-based): {page_index + 1}")
            return page_index
        
        print(f"Utilisateur {uid} non trouvé dans le repository")
        return None
    except Exception as e:
        print(f"Erreur lors de la recherche de page pour l'utilisateur {uid}: {str(e)}")
        return None



def get_layout():
    """Génère le layout de la page utilisateurs avec des IDs uniquement pour cette page"""
    return dbc.Container([
    dcc.Location(id="users-url", refresh=False),
    #dcc.Store(id="users-pagination-info", data={"page_count": 1, "total_users": 0}),
    dcc.Store(id="users-current-page", storage_type="session", data=1),  # State pour stocker la page courante (persistant)
    dcc.Store(id="selected-user-uid", storage_type="session", data=None, clear_data=False),  # Store pour l'UID de l'utilisateur sélectionné (persistant)
    dcc.Store(id="url-parameters", storage_type="memory", data=None),  # Store temporaire pour les paramètres d'URL
    dcc.Store(id="selected-user-from-url", storage_type="memory", data=None),  # State pour la sélection depuis l'URL
    dcc.Store(id="users-filter-store", storage_type="session", data={}, clear_data=False),  # Store pour les filtres de recherche
    # Interval pour déclencher la lecture des paramètres d'URL au chargement initial (astuce pour garantir l'exécution)
    dcc.Interval(id='url-init-trigger', interval=100, max_intervals=1),  # Exécute une seule fois au chargement
  
    html.H2("Dashboard utilisateurs", style={"marginTop": "20px"}),
    dbc.Row([
        dbc.Col([], width=9),
        dbc.Col([
            dbc.Button("🔄 Rafraîchir les données", id="refresh-users-btn", color="primary", className="mb-2")
        ], width=3)
    ]),
    html.Div(id="refresh-users-message"),
    # Widget de recherche
    render_search_widget(),
    # Affichage des filtres actifs
    html.Div(id="users-active-filters"),
    dbc.Row([
        dbc.Col([
            # Conteneur vide qui sera rempli par le callback render_users_table_callback
            html.Div(id="main-users-content")
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id="user-details-panel")
        ], width=6),
        dbc.Col([
            html.Div(id="user-stats-panel")
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id="user-trips-panel")
        ], width=12)
    ])
], fluid=True)



# Note: Le store users-page-store n'est plus utilisé pour stocker tous les utilisateurs
# car nous utilisons maintenant un chargement à la demande page par page

@callback(
    Output("users-current-page", "data"),
    Output("selected-user-uid", "data", allow_duplicate=True),
    Input("refresh-users-btn", "n_clicks"),
    Input("users-url", "search"),  # Ajout de l'URL comme input
    State("users-current-page", "data"),
    State("selected-user-uid", "data"),
    prevent_initial_call='initial_duplicate'
)
def get_page_info_on_page_load(n_clicks, url_search, current_page, selected_user):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Si l'URL a changé, traiter la sélection d'utilisateur
    if triggered_id == "users-url" and url_search:
        import urllib.parse
        params = urllib.parse.parse_qs(url_search.lstrip('?'))
        uid_list = params.get('uid')
        
        if uid_list:
            user_from_url = {"uid": uid_list[0]}
            # On va chercher sur quelle page se trouve l'utilisateur
            uid = uid_list[0]
            page_index = find_user_page_index(uid, Config.USERS_TABLE_PAGE_SIZE)
            if page_index is not None:
                # Convertir en 1-indexed pour l'interface
                new_page = page_index + 1
                return new_page, user_from_url
            else:
                return current_page, user_from_url
    # Si refresh a été cliqué
    if triggered_id == "refresh-users-btn" and n_clicks is not None:
        return 1, selected_user
    
    # Pour le chargement initial ou autres cas
    if current_page is None or not isinstance(current_page, (int, float)):
        return 1, selected_user
        
    return current_page, selected_user

@callback( 
    Output("refresh-users-message", "children"),
    Input("refresh-users-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_refresh_users_message(n_clicks):
    return dbc.Alert("Données utilisateurs rafraîchies!", color="success", dismissable=True)


@callback(
    Output("users-advanced-filters-collapse", "is_open"),
    Input("users-advanced-filters-btn", "n_clicks"),
    State("users-advanced-filters-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_advanced_filters(n_clicks, is_open):
    """Ouvre ou ferme le panneau des filtres avancés"""
    if n_clicks:
        return not is_open
    return is_open


@callback(
    Output("users-filter-store", "data"),
    Input("users-search-input", "value"),
    Input("users-registration-date-filter", "start_date"),
    Input("users-registration-date-filter", "end_date"),
    Input("users-role-filter", "value"),
    Input("users-driver-validation-filter", "value"),
    Input("users-rating-operator-filter", "value"),
    Input("users-rating-value-filter", "value"),
    State("users-filter-store", "data"),
    prevent_initial_call=True
)
def update_filters(
    search_text, date_from, date_to, role, driver_validation, rating_operator, rating_value, current_filters
):
    """Met à jour les filtres de recherche lorsque l'utilisateur modifie les champs"""
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Initialiser les filtres s'ils n'existent pas
    if not current_filters:
        current_filters = {}
    
    # Mettre à jour le filtre approprié en fonction du champ modifié
    if triggered_id == "users-search-input":
        current_filters["text"] = search_text
    elif triggered_id == "users-registration-date-filter":
        current_filters["date_from"] = date_from
        current_filters["date_to"] = date_to
    elif triggered_id == "users-role-filter":
        current_filters["role"] = role
    elif triggered_id == "users-driver-validation-filter":
        current_filters["driver_validation"] = driver_validation
    elif triggered_id == "users-rating-operator-filter" or triggered_id == "users-rating-value-filter":
        if rating_operator != "all":
            current_filters["rating_operator"] = rating_operator
            current_filters["rating_value"] = rating_value
        else:
            # Si l'opérateur est réinitialisé à "all", supprimer les filtres de rating
            if "rating_operator" in current_filters:
                del current_filters["rating_operator"]
            if "rating_value" in current_filters:
                del current_filters["rating_value"]
    
    # Réinitialiser la page à 1 lorsqu'un filtre change
    # (Nous gèrerons cela dans un callback séparé)
    
    print(f"Filtres mis à jour: {current_filters}")
    return current_filters


@callback(
    Output("users-current-page", "data", allow_duplicate=True),
    Input("users-filter-store", "data"),
    prevent_initial_call=True
)
def reset_page_on_filter_change(filters):
    """Réinitialise la page à 1 lorsque les filtres changent"""
    # Toujours revenir à la page 1 quand un filtre change
    return 1


@callback(
    Output("users-filter-store", "data", allow_duplicate=True),
    Input("users-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    """Réinitialise tous les filtres"""
    return {}


@callback(
    Output("users-active-filters", "children"),
    Input("users-filter-store", "data"),
)
def display_active_filters(filters):
    """Affiche les filtres actifs sous forme de badges"""
    return render_active_filters(filters)



@callback(
    Output("main-users-content", "children"),
    Input("users-current-page", "data"),
    Input("refresh-users-btn", "n_clicks"),
    Input("selected-user-uid", "data"),
    Input("users-filter-store", "data"),
    prevent_initial_call=True
)
def render_users_table_pagination(current_page, n_clicks, selected_user, filters):
    """Callback responsable uniquement de la pagination et du rendu du tableau"""
    from dash import ctx
    print("\n[DEBUG] render_users_table_pagination")
    print("current_page", current_page)
    print("Trigger:", ctx.triggered_id)
    print("Filters:", filters)
    
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
    if filters and (filters.get("date_from") or filters.get("date_to")):
        filter_params["date_from"] = filters.get("date_from")
        filter_params["date_to"] = filters.get("date_to")
        
    # Ajouter les filtres de rôle et validation conducteur s'ils sont différents de "all"
    if filters and filters.get("role") and filters.get("role") != "all":
        filter_params["role"] = filters.get("role")
        
    if filters and filters.get("driver_validation") and filters.get("driver_validation") != "all":
        filter_params["driver_validation"] = filters.get("driver_validation")
        
    # Ajouter les filtres de rating s'ils existent et si l'opérateur est différent de "all"
    if filters and filters.get("rating_operator") and filters.get("rating_operator") != "all" and filters.get("rating_value") is not None:
        filter_params["rating_operator"] = filters.get("rating_operator")
        filter_params["rating_value"] = filters.get("rating_value")
        print(f"Ajout des filtres rating: {filters.get('rating_operator')}, {filters.get('rating_value')}")
    
    # Récupérer uniquement les utilisateurs de la page courante avec filtres (pagination côté serveur)
    result = UserRepository.get_users_paginated(page_index, page_size, filters=filter_params)
    users = result.get("users", [])
    total_users = result.get("total_count", 0)
    
    # Récupérer l'utilisateur sélectionné du store (sans déclencher de mise à jour)
    # Pour l'afficher comme sélectionné dans le tableau
    selected_uid_value = selected_user.get("uid") if selected_user else None
    
    # Rendu de la table avec notre composant personnalisé
    table = render_custom_users_table(
        users, 
        current_page=current_page,  # 1-indexed pour notre composant personnalisé
        total_users=total_users,
        selected_uid=selected_uid_value
    )
    
    # Retourner uniquement le tableau
    return table


@callback(
    [Output("user-details-panel", "children"),
     Output("user-stats-panel", "children"),
     Output("user-trips-panel", "children")],
    Input("selected-user-uid", "data"),
    prevent_initial_call=True
)
def render_user_details(selected_user):
    """Callback responsable uniquement de l'affichage des détails d'un utilisateur sélectionné"""
    print("\n[DEBUG] render_user_details")
    print(f"selected_user {selected_user}")
    
    # Extraire l'UID de l'utilisateur
    selected_uid_value = selected_user.get("uid") if isinstance(selected_user, dict) else selected_user
    
    if not selected_uid_value:
        return html.Div(), html.Div(), html.Div()
        
    # Appeler directement les fonctions de layout avec l'UID
    details = render_user_profile(selected_uid_value)
    stats = render_user_stats(selected_uid_value)
    trips = render_user_trips(selected_uid_value)
    
    return details, stats, trips




layout = get_layout()
