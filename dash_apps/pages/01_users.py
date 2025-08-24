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
    dcc.Store(id="users-current-page", storage_type="session", data=0),  # State pour stocker la page courante
    dcc.Store(id="selected-user-state", storage_type="session", data=None),  # Un seul state pour l'utilisateur sélectionné
    dcc.Store(id="selected-user-from-url", storage_type="session", data=None),  # State pour la sélection depuis l'URL
    dcc.Store(id="selected-user-from-table", storage_type="session", data=None),  # State pour la sélection manuelle
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
    Output("users-current-page", "data"),
    Input("users-page-store", "data"),
    Input("users-table", "page_current"),
    State("selected-user-state", "data"),  # Repassé en State pour éviter un cycle de dépendance
    State("users-pagination-info", "data"),
    State("users-current-page", "data"),
)
def render_users_table_callback(users_data, page_current, selected_user, pagination_info, current_page_state):
    """Callback qui gère uniquement le rendu de la table des utilisateurs
    
    Cette fonction s'occupe aussi de synchroniser la sélection entre l'URL et le tableau
    """
    print(f"\n[DEBUG] Rendu table utilisateurs, page_current={page_current}, selected_user={selected_user}")
    
    # Initialiser la sélection et la page courante
    preselect_row = []
    target_page = page_current if page_current is not None else 0
    
    # Cas où aucune donnée utilisateur n'est disponible
    if not users_data:
        empty_df = pd.DataFrame([{"uid": "", "name": "", "email": "", "phone": "", "role": "", "created_at": ""}])
        table = render_users_table(
            empty_df, 
            selected_rows=[], 
            page_current=0, 
            page_size=Config.USERS_TABLE_PAGE_SIZE,
            page_count=1
        )
        return table, [], 0
    
    users_df = pd.DataFrame(users_data)
    
    # Déterminer la page à afficher
    if page_current is not None:
        current_page = page_current
    else:
        current_page = current_page_state if current_page_state is not None else 0
        
    # Déterminer la sélection en fonction de selected_user
    preselect_row = []
    
    # Si un utilisateur est sélectionné
    if selected_user and isinstance(selected_user, dict) and 'uid' in selected_user:
        uid = selected_user['uid']
        
        # Chercher l'index correspondant à l'uid dans le DataFrame
        try:
            idx = find_user_index(users_df, uid)
            if idx is not None:
                preselect_row = [idx]
                # Calculer la page où se trouve l'utilisateur si nécessaire
                if page_current is None:
                    page_size = Config.USERS_TABLE_PAGE_SIZE
                    current_page = idx // page_size
        except Exception as e:
            print(f"Erreur lors de la recherche de l'index pour l'uid {uid}: {str(e)}")
            preselect_row = []
    
    # Gestion de la pagination
    page_size = Config.USERS_TABLE_PAGE_SIZE
    
    # Récupérer le nombre total de pages depuis les infos de pagination
    page_count = pagination_info.get("page_count", 1) if pagination_info else 1
    
    # Vérifier que current_page est bien un nombre
    if not isinstance(current_page, (int, float)):
        current_page = 0
    
    # Rendu de la table
    table = render_users_table(
        users_df, 
        selected_rows=preselect_row, 
        page_current=current_page, 
        page_size=page_size,
        page_count=page_count
    )
    
    # Retourner le composant table, la sélection et la page courante
    return table, preselect_row, current_page

