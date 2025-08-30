from dash import html
import dash_bootstrap_components as dbc
import pandas as pd

from dash_apps.components.trip_stats import render_trip_stats
from dash_apps.components.trip_map import render_trip_map
from dash_apps.components.trip_driver import render_trip_driver
from dash_apps.repositories.booking_repository import BookingRepository



def render_trip_card_html(trip_data, passengers=None):
    import jinja2, os
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('trip_details_template.jinja2')
    return template.render(trip=trip_data, passengers=passengers or [])


# Styles globaux pour une cohérence visuelle
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '28px',
    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
    'padding': '15px',
    'overflow': 'hidden',
    'marginBottom': '16px'
}

COLUMN_STYLE = {
    'padding': '12px'  # Padding uniforme pour les colonnes
}

# Espacement entre les composants
SPACING_STYLE = {"marginBottom": "16px"}

def create_trip_details_layout(selected_trip_id, trips_data):
    """
    Crée le layout des détails d'un trajet sélectionné.
    
    Args:
        selected_trip_id: ID du trajet sélectionné
        trips_data: Données des trajets (peut être None)
        
    Returns:
        Un composant Dash à afficher
    """
    print(f"\n[DEBUG] create_trip_details_layout")
    print(f"selected_trip_id {selected_trip_id}")
    print(f"trips_data {trips_data}")
    
    # Validation des données d'entrée
    if selected_trip_id is None:
        return dbc.Alert(f"Veuillez sélectionner un trajet dans le tableau.", color="info")
    
    # Récupérer les données du trajet depuis le repository
    from dash_apps.repositories.trip_repository import TripRepository
    
    try:
        trip = TripRepository.get_trip_by_id(selected_trip_id)
        if not trip:
            return dbc.Alert(f"Trajet avec l'ID {selected_trip_id} non trouvé.", color="warning")
        
        # Convertir le schéma Pydantic en dictionnaire
        trip_dict = trip.model_dump()
        print(f"[DEBUG] Trajet trouvé: {trip_dict}")
        
    except Exception as e:
        print(f"[ERROR] Erreur lors de la récupération du trajet: {str(e)}")
        return dbc.Alert(f"Erreur lors de la récupération des détails du trajet: {str(e)}", color="danger")
    
    # Récupération des passagers
    trip_id = trip_dict.get("trip_id")
    try:
        from dash_apps.repositories.booking_repository import BookingRepository
        bookings_list = BookingRepository.get_trip_bookings(trip_id)
        if not bookings_list:
            print("Aucun passager trouvé pour ce trajet")
            passengers_list = []
        else:
            print("Passagers trouvés pour ce trajet")
            passenger_ids = [b['user_id'] for b in bookings_list]
            from dash_apps.repositories.user_repository import UserRepository
            passengers_list = UserRepository.get_users_by_ids(passenger_ids)
    except Exception as e:
        print(f"[WARNING] Erreur lors de la récupération des passagers: {str(e)}")
        passengers_list = []
    
    # Vérifier s'il existe des signalements associés à ce trajet
    signalements_count = 0
    signalements_list = []
    try:
        from dash_apps.repositories.support_ticket_repository import SupportTicketRepository
        signalements_count = SupportTicketRepository.get_trip_signalements_count(trip_id)
        # Charger la liste détaillée pour les boutons de navigation
        if signalements_count > 0:
            signalements_list = SupportTicketRepository.list_signalements_for_trip(trip_id)
    except Exception as e:
        # En cas d'erreur, on n'empêche pas l'affichage des détails
        signalements_count = 0
        signalements_list = []

    # Génération des composants
    # Notice + boutons pour accéder aux signalements sur la page Support
    signalement_buttons = []
    if signalements_list:
        for idx, t in enumerate(signalements_list, start=1):
            label = f"Voir signalement {idx}"
            href = f"/support?ticket_id={t.ticket_id}"
            signalement_buttons.append(
                dbc.Button(label, color="warning", outline=True, size="sm", className="me-2 mb-2", href=href)
            )

    signalement_notice = (
        html.Div([
            dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Ce trajet a {signalements_count} signalement(s)."
                ],
                color="warning",
                className="mb-2",
            ),
            html.Div(signalement_buttons)
        ]) if signalements_count > 0 else html.Div()
    )

    trip_details_card = html.Div(
        html.Iframe(
            srcDoc=render_trip_card_html(trip_dict),
            style={
                'width': '100%',
                'height': '600px',
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            sandbox='allow-scripts',
        ),
        style=CARD_STYLE
    )
    
    trip_stats_component = render_trip_stats(trip_dict)
    trip_map_component = render_trip_map(trip_dict)
    trip_driver_component = render_trip_driver(trip_dict)

    # Nouveau composant : passagers via template avancé
    def render_trip_passengers_html(passengers):
        import jinja2, os
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template('trip_passengers_template.jinja2')
        return template.render(passengers=passengers or [])

    trip_passengers_card = html.Div(
        html.Iframe(
            srcDoc=render_trip_passengers_html(passengers_list),
            style={
                'width': '100%',
                'height': '650px',
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            sandbox='allow-scripts allow-top-navigation-by-user-activation',
        ),
        style=CARD_STYLE
    )
    
    # Construction du layout en réutilisant les composants directement
    return dbc.Row([
        dbc.Col([
            # Détails du trajet avec espacement
            html.Div(signalement_notice, style={"marginBottom": "8px"}),
            html.Div(trip_details_card, style=SPACING_STYLE),
            # Conducteur du trajet
            html.Div(trip_driver_component, style=SPACING_STYLE),
            # Statistiques du trajet
            trip_stats_component,
        ], md=4, xs=12, style=COLUMN_STYLE),
        dbc.Col([
            # Carte du trajet avec espacement
            html.Div(
                trip_map_component if trip_map_component else 
                html.Div(
                    "Carte non disponible pour ce trajet.", 
                    style={"padding": "30px", "textAlign": "center", "color": "#666", 
                          "backgroundColor": "white", "borderRadius": "28px", 
                          "boxShadow": "rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px",
                          "padding": "15px"}
                ),
                style=SPACING_STYLE
            ),
            # Liste des passagers (nouveau template)
            html.Div(trip_passengers_card, style=SPACING_STYLE)
        ], md=8, xs=12, style=COLUMN_STYLE)
    ], className="align-items-stretch", style={"margin": "8px 0"})
