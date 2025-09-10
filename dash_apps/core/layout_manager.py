import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_apps.auth.simple_auth import render_user_menu

def create_main_layout():
    """
    Créé le layout principal de l'application avec Dash Pages
    """
    layout = dbc.Container([
        dcc.Location(id="url", refresh=False),
        # Auto-open control (once per session)
        dcc.Store(id="chatbot-welcome-store", storage_type="session", data=None),
        dcc.Interval(id="chatbot-autoopen-init", interval=300, max_intervals=1),
        
        # Barre latérale fixe
        dbc.Row([
            # Sidebar navigation
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Img(src="assets/icons/klando-500x173.png", style={"width": "100%", "max-width": "180px", "object-fit": "contain"}, className="mt-4 mb-4") 
                    ], style={"text-align": "center"}),
                    dbc.Nav([
                        # Navigation générée automatiquement depuis le registre des pages (exclut admin et driver_validation)
                        html.Div([
                            dcc.Link(
                                page['name'], 
                                href=page['relative_path'],
                                className="nav-link mb-2"
                            ) for page in dash.page_registry.values() 
                            if page.get('module') not in ['admin', 'driver_validation']
                        ]),
                        # Liens d'administration (affichés conditionnellement par callback)
                        html.Div(id="admin-nav-container", children=[
                            dbc.NavLink("Administration", href="/admin", active="exact", id="nav-admin", className="mb-2 text-danger"),
                            dbc.NavLink("Validation Conducteurs", href="/driver-validation", active="exact", id="nav-driver-validation", className="mb-2 text-danger")
                        ], style={"display": "none"}),
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
            
            # Contenu principal avec dash.page_container
            dbc.Col([
                html.Div([
                    dash.page_container
                ], id="main-content", style={"marginLeft": "12px", "marginRight": "12px"})
            ], width=10)
        ], className="g-0"),

        # Floating Yode logo (interactive)
        html.Img(
            src="/assets/icons/yode.svg",
            id="open-chatbot-bubble",
            n_clicks=0,
            className="yode-floating-logo",
        ),

        # Floating Chatbot container
        html.Div([
            # Chatbot window
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Img(src="/assets/icons/yode.svg", className="yode-logo-header"),
                            html.Span("Yobe", className="chatbot-title"),
                        ], className="d-flex align-items-center"),
                        html.Div([
                            dbc.Button(html.I(className="fas fa-minus"), id="minimize-chatbot-window", size="sm", color="secondary", outline=True, className="me-1", title="Réduire"),
                        ], className="d-flex align-items-center")
                    ], className="d-flex justify-content-between align-items-center"),
                ], className="chatbot-header chatbot-dragger"),
                html.Div([
                    html.Iframe(
                        src="https://klandochatbot.onrender.com/embed.html?api_key=klando-dashboard-key",
                        className="chatbot-iframe",
                        allow="clipboard-write; display-capture; autoplay",
                        title="Yobe",
                    )
                ], className="chatbot-body"),
                # Resize handle inside window
                html.Div(className="chatbot-resizer"),
            ], className="chatbot-window-inner")
        ], id="chatbot-window", className="chatbot-window", style={"display": "none"}),
    ], fluid=True, style={"height": "100vh"})
    
    # Ajouter un composant de redirection pour la déconnexion
    layout.children.append(dcc.Location(id='redirect-logout', refresh=True))
    
    return layout
