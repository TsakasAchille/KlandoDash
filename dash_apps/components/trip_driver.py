from dash import html
import dash_bootstrap_components as dbc
from jinja2 import Environment, FileSystemLoader
import os
from dash_apps.repositories.repository_factory import RepositoryFactory

# Initialisation de Jinja2 pour le template du conducteur du trajet
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir))
trip_driver_template = env.get_template("trip_driver_template.jinja2")


def render_trip_driver(trip):
    """
    Affiche les informations du conducteur d'un trajet en utilisant un template Jinja2.
    
    Args:
        trip: Dictionnaire de données du trajet
    """
    if trip is None:
        return None
        
    driver_id = trip.get('driver_id')
    if not driver_id:
        # Rendu du template HTML avec Jinja2 sans données de conducteur
        html_content = trip_driver_template.render(driver=None)
        
        # Afficher le template dans un iframe
        return html.Div(
            html.Iframe(
                srcDoc=html_content,
                style={
                    'width': '100%',
                    'height': '250px',  # Hauteur réduite pour s'adapter au contenu
                    'border': 'none',
                    'overflow': 'hidden',
                    'backgroundColor': 'transparent',
                    'borderRadius': '18px'
                },
                id='driver-iframe',
                sandbox='allow-scripts allow-top-navigation',
            ),
            className="klando-card klando-card-minimal"
        )
    
    # Récupération des informations du conducteur via REST API
    driver_data = None
    try:
        user_repository = RepositoryFactory.get_user_repository()
        driver_data = user_repository.get_user(driver_id)
    except Exception as e:
        import traceback
        print(f"Erreur lors de la récupération des informations du conducteur: {str(e)}")
        print(traceback.format_exc())
        driver_data = None
    
    # Rendu du template HTML avec Jinja2
    html_content = trip_driver_template.render(driver=driver_data)
    
    # Afficher le template dans un iframe
    return html.Div(
        html.Iframe(
            srcDoc=html_content,
            style={
                'width': '100%',
                'height': '350px',  # Hauteur réduite pour s'adapter au contenu
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            id='driver-iframe',
            sandbox='allow-scripts allow-top-navigation',
        ),
        className="klando-card klando-card-minimal"
    )
