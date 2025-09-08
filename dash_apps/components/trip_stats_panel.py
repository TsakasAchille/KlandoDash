"""
Composant pour le rendu du panneau de statistiques d'un trajet.
Séparé du service de cache pour respecter la séparation des responsabilités.
"""
from dash import html
from dash_apps.components.trip_stats import render_trip_stats


def render_trip_stats_panel(data):
    """
    Génère le panneau complet de statistiques pour un trajet.
    
    Args:
        data: Les données des statistiques du trajet
        
    Returns:
        Un composant Dash contenant les statistiques du trajet
    """
    if not data:
        return html.Div("Aucune statistique disponible pour ce trajet.", className="text-muted")
    
    return render_trip_stats(data)
