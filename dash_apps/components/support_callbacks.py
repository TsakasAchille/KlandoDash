"""
Callbacks pour la page de support technique - Version optimisée avec pagination et cache
"""

from dash import callback, Input, Output, State, ctx, ALL, html, no_update, dcc
from dash.exceptions import PreventUpdate
from dash_apps.components.support_tickets import render_tickets_list, render_ticket_details
from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
from dash_apps.repositories.support_comment_repository import SupportCommentRepository
from dash_apps.core.database import get_session
import dash_bootstrap_components as dbc
import logging
from flask import session
from datetime import datetime, timedelta

# Configuration du logging
def _init_logging():
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
_init_logging()

# Logger centralisé
logger = logging.getLogger("klando.support")


def need_refresh(last_update, force_refresh=False, max_age_seconds=300):
    """
    Détermine si les données doivent être rafraîchies
    """
    if force_refresh:
        return True
        
    if not last_update:
        return True
        
    try:
        last_update_time = datetime.fromisoformat(last_update)
        age = datetime.now() - last_update_time
        return age.total_seconds() > max_age_seconds
    except (ValueError, TypeError):
        return True


def load_paginated_tickets(page_num, page_size, status=None):
    """
    Charge une page de tickets avec la pagination
    """
    print(f"[load_paginated_tickets] Page {page_num}, {page_size} tickets/page, status={status}")
    page_num = int(page_num) if page_num else 1
    page_size = int(page_size) if page_size else 10
    
    try:
        with get_session() as session:
            result = SupportTicketRepository.get_tickets_with_pagination(
                session, page=page_num, page_size=page_size, status=status
            )
            tickets = [t.model_dump() for t in result["tickets"]]
            pagination = result["pagination"]
            
        return {
            "tickets": tickets,
            "pagination": pagination,
            "timestamp": datetime.now().isoformat(),
            "status_filter": status
        }
    except Exception as e:
        logger.error(f"[load_paginated_tickets] Erreur: {e}")
        return {
            "tickets": [],
            "pagination": {"total_count": 0, "page": 1, "page_size": page_size, "total_pages": 1},
            "timestamp": datetime.now().isoformat(),
            "status_filter": status
        }


def load_comments_for_ticket(ticket_id):
    """
    Charge les commentaires pour un ticket spécifique
    """
    if not ticket_id:
        return []
        
    try:
        with get_session() as session:
            comments = SupportCommentRepository.list_comments_for_ticket(session, str(ticket_id))
        return [c.model_dump() for c in comments] if comments else []
    except Exception as e:
        logger.error(f"[load_comments_for_ticket] Erreur pour ticket {ticket_id}: {e}")
        return []


def update_ticket_status(ticket_id, new_status):
    """
    Met à jour le statut d'un ticket
    """
    if not ticket_id or not new_status:
        logger.warning(f"[update_ticket_status] Données manquantes: ticket={ticket_id}, status={new_status}")
        return False
        
    try:
        logger.info(f"[update_ticket_status] Ticket {ticket_id} -> {new_status}")
        with get_session() as session:
            SupportTicketRepository.update_ticket(session, ticket_id, {"status": new_status})
        return True
    except Exception as e:
        logger.error(f"[update_ticket_status] Erreur pour ticket {ticket_id}: {e}")
        return False


def add_support_comment(ticket_id, user_id, comment_text):
    """
    Ajoute un commentaire à un ticket
    """
    try:
        with get_session() as db_session:
            SupportCommentRepository.add_comment(db_session, str(ticket_id), str(user_id), comment_text)
        logger.info(f"[add_support_comment] Commentaire ajouté: ticket={ticket_id}, user={user_id}")
        return True
    except Exception as e:
        logger.error(f"[add_support_comment] Erreur: {e}")
        return False


def validate_comment_input(btn_clicks, comment_texts, selected_ticket):
    """
    Valide l'entrée d'un nouveau commentaire
    """
    if not any(btn_clicks) or not selected_ticket or not selected_ticket.get("ticket_id"):
        return None, None, None
        
    ticket_id = selected_ticket["ticket_id"]
    comment_text = None
    
    # Trouver le texte du commentaire associé au bouton cliqué
    for i, clicks in enumerate(btn_clicks):
        if clicks and i < len(comment_texts):
            comment_text = comment_texts[i]
            break
            
    if not comment_text or not comment_text.strip():
        return ticket_id, None, None
        
    user_id = session.get('user_id', 'anonymous')
    return ticket_id, comment_text.strip(), user_id


