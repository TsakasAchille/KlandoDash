"""
Layout pour l'affichage des passagers d'un trajet.
"""
import dash_bootstrap_components as dbc
from dash import html
from typing import Dict, Any, List


class TripPassengersLayout:
    """Générateur de layout pour les passagers d'un trajet."""
    
    @staticmethod
    def render_empty_state() -> dbc.Card:
        """Affichage quand il n'y a pas de passagers."""
        return dbc.Card([
            dbc.CardBody([
                html.Div([
                    html.I(className="fas fa-users fa-3x text-muted mb-3"),
                    html.H5("Aucun passager", className="text-muted"),
                    html.P("Ce trajet n'a pas encore de passagers.", className="text-muted")
                ], className="text-center py-4")
            ])
        ], className="border-0")
    
    @staticmethod
    def render_passenger_card(passenger: Dict[str, Any]) -> dbc.Col:
        """Affiche une carte pour un passager."""
        # Photo de profil ou avatar par défaut
        if passenger.get('photo_url'):
            avatar = html.Img(
                src=passenger['photo_url'],
                className="rounded-circle",
                style={"width": "50px", "height": "50px", "object-fit": "cover"}
            )
        else:
            avatar = html.Div([
                html.I(className="fas fa-user fa-2x text-muted")
            ], className="rounded-circle bg-light d-flex align-items-center justify-content-center",
               style={"width": "50px", "height": "50px"})
        
        # Badge de statut
        status_color = {
            "CONFIRMED": "success",
            "PENDING": "warning", 
            "CANCELLED": "danger",
            "COMPLETED": "info"
        }.get(passenger.get('status', 'PENDING'), 'secondary')
        
        status_badge = dbc.Badge(
            passenger.get('status', 'PENDING'),
            color=status_color,
            className="ms-2"
        )
        
        return dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([avatar], width="auto"),
                        dbc.Col([
                            html.H6([
                                passenger.get('name', 'Passager anonyme'),
                                status_badge
                            ], className="mb-1"),
                            html.P([
                                html.I(className="fas fa-chair me-1"),
                                passenger.get('seats', '1 place')
                            ], className="text-muted mb-1 small"),
                            html.P([
                                html.I(className="fas fa-phone me-1"),
                                passenger.get('phone', 'Non renseigné')
                            ], className="text-muted mb-1 small"),
                            html.P([
                                html.I(className="fas fa-star me-1"),
                                passenger.get('rating', 'Pas encore noté')
                            ], className="text-muted mb-0 small")
                        ])
                    ], align="center")
                ])
            ], className="h-100 shadow-sm")
        ], md=6, lg=4, className="mb-3")
    
    @staticmethod
    def render_summary_header(summary: Dict[str, Any]) -> dbc.Alert:
        """Affiche le résumé des passagers."""
        total_passengers = summary.get('total_passengers', 0)
        total_seats = summary.get('total_seats', 0)
        
        if total_passengers == 0:
            return dbc.Alert([
                html.I(className="fas fa-info-circle me-2"),
                "Aucun passager pour ce trajet"
            ], color="info", className="mb-3")
        
        return dbc.Alert([
            html.I(className="fas fa-users me-2"),
            f"{total_passengers} passager{'s' if total_passengers > 1 else ''} - ",
            f"{total_seats} place{'s' if total_seats > 1 else ''} réservée{'s' if total_seats > 1 else ''}"
        ], color="success", className="mb-3")
    
    @staticmethod
    def render_passengers_grid(passengers_list: List[Dict[str, Any]]) -> dbc.Row:
        """Affiche la grille des passagers."""
        if not passengers_list:
            return dbc.Row([
                dbc.Col([
                    TripPassengersLayout.render_empty_state()
                ])
            ])
        
        passenger_cards = []
        for passenger in passengers_list:
            card = TripPassengersLayout.render_passenger_card(passenger)
            passenger_cards.append(card)
        
        return dbc.Row(passenger_cards)
    
    @staticmethod
    def render_complete_layout(summary: Dict[str, Any]) -> html.Div:
        """Affiche le layout complet des passagers."""
        passengers_list = summary.get('passengers_list', [])
        
        return html.Div([
            # Résumé
            TripPassengersLayout.render_summary_header(summary),
            
            # Grille des passagers
            TripPassengersLayout.render_passengers_grid(passengers_list)
        ])
    
    @staticmethod
    def render_error_state(error_message: str = None) -> dbc.Alert:
        """Affichage en cas d'erreur."""
        message = error_message or "Erreur lors du chargement des passagers"
        return dbc.Alert([
            html.I(className="fas fa-exclamation-triangle me-2"),
            message
        ], color="danger")
    
    @staticmethod
    def render_loading_state() -> html.Div:
        """Affichage pendant le chargement."""
        return html.Div([
            dbc.Spinner([
                html.Div([
                    html.I(className="fas fa-users fa-2x text-muted mb-2"),
                    html.P("Chargement des passagers...", className="text-muted")
                ], className="text-center py-4")
            ])
        ])
