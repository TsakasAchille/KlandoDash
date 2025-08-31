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
                # Flatten pour selected_user
                if k in ("selected_user", "selected_user_uid") and isinstance(v, dict) and "uid" in v:
                    cleaned["selected_uid"] = _short_str(v.get("uid"))
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


def find_user_page_index(uid, page_size):
    """Trouve l'index de page sur lequel se trouve l'utilisateur avec l'UID donné
    
    Args:
        uid: UID de l'utilisateur à trouver
        page_size: Taille de chaque page
        
    Returns:
        Index de la page (0-based) ou None si non trouvé
    """
    try:
        position = UserRepository.get_user_position(uid)
        if position is not None:
            page_index = position // page_size
            return page_index
        return None
    except Exception:
        return None


# Helper: rendre JSON-serializable (datetime -> isoformat, Pydantic -> dict)
def _to_jsonable(obj):
    """Convertit récursivement un objet en structure JSON-serializable.
    - datetime/date -> isoformat()
    - Pydantic v2 -> model_dump()
    - Pydantic v1 -> dict()
    - Decimal -> float
    - set -> list
    - objets inconnus -> str(obj)
    """
    try:
        import datetime as _dt
        import decimal as _dec
    except Exception:
        pass

    # Déballer Pydantic models
    if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
        try:
            obj = obj.model_dump()
        except Exception:
            obj = dict(obj)
    elif hasattr(obj, "dict") and callable(getattr(obj, "dict")) and not isinstance(obj, dict):
        try:
            obj = obj.dict()
        except Exception:
            try:
                obj = dict(obj)
            except Exception:
                obj = str(obj)

    # Types simples
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # datetime/date
    try:
        import datetime as _dt2
        if isinstance(obj, (_dt2.datetime, _dt2.date)):
            return obj.isoformat()
    except Exception:
        pass

    # Decimal
    try:
        import decimal as _dec2
        if isinstance(obj, _dec2.Decimal):
            return float(obj)
    except Exception:
        pass

    # list/tuple
    if isinstance(obj, (list, tuple, set)):
        return [_to_jsonable(v) for v in list(obj)]

    # dict
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}

    # fallback
    try:
        return str(obj)
    except Exception:
        return None



def get_layout():
    """Génère le layout de la page utilisateurs avec des IDs uniquement pour cette page"""
    return dbc.Container([
    dcc.Location(id="users-url", refresh=False),
    #dcc.Store(id="users-pagination-info", data={"page_count": 1, "total_users": 0}),
    dcc.Store(id="users-current-page", storage_type="session", data=1),  # State pour stocker la page courante (persistant)
    dcc.Store(id="selected-user-uid", storage_type="session", data=None, clear_data=False),  # Store pour l'UID de l'utilisateur sélectionné (persistant)
    # Cache session pour éviter les rechargements inutiles (clé = page + filtres)
    dcc.Store(id="users-page-cache", storage_type="session", data={}, clear_data=False),
    # Store session pour conserver les données basiques des utilisateurs visibles (clé = uid)
    dcc.Store(id="users-page-userdata", storage_type="session", data={}, clear_data=False),
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
            dcc.Loading(
                children=html.Div(id="user-details-panel"),
                type="default"
            )
        ], width=6),
        dbc.Col([
            dcc.Loading(
                children=html.Div(id="user-stats-panel"),
                type="default"
            )
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                children=html.Div(id="user-trips-panel"),
                type="default"
            )
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
    prevent_initial_call=True
)
def get_page_info_on_page_load(n_clicks, url_search, current_page, selected_user):
    log_callback(
        "get_page_info_on_page_load",
        {"n_clicks": n_clicks, "url_search": url_search},
        {"current_page": current_page, "selected_user": selected_user}
    )
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
    Input("users-search-input", "value"),
    Input("users-registration-date-filter", "start_date"),
    Input("users-registration-date-filter", "end_date"),
    Input("users-date-filter-type", "value"),
    Input("users-single-date-filter", "date"),
    Input("users-date-sort-filter", "value"),
    Input("users-role-filter", "value"),
    Input("users-driver-validation-filter", "value"),
    Input("users-gender-filter", "value"),
    Input("users-rating-operator-filter", "value"),
    Input("users-rating-value-filter", "value"),
    State("users-filter-store", "data"),
    prevent_initial_call=True
)
def update_filters(
    search_text, date_from, date_to, date_filter_type, single_date, date_sort, role, driver_validation, gender, rating_operator, rating_value, current_filters
):
    """Met à jour les filtres de recherche lorsque l'utilisateur modifie les champs"""
    log_callback(
        "update_filters",
        {
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
            "rating_value": rating_value,
        },
        {"current_filters": current_filters}
    )
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
    elif triggered_id == "users-date-filter-type":
        current_filters["date_filter_type"] = date_filter_type
    elif triggered_id == "users-single-date-filter":
        current_filters["single_date"] = single_date
    elif triggered_id == "users-date-sort-filter":
        current_filters["date_sort"] = date_sort
    elif triggered_id == "users-role-filter":
        current_filters["role"] = role
    elif triggered_id == "users-driver-validation-filter":
        current_filters["driver_validation"] = driver_validation
    elif triggered_id == "users-gender-filter":
        current_filters["gender"] = gender
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
    
    return current_filters

