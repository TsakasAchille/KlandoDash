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
        trips_data: Données des trajets (fournies par l'API REST)
        
    Returns:
        Un composant Dash à afficher
    """
    # Création du layout des détails de trajet
    
    # Validation des données d'entrée
    if selected_trip_id is None:
        return dbc.Alert(f"Veuillez sélectionner un trajet dans le tableau.", color="info")
    
    # Utiliser directement les données fournies (déjà récupérées par l'API REST)
    if not trips_data:
        return dbc.Alert(f"Trajet avec l'ID {selected_trip_id} non trouvé dans les données.", color="warning")
    
    try:
        # Utiliser directement les données du trajet fournies par l'API REST
        trip_dict = trips_data
        # Trajet trouvé et disponible
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du trajet: {str(e)}")
        return dbc.Alert(f"Erreur lors de la récupération des détails du trajet: {str(e)}", color="danger")
    
    # Récupération des passagers via l'API REST
    trip_id = trip_dict.get("trip_id")
    try:
        # Utiliser l'API REST pour les passagers plutôt que le repository SQL
        from dash_apps.utils.data_schema_rest import get_passengers_for_trip
        passengers_df = get_passengers_for_trip(trip_id)
        if passengers_df is None or (hasattr(passengers_df, 'empty') and passengers_df.empty):
            print("Aucun passager trouvé pour ce trajet")
            passengers_list = []
        else:
            print("Passagers trouvés pour ce trajet")
            passengers_list = passengers_df.to_dict('records') if hasattr(passengers_df, 'to_dict') else passengers_df
    except Exception as e:
        print(f"[WARNING] Erreur lors de la récupération des passagers: {str(e)}")
        passengers_list = []
    
    # Vérifier s'il existe des signalements associés à ce trajet via l'API REST
    signalements_count = 0
    signalements_list = []
    try:
        # Utiliser l'API REST pour les signalements plutôt que le repository SQL
        from dash_apps.utils.data_schema_rest import get_signalements_for_trip
        signalements_data = get_signalements_for_trip(trip_id)
        if signalements_data and isinstance(signalements_data, list):
            signalements_count = len(signalements_data)
            signalements_list = signalements_data
    except Exception as e:
        # En cas d'erreur, on n'empêche pas l'affichage des détails
        print(f"[WARNING] Erreur lors de la récupération des signalements: {str(e)}")
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

    # Ajouter une barre de défilement aux détails du trajet
    trip_details_card = html.Div(
        html.Iframe(
            srcDoc=render_trip_card_html(trip_dict),
            style={
                'width': '100%',
                'height': '600px',
                'border': 'none',
                'overflow': 'auto',  # Ajout de la barre de défilement
                'backgroundColor': 'transparent',
                'borderRadius': '18px',
                'scrollbarWidth': 'thin',  # Barre de défilement fine (Firefox)
                'scrollbarColor': '#4281ec #f4f6f8'  # Couleurs de la barre de défilement (Firefox)
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
        html.Div(signalement_notice, style={"marginBottom": "16px"}) if signalements_count > 0 else None,
        
        # Détails du trajet et informations principales
        dbc.Row([
            # Colonne gauche: Détails du trajet + Conducteur
            dbc.Col([
                # Section Détails du trajet avec titre
                html.Div([
                    section_title("Détails du trajet", "fa-info-circle"),
                    # Juste l'iframe sans div supplémentaire, car trip_details_card est déjà un html.Div
                    html.Iframe(
                        srcDoc=render_trip_card_html(trip_dict),
                        style={
                            'width': '100%',
                            'height': '600px',
                            'border': 'none',
                            'overflow': 'auto',
                            'backgroundColor': 'transparent',
                            'borderRadius': '18px',
                            'scrollbarWidth': 'thin',
                            'scrollbarColor': '#4281ec #f4f6f8'
                        },
                        sandbox='allow-scripts'
                    )
                ], style=MAP_CARD_STYLE),
                
                # Informations du conducteur
                html.Div([
                    section_title("Conducteur du trajet", "fa-user"),
                    trip_driver_component  # Déjà un html.Div, pas besoin d'un conteneur supplémentaire
                ], style=MAP_CARD_STYLE),
            ], md=5, xs=12),
            
            # Colonne droite: Carte + Statistiques
            dbc.Col([
                # Carte du trajet avec titre
                html.Div([
                    section_title("Trajet sur la carte", "fa-map-marker-alt"),
                    # Rendu de la carte
                    trip_map_component if trip_map_component else 
                    html.Div(
                        "Carte non disponible pour ce trajet.", 
                        style={"padding": "30px", "textAlign": "center", "color": "#666"}
                    )
                ], style=MAP_CARD_STYLE),
                
                # Statistiques du trajet avec titre
                html.Div([
                    section_title("Statistiques du trajet", "fa-chart-bar"),
                    # Utiliser directement le composant
                    trip_stats_component
                ], style=MAP_CARD_STYLE),
            ], md=7, xs=12),
        ], className="mb-4"),
        
        # Passagers (sur toute la largeur, en bas)
        dbc.Row([
            dbc.Col([
                html.Div([
                    section_title("Passagers et Réservations", "fa-users"),
                    trip_passengers_card  # Déjà un html.Div, pas besoin d'un conteneur supplémentaire
                ], style=MAP_CARD_STYLE),
            ], md=12)
        ])
    ], fluid=True, className="p-3")
