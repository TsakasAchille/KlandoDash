import os
import jinja2
from dash import html

# Configurer l'environnement Jinja2
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

def render_template_with_iframe(template_name, context=None, height=None, width=None, className=None, style=None):
    """
    Rend un template Jinja2 et l'intègre dans un iframe Dash.
    
    Args:
        template_name: Nom du template à rendre
        context: Dictionnaire de contexte à passer au template
        height: Hauteur de l'iframe (optionnel)
        width: Largeur de l'iframe (optionnel)
        className: Classes CSS pour l'iframe (optionnel)
        style: Style CSS pour l'iframe (optionnel)
    
    Returns:
        Un composant Dash iframe contenant le template rendu
    """
    if context is None:
        context = {}
    
    # Rendre le template
    template = env.get_template(template_name)
    rendered_html = template.render(**context)
    
    # Paramètres de l'iframe
    iframe_style = style or {}
    if height:
        iframe_style.update({"height": height})
    if width:
        iframe_style.update({"width": width})
    
    # Autres paramètres par défaut pour l'iframe
    iframe_style.update({
        "border": "none",
        "overflow": "hidden"
    })
    
    # Créer l'iframe avec le HTML rendu
    return html.Iframe(
        srcDoc=rendered_html,
        style=iframe_style,
        className=className,
        sandbox='allow-scripts allow-top-navigation'
    )
