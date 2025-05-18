from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

# Imports pour le traitement des données
from src.data_processing.processors.user_processor import UserProcessor
from dash_apps.components.trips_table import render_trips_table
from dash_apps.components.trip_details_layout import create_trip_details_layout

# Layout de la page des trajets avec des IDs uniques
def get_layout():
    """Génère le layout de la page des trajets avec des IDs uniquement pour cette page"""
    return dbc.Container([
        dcc.Store(id="klando-users-store"),
        dcc.Store(id="klando-trips-store"),
        dcc.Store(id="klando-selected-trip-id", storage_type="session"),
        
        html.H2("Dashboard utilisateurs et trajets", style={"marginTop": "20px"}),
        dbc.Row([
            dbc.Col([], width=9),
            dbc.Col([
                dbc.Button("🔄 Rafraîchir les données", id="klando-refresh-btn", color="primary", className="mb-2")
            ], width=3)
        ]),
        html.Div(id="klando-refresh-message"),
        
        # Zone principale qui sera mise à jour par les callbacks
        html.Div(id="klando-trips-main-area"),
        
        # Zone pour les détails
        html.Div(id="klando-trip-details-area")
    ], fluid=True)

# Chargement initial et rafraîchissement des données
@callback(
    [Output("klando-users-store", "data"),
     Output("klando-trips-store", "data")],
    [Input("klando-refresh-btn", "n_clicks")]
)
def load_data(n_clicks):
    # Charger les données utilisateurs et trajets
    users_df = UserProcessor.get_all_users()
    # get_trip_data doit retourner un DataFrame de trajets
    from src.streamlit_apps.pages.components.trips import get_trip_data  # TEMPORAIRE
    trips_df = get_trip_data()
    
    users_data = users_df.to_dict("records") if users_df is not None else []
    trips_data = trips_df.to_dict("records") if trips_df is not None else []
    
    return users_data, trips_data

# Message de rafraîchissement
@callback(
    Output("klando-refresh-message", "children"),
    Input("klando-refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_refresh_message(n_clicks):
    return dbc.Alert("Données rafraîchies! Les nouveaux voyages sont maintenant visibles.", 
                     color="success", 
                     dismissable=True,
                     duration=4000)  # Disparait après 4 secondes

# Affichage du contenu principal
@callback(
    Output("klando-trips-main-area", "children"),
    [Input("klando-users-store", "data"),
     Input("klando-trips-store", "data"),
     Input("klando-selected-trip-id", "data")]
)
def update_trips_content(users_data, trips_data, selected_trip_id):
    # Vérifier si les données sont disponibles
    if not trips_data:
        return dbc.Alert(
            "Chargement des données... Si ce message persiste, vérifiez la connexion à la base de données.",
            color="warning",
            className="mt-3"
        )

    # Préparer les données pour affichage
    trips_df = pd.DataFrame(trips_data)
    
    # Présélectionner une ligne si un trajet est déjà sélectionné
    preselect_row = []
    if selected_trip_id and 'trip_id' in trips_df.columns:
        idx = trips_df.index[trips_df['trip_id'] == selected_trip_id].tolist()
        if idx:
            preselect_row = [idx[0]]
    
    # Créer le tableau des trajets
    table = render_trips_table(trips_df, selected_rows=preselect_row, table_id="klando-trips-table")
    
    instruction = html.P("Sélectionnez un trajet dans le tableau pour voir les détails.", 
                       className="text-muted fst-italic")
    
    return html.Div([
        instruction, 
        table, 
        html.Hr(className="my-4")
    ])

# Mise à jour de l'ID du trajet sélectionné
@callback(
    Output("klando-selected-trip-id", "data"),
    [Input("klando-trips-table", "selected_rows")],
    [State("klando-trips-store", "data")]
)
def update_selected_trip_id(selected_rows, trips_data):
    if selected_rows and trips_data:
        trips_df = pd.DataFrame(trips_data)
        selected_trip_id = trips_df.iloc[selected_rows[0]]['trip_id']
        return selected_trip_id
    return None

# Affichage des détails du trajet sélectionné
@callback(
    Output("klando-trip-details-area", "children"),
    [Input("klando-selected-trip-id", "data"),
     Input("klando-trips-store", "data")]
)
def show_trip_details(selected_trip_id, trips_data):
    # Déléguer la création du layout à la fonction existante
    return create_trip_details_layout(selected_trip_id, trips_data)

# Exporter le layout pour l'application principale
layout = get_layout()
