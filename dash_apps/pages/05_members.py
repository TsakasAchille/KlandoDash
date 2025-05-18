from dash import html, register_page, dcc
import dash_bootstrap_components as dbc
from dash_apps.components.members_management import render_members_list
from flask_login import current_user, login_required
from dash import no_update

# Enregistrement de la page
register_page(__name__, path='/members')

# Contenu de la page
def layout():
    # Vérifier si l'utilisateur est connecté
    if not current_user.is_authenticated:
        return dbc.Container([
            dbc.Alert(
                [
                    html.H4("Accès restreint", className="alert-heading"),
                    html.P("Vous devez être connecté pour accéder à cette page."),
                    dbc.Button("Se connecter", href="/auth/login", color="primary"),
                ],
                color="warning",
                className="mt-4"
            )
        ])
    
    # Affichage de la liste des membres
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Gestion des membres"),
                html.Hr(),
                html.Div(id="members-list-container", children=render_members_list()),
                
                # Elements cachés pour les callbacks
                html.Div(id="dummy-output", style={"display": "none"}),
                html.Div(id="dummy-output-2", style={"display": "none"}),
            ])
        ])
    ])
