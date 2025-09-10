"""Page d'administration des utilisateurs - Architecture basée sur driver_validation.py"""

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, callback_context, no_update
import dash
from flask import session
from dash.exceptions import PreventUpdate
from dash_apps.utils.admin_db_rest import is_admin, get_all_authorized_users
import pandas as pd

# Helper de log standardisé (aligné avec driver_validation)
def log_callback(name, inputs, states=None):
    try:
        import json as _json
        def _short(s):
            s = str(s)
            return f"{s[:4]}…{s[-4:]}" if len(s) > 14 else s
        def _clean(v):
            if isinstance(v, dict):
                out = {}
                for k, val in v.items():
                    if val in (None, ""):
                        continue
                    if isinstance(val, str) and val == "all":
                        continue
                    out[k] = _clean(val)
                return out
            if isinstance(v, list):
                return [_clean(x) for x in v if x not in (None, "")]
            if isinstance(v, str):
                return _short(v)
            return v
        ins = _clean(inputs)
        sts = _clean(states or {})
        sep = "=" * 74
        print("\n" + sep)
        print(f"[CB] {name}")
        print("Inputs:")
        for k, v in ins.items():
            try:
                msg = _json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
            except Exception:
                msg = str(v)
            print(f"  - {k}: {msg}")
        print("States:")
        for k, v in sts.items():
            try:
                msg = _json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
            except Exception:
                msg = str(v)
            print(f"  - {k}: {msg}")
        print(sep)
    except Exception:
        pass

def render_admin_users_table(users_data, page=1, total=0, selected_email=None, tab="active"):
    """Rendu du tableau des utilisateurs administrateurs"""
    if not users_data:
        return dbc.Alert("Aucun utilisateur trouvé", color="info", className="mt-3")
    
    # Convertir en DataFrame si nécessaire
    if isinstance(users_data, list):
        df = pd.DataFrame(users_data)
    else:
        df = users_data
    
    if df.empty:
        return dbc.Alert("Aucun utilisateur trouvé", color="info", className="mt-3")
    
    # Calcul pagination
    page_size = 10
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    # Créer les lignes du tableau
    table_rows = []
    for idx, user in df.iterrows():
        email = user.get('email', 'N/A')
        role = user.get('role', 'user')
        active = user.get('active', True)
        added_at = user.get('added_at', '')
        added_by = user.get('added_by', '')
        
        # Badge de statut
        status_badge = dbc.Badge(
            "Actif" if active else "Inactif",
            color="success" if active else "secondary",
            className="me-2"
        )
        
        # Badge de rôle
        role_badge = dbc.Badge(
            role.title(),
            color="primary" if role == 'admin' else "info",
            className="me-2"
        )
        
        # Boutons d'action
        action_buttons = dbc.ButtonGroup([
            dbc.Button(
                "Activer" if not active else "Désactiver",
                id={"type": "admin-toggle-status", "index": email},
                color="success" if not active else "warning",
                size="sm"
            ),
            dbc.Button(
                "Changer rôle",
                id={"type": "admin-toggle-role", "index": email},
                color="primary",
                size="sm"
            ),
            dbc.Button(
                "Supprimer",
                id={"type": "admin-delete-user", "index": email},
                color="danger",
                size="sm"
            )
        ], size="sm")
        
        # Ligne du tableau
        row_class = "table-active" if email == selected_email else ""
        table_rows.append(
            html.Tr([
                html.Td([
                    html.Strong(email),
                    html.Br(),
                    html.Small(f"Ajouté par: {added_by}", className="text-muted")
                ]),
                html.Td([status_badge, role_badge]),
                html.Td(html.Small(added_at)),
                html.Td(action_buttons)
            ], className=row_class, id={"type": f"admin-select-{tab}", "index": email})
        )
    
    # Table
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Email / Ajouté par"),
                html.Th("Statut / Rôle"),
                html.Th("Date d'ajout"),
                html.Th("Actions")
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, hover=True, responsive=True)
    
    # Pagination
    pagination = dbc.Pagination(
        id=f"admin-pagination-{tab}",
        active_page=page,
        max_value=total_pages,
        first_last=True,
        previous_next=True,
        fully_expanded=False
    ) if total_pages > 1 else html.Div()
    
    return html.Div([
        html.P(f"Total: {total} utilisateur(s)", className="text-muted"),
        table,
        pagination
    ])