"""
@callback(
    Output("users-current-page", "data", allow_duplicate=True),
    Input("users-filter-store", "data"),
    prevent_initial_call=True
)
def reset_page_on_filter_change(filters):
    log_callback("reset_page_on_filter_change", {"filters": filters}, {})
    # Toujours revenir à la page 1 quand un filtre change
    return 1

"""
@callback(
    [Output("users-filter-store", "data", allow_duplicate=True),
     Output("users-search-input", "value")],
    Input("users-reset-filters-btn", "n_clicks"),
    prevent_initial_call=True
)
def reset_filters(n_clicks):
    """Réinitialise tous les filtres et vide la barre de recherche"""
    log_callback("reset_filters", {"n_clicks": n_clicks}, {})
    return {}, ""


@callback(
    Output("users-active-filters", "children"),
    Input("users-filter-store", "data"),
)
def display_active_filters(filters):
    """Affiche les filtres actifs sous forme de badges"""
    log_callback("display_active_filters", {"filters": filters}, {})
    return render_active_filters(filters)



@callback(
    Output("main-users-content", "children"),
    Output("users-page-cache", "data"),
    Output("users-page-userdata", "data"),
    Input("users-current-page", "data"),
    Input("refresh-users-btn", "n_clicks"),
    Input("selected-user-uid", "data"),
    Input("users-filter-store", "data"),
    State("users-page-cache", "data"),
    prevent_initial_call=True
)
def render_users_table_pagination(current_page, n_clicks, selected_user, filters, page_cache):
    """Callback responsable uniquement de la pagination et du rendu du tableau"""
    log_callback(
        "render_users_table_pagination",
        {"current_page": current_page, "n_clicks": n_clicks, "selected_user": selected_user, "filters": filters},
        {"page_cache_present": isinstance(page_cache, dict)}
    )
    # Initialise le cache si nécessaire
    if not isinstance(page_cache, dict):
        page_cache = {}

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
        
    # Ajouter les filtres de rôle et validation conducteur s'ils sont différents de "all"
    if filters and filters.get("role") and filters.get("role") != "all":
        filter_params["role"] = filters.get("role")
        
    if filters and filters.get("driver_validation") and filters.get("driver_validation") != "all":
        filter_params["driver_validation"] = filters.get("driver_validation")
        
    # Ajouter le filtre genre s'il est différent de "all"
    if filters and filters.get("gender") and filters.get("gender") != "all":
        filter_params["gender"] = filters.get("gender")
        
    # Ajouter les filtres de rating s'ils existent et si l'opérateur est différent de "all"
    if filters and filters.get("rating_operator") and filters.get("rating_operator") != "all" and filters.get("rating_value") is not None:
        filter_params["rating_operator"] = filters.get("rating_operator")
        filter_params["rating_value"] = filters.get("rating_value")

    # Construire une clé de cache basée sur page + filtres
    try:
        filters_key = json.dumps(filter_params, sort_keys=True, ensure_ascii=False)
    except Exception:
        filters_key = str(filter_params)
    cache_key = f"p={page_index}|f={filters_key}"

    # Déterminer si on force le rechargement (bouton refresh)
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    force_reload = (triggered_id == "refresh-users-btn" and n_clicks is not None)

    users = []
    total_users = 0

    if (not force_reload) and cache_key in page_cache:
        cached = page_cache.get(cache_key) or {}
        # Sanitize cached content in case older entries contain datetimes or Pydantic models
        users = _to_jsonable(cached.get("users", []))
        total_users = int(cached.get("total_count", 0))
        try:
            print(f"[USERS][CACHE HIT] page_index={page_index} key={cache_key} users={len(users)} total={total_users}")
        except Exception:
            pass
    else:
        # Appel serveur uniquement si pas en cache ou refresh explicite
        result = UserRepository.get_users_paginated(page_index, page_size, filters=filter_params)
        raw_users = result.get("users", [])
        total_users = int(result.get("total_count", 0))
        # Convertir avant usage (UI et cache) pour garantir JSON-serializable
        users = _to_jsonable(raw_users)
        # Mettre à jour le cache (écrase l'entrée)
        page_cache[cache_key] = {"users": users, "total_count": total_users}
        try:
            print(f"[USERS][FETCH] page_index={page_index} key={cache_key} users={len(users)} total={total_users} refresh={force_reload}")
        except Exception:
            pass

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
    # Préparer un dictionnaire basique par UID pour pré-charger le profil
    basic_by_uid = {}
    try:
        for u in users or []:
            uid = (u or {}).get("uid")
            if not uid:
                continue
            # Conserver uniquement les champs utiles au profil (sûrs pour le front)
            basic_by_uid[uid] = {
                k: (u.get(k)) for k in [
                    "uid", "display_name", "first_name", "name", "email", "phone", "phone_number",
                    "gender", "role", "rating", "rating_count", "photo_url", "birth", "bio",
                    "created_time", "updated_at"
                ] if k in u
            }
    except Exception:
        basic_by_uid = {}

    # Retourner le tableau, le cache et les données basiques des utilisateurs visibles
    return table, page_cache, basic_by_uid


