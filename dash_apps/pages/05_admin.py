from dash import html, dcc, callback, Input, Output, State, ctx, ALL, no_update
import dash_bootstrap_components as dbc
from flask import session, render_template_string
from dash_apps.utils.admin_db import get_all_authorized_users, add_authorized_user, update_user_status, update_user_role, is_admin, delete_user
import pandas as pd
from datetime import datetime
import os

# Définir le chemin vers les templates
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'admin')

# Charger les templates
def load_template(template_name):
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()

# Préfixe pour éviter les conflits de callbacks avec d'autres pages
ADMIN_PREFIX = 'adm-'

# Charger les templates
USER_FORM_TEMPLATE = load_template('user_form.html')
USER_TABLE_TEMPLATE = load_template('user_table.html')
ADMIN_JS = load_template('admin.js')
ADMIN_LAYOUT = load_template('admin_layout.html')

# Layout de la page d'administration - accès restreint aux admins
layout = html.Div([
    # Stores pour les données d'état
    dcc.Store(id=f"{ADMIN_PREFIX}auth-store"),
    dcc.Store(id=f"{ADMIN_PREFIX}users-store"),
    
    # Conteneur principal - sera rempli par le callback de rendu du template
    html.Div(id=f"{ADMIN_PREFIX}main-container")
])

# Vérifier si l'utilisateur est autorisé à accéder à la page admin
@callback(
    Output(f"{ADMIN_PREFIX}auth-store", "data"),
    Input(f"{ADMIN_PREFIX}auth-store", "id")
)
def check_admin_auth(_):
    # Récupérer l'email de l'utilisateur depuis la session
    user_email = session.get('user_email', None)
    admin_status = is_admin(user_email)
    return {"is_admin": admin_status, "user_email": user_email}

# Charger les utilisateurs autorisés
@callback(
    Output(f"{ADMIN_PREFIX}users-store", "data"),
    [Input(f"{ADMIN_PREFIX}refresh-btn", "n_clicks"),
     Input(f"{ADMIN_PREFIX}add-user-result", "children")]
)
def load_authorized_users(refresh_clicks, add_result):
    # Cette fonction est appelée quand on clique sur le bouton refresh
    # ou après avoir ajouté un utilisateur
    users = get_all_authorized_users()
    return users

# Rendu principal de la page d'administration
@callback(
    Output(f"{ADMIN_PREFIX}main-container", "children"),
    [Input(f"{ADMIN_PREFIX}auth-store", "data"),
     Input(f"{ADMIN_PREFIX}users-store", "data")]
)
def render_admin_page(auth_data, users_data):
    # Vérifier que l'utilisateur est admin
    if not auth_data or not auth_data.get("is_admin", False):
        return dbc.Alert(
            "Vous n'êtes pas autorisé à accéder à cette page. Seuls les administrateurs peuvent y accéder.",
            color="danger",
            className="mt-3 mb-3"
        )
    
    # Formater les données des utilisateurs pour le template
    users = []
    if users_data:
        df = pd.DataFrame(users_data)
        # Formater les dates pour l'affichage
        for date_col in ['added_at', 'updated_at']:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col]).dt.strftime("%d/%m/%Y %H:%M")
        
        # Convertir en liste de dictionnaires pour le template
        users = df.to_dict('records')
    
    # Rendre les templates
    user_form_html = render_template_string(USER_FORM_TEMPLATE)
    user_table_html = render_template_string(USER_TABLE_TEMPLATE, users=users)
    
    # Rendre le template principal avec les sous-templates
    admin_html = render_template_string(
        ADMIN_LAYOUT,
        user_form=user_form_html,
        user_table=user_table_html,
        admin_js=ADMIN_JS
    )
    
    return html.Div([
        html.Div(dangerouslySetInnerHTML=dict(
            __html=admin_html
        ))
    ])

# Callback pour ajouter un nouvel utilisateur via l'API
@callback(
    Output(f"{ADMIN_PREFIX}add-user-result", "children"),
    Input(f"{ADMIN_PREFIX}add-user-form", "n_submit"),
    [State(f"{ADMIN_PREFIX}new-email", "value"),
     State(f"{ADMIN_PREFIX}new-role", "value"),
     State(f"{ADMIN_PREFIX}new-notes", "value"),
     State(f"{ADMIN_PREFIX}auth-store", "data")],
    prevent_initial_call=True
)
def add_new_user(n_submit, email, role, notes, auth_data):
    # Ce callback ne sera pas utilisé directement - c'est l'API qui sera appelée par le JavaScript
    # Il est gardé ici pour référence et compatibilité avec le code existant
    return no_update