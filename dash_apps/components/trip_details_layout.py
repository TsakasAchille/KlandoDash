from dash import html
import dash_bootstrap_components as dbc

from dash_apps.components.trip_stats import render_trip_stats
from dash_apps.components.trip_map import render_trip_map
from dash_apps.components.trip_driver import render_trip_driver
from dash_apps.components.trip_passengers import render_trip_passengers
from dash_apps.components.trip_details import render_trip_details
from dash_apps.components.signalement_notice import render_signalement_notice
from dash_apps.services.trip_data_service import TripDataService





COLUMN_STYLE = {
    'padding': '12px'  # Padding uniforme pour les colonnes
}

# Espacement entre les composants
SPACING_STYLE = {"marginBottom": "16px"}

def create_trip_details_layout(selected_trip_id, trips_data):
    """
    Orchestrateur principal pour le layout des détails d'un trajet.
    Récupère les données via le service et orchestre les composants.
    
    Args:
        selected_trip_id: ID du trajet sélectionné
        trips_data: Données du trajet principal (fournies par l'API REST)
        
    Returns:
        Un composant Dash à afficher
    """
    # Validation des données d'entrée
    if selected_trip_id is None:
        return dbc.Alert("Veuillez sélectionner un trajet dans le tableau.", color="info")
    
    # Récupération de toutes les données via le service
    try:
        trip_dict, passengers_list, signalements_list, signalements_count = TripDataService.get_trip_complete_data(
            selected_trip_id, trips_data
        )
    except ValueError as e:
        return dbc.Alert(str(e), color="warning")
    except Exception as e:
        return dbc.Alert(f"Erreur lors de la récupération des détails du trajet: {str(e)}", color="danger")

    # Génération de la notice de signalement
    signalement_notice = render_signalement_notice(signalements_list, signalements_count)
    
    # Génération des composants individuels
    trip_details_component = render_trip_details(trip_dict)
    trip_stats_component = render_trip_stats(trip_dict)
    trip_map_component = render_trip_map(trip_dict)
    trip_driver_component = render_trip_driver(trip_dict)
    trip_passengers_component = render_trip_passengers({
        'trip_id': trip_dict.get('trip_id'),
        'passengers': passengers_list
    })


   
    # Styles de carte pour uniformisation visuelle
    MAP_CARD_STYLE = {
        'backgroundColor': 'white',
        'borderRadius': '28px',
        'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
        'padding': '15px',
        'overflow': 'hidden',
        'marginBottom': '16px'
    }
    
    # Style des titres de section uniformisé
    TITLE_STYLE = {
        "fontWeight": "600",
        "fontSize": "18px",
        "color": "#3a4654",
        "margin": "0 0 15px 0",
        "display": "flex",
        "alignItems": "center"
    }
    
    # Composant titre avec icône pour uniformité
    def section_title(title, icon):
        return html.H5([
            html.I(className=f"fas {icon} mr-2", style={"marginRight": "10px", "color": "#4281ec"}),
            title
        ], style=TITLE_STYLE)
    
    # Construction du layout réorganisé pour une meilleure cohérence visuelle
    return dbc.Container([
        # Signalements en haut si présents (commun à tout le conteneur)
        signalement_notice,

        # Ligne 1: Détails (1/3) | Carte (2/3)
        dbc.Row([
            dbc.Col([
                html.Div([
                    section_title("Détails du trajet", "fa-info-circle"),
                    trip_details_component if trip_details_component else html.Div(
                        "Aucun détail disponible pour ce trajet.",
                        style={"padding": "30px", "textAlign": "center", "color": "#666"}
                    )
                ], style=MAP_CARD_STYLE)
            ], md=4, xs=12),
            dbc.Col([
                html.Div([
                    section_title("Trajet sur la carte", "fa-map-marker-alt"),
                    trip_map_component if trip_map_component else html.Div(
                        "Carte non disponible pour ce trajet.",
                        style={"padding": "30px", "textAlign": "center", "color": "#666"}
                    )
                ], style=MAP_CARD_STYLE)
            ], md=8, xs=12),
        ], className="mb-4"),

        # Ligne 2: Statistiques (2/3) | Conducteur (1/3)
        dbc.Row([
            dbc.Col([
                html.Div([
                    section_title("Statistiques du trajet", "fa-chart-bar"),
                    trip_stats_component
                ], style=MAP_CARD_STYLE)
            ], md=8, xs=12),
            dbc.Col([
                html.Div([
                    section_title("Conducteur du trajet", "fa-user"),
                    trip_driver_component
                ], style=MAP_CARD_STYLE)
            ], md=4, xs=12),
        ], className="mb-4"),

        # Ligne 3: Passagers (pleine largeur)
        dbc.Row([
            dbc.Col([
                html.Div([
                    section_title("Passagers et Réservations", "fa-users"),
                    trip_passengers_component
                ], style=MAP_CARD_STYLE)
            ], md=12)
        ])
    ], fluid=True, className="p-3")
