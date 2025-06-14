"""
Callbacks pour la page de support technique - Version optimisée avec pagination et cache
"""

from dash import callback, Input, Output, State, ctx, ALL, html, no_update, dcc
from dash.exceptions import PreventUpdate
from dash_apps.components.support_tickets import render_tickets_list, render_ticket_details
from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
from dash_apps.repositories.support_comment_repository import SupportCommentRepository
from dash_apps.models.support_ticket import SupportTicket
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


def load_tickets_by_page(page=1, page_size=10, status=None):
    """
    Charge les tickets par page, version simplifiée
    """
    print(f"[load_tickets_by_page] Page {page}, {page_size} tickets/page, status={status}")
    
    try:
        with get_session() as session:
            result = SupportTicketRepository.get_tickets_by_page(
                session, page=page, page_size=page_size, status=status
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
        logger.error(f"[load_tickets_by_page] Erreur: {e}")
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
    Met à jour le statut d'un ticket et retourne l'ancien et le nouveau statut
    """
    try:
        with get_session() as session:
            # Récupérer le ticket
            ticket = session.query(SupportTicket).filter(SupportTicket.ticket_id == ticket_id).first()
            if ticket:
                old_status = ticket.status
                ticket.status = new_status
                ticket.updated_at = datetime.now()
                session.commit()
                logger.info(f"Ticket {ticket_id} mis à jour : {old_status} -> {new_status}")
                return old_status, new_status
            else:
                logger.warning(f"Ticket {ticket_id} non trouvé pour mise à jour")
                return None, None
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du ticket {ticket_id}: {e}")
        return None, None


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
     Input("support-refresh-btn", "n_clicks")],
    [State("support-tickets-timestamp", "data")]
)
def update_pending_tickets_data(page, refresh_clicks, last_update):
    """
    Charge les tickets en attente pour la page demandée
    """
    print("page", page)
    print("refresh_clicks", refresh_clicks)
    print("last_update", last_update)
    
    # Vérifier si un rafraîchissement est nécessaire
    #if not force_refresh and not need_refresh(last_update):
    #    raise PreventUpdate
        
    # Charger les tickets pour la page demandée (10 tickets par page)
    data = load_tickets_by_page(page=page or 1, page_size=10, status="PENDING")
    
    # Retourner le nombre total de pages pour le paginateur
    total_pages = data["pagination"]["total_pages"]
    
    # Utiliser le timestamp déjà inclus dans les données
    return total_pages, data, data["timestamp"]


# CALLBACKS
@callback(
    [Output("closed-pagination-page", "max_value"),
     Output("closed-tickets-cache", "data"),
     Output("closed-tickets-timestamp", "data")],
    [Input("closed-pagination-page", "active_page"),
     Input("support-refresh-btn", "n_clicks")],
    [State("closed-tickets-timestamp", "data")]
)
def update_closed_tickets_data(page, refresh_clicks, last_update):
    """
    Charge les tickets fermés pour la page demandée
    """
    print("closed page", page)
    print("refresh_clicks", refresh_clicks)
    print("closed last_update", last_update)
    
    # Charger les tickets fermés pour la page demandée (10 tickets par page)
    data = load_tickets_by_page(page=page or 1, page_size=10, status="CLOSED")
    
    # Retourner le nombre total de pages pour le paginateur
    total_pages = data["pagination"]["total_pages"]
    
    # Utiliser le timestamp déjà inclus dans les données
    return total_pages, data, data["timestamp"]


@callback(
    [Output("support-tickets-store", "data"),
     Output("closed-tickets-store", "data"),
     Output("support-refresh-btn", "n_clicks", allow_duplicate=True)],
    [Input("support-tickets-cache", "data"),
     Input("closed-tickets-cache", "data"),
     Input({"type": "update-status-btn", "index": ALL}, "n_clicks")],
    [State({"type": "status-dropdown", "index": ALL}, "value"),
     State("selected-ticket-store", "data"),
     State("support-refresh-btn", "n_clicks")],
    prevent_initial_call=True
)
def process_tickets_data(cache_pending, cache_closed, status_clicks, status_values, selected_ticket, refresh_clicks):
    """
    Traite les données du cache et les met à jour si nécessaire (ex: changement de statut)
    """
    if not cache_pending or not cache_closed:
        return no_update, no_update, no_update
        
    refresh_needed = False
    pending_data = cache_pending
    closed_data = cache_closed
        
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
                    old_status, new_status = update_ticket_status(ticket_id, new_status)
                    
                    # Si le ticket en cours est modifié, mettre à jour son statut dans la sélection
                    if selected_ticket and selected_ticket.get("ticket_id") == ticket_id:
                        selected_ticket["status"] = new_status
                    
                    # Supprimer immédiatement le ticket des listes appropriées
                    if new_status == "CLOSED" and pending_data and "tickets" in pending_data:
                        # Retirer le ticket des tickets en attente et l'ajouter aux tickets fermés
                        pending_data["tickets"] = [t for t in pending_data["tickets"] if t.get("ticket_id") != ticket_id]
                        # Maj des métadonnées de pagination
                        if "pagination" in pending_data:
                            pending_data["pagination"]["total_count"] -= 1
                    
                    elif new_status != "CLOSED" and closed_data and "tickets" in closed_data:
                        # Retirer le ticket des tickets fermés et l'ajouter aux tickets en attente
                        closed_data["tickets"] = [t for t in closed_data["tickets"] if t.get("ticket_id") != ticket_id]
                        # Maj des métadonnées de pagination
                        if "pagination" in closed_data:
                            closed_data["pagination"]["total_count"] -= 1
                    
                    # Indiquer qu'un rafraîchissement complet est nécessaire
                    refresh_needed = True
        except Exception as e:
            logger.error(f"Erreur de mise à jour de statut: {e}")
    
    # Déclencher un rafraîchissement si nécessaire
    if refresh_needed:
        return pending_data, closed_data, (refresh_clicks or 0) + 1
    else:
        return pending_data, closed_data, no_update





@callback(
    [Output("open-tickets-container", "children"),
     Output("open-count", "children")],
    [Input("support-tickets-store", "data"),
     Input("selected-ticket-store", "data")]
)
def update_pending_tickets_list(pending_tickets_data, selected_ticket):
    """
    Met à jour la liste des tickets en attente
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
    
    print(f"Tickets en attente: {total_pending}")
    return pending_list, str(total_pending)


@callback(
    [Output("closed-tickets-container", "children"),
     Output("closed-count", "children")],
    [Input("closed-tickets-store", "data"),
     Input("selected-ticket-store", "data")]
)
def update_closed_tickets_list(closed_tickets_data, selected_ticket):
    """
    Met à jour la liste des tickets fermés
    """
    empty_message = html.Div("Aucun ticket disponible", className="text-muted text-center py-4")
    
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
    
    print(f"Tickets fermés: {total_closed}")
    return closed_list, str(total_closed)


@callback(
    Output("selected-ticket-store", "data"),
    [Input({"type": "ticket-item", "index": ALL}, "n_clicks")],
    [State("support-tickets-store", "data"),
     State("closed-tickets-store", "data"),
     State("selected-ticket-store", "data")]
)
def update_selected_ticket(ticket_item_n_clicks, pending_tickets_data, closed_tickets_data, selected_ticket):
    """
    Gère la sélection d'un ticket
    """
    if not ctx.triggered:
        return no_update
        
    # Vérifier si les données de tickets sont disponibles
    has_pending_tickets = pending_tickets_data and pending_tickets_data.get("tickets")
    has_closed_tickets = closed_tickets_data and closed_tickets_data.get("tickets")
        
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
        
    # Chercher le ticket dans les deux listes (tickets en attente et tickets fermés)
    ticket = None
    if has_pending_tickets:
        ticket = next((t for t in pending_tickets_data.get("tickets", []) if t.get("ticket_id") == ticket_id), None)
    
    if not ticket and has_closed_tickets:
        ticket = next((t for t in closed_tickets_data.get("tickets", []) if t.get("ticket_id") == ticket_id), None)
        
    if ticket:
        logger.info(f"Ticket sélectionné: {ticket_id}")
        return ticket
        
    return no_update


@callback(
    Output("ticket-details-container", "children"),
    [Input("selected-ticket-store", "data")],
    [State("support-tickets-store", "data"),
     State("closed-tickets-store", "data")]
)
def display_ticket_details(selected_ticket, pending_tickets_data, closed_tickets_data):
    """
    Affiche les détails du ticket sélectionné
    """
    # Si pas de ticket sélectionné, afficher un message
    if not selected_ticket:
        return html.Div(
            "Aucun ticket sélectionné", 
            className="text-muted text-center p-5",
            style={"fontStyle": "italic"}
        )
    
    # Pour l'affichage, on n'a pas besoin des données complètes de tous les tickets
    # On utilise directement le ticket sélectionné
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