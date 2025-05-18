from dash import html, dcc, Input, Output, State, callback, callback_context
import dash_bootstrap_components as dbc
from flask_login import current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dash_apps.auth.models import User
import json

# Configuration SQLAlchemy
engine = create_engine('sqlite:///users.db')
DBSession = sessionmaker(bind=engine)

def is_admin():
    """Vu00e9rifie si l'utilisateur actuel est admin"""
    return current_user.is_authenticated and current_user.admin

def render_members_list():
    """Rend le tableau des membres avec leurs tags"""
    # Cru00e9ation d'une session pour accu00e9der u00e0 la base de donnu00e9es
    db_session = DBSession()
    users = db_session.query(User).all()
    db_session.close()
    
    rows = []
    for user in users:
        tag_badges = []
        for tag in user.get_tags_list():
            tag_badge = dbc.Badge(
                tag,
                color="primary",
                className="me-1 mb-1",
                id={"type": "tag-badge", "user_id": user.id, "tag": tag},
                style={"cursor": "pointer"} if is_admin() else {}
            )
            tag_badges.append(tag_badge)
        
        # Composant pour ajouter un tag si admin
        tag_input = html.Div([
            dbc.InputGroup(
                [
                    dbc.Input(id={"type": "new-tag-input", "user_id": user.id}, placeholder="Nouveau tag", size="sm"),
                    dbc.Button("+", id={"type": "add-tag-btn", "user_id": user.id}, color="success", size="sm"),
                ],
                size="sm",
                className="mt-1"
            )
        ]) if is_admin() else None
        
        # Ligne du tableau pour l'utilisateur
        row = html.Tr([
            html.Td(
                html.Div([
                    html.Img(src=user.profile_pic, style={"width": "32px", "height": "32px", "borderRadius": "50%", "marginRight": "10px"}) if user.profile_pic else None,
                    html.Span(user.name or "Sans nom")
                ], style={"display": "flex", "alignItems": "center"})
            ),
            html.Td(user.email),
            html.Td(
                html.Div([
                    html.Div(tag_badges, className="d-flex flex-wrap"),
                    tag_input
                ])
            ),
            html.Td(
                dbc.Badge("Admin", color="danger", className="me-1") if user.admin else ""
            ),
            html.Td(
                dbc.Form(
                    dbc.Switch(
                        id={"type": "user-active-switch", "user_id": user.id},
                        value=user.active,
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
    
    # Ajouter le tag
    db_session = DBSession()
    user = db_session.query(User).get(user_id)
    if user:
        user.add_tag(tag_value)
        db_session.commit()
    db_session.close()
    
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
    
    # Supprimer le tag
    db_session = DBSession()
    user = db_session.query(User).get(user_id)
    if user:
        user.remove_tag(tag)
        db_session.commit()
    db_session.close()
    
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
    
    # Mettre à jour le statut de l'utilisateur
    db_session = DBSession()
    user = db_session.query(User).get(user_id)
    if user:
        user.active = active_value
        db_session.commit()
    db_session.close()
    
    return ""
