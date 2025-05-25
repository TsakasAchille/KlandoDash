from dash import html, dcc
import dash_bootstrap_components as dbc
from flask_login import current_user

# Ne pas utiliser register_page pour u00e9viter le conflit
# Cette page sera appelu00e9e directement depuis app.py

def layout():
    # Si l'utilisateur est du00e9ju00e0 connectu00e9, rediriger vers la page d'accueil
    if current_user.is_authenticated:
        return dcc.Location(pathname="/", id="redirect-home")
    
    # Récupérer les messages flash depuis la session Flask
    from flask import get_flashed_messages
    flash_messages = get_flashed_messages(with_categories=True)
    
    # Créer une liste de messages d'alerte
    alerts = []
    for category, message in flash_messages:
        # Convertir les catégories Flask en couleurs Bootstrap
        color = {
            'danger': 'danger',
            'warning': 'warning',
            'info': 'info',
            'success': 'success'
        }.get(category, 'info')
        
        alerts.append(
            dbc.Alert(message, color=color, dismissable=True, className="mb-2")
        )
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    # Zone d'affichage des messages flash
                    html.Div(alerts, id="flash-messages", className="mb-4"),
                    
                    # Logo Klando
                    html.Div([
                        html.Img(src="assets/icons/klando-500x173.png", style={
                            "width": "100%", 
                            "max-width": "280px", 
                            "object-fit": "contain",
                            "marginBottom": "20px"
                        })
                    ], style={"textAlign": "center"}),
                    
                    html.H2("Bienvenue sur KlandoDash", 
                           className="mb-3", 
                           style={"color": "#505050", "fontWeight": "500"}),
                    
                    html.P("Connectez-vous pour accéder à l'application", 
                          className="text-muted mb-4"),
                    
                    # Carte d'authentification avec style correct (ombres subtiles sur tous les côtés)
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Authentification", 
                                   className="card-title mb-4", 
                                   style={"color": "#464646", "fontWeight": "500"}),
                            
                            # Bouton Google avec icône Font Awesome
                            html.A(
                                dbc.Button(
                                    children=[
                                        html.I(className="fab fa-google me-2"),
                                        "Se connecter avec Google"
                                    ],
                                    color="danger",
                                    size="lg",
                                    className="w-100 mb-3",
                                    style={"borderRadius": "4px", "boxShadow": "0 2px 5px rgba(0,0,0,0.1)"}
                                ),
                                href="/auth/login",
                                style={"textDecoration": "none"}
                            ),
                            
                            # Note sur la restriction des emails
                            html.Div(
                                html.Span(
                                    "Seuls les emails @klando-sn.com sont autorisés",
                                    className="badge bg-primary rounded-pill mt-3"
                                ),
                                className="text-center"
                            )
                        ])
                    ], className="shadow", style={
                        "borderRadius": "8px",
                        "border": "none",
                        "boxShadow": "0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08)",
                        "backgroundColor": "white"
                    }),
                    
                    # Version du bas de page
                    html.P("KlandoDash v1.0", 
                          className="mt-4 text-muted small",
                          style={"opacity": "0.6"})
                    
                ], style={
                    "maxWidth": "450px",
                    "margin": "0 auto",
                    "paddingTop": "80px",
                    "textAlign": "center"
                })
            ], width=12)
        ])
    ], fluid=True, style={
        "background": "linear-gradient(to bottom, #f8f9fa, #e9ecef)",  # Fond légèrement grisé/bleuté
        "minHeight": "100vh",  # Page pleine hauteur
        "padding": "0 12px"    # Léger padding pour les petits écrans
    })
