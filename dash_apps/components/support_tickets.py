import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
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
    Affiche les détails d'un ticket et ses commentaires en utilisant des composants Dash natifs
    
    Args:
        ticket: Le ticket à afficher
        comments: Liste des commentaires associés au ticket
    
    Returns:
        Un composant Dash pour afficher les détails du ticket
    """
    
    # Définir les classes et textes selon le statut
    status = ticket.get("status", "PENDING")
    status_mapping = {
        "PENDING": {"color": "warning", "text": "En attente"},
        "CLOSED": {"color": "success", "text": "Fermé"}
    }
    
    # Valeurs par défaut si le statut n'est pas reconnu
    status_info = status_mapping.get(status, {"color": "secondary", "text": status})
    
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
    
    # Inverser pour afficher les plus récents en premier
    formatted_comments.reverse()
    
    # Section fixe - Informations du ticket
    fixed_section = dbc.Card([
        dbc.CardBody([
            # Titre du ticket
            html.H4(ticket.get('subject', 'Sans objet'), className="mb-3"),
            
            # Formulaire de mise à jour du statut
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
            ], className="mb-3"),


            
            # Informations du ticket en grille
            dbc.Row([
                dbc.Col([
                    html.P([html.Strong("N° Ticket: "), html.Span(ticket.get("ticket_id", "N/A"))], className="mb-1"),
                    html.P([html.Strong("Statut: "), dbc.Badge(status_info["text"], color=status_info["color"])], className="mb-1"),
                    html.P([
                        html.Strong("Utilisateur: "),
                        html.Span(ticket.get("user_id", "-")),
                        dcc.Clipboard(
                            target_id=None,
                            title="Copier l'ID utilisateur",
                            style={"marginLeft": "5px", "display": "inline-block", "verticalAlign": "middle",
                                   "cursor": "pointer", "fontSize": "1.2rem"},
                            content=ticket.get("user_id", "-"),
                            className="copy-btn"
                        )
                    ], className="mb-1"),
                    html.P([html.Strong("Créé le: "), html.Span(created_at.strftime("%d/%m/%Y %H:%M"))], className="mb-1"),
                ], width=6),
                dbc.Col([
                    html.P([html.Strong("Mis à jour le: "), html.Span(updated_at.strftime("%d/%m/%Y %H:%M"))], className="mb-1"),
                    html.P([html.Strong("Préférence de contact: "), html.Span(ticket.get("contact_preference", "-"))], className="mb-1"),
                    html.P([
                        html.Strong("Téléphone: "),
                        html.Span(ticket.get("phone", "-")),
                        dcc.Clipboard(
                            target_id=None,
                            title="Copier le numéro de téléphone", 
                            style={"marginLeft": "5px", "display": "inline-block", "verticalAlign": "middle",
                                   "cursor": "pointer", "fontSize": "1.2rem"},
                            content=ticket.get("phone", "-"),
                            className="copy-btn"
                        )
                    ], className="mb-1"),
                    html.P([
                        html.Strong("E-mail: "),
                        html.Span(ticket.get("mail", "-")),
                        dcc.Clipboard(
                            target_id=None,
                            title="Copier l'adresse email", 
                            style={"marginLeft": "5px", "display": "inline-block", "verticalAlign": "middle",
                                   "cursor": "pointer", "fontSize": "1.2rem"},
                            content=ticket.get("mail", "-"),
                            className="copy-btn"
                        )
                    ], className="mb-1"),
                ], width=6),
            ], className="mb-3"),
            
            # Message du ticket
            dbc.Card(
                dbc.CardBody(ticket.get('message', 'Pas de message')),
                className="mb-3"
            ),
        ])
    ], className="mb-3")
    
    # Section défilante - Commentaires
    comment_form = dbc.Card([
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
    ], className="mb-3")
    
    # Liste des commentaires - style fluide et continu
    comments_container = []
    if formatted_comments:
        comments_list = []
        for comment in formatted_comments:
            comment_item = html.Div([
                # En-tête avec auteur et date
                html.Div([
                    html.Span(comment["author_id"], style={
                        "fontWeight": "bold", 
                        "color": "#3A506B"  # Couleur pour faire ressortir le nom
                    }),
                    html.Span(comment["formatted_date"], 
                             style={"float": "right", "fontSize": "0.85rem", "color": "#777"}),
                ], style={
                    "borderBottom": "1px solid #eaeaea",
                    "paddingBottom": "4px",
                    "marginBottom": "8px"
                }),
                # Contenu du commentaire
                html.P(comment["content"], style={"marginBottom": "5px"})
            ], className="comment-item", style={
                "padding": "12px 15px",
                "marginBottom": "12px",
                "borderLeft": "3px solid #dee2e6",
                "backgroundColor": "#f8f9fa",
                "borderRadius": "4px"
            })
            comments_list.append(comment_item)
        comments_container = comments_list
    else:
        comments_container = [html.P("Aucun commentaire pour l'instant", className="text-muted")]
    
    # Scrollable section with comments
    scrollable_section = html.Div([
        html.H5(f"Commentaires ({len(formatted_comments)})", className="mb-3"),
        comment_form,
        html.Hr(),
        html.Div(comments_container, style={"maxHeight": "800px", "overflowY": "auto"}),
    ], className="mt-3", id="comment-form")
    
    # Section détails avec une structure fixe et défilante
    details_section = html.Div([
        # Section fixe (infos ticket et statut)
        fixed_section,
        # Section défilante (commentaires avec formulaire au début)
        scrollable_section
    ])
    
    # Retourner directement la section de détails qui contient déjà tout ce dont nous avons besoin
    return details_section


# La fonction register_copy_callbacks a été supprimée car nous utilisons maintenant dcc.Clipboard qui intègre déjà la fonctionnalité de copie
