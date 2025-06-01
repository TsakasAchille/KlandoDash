from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from jinja2 import Environment, FileSystemLoader
import os
import dash

# Initialisation de Jinja2 pour le template de passagers
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir))
bookings_template = env.get_template("passengers_template.jinja2")

# Affiche la liste des passagers/réservations d'un trajet
def render_bookings(bookings):
    """
    Affiche la liste des réservations (déjà enrichie, issue de la base SQL ou d'une liste).
    Paramètres :
        bookings : list[dict] | None
    """
    if bookings is None:
        bookings = []
        
    # Rendu du template HTML avec Jinja2
    html_content = bookings_template.render(
        bookings=bookings
    )
    
    # Utiliser la même technique que pour trip_map et trip_details
    return html.Div(
        html.Iframe(
            srcDoc=html_content,
            style={
                'width': '100%',
                'height': '420px',
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            # Permettre la navigation vers le top (fenêtre parente)
            sandbox='allow-scripts allow-top-navigation',
        ),
        style={
            'backgroundColor': 'white',
            'borderRadius': '28px',
            'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
            'padding': '8px',
            'overflow': 'hidden',
            'marginBottom': '0',
            'maxWidth': '95%',
            'margin': 'auto'
        }
    )

# La redirection est désormais gérée directement via les liens HTML avec target="_top"

