import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
import pandas as pd
from dash import dash_table
from dash_apps.components.users_table import render_users_table

layout = dbc.Container([
    html.H2("Dashboard utilisateurs", style={"marginTop": "20px"}),
    dbc.Row([
        dbc.Col([], width=9),
        dbc.Col([
            dbc.Button("🔄 Rafraîchir les données", id="refresh-users-btn", color="primary", className="mb-2")
        ], width=3)
    ]),
    html.Div(id="refresh-users-message"),
    dcc.Store(id="users-page-store"),
    dbc.Row([
        dbc.Col([
            # DataTable vide par défaut pour que l'id existe toujours
            html.Div(
                dash_table.DataTable(
                    id="users-table",
                    columns=[{"name": c, "id": c} for c in ["uid", "name", "email", "phone", "role", "created_at"]],
                    data=[],
                    row_selectable="single",
                    selected_rows=[],
                ), id="main-users-content"
            )
        ], width=8),
        dbc.Col([
            html.Div(id="user-details-panel")
        ], width=4)
    ])
], fluid=True)

@callback(
    Output("users-page-store", "data"),
    Input("refresh-users-btn", "n_clicks"),
    prevent_initial_call=False
)
def load_users_data(n_clicks):
    from src.data_processing.processors.user_processor import UserProcessor
    users_df = UserProcessor.get_all_users()
    users_data = users_df.to_dict("records") if users_df is not None else None
    return users_data

@callback(
    Output("refresh-users-message", "children"),
    Input("refresh-users-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_refresh_users_message(n_clicks):
    return dbc.Alert("Données utilisateurs rafraîchies!", color="success", dismissable=True)

@callback(
    Output("main-users-content", "children"),
    Output("user-details-panel", "children"),
    Input("users-page-store", "data"),
    Input("users-table", "selected_rows"),
)
def show_users_content(users_data, selected_rows):
    if not users_data:
        # Affiche un DataTable vide pour que l'Input existe toujours
        empty_df = pd.DataFrame([{"uid": "", "name": "", "email": "", "phone": "", "role": "", "created_at": ""}])
        table = render_users_table(empty_df)
        return table, None
    users_df = pd.DataFrame(users_data)
    table = render_users_table(users_df)
    # Affichage du détail utilisateur si une ligne est sélectionnée
    details = None
    if selected_rows and len(selected_rows) > 0:
        user = users_df.iloc[selected_rows[0]]
        details = dbc.Card([
            dbc.CardHeader(f"Détail utilisateur : {user.get('name', user.get('uid', ''))}"),
            dbc.CardBody([
                html.Ul([
                    html.Li(f"ID : {user.get('uid', '')}"),
                    html.Li(f"Nom : {user.get('name', '')}"),
                    html.Li(f"Email : {user.get('email', '')}"),
                    html.Li(f"Téléphone : {user.get('phone', '')}"),
                    html.Li(f"Rôle : {user.get('role', '')}"),
                    html.Li(f"Date création : {user.get('created_at', '')}"),
                ])
            ])
        ], className="klando-card")
    return table, details
