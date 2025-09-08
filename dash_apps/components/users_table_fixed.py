from dash import html, dcc, Input, Output, State, callback, callback_context
import dash
import json
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash_apps.config import Config
from dash_apps.repositories.user_repository import UserRepository


# Helper de log standardisé (même format que dans users.py)
def log_callback(name, inputs, states=None):
    def _short_str(s):
        try:
            s = str(s)
        except Exception:
            return s
        if len(s) > 14:
            return f"{s[:4]}…{s[-4:]}"
        return s

    def _clean(value):
        if isinstance(value, dict):
            cleaned = {}
            for k, v in value.items():
                if v is None or v == "":
                    continue
                if isinstance(v, str) and v == "all":
                    continue
                if k in ("selected_user", "selected_user_uid") and isinstance(v, dict) and "uid" in v:
                    cleaned["selected_uid"] = _short_str(v.get("uid"))
                    continue
                cleaned[k] = _clean(v)
            return cleaned
        if isinstance(value, list):
            return [_clean(v) for v in value if v is not None and v != ""]
        if isinstance(value, str):
            return _short_str(value)
        return value

    def _kv_lines(dct):
        if not dct:
            return ["  (none)"]
        lines = []
        for k, v in dct.items():
            try:
                if isinstance(v, (dict, list)):
                    v_str = json.dumps(v, ensure_ascii=False)
                else:
                    v_str = str(v)
            except Exception:
                v_str = f"<{type(v).__name__}>"
            lines.append(f"  {k}: {v_str}")
        return lines

    inputs = _clean(inputs) if inputs else {}
    states = _clean(states) if states else {}
    
    print(f"\n==========================================================================")
    print(f"[CB] {name}")
    print(f"Inputs:")
    for line in _kv_lines(inputs):
        print(line)
    if states:
        print(f"States:")
        for line in _kv_lines(states):
            print(line)
    print(f"==========================================================================\n")
    
    
def render_users_table(users_data, page_count, current_page=1, total_users=0, selected_uid=None):
    """
    Crée un tableau d'utilisateurs avec pagination et sélection de ligne.
    
    Args:
        users_data: Liste de dictionnaires avec les données utilisateurs
        page_count: Nombre total de pages
        current_page: Page actuelle (1-based)
        total_users: Nombre total d'utilisateurs
        selected_uid: UID de l'utilisateur sélectionné
        
    Returns:
        Composant Dash contenant le tableau et les contrôles de pagination
    """
    print(f"[DEBUG] render_custom_users_table appelé avec selected_uid = {selected_uid}, type: {type(selected_uid)}")
    
    # Colonnes à afficher
    columns = [
        {"id": "display_name", "name": "Nom d'affichage"},
        {"id": "first_name", "name": "Prénom"},
        {"id": "name", "name": "Nom"},
        {"id": "email", "name": "Email"},
        {"id": "role", "name": "Rôle"}
    ]
    
    headers = [col["name"] for col in columns]
    
    # Générer les lignes du tableau avec surlignage conditionnel
    table_rows = []
    
    # Si aucun utilisateur, afficher un message
    if not users_data:
        return html.Div([
            html.P("Aucun utilisateur trouvé", style={"textAlign": "center", "padding": "20px"})
        ])
    
    # Extraire l'UID sélectionné du dictionnaire si nécessaire
    selected_uid_value = None
    if selected_uid:
        if isinstance(selected_uid, dict) and "uid" in selected_uid:
            selected_uid_value = selected_uid["uid"]
        else:
            selected_uid_value = selected_uid
    
    # Couleur de surbrillance pour la ligne sélectionnée
    highlight_color = "#e8f4ff"
    
    for user_data in users_data:
        # Préparer l'ID pour le pattern-matching callback
        uid = user_data.get("uid", "")
        # Déterminer si cette ligne est sélectionnée
        is_selected = selected_uid_value and uid == selected_uid_value
        
        # Style conditionnel pour la ligne
        row_style = {
            "backgroundColor": highlight_color if is_selected else "white",
            "cursor": "pointer",
            "transition": "background-color 0.2s"
        }
        
        # Classe conditionnelle pour la ligne
        row_class = "selected-row" if is_selected else ""
        
        # Créer les cellules pour cette ligne
        row_cells = []
        for col in columns:
            col_id = col["id"]
            value = user_data.get(col_id, "")
            # Styliser spécifiquement la colonne du rôle
            if col_id == "role":
                role_styles = {
                    "admin": {"color": "#d9534f", "fontWeight": "bold"},
                    "driver": {"color": "#0275d8", "fontWeight": "500"},
                    "user": {"color": "#5cb85c"}
                }
                cell_style = role_styles.get(value.lower(), {})
                row_cells.append(html.Td(value, style=cell_style))
            else:
                row_cells.append(html.Td(value))
        
        # Ajouter la ligne complète au tableau
        table_rows.append(
            html.Tr(
                row_cells,
                id={"type": "user-row", "index": uid},
                style=row_style,
                className=row_class
            )
        )
    
    # Créer le tableau avec les entêtes
    table = html.Table(
        [
            # Entête du tableau
            html.Thead(
                html.Tr([html.Th(header) for header in headers]),
                style={
                    "backgroundColor": "#f4f6f8",
                    "color": "#3a4654",
                    "fontWeight": "600",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px"
                }
            ),
            # Corps du tableau
            html.Tbody(table_rows, id="users-table-body")
        ],
        className="table table-hover",
        style={
            "width": "100%",
            "marginBottom": "0",
            "backgroundColor": "white",
            "borderCollapse": "collapse"
        }
    )
    
    # Contrôles de pagination avec flèches
    pagination = html.Div([
        dbc.Button([
            html.I(className="fas fa-arrow-left mr-2"),
            "Précédent"
        ],
            id="prev-page-btn", 
            color="primary", 
            outline=False,
            disabled=current_page <= 1,
            style={"backgroundColor": "#4582ec", "borderColor": "#4582ec", "color": "white"}
        ),
        html.Span(
            f"Page {current_page} sur {page_count} (Total: {total_users} utilisateurs)", 
            style={"margin": "0 15px", "lineHeight": "38px"}
        ),
        dbc.Button([
            "Suivant",
            html.I(className="fas fa-arrow-right ml-2")
        ],
            id="next-page-btn", 
            color="primary", 
            outline=False,
            disabled=current_page >= page_count,
            style={"backgroundColor": "#4582ec", "borderColor": "#4582ec", "color": "white"}
        )
    ], style={"marginTop": "20px", "textAlign": "center", "padding": "10px"})
    
    # Composant complet
    return html.Div([
        html.Div([
            html.H5("Liste des utilisateurs", style={
                "marginBottom": "15px", 
                "color": "#3a4654",
                "fontWeight": "500",
                "fontSize": "18px"
            }),
            # Message d'aide pour indiquer que les lignes sont cliquables
            html.Div(
                html.Small("Cliquez sur une ligne pour sélectionner un utilisateur",
                    style={
                        "color": "#666", 
                        "fontStyle": "italic",
                        "marginBottom": "10px",
                        "display": "block"
                    }
                ),
                style={"marginBottom": "10px"}
            ),
            # Les styles sont maintenant appliqués directement aux lignes du tableau
            table
        ], style={
            "padding": "20px",
            "borderRadius": "6px",
            "backgroundColor": "white",
            "boxShadow": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
        }),
        pagination
    ])


