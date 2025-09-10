"""Callbacks pour la page d'administration"""

from dash import callback, Input, Output, State, ctx, ALL, no_update, html, dcc
from dash_apps.pages.admin.admin_templates import ADMIN_LAYOUT, USER_FORM_TEMPLATE, USER_TABLE_TEMPLATE, ADMIN_JS
import dash_bootstrap_components as dbc
from flask import session, render_template_string
from dash_apps.utils.admin_db_rest import (
    get_all_authorized_users, add_authorized_user, update_user_status,
    update_user_role, is_admin, delete_user
)
import pandas as pd
from datetime import datetime

# Préfixe pour éviter les conflits de callbacks avec d'autres pages
ADMIN_PREFIX = 'adm-'

def register_admin_callbacks(app):
    """Enregistre tous les callbacks de la page d'administration"""
    
    # Vérifier si l'utilisateur est autorisé à accéder à la page admin
    @app.callback(
        Output(f"{ADMIN_PREFIX}auth-store", "data", allow_duplicate=True),
        Input(f"{ADMIN_PREFIX}page-loaded", "children"),
        prevent_initial_call=False
    )
    def check_admin_auth(_):
        # Récupérer l'email de l'utilisateur depuis la session
        user_email = session.get('user_email', None)
        admin_status = is_admin(user_email)
        return {"is_admin": admin_status, "user_email": user_email}
    
    # Charger les utilisateurs autorisés
    @app.callback(
        Output(f"{ADMIN_PREFIX}users-store", "data", allow_duplicate=True),
        Input(f"{ADMIN_PREFIX}refresh-button", "n_clicks"),
        Input(f"{ADMIN_PREFIX}add-result", "data"),
        State(f"{ADMIN_PREFIX}auth-store", "data"),
        prevent_initial_call=False
    )
    def load_authorized_users(refresh_clicks, add_result, auth_data):
        if auth_data and auth_data.get("is_admin", False):
            # Charger les utilisateurs depuis la base de données
            users_df = get_all_authorized_users()
            if isinstance(users_df, pd.DataFrame) and not users_df.empty:
                users_df['added_at'] = users_df['added_at'].dt.strftime('%Y-%m-%d %H:%M:%S') if 'added_at' in users_df.columns else ''
                users_df['updated_at'] = users_df['updated_at'].dt.strftime('%Y-%m-%d %H:%M:%S') if 'updated_at' in users_df.columns else ''
                return users_df.to_dict('records')
        return []
    
    # Rendu principal de la page d'administration
    @app.callback(
        Output(f"{ADMIN_PREFIX}content", "children", allow_duplicate=True),
        Input(f"{ADMIN_PREFIX}auth-store", "data"),
        Input(f"{ADMIN_PREFIX}users-store", "data")
    )
    def render_admin_page(auth_data, users_data):
        if not auth_data or not auth_data.get("is_admin", False):
            return dbc.Alert(
                "Vous n'avez pas accès à cette page. Seuls les administrateurs peuvent y accéder.",
                color="danger",
                className="mt-4"
            )
        
        # Préparer les données pour le template
        users = users_data if users_data else []

        # Normaliser les clés attendues par le template Jinja (user_table.html)
        # Le template attend: email, role, active, added_at, updated_at, added_by, notes
        normalized_users = []
        for u in users:
            try:
                # Autoriser à fonctionner avec dict-like (venant de DataFrame.to_dict('records'))
                email = u.get('email') if isinstance(u, dict) else getattr(u, 'email', None)
                role = (u.get('role') if isinstance(u, dict) else getattr(u, 'role', None)) or 'user'
                active = (
                    (u.get('active') if isinstance(u, dict) else getattr(u, 'active', None))
                    if (isinstance(u, dict) and 'active' in u) or (not isinstance(u, dict) and hasattr(u, 'active'))
                    else (u.get('is_active') if isinstance(u, dict) else getattr(u, 'is_active', True))
                )
                added_at = u.get('added_at') if isinstance(u, dict) else getattr(u, 'added_at', '')
                updated_at = u.get('updated_at') if isinstance(u, dict) else getattr(u, 'updated_at', '')
                added_by = u.get('added_by') if isinstance(u, dict) else getattr(u, 'added_by', '')
                notes = u.get('notes') if isinstance(u, dict) else getattr(u, 'notes', '')
            except Exception:
                email = None; role = 'user'; active = True; added_at = updated_at = added_by = notes = ''

            normalized_users.append({
                'email': email or 'N/A',
                'role': role,
                'active': bool(active),
                'added_at': added_at or '',
                'updated_at': updated_at or '',
                'added_by': added_by or '',
                'notes': notes or ''
            })

        # Pré-rendre les sous-templates puis injecter dans le layout principal
        user_form_html = render_template_string(USER_FORM_TEMPLATE, admin_prefix=ADMIN_PREFIX)
        user_table_html = render_template_string(USER_TABLE_TEMPLATE, users=normalized_users, admin_prefix=ADMIN_PREFIX)

        admin_layout_html = render_template_string(
            ADMIN_LAYOUT,
            user_form=user_form_html,
            user_table=user_table_html,
            admin_js=ADMIN_JS,
            admin_prefix=ADMIN_PREFIX
        )
        
        return html.Div([
            dcc.Store(id=f"{ADMIN_PREFIX}add-result"),
            html.Div([
                html.Div([
                    html.H1("Administration", className="mb-4"),
                    html.Div([
                        html.Button(
                            html.I(className="fas fa-sync-alt"), 
                            id=f"{ADMIN_PREFIX}refresh-button",
                            className="btn btn-outline-primary",
                            title="Rafraîchir la liste"
                        ),
                        html.Span(" "),
                        html.Button(
                            [
                                html.I(className="fas fa-user-plus"),
                                " Ajouter un utilisateur"
                            ],
                            id=f"{ADMIN_PREFIX}add-user-button",
                            className="btn btn-primary",
                            **{'data-bs-toggle': 'modal', 'data-bs-target': '#addUserModal'}
                        )
                    ], className="mb-4 d-flex")
                ], className="col-12")
            ], className="row mb-4"),
            
            # Rendu du layout admin (HTML) dans Dash
            dcc.Markdown(admin_layout_html, dangerously_allow_html=True),
            
            # Modal pour ajouter un utilisateur
            html.Div(
                dbc.Modal([
                    dbc.ModalHeader("Ajouter un utilisateur"),
                    dbc.ModalBody(render_template_string(USER_FORM_TEMPLATE, admin_prefix=ADMIN_PREFIX)),
                    dbc.ModalFooter([
                        html.Button("Annuler", className="btn btn-secondary", **{'data-bs-dismiss': 'modal'}),
                        html.Button(
                            "Ajouter", 
                            id=f"{ADMIN_PREFIX}submit-add-user", 
                            className="btn btn-primary"
                        )
                    ])
                ], id="addUserModal", is_open=False, backdrop="static"),
            ),
            
            # JavaScript pour les interactions côté client
            html.Script(ADMIN_JS),
        ])
    
    # Callback pour ajouter un nouvel utilisateur
    @app.callback(
        Output(f"{ADMIN_PREFIX}add-result", "data", allow_duplicate=True),
        Output(f"{ADMIN_PREFIX}add-user-message", "children", allow_duplicate=True),
        Input(f"{ADMIN_PREFIX}submit-add-user", "n_clicks"),
        State(f"{ADMIN_PREFIX}add-email", "value"),
        State(f"{ADMIN_PREFIX}add-role", "value"),
        State(f"{ADMIN_PREFIX}add-notes", "value"),
        State(f"{ADMIN_PREFIX}auth-store", "data"),
        prevent_initial_call=True
    )
    def add_new_user(n_clicks, email, role, notes, auth_data):
        if not n_clicks or not auth_data or not auth_data.get("is_admin", False):
            return no_update, no_update
        
        if not email or not role:
            return {
                "success": False,
                "timestamp": datetime.now().isoformat()
            }, dbc.Alert("Email et rôle sont requis", color="danger")
        
        # Vérifier que le rôle est valide
        valid_roles = ['admin', 'user', 'viewer']
        if role not in valid_roles:
            return {
                "success": False,
                "timestamp": datetime.now().isoformat()
            }, dbc.Alert(f"Ru00f4le invalide. Les ru00f4les valides sont: {', '.join(valid_roles)}", color="danger")
        
        # Ajouter l'utilisateur
        admin_email = auth_data.get("user_email")
        success, message = add_authorized_user(email, role, admin_email, notes or "")
        
        return {
            "success": success,
            "timestamp": datetime.now().isoformat()
        }, dbc.Alert(message, color="success" if success else "danger")
    
    # Callback pour activer/désactiver un utilisateur
    @app.callback(
        Output(f"{ADMIN_PREFIX}toggle-status-result", "data", allow_duplicate=True),
        Input({"type": f"{ADMIN_PREFIX}toggle-status", "index": ALL}, "n_clicks"),
        State(f"{ADMIN_PREFIX}auth-store", "data"),
        prevent_initial_call=True
    )
    def toggle_user_status(n_clicks, auth_data):
        if not ctx.triggered or not auth_data or not auth_data.get("is_admin", False):
            return no_update
        
        # Récupérer l'ID du bouton cliqué
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        parsed_id = json.loads(triggered_id)
        target_email = parsed_id.get("index")
        
        if not target_email:
            return {"success": False, "message": "Email de l'utilisateur manquant"}
        
        # Inverser le statut (sera géré par l'API)
        admin_email = auth_data.get("user_email")
        
        # Faire une requête AJAX côté client via le script JS
        # Ce callback ne met à jour que le store pour déclencher une actualisation
        return {"target": target_email, "timestamp": datetime.now().isoformat()}
    
    # Callback pour changer le rôle d'un utilisateur
    @app.callback(
        Output(f"{ADMIN_PREFIX}toggle-role-result", "data", allow_duplicate=True),
        Input({"type": f"{ADMIN_PREFIX}toggle-role", "index": ALL}, "n_clicks"),
        State(f"{ADMIN_PREFIX}auth-store", "data"),
        prevent_initial_call=True
    )
    def toggle_user_role(n_clicks, auth_data):
        if not ctx.triggered or not auth_data or not auth_data.get("is_admin", False):
            return no_update
        
        # Récupérer l'ID du bouton cliqué
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        parsed_id = json.loads(triggered_id)
        target_email = parsed_id.get("index")
        
        if not target_email:
            return {"success": False, "message": "Email de l'utilisateur manquant"}
        
        # La logique de changement de rôle sera gérée par le script JS
        # Ce callback ne met à jour que le store pour déclencher une actualisation
        return {"target": target_email, "timestamp": datetime.now().isoformat()}
    
    # Callback pour supprimer un utilisateur
    @app.callback(
        Output(f"{ADMIN_PREFIX}delete-user-result", "data", allow_duplicate=True),
        Input({"type": f"{ADMIN_PREFIX}delete-user", "index": ALL}, "n_clicks"),
        State(f"{ADMIN_PREFIX}auth-store", "data"),
        prevent_initial_call=True
    )
    def delete_user_callback(n_clicks, auth_data):
        if not ctx.triggered or not auth_data or not auth_data.get("is_admin", False):
            return no_update
        
        # Ru00e9cupu00e9rer l'ID du bouton cliquu00e9
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        parsed_id = json.loads(triggered_id)
        target_email = parsed_id.get("index")
        
        if not target_email:
            return {"success": False, "message": "Email de l'utilisateur manquant"}
        
        # La logique de suppression sera gérée par le script JS
        # Ce callback ne met à jour que le store pour déclencher une actualisation
        return {"target": target_email, "timestamp": datetime.now().isoformat()}
    
    # Callback simple pour la liste d'utilisateurs dans l'interface basique
    @app.callback(
        Output(f"{ADMIN_PREFIX}users-list", "children"),
        Input(f"{ADMIN_PREFIX}refresh-button", "n_clicks"),
        Input(f"{ADMIN_PREFIX}auth-store", "data"),
        prevent_initial_call=False
    )
    def update_simple_users_list(n_clicks, auth_data):
        if not auth_data or not auth_data.get("is_admin", False):
            return html.P("Accès non autorisé", className="text-danger")
        
        try:
            # Charger les utilisateurs depuis la base de données
            users_df = get_all_authorized_users()
            if isinstance(users_df, pd.DataFrame) and not users_df.empty:
                users_list = []
                for _, user in users_df.iterrows():
                    status_badge = dbc.Badge(
                        "Actif" if user.get('is_active', True) else "Inactif",
                        color="success" if user.get('is_active', True) else "secondary",
                        className="me-2"
                    )
                    role_badge = dbc.Badge(
                        user.get('role', 'user').title(),
                        color="primary" if user.get('role') == 'admin' else "info",
                        className="me-2"
                    )
                    
                    users_list.append(
                        dbc.ListGroupItem([
                            html.Div([
                                html.Strong(user.get('email', 'N/A')),
                                html.Br(),
                                status_badge,
                                role_badge,
                                html.Small(f"Ajouté le: {user.get('added_at', 'N/A')}", className="text-muted")
                            ])
                        ])
                    )
                
                return dbc.ListGroup(users_list)
            else:
                return dbc.Alert("Aucun utilisateur autorisé trouvé", color="info")
        except Exception as e:
            return dbc.Alert(f"Erreur lors du chargement des utilisateurs: {str(e)}", color="danger")
    
    return app
