from dash import html, dcc
import dash_bootstrap_components as dbc
from datetime import datetime
import uuid

# Importer les composants et callbacks pour la page de support
from dash_apps.components.support_tickets import render_tickets_list, render_ticket_details
# Les callbacks sont maintenant dans support_callbacks.py
from dash_apps.components import support_callbacks

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
# Style personnalisé pour la page
support_styles = {
    "main-container": {
        "padding": "20px",
        "backgroundColor": "#f8f9fa",
        "minHeight": "100vh",
        "width": "100%"
    },
    "card": {
        "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
        "borderRadius": "8px",
        "backgroundColor": "white",
        "border": "none"
    },
    "ticket-list": {
        "height": "350px",
        "overflowY": "auto",
        "padding": "5px"
    },
    "details-card": {
        "minHeight": "400px",
        "marginTop": "20px"
    }
}

layout = html.Div([
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

    # Filtres des tickets (par titre et sous-type du message)
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id="ticket-category-filter",
                options=[
                    {"label": "Tous les types", "value": "all"},
                    {"label": "Signalement trajet", "value": "signalement_trajet"},
                ],
                value="all",
                clearable=False,
                placeholder="Filtrer par type de ticket (ex: Signalement trajet)",
                className="mb-2"
            )
        ], width=6),
        dbc.Col([
            dcc.Dropdown(
                id="ticket-subtype-filter",
                options=[
                    {"label": "Tous les sous-types", "value": "all"},
                    {"label": "Conducteur absent", "value": "conducteur_absent"},
                    {"label": "Conducteur en retard", "value": "conducteur_en_retard"},
                    {"label": "Autre", "value": "autre"},
                ],
                value="all",
                clearable=False,
                placeholder="Filtrer par sous-type du message",
            )
        ], width=6),
    ], className="mb-3"),
    
    # Store pour les données des tickets avec cache de session et timestamp
    dcc.Store(id="support-tickets-store", storage_type="session"),
    dcc.Store(id="support-tickets-cache", storage_type="session"),
    dcc.Store(id="support-tickets-timestamp", storage_type="session"),
    
    # Store pour les données des tickets fermés avec cache de session et timestamp
    dcc.Store(id="closed-tickets-store", storage_type="session"),
    dcc.Store(id="closed-tickets-cache", storage_type="session"),
    dcc.Store(id="closed-tickets-timestamp", storage_type="session"),
    
    # Signal pour les mises à jour de tickets (évite les manipulations directes des listes)
    dcc.Store(id="ticket-update-signal", data={"count": 0, "updated_id": None, "status": None}, storage_type="session"),
    
    # Store pour le ticket sélectionné
    dcc.Store(id="selected-ticket-store", storage_type="session"),
    
    # Store pour les commentaires
    dcc.Store(id="ticket-comments-store"),
    
    # Signal spécifique pour les mises à jour de commentaires
    dcc.Store(id="comment-update-signal", data={"count": 0, "updated_id": None}, storage_type="session"),
    
    # Signal pour l'envoi d'emails
    dcc.Store(id="email-send-signal", data={"count": 0, "ticket_id": None, "status": None}, storage_type="session"),

    
    # Layout avec deux colonnes: tickets à gauche, détails à droite
    dbc.Container(
        [
            dbc.Row(
                [
                    # Colonne de gauche avec les listes de tickets empilées verticalement
                    dbc.Col(
                        [
                            # Tickets en attente
                            dbc.Card(
                                [
                                    dbc.CardHeader(["Tickets en attente ", dbc.Badge("0", id="open-count", color="warning", className="ms-1")]),
                                    dbc.CardBody([
                                        html.Div(id="open-tickets-container", style={"height": "500px", "overflowY": "auto"})
                                    ]),
                                    dbc.CardFooter([
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Pagination(
                                                    id="pagination-page",
                                                    max_value=1,
                                                    fully_expanded=False,
                                                    first_last=True,
                                                    previous_next=True,
                                                    size="sm",
                                                )
                                            ], width=8)
                                        ])
                                    ])
                                ],
                                className="mb-3",
                                style={"boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)", "borderRadius": "8px"}
                            ),
                            
                            # Tickets fermés
                            dbc.Card(
                                [
                                    dbc.CardHeader(["Tickets Fermés ", dbc.Badge("0", id="closed-count", color="success", className="ms-1")]),
                                    dbc.CardBody([
                                        html.Div(id="closed-tickets-container", style={"height": "500px", "overflowY": "auto"})
                                    ]),
                                    dbc.CardFooter([
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Pagination(
                                                    id="closed-pagination-page",
                                                    max_value=1,
                                                    fully_expanded=False,
                                                    first_last=True,
                                                    previous_next=True,
                                                    size="sm",
                                                )
                                            ], width=8)
                                        ])
                                    ])
                                ],
                                style={"boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)", "borderRadius": "8px"}
                            ),
                        ],
                        width=4,
                    ),
                    
                    # Colonne de droite avec les détails du ticket
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Détails du Ticket"),
                                dbc.CardBody([
                                    html.Div(id="ticket-details-container")
                                ])
                            ],
                            style={
                                "minHeight": "500px", 
                                "boxShadow": "0 2px 5px rgba(0, 0, 0, 0.1)",
                                "borderRadius": "8px"
                            }
                        ),
                        width=8,
                    ),
                ],
            )
        ],
        fluid=True,
        className="py-3"
    )
])


# Les fonctions d'accès à la base de données et tous les callbacks ont été déplacés dans support_callbacks.py