# Layout principal de la page d'administration
def serve_layout():
    user_email = session.get('user_email', None)
    
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
    
    return dbc.Container([
        html.H2("Administration - Gestion des utilisateurs", style={"marginTop": "20px"}),
        html.P("Cette page permet de gérer les utilisateurs autorisés à accéder au dashboard.", className="text-muted"),
        
        # Stores (session) pour persister état
        dcc.Store(id="admin-selected-email", storage_type="session", data=None, clear_data=False),
        dcc.Store(id="admin-current-page-active", storage_type="session", data=1),
        dcc.Store(id="admin-current-page-inactive", storage_type="session", data=1),
        dcc.Store(id="admin-refresh", storage_type="session", data=0),
        dcc.Store(id="admin-tab-pref", storage_type="session", data="active"),
        
        # En-tête avec onglets
        dbc.Card([
            dbc.CardHeader([
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Utilisateurs actifs", href="#", id="admin-tab1-link", active=True, className="fw-bold")),
                    dbc.NavItem(dbc.NavLink("Utilisateurs inactifs", href="#", id="admin-tab2-link")),
                ], pills=True, card=True, className="nav-justified"),
                html.Hr(),
                dbc.ButtonGroup([
                    dbc.Button("Actualiser", id="admin-refresh-btn", color="primary", size="sm"),
                    dbc.Button("Ajouter utilisateur", id="admin-add-user-btn", color="success", size="sm")
                ])
            ]),
            dbc.CardBody([
                html.Div(id="admin-active-users-container", className="mt-2"),
                html.Div(id="admin-inactive-users-container", className="mt-2", style={"display": "none"}),
            ]),
        ], className="mt-3"),
        
        # Modal pour ajouter un utilisateur
        dbc.Modal([
            dbc.ModalHeader("Ajouter un utilisateur"),
            dbc.ModalBody([
                dbc.Form([
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Email"),
                            dbc.Input(id="admin-add-email", type="email", placeholder="utilisateur@example.com")
                        ], width=12)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Rôle"),
                            dbc.Select(
                                id="admin-add-role",
                                options=[
                                    {"label": "Utilisateur", "value": "user"},
                                    {"label": "Administrateur", "value": "admin"}
                                ],
                                value="user"
                            )
                        ], width=12)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Notes (optionnel)"),
                            dbc.Textarea(id="admin-add-notes", placeholder="Notes sur cet utilisateur...")
                        ], width=12)
                    ])
                ])
            ]),
            dbc.ModalFooter([
                dbc.Button("Annuler", id="admin-add-cancel", color="secondary"),
                dbc.Button("Ajouter", id="admin-add-submit", color="primary")
            ])
        ], id="admin-add-modal", is_open=False),
        
        # Zone de messages
        html.Div(id="admin-messages")
    ], fluid=True)

layout = serve_layout

# DEBUG - Chargement du module admin_page.py
print("[DEBUG] admin_page.py chargé")

# DEBUG - Layout défini
print("[DEBUG] Layout de la page admin défini")

# Callbacks

@callback(
    Output("admin-tab1-link", "active"),
    Output("admin-tab2-link", "active"),
    Output("admin-active-users-container", "style"),
    Output("admin-inactive-users-container", "style"),
    Input("admin-tab1-link", "n_clicks"),
    Input("admin-tab2-link", "n_clicks"),
    Input("admin-tab-pref", "data"),
    prevent_initial_call=False
)
def switch_admin_tabs(tab1_clicks, tab2_clicks, tab_pref):
    ctx = callback_context
    triggered = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else "admin-tab1-link"
    tab_pref = (tab_pref or "active")
    
    if triggered == "admin-tab2-link" or (triggered == "admin-tab-pref" and tab_pref == "inactive"):
        tab1_active = False
        tab2_active = True
    else:
        tab1_active = True
        tab2_active = False
    
    return (
        tab1_active, 
        tab2_active, 
        {"display": "block"} if tab1_active else {"display": "none"}, 
        {"display": "block"} if tab2_active else {"display": "none"}
    )