# CALLBACKS
@callback(
    [Output("pagination-page", "max_value"),
     Output("support-tickets-cache", "data"),
     Output("support-tickets-timestamp", "data")],
    [Input("pagination-page", "active_page"),
     Input("pagination-page-size", "value"),
     Input("support-refresh-btn", "n_clicks")],
    [State("support-tickets-timestamp", "data")]
)
def update_pending_tickets_data(page, page_size, refresh_clicks, last_update):
    """
    Charge les tickets avec pagination et met à jour le cache
    """

    print("page", page)
    print("page_size", page_size)
    print("refresh_clicks", refresh_clicks)
    print("last_update", last_update)
    
    # Vérifier si un rafraîchissement est nécessaire
    #if not force_refresh and not need_refresh(last_update):
    #    raise PreventUpdate
        
    # Charger les tickets pour la page demandée
    data = load_paginated_tickets(page or 1, page_size or 10,status="PENDING")
    
    # Retourner le nombre total de pages pour le paginateur
    total_pages = data["pagination"]["total_pages"]
    timestamp = datetime.now().isoformat()
    
    return total_pages, data, timestamp


# CALLBACKS
@callback(
    [Output("closed-pagination-page", "max_value"),
     Output("closed-tickets-cache", "data"),
     Output("closed-tickets-timestamp", "data")],
    [Input("closed-pagination-page", "active_page"),
     Input("closed-pagination-page-size", "value"),
     Input("support-refresh-btn", "n_clicks")],
    [State("closed-tickets-timestamp", "data")]
)
def update_closed_tickets_data(page, page_size, refresh_clicks, last_update):
    """
    Charge les tickets fermés avec pagination et met à jour le cache
    """

    print("closed page", page)
    print("closed page_size", page_size)
    print("refresh_clicks", refresh_clicks)
    print("closed last_update", last_update)
    
    # Vérifier si un rafraîchissement est nécessaire
    #if not force_refresh and not need_refresh(last_update):
    #    raise PreventUpdate
        
    # Charger les tickets pour la page demandée
    data = load_paginated_tickets(page or 1, page_size or 10, status="CLOSED")
    
    # Retourner le nombre total de pages pour le paginateur
    total_pages = data["pagination"]["total_pages"]
    timestamp = datetime.now().isoformat()
    
    return total_pages, data, timestamp


@callback(
    Output("support-tickets-store", "data"),
    [Input("support-tickets-cache", "data"),
     Input({"type": "update-status-btn", "index": ALL}, "n_clicks")],
    [State({"type": "status-dropdown", "index": ALL}, "value"),
     State("selected-ticket-store", "data")]
)
def process_tickets_data(cache_data, status_clicks, status_values, selected_ticket):
    """
    Traite les données du cache et les met à jour si nécessaire (ex: changement de statut)
    """
    if not cache_data:
        return no_update
        
    # Vérifier si le callback est déclenché par un bouton de mise à jour de statut
    triggered = ctx.triggered_id
    if isinstance(triggered, dict) and triggered.get("type") == "update-status-btn":
        ticket_id = triggered.get("index")
        try:
            # Trouver le bouton cliqué et la valeur associée
            if any(status_clicks):
                idx = next((i for i, clicks in enumerate(status_clicks) if clicks), None)
                if idx is not None and idx < len(status_values):
                    new_status = status_values[idx]
                    logger.info(f"Mise à jour statut: ticket {ticket_id} -> {new_status}")
                    update_ticket_status(ticket_id, new_status)
                    
                    # Si le ticket en cours est modifié, mettre à jour son statut dans la sélection
                    if selected_ticket and selected_ticket.get("ticket_id") == ticket_id:
                        selected_ticket["status"] = new_status
        except Exception as e:
            logger.error(f"Erreur de mise à jour de statut: {e}")
    
    # Toujours retourner les données du cache
    return cache_data


@callback(
    Output("closed-tickets-store", "data"),
    [Input("closed-tickets-cache", "data")]
)
def process_closed_tickets_data(cache_data):
    """
    Traite les données du cache des tickets fermés
    """
    if not cache_data:
        return no_update
    
    # Toujours retourner les données du cache
    return cache_data


