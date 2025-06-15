import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import dash
import pandas as pd
from dash_apps.repositories.user_repository import UserRepository
from dash_apps.utils.admin_db import is_admin
from dash_apps.utils.user_data_old import update_user_field
from flask import session

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
            dbc.Card([
                dbc.CardHeader("Liste des documents à valider"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Badge(id="documents-count-badge", color="primary", className="me-1"),
                            html.Span(" documents en attente de validation", className="text-muted")
                        ], width=6),
                        dbc.Col([
                            html.Div([
                                dbc.Label("Filtrer par statut:"),
                                dbc.RadioItems(
                                    options=[
                                        {"label": "En attente de validation", "value": "pending"},
                                        {"label": "Documents validés", "value": "validated"}
                                    ],
                                    value="pending",
                                    id="validation-filter",
                                    inline=True
                                )
                            ])
                        ], width=6)
                    ])
                ]),
                html.Div(id="drivers-documents-container")
            ])
        ])

import dash

refresh_store_id = "driver-validation-refresh"

# Ajout du Store dans le layout

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
            dcc.Store(id="drivers-data-store"),
            dcc.Store(id=refresh_store_id, data=0),
            dbc.Card([
                dbc.CardHeader("Liste des documents à valider"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Badge(id="documents-count-badge", color="primary", className="me-1"),
                            html.Span(" documents en attente de validation", className="text-muted")
                        ], width=6),
                        dbc.Col([
                            html.Div([
                                dbc.Label("Filtrer par statut:"),
                                dbc.RadioItems(
                                    options=[
                                        {"label": "En attente de validation", "value": "pending"},
                                        {"label": "Documents validés", "value": "validated"}
                                    ],
                                    value="pending",
                                    id="validation-filter",
                                    inline=True
                                )
                            ])
                        ], width=6)
                    ])
                ]),
                html.Div(id="drivers-documents-container")
            ])
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

