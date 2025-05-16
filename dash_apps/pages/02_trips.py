from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

# TODO: Migrer/remplacer les imports Streamlit par des modules Dash natifs ou custom
from src.data_processing.processors.user_processor import UserProcessor
from dash_apps.components.trips_table import render_trips_table
from dash_apps.components.trip_map import render_trip_map
from dash_apps.components.trip_stats import render_trip_stats
from dash_apps.components.trip_passengers import render_trip_passengers
from dash_apps.utils.db_utils import get_trip_passengers
from src.core.database import get_session, User
from dash_apps.components.trip_details import trip_details_layout

# Layout de la page (exposé pour import via multipage)
layout = dbc.Container([
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
    dcc.Store(id="selected-trip-id"),
    html.Div(id="main-content"),
    html.Div(id="trip-details")
], fluid=True)

# --- Callbacks Dash multipage ---

@callback(
    Output("users-store", "data"),
    Output("trips-store", "data"),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=False
)
def load_data(n_clicks):
    # TODO: Remplacer get_trip_data par une version Dash compatible si besoin
    users_df = UserProcessor.get_all_users()
    # get_trip_data doit retourner un DataFrame de trajets
    from src.streamlit_apps.pages.components.trips import get_trip_data  # TEMPORAIRE
    trips_df = get_trip_data()
    users_data = users_df.to_dict("records") if users_df is not None else None
    trips_data = trips_df.to_dict("records") if trips_df is not None else None
    return users_data, trips_data

@callback(
    Output("refresh-message", "children"),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_refresh_message(n_clicks):
    return dbc.Alert("Données rafraîchies! Les nouveaux voyages sont maintenant visibles.", color="success", dismissable=True)

@callback(
    Output("main-content", "children"),
    Input("users-store", "data"),
    Input("trips-store", "data"),
)
def update_main_content(users_data, trips_data):
    if users_data is None:
        return dbc.Alert("Aucun utilisateur trouvé", color="danger")
    if trips_data is None or len(trips_data) == 0:
        return dbc.Alert("Aucun trajet trouvé", color="danger")
    trips_df = pd.DataFrame(trips_data)
    table = render_trips_table(trips_df)
    instruction = html.P("Sélectionnez un trajet dans le tableau pour voir les détails.")
    details_div = html.Div(id="trip-details")
    return html.Div([instruction, table, html.Hr(), details_div])

@callback(
    Output("selected-trip-id", "data"),
    Input("trips-table", "selected_rows"),
    State("trips-store", "data")
)
def update_selected_trip_id(selected_rows, trips_data):
    if selected_rows and trips_data:
        trips_df = pd.DataFrame(trips_data)
        selected_trip_id = trips_df.iloc[selected_rows[0]]['trip_id']
        return selected_trip_id
    return None

@callback(
    Output("trip-details", "children"),
    Input("selected-trip-id", "data"),
    State("trips-store", "data")
)

def show_trip_details(selected_trip_id, trips_data):
    if not selected_trip_id or not trips_data:
        return dbc.Alert("Aucun trajet sélectionné.", color="warning")
    trips_df = pd.DataFrame(trips_data)
    selected_trip = trips_df[trips_df["trip_id"] == selected_trip_id]
    if selected_trip.empty:
        return dbc.Alert("Trajet introuvable.", color="danger")
    return trip_details_layout(selected_trip.iloc[0], trips_data)

if __name__ == "__main__":
    app.run(debug=True)