@callback(
    Output("user-details-panel", "children"),
    Output("user-stats-panel", "children"),
    Output("user-trips-panel", "children"),
    Input("selected-user-state", "data"),
)
def render_user_panels(selected_user_data):
    """Callback qui affiche les détails, statistiques et trajets de l'utilisateur sélectionné
    Désormais, selected_user_data ne contient que l'uid et l'index, il faut donc récupérer
    les données complètes depuis le repository
    """
    
    # Si aucun utilisateur n'est sélectionné
    print("selected_user_data", selected_user_data)
    if not selected_user_data or 'uid' not in selected_user_data:
        return None, None, None
    
    # Récupérer l'uid de l'utilisateur
    uid = selected_user_data['uid']
    
    # Récupérer les données complètes depuis le repository
    try:
        repo = UserRepository()
        user_model = repo.get_user_by_id(uid)
        
        if not user_model:
            print(f"Utilisateur non trouvé dans le repository: {uid}")
            return None, None, None
            
        # Convertir le modèle en dictionnaire pour une manipulation plus facile
        if hasattr(user_model, 'model_dump'):
            user_dict = user_model.model_dump(mode='json')
        else:
            # Si user_model est déjà un dict
            user_dict = user_model
    except Exception as e:
        print(f"Erreur lors de la récupération des données utilisateur: {str(e)}")
        user_dict = {"uid": uid}  # Utiliser au moins l'uid disponible
    
    # Conserver l'index si disponible
    if 'index' in selected_user_data:
        user_dict['index'] = selected_user_data['index']
    
    # S'assurer que les champs critiques ont des valeurs par défaut
    default_fields = {
        'rating': 0,
        'rating_count': 0,
        'trips_count': 0,
        'created_at': None,
        'last_login': None,
        'name': "Utilisateur",
        'email': "",
        'phone': "",
        'role': "user"
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

# Fonction utilitaire pour trouver l'index d'un utilisateur par son uid
def find_user_index(users_df, uid):
    """Recherche l'index d'un utilisateur dans le dataframe par son uid
    
    Args:
        users_df: DataFrame contenant les utilisateurs
        uid: L'identifiant unique de l'utilisateur recherché
        
    Returns:
        L'index de l'utilisateur s'il est trouvé, None sinon
    """
    try:
        idx = users_df.index[users_df['uid'] == uid].tolist()
        return idx[0] if idx else None
    except Exception:
        return None

# Callback spécifique pour gérer la sélection manuelle
@callback(
    Output("selected-user-from-table", "data"),
    Input("users-table", "selected_rows"),
    State("users-page-store", "data"),
    prevent_initial_call=True
)
def handle_manual_selection(selected_rows, users_data):
    """Callback qui gère la sélection d'un utilisateur manuellement dans le tableau"""
    # Si aucune donnée ou pas de sélection
    if not users_data or not selected_rows:
        return None
    
    users_df = pd.DataFrame(users_data)
    
    # Récupérer uniquement l'uid de l'utilisateur sélectionné
    try:
        idx = selected_rows[0]
        user = users_df.iloc[idx]
        # Retourner seulement l'uid
        return user['uid']
    except Exception:
        return None

# Callback spécifique pour gérer la sélection par URL
@callback(
    Output("selected-user-from-url", "data"),
    Input("users-url", "search"),
    State("users-page-store", "data"),
    prevent_initial_call=True
)
def handle_url_selection(url_search, users_data):
    """Callback qui gère la sélection d'un utilisateur par paramètre URL"""
    import urllib.parse
    
    # Si aucune donnée ou pas de recherche URL
    if not users_data or not url_search:
        return None
        
    # Recherche d'un paramètre uid dans l'URL
    params = urllib.parse.parse_qs(url_search.lstrip('?'))
    uid_list = params.get('uid')
    if not uid_list:
        return None
        
    uid_from_url = uid_list[0]
    users_df = pd.DataFrame(users_data)

    print(f"Recherche de l'utilisateur {uid_from_url}")
    
    # Vérifier si l'uid existe dans les données
    if uid_from_url in users_df['uid'].values:
        # Retourner directement l'uid
        return uid_from_url
    
    return None


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


@callback(
    Output("selected-user-state", "data"),
    Input("selected-user-from-table", "data"),
    Input("selected-user-from-url", "data"),
    Input("users-page-store", "data"),
    prevent_initial_call=False
)
def consolidate_user_selection(table_selection, url_selection, users_data):
    """Callback qui détermine l'utilisateur sélectionné en fonction du dernier changement
    Sans priorité fixe, c'est la dernière sélection qui a déclenché le callback qui est retenue
    Maintenant nous recevons directement des UIDs au lieu d'objets utilisateur
    """
    print("[TEST] consolidate_user_selection")
    print("table_selection", table_selection)
    print("url_selection", url_selection)

    # Utilisation du callback context pour déterminer quel Input a déclenché le callback
    from dash import callback_context
    
    # Si aucun callback n'a été déclenché ou si les deux sélections sont None
    if not callback_context.triggered or (table_selection is None and url_selection is None):
        return None
    
    # Déterminer l'input qui a déclenché le callback
    triggered = callback_context.triggered[0]
    triggered_id = triggered['prop_id'].split('.')[0]
    print(f"Input déclencheur: {triggered_id}")
    
    # Déterminer l'UID sélectionné strictement en fonction de l'input qui a déclenché le callback
    if triggered_id == "selected-user-from-table" and table_selection is not None:
        selected_uid = table_selection
        print(f"Sélection depuis table: {selected_uid}")
    elif triggered_id == "selected-user-from-url" and url_selection is not None:
        selected_uid = url_selection
        print(f"Sélection depuis URL: {selected_uid}")
    elif triggered_id == "users-page-store":
        # Si le déclencheur est le store, on garde la dernière sélection connue, priorité à l'URL
        selected_uid = url_selection if url_selection is not None else table_selection
        print(f"Sélection depuis store, utilisation valeur existante: {selected_uid}")
    else:
        # Fallback, priorité à URL puis table
        selected_uid = url_selection if url_selection is not None else table_selection
        print(f"Autre cas, utilisation valeur existante: {selected_uid}")
    
    # Si on a un UID, on retourne un objet avec l'UID
    if selected_uid:
        print("selected_uid final", selected_uid)
        return {"uid": selected_uid}
    
    return None