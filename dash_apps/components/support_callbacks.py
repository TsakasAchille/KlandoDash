"""
Callbacks pour la page de support technique
Ce fichier contient tous les callbacks liés à la gestion des tickets et commentaires
"""

from dash import callback, Input, Output, State, ctx, ALL, html
from dash_apps.components.support_tickets import render_tickets_list, render_ticket_details
from dash_apps.utils.support_db import (
    get_all_tickets,
    get_ticket_by_id,
    get_comments_for_ticket,
    update_ticket_status as db_update_ticket_status,
    add_comment as db_add_comment
)
import uuid
from datetime import datetime


# Callback pour charger les données des tickets
@callback(
    Output("support-tickets-store", "data"),
    Input("support-refresh-btn", "n_clicks")
)
def load_support_tickets(n_clicks):
    print(f"[DEBUG] Tentative de chargement des tickets... (n_clicks={n_clicks})")
    
    # Récupérer les tickets depuis la base de données
    tickets = get_all_tickets()
    
    # Si nous n'avons pas pu récupérer de tickets (erreur), utiliser des données fictives pour l'exemple
    if not tickets:
        print("[WARNING] Aucun ticket trouvé en base de données. Utilisation de données fictives.")
        tickets = [
            {
                "ticket_id": str(uuid.uuid4()),
                "user_id": "user123",
                "objet": "Problème de réservation",
                "message": "Je n'arrive pas à finaliser ma réservation pour le trajet Paris-Lyon.",
                "status": "open",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "contact_preference": "email",
                "phone": "+33612345678",
                "mail": "user123@example.com"
            }
        ]
    
    # Initialiser le dictionnaire de commentaires
    comments = {}
    
    # Récupérer les commentaires pour chaque ticket
    for ticket in tickets:
        ticket_id = ticket["ticket_id"]
        ticket_comments = get_comments_for_ticket(ticket_id)
        if ticket_comments:
            comments[ticket_id] = ticket_comments
    
    # Combiner tickets et commentaires
    data = {"tickets": tickets, "comments": comments}
    
    print(f"[DEBUG] {len(tickets)} tickets chargés")
    return data


# Callback pour mettre à jour les 3 listes de tickets et les compteurs
@callback(
[
    # Contenu des listes
    Output("open-tickets-container", "children"),
    Output("progress-tickets-container", "children"),
    Output("closed-tickets-container", "children"),
    
    # Compteurs
    Output("open-count", "children"),
    Output("progress-count", "children"),
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
    open_tickets = [t for t in tickets_data["tickets"] if t.get("status") == "open"]
    progress_tickets = [t for t in tickets_data["tickets"] if t.get("status") == "in progress"]
    closed_tickets = [t for t in tickets_data["tickets"] if t.get("status") == "closed"]
    
    # Rendre chaque liste avec la fonction de rendu
    open_list = render_tickets_list(open_tickets, selected_id) if open_tickets else html.Div("Aucun ticket ouvert", className="text-muted text-center py-4")
    progress_list = render_tickets_list(progress_tickets, selected_id) if progress_tickets else html.Div("Aucun ticket en cours", className="text-muted text-center py-4")
    closed_list = render_tickets_list(closed_tickets, selected_id) if closed_tickets else html.Div("Aucun ticket fermé", className="text-muted text-center py-4")
    
    # Mettre à jour les compteurs
    open_count = str(len(open_tickets))
    progress_count = str(len(progress_tickets))
    closed_count = str(len(closed_tickets))
    
    return open_list, progress_list, closed_list, open_count, progress_count, closed_count


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
@callback(
    Output("support-tickets-store", "data", allow_duplicate=True),
    Input({"type": "update-status-btn", "index": ALL}, "n_clicks"),
    State({"type": "status-dropdown", "index": ALL}, "value"),
    State("selected-ticket-store", "data"),
    State("support-tickets-store", "data"),
    prevent_initial_call=True
)
def update_ticket_status_callback(btn_clicks, status_values, selected_ticket, tickets_data):
    # Vérifier si un bouton a été cliqué
    if not any(btn_clicks) or not selected_ticket or not selected_ticket.get("ticket_id"):
        return tickets_data
    
    # Récupérer l'ID du ticket sélectionné
    ticket_id = selected_ticket["ticket_id"]
    
    # Trouver la valeur du statut correspondant au ticket sélectionné
    # en cherchant l'élément qui a le même index (ticket_id)
    new_status = None
    for i, clicks in enumerate(btn_clicks):
        if clicks:  # Si ce bouton a été cliqué
            if i < len(status_values):
                new_status = status_values[i]
                break
    
    if not new_status:
        return tickets_data
    
    # Mettre à jour le statut dans la base de données
    success = db_update_ticket_status(ticket_id, new_status)
    
    if success:
        # Mettre à jour les données localement pour éviter de recharger tous les tickets
        updated_tickets = tickets_data.copy()
        for i, ticket in enumerate(updated_tickets["tickets"]):
            if ticket["ticket_id"] == ticket_id:
                updated_tickets["tickets"][i]["status"] = new_status
                updated_tickets["tickets"][i]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break
        
        print(f"[DEBUG] Statut du ticket {ticket_id} mis à jour avec succès: {new_status}")
        return updated_tickets
    else:
        print(f"[ERROR] Échec de la mise à jour du statut pour le ticket {ticket_id}")
        return tickets_data


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
