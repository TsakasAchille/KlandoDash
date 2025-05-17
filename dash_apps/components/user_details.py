from dash import html
import dash_bootstrap_components as dbc
from dash_apps.components.user_profile import render_user_profile
from dash_apps.components.user_stats import render_user_stats

def render_user_details(user):
    if user is None:
        return None
    return html.Div([
        render_user_profile(user)
    ])
