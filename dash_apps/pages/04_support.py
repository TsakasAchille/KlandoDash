from dash import html, dcc, callback, Input, Output, State, ctx, ALL
import dash_bootstrap_components as dbc
import pandas as pd
import uuid
from datetime import datetime

# Component pour gérer les tickets de support
from dash_apps.components.support_tickets import render_tickets_list, render_ticket_details, update_ticket_status, add_ticket_comment

# CSS personnalisé pour la page de support
support_css = '''
<style>
    .ticket-row:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12) !important;
        transition: all 0.2s ease;
    }
</style>
'''

# Layout de la page de support technique
layout = dbc.Container([
    # Injecter le CSS personnalisé
    html.Div(html.Iframe(srcDoc=support_css, style={'display': 'none'})),
    html.H2("Support Technique", style={"marginTop": "20px", "marginBottom": "20px"}),
    
    # Bouton de rafraîchissement des données
    dbc.Row([
        dbc.Col([], width=9),
        dbc.Col([
            dbc.Button("🔄 Rafraîchir les données", id="support-refresh-btn", color="primary", className="mb-4")
        ], width=3)
    ]),
    
    # Store pour les données des tickets
    dcc.Store(id="support-tickets-store"),
    
    # Store pour le ticket sélectionné
    dcc.Store(id="selected-ticket-store"),
    
    # Layout principal avec 2 colonnes: liste des tickets et détails
    dbc.Row([
        # Colonne gauche: Liste des tickets
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Liste des Tickets"),
                dbc.CardBody([
                    html.Div(id="tickets-list-container")
                ])
            ])
        ], width=4),
        
        # Colonne droite: Détails du ticket et commentaires
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Détails du Ticket"),
                dbc.CardBody([
                    html.Div(id="ticket-details-container")
                ])
            ])
        ], width=8)
    ])
])


# Import des fonctions d'accès à la base de données
from dash_apps.utils.support_db import (
    get_all_tickets, 
    get_ticket_by_id, 
    get_comments_for_ticket,
    update_ticket_status as db_update_ticket_status,
    add_comment as db_add_comment
)

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


# Callback pour stocker le ticket sélectionné et afficher les tickets
@callback(
    [Output("selected-ticket-store", "data"),
     Output("tickets-list-container", "children")],
    [Input("support-tickets-store", "data"),
     Input({"type": "ticket-item", "index": ALL}, "n_clicks")],
    [State("selected-ticket-store", "data")]
)
def update_tickets_and_selection(tickets_data, ticket_clicks, selected_ticket):
    triggered = ctx.triggered_id
    
    if not tickets_data:
        return None, html.Div("Aucun ticket disponible")
    
    # Par défaut, garder le ticket sélectionné actuel
    new_selected = selected_ticket
    
    # Si un ticket a été cliqué
    if triggered and isinstance(triggered, dict) and triggered.get("type") == "ticket-item":
        ticket_index = triggered.get("index")
        if ticket_index < len(tickets_data["tickets"]):
            new_selected = tickets_data["tickets"][ticket_index]
    
    # Sélectionner le premier ticket par défaut si aucun n'est sélectionné
    if not new_selected and tickets_data["tickets"]:
        new_selected = tickets_data["tickets"][0]
    
    # Obtenir l'ID du ticket sélectionné
    selected_id = new_selected.get("ticket_id") if new_selected else None
    
    # Rendre la liste des tickets
    tickets_list = render_tickets_list(tickets_data["tickets"], selected_id)
    
    return new_selected, tickets_list


# Callback pour afficher les détails du ticket et les commentaires
@callback(
    Output("ticket-details-container", "children"),
    Input("selected-ticket-store", "data"),
    Input("support-tickets-store", "data"),
)
def display_ticket_details(selected_ticket, tickets_data):
    if not selected_ticket or not tickets_data:
        return html.Div("Sélectionnez un ticket pour voir les détails")
    
    # Récupérer les commentaires pour ce ticket
    ticket_id = selected_ticket["ticket_id"]
    comments = tickets_data["comments"].get(ticket_id, [])
    
    return render_ticket_details(selected_ticket, comments)


# Callback pour mettre à jour le statut d'un ticket
@callback(
    Output("support-tickets-store", "data", allow_duplicate=True),
    Input("update-status-button", "n_clicks"),
    State("status-dropdown", "value"),
    State("selected-ticket-store", "data"),
    State("support-tickets-store", "data"),
    prevent_initial_call=True
)
def update_ticket_status_callback(n_clicks, new_status, selected_ticket, tickets_data):
    if not n_clicks or not selected_ticket or not new_status:
        return tickets_data
        
    ticket_id = selected_ticket["ticket_id"]
    
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
     Output("comment-input", "value")],  # Vider le champ de commentaire après ajout
    Input("add-comment-button", "n_clicks"),
    State("comment-input", "value"),
    State("selected-ticket-store", "data"),
    State("support-tickets-store", "data"),
    prevent_initial_call=True
)
def add_comment_callback(n_clicks, comment_text, selected_ticket, tickets_data):
    if not n_clicks or not comment_text or not selected_ticket:
        return tickets_data, ""
    
    # Ajouter un nouveau commentaire dans la base de données
    ticket_id = selected_ticket["ticket_id"]
    user_id = "admin"  # Dans une version réelle, ce serait l'utilisateur connecté
    
    # Appel à la fonction de la base de données
    new_comment = db_add_comment(ticket_id, user_id, comment_text)
    
    if new_comment:
        # Mise à jour des données locales
        updated_data = tickets_data.copy()
        
        # Initialiser la liste de commentaires si nécessaire
        if ticket_id not in updated_data["comments"]:
            updated_data["comments"][ticket_id] = []
        
        # Ajouter le nouveau commentaire
        updated_data["comments"][ticket_id].append(new_comment)
        
        # Mettre à jour la date de mise à jour du ticket
        for i, ticket in enumerate(updated_data["tickets"]):
            if ticket["ticket_id"] == ticket_id:
                updated_data["tickets"][i]["updated_at"] = new_comment["created_at"]
                break
        
        print(f"[DEBUG] Commentaire ajouté avec succès au ticket {ticket_id}")
        return updated_data, ""  # Vider le champ de commentaire
    else:
        print(f"[ERROR] Échec de l'ajout du commentaire au ticket {ticket_id}")
        return tickets_data, comment_text  # Garder le commentaire dans le champ
