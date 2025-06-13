"""
Callbacks pour la page de support technique
Ce fichier contient tous les callbacks liés à la gestion des tickets et commentaires
"""

from dash import callback, Input, Output, State, ctx, ALL, html
from dash_apps.components.support_tickets import render_tickets_list, render_ticket_details
from dash_apps.repositories.support_comment_repository import SupportCommentRepository
from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
from dash_apps.core.database import get_session
import logging
from flask import session


# Configuration minimale du logging si pas déjà fait ailleurs
def _init_logging():
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
_init_logging()

# Logger centralisé
logger = logging.getLogger("klando.support")


def get_tickets_and_comments():
    """
    Fonction centralisée pour charger tous les tickets et leurs commentaires associés.
    Réutilisable par plusieurs callbacks.
    
    Returns:
        dict: Dictionnaire contenant les tickets et commentaires
    """
    logger.info("[get_tickets_and_comments] Début récupération des tickets")
    
    # Récupération des tickets
    try:
        with get_session() as session:
            tickets = SupportTicketRepository.list_tickets(session)
            logger.debug(f"[get_tickets_and_comments] {len(tickets)} tickets bruts récupérés")
            tickets = [t.model_dump() for t in tickets]
    except Exception as e:
        logger.error(f"[get_tickets_and_comments] Erreur lors de la récupération des tickets : {e}")
        tickets = []
    
    # Récupération des commentaires pour chaque ticket
    comments = {}
    for ticket in tickets:
        ticket_id = ticket["ticket_id"]
        try:
            with get_session() as session:
                ticket_comments = SupportCommentRepository.list_comments_for_ticket(session, str(ticket_id))
            if ticket_comments:
                comments[ticket_id] = [c.model_dump() for c in ticket_comments]
        except Exception as e:
            logger.error(f"[get_tickets_and_comments] Erreur lors de la récupération des commentaires pour ticket {ticket_id} : {e}")
    
    logger.info(f"[get_tickets_and_comments] Résultat final : {len(tickets)} tickets, {sum(len(v) for v in comments.values())} commentaires")
    return {"tickets": tickets, "comments": comments}


def update_ticket_status(ticket_id, new_status):
    """
    Met à jour le statut d'un ticket
    
    Args:
        ticket_id (str): ID du ticket à mettre à jour
        new_status (str): Nouveau statut à appliquer
        
    Returns:
        bool: True si la mise à jour a réussi, False sinon
    """
    if not ticket_id or not new_status:
        logger.warning(f"[update_ticket_status] ticket_id ou new_status manquant: ticket_id={ticket_id}, new_status={new_status}")
        return False
        
    try:
        logger.info(f"[update_ticket_status] Mise à jour du statut du ticket {ticket_id} -> {new_status}")
        with get_session() as session:
            SupportTicketRepository.update_ticket(session, ticket_id, {"status": new_status})
        return True
    except Exception as e:
        logger.error(f"[update_ticket_status] Impossible de mettre à jour le statut du ticket {ticket_id}: {e}")
        return False


def add_support_comment(ticket_id, user_id, comment_text):
    """
    Ajoute un commentaire à un ticket
    
    Args:
        ticket_id (str): ID du ticket
        user_id (str): ID de l'utilisateur qui commente
        comment_text (str): Texte du commentaire
        
    Returns:
        bool: True si l'ajout a réussi, False sinon
    """
    try:
        with get_session() as db_session:
            SupportCommentRepository.add_comment(db_session, str(ticket_id), str(user_id), comment_text)
        logger.info(f"[add_support_comment] Commentaire ajouté avec succès pour le ticket {ticket_id} par {user_id}.")
        return True
    except Exception as e:
        logger.error(f"[add_support_comment] Erreur lors de l'ajout du commentaire pour le ticket {ticket_id} par {user_id}: {e}")
        return False


