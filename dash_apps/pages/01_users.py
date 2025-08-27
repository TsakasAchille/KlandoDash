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
    #dcc.Store(id="users-pagination-info", data={"page_count": 1, "total_users": 0}),
    dcc.Store(id="users-current-page", storage_type="session", data=1),  # State pour stocker la page courante (persistant)
    dcc.Store(id="selected-user-uid", storage_type="session", data=None, clear_data=False),  # Store pour l'UID de l'utilisateur sélectionné (persistant)
    dcc.Store(id="url-parameters", storage_type="memory", data=None),  # Store temporaire pour les paramètres d'URL
    dcc.Store(id="selected-user-from-url", storage_type="memory", data=None),  # State pour la sélection depuis l'URL
    dcc.Store(id="selected-user-from-table", storage_type="memory", data=None),  # State pour la sélection manuelle
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

"""
@callback(
    Output("users-pagination-info", "data"),
    Input("refresh-users-btn", "n_clicks"),
    prevent_initial_call=False
)
def calculate_pagination_info(n_clicks):
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

"""


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
    Input("selected-user-uid", "data"),  # Transformé en Input au lieu de State
    prevent_initial_call=True  # Permettre l'exécution initiale
)
def render_users_table_callback(current_page, selected_user):
    from dash import ctx, no_update
    print("\n[DEBUG] render_users_table_callback")
    print("current_page", current_page)
    print("selected_user", selected_user)
    
    # Variable pour savoir si on doit mettre à jour la page
    new_page = current_page
    triggered_by_user_selection = ctx.triggered_id == "selected-user-uid"
    
    # Si déclenchement par sélection d'utilisateur, déterminer sur quelle page il se trouve
    if triggered_by_user_selection and selected_user:
        uid = selected_user.get("uid") if isinstance(selected_user, dict) else selected_user
        if uid:
            # Appeler notre fonction pour trouver sur quelle page se trouve l'utilisateur
            page_index = find_user_page_index(uid, Config.USERS_TABLE_PAGE_SIZE)
        
        if page_index is not None:
            # Convertir en 1-indexed pour l'interface
            new_page = page_index + 1
            print(f"L'utilisateur {uid} se trouve sur la page {new_page}")
            
            # Si différent de la page actuelle, mettre à jour
            if new_page != current_page:
                current_page = new_page
                print(f"Ajustement de la page à {current_page} pour montrer l'utilisateur sélectionné")
    
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

    # Retourner uniquement le tableau
    #return table

    
    # Fetch user data if we have a selected user
    user = None
    if selected_uid_value:
        # Get complete user data from repository using the selected UID
        user = UserRepository.get_user_by_id(selected_uid_value)
        
        # Rendu des panneaux seulement si un utilisateur est sélectionné
        if user:
            # Convertir l'objet UserSchema en dictionnaire
            if hasattr(user, "model_dump"):
                # Pour Pydantic v2
                user_dict = user.model_dump()
            elif hasattr(user, "dict"):
                # Pour Pydantic v1
                user_dict = user.dict()
            else:
                # Fallback
                user_dict = {k: getattr(user, k) for k in dir(user) if not k.startswith('_') and not callable(getattr(user, k))}
                
            # Garantir que toutes les valeurs utilisées dans les templates existent
            # Vérifier que toutes les clés necessaires existent avec des valeurs par défaut
            defaults = {
                "rating": 0, 
                "rating_count": 0,
                "display_name": "",
                "name": "",
                "first_name": "",
                "email": "",
                "phone": "", 
                "phone_number": "",
                "birth": "",
                "bio": "",
                "gender": "",
                "role_preference": "",
                "created_time": "", 
                "updated_at": ""
            }
            
            # Appliquer les valeurs par défaut
            for key, default_value in defaults.items():
                if key not in user_dict or user_dict[key] is None:
                    user_dict[key] = default_value
            
            # Afficher les informations pour debugging
            print(f"Debug user_dict['rating']: {user_dict['rating']}, type: {type(user_dict['rating'])}")
            
            details = render_user_profile(user_dict)
            stats = render_user_stats(user_dict)
            trips = render_user_trips(user_dict)
            return table, details, stats, trips
    
    # Return empty panels if no user selected or user not found
    return table, html.Div(), html.Div(), html.Div()


# Callback unique pour gérer la sélection utilisateur depuis la table ou l'URL
# Callback pour la sélection depuis l'URL
@callback(
    Output("selected-user-uid", "data", allow_duplicate=True),
    Input("users-url", "search"),
    prevent_initial_call='initial_duplicate'
)
def handle_url_selection(url_search):
    from dash import ctx
    import urllib.parse
    
    # Si aucun paramètre d'URL
    """
    if not url_search:
        print("[DEBUG-URL] Pas de paramètres URL")
        return dash.no_update
    """
    print(f"[DEBUG-URL] URL search: {url_search}")
    params = urllib.parse.parse_qs(url_search.lstrip('?'))
    uid_list = params.get('uid')
    
    if uid_list:
        uid = uid_list[0]
        selected_user = {"uid": uid}
        print(f"[DEBUG-URL] Sélection depuis URL: {selected_user}")
        # Vérifier que la valeur est correctement renvoyée
        print(f"[DEBUG-URL] Type de retour: {type(selected_user)}")
        return selected_user
    
    print("[DEBUG-URL] Pas de paramètre uid dans l'URL")
    #return dash.no_update

# Callback pour la sélection depuis le tableau
@callback(
    Output("selected-user-uid", "data", allow_duplicate=True),
    Input("selected-user-from-table", "data"),
    prevent_initial_call=True
)
def handle_table_selection(table_selection):
    if table_selection is None:
        return dash.no_update
        
    print(f"Sélection depuis tableau: {table_selection}")
    return table_selection

layout = get_layout()
