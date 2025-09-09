from dash import html
import dash_bootstrap_components as dbc
import jinja2
import os

def render_trip_passengers_html(trip_data):
    """
    Génère le HTML pour les passagers du trajet en utilisant le template Jinja2.
    
    Args:
        trip_data: dictionnaire contenant les informations du trajet et des passagers
    Returns:
        HTML généré à partir du template
    """
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('trip_passengers_template.jinja2')
    return template.render(trip=trip_data)


def render_trip_passengers(data):
    """
    Affiche les passagers du trajet avec un design moderne.
    
    Args:
        data: dictionnaire contenant trip_id et passengers (DataFrame ou list)
    """
    passengers = data.get('passengers') if data else None
    if not data or passengers is None:
        return html.Div("Aucun passager pour ce trajet", className="text-muted")
    
    # Check if DataFrame is empty
    if hasattr(passengers, 'empty') and passengers.empty:
        return html.Div("Aucun passager pour ce trajet", className="text-muted")
    
    # Convertir DataFrame en liste de dictionnaires si nécessaire
    if hasattr(passengers, 'to_dict'):
        passengers_list = passengers.to_dict('records')
    elif isinstance(passengers, list):
        passengers_list = passengers
    else:
        passengers_list = []
    
    # Préparer les données pour le template
    trip_data = {
        'trip_id': data.get('trip_id'),
        'passengers': passengers_list,
        'passenger_count': len(passengers_list)
    }
    
    # Génération du HTML pour les passagers en utilisant Jinja
    passengers_html = render_trip_passengers_html(trip_data)
    
    # Création du composant Dash à partir du HTML généré
    return html.Div(
        html.Iframe(
            srcDoc=passengers_html,
            style={
                'width': '100%',
                'height': '500px',
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            sandbox='allow-scripts',
        ),
        className="klando-card klando-card-minimal"
    )
