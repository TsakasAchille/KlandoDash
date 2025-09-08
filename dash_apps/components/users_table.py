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
                v_str = str(v)
            lines.append(f"  - {k}: {v_str}")
        return lines

    try:
        c_inputs = _clean(inputs)
        c_states = _clean(states or {})
        sep = "=" * 74
        print("\n" + sep)
        print(f"[CB] {name}")
        print("Inputs:")
        for line in _kv_lines(c_inputs):
            print(line)
        print("States:")
        for line in _kv_lines(c_states):
            print(line)
        print(sep)
    except Exception:
        sep = "=" * 74
        print("\n" + sep)
        print(f"[CB] {name}")
        print(f"Inputs: {inputs}")
        print(f"States: {states or {}}")
        print(sep)

# Store pour gérer la pagination de manière locale sans déclencher le callback principal
def render_custom_users_table(users_data, page_count=1, current_page=1, total_users=0, selected_uid=None):
    """Fonction principale pour générer le tableau d'utilisateurs
    
    Args:
        users_data: Liste des données utilisateurs
        page_count: Nombre total de pages
        current_page: Numéro de la page courante (1-based)
        total_users: Nombre total d'utilisateurs (pour info pagination)
        selected_uid: UID de l'utilisateur sélectionné (dict avec clé 'uid' ou string)
    """
    
    # Debug pour détecter les erreurs de types
    print(f"[DEBUG] render_custom_users_table appelé avec selected_uid = {selected_uid}, type: {type(selected_uid)}")
    page_size = Config.USERS_TABLE_PAGE_SIZE
    
    # Créer les en-têtes du tableau
    headers = ["", "Nom", "Email", "Téléphone", "Rôle", "Genre", "Notation", "Date d'inscription"]
    
    # Créer les lignes du tableau à partir des données pré-calculées
    table_rows = []
    for row_data in users_data:
        # Extraire les champs directement des données pré-calculées
        uid = row_data.get("uid", "")
        name = row_data.get("display_name", "")
        email = row_data.get("email", "")
        phone = row_data.get("phone_number", "")
        role = row_data.get("role", "")
        gender = row_data.get("gender", "")
        rating = row_data.get("rating", None)
        created_at = row_data.get("created_at", "")
            
        # Debug pour comprendre les types et valeurs
        #print(f"\n[DEBUG] Type de selected_uid: {type(selected_uid)}, Valeur: {selected_uid}")
        #print(f"\n[DEBUG] Type de uid: {type(uid)}, Valeur: {uid}")
        
        # Extraire l'UID de selected_uid s'il s'agit d'un dictionnaire
        selected_uid_value = selected_uid
        if isinstance(selected_uid, dict) and 'uid' in selected_uid:
            selected_uid_value = selected_uid['uid']
            #print(f"\n[DEBUG] Extraction de l'UID du dictionnaire: {selected_uid_value}")
        
        # Conversion en string pour la comparaison
        uid_str = str(uid)
        selected_uid_str = str(selected_uid_value)
        
        # Comparaison stricte des strings
        is_selected = uid_str == selected_uid_str
        
        # Logging pour debug
        #print(f"\n[DEBUG] Comparaison: '{uid_str}' == '{selected_uid_str}' => {is_selected}")

            
        # Styles de base pour la ligne (laisser la mise en évidence au CSS via className)
        row_style = {
            "transition": "all 0.2s",
            "cursor": "pointer",
        }

        # Attributs pour la ligne
        row_class = "user-row selected-user-row" if is_selected else "user-row"
        
        # Créer un ID string pour la ligne et convertir l'objet JSON en string
        row_id_obj = {"type": "user-row", "index": uid}
        
        row_attributes = {
            "id": row_id_obj,  # Dash convertira automatiquement en JSON str
            "className": row_class,
            "title": "Cliquez pour sélectionner cet utilisateur",
            "style": row_style,
            "n_clicks": 0  # Permettre de capturer les clics sur la ligne
        }
        
        row = html.Tr([
            # Case à cocher ou indicateur de sélection
            html.Td(
                dbc.Button(
                    children=html.I(className="fas fa-check"),
                    id={"type": "select-user-btn", "index": uid},
                    color="danger" if is_selected else "light",
                    outline=not is_selected,
                    size="sm",
                    style={
                        "width": "30px",
                        "height": "30px",
                        "padding": "0px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "margin": "0 auto"
                    }
                ),
                style={"width": "40px", "cursor": "pointer"}
            ),
            # Autres colonnes
            html.Td(name),
            html.Td(email),
            html.Td(phone),
            html.Td(role),
            # Afficher le genre avec formatage
            html.Td(
                {"man": "Homme", "woman": "Femme", "male": "Homme", "female": "Femme", "helicopter": "🚁 Helicopter", "other": "Autre"}.get(gender, "-"),
                style={}
            ),
            # Afficher le rating avec formatage
            html.Td(
                f"{rating:.1f} ★" if rating is not None else "-",
                style={"fontWeight": "bold" if rating and rating >= 4.0 else "normal"}
            ),
            html.Td(created_at),
        ], **row_attributes)
        
        table_rows.append(row)
    
    # Si aucun utilisateur n'est disponible, afficher une ligne vide
    if not table_rows:
        table_rows = [html.Tr([html.Td("Aucun utilisateur trouvé", colSpan=8)])]
    
    # Construire le tableau
    table = html.Table(
        [
            # En-tête
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
            html.Tbody(table_rows)
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


"""
# Callback unifié pour la sélection d'utilisateur (bouton ou ligne)
@callback(
    Output("selected-user-from-table", "data"),
    Input({"type": "select-user-btn", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def handle_button_selection(btn_clicks):
    print("\n[DEBUG] Début callback handle_button_selection")
    
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Déterminer ce qui a été cliqué
    clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    try:
        # Extraire le type et l'index de l'ID
        id_dict = json.loads(clicked_id)
        uid = id_dict["index"]
        print(f"\n[DEBUG] Bouton cliqué, uid: {uid}")
        
        # Retourner directement le UID sélectionné
        return {"uid": uid}
    
    except Exception as e:
        print(f"\n[ERROR] Erreur sélection via bouton: {str(e)}")
        raise PreventUpdate
"""

# 2. Gestion des clics sur les lignes
@callback(
    #Output("selected-user-from-table", "data"),
    Output("selected-user-uid", "data", allow_duplicate=True),
    Input({"type": "user-row", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True  # Ceci ne suffit pas toujours avec les pattern-matching callbacks
)
def handle_row_selection(row_clicks):
    log_callback("handle_row_selection", {"row_clicks": row_clicks}, {})
    
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Vérifier si le callback est déclenché lors du chargement initial
    # Les clicks seront tous à zéro lors du chargement initial
    if not any(clicks > 0 for clicks in row_clicks):
        raise PreventUpdate
    
    # Déterminer ce qui a été cliqué
    clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    try:
        # Extraire l'index (uid) de l'ID JSON
        id_dict = json.loads(clicked_id)
        uid = id_dict["index"]
        
        # Retourner l'UID extrait
        return {"uid": uid}
    except Exception as e:
        # Logs d'erreur concis
        log_callback("handle_row_selection_error", {"error": str(e), "clicked_id": clicked_id}, {})
        raise PreventUpdate

# 3. Nouveau callback pour gérer uniquement la mise en surbrillance des lignes


@callback(
    Output({"type": "user-row", "index": dash.ALL}, "style"),
    Output({"type": "user-row", "index": dash.ALL}, "className"),
    Output({"type": "select-user-btn", "index": dash.ALL}, "color"),
    Output({"type": "select-user-btn", "index": dash.ALL}, "outline"),
    Input("selected-user-uid", "data"),

    State({"type": "user-row", "index": dash.ALL}, "id"),
    State({"type": "select-user-btn", "index": dash.ALL}, "id"),
    prevent_initial_call=True
)
def highlight_selected_row(selected_user, row_ids, button_ids):
    log_callback("highlight_selected_row", {"selected_user": selected_user}, {"row_count": len(row_ids) if row_ids else 0})
    
    if not selected_user or not row_ids:
        raise PreventUpdate
    
    # Extraire l'uid de l'utilisateur sélectionné
    selected_uid = None
    if isinstance(selected_user, dict) and "uid" in selected_user:
        selected_uid = selected_user["uid"]
    else:
        selected_uid = selected_user
    
    # UID sélectionné nettoyé, la suite applique juste les styles
    
    # Préparer les styles pour chaque ligne (styles de base uniquement)
    styles = []
    classes = []
    button_colors = []
    button_outlines = []
    
    # Styles pour les lignes
    for row_id in row_ids:
        if isinstance(row_id, dict) and "index" in row_id:
            uid = row_id["index"]
            is_selected = str(uid) == str(selected_uid)
            # Appliquer uniquement les styles de base; l'accentuation vient de la classe CSS
            style = {
                "transition": "all 0.2s",
                "cursor": "pointer",
            }

            # Classe pour la ligne
            class_name = "user-row selected-user-row" if is_selected else "user-row"
            
            styles.append(style)
            classes.append(class_name)
        else:
            # Valeur par défaut si row_id n'est pas au format attendu
            styles.append({"transition": "all 0.2s", "cursor": "pointer"})
            classes.append("user-row")
    
    # Styles pour les boutons
    for button_id in button_ids:
        if isinstance(button_id, dict) and "index" in button_id:
            uid = button_id["index"]
            is_selected = str(uid) == str(selected_uid)
            
            # Couleur et outline du bouton
            button_colors.append("danger" if is_selected else "light")
            button_outlines.append(not is_selected)
        else:
            # Valeur par défaut
            button_colors.append("light")
            button_outlines.append(True)
    
    return styles, classes, button_colors, button_outlines

