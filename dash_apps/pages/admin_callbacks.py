from dash import callback, Input, Output, State, ctx, ALL
import dash_bootstrap_components as dbc
from flask import session
from dash_apps.utils.admin_db import get_all_authorized_users, add_authorized_user, update_user_status, update_user_role, is_admin
import pandas as pd
from datetime import datetime

# Pru00e9fixe des IDs pour la page admin pour u00e9viter les conflits
ADMIN_PREFIX = 'admin-'

def register_admin_callbacks(app):
    """Enregistre les callbacks de la page d'administration.
    Cette fonction est appelu00e9e uniquement lorsque la page admin est chargu00e9e.
    """
    
    # Vu00e9rifier si l'utilisateur est autorisu00e9 u00e0 accu00e9der u00e0 la page admin
    @app.callback(
        Output(f"{ADMIN_PREFIX}auth-store", "data"),
        Input(f"{ADMIN_PREFIX}auth-store", "id")
    )
    def check_admin_auth(_):
        # Ru00e9cupu00e9rer l'email de l'utilisateur depuis la session
        user_email = session.get('user_email', None)
        admin_status = is_admin(user_email)
        return {"is_admin": admin_status, "user_email": user_email}

    # Afficher le contenu appropriu00e9 selon les droits d'accu00e8s
    @app.callback(
        Output(f"{ADMIN_PREFIX}auth-check", "children"),
        Output(f"{ADMIN_PREFIX}content", "style"),
        Input(f"{ADMIN_PREFIX}auth-store", "data")
    )
    def update_admin_access(auth_data):
        if not auth_data or not auth_data.get("is_admin", False):
            return dbc.Alert(
                "Vous n'u00eates pas autorisu00e9 u00e0 accu00e9der u00e0 cette page. Seuls les administrateurs peuvent y accu00e9der.",
                color="danger",
                className="mt-3 mb-3"
            ), {"display": "none"}
        
        return None, {"display": "block"}

    # Charger les utilisateurs autorisu00e9s
    @app.callback(
        Output(f"{ADMIN_PREFIX}users-store", "data"),
        Input(f"{ADMIN_PREFIX}refresh-btn", "n_clicks"),
        Input(f"{ADMIN_PREFIX}add-btn", "n_clicks")
    )
    def load_authorized_users(refresh_clicks, add_clicks):
        users = get_all_authorized_users()
        return users

    # Afficher le tableau des utilisateurs
    @app.callback(
        Output(f"{ADMIN_PREFIX}table-container", "children"),
        Input(f"{ADMIN_PREFIX}users-store", "data")
    )
    def display_users_table(users_data):
        if not users_data:
            return html.Div("Aucun utilisateur trouvu00e9.")
        
        # Cru00e9er un DataFrame avec les donnu00e9es
        df = pd.DataFrame(users_data)
        
        # Formater les dates pour l'affichage
        for date_col in ['added_at', 'updated_at']:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col]).dt.strftime("%d/%m/%Y %H:%M")
        
        # Pru00e9parer les donnu00e9es avec une colonne d'actions
        table_data = []
        for user in users_data:
            # Cru00e9er des boutons HTML pour les actions
            toggle_text = "Du00e9sactiver" if user.get("active") else "Activer"
            toggle_color = "danger" if user.get("active") else "success"
            
            actions_html = f'''
            <div class="d-flex justify-content-around">
                <button id="toggle-{user['email']}" class="btn btn-sm btn-{toggle_color} mx-1" onclick="toggleUserStatus('{user['email']}')">
                    {toggle_text}
                </button>
                <button id="role-{user['email']}" class="btn btn-sm btn-primary mx-1" onclick="changeUserRole('{user['email']}')">
                    Ru00f4le
                </button>
            </div>
            '''
            
            table_data.append({
                **user,
                "active": "\u2705" if user.get("active") else "\u274C",
                "actions": actions_html
            })
        
        # Rendre le tableau des utilisateurs
        from dash import dash_table
        
        table = dash_table.DataTable(
            id=f"{ADMIN_PREFIX}users-table",
            columns=[
                {"name": "Email", "id": "email"},
                {"name": "Ru00f4le", "id": "role"},
                {"name": "Actif", "id": "active", "presentation": "markdown"},
                {"name": "Ajoutu00e9 le", "id": "added_at"},
                {"name": "Mis u00e0 jour le", "id": "updated_at"},
                {"name": "Ajoutu00e9 par", "id": "added_by"},
                {"name": "Notes", "id": "notes"},
                {"name": "Actions", "id": "actions", "presentation": "markdown"}
            ],
            data=table_data,
            style_table={
                "overflowX": "auto"
            },
            style_cell={
                "textAlign": "left",
                "padding": "10px",
                "whiteSpace": "normal",
                "height": "auto",
                "fontSize": "14px"
            },
            style_header={
                "backgroundColor": "#f4f6f8",
                "fontWeight": "bold",
                "textAlign": "left",
                "fontSize": "15px",
                "color": "#3a4654"
            },
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "#f9fafb"
                }
            ],
            filter_action="native",
            sort_action="native",
            page_size=10
        )
        
        return table

    # Callback pour ajouter un nouvel utilisateur
    @app.callback(
        Output(f"{ADMIN_PREFIX}add-result", "children"),
        Input(f"{ADMIN_PREFIX}add-btn", "n_clicks"),
        State(f"{ADMIN_PREFIX}new-email", "value"),
        State(f"{ADMIN_PREFIX}new-role", "value"),
        State(f"{ADMIN_PREFIX}new-notes", "value"),
        State(f"{ADMIN_PREFIX}auth-store", "data"),
        prevent_initial_call=True
    )
    def add_new_user(n_clicks, email, role, notes, auth_data):
        if not n_clicks:
            return ""
            
        # Vu00e9rifier que l'utilisateur est admin
        if not auth_data or not auth_data.get("is_admin"):
            return dbc.Alert("Vous n'avez pas les droits pour effectuer cette action", color="danger")
            
        # Vu00e9rifier que l'email est valide
        if not email:
            return dbc.Alert("Veuillez saisir un email valide", color="danger")
            
        # Ajouter l'utilisateur
        admin_email = auth_data.get("user_email")
        success, message = add_authorized_user(email, role, admin_email, notes)
        
        if success:
            return dbc.Alert(message, color="success")
        else:
            return dbc.Alert(message, color="danger")

    # Import des modules nu00e9cessaires pour les autres callbacks
    from dash import html

    # Du00e9claration des callbacks restants selon le mu00eame principe
    # ...

    # Note: Les autres callbacks (pour la gestion des utilisateurs) peuvent u00eatre ajoutu00e9s ici
    # en suivant le mu00eame modu00e8le et en pru00e9fixant les IDs avec ADMIN_PREFIX
