"""
Composant pour l'affichage des notices de signalement.
"""
from dash import html
import dash_bootstrap_components as dbc
from typing import List, Dict


def render_signalement_notice(signalements_list: List[Dict], signalements_count: int) -> html.Div:
    """
    Génère la notice et les boutons pour accéder aux signalements.
    
    Args:
        signalements_list: Liste des signalements
        signalements_count: Nombre de signalements
        
    Returns:
        Composant Dash pour la notice de signalement
    """
    if not signalements_list or signalements_count == 0:
        return None
    
    # Construction des boutons de signalement
    signalement_buttons = []
    for idx, t in enumerate(signalements_list, start=1):
        label = f"Voir signalement {idx}"
        href = f"/support?ticket_id={t.get('ticket_id', '')}"
        signalement_buttons.append(
            dbc.Button(
                label, 
                color="warning", 
                outline=True, 
                size="sm", 
                className="me-2 mb-2", 
                href=href
            )
        )
    
    # Notice principale
    notice_text = f"⚠️ Ce trajet a {signalements_count} signalement{'s' if signalements_count > 1 else ''} associé{'s' if signalements_count > 1 else ''}."
    
    return html.Div([
        dbc.Alert([
            html.P(notice_text, className="mb-2"),
            html.Div(signalement_buttons, className="d-flex flex-wrap")
        ], color="warning", className="mb-3")
    ])
