from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

# Importer les composants avec templates Jinja2
from dash_apps.components.stats_general import render_stats_general
from dash_apps.components.stats_temporal import render_stats_temporal

# Layout de la page de statistiques
layout = dbc.Container([
    html.H2("Statistiques et Analytics", style={"marginTop": "20px", "marginBottom": "20px"}),
    
    # Bouton de rafraîchissement des données
    dbc.Row([
        dbc.Col([], width=9),
        dbc.Col([
            dbc.Button("🔄 Rafraîchir les données", id="stats-refresh-btn", color="primary", className="mb-4")
        ], width=3)
    ]),
    
    # Message de rafraîchissement
    html.Div(id="stats-refresh-message"),
    
    # Store pour les données
    dcc.Store(id="stats-trips-store"),
    
    # Composant de statistiques générales avec template
    html.Div(id="stats-general-container"),
    
    # Composant de statistiques temporelles avec template
    html.Div(id="stats-temporal-container")
], fluid=True)

# --- Callbacks Dash ---

@callback(
    Output("stats-trips-store", "data"),
    Input("stats-refresh-btn", "n_clicks"),
    prevent_initial_call=False
)
def load_stats_data(n_clicks):
    """Charge les données des trajets pour les statistiques"""
    try:
        # Obtenir les données de trajet du processeur
        from src.streamlit_apps.pages.components.trips import get_trip_data  # TEMPORAIRE
        trips_df = get_trip_data()
        
        # Convertir en dict pour stockage
        trips_data = trips_df.to_dict("records") if trips_df is not None else None
        return trips_data
    except Exception as e:
        print(f"Erreur lors du chargement des données : {str(e)}")
        return None

@callback(
    Output("stats-refresh-message", "children"),
    Input("stats-refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_stats_refresh_message(n_clicks):
    """Affiche un message de confirmation après le rafraîchissement des données"""
    return dbc.Alert(
        "Données rafraîchies avec succès!",
        color="success",
        dismissable=True,
        duration=3000,
    )

@callback(
    Output("stats-general-container", "children"),
    Input("stats-trips-store", "data")
)
def update_stats_general(trips_data):
    """Mettre à jour les statistiques générales avec le composant utilisant le template Jinja2"""
    return render_stats_general(trips_data)

@callback(
    Output("stats-temporal-container", "children"),
    Input("stats-trips-store", "data")
)
def update_stats_temporal(trips_data):
    """Mettre à jour les statistiques temporelles avec le composant utilisant le template Jinja2"""
    return render_stats_temporal(trips_data)

# Les callbacks pour les composants avec templates Jinja2 sont déjà définis plus haut

# Les callbacks pour les composants avec templates Jinja2 sont déjà définis plus haut