# Callback pour la navigation entre les pages
@callback(
    Output("users-current-page", "data", allow_duplicate=True),
    Input("prev-page-btn", "n_clicks"),
    Input("next-page-btn", "n_clicks"),
    State("users-current-page", "data"),
    prevent_initial_call=True
)
def handle_pagination_buttons(prev_clicks, next_clicks, current_page):
    ctx = callback_context
    log_callback(
        "handle_pagination_buttons",
        {"prev_clicks": prev_clicks, "next_clicks": next_clicks},
        {"current_page": current_page}
    )
    # Si aucun bouton n'a été cliqué
    if not ctx.triggered:
        raise PreventUpdate

    if prev_clicks is None and next_clicks is None:
        raise PreventUpdate
    
    # Déterminer quel bouton a été cliqué
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Valeur par défaut pour current_page si elle n'existe pas encore
    if not isinstance(current_page, (int, float)):
        current_page = 1
        
    # Mettre à jour la page en fonction du bouton cliqué
    if button_id == "prev-page-btn":
        return max(1, current_page - 1)
    elif button_id == "next-page-btn":
        # On vérifiera que la page n'est pas trop grande dans le callback qui utilise cette valeur
        return current_page + 1
    
    # Par défaut, ne pas changer de page
    raise PreventUpdate


# Gestion des clics sur les lignes
@callback(
    [Output("selected-user-uid", "data"),
     Output("users-current-page", "data", allow_duplicate=True)],
    Input("users-table-body", "active_cell"),
    [State("users-table-body", "data"),
     State("users-current-page", "data")],
    prevent_initial_call=True
)
def handle_row_selection(active_cell, data, current_page):
    """Gère la sélection d'une ligne dans le tableau des utilisateurs"""
    log_callback("handle_row_selection", {"row_clicks": active_cell}, {})
    
    # Si aucune ligne n'est sélectionnée
    if not active_cell or not data:
        raise PreventUpdate
    
    row_idx = active_cell["row"]
    if row_idx >= len(data):
        raise PreventUpdate
        
    # Récupérer l'UID dans la ligne sélectionnée
    user_data = data[row_idx]
    if "uid" in user_data:
        # Retourner l'UID sélectionné sous forme de dict et préserver la page actuelle
        return {"uid": user_data["uid"]}, current_page
    
    # Si l'UID n'est pas trouvé, ne rien mettre à jour
    raise PreventUpdate


# Callback pour la mise en surbrillance des lignes
@callback(
    Output("users-table-body", "style_data_conditional"),
    Input("selected-user-uid", "data"),
    State("users-table-body", "data"),
    prevent_initial_call=True
)
def highlight_selected_row(selected_uid, row_data):
    """Met en surbrillance la ligne sélectionnée dans le tableau"""
    log_callback(
        "highlight_selected_row",
        {"selected_uid": selected_uid},
        {"row_count": len(row_data) if row_data else 0}
    )
    
    # Si aucun utilisateur n'est sélectionné, ne pas mettre en surbrillance
    if not selected_uid or not row_data:
        return []
    
    # Extraire l'UID du dictionnaire si nécessaire
    uid_value = selected_uid.get("uid") if isinstance(selected_uid, dict) else selected_uid
    
    # Trouver l'index de la ligne correspondant à l'UID sélectionné
    selected_indices = []
    for i, row in enumerate(row_data):
        if row.get("uid") == uid_value:
            selected_indices.append(i)
    
    # Créer un style conditionnel pour chaque ligne sélectionnée
    styles = []
    for idx in selected_indices:
        styles.append({
            "if": {"row_index": idx},
            "backgroundColor": "#e8f4ff",
            "border": "1px solid #4582ec"
        })
    
    return styles
