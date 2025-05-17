import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output
import pandas as pd
from dash import dash_table
from dash_apps.components.users_table import render_users_table
from dash_apps.components.user_details import render_user_details

layout = dbc.Container([
    dcc.Location(id="users-url", refresh=False),
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
    Output("users-table", "selected_rows"),
    Input("users-page-store", "data"),
    Input("users-table", "selected_rows"),
    Input("users-url", "search"),
)
def show_users_content(users_data, selected_rows, url_search):
    import urllib.parse
    preselect_row = None
    if not users_data:
        # Affiche un DataTable vide pour que l'Input existe toujours
        empty_df = pd.DataFrame([{"uid": "", "name": "", "email": "", "phone": "", "role": "", "created_at": ""}])
        table = render_users_table(empty_df, selected_rows=selected_rows)
        return table, None, selected_rows
    users_df = pd.DataFrame(users_data)
    # Recherche d'un paramètre uid dans l'URL
    uid_from_url = None
    if url_search:
        params = urllib.parse.parse_qs(url_search.lstrip('?'))
        uid_list = params.get('uid')
        if uid_list:
            uid_from_url = uid_list[0]
    # Si un uid est présent dans l'URL, présélectionner la ligne
    if uid_from_url:
        try:
            idx = users_df.index[users_df['uid'] == uid_from_url].tolist()
            if idx:
                preselect_row = [idx[0]]
        except Exception:
            preselect_row = selected_rows or []
    # Si pas de sélection, garder la sélection courante
    if preselect_row is None:
        preselect_row = selected_rows or []
    table = render_users_table(users_df, selected_rows=preselect_row)
    # Affichage du détail utilisateur si une ligne est sélectionnée
    details = None
    if preselect_row and len(preselect_row) > 0:
        user = users_df.iloc[preselect_row[0]]
        details = render_user_details(user)
    return table, details, preselect_row
