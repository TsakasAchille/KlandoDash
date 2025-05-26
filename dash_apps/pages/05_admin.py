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
    
    # Éléments invisibles pour éviter les dépendances circulaires
    html.Div([
        html.Button(id=f"{ADMIN_PREFIX}refresh-btn", style={"display": "none"}),
        html.Div(id=f"{ADMIN_PREFIX}add-user-result", style={"display": "none"}),
        dbc.Input(id=f"{ADMIN_PREFIX}add-user-form", type="hidden"),
        dbc.Input(id=f"{ADMIN_PREFIX}new-email", type="hidden"),
        dbc.Input(id=f"{ADMIN_PREFIX}new-role", type="hidden"),
        dbc.Input(id=f"{ADMIN_PREFIX}new-notes", type="hidden")
    ], style={"display": "none"}),
    
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
     Input(f"{ADMIN_PREFIX}add-user-result", "children"),
     Input(f"{ADMIN_PREFIX}auth-store", "data")]  # Ajouter ce trigger pour charger au démarrage
)
def load_authorized_users(refresh_clicks, add_result, auth_data):
    # Cette fonction est appelée quand:
    # 1. On clique sur le bouton refresh
    # 2. Après avoir ajouté un utilisateur
    # 3. Au chargement initial de la page (via auth-store)
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
    
    # Convertir les templates HTML en composants Dash
    # Créer une div pour chaque section
    
    # En-tête
    header = html.Div([
        html.H2("Gestion des utilisateurs autorisés", className="mb-4"),
        html.Hr(),
    ])
    
    # Bouton de rafraîchissement
    refresh_btn = html.Button(
        [html.I(className="fas fa-sync-alt me-2"), "Rafraîchir"],
        id=f"{ADMIN_PREFIX}refresh-btn",
        className="btn btn-primary mb-3"
    )
    
    # Formulaire d'ajout d'utilisateur
    add_user_form = html.Div([
        html.H4("Ajouter un nouvel utilisateur", className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Email", html_for=f"{ADMIN_PREFIX}new-email"),
                dbc.Input(type="email", id=f"{ADMIN_PREFIX}new-email", placeholder="email@klando-sn.com"),
            ], width=4),
            dbc.Col([
                dbc.Label("Rôle", html_for=f"{ADMIN_PREFIX}new-role"),
                dbc.Select(
                    id=f"{ADMIN_PREFIX}new-role",
                    options=[
                        {"label": "Utilisateur", "value": "user"},
                        {"label": "Administrateur", "value": "admin"}
                    ],
                    value="user"
                ),
            ], width=4),
            dbc.Col([
                dbc.Label("Notes", html_for=f"{ADMIN_PREFIX}new-notes"),
                dbc.Input(type="text", id=f"{ADMIN_PREFIX}new-notes", placeholder="Notes (optionnel)"),
            ], width=4),
        ]),
        dbc.Button(
            [html.I(className="fas fa-plus-circle me-2"), "Ajouter"],
            id=f"{ADMIN_PREFIX}add-user-btn",
            color="success",
            className="mt-3"
        ),
        # Input hidden pour la soumission du formulaire
        dbc.Input(id=f"{ADMIN_PREFIX}add-user-form", type="hidden"),
        html.Div(id=f"{ADMIN_PREFIX}add-user-result")
    ], className="mb-4 p-3 border rounded")
    
    # Tableau des utilisateurs
    if users:
        user_rows = []
        for user in users:
            active_badge = html.Span("Actif", className="badge bg-success") if user.get('active') else html.Span("Inactif", className="badge bg-danger")
            role_badge = html.Span("Admin", className="badge bg-primary") if user.get('role') == 'admin' else html.Span("Utilisateur", className="badge bg-secondary")
            
            # Actions pour chaque utilisateur
            actions = html.Div([
                dbc.ButtonGroup([
                    dbc.Button(
                        html.I(className="fas fa-toggle-on" if not user.get('active') else "fas fa-toggle-off"),
                        id={"type": f"{ADMIN_PREFIX}toggle-user", "index": user.get('email')},
                        color="success" if not user.get('active') else "danger",
                        className="btn-sm me-1",
                        title="Activer" if not user.get('active') else "Désactiver"
                    ),
                    dbc.Button(
                        html.I(className="fas fa-user-shield"),
                        id={"type": f"{ADMIN_PREFIX}toggle-role", "index": user.get('email')},
                        color="primary",
                        className="btn-sm me-1",
                        title="Changer le rôle"
                    ),
                    dbc.Button(
                        html.I(className="fas fa-trash"),
                        id={"type": f"{ADMIN_PREFIX}delete-user", "index": user.get('email')},
                        color="danger",
                        className="btn-sm",
                        title="Supprimer"
                    ),
                ])
            ])
            
            # Ligne pour chaque utilisateur
            user_row = html.Tr([
                html.Td(user.get('email')),
                html.Td(active_badge),
                html.Td(role_badge),
                html.Td(user.get('added_at', '-')),
                html.Td(user.get('updated_at', '-')),
                html.Td(user.get('added_by', '-')),
                html.Td(user.get('notes', '-')),
                html.Td(actions)
            ])
            user_rows.append(user_row)
        
        # En-tête du tableau
        table_header = html.Thead(html.Tr([
            html.Th("Email"),
            html.Th("Statut"),
            html.Th("Rôle"),
            html.Th("Ajouté le"),
            html.Th("Mis à jour le"),
            html.Th("Ajouté par"),
            html.Th("Notes"),
            html.Th("Actions")
        ]))
        
        # Corps du tableau
        table_body = html.Tbody(user_rows)
        
        # Tableau complet
        users_table = html.Div([
            html.H4("Utilisateurs autorisés", className="mb-3"),
            dbc.Table([
                table_header,
                table_body
            ], striped=True, bordered=True, hover=True, responsive=True)
        ], className="mt-4")
    else:
        users_table = html.Div([
            html.H4("Utilisateurs autorisés", className="mb-3"),
            html.P("Aucun utilisateur autorisé trouvé.")
        ], className="mt-4")
    
    # Assembler tous les composants
    return html.Div([
        header,
        refresh_btn,
        add_user_form,
        users_table
    ], className="p-4")

