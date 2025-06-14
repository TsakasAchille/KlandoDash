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
    
    for ticket in tickets:
        # Définir les classes et textes selon le statut
        status = ticket.get("status", "PENDING")
        status_mapping = {
            "PENDING": {"color": "warning", "text": "En attente"},
            "CLOSED": {"color": "success", "text": "Fermé"}
        }
        
        # Valeurs par défaut si le statut n'est pas reconnu
        status_info = status_mapping.get(status, {"color": "secondary", "text": status})
        
        # Formater la date
        date_obj = parse_date(ticket["created_at"])
        formatted_date = date_obj.strftime("%d/%m/%Y")
        
        # Style pour le ticket sélectionné
        is_selected = ticket["ticket_id"] == selected_ticket_id if selected_ticket_id else False
        
        # Si le ticket est sélectionné, on utilise une bordure bleue
        # Sinon, on n'ajoute pas de bordure colorée spécifique
        border_style = f"4px solid #3498db" if is_selected else "1px solid #eee"
        
        ticket_style = {
            "padding": "10px",
            "borderLeft": border_style,
            "backgroundColor": "#f8f9fa" if is_selected else "white",
            "borderRadius": "5px",
            "marginBottom": "8px",
            "cursor": "pointer",
            "transition": "all 0.2s",
            "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.08)"
        }
        
        # Créer l'élément ticket cliquable
        ticket_items.append(
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(ticket["subject"], style={"fontWeight": "600", "marginBottom": "4px"}),
                                    html.Div(["De: ", html.Span(ticket["user_id"], style={"fontStyle": "italic"})], style={"fontSize": "12px", "color": "#666"})
                                ],
                                style={"flex": "1"}
                            ),
                            html.Div(
                                [
                                    dbc.Badge(status_info["text"], color=status_info["color"], className="mb-1"),
                                    html.Div(formatted_date, style={"fontSize": "11px", "color": "#999", "textAlign": "right"})
                                ],
                                style={"textAlign": "right"}
                            )
                        ],
                        style={"display": "flex", "justifyContent": "space-between"}
                    )
                ],
                style=ticket_style,
                id={"type": "ticket-item", "index": ticket["ticket_id"]},
                className="ticket-row"
            )
        )
    
    # Ajouter le style CSS pour l'effet hover avec un iframe invisible
    hover_css = '''
    <style>
        .ticket-row:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12) !important;
            transition: all 0.2s ease;
        }
    </style>
    '''
    
    # Retourner la liste des tickets avec le style hover intégré dans un iframe invisible
    return html.Div(
        [
            # Iframe invisible pour injecter le CSS
            html.Iframe(srcDoc=hover_css, style={'display': 'none'}),
            # Liste des tickets
            *ticket_items
        ],
        id="tickets-list",
        style={"maxHeight": "500px"}
    )


def render_ticket_details(ticket, comments):
    """
    Affiche les détails d'un ticket et ses commentaires en utilisant un template Jinja2
    
    Args:
        ticket: Le ticket à afficher
        comments: Liste des commentaires associés au ticket
    
    Returns:
        Un composant Dash pour afficher les détails du ticket
    """
    # Importer l'utilitaire de rendu de template
    from dash_apps.utils.template_utils import render_template_with_iframe
    
    # Définir les classes et textes selon le statut
    status = ticket.get("status", "PENDING")
    status_mapping = {
        "PENDING": {"class": "warning", "text": "En attente"},
        "CLOSED": {"class": "success", "text": "Fermé"}
    }
    
    # Valeurs par défaut si le statut n'est pas reconnu
    status_info = status_mapping.get(status, {"class": "secondary", "text": status})
    
    # Formatter les dates
    created_at = parse_date(ticket["created_at"])
    updated_at = parse_date(ticket["updated_at"])
    
    # Formater les commentaires
    formatted_comments = []
    for comment in comments if comments else []:
        comment_date = parse_date(comment.get("created_at", ""))
        # Utiliser user_name s'il existe, sinon utiliser user_id
        author_name = comment.get("user_name", comment.get("user_id", "Système"))
        formatted_comments.append({
            "author_id": author_name,  # Utiliser le nom de l'utilisateur
            "content": comment.get("comment_text", ""),  # Utiliser comment_text au lieu de content
            "formatted_date": comment_date.strftime("%d/%m/%Y %H:%M")
        })
    
    # Contexte à passer au template
    context = {
        "ticket": ticket,
        "status_class": status_info["class"],
        "status_text": status_info["text"],
        "created_date": created_at.strftime("%d/%m/%Y %H:%M"),
        "updated_date": updated_at.strftime("%d/%m/%Y %H:%M"),
        "comments": formatted_comments
    }
    
    # Rendre le template dans un iframe
    iframe = render_template_with_iframe(
        "support_ticket_details_template.jinja2", 
        context,
        height="500px",
        width="100%"
    )
    
    # Section détails avec l'iframe et les formulaires interactifs
    details_section = html.Div([
        # Iframe du template pour les détails du ticket
        iframe,
        
        # Formulaire de mise à jour du statut (toujours géré par Dash)
        html.Div([
            dbc.Card([
                dbc.CardHeader("Mettre à jour le statut"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                id={"type": "status-dropdown", "index": ticket["ticket_id"]},
                                options=[
                                    {"label": "En attente", "value": "PENDING"},
                                    {"label": "Fermé", "value": "CLOSED"}
                                ],
                                value=ticket["status"],
                                className="mb-2"
                            ),
                            dbc.Button(
                                "Mettre à jour",
                                id={"type": "update-status-btn", "index": ticket["ticket_id"]},
                                color="primary",
                                className="mt-2"
                            )
                        ])
                    ])
                ])
            ], className="mb-4")
        ], id="status-change-form"),
        
        # Formulaire d'ajout de commentaire (toujours géré par Dash)
        html.Div([
            dbc.Card([
                dbc.CardHeader("Ajouter un commentaire"),
                dbc.CardBody([
                    dbc.InputGroup([
                        dbc.Textarea(
                            id={"type": "comment-textarea", "index": ticket["ticket_id"]},
                            placeholder="Votre commentaire...",
                            style={"height": "80px", "resize": "none"}
                        )
                    ], className="mb-2"),
                    dbc.Button(
                        "Ajouter",
                        id={"type": "comment-btn", "index": ticket["ticket_id"]},
                        color="primary"
                    )
                ])
            ])
        ], id="comment-form")
    ])
    
    # Retourner directement la section de détails qui contient déjà tout ce dont nous avons besoin
    return details_section

