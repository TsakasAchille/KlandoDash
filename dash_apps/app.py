import sys
import os

# Ajouter le répertoire racine du projet au PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Multipage support (Dash >=2.0)
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
server = app.server

# Layout de base (navbar + contenu)
app.layout = dbc.Container([
    dbc.Row([
        # Sidebar navigation
        dbc.Col([
            html.Div([
                html.H3("KlandoDash", className="mt-4 mb-4", style={"color": "#730200", "fontFamily": "Gliker, Arial, sans-serif"}),
                dbc.Nav([
                    dbc.NavLink("Utilisateurs", href="/users", active="exact", id="nav-users", className="mb-2"),
                    dbc.NavLink("Trajets", href="/trips", active="exact", id="nav-trips", className="mb-2"),
                ], vertical=True, pills=True, className="sidebar-nav"),
            ], style={"position": "fixed", "top": 0, "left": 0, "height": "100vh", "width": "220px", "background": "#f8f9fa", "padding": "24px 12px 0 12px", "borderRight": "2px solid #eee", "zIndex": 1000})
        ], width=2, style={"padding": 0, "maxWidth": "220px"}),
        # Main content
        dbc.Col([
            dcc.Location(id="url"),
            html.Div(id="page-content", style={"marginLeft": "12px", "marginRight": "12px"})
        ], width=10)
    ], className="g-0")
], fluid=True)

# Import dynamique des pages
from dash_apps.pages import trips_page
import importlib
users_page = importlib.import_module('dash_apps.pages.01_users')

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname in ["/", "/trips"]:
        return trips_page
    if pathname == "/users":
        return users_page.layout
    return dbc.Alert("Page non trouvée", color="danger")

if __name__ == "__main__":
    app.run(debug=True)
