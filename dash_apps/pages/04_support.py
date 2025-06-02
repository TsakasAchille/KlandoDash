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
    
    # Store pour les données des tickets
    dcc.Store(id="support-tickets-store"),
    
    # Store pour le ticket sélectionné
    dcc.Store(id="selected-ticket-store"),
    
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
                                        html.Div(id="open-tickets-container", style={"height": "220px", "overflowY": "auto"})
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
                                        html.Div(id="closed-tickets-container", style={"height": "220px", "overflowY": "auto"})
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
