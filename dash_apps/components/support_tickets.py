import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import pandas as pd
from datetime import datetime
import uuid


# Fonction de conversion de format de date robuste
def parse_date(date_str):
    """
    Fonction utilitaire pour parser des dates dans différents formats.
    
    Args:
        date_str: La date sous forme de chaîne de caractères à convertir
    
    Returns:
        Objet datetime
    """
    if not isinstance(date_str, str):
        return date_str
        
    formats = [
        "%Y-%m-%d %H:%M:%S",     # Format standard
        "%Y-%m-%dT%H:%M:%S",     # Format ISO
        "%Y-%m-%dT%H:%M:%S.%f",  # Format ISO avec microsecondes
        "%Y-%m-%d"              # Date simple
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    print(f"[WARNING] Format de date non reconnu: {date_str}")
    return datetime.now()


def render_tickets_list(tickets, selected_ticket_id=None):
    """
    Affiche la liste des tickets de support
    
    Args:
        tickets: Liste des tickets de support
        selected_ticket_id: ID du ticket sélectionné
    
    Returns:
        Un composant Dash pour afficher la liste des tickets
    """
    if not tickets:
        return dbc.Alert("Aucun ticket disponible", color="warning")
    
    # Créer la liste des tickets
    ticket_items = []
    
    for i, ticket in enumerate(tickets):
        status_colors = {
            "open": "danger",
            "in progress": "warning",
            "closed": "success"
        }
        
        status_badges = {
            "open": "Ouvert",
            "in progress": "En cours",
            "closed": "Fermé"
        }
        
        # Utiliser la fonction parse_date pour convertir la date
        date_obj = parse_date(ticket["created_at"])
        formatted_date = date_obj.strftime("%d/%m/%Y")
        
        # Style pour le ticket sélectionné
        selected = ticket["ticket_id"] == selected_ticket_id if selected_ticket_id else False
        row_style = {
            "padding": "10px",
            "borderLeft": "4px solid #3498db" if selected else "none",
            "backgroundColor": "#f8f9fa" if selected else "white",
            "borderRadius": "5px",
            "marginBottom": "8px",
            "cursor": "pointer",
            "transition": "all 0.2s",
            "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.08)"
        }
        
        ticket_items.append(
            html.Div([
                html.Div([
                    html.Div([
                        html.Strong(ticket["objet"], className="d-block"),
                        html.Small([
                            "De: ", 
                            html.Span(ticket["user_id"], style={"fontStyle": "italic"})
                        ], className="text-muted"),
                    ], style={"flex": "1"}),
                    html.Div([
                        dbc.Badge(status_badges.get(ticket["status"], ticket["status"]), 
                                 color=status_colors.get(ticket["status"], "secondary"),
                                 className="mb-1"),
                        html.Div(formatted_date, className="small text-muted text-end")
                    ], style={"textAlign": "right"})
                ], style={"display": "flex", "justifyContent": "space-between"})
            ], 
            style=row_style, 
            id={"type": "ticket-item", "index": i},
            className="ticket-row"
            )
        )
    
    # Appliquer les styles directement dans le conteneur
    return html.Div(
        ticket_items,
        # Nous utilisons le style inline pour l'effet hover via la prop className
        style={
            "maxHeight": "500px",
            "overflowY": "auto"
        },
        # Ajoutons un ID pour appliquer du CSS personnalisé dans app.py si nécessaire
        id="tickets-list"
    )


def render_ticket_details(ticket, comments):
    """
    Affiche les détails d'un ticket et ses commentaires
    
    Args:
        ticket: Le ticket à afficher
        comments: Liste des commentaires associés au ticket
    
    Returns:
        Un composant Dash pour afficher les détails du ticket
    """
    status_options = [
        {"label": "Ouvert", "value": "open"},
        {"label": "En cours", "value": "in progress"},
        {"label": "Fermé", "value": "closed"}
    ]
    
    # Formatter les dates en utilisant la fonction globale parse_date
    created_at = parse_date(ticket["created_at"])
    updated_at = parse_date(ticket["updated_at"])
    
    # Section détails
    details_section = html.Div([
        html.H4(ticket["objet"], className="mb-3"),
        
        # Info générales
        dbc.Row([
            dbc.Col([
                html.P([
                    html.Strong("Statut: "),
                    dbc.Badge(
                        {"open": "Ouvert", "in progress": "En cours", "closed": "Fermé"}.get(ticket["status"], ticket["status"]),
                        color={"open": "danger", "in progress": "warning", "closed": "success"}.get(ticket["status"], "secondary")
                    )
                ], className="mb-2"),
                html.P([
                    html.Strong("Utilisateur: "),
                    ticket["user_id"]
                ], className="mb-2"),
                html.P([
                    html.Strong("Créé le: "),
                    created_at.strftime("%d/%m/%Y %H:%M")
                ], className="mb-2"),
                html.P([
                    html.Strong("Mis à jour le: "),
                    updated_at.strftime("%d/%m/%Y %H:%M")
                ], className="mb-2"),
            ], width=6),
            dbc.Col([
                html.P([
                    html.Strong("Préférence de contact: "),
                    ticket["contact_preference"]
                ], className="mb-2"),
                html.P([
                    html.Strong("Téléphone: "),
                    ticket["phone"] if ticket["phone"] else "-"
                ], className="mb-2"),
                html.P([
                    html.Strong("E-mail: "),
                    ticket["mail"] if ticket["mail"] else "-"
                ], className="mb-2"),
            ], width=6),
        ], className="mb-4"),
        
        # Message
        dbc.Card([
            dbc.CardHeader("Message"),
            dbc.CardBody([
                html.P(ticket["message"])
            ])
        ], className="mb-4"),
        
        # Mise à jour du statut
        dbc.Card([
            dbc.CardHeader("Mettre à jour le statut"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(
                            id="status-dropdown",
                            options=status_options,
                            value=ticket["status"],
                            clearable=False
                        )
                    ], width=9),
                    dbc.Col([
                        dbc.Button(
                            "Mettre à jour", 
                            id="update-status-button", 
                            color="primary",
                            className="w-100"
                        )
                    ], width=3),
                ])
            ])
        ], className="mb-4"),
    ])
    
    # Section commentaires
    comments_header = html.Div([
        html.H5("Commentaires", className="mb-3"),
        html.Hr()
    ]) if comments else html.Div([
        html.H5("Commentaires", className="mb-3"),
        html.P("Aucun commentaire pour ce ticket", className="text-muted"),
        html.Hr()
    ])
    
    comments_items = []
    for comment in comments:
        # Utiliser la fonction parse_date pour gérer tous les formats de date
        comment_date = parse_date(comment["created_at"])
        
        # Différencier les commentaires admin/utilisateur
        is_admin = comment["user_id"] == "admin"
        comment_style = {
            "backgroundColor": "#f0f7ff" if is_admin else "#f8f9fa",
            "borderLeft": f"4px solid {'#3498db' if is_admin else '#7f8c8d'}",
            "padding": "12px 15px",
            "borderRadius": "5px",
            "marginBottom": "12px"
        }
        
        comments_items.append(html.Div([
            html.Div([
                html.Strong(
                    f"{'Support technique' if is_admin else comment['user_id']}",
                    style={"color": "#3498db" if is_admin else "#7f8c8d"}
                ),
                html.Small(
                    comment_date.strftime("%d/%m/%Y %H:%M"),
                    className="text-muted ms-2"
                )
            ], className="mb-2"),
            html.P(comment["comment_text"], style={"marginBottom": "0"})
        ], style=comment_style))
    
    # Section ajouter un commentaire
    add_comment_section = html.Div([
        html.H5("Ajouter un commentaire", className="mb-3"),
        dbc.Textarea(
            id="comment-input",
            placeholder="Votre commentaire...",
            style={"height": "100px", "marginBottom": "10px"}
        ),
        dbc.Button(
            "Ajouter un commentaire", 
            id="add-comment-button", 
            color="primary"
        )
    ])
    
    return html.Div([
        details_section,
        comments_header,
        html.Div(comments_items, className="mb-4"),
        add_comment_section
    ])