@callback(
    Output("admin-active-users-container", "children"),
    Input("admin-current-page-active", "data"),
    Input("admin-selected-email", "data"),
    Input("admin-refresh", "data"),
    prevent_initial_call=False
)
def render_active_users_table(current_page, selected_email, _refresh):
    log_callback("render_active_users_table", {"page": current_page, "selected_email": selected_email}, {})
    
    try:
        # Récupérer tous les utilisateurs
        all_users = get_all_authorized_users()
        if not all_users:
            return dbc.Alert("Aucun utilisateur trouvé", color="info")
        
        # Filtrer les utilisateurs actifs
        active_users = [u for u in all_users if u.get('active', True)]
        
        return render_admin_users_table(active_users, current_page or 1, len(active_users), selected_email, "active")
    except Exception as e:
        return dbc.Alert(f"Erreur lors du chargement des utilisateurs: {str(e)}", color="danger")

@callback(
    Output("admin-inactive-users-container", "children"),
    Input("admin-current-page-inactive", "data"),
    Input("admin-selected-email", "data"),
    Input("admin-refresh", "data"),
    prevent_initial_call=False
)
def render_inactive_users_table(current_page, selected_email, _refresh):
    log_callback("render_inactive_users_table", {"page": current_page, "selected_email": selected_email}, {})
    
    try:
        # Récupérer tous les utilisateurs
        all_users = get_all_authorized_users()
        if not all_users:
            return dbc.Alert("Aucun utilisateur inactif", color="info")
        
        # Filtrer les utilisateurs inactifs
        inactive_users = [u for u in all_users if not u.get('active', True)]
        
        if not inactive_users:
            return dbc.Alert("Aucun utilisateur inactif", color="info")
        
        return render_admin_users_table(inactive_users, current_page or 1, len(inactive_users), selected_email, "inactive")
    except Exception as e:
        return dbc.Alert(f"Erreur lors du chargement des utilisateurs inactifs: {str(e)}", color="danger")

@callback(
    Output("admin-refresh", "data", allow_duplicate=True),
    Input("admin-refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def refresh_admin_data(n_clicks):
    if n_clicks:
        return n_clicks
    return no_update

@callback(
    Output("admin-add-modal", "is_open"),
    Input("admin-add-user-btn", "n_clicks"),
    Input("admin-add-cancel", "n_clicks"),
    Input("admin-add-submit", "n_clicks"),
    State("admin-add-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_add_modal(add_clicks, cancel_clicks, submit_clicks, is_open):
    ctx = callback_context
    if not ctx.triggered:
        return no_update
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "admin-add-user-btn":
        return True
    elif button_id in ["admin-add-cancel", "admin-add-submit"]:
        return False
    
    return is_open

@callback(
    Output("admin-messages", "children"),
    Output("admin-refresh", "data", allow_duplicate=True),
    Input("admin-add-submit", "n_clicks"),
    State("admin-add-email", "value"),
    State("admin-add-role", "value"),
    State("admin-add-notes", "value"),
    prevent_initial_call=True
)
def add_new_user(n_clicks, email, role, notes):
    if not n_clicks or not email or not role:
        return no_update, no_update
    
    try:
        from dash_apps.utils.admin_db_rest import add_authorized_user
        admin_email = session.get('user_email', 'admin')
        
        success, message = add_authorized_user(email, role, admin_email, notes or "")
        
        if success:
            return dbc.Alert(message, color="success", dismissable=True), n_clicks + 1
        else:
            return dbc.Alert(message, color="danger", dismissable=True), no_update
    except Exception as e:
        return dbc.Alert(f"Erreur: {str(e)}", color="danger", dismissable=True), no_update