@callback(
    Output("user-details-panel", "children"),
    Input("selected-user-uid", "data"),
    State("users-page-userdata", "data"),
    prevent_initial_call=True
)
def render_user_profile_panel(selected_user, page_userdata):
    """Rendu du panneau profil (utilise les données préchargées si disponibles)"""
    log_callback("render_user_profile_panel", {"selected_user": selected_user}, {})
    uid = selected_user.get("uid") if isinstance(selected_user, dict) else selected_user
    if not uid:
        return html.Div()
    pre_user = None
    try:
        if isinstance(page_userdata, dict):
            pre_user = page_userdata.get(uid)
    except Exception:
        pre_user = None
    return render_user_profile(uid, user=pre_user)

@callback(
    Output("user-stats-panel", "children"),
    Input("selected-user-uid", "data"),
    prevent_initial_call=True
)
def render_user_stats_panel(selected_user):
    """Rendu du panneau statistiques"""
    log_callback("render_user_stats_panel", {"selected_user": selected_user}, {})
    uid = selected_user.get("uid") if isinstance(selected_user, dict) else selected_user
    if not uid:
        return html.Div()
    return render_user_stats(uid)

@callback(
    Output("user-trips-panel", "children"),
    Input("selected-user-uid", "data"),
    prevent_initial_call=True
)
def render_user_trips_panel(selected_user):
    """Rendu du panneau trajets"""
    log_callback("render_user_trips_panel", {"selected_user": selected_user}, {})
    uid = selected_user.get("uid") if isinstance(selected_user, dict) else selected_user
    if not uid:
        return html.Div()
    return render_user_trips(uid)




@callback(
    Output("users-url", "pathname", allow_duplicate=True),  # Output factice pour permettre le callback
    [
        Input("users-current-page", "data"),
        Input("selected-user-uid", "data"),
        Input("users-filter-store", "data"),
        Input("refresh-users-btn", "n_clicks"),
        Input("users-search-input", "value"),
        Input("users-registration-date-filter", "start_date"),
        Input("users-registration-date-filter", "end_date"),
        Input("users-date-filter-type", "value"),
        Input("users-single-date-filter", "date"),
        Input("users-date-sort-filter", "value"),
        Input("users-role-filter", "value"),
        Input("users-driver-validation-filter", "value"),
        Input("users-gender-filter", "value"),
        Input("users-rating-operator-filter", "value"),
        Input("users-rating-value-filter", "value"),
        Input("users-url", "search"),
        Input("url-init-trigger", "n_intervals")
    ],
    prevent_initial_call=True
)
def debug_all_inputs(
    current_page, selected_user, filter_store, refresh_clicks,
    search_input, date_from, date_to, date_filter_type, single_date, date_sort,
    role_filter, driver_validation, gender_filter, rating_operator, rating_value,
    url_search, url_trigger
):
    """Callback de debug minimal: log standardisé de tous les inputs/states"""
    log_callback(
        "debug_all_inputs",
        {
            "current_page": current_page,
            "selected_user": selected_user,
            "filter_store": filter_store,
            "refresh_clicks": refresh_clicks,
            "search_input": search_input,
            "date_from": date_from,
            "date_to": date_to,
            "date_filter_type": date_filter_type,
            "single_date": single_date,
            "date_sort": date_sort,
            "role_filter": role_filter,
            "driver_validation": driver_validation,
            "gender_filter": gender_filter,
            "rating_operator": rating_operator,
            "rating_value": rating_value,
            "url_search": url_search,
            "url_trigger": url_trigger,
        },
        {}
    )
    return dash.no_update


layout = get_layout()
