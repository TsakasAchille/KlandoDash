"""
Callbacks pour la page de support technique
Ce fichier contient tous les callbacks liés à la gestion des tickets et commentaires
"""

from dash import callback, Input, Output, State, ctx, ALL, html
from dash_apps.components.support_tickets import render_tickets_list, render_ticket_details
from dash_apps.utils.support_db import (
    get_comments_for_ticket,
    add_comment as db_add_comment
)
from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
from dash_apps.core.database import get_session

import uuid
from datetime import datetime


# Callback pour charger les données des tickets
@callback(
    [Output("support-tickets-store", "data"), Output("selected-ticket-store", "data", allow_duplicate=True)],
    [Input("support-refresh-btn", "n_clicks"),
     Input({"type": "update-status-btn", "index": ALL}, "n_clicks")],
    [State("selected-ticket-store", "data"),
     State("support-tickets-store", "data"),
     State({"type": "status-dropdown", "index": ALL}, "value")],
    prevent_initial_call='initial_duplicate'
)
def unified_tickets_callback(refresh_click, update_status_clicks, selected_ticket, tickets_data, status_dropdown_values):
    from dash import ctx
    triggered = ctx.triggered_id
    # Gestion du clic sur un bouton dynamique
    if isinstance(triggered, dict) and triggered.get("type") == "update-status-btn":
        ticket_id = triggered.get("index")
        # Trouver la valeur du dropdown associé
        new_status = None
        try:
            # L’index du bouton cliqué est celui dont la valeur vient de changer (en général, valeur la plus grande)
            if update_status_clicks:
                idx = max(range(len(update_status_clicks)), key=lambda i: update_status_clicks[i] or 0)
                ticket_id = triggered.get("index")
                new_status = status_dropdown_values[idx]
                print(f"[DEBUG] Mapping bouton {ticket_id} à dropdown index {idx} -> valeur {new_status}")
                if not ticket_id or not new_status:
                    return tickets_data
                print(f"[DEBUG] Mise à jour du statut du ticket {ticket_id} -> {new_status}")
                with get_session() as session:
                    SupportTicketRepository.update_ticket(session, ticket_id, {"status": new_status})
        except Exception as e:
            print(f"[ERROR] Impossible de retrouver la valeur du dropdown pour le ticket {ticket_id}: {e}")
            return tickets_data
    # Dans tous les cas, on recharge la liste (refresh ou update)
    with get_session() as session:
        tickets = SupportTicketRepository.list_tickets(session)
        tickets = [t.model_dump() for t in tickets]
    comments = {}
    for ticket in tickets:
        ticket_id = ticket["ticket_id"]
        ticket_comments = get_comments_for_ticket(ticket_id)
        if ticket_comments:
            comments[ticket_id] = ticket_comments
    data = {"tickets": tickets, "comments": comments}
    print(f"[DEBUG] {len(tickets)} tickets chargés (après refresh/update)")
    return data, None


# Callback pour mettre à jour les 3 listes de tickets et les compteurs
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
    # Ce callback doit se déclencher quand les données des tickets changent
    Input("support-tickets-store", "data"),
    # ET quand le ticket sélectionné change, pour mettre à jour la sélection visuelle
    Input("selected-ticket-store", "data")
]
)
def update_tickets_lists(tickets_data, selected_ticket):
    if not tickets_data or not tickets_data.get("tickets"):
        empty_message = html.Div("Aucun ticket disponible", className="text-muted text-center py-4")
        return empty_message, empty_message, empty_message, "0", "0", "0"
    
    # Récupérer l'ID du ticket sélectionné
    selected_id = selected_ticket.get("ticket_id") if selected_ticket else None
    
    # Séparer les tickets par statut
    pending_tickets = [t for t in tickets_data["tickets"] if t.get("status") == "PENDING"]
    closed_tickets = [t for t in tickets_data["tickets"] if t.get("status") == "CLOSED"]
    
    # Rendre chaque liste avec la fonction de rendu
    pending_list = render_tickets_list(pending_tickets, selected_id) if pending_tickets else html.Div("Aucun ticket en attente", className="text-muted text-center py-4")
    closed_list = render_tickets_list(closed_tickets, selected_id) if closed_tickets else html.Div("Aucun ticket fermé", className="text-muted text-center py-4")
    
    # Mettre à jour les compteurs
    pending_count = str(len(pending_tickets))
    closed_count = str(len(closed_tickets))
    
    return pending_list, closed_list, pending_count, closed_count


