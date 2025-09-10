import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

# L'enregistrement se fera dans app_factory après la création de l'app

# Importer les composants avec templates Jinja2
from dash_apps.components.stats_general import render_stats_general
from dash_apps.components.stats_temporal import render_stats_temporal
from dash_apps.components.stats_geographic import render_stats_geographic
from dash_apps.components.stats_financial import render_stats_financial
from dash_apps.components.stats_map import render_stats_map

# Layout de la page de statistiques - Version débogging simple
layout = dbc.Container([
    html.H2("Statistiques et Analytics", style={"marginTop": "20px", "marginBottom": "20px"}),
    
    # Bouton de rafraîchissement des données
    dbc.Row([
        dbc.Col([], width=9),
        dbc.Col([
            dbc.Button("🔄 Rafraîchir les données", id="stats-refresh-btn", color="primary", className="mb-4")
        ], width=3)
    ]),
    
    # Suppression du message de rafraîchissement qui n'est plus utilisé
    
    # Store pour les données
    dcc.Store(id="stats-trips-store"),
    
    # Système d'onglets pour les statistiques
    dcc.Tabs(
        [
            dcc.Tab(
                label="Vue générale",
                value="tab-general",
                children=[
                    html.Div(id="stats-general-container", className="p-3")
                ]
            ),
            dcc.Tab(
                label="Analyse temporelle",
                value="tab-temporal",
                children=[
                    html.Div(id="stats-temporal-container", className="p-3")
                ]
            ),
            dcc.Tab(
                label="Analyse géographique",
                value="tab-geographic",
                children=[
                    html.Div(id="stats-geographic-container", className="p-3")
                ]
            ),
            dcc.Tab(
                label="Analyse financière",
                value="tab-financial",
                children=[
                    html.Div(id="stats-financial-container", className="p-3")
                ]
            )
        ],
        id="stats-tabs",
        value="tab-general",
        className="mb-3"
    )
], fluid=True)

# Les callbacks sont maintenant dans callbacks/stats_callbacks.py
from dash_apps.callbacks import stats_callbacks
