import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask import session
from dash_apps.utils.admin_db_rest import is_admin

# Importer les callbacks admin
from dash_apps.callbacks import admin_callbacks

# L'enregistrement se fera dans app_factory après la création de l'app

# Préfixe pour éviter les conflits de callbacks avec d'autres pages
ADMIN_PREFIX = 'adm-'

# Layout de la page d'administration - accès restreint aux admins
def serve_layout():
    user_email = session.get('user_email', None)
    
    # Debug: afficher les informations de session
    print(f"[ADMIN_DEBUG] user_email: {user_email}")
    print(f"[ADMIN_DEBUG] session keys: {list(session.keys())}")
    print(f"[ADMIN_DEBUG] is_admin from session: {session.get('is_admin', False)}")
    
    try:
        admin_from_db = is_admin(user_email)
        print(f"[ADMIN_DEBUG] is_admin from DB: {admin_from_db}")
        is_admin_flag = bool(admin_from_db or session.get('is_admin', False))
    except Exception as e:
        print(f"[ADMIN_DEBUG] Exception in is_admin: {e}")
        is_admin_flag = bool(session.get('is_admin', False))
    
    print(f"[ADMIN_DEBUG] Final is_admin_flag: {is_admin_flag}")
    
    if not is_admin_flag:
        return dbc.Container([
            html.H2("Accès refusé", style={"marginTop": "20px"}),
            dbc.Alert([
                "Vous n'êtes pas autorisé à accéder à cette page. Seuls les administrateurs peuvent y accéder.",
                html.Br(),
                html.Small(f"Email de session: {user_email}", className="text-muted")
            ], color="danger")
        ], fluid=True)
    else:
        return dbc.Container([
            html.H2("Gestion des utilisateurs autorisés", style={"marginTop": "20px"}),
            html.P("Cette page permet aux administrateurs de gérer les utilisateurs autorisés.", className="text-muted"),
            # Stores pour les données d'état
            dcc.Store(id=f"{ADMIN_PREFIX}auth-store"),
            dcc.Store(id=f"{ADMIN_PREFIX}users-store"),
            
            # Éléments invisibles pour éviter les dépendances circulaires
            html.Div([
                html.Button(id=f"{ADMIN_PREFIX}refresh-btn", style={"display": "none"}),
                html.Div(id=f"{ADMIN_PREFIX}add-user-result", style={"display": "none"}),
                dbc.Input(id=f"{ADMIN_PREFIX}add-user-form", type="hidden"),
                dbc.Input(id=f"{ADMIN_PREFIX}new-email", type="hidden"),
                dbc.Input(id=f"{ADMIN_PREFIX}new-role", type="hidden"),
                html.Div(id=f"{ADMIN_PREFIX}user-management-content"),
            html.Div(id=f"{ADMIN_PREFIX}user-details-content"),
            html.Div(id=f"{ADMIN_PREFIX}add-user-content"),
            html.Div(id=f"{ADMIN_PREFIX}edit-user-content"),
            html.Div(id=f"{ADMIN_PREFIX}delete-user-content"),
            ], style={"display": "none"}),
            
            # Conteneur principal - sera rempli par le callback de rendu du template
            html.Div(id=f"{ADMIN_PREFIX}main-container")
        ], fluid=True)

# Export layout using the same pattern as driver_validation
layout = serve_layout
