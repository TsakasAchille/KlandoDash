import math
import json
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from dash_apps.config import Config
# Import du nouveau composant personnalisé à la place du DataTable
from dash_apps.components.users_table import render_custom_users_table
from dash_apps.components.user_profile import render_user_profile
from dash_apps.components.user_stats import render_user_stats
from dash_apps.components.user_trips import render_user_trips
from dash_apps.components.user_search_widget import render_search_widget, render_active_filters
from dash_apps.utils.layout_config import create_responsive_col
from dash_apps.repositories.repository_factory import RepositoryFactory
from dash_apps.services.redis_cache import redis_cache
from dash_apps.services.users_cache_service import UsersCacheService
from dash_apps.services.user_panels_preloader import UserPanelsPreloader

# L'enregistrement se fera dans app_factory après la création de l'app

# Constante pour l'espacement entre les layouts
ROW_SPACING = "mb-4"



def get_layout():
    """Génère le layout de la page utilisateurs avec des IDs uniquement pour cette page"""
    return dbc.Container([
    dcc.Location(id="users-url", refresh=False),
    #dcc.Store(id="users-pagination-info", data={"page_count": 1, "total_users": 0}),
    dcc.Store(id="users-current-page", storage_type="session", data=1),  # State pour stocker la page courante (persistant)
    dcc.Store(id="selected-user-uid", storage_type="session", data=None, clear_data=False),  # Store pour l'UID de l'utilisateur sélectionné (persistant)
    dcc.Store(id="selected-users-store", storage_type="session", data=[]),  # UIDs des utilisateurs sélectionnés avec cases à cocher
    # Cache session pour éviter les rechargements inutiles (clé = page + filtres)
    dcc.Store(id="users-page-cache", storage_type="session", data={}, clear_data=False),
    # Store session pour précharger les données nécessaires aux panneaux (profil, stats, aperçus trajets)
    dcc.Store(id="users-panels-store", storage_type="session", data={}, clear_data=False),
    dcc.Store(id="url-parameters", storage_type="memory", data=None),  # Store temporaire pour les paramètres d'URL
    dcc.Store(id="selected-user-from-url", storage_type="memory", data=None),  # State pour la sélection depuis l'URL
    dcc.Store(id="users-filter-store", storage_type="session", data={}, clear_data=False),  # Store pour les filtres de recherche
    # Interval pour déclencher la lecture des paramètres d'URL au chargement initial (astuce pour garantir l'exécution)
    dcc.Interval(id='url-init-trigger', interval=100, max_intervals=1),  # Exécute une seule fois au chargement
  
    html.H2("Dashboard utilisateurs", style={"marginTop": "20px"}),
    dbc.Row([
        dbc.Col([], width=9),
        dbc.Col([
            dbc.Button("🔄 Rafraîchir les données", id="refresh-users-btn", color="primary", className="mb-2")
        ], width=3)
    ]),
    html.Div(id="refresh-users-message"),
    # Widget de recherche
    render_search_widget(),
    # Affichage des filtres actifs
    html.Div(id="users-active-filters"),
    dbc.Row([
        dbc.Col([
            # Conteneur vide qui sera rempli par le callback render_users_table_callback
            html.Div(id="main-users-content")
        ], width=12)
    ]),
    dbc.Row([
        create_responsive_col(
            "user_details_panel",
            [
                # Header avec titre et icône
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-user-circle me-2", style={"color": "#007bff"}),
                        html.H5("Détails de l'utilisateur", className="mb-0", style={"color": "#333"})
                    ], style={"background-color": "#f8f9fa", "border-bottom": "2px solid #007bff"}),
                    dbc.CardBody([
                        dcc.Loading(
                            children=html.Div(id="user-details-panel"),
                            type="default"
                        )
                    ], style={"padding": "0"})
                ], style={"border": "1px solid #dee2e6", "border-radius": "8px"})
            ],
            config_file="user_details_config.json"
        ),
        create_responsive_col(
            "user_stats_panel",
            [
                # Header avec titre et icône
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-bar me-2", style={"color": "#28a745"}),
                        html.H5("Statistiques", className="mb-0", style={"color": "#333"})
                    ], style={"background-color": "#f8f9fa", "border-bottom": "2px solid #28a745"}),
                    dbc.CardBody([
                        dcc.Loading(
                            children=html.Div(id="user-stats-panel"),
                            type="default"
                        )
                    ], style={"padding": "0"})
                ], style={"border": "1px solid #dee2e6", "border-radius": "8px"})
            ],
            config_file="user_details_config.json"
        ),
    ], className=ROW_SPACING),
    dbc.Row([
        create_responsive_col(
            "user_trips_panel",
            [
                # Header avec titre et icône
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-route me-2", style={"color": "#17a2b8"}),
                        html.H5("Trajets de l'utilisateur", className="mb-0", style={"color": "#333"})
                    ], style={"background-color": "#f8f9fa", "border-bottom": "2px solid #17a2b8"}),
                    dbc.CardBody([
                        dcc.Loading(
                            children=html.Div(id="user-trips-panel"),
                            type="default"
                        )
                    ], style={"padding": "0"})
                ], style={"border": "1px solid #dee2e6", "border-radius": "8px"})
            ],
            config_file="user_details_config.json"
        ),
    ], className=ROW_SPACING)
], fluid=True)



# Note: Le store users-page-store n'est plus utilisé pour stocker tous les utilisateurs
# car nous utilisons maintenant un chargement à la demande page par page

# Les callbacks sont maintenant dans callbacks/users_callbacks.py
from dash_apps.callbacks import users_callbacks



layout = get_layout()
