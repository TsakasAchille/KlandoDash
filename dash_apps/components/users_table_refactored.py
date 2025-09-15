"""
Composant tableau users refactorisé avec le pattern trips.
Utilise UsersService avec cache, validation Pydantic et configuration JSON.
"""
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
from dash_apps.services.users_service import UsersService
from dash_apps.utils.callback_logger import CallbackLogger
import os


def render_users_table_component():
    """Rendu du composant tableau users avec pagination."""
    return html.Div([
        # Conteneur pour le tableau
        html.Div(id="users-table-container"),
        
        # Contrôles de pagination
        html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.ButtonGroup([
                        dbc.Button("← Précédent", id="users-prev-btn", color="secondary", disabled=True),
                        dbc.Button("Suivant →", id="users-next-btn", color="secondary", disabled=True)
                    ])
                ], width="auto"),
                dbc.Col([
                    html.Div(id="users-pagination-info", className="text-muted mt-2")
                ], width=True)
            ], justify="between", align="center")
        ], className="mt-3")
    ])


def create_users_table(users_data: dict, selected_uid: str = None) -> html.Div:
    """Crée le tableau HTML des utilisateurs."""
    users = users_data.get('users', [])
    
    if not users:
        return dbc.Alert(
            [
                html.I(className="fas fa-info-circle me-2"),
                "Aucun utilisateur trouvé"
            ],
            color="info",
            className="text-center"
        )
    
    # En-têtes du tableau
    headers = [
        "Sélection",
        "Nom",
        "Email", 
        "Téléphone",
        "Rôle",
        "Genre",
        "Note",
        "Créé le"
    ]
    
    # Créer les lignes du tableau
    table_rows = []
    for user in users:
        uid = user.get('uid')
        is_selected = uid == selected_uid
        
        # Style de la ligne
        row_class = "user-row selected-user-row" if is_selected else "user-row"
        
        # Formater les données
        display_name = user.get('display_name') or "Nom non renseigné"
        email = user.get('email') or "Email non renseigné"
        phone = user.get('phone_number') or "-"
        role = user.get('role', 'user').upper()
        
        # Genre avec formatage
        gender_map = {
            "man": "Homme", "male": "Homme",
            "woman": "Femme", "female": "Femme", 
            "other": "Autre"
        }
        gender = gender_map.get(user.get('gender', '').lower(), "-")
        
        # Rating avec formatage
        rating = user.get('rating')
        rating_display = f"{rating:.1f} ★" if rating else "-"
        
        # Date de création
        created_at = user.get('created_at', '')
        if created_at:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_at = dt.strftime('%d/%m/%Y')
            except:
                created_at = created_at[:10] if len(created_at) >= 10 else created_at
        
        row = html.Tr([
            # Bouton de sélection
            html.Td([
                dbc.Button(
                    html.I(className="fas fa-check"),
                    id={"type": "select-user-btn", "index": uid},
                    color="primary" if is_selected else "light",
                    outline=not is_selected,
                    size="sm",
                    style={
                        "width": "30px", "height": "30px", "padding": "0",
                        "display": "flex", "alignItems": "center", "justifyContent": "center"
                    }
                )
            ], style={"width": "60px", "text-align": "center"}),
            
            # Données utilisateur
            html.Td(display_name, style={"fontWeight": "bold" if is_selected else "normal"}),
            html.Td(email),
            html.Td(phone),
            html.Td([
                dbc.Badge(role, color="primary" if role == "DRIVER" else "secondary", className="me-1")
            ]),
            html.Td(gender),
            html.Td(rating_display, style={"fontWeight": "bold" if rating and rating >= 4.0 else "normal"}),
            html.Td(created_at)
        ], 
        className=row_class,
        style={"cursor": "pointer", "transition": "all 0.2s"},
        id={"type": "user-row", "index": uid}
        )
        
        table_rows.append(row)
    
    # Construire le tableau
    table = dbc.Table([
        html.Thead([
            html.Tr([html.Th(header) for header in headers])
        ], className="table-dark"),
        html.Tbody(table_rows)
    ], 
    striped=True, 
    hover=True, 
    responsive=True,
    className="users-table"
    )
    
    return html.Div([
        table,
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.Small(f"Affichage de {len(users)} utilisateur(s)", className="text-muted")
            ])
        ])
    ])


