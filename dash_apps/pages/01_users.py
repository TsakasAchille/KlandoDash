import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import pandas as pd
from dash import dash_table
from dash_apps.config import Config
# Import du nouveau composant personnalisé à la place du DataTable
from dash_apps.components.custom_users_table import render_custom_users_table
from dash_apps.components.user_profile import render_user_profile
from dash_apps.components.user_stats import render_user_stats
from dash_apps.components.user_trips import render_user_trips
from dash_apps.repositories.user_repository import UserRepository

def get_uid_from_index(row_index, page_index=0):
    """Convertit un index de ligne en UID d'utilisateur pour pagination côté serveur
    
    Args:
        row_index: L'index de la ligne dans le tableau (0-based)
        page_index: L'index de la page (0-based)
        
    Returns:
        L'UID de l'utilisateur correspondant ou None si non trouvé
    """
    try:
        page_size = Config.USERS_TABLE_PAGE_SIZE
        
        # Récupérer uniquement les données nécessaires pour cette page
        result = UserRepository.get_users_paginated(page_index, page_size)
        users = result.get("users", [])
        
        if not users or row_index >= len(users):
            print(f"Aucun utilisateur trouvé à l'index {row_index} sur la page {page_index}")
            return None
            
        # Utiliser directement l'index relatif à la page
        user = users[row_index]
        uid = user.uid if hasattr(user, "uid") else user.get("uid")
        print(f"UID trouvé pour l'indice {row_index} sur la page {page_index}: {uid}")
        return uid
        
    except Exception as e:
        print(f"Erreur lors de la conversion index -> UID via repository: {str(e)}")
        return None


