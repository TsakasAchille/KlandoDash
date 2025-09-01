from dash import html
import dash_bootstrap_components as dbc
import jinja2
import os

def render_trip_stats_html(trip_data):
    """
    Génère le HTML pour les statistiques du trajet en utilisant le template Jinja2.
    
    Args:
        trip_data: dictionnaire contenant les informations du trajet
    Returns:
        HTML généré à partir du template
    """
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('trip_stats_template.jinja2')
    return template.render(trip=trip_data)


def render_trip_stats(data):
    """
    Affiche les stats principales du trajet (financier, occupation, etc.) avec un design moderne.
    
    Args:
        data: dictionnaire contenant trip_id et stats
    """
    if not data or not data.get('stats'):
        return html.Div("Aucune statistique disponible", className="text-muted")
        
    # Récupérer les stats depuis les données
    trip_dict = data.get('stats', {})
    
    # Génération du HTML pour les statistiques du trajet en utilisant Jinja
    stats_html = render_trip_stats_html(trip_dict)
    
    # Création du composant Dash à partir du HTML généré
    return html.Div(
        html.Iframe(
            srcDoc=stats_html,
            style={
                'width': '100%',
                'height': '400px',
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            sandbox='allow-scripts',
        ),
        style={
            'backgroundColor': 'white',
            'borderRadius': '28px',
            'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
            'padding': '15px',
            'overflow': 'hidden',
            'marginBottom': '20px'
        }
    )
