from dash import html, dcc, Input, Output, State, callback, callback_context
import dash_bootstrap_components as dbc
from flask_login import current_user
from dash_apps.repositories.repository_factory import RepositoryFactory
import json

def is_admin():
    """Vérifie si l'utilisateur actuel est admin"""
    return current_user.is_authenticated and current_user.admin

def render_members_list():
    """Rend le tableau des membres avec leurs tags"""
    # Récupération des utilisateurs via REST API
    try:
        user_repository = RepositoryFactory.get_user_repository()
        users = user_repository.list_users()
    except Exception as e:
        print(f"Erreur lors de la récupération des utilisateurs: {e}")
        users = []
    
    rows = []
    for user in users:
        tag_badges = []
        # Gérer les tags (supposons qu'ils sont stockés dans un champ 'tags' ou similaire)
        user_tags = user.get('tags', []) if isinstance(user.get('tags'), list) else []
        for tag in user_tags:
            tag_badge = dbc.Badge(
                tag,
                color="primary",
                className="me-1 mb-1",
                id={"type": "tag-badge", "user_id": user.get('uid'), "tag": tag},
                style={"cursor": "pointer"} if is_admin() else {}
            )
            tag_badges.append(tag_badge)
        
        # Composant pour ajouter un tag si admin
        tag_input = html.Div([
            dbc.InputGroup(
                [
                    dbc.Input(id={"type": "new-tag-input", "user_id": user.get('uid')}, placeholder="Nouveau tag", size="sm"),
                    dbc.Button("+", id={"type": "add-tag-btn", "user_id": user.get('uid')}, color="success", size="sm"),
                ],
                size="sm",
                className="mt-1"
            )
        ]) if is_admin() else None
        
        # Ligne du tableau pour l'utilisateur
        row = html.Tr([
            html.Td(
                html.Div([
                    html.Img(src=user.get('profile_pic'), style={"width": "32px", "height": "32px", "borderRadius": "50%", "marginRight": "10px"}) if user.get('profile_pic') else None,
                    html.Span(user.get('display_name') or user.get('name') or "Sans nom")
                ], style={"display": "flex", "alignItems": "center"})
            ),
            html.Td(user.get('email', '')),
            html.Td(
                html.Div([
                    html.Div(tag_badges, className="d-flex flex-wrap"),
                    tag_input
                ])
            ),
            html.Td(
                dbc.Badge("Admin", color="danger", className="me-1") if user.get('admin') else ""
            ),
            html.Td(
                dbc.Form(
                    dbc.Switch(
                        id={"type": "user-active-switch", "user_id": user.get('uid')},
                        value=user.get('active', True),
                        label="Actif",
                        disabled=not is_admin()
                    )
                )
            )
        ])
        rows.append(row)
    
    # Tableau des membres
    return html.Div([
        html.H2("Gestion des membres", className="mt-3 mb-4"),
        dbc.Table([
            html.Thead(
                html.Tr([
                    html.Th("Nom"),
                    html.Th("Email"),
                    html.Th("Tags"),
                    html.Th("Rôle"),
                    html.Th("Statut")
                ])
            ),
            html.Tbody(rows)
        ], striped=True, bordered=True, hover=True)
    ])

# Callback pour gérer l'ajout de tag
@callback(
    Output({"type": "new-tag-input", "user_id": "ALL"}, "value"),
    Input({"type": "add-tag-btn", "user_id": "ALL"}, "n_clicks"),
    State({"type": "new-tag-input", "user_id": "ALL"}, "value"),
    prevent_initial_call=True
)
def add_tag(n_clicks, tag_value):
    """Ajoute un tag à un utilisateur"""
    if not n_clicks or not tag_value:
        return ""
    
    # Vérifier les permissions
    if not is_admin():
        return tag_value
    
    # Récupérer l'ID utilisateur du contexte du callback
    ctx = callback_context
    if not ctx.triggered:
        return ""
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    prop_id = json.loads(trigger_id)
    user_id = prop_id['user_id']
    
    # Ajouter le tag via REST API
    try:
        user_repository = RepositoryFactory.get_user_repository()
        user = user_repository.get_user(user_id)
        if user:
            # Pour l'instant, on simule l'ajout de tag
            # Cette fonctionnalité devra être implémentée dans l'API REST
            print(f"TODO: Implémenter l'ajout de tag '{tag_value}' pour l'utilisateur {user_id}")
    except Exception as e:
        print(f"Erreur lors de l'ajout du tag: {e}")
    
    # Vider le champ après ajout
    return ""

# Callback pour supprimer un tag (lorsqu'on clique sur un badge)
@callback(
    Output("dummy-output", "children"),
    Input({"type": "tag-badge", "user_id": "ALL", "tag": "ALL"}, "n_clicks"),
    prevent_initial_call=True
)
def remove_tag(n_clicks):
    """Supprime un tag lorsqu'on clique dessus (admins uniquement)"""
    ctx = callback_context
    if not ctx.triggered or not n_clicks:
        return ""
    
    # Vérifier les permissions
    if not is_admin():
        return ""
    
    # Extraire les informations du badge cliqué
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    tag_info = json.loads(trigger_id)
    user_id = tag_info["user_id"]
    tag = tag_info["tag"]
    
    # Supprimer le tag via REST API
    try:
        user_repository = RepositoryFactory.get_user_repository()
        user = user_repository.get_user(user_id)
        if user:
            # Pour l'instant, on simule la suppression de tag
            # Cette fonctionnalité devra être implémentée dans l'API REST
            print(f"TODO: Implémenter la suppression de tag '{tag}' pour l'utilisateur {user_id}")
    except Exception as e:
        print(f"Erreur lors de la suppression du tag: {e}")
    
    return ""

# Callback pour changer le statut actif d'un utilisateur
@callback(
    Output("dummy-output-2", "children"),
    Input({"type": "user-active-switch", "user_id": "ALL"}, "value"),
    prevent_initial_call=True
)
def toggle_user_active(active_value):
    """Change le statut actif d'un utilisateur"""
    # Vérifier les permissions
    if not is_admin():
        return ""
    
    # Récupérer l'ID utilisateur du contexte    
    ctx = callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    prop_id = json.loads(trigger_id)
    user_id = prop_id["user_id"]
    
    # Mettre à jour le statut de l'utilisateur via REST API
    try:
        user_repository = RepositoryFactory.get_user_repository()
        user_repository.update_user(user_id, {'active': active_value})
    except Exception as e:
        print(f"Erreur lors de la mise à jour du statut utilisateur: {e}")
    
    return ""
