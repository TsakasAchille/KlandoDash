import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import dash
import pandas as pd
from dash_apps.repositories.user_repository import UserRepository
from dash_apps.utils.admin_db import is_admin
from dash_apps.utils.user_data_old import update_user_field
from flask import session

# ID du store pour rafraîchissement
refresh_store_id = "driver-validation-refresh"

# Layout principal de la page de validation des documents conducteur
def serve_layout():
    user_email = session.get('user_email', None)
    if not is_admin(user_email):
        return dbc.Container([
            html.H2("Accès refusé", style={"marginTop": "20px"}),
            dbc.Alert("Vous n'êtes pas autorisé à accéder à cette page.", color="danger")
        ], fluid=True)
    else:
        return dbc.Container([
            html.H2("Validation des documents conducteur", style={"marginTop": "20px"}),
            html.P("Cette page permet aux administrateurs de vérifier et valider les documents soumis par les conducteurs.",
                   className="text-muted"),
            # Stores pour les données
            dcc.Store(id="drivers-data-store"),
            dcc.Store(id=refresh_store_id, data=0),
            dbc.Card([
                dbc.CardHeader("Documents conducteurs"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Badge(id="documents-count-badge", color="primary", className="me-1"),
                            html.Span(" documents au total", className="text-muted")
                        ], width=12)
                    ])
                ])
            ]),
            
            # Onglets avec style amélioré
            dbc.Card([
                dbc.CardHeader(
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Documents en attente", href="#", id="tab1-link", active=True, className="fw-bold")),
                        dbc.NavItem(dbc.NavLink("Documents validés", href="#", id="tab2-link")),
                    ], pills=True, card=True, className="nav-justified"),
                ),
                dbc.CardBody([
                    # Premier onglet
                    html.Div([
                        html.Div(id="pending-documents-container", className="mt-2"),
                        dbc.Pagination(
                            id="pending-page",
                            max_value=1,
                            fully_expanded=False,
                            first_last=True,
                            previous_next=True,
                            active_page=1,
                            className="mt-3"
                        ),
                    ], id="tab-content-1"),
                    
                    # Second onglet (invisible au départ)
                    html.Div([
                        html.Div(id="validated-documents-container", className="mt-2"),
                        dbc.Pagination(
                            id="validated-page",
                            max_value=1,
                            fully_expanded=False,
                            first_last=True,
                            previous_next=True,
                            active_page=1,
                            className="mt-3"
                        ),
                    ], id="tab-content-2", style={"display": "none"}),
                ]),
            ], className="mt-3")
        ])

layout = serve_layout

# DEBUG - Chargement du module 06_driver_validation.py
print("[DEBUG] 06_driver_validation.py chargé")

# DEBUG - Layout défini
print("[DEBUG] Layout de la page driver_validation défini")

# Enregistrement des callbacks de validation (modulaire)
try:
    from dash_apps.components import driver_validation_callbacks
    print("[DEBUG] Module driver_validation_callbacks importé avec succès")
except Exception as e:
    print(f"[DEBUG] Erreur lors de l'import de driver_validation_callbacks : {e}")