# Callback pour stocker le ticket sélectionné
@callback(
    Output("selected-ticket-store", "data"),
    [Input("support-tickets-store", "data"),
     Input({"type": "ticket-item", "index": ALL}, "n_clicks")],
    [State("selected-ticket-store", "data")]
)
def update_selected_ticket(tickets_data, ticket_clicks, selected_ticket):
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


# Callback pour afficher les détails du ticket et les commentaires
@callback(
    Output("ticket-details-container", "children"),
    Input("selected-ticket-store", "data"),
    Input("support-tickets-store", "data"),
)
def display_ticket_details(selected_ticket, tickets_data):
    if not selected_ticket:
        return html.Div("Sélectionnez un ticket pour afficher les détails", className="text-muted text-center py-5")
    
    # Récupérer les commentaires associés à ce ticket
    ticket_id = selected_ticket.get("ticket_id")
    comments = tickets_data.get("comments", {}).get(ticket_id, [])
    
    return render_ticket_details(selected_ticket, comments)


# Callback pour mettre à jour le statut d'un ticket


# Callback pour ajouter un commentaire à un ticket
@callback(
    [Output("support-tickets-store", "data", allow_duplicate=True),
     Output({"type": "comment-text", "index": ALL}, "value")],
    Input({"type": "add-comment-btn", "index": ALL}, "n_clicks"),
    [State({"type": "comment-text", "index": ALL}, "value"),
     State("selected-ticket-store", "data"),
     State("support-tickets-store", "data")],
    prevent_initial_call=True
)
def add_comment_callback(btn_clicks, comment_texts, selected_ticket, tickets_data):
    from flask import session
    # Vérifier si un bouton a été cliqué
    if not any(btn_clicks) or not selected_ticket or not selected_ticket.get("ticket_id"):
        return tickets_data, [""] * len(comment_texts)
    
    # Récupérer l'ID du ticket sélectionné
    ticket_id = selected_ticket["ticket_id"]
    
    # Trouver le texte du commentaire
    comment_text = None
    for i, clicks in enumerate(btn_clicks):
        if clicks:  # Si ce bouton a été cliqué
            if i < len(comment_texts):
                comment_text = comment_texts[i]
                break
    
    if not comment_text or not comment_text.strip():
        # Si le commentaire est vide, on ne fait rien
        return tickets_data, [""] * len(comment_texts)
    
    # Récupérer le nom et l'ID de l'utilisateur connecté depuis la session
    user_name = session.get('user_name', 'Utilisateur')
    user_id = session.get('user_id', 'anonymous')
    
    # Ajouter le commentaire dans la base de données
    success = db_add_comment(
        ticket_id,
        user_name,  # Nom de l'utilisateur connecté
        comment_text.strip()
    )
    
    if success:
        # Mise à jour des données locales
        updated_data = tickets_data.copy()
        
        # On ajoute le nouveau commentaire localement
        if "comments" not in updated_data:
            updated_data["comments"] = {}
            
        if ticket_id not in updated_data["comments"]:
            updated_data["comments"][ticket_id] = []
        
        # Créer un nouveau commentaire pour l'affichage local
        new_comment = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "user_name": user_name,
            "comment_text": comment_text.strip(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
            
        updated_data["comments"][ticket_id].append(new_comment)
        
        # Mettre à jour la date de mise à jour du ticket
        for i, ticket in enumerate(updated_data["tickets"]):
            if ticket["ticket_id"] == ticket_id:
                updated_data["tickets"][i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
        
        print(f"[DEBUG] Commentaire ajouté avec succès au ticket {ticket_id}")
        return updated_data, [""] * len(comment_texts)
    else:
        print(f"[ERROR] Échec de l'ajout du commentaire au ticket {ticket_id}")
        return tickets_data, [""] * len(comment_texts)  # Vider les champs de commentaire