def update_ticket_status(ticket_id, new_status, tickets_data):
    """
    Met à jour le statut d'un ticket
    
    Args:
        ticket_id: ID du ticket à mettre à jour
        new_status: Nouveau statut à appliquer
        tickets_data: Données des tickets
    
    Returns:
        Les données des tickets mises à jour
    """
    updated_data = tickets_data.copy()
    
    for i, ticket in enumerate(updated_data["tickets"]):
        if ticket["ticket_id"] == ticket_id:
            updated_data["tickets"][i]["status"] = new_status
            updated_data["tickets"][i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    
    return updated_data


def add_ticket_comment(ticket_id, comment_text, user_id, tickets_data):
    """
    Ajoute un commentaire à un ticket
    
    Args:
        ticket_id: ID du ticket auquel ajouter un commentaire
        comment_text: Texte du commentaire
        user_id: ID de l'utilisateur qui ajoute le commentaire
        tickets_data: Données des tickets
    
    Returns:
        Les données des tickets mises à jour
    """
    updated_data = tickets_data.copy()
    
    # Créer un nouveau commentaire
    new_comment = {
        "comment_id": str(uuid.uuid4()),
        "ticket_id": ticket_id,
        "user_id": user_id,
        "comment_text": comment_text,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Ajouter le commentaire
    if ticket_id not in updated_data["comments"]:
        updated_data["comments"][ticket_id] = []
    
    updated_data["comments"][ticket_id].append(new_comment)
    
    # Mettre à jour la date de mise à jour du ticket
    for i, ticket in enumerate(updated_data["tickets"]):
        if ticket["ticket_id"] == ticket_id:
            updated_data["tickets"][i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    
    return updated_data
