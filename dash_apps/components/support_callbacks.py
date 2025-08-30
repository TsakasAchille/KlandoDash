"""
Callbacks pour la page de support technique - Version optimisée avec pagination et cache
"""

from dash import callback, Input, Output, State, ctx, ALL, html, no_update, dcc
from urllib.parse import parse_qs
from dash.exceptions import PreventUpdate
from dash_apps.components.support_tickets import render_tickets_list, render_ticket_details
from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
from dash_apps.repositories.support_comment_repository import SupportCommentRepository
from dash_apps.repositories.user_repository import UserRepository
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


def load_tickets_by_page(page=1, page_size=10, status=None, category=None, subtype=None):
    """
    Charge les tickets par page, version simplifiée
    """
    print(f"[load_tickets_by_page] Page {page}, {page_size} tickets/page, status={status}")
    
    try:
        with get_session() as session:
            result = SupportTicketRepository.get_tickets_by_page(
                session, page=page, page_size=page_size, status=status,
                category=category, subtype=subtype
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
    Utilise la méthode du repository pour respecter la séparation des responsabilités
    """
    try:
        with get_session() as session:
            old_status, updated_status = SupportTicketRepository.update_ticket_status(session, ticket_id, new_status)
            if updated_status:
                logger.info(f"Ticket {ticket_id} mis à jour : {old_status} -> {updated_status}")
                return old_status, updated_status
            else:
                logger.warning(f"Ticket {ticket_id} non trouvé pour mise à jour")
                return None, None
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du ticket {ticket_id}: {e}")
        return None, None



# CALLBACKS
@callback(
    [Output("pagination-page", "max_value"),
     Output("support-tickets-cache", "data"),
     Output("support-tickets-timestamp", "data")],
    [Input("pagination-page", "active_page"),
     Input("support-refresh-btn", "n_clicks"),
     Input("ticket-update-signal", "data"),
     Input("ticket-category-filter", "value"),
     Input("ticket-subtype-filter", "value")],
    [State("support-tickets-timestamp", "data")]
)
def update_pending_tickets_data(page, refresh_clicks, update_signal, category_filter, subtype_filter, last_update):
    """
    Charge les tickets en attente pour la page demandée
    """
    print("")
    print("update_pending_tickets_data")
    print("page", page)
    print("refresh_clicks", refresh_clicks)
    print("last_update", last_update)
    
    # Les logs pour le debugging du signal de mise à jour
    if update_signal:
        print(f"Signal de mise à jour reçu: {update_signal}")
    
    # Charger les tickets pour la page demandée (10 tickets par page) avec filtres serveur
    data = load_tickets_by_page(
        page=page or 1, page_size=10, status="OPEN",
        category=(category_filter if category_filter != "all" else None),
        subtype=(subtype_filter if subtype_filter != "all" else None)
    )
    
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
     Input("support-refresh-btn", "n_clicks"),
     Input("ticket-update-signal", "data"),
     Input("ticket-category-filter", "value"),
     Input("ticket-subtype-filter", "value")],
    [State("closed-tickets-timestamp", "data")]
)
def update_closed_tickets_data(page, refresh_clicks, update_signal, category_filter, subtype_filter, last_update):
    """
    Charge les tickets fermés pour la page demandée
    """
    print("")
    print("update_closed_tickets_data")
    print("closed page", page)
    print("refresh_clicks", refresh_clicks)
    print("closed last_update", last_update)
    
    # Les logs pour le debugging du signal de mise à jour
    if update_signal:
        print(f"Signal de mise à jour reçu: {update_signal}")
        
    # Charger les tickets pour la page demandée (10 tickets par page) avec filtres serveur
    data = load_tickets_by_page(
        page=page or 1, page_size=10, status="CLOSED",
        category=(category_filter if category_filter != "all" else None),
        subtype=(subtype_filter if subtype_filter != "all" else None)
    )
    
    # Retourner le nombre total de pages pour le paginateur
    total_pages = data["pagination"]["total_pages"]
    
    # Utiliser le timestamp déjà inclus dans les données
    return total_pages, data, data["timestamp"]


@callback(
    Output("ticket-update-signal", "data"),
    [Input({"type": "update-status-btn", "index": ALL}, "n_clicks")],
    [State({"type": "status-dropdown", "index": ALL}, "value"),
     State("selected-ticket-store", "data"),
     State("ticket-update-signal", "data")],
    prevent_initial_call=True
)
def process_ticket_status_update(status_clicks, status_values, selected_ticket, current_signal):
    """
    Traite les mises à jour de statut des tickets et émet un signal de mise à jour
    pour déclencher le rafraîchissement des listes
    """
    # Récupérer l'id du ticket directement depuis le déclencheur
    triggered = ctx.triggered_id
    ticket_id = triggered.get("index")
    try:
        # Trouver le bouton cliqué et la valeur associée
        if any(status_clicks):
            idx = next((i for i, clicks in enumerate(status_clicks) if clicks), None)
            if idx is not None and idx < len(status_values):
                new_status = status_values[idx]
                logger.info(f"Mise à jour statut: ticket {ticket_id} -> {new_status}")
                update_ticket_status(ticket_id, new_status)
                
                updated_signal = {
                    "count": current_signal.get("count", 0) + 1,
                    "updated_id": ticket_id,
                    "timestamp": datetime.now().isoformat()
                }
                return updated_signal
    except Exception as e:
        logger.error(f"Erreur de mise à jour de statut: {e}")
    
    return no_update


@callback(
    [Output("support-tickets-store", "data"),
     Output("closed-tickets-store", "data")],
    [Input("support-tickets-cache", "data"),
     Input("closed-tickets-cache", "data"),
     Input("ticket-update-signal", "data")],
    [State("support-tickets-store", "data"),
     State("closed-tickets-store", "data")],
    prevent_initial_call=True
)
def update_ticket_stores(cache_pending, cache_closed, update_signal, current_pending, current_closed):
    """
    Met à jour les stores de tickets en fonction des caches et du signal de mise à jour
    """
   
    # Utiliser simplement les données des caches quand ils sont disponibles
    # Cette approche est plus simple et maintient quand même les données à jour
    pending_data = cache_pending if cache_pending else current_pending
    closed_data = cache_closed if cache_closed else current_closed
    
    return pending_data, closed_data


@callback(
    [Output("open-tickets-container", "children"),
     Output("open-count", "children")],
    [Input("support-tickets-store", "data"),
     Input("selected-ticket-store", "data"),
     Input("ticket-category-filter", "value"),
     Input("ticket-subtype-filter", "value")]
)
def update_pending_tickets_list(pending_tickets_data, selected_ticket, category_filter, subtype_filter):
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
        # Plus de filtrage côté client: déjà filtré par le serveur
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
     Input("selected-ticket-store", "data"),
     Input("ticket-category-filter", "value"),
     Input("ticket-subtype-filter", "value")]
)
def update_closed_tickets_list(closed_tickets_data, selected_ticket, category_filter, subtype_filter):
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
        # Plus de filtrage côté client: déjà filtré par le serveur
        closed_pagination = closed_tickets_data.get("pagination", {})
        total_closed = closed_pagination.get("total_count", len(closed_tickets))
        
        selected_id = selected_ticket.get("ticket_id") if selected_ticket else None
        closed_list = render_tickets_list(closed_tickets, selected_id) if closed_tickets else \
                   html.Div("Aucun ticket fermé", className="text-muted text-center py-4")
    
    print(f"Tickets fermés: {total_closed}")
    return closed_list, str(total_closed)


# Réinitialiser la pagination quand les filtres changent (tickets ouverts)
@callback(
    Output("pagination-page", "active_page"),
    [Input("ticket-category-filter", "value"),
     Input("ticket-subtype-filter", "value")],
    prevent_initial_call=True
)
def reset_open_pagination_on_filters(category, subtype):
    return 1


# Réinitialiser la pagination quand les filtres changent (tickets fermés)
@callback(
    Output("closed-pagination-page", "active_page"),
    [Input("ticket-category-filter", "value"),
     Input("ticket-subtype-filter", "value")],
    prevent_initial_call=True
)
def reset_closed_pagination_on_filters(category, subtype):
    return 1


@callback(
    Output("selected-ticket-store", "data"),
    [Input({"type": "ticket-item", "index": ALL}, "n_clicks"),
     Input("url", "pathname"),
     Input("url", "search")],
    [State("support-tickets-store", "data"),
     State("closed-tickets-store", "data"),
    State("selected-ticket-store", "data")]
)
def update_selected_ticket(ticket_item_n_clicks, pathname, search, pending_tickets_data, closed_tickets_data, selected_ticket):
    """
    Gère la sélection d'un ticket
    """
    print("[DEBUG] update_selected_ticket called")
    print("ticket_item_n_clicks:", ticket_item_n_clicks)
    print("ctx.triggered_id:", ctx.triggered_id)
    print("selected_ticket:", selected_ticket)

    # 1) Pré-sélection via URL: /support?ticket_id=...
    try:
        if pathname == "/support" and search:
            qs = parse_qs(search.lstrip('?'))
            url_ticket_id = (qs.get('ticket_id') or [None])[0]
            if url_ticket_id:
                # Ne rien faire si déjà sélectionné
                if selected_ticket and str(selected_ticket.get("ticket_id")) == str(url_ticket_id):
                    pass
                else:
                    # Chercher le ticket dans les stores
                    ticket = None
                    if pending_tickets_data and pending_tickets_data.get("tickets"):
                        ticket = next((t for t in pending_tickets_data["tickets"] if str(t.get("ticket_id")) == str(url_ticket_id)), None)
                    if not ticket and closed_tickets_data and closed_tickets_data.get("tickets"):
                        ticket = next((t for t in closed_tickets_data["tickets"] if str(t.get("ticket_id")) == str(url_ticket_id)), None)
                    # Si pas trouvé, charger depuis la base
                    if not ticket:
                        from dash_apps.core.database import get_session
                        with get_session() as session:
                            from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
                            schema = SupportTicketRepository.get_ticket(session, str(url_ticket_id))
                            ticket = schema.model_dump() if schema else None
                    if ticket:
                        return ticket
    except Exception as e:
        logger.error(f"Erreur lors de la pré-sélection via URL: {e}")
    # 2) Sélection via clic sur un ticket
    # Si aucun ticket n'a été cliqué (tous les n_clicks sont None ou 0), ne rien faire
    if not ticket_item_n_clicks or all(x in (None, 0) for x in ticket_item_n_clicks):
        return no_update
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
    [Input("selected-ticket-store", "data"),
     Input("comment-update-signal", "data")],
    [State("support-tickets-store", "data"),
     State("closed-tickets-store", "data")]
)
def display_ticket_details(selected_ticket, comment_signal, pending_tickets_data, closed_tickets_data):
    """
    Affiche les détails du ticket sélectionné
    Rafraîchit également les commentaires quand le signal de commentaires est modifié
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
    # Si le signal de commentaire concerne ce ticket, ou dans tous les cas (nouveau ticket sélectionné)
    # on recharge toujours les commentaires pour avoir les plus récents
    comments = load_comments_for_ticket(ticket_id)
        
    # Rendre les détails avec les commentaires
    return render_ticket_details(selected_ticket, comments)


@callback(
    [Output("comment-update-signal", "data"),
     Output({"type": "comment-textarea", "index": ALL}, "value")],
    [Input({"type": "comment-btn", "index": ALL}, "n_clicks")],
    [State({"type": "comment-textarea", "index": ALL}, "value"),
     State("selected-ticket-store", "data"),
     State("comment-update-signal", "data")],
    prevent_initial_call=True
)
def add_comment_callback(btn_clicks, comment_texts, selected_ticket, current_signal):
    """
    Gère l'ajout d'un nouveau commentaire
    """
    # Vérification des prérequis
    if not btn_clicks or not btn_clicks[0] or not selected_ticket or not selected_ticket.get("ticket_id"):
        return no_update, [""] * len(comment_texts)
    
    # Récupérer les informations nécessaires
    ticket_id = selected_ticket["ticket_id"]
    comment_text = comment_texts[0] if comment_texts else ""
    
    # Vérifier si le commentaire est vide
    if not comment_text or not comment_text.strip():
        return no_update, [""] * len(comment_texts)
    
    from flask import session
    
    # Récupérer directement l'ID et le nom de l'utilisateur depuis la session
    user_id = session.get('user_id', 'anonymous')
    user_name = session.get('user_name', 'Utilisateur')
    
    # Ajouter le commentaire directement via le repository
    try:
        with get_session() as session:
            # Utiliser le nom d'utilisateur pour l'affichage
            comment = SupportCommentRepository.add_comment(
                session, 
                str(ticket_id),
                str(user_id),
                comment_text.strip(),
                user_name
            )
            
            display_name = user_name or user_id
            logger.info(f"Commentaire ajouté: ticket={ticket_id}, user={display_name}")
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du commentaire: {e}")
        return no_update, [""] * len(comment_texts)
        
    if comment is None:
        return no_update, [""] * len(comment_texts)
    
    # Émettre un signal spécifique pour les commentaires uniquement
    updated_signal = {
        "count": current_signal.get("count", 0) + 1,
        "ticket_id": ticket_id,
        "timestamp": datetime.now().isoformat()
    }
    
    # Renvoyer le signal et vider le champ de commentaire
    return updated_signal, ["" for _ in comment_texts]