@callback(
    [Output("users-table-container", "children"),
     Output("users-pagination-info", "children"),
     Output("users-prev-btn", "disabled"),
     Output("users-next-btn", "disabled")],
    [Input("users-current-page", "data"),
     Input("users-filter-store", "data"),
     Input("users-prev-btn", "n_clicks"),
     Input("users-next-btn", "n_clicks")],
    [State("selected-user-uid", "data")],
    prevent_initial_call=False
)
def render_users_table_callback(current_page, filter_data, prev_clicks, next_clicks, selected_uid):
    """Callback principal pour rendre le tableau users avec pagination."""
    
    # Log de debug si activé
    debug_enabled = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
    if debug_enabled:
        CallbackLogger.log_callback(
            "render_users_table_callback",
            {
                "current_page": current_page,
                "filter_data": filter_data,
                "selected_uid": selected_uid[:8] if selected_uid else None
            },
            status="INFO",
            extra_info="Rendering users table"
        )
    
    # Déterminer la page à afficher
    page = current_page or 1
    page_size = 20
    
    # Gérer les clics de pagination
    ctx = callback_context
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == "users-prev-btn" and page > 1:
            page -= 1
        elif trigger_id == "users-next-btn":
            page += 1
    
    try:
        # Récupérer les données via le service
        users_summary = UsersService.get_users_summary(
            page=page, 
            page_size=page_size, 
            filters=filter_data or {}
        )
        
        # Créer le tableau
        table_component = create_users_table(users_summary, selected_uid)
        
        # Informations de pagination
        total_count = users_summary.get('total_count', 0)
        total_pages = users_summary.get('total_pages', 1)
        has_next = users_summary.get('has_next', False)
        has_previous = users_summary.get('has_previous', False)
        
        pagination_info = f"Page {page} sur {total_pages} - {total_count} utilisateur(s) au total"
        
        # États des boutons de pagination
        prev_disabled = not has_previous
        next_disabled = not has_next
        
        if debug_enabled:
            CallbackLogger.log_callback(
                "render_users_table_success",
                {
                    "page": page,
                    "total_count": total_count,
                    "users_found": len(users_summary.get('users', []))
                },
                status="SUCCESS",
                extra_info="Users table rendered successfully"
            )
        
        return table_component, pagination_info, prev_disabled, next_disabled
        
    except Exception as e:
        if debug_enabled:
            CallbackLogger.log_callback(
                "render_users_table_error",
                {"error": str(e)},
                status="ERROR",
                extra_info="Failed to render users table"
            )
        
        # Retourner un message d'erreur
        error_component = dbc.Alert(
            [
                html.I(className="fas fa-exclamation-triangle me-2"),
                f"Erreur lors du chargement des utilisateurs: {str(e)}"
            ],
            color="danger"
        )
        
        return error_component, "Erreur", True, True


@callback(
    Output("selected-user-uid", "data", allow_duplicate=True),
    Input({"type": "select-user-btn", "index": dash.ALL}, "n_clicks"),
    State("selected-user-uid", "data"),
    prevent_initial_call=True
)
def handle_user_selection(n_clicks_list, current_selected_uid):
    """Gère la sélection d'un utilisateur via les boutons."""
    
    if not any(n_clicks_list):
        raise PreventUpdate
    
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Extraire l'UID du bouton cliqué
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    import json
    button_data = json.loads(button_id)
    clicked_uid = button_data['index']
    
    # Log de debug si activé
    debug_enabled = os.getenv('DEBUG_USERS', 'False').lower() == 'true'
    if debug_enabled:
        CallbackLogger.log_callback(
            "handle_user_selection",
            {
                "clicked_uid": clicked_uid[:8] if clicked_uid else None,
                "current_selected": current_selected_uid[:8] if current_selected_uid else None
            },
            status="INFO",
            extra_info="User selection changed"
        )
    
    # Si l'utilisateur est déjà sélectionné, le désélectionner
    if current_selected_uid == clicked_uid:
        return None
    
    # Sinon, sélectionner le nouvel utilisateur
    return clicked_uid