def validate_comment_input(btn_clicks, comment_texts, selected_ticket):
    """
    Valide l'entrée d'un nouveau commentaire
    
    Args:
        btn_clicks (list): Liste des clics sur les boutons de commentaire
        comment_texts (list): Liste des textes de commentaire
        selected_ticket (dict): Ticket sélectionné
        
    Returns:
        tuple: (ticket_id, comment_text, user_id) ou valeurs None si invalide
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
    [Output("support-tickets-store", "data", allow_duplicate=True), 
     Output("selected-ticket-store", "data", allow_duplicate=True)],
    [Input("support-refresh-btn", "n_clicks"),
     Input({"type": "update-status-btn", "index": ALL}, "n_clicks")],
    [State("selected-ticket-store", "data"),
     State("support-tickets-store", "data"),
     State({"type": "status-dropdown", "index": ALL}, "value")],
    prevent_initial_call='initial_duplicate'
)
def unified_tickets_callback(refresh_click, update_status_clicks, selected_ticket, tickets_data, status_dropdown_values):
    """
    Callback principal pour rafraîchir les tickets et gérer les mises à jour de statut
    """
    triggered = ctx.triggered_id
    logger.info(f"[unified_tickets_callback] triggered={triggered}")
    
    # Mise à jour du statut si nécessaire
    if isinstance(triggered, dict) and triggered.get("type") == "update-status-btn":
        ticket_id = triggered.get("index")
        try:
            if update_status_clicks:
                idx = max(range(len(update_status_clicks)), key=lambda i: update_status_clicks[i] or 0)
                new_status = status_dropdown_values[idx]
                logger.info(f"[unified_tickets_callback] Mapping bouton {ticket_id} à dropdown index {idx} -> valeur {new_status}")
                update_ticket_status(ticket_id, new_status)
        except Exception as e:
            logger.error(f"[unified_tickets_callback] Erreur lors de la mise à jour du statut: {e}")
    
    # Dans tous les cas, on rafraîchit les données
    data = get_tickets_and_comments()
    logger.info(f"[unified_tickets_callback] {len(data['tickets'])} tickets chargés (après refresh/update)")
    return data, None


@callback(
    [
        # Contenu des listes
        Output("open-tickets-container", "children"),
        Output("closed-tickets-container", "children"),
        # Compteurs
        Output("open-count", "children"),
        Output("closed-count", "children"),
    ],
    [
        # Déclencheurs: changement des données ou du ticket sélectionné
        Input("support-tickets-store", "data"),
        Input("selected-ticket-store", "data")
    ]
)
def update_tickets_lists(tickets_data, selected_ticket):
    """
    Met à jour les listes de tickets par statut et les compteurs associés
    """
    logger.info(f"[update_tickets_lists] MaJ listes tickets, selected={selected_ticket['ticket_id'] if selected_ticket else None}")
    
    if not tickets_data or not tickets_data.get("tickets"):
        logger.warning("[update_tickets_lists] Aucun ticket disponible dans tickets_data")
        empty_message = html.Div("Aucun ticket disponible", className="text-muted text-center py-4")
        return empty_message, empty_message, "0", "0"
    
    # Récupérer l'ID du ticket sélectionné
    selected_id = selected_ticket.get("ticket_id") if selected_ticket else None
    
    # Séparer les tickets par statut
    pending_tickets = [t for t in tickets_data["tickets"] if t.get("status") == "PENDING"]
    closed_tickets = [t for t in tickets_data["tickets"] if t.get("status") == "CLOSED"]
    logger.info(f"[update_tickets_lists] {len(pending_tickets)} tickets PENDING, {len(closed_tickets)} tickets CLOSED")
    
    # Rendre chaque liste avec la fonction de rendu
    pending_list = render_tickets_list(pending_tickets, selected_id) if pending_tickets else html.Div("Aucun ticket en attente", className="text-muted text-center py-4")
    closed_list = render_tickets_list(closed_tickets, selected_id) if closed_tickets else html.Div("Aucun ticket fermé", className="text-muted text-center py-4")
    
    # Mettre à jour les compteurs
    pending_count = str(len(pending_tickets))
    closed_count = str(len(closed_tickets))
    
    return pending_list, closed_list, pending_count, closed_count


@callback(
    Output("selected-ticket-store", "data"),
    [Input("support-tickets-store", "data"),
     Input({"type": "ticket-item", "index": ALL}, "n_clicks")],
    [State("selected-ticket-store", "data")]
)
def update_selected_ticket(tickets_data, ticket_item_n_clicks, selected_ticket):
    """
    Gère la sélection d'un ticket et stocke le ticket sélectionné
    """
    triggered = ctx.triggered_id
    
    if not tickets_data or not tickets_data.get("tickets"):
        return None
    
    # Par défaut, garder le ticket sélectionné actuel
    new_selected = selected_ticket
    
    # Si un ticket a été cliqué
    if triggered and isinstance(triggered, dict) and triggered.get("type") == "ticket-item":
        ticket_id = triggered.get("index")  # Maintenant c'est l'ID du ticket, pas l'index
        
        # Trouver le ticket correspondant à cet ID
        all_tickets = tickets_data["tickets"]
        for ticket in all_tickets:
            if ticket["ticket_id"] == ticket_id:
                new_selected = ticket
                break
    
    # Sélectionner le premier ticket par défaut si aucun n'est sélectionné
    if not new_selected and tickets_data["tickets"]:
        new_selected = tickets_data["tickets"][0]
    
    return new_selected


@callback(
    Output("ticket-details-container", "children"),
    Input("selected-ticket-store", "data"),
    Input("support-tickets-store", "data"),
)
def display_ticket_details(selected_ticket, tickets_data):
    """
    Affiche les détails du ticket sélectionné et ses commentaires
    """
    if not selected_ticket:
        return html.Div("Sélectionnez un ticket pour afficher les détails", className="text-muted text-center py-5")
    
    # Récupérer les commentaires associés à ce ticket
    ticket_id = selected_ticket.get("ticket_id")
    comments = tickets_data.get("comments", {}).get(ticket_id, [])
    
    return render_ticket_details(selected_ticket, comments)


@callback(
    [Output("support-tickets-store", "data", allow_duplicate=True),
     Output({"type": "comment-text", "index": ALL}, "value", allow_duplicate=True)],
    Input({"type": "add-comment-btn", "index": ALL}, "n_clicks"),
    [State({"type": "comment-text", "index": ALL}, "value"),
     State("selected-ticket-store", "data"),
     State("support-tickets-store", "data")],
    prevent_initial_call=True
)
def add_comment_callback(btn_clicks, comment_texts, selected_ticket, tickets_data):
    """
    Gère l'ajout d'un nouveau commentaire à un ticket
    """
    # Validation de l'entrée
    ticket_id, comment_text, user_id = validate_comment_input(btn_clicks, comment_texts, selected_ticket)
    
    # Cas où aucun bouton n'est cliqué ou pas de ticket sélectionné
    if ticket_id is None and comment_text is None:
        logger.debug("[add_comment_callback] Aucun bouton d'ajout de commentaire cliqué ou ticket non sélectionné")
        return tickets_data, [""] * len(comment_texts)
    
    # Cas où le commentaire est vide
    if comment_text is None:
        logger.info(f"[add_comment_callback] Tentative d'ajout de commentaire vide pour le ticket {ticket_id}")
        return tickets_data, [""] * len(comment_texts)
    
    # Ajout du commentaire
    logger.info(f"[add_comment_callback] Utilisateur: {user_id}, Ticket: {ticket_id}, Texte: '{comment_text[:100]}'")
    success = add_support_comment(ticket_id, user_id, comment_text)
    
    if not success:
        return tickets_data, [""] * len(comment_texts)
    
    # Rafraîchir les données après ajout réussi
    data = get_tickets_and_comments()
    return data, [""] * len(comment_texts)
