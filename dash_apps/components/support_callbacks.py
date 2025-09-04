"""
Callbacks pour la page de support technique - Version optimisée avec pagination et cache
"""

from dash import callback, Input, Output, State, ctx, ALL, html, no_update, dcc, callback_context
from urllib.parse import parse_qs
from dash.exceptions import PreventUpdate
from dash_apps.components.support_tickets import render_tickets_list, render_ticket_details
from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
from dash_apps.repositories.support_comment_repository import SupportCommentRepository
from dash_apps.repositories.user_repository import UserRepository
from dash_apps.models.support_ticket import SupportTicket
from dash_apps.core.database import get_session
from dash_apps.services.support_cache_service import SupportCacheService
import dash_bootstrap_components as dbc
import logging
import os
from flask import session
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

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


def load_tickets_by_page(page=1, page_size=10, status=None, category=None, subtype=None, force_reload=False):
    """
    Charge les tickets par page avec cache optimisé
    """
    print(f"[load_tickets_by_page] Page {page}, {page_size} tickets/page, status={status}")
    
    # Utiliser le service de cache centralisé
    filter_params = {
        'category': category,
        'subtype': subtype
    }
    
    try:
        result = SupportCacheService.get_tickets_page_result(
            page_index=page,
            page_size=page_size,
            status=status,
            filter_params=filter_params,
            force_reload=force_reload
        )
        
        return {
            "tickets": result["tickets"],
            "pagination": result["pagination"],
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
    Charge les tickets en attente pour la page demandée avec cache optimisé
    """
    print("")
    print("update_pending_tickets_data")
    print("page", page)
    print("refresh_clicks", refresh_clicks)
    print("last_update", last_update)
    
    # Les logs pour le debugging du signal de mise à jour
    if update_signal:
        print(f"Signal de mise à jour reçu: {update_signal}")
    
    # Déterminer si on force le reload (bouton refresh ou signal de mise à jour)
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    force_reload = (triggered_id == "support-refresh-btn" and refresh_clicks is not None) or bool(update_signal and update_signal.get("count", 0) > 0)
    
    # Charger les tickets pour la page demandée (10 tickets par page) avec filtres serveur
    data = load_tickets_by_page(
        page=page or 1, page_size=10, status="OPEN",
        category=(category_filter if category_filter != "all" else None),
        subtype=(subtype_filter if subtype_filter != "all" else None),
        force_reload=force_reload
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
    Charge les tickets fermés pour la page demandée avec cache optimisé
    """
    print("")
    print("update_closed_tickets_data")
    print("closed page", page)
    print("refresh_clicks", refresh_clicks)
    print("closed last_update", last_update)
    
    # Les logs pour le debugging du signal de mise à jour
    if update_signal:
        print(f"Signal de mise à jour reçu: {update_signal}")
    
    # Déterminer si on force le reload (bouton refresh ou signal de mise à jour)
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    force_reload = (triggered_id == "support-refresh-btn" and refresh_clicks is not None) or bool(update_signal and update_signal.get("count", 0) > 0)
        
    # Charger les tickets pour la page demandée (10 tickets par page) avec filtres serveur
    data = load_tickets_by_page(
        page=page or 1, page_size=10, status="CLOSED",
        category=(category_filter if category_filter != "all" else None),
        subtype=(subtype_filter if subtype_filter != "all" else None),
        force_reload=force_reload
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
    Utilise le cache centralisé pour optimiser les performances
    """
    # Effacer le cache HTML si un ticket a été mis à jour
    if update_signal and update_signal.get("updated_id"):
        SupportCacheService.clear_ticket_cache(update_signal["updated_id"])
   
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
     Input("comment-update-signal", "data"),
     Input("comments-polling-interval", "n_intervals")],
    [State("support-tickets-store", "data"),
     State("closed-tickets-store", "data")]
)
def display_ticket_details(selected_ticket, comment_signal, n_intervals, pending_tickets_data, closed_tickets_data):
    """
    Affiche les détails du ticket sélectionné avec cache optimisé
    Rafraîchit également les commentaires quand le signal de commentaires est modifié
    """
    # Validation robuste du ticket sélectionné
    if not selected_ticket or not isinstance(selected_ticket, dict):
        return html.Div(
            "Aucun ticket sélectionné", 
            className="text-muted text-center p-5",
            style={"fontStyle": "italic"}
        )
    
    ticket_id = selected_ticket.get("ticket_id")
    if not ticket_id or not isinstance(ticket_id, str) or len(ticket_id.strip()) == 0:
        return html.Div(
            "ID de ticket invalide", 
            className="text-muted text-center p-5",
            style={"fontStyle": "italic"}
        )
    
    # Si le signal de commentaire a été déclenché ou polling interval, effacer le cache pour ce ticket
    if (comment_signal and comment_signal.get("ticket_id") == ticket_id) or n_intervals > 0:
        SupportCacheService.clear_ticket_cache(ticket_id)
    
    # Utiliser le service de cache pour récupérer les détails
    try:
        return SupportCacheService.get_ticket_details_panel(ticket_id)
    except Exception as e:
        logger.error(f"Erreur affichage détails ticket {ticket_id}: {e}")
        # Fallback: charger directement sans cache
        comments = load_comments_for_ticket(ticket_id)
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
    Gère l'ajout d'un nouveau commentaire avec invalidation de cache
    """
    # Vérification des prérequis
    if not btn_clicks or not btn_clicks[0] or not selected_ticket or not selected_ticket.get("ticket_id"):
        return no_update, [""]*len(comment_texts)
    
    # Récupérer les informations nécessaires
    ticket_id = selected_ticket["ticket_id"]
    comment_text = comment_texts[0] if comment_texts else ""
    
    # Vérifier si le commentaire est vide
    if not comment_text or not comment_text.strip():
        return no_update, [""]*len(comment_texts)
    
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
            
            # Effacer le cache pour ce ticket après ajout du commentaire
            SupportCacheService.clear_ticket_cache(ticket_id)
            
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du commentaire: {e}")
        return no_update, [""]*len(comment_texts)
        
    if comment is None:
        return no_update, [""]*len(comment_texts)
    
    # Émettre un signal spécifique pour les commentaires uniquement
    updated_signal = {
        "count": current_signal.get("count", 0) + 1,
        "ticket_id": ticket_id,
        "timestamp": datetime.now().isoformat()
    }
    
    # Renvoyer le signal et vider le champ de commentaire
    return updated_signal, ["" for _ in comment_texts]


# Callback pour ouvrir le modal de confirmation
@callback(
    Output({"type": "email-confirm-modal", "index": ALL}, "is_open"),
    [Input({"type": "client-response-btn", "index": ALL}, "n_clicks"),
     Input({"type": "cancel-email-btn", "index": ALL}, "n_clicks")],
    [State({"type": "email-confirm-modal", "index": ALL}, "is_open"),
     State({"type": "comment-textarea", "index": ALL}, "value")],
    prevent_initial_call=True
)
def toggle_email_confirmation_modal(response_clicks, cancel_clicks, modal_states, comment_texts):
    """
    Ouvre/ferme le modal de confirmation d'envoi d'email
    """
    if not ctx.triggered:
        return [no_update] * len(modal_states) if modal_states else [no_update]
    
    triggered_id = ctx.triggered[0]["prop_id"]
    
    # Si c'est le bouton "Envoyer réponse client"
    if "client-response-btn" in triggered_id:
        # Vérifier qu'il y a du contenu
        if comment_texts and comment_texts[0] and comment_texts[0].strip():
            return [True] + [False] * (len(modal_states) - 1) if len(modal_states) > 1 else [True]
        else:
            return [no_update] * len(modal_states) if modal_states else [no_update]
    
    # Si c'est le bouton "Annuler"
    elif "cancel-email-btn" in triggered_id:
        return [False] * len(modal_states) if modal_states else [no_update]
    
    return [no_update] * len(modal_states) if modal_states else [no_update]


@callback(
    [Output("email-send-signal", "data"),
     Output({"type": "comment-textarea", "index": ALL}, "value", allow_duplicate=True),
     Output({"type": "email-confirm-modal", "index": ALL}, "is_open", allow_duplicate=True)],
    [Input({"type": "confirm-email-btn", "index": ALL}, "n_clicks")],
    [State({"type": "comment-textarea", "index": ALL}, "value"),
     State("selected-ticket-store", "data"),
     State("email-send-signal", "data"),
     State({"type": "email-confirm-modal", "index": ALL}, "is_open")],
    prevent_initial_call=True
)
def send_email_to_client_callback(btn_clicks, comment_texts, selected_ticket, current_signal, modal_states):
    """
    Gère l'envoi d'email au client via Gmail API OAuth2 après confirmation
    """
    # Vérification des prérequis
    if not btn_clicks or not btn_clicks[0] or not selected_ticket or not selected_ticket.get("ticket_id"):
        return no_update, [no_update] * len(comment_texts) if comment_texts else [no_update], [no_update] * len(modal_states) if modal_states else [no_update]
    
    # Récupérer les informations nécessaires
    ticket_id = selected_ticket["ticket_id"]
    message_content = comment_texts[0] if comment_texts else ""
    
    # Vérifier si le message est vide
    if not message_content or not message_content.strip():
        logger.warning("Tentative d'envoi d'email avec message vide")
        return no_update, [no_update] * len(comment_texts) if comment_texts else [no_update], [no_update] * len(modal_states) if modal_states else [no_update]
    
    # Utiliser EmailService au lieu de N8N
    try:
        from dash_apps.services.email_service import EmailService
        
        logger.info(f"Tentative d'envoi email pour ticket {ticket_id}")
        
        # Envoyer l'email via EmailService
        success = EmailService.send_email_to_client(selected_ticket, message_content.strip())
        
        if success:
            logger.info(f"Email envoyé avec succès pour ticket {ticket_id}")
            
            # Émettre un signal de succès
            success_signal = {
                "count": current_signal.get("count", 0) + 1,
                "ticket_id": ticket_id,
                "status": "success",
                "message": f"✅ Email envoyé avec succès via Gmail API",
                "timestamp": datetime.now().isoformat()
            }
            
            # Fermer le modal et vider le champ
            return success_signal, ["" for _ in comment_texts], [False] * len(modal_states) if modal_states else [no_update]
        else:
            # Émettre un signal d'échec
            error_signal = {
                "count": current_signal.get("count", 0) + 1,
                "ticket_id": ticket_id,
                "status": "error",
                "message": "❌ Échec envoi email via Gmail API",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.error(f"Échec envoi email pour ticket {ticket_id}")
            return error_signal, [no_update] * len(comment_texts) if comment_texts else [no_update], [False] * len(modal_states) if modal_states else [no_update]
            
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi email: {e}")
        
        # Signal d'erreur
        error_signal = {
            "count": current_signal.get("count", 0) + 1,
            "ticket_id": ticket_id,
            "status": "error",
            "message": f"❌ Erreur: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        
        return error_signal, [no_update] * len(comment_texts) if comment_texts else [no_update], [False] * len(modal_states) if modal_states else [no_update]


# Callback pour afficher les notifications d'envoi d'email près du bouton
@callback(
    Output({"type": "email-notification", "index": ALL}, "children"),
    [Input("email-send-signal", "data")],
    [State("selected-ticket-store", "data")],
    prevent_initial_call=True
)
def display_email_notification(signal_data, selected_ticket):
    """
    Affiche les notifications d'envoi d'email près du bouton d'envoi
    """
    if not signal_data or not signal_data.get("status") or not selected_ticket:
        return [no_update]
    
    # Vérifier si le signal correspond au ticket sélectionné
    signal_ticket_id = signal_data.get("ticket_id")
    selected_ticket_id = selected_ticket.get("ticket_id")
    
    if signal_ticket_id != selected_ticket_id:
        return [no_update]
    
    status = signal_data.get("status")
    message = signal_data.get("message", "")
    
    notification = ""
    if status == "success":
        notification = dbc.Alert(
            message,
            color="success",
            dismissable=True,
            duration=4000,
            style={"marginBottom": "10px", "fontSize": "0.9em"}
        )
    elif status == "error":
        notification = dbc.Alert(
            message,
            color="danger",
            dismissable=True,
            duration=6000,
            style={"marginBottom": "10px", "fontSize": "0.9em"}
        )
    elif status == "sending":
        notification = dbc.Alert(
            message,
            color="info",
            dismissable=False,
            style={"marginBottom": "10px", "fontSize": "0.9em"}
        )
    
    return [notification]