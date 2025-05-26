import dash_bootstrap_components as dbc
from dash import html, dcc
from dash_apps.config import Config

# Layout de la page de login en version Dash (équivalent au template login.html)
login_layout = html.Div([
    html.Div([
        # Logo Klando avec le logo préféré (selon les préférences de l'utilisateur)
        html.Img(src="/assets/icons/NewLogo.png", alt="KLANDO", style={"height": "120px", "marginBottom": "1.5rem"}),
        
        html.H2("Bienvenue", style={"color": "#505050", "fontWeight": "500", "marginBottom": "1rem"}),
        
        html.P("Connectez-vous pour accéder à l'application", 
              className="text-muted mb-4"),
        
        # Carte d'authentification
        dbc.Card([
            dbc.CardBody([
                html.H4("Authentification", 
                        style={"color": "#464646", "fontWeight": "500"}, 
                        className="card-title mb-4"),
                
                # Onglets de connexion
                dbc.Tabs([
                    dbc.Tab([
                        # Google Login Button
                        dbc.Button([
                            html.I(className="fab fa-google me-2"),
                            "Se connecter avec Google"
                        ], color="danger", className="btn-lg w-100 mb-3", href="/auth/login"),
                        
                        html.Div([
                            dbc.Badge("Connexion avec Google", color="success", pill=True, className="mt-2"),
                            html.P("Seuls les utilisateurs autorisés dans Google Cloud peuvent se connecter."
                                   "Si vous n'avez pas accès, contactez l'administrateur.", 
                                   className="small text-muted mt-2")
                        ], style={"textAlign": "center"})
                    ], label="Google", tab_id="google"),
                    
                    dbc.Tab([
                        # Admin Login Form
                        html.Form([
                            dbc.InputGroup([
                                dbc.InputGroupText(html.I(className="fas fa-user")),
                                dbc.Input(placeholder="Nom d'utilisateur", name="username", required=True)
                            ], className="mb-3"),
                            
                            dbc.InputGroup([
                                dbc.InputGroupText(html.I(className="fas fa-lock")),
                                dbc.Input(placeholder="Mot de passe", type="password", name="password", required=True)
                            ], className="mb-3"),
                            
                            dbc.Button([
                                html.I(className="fas fa-sign-in-alt me-2"),
                                "Connexion"
                            ], color="primary", className="w-100 mb-3", type="submit")
                        ], action="/auth/admin-login", method="post")
                    ], label="Admin", tab_id="admin")
                ], id="login-tabs", active_tab="google")
            ])
        ], className="shadow mb-4"),
        
        # Informations de version
        html.Div([
            html.P([
                "KlandoDash ", 
                html.Span("v1.0.0", className="badge bg-secondary"),
                " - ",
                html.A("Aide", href="/support", className="text-decoration-none")
            ], className="small text-muted")
        ])
    ], className="login-container")
], style={
    "background": "linear-gradient(to bottom, #f8f9fa, #e9ecef)",
    "minHeight": "100vh",
    "padding": "0 12px",
    "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
})
