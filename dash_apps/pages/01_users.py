import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from dash import dash_table
from dash_apps.config import Config
from dash_apps.components.users_table import render_users_table
from dash_apps.components.user_profile import render_user_profile
from dash_apps.components.user_stats import render_user_stats
from dash_apps.components.user_trips import render_user_trips
from dash_apps.repositories.user_repository import UserRepository

def get_layout():
    """Génère le layout de la page utilisateurs avec des IDs uniquement pour cette page"""
    return dbc.Container([
    dcc.Location(id="users-url", refresh=False),
    dcc.Store(id="users-page-store", storage_type="session"),
    dcc.Store(id="users-pagination-info", data={"page_count": 1, "total_users": 0}),
    dcc.Store(id="selected-user-state", storage_type="session", data=None),  # Un seul state pour l'utilisateur sélectionné
    html.H2("Dashboard utilisateurs", style={"marginTop": "20px"}),
    dbc.Row([
        dbc.Col([], width=9),
        dbc.Col([
            dbc.Button("🔄 Rafraîchir les données", id="refresh-users-btn", color="primary", className="mb-2")
        ], width=3)
    ]),
    html.Div(id="refresh-users-message"),
    dbc.Row([
        dbc.Col([
            # DataTable vide par défaut pour que l'id existe toujours
            html.Div(
                dash_table.DataTable(
                    id="users-table",
                    columns=[{"name": c, "id": c} for c in ["uid", "name", "email", "phone", "role", "created_at"]],
                    data=[],
                    row_selectable="single",
                    selected_rows=[],
                ), id="main-users-content"
            )
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

@callback(
    Output("users-pagination-info", "data"),
    Input("refresh-users-btn", "n_clicks"),
    prevent_initial_call=False
)
def calculate_pagination_info(n_clicks):
    """Calcule le nombre total d'utilisateurs et les informations de pagination"""
    # Récupérer le nombre total d'utilisateurs depuis le repository
    total_users = UserRepository.get_users_count()
    
    # Calculer le nombre de pages nécessaires
    page_size = Config.USERS_TABLE_PAGE_SIZE
    page_count = (total_users - 1) // page_size + 1 if total_users > 0 else 1
    
    print("Total users:", total_users)
    print("Page count:", page_count)
    print("Page size:", page_size)

    return {
        "total_users": total_users,
        "page_count": page_count,
        "page_size": page_size
    }

@callback(
    Output("users-page-store", "data"),
    Input("refresh-users-btn", "n_clicks"),
    prevent_initial_call=False
)
def load_users_data(n_clicks):
    users = UserRepository.get_all_users()
    # Convert Pydantic objects to dictionaries, handling date/datetime objects correctly
    users_data = [u.model_dump(mode='json') for u in users] if users else []
    return users_data


@callback( 
    Output("refresh-users-message", "children"),
    Input("refresh-users-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_refresh_users_message(n_clicks):
    return dbc.Alert("Données utilisateurs rafraîchies!", color="success", dismissable=True)

@callback(
    Output("main-users-content", "children"),
    Output("users-table", "selected_rows"),
    Output("selected-user-state", "data"),
    Input("users-page-store", "data"),
    Input("users-table", "selected_rows"),
    Input("users-url", "search"),
    Input("users-table", "page_current"),
    State("selected-user-state", "data"),
    State("users-pagination-info", "data"),
)
def handle_users_selection(users_data, selected_rows, url_search, page_current, stored_user_id, pagination_info):
    """Callback qui gère la table des utilisateurs et la sélection d'un utilisateur"""
    import urllib.parse
    preselect_row = None
    
    # Cas où aucune donnée utilisateur n'est disponible
    if not users_data:
        empty_df = pd.DataFrame([{"uid": "", "name": "", "email": "", "phone": "", "role": "", "created_at": ""}])
        table = render_users_table(
            empty_df, 
            selected_rows=selected_rows, 
            page_current=0, 
            page_size=Config.USERS_TABLE_PAGE_SIZE,
            page_count=1
        )
        return table, selected_rows, None
    
    users_df = pd.DataFrame(users_data)
    
    # Recherche d'un paramètre uid dans l'URL
    uid_from_url = None
    if url_search:
        params = urllib.parse.parse_qs(url_search.lstrip('?'))
        uid_list = params.get('uid')
        if uid_list:
            uid_from_url = uid_list[0]
    
    # Priorité à la sélection manuelle, puis à l'URL, puis au state existant
    current_uid = None
    
    if selected_rows:
        # Sélection manuelle dans le tableau
        preselect_row = selected_rows
    elif uid_from_url:
        # Sélection depuis l'URL
        try:
            idx = users_df.index[users_df['uid'] == uid_from_url].tolist()
            if idx:
                preselect_row = [idx[0]]
                current_uid = uid_from_url
        except Exception:
            preselect_row = []
    elif stored_user_id and isinstance(stored_user_id, dict) and 'uid' in stored_user_id:
        # Sélection depuis le state existant
        try:
            idx = users_df.index[users_df['uid'] == stored_user_id['uid']].tolist()
            if idx:
                preselect_row = [idx[0]]
                current_uid = stored_user_id['uid']
        except Exception:
            preselect_row = []
    
    # Par défaut, aucune sélection
    if preselect_row is None:
        preselect_row = []
    
    # Gestion de la pagination
    page_size = Config.USERS_TABLE_PAGE_SIZE
    
    # Utiliser la page courante du tableau ou 0 par défaut
    current_page = page_current if page_current is not None else 0
    
    # Récupérer le nombre total de pages depuis les infos de pagination
    page_count = pagination_info.get("page_count", 1) if pagination_info else 1
    
    # Rendu de la table
    table = render_users_table(
        users_df, 
        selected_rows=preselect_row, 
        page_current=current_page, 
        page_size=page_size,
        page_count=page_count
    )
    
    # Préparer les données pour le store utilisateur sélectionné
    selected_user_state = None
    if preselect_row and len(preselect_row) > 0:
        user = users_df.iloc[preselect_row[0]]
        # Stocker toutes les infos de l'utilisateur dans un seul state
        selected_user_state = user.to_dict()
    
    return table, preselect_row, selected_user_state

@callback(
    Output("user-details-panel", "children"),
    Output("user-stats-panel", "children"),
    Output("user-trips-panel", "children"),
    Input("selected-user-state", "data"),
)
def render_user_panels(selected_user_data):
    """Callback qui affiche les détails, statistiques et trajets de l'utilisateur sélectionné"""
    
    # Si aucun utilisateur n'est sélectionné
    if not selected_user_data:
        return None, None, None
    
    # S'assurer que les données sont sous forme de dictionnaire avec des valeurs par défaut
    # pour éviter les erreurs dans les templates Jinja2
    user_dict = selected_user_data.copy()
    
    # S'assurer que les champs critiques ont des valeurs par défaut
    default_fields = {
        'rating': 0,
        'rating_count': 0,
        'trips_count': 0,
        'created_at': None,
        'last_login': None
    }
    
    for field, default_value in default_fields.items():
        if field not in user_dict or user_dict[field] is None:
            user_dict[field] = default_value
    
    # Créer un objet qui supporte à la fois .get() et l'accès par index
    class UserWrapper:
        def __init__(self, data):
            self.data = data
        
        def __getitem__(self, key):
            return self.data.get(key)
        
        def get(self, key, default=None):
            return self.data.get(key, default)
    
    user = UserWrapper(user_dict)
    
    # Rendu des panneaux
    details = render_user_profile(user)
    stats = render_user_stats(user)
    trips = render_user_trips(user)
    
    return details, stats, trips

# Exporter le layout pour l'application principale
def calculate_page_current(selected_rows, page_size):
    """Calcule le numéro de page à afficher en fonction de la sélection
    
    Cette fonction détermine sur quelle page se trouve un index sélectionné,
    en fonction de la taille de page configurée.
    
    Args:
        selected_rows: Liste des indices des lignes sélectionnées dans la table
        page_size: Nombre d'éléments par page
        
    Returns:
        Le numéro de page (0-based) qui contient l'élément sélectionné
    """
    page_current = 0
    if selected_rows and len(selected_rows) > 0:
        idx = selected_rows[0]
        page_current = idx // page_size
    return page_current

layout = get_layout()
