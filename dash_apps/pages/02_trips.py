from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

# TODO: Migrer/remplacer les imports Streamlit par des modules Dash natifs ou custom
from src.data_processing.processors.user_processor import UserProcessor
from dash_apps.components.trips_table import render_trips_table
from dash_apps.components.trip_details_layout import create_trip_details_layout

# Layout de la page (exposé pour import via multipage)
layout = dbc.Container([
    dcc.Location(id="trips-url", refresh=False),  # Composant de navigation pour la page trajets
    html.H2("Dashboard utilisateurs et trajets", style={"marginTop": "20px"}),
    dbc.Row([
        dbc.Col([], width=9),
        dbc.Col([
            dbc.Button("🔄 Rafraîchir les données", id="refresh-btn", color="primary", className="mb-2")
        ], width=3)
    ]),
    html.Div(id="refresh-message"),
    dcc.Store(id="users-store"),
    dcc.Store(id="trips-store"),
    dcc.Store(id="selected-trip-id", storage_type="session"),
    html.Div(id="trips-content-area"),  # Changement d'ID pour éviter le conflit
    html.Div(id="trip-details")
], fluid=True)

# --- Callbacks Dash multipage ---

@callback(
    Output("users-store", "data", allow_duplicate=True),
    Output("trips-store", "data", allow_duplicate=True),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call='initial_duplicate'
)
def load_data(n_clicks):
    # TODO: Remplacer get_trip_data par une version Dash compatible si besoin
    users_df = UserProcessor.get_all_users()
    # get_trip_data doit retourner un DataFrame de trajets
    from dash_apps.utils.trip_data import get_trip_data
    trips_df = get_trip_data()
    users_data = users_df.to_dict("records") if users_df is not None else None
    trips_data = trips_df.to_dict("records") if trips_df is not None else None
    return users_data, trips_data

@callback(
    Output("refresh-message", "children", allow_duplicate=True),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_refresh_message(n_clicks):
    return dbc.Alert("Données rafraîchies! Les nouveaux voyages sont maintenant visibles.", color="success", dismissable=True)

@callback(
    Output("trips-content-area", "children", allow_duplicate=True),
    Input("users-store", "data"),
    Input("trips-store", "data"),
    Input("selected-trip-id", "data"),
    prevent_initial_call='initial_duplicate'
)
def update_main_content(users_data, trips_data, selected_trip_id):
    if users_data is None:
        return dbc.Alert("Aucun utilisateur trouvé", color="danger")
    if trips_data is None or len(trips_data) == 0:
        return dbc.Alert("Aucun trajet trouvé", color="danger")
    trips_df = pd.DataFrame(trips_data)
    # Préselection du trajet si selected_trip_id est présent
    preselect_row = []
    if selected_trip_id:
        idx = trips_df.index[trips_df['trip_id'] == selected_trip_id].tolist()
        if idx:
            preselect_row = [idx[0]]
    table = render_trips_table(trips_df, selected_rows=preselect_row)
    instruction = html.P("Sélectionnez un trajet dans le tableau pour voir les détails.")
    # Renommer le composant pour éviter les conflits de callbacks
    details_div = html.Div(id="trips-page-details")
    return html.Div([instruction, table, html.Hr(), details_div])

@callback(
    Output("selected-trip-id", "data", allow_duplicate=True),
    Input("trips-table", "selected_rows"),
    State("trips-store", "data"),
    prevent_initial_call='initial_duplicate'
)
def update_selected_trip_id(selected_rows, trips_data):
    if selected_rows and trips_data:
        trips_df = pd.DataFrame(trips_data)
        selected_trip_id = trips_df.iloc[selected_rows[0]]['trip_id']
        return selected_trip_id
    return None

@callback(
    Output("trips-page-details", "children", allow_duplicate=True),
    Input("selected-trip-id", "data"),
    Input("trips-store", "data"),
    prevent_initial_call='initial_duplicate'
)
def show_trip_details(selected_trip_id, trips_data):
    # Debug logs
    print(f"[DEBUG] selected_trip_id: {selected_trip_id}")
    print(f"[DEBUG] trips_data existe: {trips_data is not None}")
    
    # Délègue la création du layout à une fonction dédiée avec style Klando
    return create_trip_details_layout(selected_trip_id, trips_data)

if __name__ == "__main__":
    app.run(debug=True)
