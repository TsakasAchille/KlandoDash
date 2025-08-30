from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_apps.auth.simple_auth import render_user_menu

def create_main_layout():
    """
    Créé le layout principal de l'application avec la barre latérale et l'espace pour le contenu
    """
    layout = dbc.Container([
        dcc.Location(id="url", refresh=False),
        
        # Barre latérale fixe
        dbc.Row([
            # Sidebar navigation
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Img(src="assets/icons/klando-500x173.png", style={"width": "100%", "max-width": "180px", "object-fit": "contain"}, className="mt-4 mb-4") 
                    ], style={"text-align": "center"}),
                    dbc.Nav([
                        dbc.NavLink("Carte", href="/", active="exact", id="nav-map", className="mb-2"),
                        dbc.NavLink("Utilisateurs", href="/users", active="exact", id="nav-users", className="mb-2"),
                        dbc.NavLink("Trajets", href="/trips", active="exact", id="nav-trips", className="mb-2"),
                        dbc.NavLink("Statistiques", href="/stats", active="exact", id="nav-stats", className="mb-2"),
                        dbc.NavLink("Support", href="/support", active="exact", id="nav-support", className="mb-2"),
                        # Liens d'administration (affichés conditionnellement par callback)
                        html.Div(id="admin-nav-container", children=[
                            dbc.NavLink("Administration", href="/admin", active="exact", id="nav-admin", className="mb-2 text-danger"),
                            dbc.NavLink("Validation Conducteurs", href="/driver-validation", active="exact", id="nav-driver-validation", className="mb-2 text-danger")
                        ], style={"display": "none"}),
                        # Temporairement désactivé car incompatible avec le nouveau système d'authentification
                        # dbc.NavLink("Membres", href="/members", active="exact", id="nav-members", className="mb-2"),
                    ], vertical=True, pills=True, className="sidebar-nav"),
                    
                    html.Div([
                        html.Hr(),
                        html.Div(id="user-info-sidebar")
                    ], className="mt-auto mb-3")
                    
                ], style={
                    "position": "fixed", 
                    "top": 0, 
                    "left": 0, 
                    "height": "100vh", 
                    "width": "220px", 
                    "background": "#f8f9fa", 
                    "padding": "24px 12px 0 12px", 
                    "borderRight": "2px solid #eee", 
                    "zIndex": 1000,
                    "display": "flex",
                    "flexDirection": "column",
                    "justifyContent": "space-between"
                })
            ], width=2, style={"padding": 0, "maxWidth": "220px"}),
            
            # Contenu principal
            dbc.Col([
                html.Div(id="main-content", style={"marginLeft": "12px", "marginRight": "12px"})
            ], width=10)
        ], className="g-0")
    ], fluid=True, style={"height": "100vh"})
    
    # Ajouter un composant de redirection pour la déconnexion
    layout.children.append(dcc.Location(id='redirect-logout', refresh=True))
    
    return layout