def get_layout():
    """Génère le layout de la page utilisateurs avec des IDs uniquement pour cette page"""
    return dbc.Container([
    dcc.Location(id="users-url", refresh=False),
    dcc.Store(id="users-pagination-info", data={"page_count": 1, "total_users": 0}),
    dcc.Store(id="users-current-page", storage_type="session", data=1),  # State pour stocker la page courante (1-indexed)
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




# Note: Le store users-page-store n'est plus utilisé pour stocker tous les utilisateurs
# car nous utilisons maintenant un chargement à la demande page par page

@callback(
    Output("users-current-page", "data"),
    Input("refresh-users-btn", "n_clicks"),
    State("users-current-page", "data"),
    prevent_initial_call=False
)
def reset_to_first_page_on_refresh(n_clicks, current_page):
    """Réinitialise à la première page lors d'un rafraîchissement explicite"""
    # Si c'est le chargement initial (n_clicks=None), conserver la page actuelle
    if n_clicks is None:
        return current_page if current_page else 1
    # Sinon, revenir à la première page
    return 1


@callback( 
    Output("refresh-users-message", "children"),
    Input("refresh-users-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_refresh_users_message(n_clicks):
    return dbc.Alert("Données utilisateurs rafraîchies!", color="success", dismissable=True)

@callback(
    Output("main-users-content", "children"),
    Input("users-current-page", "data"),
    State("selected-user-state", "data")
)
def render_users_table_callback(current_page, selected_user):
    """Callback qui gère uniquement le rendu de la table des utilisateurs avec pagination à la demande"""
    print(f"\n[DEBUG] Rendu table utilisateurs, page={current_page}, selected_user={selected_user}")
    
    # Configuration pagination
    page_size = Config.USERS_TABLE_PAGE_SIZE
    
    # Si la page n'est pas spécifiée, utiliser la page 1 par défaut
    if not isinstance(current_page, (int, float)):
        current_page = 1  # Défaut à 1 (pagination commence à 1)
    
    # Convertir la page en index 0-based pour l'API
    page_index = current_page - 1 if current_page > 0 else 0
    
    # Récupérer uniquement les utilisateurs de la page courante (pagination côté serveur)
    result = UserRepository.get_users_paginated(page_index, page_size)
    users = result.get("users", [])
    total_users = result.get("total_count", 0)
    
    # Calculer le nombre total de pages
    page_count = (total_users - 1) // page_size + 1 if total_users > 0 else 1
    
    # Si aucun utilisateur n'est disponible
    if not users:
        # Utiliser notre composant personnalisé au lieu du DataTable
        table = render_custom_users_table(
            [], 
            current_page=current_page,  # 1-indexed pour notre composant personnalisé
            total_users=0, 
            selected_uid=None
        )
        return table, []
    
    # Convertir les utilisateurs en dictionnaires pour le DataFrame
    users_data = [u.model_dump() if hasattr(u, "model_dump") else u for u in users]
    users_df = pd.DataFrame(users_data)
    
    # Rendu de la table avec notre composant personnalisé
    table = render_custom_users_table(
        users, 
        current_page=current_page,  # 1-indexed pour notre composant personnalisé
        total_users=total_users,
        selected_uid=selected_user
    )

    # Ne retourner que le tableau
    return table

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


# Callback spécifique pour gérer la sélection manuelle
@callback(
    Output("selected-user-from-table", "data"),
    Input("users-table", "selected_rows"),
    Input("users-table", "page_current"),  # Page actuelle du tableau (0-indexed)
    prevent_initial_call=True
)
def handle_manual_selection(selected_rows, page_current):
    """Callback qui gère la sélection d'un utilisateur manuellement dans le tableau"""
    print(f"selected_rows: {selected_rows}, page_current: {page_current}")
    
    # Si pas de sélection
    if not selected_rows:
        return None
    
    # Utiliser la fonction utilitaire pour convertir l'indice en UID
    try:
        idx = selected_rows[0]
        page_index = page_current if page_current is not None else 0
        uid = get_uid_from_index(idx, page_index)
        return uid
    except Exception as e:
        print(f"Erreur lors de la sélection manuelle: {str(e)}")
        return None

# Callback pour gérer le changement de page depuis le DataTable
@callback(
    Output("users-current-page", "data", allow_duplicate=True),
    Input("users-table", "page_current"),
    State("users-current-page", "data"),
    prevent_initial_call=True
)
def handle_page_change(page_current, current_page):
    """Gère le changement de page depuis le DataTable"""
    print(f"[DEBUG] Changement de page depuis DataTable: page_current={page_current}")
    # page_current est 0-indexed, mais nous stockons les pages en 1-indexed
    if page_current is not None:
        return page_current + 1
    return current_page

# Callback spécifique pour gérer la sélection par URL
@callback(
    Output("selected-user-from-url", "data"),
    Output("users-current-page", "data", allow_duplicate=True),  # allow_duplicate=True pour éviter le conflit
    Input("users-url", "search"),
    prevent_initial_call=True
)
def handle_url_selection(url_search):
    """Callback qui gère la sélection d'un utilisateur par paramètre URL"""
    import urllib.parse
    
    # Si pas de recherche URL
    if not url_search:
        return None, 1  # Page 1 par défaut
        
    # Recherche d'un paramètre uid dans l'URL
    params = urllib.parse.parse_qs(url_search.lstrip('?'))
    uid_list = params.get('uid')
    if not uid_list:
        return None, 1  # Page 1 par défaut
        
    uid_from_url = uid_list[0]
    
    # Vérifier si l'utilisateur existe
    user = UserRepository.get_user_by_id(uid_from_url)
    if not user:
        print(f"Utilisateur {uid_from_url} non trouvé dans la base de données")
        return None, 1
    
    # Déterminer la position de l'utilisateur pour trouver sa page
    position = UserRepository.get_user_position(uid_from_url)
    if position is not None:
        page_size = Config.USERS_TABLE_PAGE_SIZE
        # Calculer la page (1-indexed) où se trouve l'utilisateur
        page_number = (position // page_size) + 1
        print(f"Utilisateur {uid_from_url} trouvé à la position {position}, page {page_number}")
        return uid_from_url, page_number
    
    # Fallback si la position n'a pas été trouvée
    return uid_from_url, 1


# Note: Le callback calculate_page_current a été supprimé car cette fonctionnalité est 
# maintenant gérée directement par handle_url_selection qui utilise UserRepository.get_user_position()

layout = get_layout()


@callback(
    Output("selected-user-state", "data"),
    Input("selected-user-from-table", "data"),
    Input("selected-user-from-url", "data"),
    prevent_initial_call=False
)
def consolidate_user_selection(table_selection, url_selection):
    """Callback qui détermine l'utilisateur sélectionné en fonction du dernier changement
    Sans priorité fixe, c'est la dernière sélection qui a déclenché le callback qui est retenue
    """
    print("[DEBUG] consolidate_user_selection")
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
    else:
        # Fallback, priorité à URL puis table
        selected_uid = url_selection if url_selection is not None else table_selection
        print(f"Autre cas, utilisation valeur existante: {selected_uid}")
    
    # Si on a un UID, on récupère l'utilisateur directement depuis le repository
    if selected_uid:
        user = UserRepository.get_user_by_id(selected_uid)
        if user:
            print(f"Utilisateur trouvé pour UID {selected_uid}")
            return {"uid": selected_uid}
        else:
            print(f"Aucun utilisateur trouvé pour UID {selected_uid}")
    
    return None