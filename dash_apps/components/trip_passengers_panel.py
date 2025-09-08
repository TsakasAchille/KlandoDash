"""
Composant pour le rendu du panneau des passagers d'un trajet.
Séparé du service de cache pour respecter la séparation des responsabilités.
"""
from dash import html
import dash_bootstrap_components as dbc
from dash_apps.components.trip_passengers import render_trip_passengers


def render_trip_passengers_panel(data):
    """
    Génère le panneau complet des passagers pour un trajet.
    
    Args:
        data: Les données des passagers du trajet
        
    Returns:
        Un composant Dash contenant la liste des passagers du trajet
    """
    if not data:
        return html.Div(
            dbc.Alert("Aucun passager pour ce trajet.", color="warning", className="mb-3"),
            style={
                'backgroundColor': 'white',
                'borderRadius': '28px',
                'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
                'padding': '15px',
                'overflow': 'hidden',
                'marginBottom': '20px'
            }
        )
    
    return render_trip_passengers(data)
