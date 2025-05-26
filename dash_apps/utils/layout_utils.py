from flask import render_template
from dash import html
from flask_login import current_user

def render_main_layout(content_html, active_page='', extra_head='', extra_scripts=''):
    """
    Rend le layout principal à partir du template Jinja2 et l'injecte dans un iframe Dash
    
    Args:
        content_html (str): Le contenu HTML à afficher dans la zone principale
        active_page (str): La page active pour le menu (users, trips, stats, support)
        extra_head (str): Code HTML supplementaire à inclure dans le head
        extra_scripts (str): Scripts supplementaires à inclure en fin de page
    
    Returns:
        html.Iframe: Un iframe Dash contenant le layout rendu
    """
    # Rendre le template avec les parametres
    rendered_template = render_template(
        'layouts/main_layout.jinja2',
        user=current_user if hasattr(current_user, 'is_authenticated') else None,
        content=content_html,
        active_page=active_page,
        extra_head=extra_head,
        extra_scripts=extra_scripts
    )
    
    # Creer un iframe contenant le layout rendu
    return html.Iframe(
        srcDoc=rendered_template,
        style={
            "width": "100%",
            "height": "100vh",
            "border": "none",
            "overflow": "hidden"
        }
    )

def integrate_template_into_dash(page_content, template_data=None, template_name=None):
    """
    Integre un template Jinja2 dans une page Dash
    
    Args:
        page_content (str): Contenu HTML à insérer dans le template
        template_data (dict): Donnees à passer au template
        template_name (str): Nom du template à utiliser (si different de main_layout.jinja2)
    
    Returns:
        html.Div: Un conteneur Dash avec l'iframe integre
    """
    if template_name and template_data:
        rendered_content = render_template(template_name, **template_data)
    else:
        # Utiliser le template principal par defaut
        rendered_content = render_main_layout(page_content)
    
    return html.Div([
        rendered_content
    ], style={"height": "100vh", "width": "100%"})
