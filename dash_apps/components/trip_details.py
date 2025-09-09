from dash import html
import jinja2
import os


def render_trip_details_html(trip_data, passengers=None):
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    template_loader = jinja2.FileSystemLoader(searchpath=templates_dir)
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template('trip_details_template.jinja2')
    return template.render(trip=trip_data, passengers=passengers or [])


def render_trip_details(trip_data, height='400px'):
    """
    Render the trip details card using the Jinja2 template inside an iframe.
    Styling of the card is handled by assets CSS classes.
    """
    html_doc = render_trip_details_html(trip_data)
    return html.Div(
        html.Iframe(
            srcDoc=html_doc,
            style={
                'width': '100%',
                'height': height,
                'border': 'none',
                'overflow': 'auto',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            sandbox='allow-scripts'
        ),
        className="klando-card klando-card-minimal"
    )