@callback(
    [Output("open-tickets-container", "children"),
     Output("closed-tickets-container", "children"),
     Output("open-count", "children"),
     Output("closed-count", "children")],
    [Input("support-tickets-store", "data"),
     Input("closed-tickets-store", "data"),
     Input("selected-ticket-store", "data")]
)
def update_tickets_lists(pending_tickets_data, closed_tickets_data, selected_ticket):
    """
    Met à jour les listes de tickets par statut
    """
    empty_message = html.Div("Aucun ticket disponible", className="text-muted text-center py-4")
    
    # Traitement des tickets en attente
    if not pending_tickets_data or not pending_tickets_data.get("tickets"):
        pending_list = empty_message
        total_pending = 0
    else:
        pending_tickets = pending_tickets_data["tickets"]
        pending_pagination = pending_tickets_data.get("pagination", {})
        total_pending = pending_pagination.get("total_count", len(pending_tickets))
        
        selected_id = selected_ticket.get("ticket_id") if selected_ticket else None
        pending_list = render_tickets_list(pending_tickets, selected_id) if pending_tickets else \
                    html.Div("Aucun ticket en attente", className="text-muted text-center py-4")
    
    # Traitement des tickets fermés
    if not closed_tickets_data or not closed_tickets_data.get("tickets"):
        closed_list = empty_message 
        total_closed = 0
    else:
        closed_tickets = closed_tickets_data["tickets"]
        closed_pagination = closed_tickets_data.get("pagination", {})
        total_closed = closed_pagination.get("total_count", len(closed_tickets))
        
        selected_id = selected_ticket.get("ticket_id") if selected_ticket else None
        closed_list = render_tickets_list(closed_tickets, selected_id) if closed_tickets else \
                   html.Div("Aucun ticket fermé", className="text-muted text-center py-4")
    
    print(f"Tickets en attente: {total_pending}, Tickets fermés: {total_closed}")
    
    return pending_list, closed_list, str(total_pending), str(total_closed)


@callback(
    Output("selected-ticket-store", "data"),
    [Input({"type": "ticket-item", "index": ALL}, "n_clicks")],
    [State("support-tickets-store", "data"),
     State("selected-ticket-store", "data")]
)
def update_selected_ticket(ticket_item_n_clicks, tickets_data, selected_ticket):
    """
    Gère la sélection d'un ticket
    """
    if not ctx.triggered or not tickets_data or not tickets_data.get("tickets"):
        return no_update
        
    # Vérifier si un ticket a été cliqué
    triggered = ctx.triggered_id
    if not triggered or not isinstance(triggered, dict) or triggered.get("type") != "ticket-item":
        return no_update
        
    # Récupérer l'ID du ticket cliqué
    ticket_id = triggered.get("index")
    if not ticket_id:
        return no_update
        
    # Si c'est le même ticket déjà sélectionné, ne rien faire
    if selected_ticket and selected_ticket.get("ticket_id") == ticket_id:
        return no_update
        
    # Trouver le ticket complet dans les données
    ticket = next((t for t in tickets_data.get("tickets", []) if t.get("ticket_id") == ticket_id), None)
    if ticket:
        logger.info(f"Ticket sélectionné: {ticket_id}")
        return ticket
        
    return no_update


@callback(
    Output("ticket-details-container", "children"),
    [Input("selected-ticket-store", "data")],
    [State("support-tickets-store", "data")]
)
def display_ticket_details(selected_ticket, tickets_data):
    """
    Affiche les détails du ticket sélectionné
    """
    if not selected_ticket or not selected_ticket.get("ticket_id"):
        return html.Div([
            html.Div("Sélectionnez un ticket pour voir ses détails", className="text-center text-muted p-5")
        ])
    
    ticket_id = selected_ticket["ticket_id"]
    # Charger les commentaires à la demande
    comments = load_comments_for_ticket(ticket_id)
    
    # Rendre les détails avec les commentaires
    return render_ticket_details(selected_ticket, comments)


@callback(
    [Output("support-tickets-store", "data", allow_duplicate=True),
     Output({"type": "comment-textarea", "index": ALL}, "value")],
    [Input({"type": "comment-btn", "index": ALL}, "n_clicks")],
    [State({"type": "comment-textarea", "index": ALL}, "value"),
     State("selected-ticket-store", "data"),
     State("support-tickets-store", "data")],
    prevent_initial_call=True
)
def add_comment_callback(btn_clicks, comment_texts, selected_ticket, tickets_data):
    """
    Gère l'ajout d'un nouveau commentaire
    """
    # Validation des entrées
    ticket_id, comment_text, user_id = validate_comment_input(btn_clicks, comment_texts, selected_ticket)
    
    if not ticket_id or not comment_text or not user_id:
        return no_update, ["" for _ in comment_texts]
    
    # Ajouter le commentaire
    success = add_support_comment(ticket_id, user_id, comment_text)
    
    if not success:
        return no_update, ["" for _ in comment_texts]
    
    # Rafraîchir les données (en pratique, seul le commentaire serait ajouté)
    # Pour simplifier, on rafraîchit tout le cache
    return tickets_data, ["" for _ in comment_texts]