# Callback pour ajouter un nouvel utilisateur
@callback(
    Output(f"{ADMIN_PREFIX}add-user-result", "children"),
    Input(f"{ADMIN_PREFIX}add-user-btn", "n_clicks"),
    [State(f"{ADMIN_PREFIX}new-email", "value"),
     State(f"{ADMIN_PREFIX}new-role", "value"),
     State(f"{ADMIN_PREFIX}new-notes", "value"),
     State(f"{ADMIN_PREFIX}auth-store", "data")],
    prevent_initial_call=True
)
def add_new_user(n_clicks, email, role, notes, auth_data):
    if not n_clicks:
        return no_update
        
    # Vérifier que l'email est valide
    if not email or '@' not in email:
        return dbc.Alert("Veuillez fournir un email valide", color="danger", dismissable=True, duration=4000)
    
    # Récupérer l'email de l'administrateur 
    admin_email = auth_data.get('user_email', 'unknown')
    
    # Ajouter l'utilisateur à la base de données
    try:
        result = add_authorized_user(email, role, admin_email, notes)
        if result:
            return dbc.Alert(
                f"Utilisateur {email} ajouté avec succès avec le rôle {role}", 
                color="success", 
                dismissable=True,
                duration=4000
            )
        else:
            return dbc.Alert("Erreur lors de l'ajout de l'utilisateur", color="danger", dismissable=True)
    except Exception as e:
        return dbc.Alert(f"Erreur: {str(e)}", color="danger", dismissable=True)

# Callback pour activer/désactiver un utilisateur
@callback(
    Output(f"{ADMIN_PREFIX}refresh-btn", "n_clicks", allow_duplicate=True),
    Input({"type": f"{ADMIN_PREFIX}toggle-user", "index": ALL}, "n_clicks"),
    State(f"{ADMIN_PREFIX}auth-store", "data"),
    prevent_initial_call=True
)
def toggle_user_status(n_clicks, auth_data):
    # Identifier quel bouton a été cliqué
    if not n_clicks or not any(n_clicks):
        return no_update
        
    # Récupérer l'email de l'administrateur 
    admin_email = auth_data.get('user_email', 'unknown')
    
    # Récupérer l'email de l'utilisateur à modifier
    triggered_id = ctx.triggered_id
    if triggered_id and 'index' in triggered_id:
        user_email = triggered_id['index']
        
        # Récupérer l'utilisateur pour connaître son statut actuel
        users = get_all_authorized_users()
        user = next((u for u in users if u.get('email') == user_email), None)
        
        if user:
            # Inverser le statut actuel
            new_status = not user.get('active', True)
            result = update_user_status(user_email, new_status, admin_email)
            
            # Forcer le rafraîchissement en simulant un clic sur le bouton refresh
            return 1
            
    return no_update

# Callback pour changer le rôle d'un utilisateur
@callback(
    Output(f"{ADMIN_PREFIX}refresh-btn", "n_clicks", allow_duplicate=True),
    Input({"type": f"{ADMIN_PREFIX}toggle-role", "index": ALL}, "n_clicks"),
    State(f"{ADMIN_PREFIX}auth-store", "data"),
    prevent_initial_call=True
)
def toggle_user_role(n_clicks, auth_data):
    # Identifier quel bouton a été cliqué
    if not n_clicks or not any(n_clicks):
        return no_update
        
    # Récupérer l'email de l'administrateur 
    admin_email = auth_data.get('user_email', 'unknown')
    
    # Récupérer l'email de l'utilisateur à modifier
    triggered_id = ctx.triggered_id
    if triggered_id and 'index' in triggered_id:
        user_email = triggered_id['index']
        
        # Récupérer l'utilisateur pour connaître son rôle actuel
        users = get_all_authorized_users()
        user = next((u for u in users if u.get('email') == user_email), None)
        
        if user:
            # Inverser le rôle actuel (admin <-> user)
            current_role = user.get('role', 'user')
            new_role = 'user' if current_role == 'admin' else 'admin'
            result = update_user_role(user_email, new_role, admin_email)
            
            # Forcer le rafraîchissement en simulant un clic sur le bouton refresh
            return 1
            
    return no_update

# Callback pour supprimer un utilisateur
@callback(
    Output(f"{ADMIN_PREFIX}refresh-btn", "n_clicks", allow_duplicate=True),
    Input({"type": f"{ADMIN_PREFIX}delete-user", "index": ALL}, "n_clicks"),
    State(f"{ADMIN_PREFIX}auth-store", "data"),
    prevent_initial_call=True
)
def delete_user_callback(n_clicks, auth_data):
    # Identifier quel bouton a été cliqué
    if not n_clicks or not any(n_clicks):
        return no_update
        
    # Récupérer l'email de l'administrateur 
    admin_email = auth_data.get('user_email', 'unknown')
    
    # Récupérer l'email de l'utilisateur à supprimer
    triggered_id = ctx.triggered_id
    if triggered_id and 'index' in triggered_id:
        user_email = triggered_id['index']
        
        # Ne pas permettre à un admin de se supprimer lui-même
        if user_email == admin_email:
            return no_update
            
        # Supprimer l'utilisateur
        result = delete_user(user_email, admin_email)
        
        # Forcer le rafraîchissement en simulant un clic sur le bouton refresh
        return 1
        
    return no_update