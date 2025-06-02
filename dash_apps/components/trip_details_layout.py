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
        trips_data: Données des trajets
        
    Returns:
        Un composant Dash à afficher
    """
    # Validation des données d'entrée
    if selected_trip_id is None or trips_data is None or len(trips_data) == 0:
        return dbc.Alert(f"Veuillez sélectionner un trajet dans le tableau.", color="info")
    
    trips_df = pd.DataFrame(trips_data)
    
    # Vérification de la validité des données
    if 'trip_id' not in trips_df.columns:
        return dbc.Alert("Erreur: la colonne 'trip_id' est absente dans les données.", color="danger")
    
    # Gestion du type de l'ID du trajet
    selected_trip_id_type = type(trips_df['trip_id'].iloc[0]) if not trips_df.empty else None
    if selected_trip_id_type and selected_trip_id_type != type(selected_trip_id):
        try:
            if selected_trip_id_type == int:
                selected_trip_id = int(selected_trip_id)
            elif selected_trip_id_type == str:
                selected_trip_id = str(selected_trip_id)
        except:
            pass
    
    # Récupération du trajet sélectionné
    selected_trip = trips_df[trips_df["trip_id"] == selected_trip_id]
    if selected_trip.empty:
        return dbc.Alert(f"Trajet introuvable. ID: {selected_trip_id}", color="danger")
    
    trip_row = selected_trip.iloc[0]
    
    # Récupération des passagers
    trip_id = trip_row.get("trip_id")
    bookings_list = BookingRepository.get_trip_bookings(trip_id)
    if not bookings_list:
        print("Aucun passager trouvé pour ce trajet")
        passengers_list = []
    else:
        print("Passagers trouvés pour ce trajet")
        passenger_ids = [b['user_id'] for b in bookings_list]
        from dash_apps.repositories.user_repository import UserRepository
        passengers_list = UserRepository.get_users_by_ids(passenger_ids)
    
    # Génération des composants
    trip_details_card = html.Div(
        html.Iframe(
            srcDoc=render_trip_card_html(trip_row),
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
    
    trip_stats_component = render_trip_stats(trip_row)
    trip_map_component = render_trip_map(trip_row)
    trip_driver_component = render_trip_driver(trip_row)

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
