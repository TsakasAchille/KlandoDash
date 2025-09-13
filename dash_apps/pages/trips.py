import math
import json
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from dash_apps.config import Config
from dash import html, dcc, register_page
import dash_bootstrap_components as dbc
from dash_apps.components.trips_table_custom import render_custom_trips_table
from dash_apps.components.trip_search_widget import render_trip_search_widget
from dash_apps.utils.settings import load_json_config
from dash_apps.utils.layout_config import create_responsive_col
from dash_apps.repositories.repository_factory import RepositoryFactory
from dash_apps.services.redis_cache import redis_cache
from dash_apps.services.trips_cache_service import TripsCacheService

# L'enregistrement se fera dans app_factory après la création de l'app

## Utiliser la factory pour obtenir le repository approprié
#trip_repository = RepositoryFactory.get_trip_repository()



def get_layout():
    """Génère le layout de la page trajets avec des IDs uniquement pour cette page"""
    return dbc.Container([
    dcc.Location(id="trips-url", refresh=False),
    dcc.Store(id="trips-current-page", storage_type="session", data=1),  # State pour stocker la page courante (persistant)
    dcc.Store(id="selected-trip-id", storage_type="session", data=None, clear_data=False),  # Store pour l'ID du trajet sélectionné (persistant)
    dcc.Store(id="url-trip-parameters", storage_type="memory", data=None),  # Store temporaire pour les paramètres d'URL
    dcc.Store(id="selected-trip-from-url", storage_type="memory", data=None),  # State pour la sélection depuis l'URL
    dcc.Store(id="trips-filter-store", storage_type="session", data={}, clear_data=False),  # Store pour les filtres de recherche
    # Interval pour déclencher la lecture des paramètres d'URL au chargement initial (astuce pour garantir l'exécution)
    dcc.Interval(id='trips-url-init-trigger', interval=100, max_intervals=1),  # Exécute une seule fois au chargement
  
    html.H2("Dashboard trajets", style={"marginTop": "20px"}),
    dbc.Row([
        dbc.Col([], width=9),
        dbc.Col([
            dbc.Button("🔄 Rafraîchir les données", id="refresh-trips-btn", color="primary", className="mb-2")
        ], width=3)
    ]),
    html.Div(id="refresh-trips-message"),
    # Widget de recherche
    render_trip_search_widget(),
    # Affichage des filtres actifs
    html.Div(id="trips-active-filters"),
    dbc.Row([
        dbc.Col([
            # Conteneur vide qui sera rempli par le callback render_trips_table_callback
            html.Div(id="main-trips-content")
        ], width=12)
    ]),
    dbc.Row([
        create_responsive_col(
            "trip_details_panel",
            dcc.Loading(
                children=html.Div(id="trip-details-panel"),
                type="default"
            )
        ),
        create_responsive_col(
            "trip_stats_panel",
            dcc.Loading(
                children=html.Div(id="trip-stats-panel"),
                type="default"
            )
        ),
    ]),
    dbc.Row([
        create_responsive_col(
            "trip_driver_panel",
            dcc.Loading(
                children=html.Div(id="trip-driver-panel"),
                type="default"
            )
        ),
        create_responsive_col(
            "trip_passengers_panel",
            dcc.Loading(
                children=html.Div(id="trip-passengers-panel"),
                type="default"
            )
        )
    ])
], fluid=True)



# Note: Le store trips-page-store n'est plus utilisé pour stocker tous les trajets
# car nous utilisons maintenant un chargement à la demande page par page

# Les callbacks sont maintenant dans callbacks/trips_callbacks.py
from dash_apps.callbacks import trips_callbacks


# Exporter le layout pour l'application principale
layout = get_layout()
