import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import re
import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
import pandas as pd
from datetime import datetime
import uuid


# Fonction de conversion de format de date robuste
def classify_ticket(ticket):
    """
    Classifie un ticket selon son type et sous-type
    
    Args:
        ticket: Le ticket à classifier
    
    Returns:
        dict: Classification du ticket avec type, sous-type et statut
    """
    subject = ticket.get('subject', '').lower()
    message = ticket.get('message', '').lower()
    status = ticket.get('status', 'OPEN')
    
    # Classification du type principal
    is_trip_report = '[signalement trajet]' in subject
    
    # Classification du sous-type basée sur le message
    subtype = None
    if '[conducteur absent]' in message or 'conducteur absent' in message:
        subtype = 'conducteur_absent'
    elif '[conducteur en retard]' in message or 'conducteur en retard' in message:
        subtype = 'conducteur_en_retard'
    elif '[autre]' in message:
        subtype = 'autre'
    
    return {
        'is_trip_report': is_trip_report,
        'type': 'signalement_trajet' if is_trip_report else 'autre',
        'subtype': subtype,
        'status': status,
        'is_open': status in ['OPEN', 'PENDING']
    }


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
        "%Y-%m-%d %H:%M:%S.%f",  # Format avec microsecondes (le plus courant dans les logs)
        "%Y-%m-%d %H:%M:%S",     # Format standard
        "%Y-%m-%dT%H:%M:%S.%f",  # Format ISO avec microsecondes
        "%Y-%m-%dT%H:%M:%S",     # Format ISO
        "%Y-%m-%d"              # Date simple
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
            
    # Essayer de traiter manuellement les microsecondes trop longues
    if '.' in date_str:
        try:
            # Tronquer les microsecondes à 6 chiffres maximum
            parts = date_str.split('.')
            if len(parts) == 2:
                microseconds = parts[1][:6].ljust(6, '0')  # Tronquer ou compléter à 6 chiffres
                normalized_date = f"{parts[0]}.{microseconds}"
                return datetime.strptime(normalized_date, "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            pass
            
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
    Affiche les détails d'un ticket avec un layout amélioré selon les spécifications
    
    Args:
        ticket: Le ticket à afficher
        comments: Liste des commentaires associés au ticket
    
    Returns:
        Un composant Dash pour afficher les détails du ticket
    """
    
    # Classifier le ticket
    classification = classify_ticket(ticket)
    
    # Définir les classes et textes selon le statut
    status = ticket.get("status", "PENDING")
    status_mapping = {
        "PENDING": {"color": "warning", "text": "En attente", "icon": "⏳"},
        "OPEN": {"color": "warning", "text": "Ouvert", "icon": "🔓"},
        "CLOSED": {"color": "success", "text": "Fermé", "icon": "✅"}
    }
    
    # Valeurs par défaut si le statut n'est pas reconnu
    status_info = status_mapping.get(status, {"color": "secondary", "text": status, "icon": "❓"})
    
    # Formatter les dates
    created_at = parse_date(ticket["created_at"])
    updated_at = parse_date(ticket["updated_at"])
    
    # Formater les commentaires avec types d'interaction
    formatted_comments = []
    for comment in comments if comments else []:
        # Convertir le schema en dictionnaire si nécessaire
        if hasattr(comment, 'model_dump'):
            comment_dict = comment.model_dump()
        elif hasattr(comment, 'dict'):
            comment_dict = comment.dict()
        else:
            comment_dict = dict(comment) if not isinstance(comment, dict) else comment
        
        comment_date = parse_date(comment_dict.get("created_at", ""))
        # Utiliser user_name s'il existe, sinon utiliser user_id
        author_name = comment_dict.get("user_name", comment_dict.get("user_id", "Système"))
        
        # Déterminer le type d'interaction basé sur les colonnes existantes
        comment_type = comment_dict.get("comment_type")
        comment_sent = comment_dict.get("comment_sent")
        comment_received = comment_dict.get("comment_received")
        comment_text = comment_dict.get("comment_text")
        comment_source = comment_dict.get("comment_source")  # Nouvelle colonne: mail ou phone
        
        print(f"DEBUG: Comment ID: {comment_dict.get('comment_id')}")
        print(f"DEBUG: comment_type: '{comment_type}'")
        print(f"DEBUG: comment_sent: '{comment_sent}'")
        print(f"DEBUG: comment_received: '{comment_received}'")
        print(f"DEBUG: comment_text: '{comment_text}'")
        print(f"DEBUG: comment_source: '{comment_source}'")
        
        # Logique pour déterminer le type d'affichage
        if comment_sent and comment_sent.strip():
            interaction_type = "comment_sent"
            content = comment_sent
            print(f"DEBUG: Utilisation comment_sent: '{content}'")
        elif comment_received and comment_received.strip():
            interaction_type = "comment_received"
            content = comment_received
            print(f"DEBUG: Utilisation comment_received: '{content}'")
        else:
            # Pour tous les autres cas (internal, external sans comment_sent/received)
            interaction_type = "internal" if comment_type != "external" else "external"
            content = comment_dict.get("comment_text", "")
            print(f"DEBUG: Utilisation comment_text: '{content}' (type: {interaction_type})")
        
        print(f"DEBUG: Contenu final: '{content}'")
        print("DEBUG: ---")
        
        formatted_comments.append({
            "author_id": author_name,
            "content": content,
            "formatted_date": comment_date.strftime("%d/%m/%Y %H:%M"),
            "interaction_type": interaction_type,
            "comment_type": comment_type,
            "comment_source": comment_source
        })
    
    # Les commentaires sont déjà triés par date décroissante depuis le repository
    # formatted_comments.reverse() - supprimé car maintenant inutile
    
    # Détecter un éventuel identifiant de trajet dans le sujet
    subject_text = ticket.get('subject', '') or ''
    subject_lower = subject_text.lower()
    trip_url = None
    if "[signalement trajet]" in subject_lower:
        # Chercher un identifiant commençant par TRIP-
        m = re.search(r"\bTRIP-[A-Za-z0-9\-]+\b", subject_text)
        if m:
            trip_id = m.group(0)
            trip_url = f"/trips?trip_id={trip_id}"

    # 1. BOX DE CLASSIFICATION DU TICKET
    classification_box = dbc.Card([
        dbc.CardHeader([
            html.H5("📋 Classification du Ticket", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Strong("Type: "),
                        dbc.Badge(
                            "🚗 Signalement trajet" if classification['is_trip_report'] else "📝 Autre",
                            color="info" if classification['is_trip_report'] else "secondary",
                            className="me-2"
                        )
                    ], className="mb-2"),
                    html.P([
                        html.Strong("Sous-type: "),
                        dbc.Badge(
                            {
                                'conducteur_absent': "❌ Conducteur absent",
                                'conducteur_en_retard': "⏰ Conducteur en retard", 
                                'autre': "❓ Autre"
                            }.get(classification['subtype'], "➖ Non spécifié"),
                            color={
                                'conducteur_absent': "danger",
                                'conducteur_en_retard': "warning",
                                'autre': "secondary"
                            }.get(classification['subtype'], "light"),
                            className="me-2"
                        )
                    ], className="mb-2"),
                ], width=6),
                dbc.Col([
                    html.P([
                        html.Strong("Statut: "),
                        dbc.Badge(
                            f"{status_info['icon']} {status_info['text']}",
                            color=status_info["color"],
                            className="me-2"
                        )
                    ], className="mb-2"),
                    # Bouton voir trajet si applicable
                    (dbc.Button("🔍 Voir trajet", color="primary", size="sm", href=trip_url, className="mb-2") if trip_url else html.Span()),
                ], width=6)
            ])
        ])
    ], className="mb-3")
    
    # 2. FORMULAIRE DE MISE À JOUR DU STATUT
    status_update_box = dbc.Card([
        dbc.CardHeader("⚙️ Mettre à jour le statut"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id={"type": "status-dropdown", "index": ticket["ticket_id"]},
                        options=[
                            {"label": "🔓 Ouvert", "value": "OPEN"},
                            {"label": "✅ Fermé", "value": "CLOSED"}
                        ],
                        value=ticket["status"],
                        className="mb-2"
                    ),
                    dbc.Button(
                        "Mettre à jour",
                        id={"type": "update-status-btn", "index": ticket["ticket_id"]},
                        color="primary",
                        size="sm"
                    )
                ], width=12)
            ])
        ])
    ], className="mb-3")
    
    # 3. INFORMATIONS DU TICKET
    info_box = dbc.Card([
        dbc.CardHeader("ℹ️ Informations du Ticket"),
        dbc.CardBody([
            html.H5(ticket.get('subject', 'Sans objet'), className="mb-3", style={"color": "#2c3e50"}),
            dbc.Row([
                dbc.Col([
                    html.P([html.Strong("N° Ticket: "), html.Span(ticket.get("ticket_id", "N/A"))], className="mb-2"),
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
                    ], className="mb-2"),
                    html.P([html.Strong("Créé le: "), html.Span(created_at.strftime("%d/%m/%Y %H:%M"))], className="mb-2"),
                ], width=6),
                dbc.Col([
                    html.P([html.Strong("Mis à jour le: "), html.Span(updated_at.strftime("%d/%m/%Y %H:%M"))], className="mb-2"),
                    html.P([html.Strong("Contact: "), html.Span(ticket.get("contact_preference", "-"))], className="mb-2"),
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
                    ], className="mb-2"),
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
                    ], className="mb-2"),
                ], width=6),
            ])
        ])
    ], className="mb-3")
    
    # 4. BOX MESSAGE
    message_box = dbc.Card([
        dbc.CardHeader("💬 Message du Client"),
        dbc.CardBody([
            html.Div(
                ticket.get('message', 'Pas de message'),
                style={
                    "backgroundColor": "#f8f9fa",
                    "padding": "15px",
                    "borderRadius": "8px",
                    "border": "1px solid #e9ecef",
                    "fontStyle": "italic",
                    "lineHeight": "1.6"
                }
            )
        ])
    ], className="mb-3")
    
    # 5. SECTION INTERACTIONS (anciennement Commentaires)
    interaction_form = dbc.Card([
        dbc.CardHeader("🔄 Nouvelles Interactions"),
        dbc.CardBody([
            # Sélecteur de type d'interaction
            dbc.Row([
                dbc.Col([
                    dbc.Label("Type d'interaction:"),
                    dbc.RadioItems(
                        id={"type": "interaction-type", "index": ticket["ticket_id"]},
                        options=[
                            {"label": "💭 Commentaire interne", "value": "internal"},
                            {"label": "📧 Réponse au client", "value": "client_response"}
                        ],
                        value="internal",
                        inline=True,
                        className="mb-3"
                    )
                ], width=12)
            ]),
            # Zone de texte pour l'interaction
            dbc.InputGroup([
                dbc.Textarea(
                    id={"type": "comment-textarea", "index": ticket["ticket_id"]},
                    placeholder="Votre commentaire ou réponse...",
                    style={"height": "100px", "resize": "none"}
                )
            ], className="mb-3"),
            # Boutons d'action
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "💾 Ajouter commentaire interne",
                        id={"type": "comment-btn", "index": ticket["ticket_id"]},
                        color="secondary",
                        size="sm",
                        className="me-2"
                    ),
                    dbc.Button(
                        "📤 Envoyer réponse client",
                        id={"type": "client-response-btn", "index": ticket["ticket_id"]},
                        color="primary" if ticket.get("contact_preference") == "mail" and ticket.get("mail") else "secondary",
                        size="sm",
                        disabled=not (ticket.get("contact_preference") == "mail" and ticket.get("mail")),
                        title="Envoie un email au client" if ticket.get("contact_preference") == "mail" and ticket.get("mail") else "Client ne souhaite pas être contacté par email"
                    )
                ], width=12)
            ])
        ])
    ], className="mb-3")
    
    # Liste des commentaires avec distinction visuelle par type
    comments_container = []
    if formatted_comments:
        comments_list = []
        for comment in formatted_comments:
            interaction_type = comment.get("interaction_type", "internal")
            
            # Déterminer l'icône et le label selon la source pour les commentaires externes
            comment_source = comment.get("comment_source")
            source_icon = ""
            source_label_suffix = ""
            
            if interaction_type in ["comment_sent", "comment_received", "external"] and comment_source:
                if comment_source == "mail":
                    source_icon = "📧 "
                    source_label_suffix = " (Email)"
                elif comment_source == "phone":
                    source_icon = "📞 "
                    source_label_suffix = " (Téléphone)"
            
            # Configuration visuelle selon le type de commentaire
            type_config = {
                "internal": {
                    "icon": "💭",
                    "label": "Commentaire interne",
                    "border_color": "#6c757d",
                    "bg_color": "#f8f9fa",
                    "text_color": "#495057"
                },
                "external_sent": {
                    "icon": f"{source_icon}📤",
                    "label": f"Envoyé au client{source_label_suffix}",
                    "border_color": "#28a745",
                    "bg_color": "#d4edda",
                    "text_color": "#155724"
                },
                "external_received": {
                    "icon": f"{source_icon}📥",
                    "label": f"Reçu du client{source_label_suffix}",
                    "border_color": "#007bff",
                    "bg_color": "#d1ecf1",
                    "text_color": "#0c5460"
                },
                "comment_sent": {
                    "icon": f"{source_icon}📤",
                    "label": f"Message envoyé{source_label_suffix}",
                    "border_color": "#28a745",
                    "bg_color": "#d4edda",
                    "text_color": "#155724"
                },
                "comment_received": {
                    "icon": f"{source_icon}📥",
                    "label": f"Message reçu{source_label_suffix}",
                    "border_color": "#007bff",
                    "bg_color": "#d1ecf1",
                    "text_color": "#0c5460"
                },
                "comment_type": {
                    "icon": f"{source_icon}📝",
                    "label": f"Commentaire{source_label_suffix}",
                    "border_color": "#17a2b8",
                    "bg_color": "#d1ecf1",
                    "text_color": "#0c5460"
                },
                "external": {
                    "icon": f"{source_icon}🌐",
                    "label": f"Message externe{source_label_suffix}",
                    "border_color": "#ffc107",
                    "bg_color": "#fff3cd",
                    "text_color": "#856404"
                }
            }
            
            config = type_config.get(interaction_type, type_config["internal"])
            
            comment_item = html.Div([
                # En-tête avec type, auteur et date
                html.Div([
                    html.Div([
                        html.Span([
                            config["icon"], " ",
                            html.Strong(config["label"]),
                            " - ",
                            comment["author_id"]
                        ], style={
                            "fontWeight": "600",
                            "color": config["text_color"]
                        }),
                    ], style={"flex": "1"}),
                    html.Span(comment["formatted_date"], 
                             style={"fontSize": "0.85rem", "color": "#777", "fontStyle": "italic"}),
                ], style={
                    "display": "flex",
                    "justifyContent": "space-between",
                    "alignItems": "center",
                    "borderBottom": f"2px solid {config['border_color']}",
                    "paddingBottom": "6px",
                    "marginBottom": "10px"
                }),
                # Contenu du commentaire
                html.Div(comment["content"], style={
                    "lineHeight": "1.5",
                    "color": config["text_color"],
                    "fontWeight": "400"
                })
            ], className="comment-item", style={
                "padding": "15px",
                "marginBottom": "15px",
                "borderLeft": f"4px solid {config['border_color']}",
                "backgroundColor": config["bg_color"],
                "borderRadius": "6px",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.1)"
            })
            comments_list.append(comment_item)
        comments_container = comments_list
    else:
        comments_container = [html.P("Aucune interaction pour l'instant", className="text-muted")]
    
    # 6. HISTORIQUE DES INTERACTIONS
    interactions_history = dbc.Card([
        dbc.CardHeader(f"📋 Historique des Interactions ({len(formatted_comments)})"),
        dbc.CardBody([
            html.Div(comments_container, style={"maxHeight": "600px", "overflowY": "auto"})
        ])
    ], className="mb-3")
    
    # LAYOUT FINAL AVEC TOUTES LES SECTIONS
    details_section = html.Div([
        # 1. Classification du ticket
        classification_box,
        # 2. Mise à jour du statut
        status_update_box,
        # 3. Informations du ticket
        info_box,
        # 4. Message du client
        message_box,
        # 5. Formulaire d'interactions
        interaction_form,
        # 6. Historique des interactions
        interactions_history
    ])
    
    return details_section


# La fonction register_copy_callbacks a été supprimée car nous utilisons maintenant dcc.Clipboard qui intègre déjà la fonctionnalité de copie
