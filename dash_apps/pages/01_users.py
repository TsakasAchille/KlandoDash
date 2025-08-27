import math
import json
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback, Input, Output, State
from dash.exceptions import PreventUpdate
from dash_apps.config import Config
# Import du nouveau composant personnalisé à la place du DataTable
from dash_apps.components.custom_users_table import render_custom_users_table
from dash_apps.components.user_profile import render_user_profile
from dash_apps.components.user_stats import render_user_stats
from dash_apps.components.user_trips import render_user_trips
from dash_apps.repositories.user_repository import UserRepository
"""
def get_uid_from_index(row_index, page_index=0):

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
"""

def get_layout():
    """Génère le layout de la page utilisateurs avec des IDs uniquement pour cette page"""
    return dbc.Container([
    dcc.Location(id="users-url", refresh=False),
    dcc.Store(id="users-pagination-info", data={"page_count": 1, "total_users": 0}),
    dcc.Store(id="users-current-page", storage_type="session", data=1),  # State pour stocker la page courante (persistant)
    dcc.Store(id="selected-user-uid", storage_type="session", data=None),  # Store pour l'UID de l'utilisateur sélectionné (persistant)
    dcc.Store(id="selected-user-from-url", storage_type="memory", data=None),  # State pour la sélection depuis l'URL
    dcc.Store(id="selected-user-from-table", storage_type="memory", data=None),  # State pour la sélection manuelle
    # Flags pour indiquer quelle source de sélection est active
  
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
"""
@callback(
    Output("users-current-page", "data"),
    Input("refresh-users-btn", "n_clicks"),
    State("users-current-page", "data"),
    prevent_initial_call=False
)
def reset_to_first_page_on_refresh(n_clicks, current_page):
    # Si c'est le chargement initial (n_clicks=None), conserver la page actuelle
    if n_clicks is None:
        return current_page if current_page else 1
    # Sinon, revenir à la première page
    return 1
"""

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
    State("selected-user-uid", "data")
)
def render_users_table_callback(current_page, selected_user):
    #print(f"\n[DEBUG] Rendu table utilisateurs, page={current_page}, selected_user={selected_user}")
    print("\n[DEBUG] render_users_table_callback")
    print("current_page", current_page)
    print("selected_user", selected_user)
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
    
    # Debug de la valeur selected_user
   # print(f"\n[DEBUG-TABLE] Type de selected_user: {type(selected_user)}, Valeur: {selected_user}")
    
    # Déterminer la valeur à passer à selected_uid
    if isinstance(selected_user, dict) and "uid" in selected_user:
        selected_uid_value = selected_user["uid"]
    else:
        selected_uid_value = selected_user
    
   # print(f"\n[DEBUG-TABLE] Valeur envoyée à selected_uid: {selected_uid_value}")
    
    # Rendu de la table avec notre composant personnalisé
    table = render_custom_users_table(
        users, 
        current_page=current_page,  # 1-indexed pour notre composant personnalisé
        total_users=total_users,
        selected_uid=selected_uid_value
    )

    # Ne retourner que le tableau
    return table

    
@callback(
    Output("user-details-panel", "children"),
    Output("user-stats-panel", "children"),
    Output("user-trips-panel", "children"),
    Input("selected-user-uid", "data"),
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


# Callback unique pour gérer la sélection utilisateur depuis la table ou l'URL
@callback(
    Output("selected-user-uid", "data"),
    [Input("users-url", "search"),
     Input("selected-user-from-table", "data")],
)
def handle_user_selection(url_search, table_selection):
    from dash import ctx
    import urllib.parse
    
    # Utiliser ctx.triggered pour déterminer quel input a déclenché le callback (méthode moderne)
    # Plus fiable que callback_context.triggered
    print(f"\n[DEBUG] Triggered: {ctx.triggered_id}")
    
    # Si déclencheur vide, rien à faire
    if not ctx.triggered_id:
        return dash.no_update
    
    
    # Si déclenché par l'URL, vérifier et extraire l'uid
    if ctx.triggered_id == "users-url" and url_search:
        print(f"URL search: {url_search}")
        params = urllib.parse.parse_qs(url_search.lstrip('?'))
        uid_list = params.get('uid')
        
        if uid_list:
            uid = uid_list[0]
            selected_user = {"uid": uid}
            print(f"Sélection depuis URL: {selected_user}")
            return selected_user
    
    # Si déclenché par le tableau et il y a une sélection valide
    if ctx.triggered_id == "selected-user-from-table" and table_selection is not None:
        print(f"Sélection depuis tableau: {table_selection}")
        return table_selection
    
    return dash.no_update

layout = get_layout()
