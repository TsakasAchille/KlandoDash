from dash import html, dcc, Input, Output, State, callback, callback_context
import dash
import json
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash_apps.config import Config
from dash_apps.repositories.user_repository import UserRepository

# Store pour gérer la pagination de manière locale sans déclencher le callback principal
def render_custom_users_table(users, current_page, total_users, selected_uid=None):
    """Rendu d'un tableau personnalisé avec pagination manuelle
    
    Args:
        users: Liste des utilisateurs à afficher
        current_page: Page courante (1-indexed)
        total_users: Nombre total d'utilisateurs
        selected_uid: UID de l'utilisateur sélectionné
    
    Returns:
        Un composant HTML avec un tableau et des contrôles de pagination
    """
    print(f"\n[DEBUG] render_custom_users_table appelé avec selected_uid = {selected_uid}, type: {type(selected_uid)}")
    page_size = Config.USERS_TABLE_PAGE_SIZE
    page_count = (total_users - 1) // page_size + 1 if total_users > 0 else 1
    
    # Créer les en-têtes du tableau
    headers = ["", "Nom", "Email", "Téléphone", "Rôle", "Genre", "Notation", "Date d'inscription"]
    
    # Créer les lignes du tableau
    table_rows = []
    for user in users:
        # Pour les objets Pydantic (UserSchema)
        if hasattr(user, "model_dump"):
            # Convertir l'objet Pydantic en dictionnaire
            user_dict = user.model_dump()
            uid = user_dict.get("uid", "")
            name = user_dict.get("display_name", "")
            email = user_dict.get("email", "")
            phone = user_dict.get("phone_number", "")
            role = user_dict.get("role", "")
            gender = user_dict.get("gender", "")
            rating = user_dict.get("rating", None)
            created_at = user_dict.get("created_at", "")
        # Pour les dictionnaires
        elif isinstance(user, dict):
            uid = user.get("uid", "")
            name = user.get("display_name", "")
            email = user.get("email", "")
            phone = user.get("phone_number", "")
            role = user.get("role", "")
            gender = user.get("gender", "")
            rating = user.get("rating", None)
            created_at = user.get("created_at", "")
        # Pour les objets avec attributs
        else:
            uid = getattr(user, "uid", "")
            name = getattr(user, "display_name", "")
            email = getattr(user, "email", "")
            phone = getattr(user, "phone_number", "")
            role = getattr(user, "role", "")
            gender = getattr(user, "gender", "")
            rating = getattr(user, "rating", None)
            created_at = getattr(user, "created_at", "")
            
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

            
        # Style pour la ligne sélectionnée - en rouge très vif avec bordure
        row_style = {
            "backgroundColor": "#ff3547 !important" if is_selected else "transparent",
            "transition": "all 0.2s",
            "cursor": "pointer",
            "border": "2px solid #dc3545 !important" if is_selected else "none",
            "color": "white !important" if is_selected else "inherit",
            "fontWeight": "bold !important" if is_selected else "normal",
        }
        
        # Style pour chaque cellule de la ligne
        cell_style = {"backgroundColor": "#ff3547 !important" if is_selected else "transparent"}
        
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
            html.Td(name, style=cell_style),
            html.Td(email, style=cell_style),
            html.Td(phone, style=cell_style),
            html.Td(role, style=cell_style),
            # Afficher le genre avec formatage
            html.Td(
                {"man": "Homme", "woman": "Femme", "male": "Homme", "female": "Femme", "helicopter": "🚁 Helicopter", "other": "Autre"}.get(gender, "-"),
                style=cell_style
            ),
            # Afficher le rating avec formatage
            html.Td(
                f"{rating:.1f} ★" if rating is not None else "-",
                style={**cell_style, "fontWeight": "bold" if rating and rating >= 4.0 else "normal"}
            ),
            html.Td(created_at, style=cell_style),
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
    print("\n[DEBUG] handle_pagination_buttons")
    print("prev_clicks", prev_clicks)
    print("next_clicks", next_clicks)
    print("current_page", current_page)
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
        print("max(1, current_page - 1)", max(1, current_page - 1))
        return max(1, current_page - 1)
    elif button_id == "next-page-btn":
        # On vérifiera que la page n'est pas trop grande dans le callback qui utilise cette valeur
        print("current_page + 1", current_page + 1)
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
    print("\n[DEBUG] Début callback handle_row_selection")
    print(f"\n[DEBUG] row_clicks: {row_clicks}")
    
    ctx = callback_context
    if not ctx.triggered:
        print("\n[DEBUG] Pas de déclencheur, PreventUpdate")
        raise PreventUpdate
    
    # Vérifier si le callback est déclenché lors du chargement initial
    # Les clicks seront tous à zéro lors du chargement initial
    if not any(clicks > 0 for clicks in row_clicks):
        print("\n[DEBUG] Tous les clicks sont à zéro, probablement un chargement initial, PreventUpdate")
        raise PreventUpdate
    
    # Déterminer ce qui a été cliqué
    clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]
    print(f"\n[DEBUG] clicked_id: {clicked_id}")
    
    try:
        # Extraire l'index (uid) de l'ID JSON
        id_dict = json.loads(clicked_id)
        uid = id_dict["index"]
        print(f"\n[DEBUG] Ligne cliquée, uid extrait: {uid}")
        
        # Retourner l'UID extrait
        return {"uid": uid}
    except Exception as e:
        print(f"\n[ERROR] Erreur extraction uid: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise PreventUpdate

# 3. Nouveau callback pour gérer uniquement la mise en surbrillance des lignes


@callback(
    Output({"type": "user-row", "index": dash.ALL}, "style"),
    Output({"type": "user-row", "index": dash.ALL}, "className"),
    Output({"type": "select-user-btn", "index": dash.ALL}, "color"),
    Output({"type": "select-user-btn", "index": dash.ALL}, "outline"),
   # Input("selected-user-from-table", "data"),
    Input("selected-user-uid", "data"),

    State({"type": "user-row", "index": dash.ALL}, "id"),
    State({"type": "select-user-btn", "index": dash.ALL}, "id"),
    prevent_initial_call=True
)
def highlight_selected_row(selected_user, row_ids, button_ids):

    print("\n[DEBUG] Début callback highlight_selected_row")
    print(f"\n[DEBUG] selected_user: {selected_user}")
    
    if not selected_user or not row_ids:
        raise PreventUpdate
    
    # Extraire l'uid de l'utilisateur sélectionné
    selected_uid = None
    if isinstance(selected_user, dict) and "uid" in selected_user:
        selected_uid = selected_user["uid"]
    else:
        selected_uid = selected_user
    
    print(f"\n[DEBUG] UID utilisateur sélectionné: {selected_uid}")
    
    # Préparer les styles pour chaque ligne
    styles = []
    classes = []
    button_colors = []
    button_outlines = []
    
    # Styles pour les lignes
    for row_id in row_ids:
        if isinstance(row_id, dict) and "index" in row_id:
            uid = row_id["index"]
            is_selected = str(uid) == str(selected_uid)
            
            # Exactement les mêmes styles que ceux définis initialement
            style = {
                "backgroundColor": "#ff3547 !important" if is_selected else "transparent",
                "transition": "all 0.2s",
                "cursor": "pointer",
                "border": "2px solid #dc3545 !important" if is_selected else "none",
                "color": "white !important" if is_selected else "inherit",
                "fontWeight": "bold !important" if is_selected else "normal",
            }
            
            # Classe pour la ligne
            class_name = "user-row selected-user-row" if is_selected else "user-row"
            
            styles.append(style)
            classes.append(class_name)
        else:
            # Valeur par défaut si row_id n'est pas au format attendu
            styles.append({})
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

