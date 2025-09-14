#!/usr/bin/env python3
"""
Script de test pour les panels d'entreprise dynamiques
Permet de tester les différents layouts et configurations
"""
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from dash_apps.layouts.dynamic_company_panel import DynamicCompanyPanel
from dash_apps.utils.settings import load_json_config

# Initialiser l'app Dash
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
])

def get_sample_data():
    """Récupère les données d'exemple depuis la config"""
    try:
        config = load_json_config('company_panel_config.json')
        return config.get('sample_data', {})
    except Exception as e:
        print(f"Erreur chargement données: {e}")
        return {
            "klando": {
                "name": "Klando",
                "logo_url": "https://via.placeholder.com/120x120/667eea/white?text=K",
                "description": "Plateforme de covoiturage moderne et sécurisée.",
                "website": "https://klando.com",
                "contact_email": "contact@klando.com",
                "phone": "+33 1 23 45 67 89"
            }
        }

# Layout de l'app de test
app.layout = dbc.Container([
    html.H1("Test des Panels d'Entreprise Dynamiques", className="mb-4 text-center"),
    
    # Contrôles
    dbc.Row([
        dbc.Col([
            html.Label("Choisir l'entreprise:", className="fw-bold"),
            dcc.Dropdown(
                id="company-selector",
                options=[
                    {"label": "Klando", "value": "klando"},
                    {"label": "Test Company", "value": "test_company"},
                    {"label": "StartupTech (avec plus de champs)", "value": "startup_example"}
                ],
                value="klando",
                className="mb-3"
            )
        ], width=6),
        dbc.Col([
            html.Label("Type de panel:", className="fw-bold"),
            dcc.Dropdown(
                id="panel-type-selector",
                options=[
                    {"label": "Default (Horizontal)", "value": "default"},
                    {"label": "Compact", "value": "compact"},
                    {"label": "Full (Vertical)", "value": "full"},
                    {"label": "Card", "value": "card"},
                    {"label": "Minimal", "value": "minimal"},
                    {"label": "Detailed (avec icônes)", "value": "detailed"}
                ],
                value="default",
                className="mb-3"
            )
        ], width=6)
    ]),
    
    # Zone d'affichage du panel
    html.Hr(),
    html.H3("Aperçu du Panel:", className="mb-3"),
    html.Div(id="panel-display"),
    
    # Informations de debug
    html.Hr(),
    html.H4("Données utilisées:", className="mb-2"),
    html.Pre(id="debug-info", style={"backgroundColor": "#f8f9fa", "padding": "10px", "borderRadius": "5px"})
    
], fluid=True, className="py-4")

@callback(
    [Output("panel-display", "children"),
     Output("debug-info", "children")],
    [Input("company-selector", "value"),
     Input("panel-type-selector", "value")]
)
def update_panel(company_key, panel_type):
    """Met à jour l'affichage du panel selon les sélections"""
    
    # Récupérer les données d'exemple
    sample_data = get_sample_data()
    company_data = sample_data.get(company_key, {})
    
    if not company_data:
        return (
            dbc.Alert("Données d'entreprise non trouvées", color="warning"),
            "Aucune donnée disponible"
        )
    
    # Générer le panel
    try:
        panel = DynamicCompanyPanel.render_company_panel(company_data, panel_type)
        
        # Informations de debug
        debug_info = f"""Entreprise: {company_key}
Type de panel: {panel_type}
Données:
{json.dumps(company_data, indent=2, ensure_ascii=False)}"""
        
        return panel, debug_info
        
    except Exception as e:
        error_msg = f"Erreur lors de la génération du panel: {e}"
        return dbc.Alert(error_msg, color="danger"), error_msg

if __name__ == "__main__":
    import json
    print("🚀 Démarrage du serveur de test des panels d'entreprise...")
    print("📱 Ouvrez http://localhost:8051 dans votre navigateur")
    print("🎨 Testez les différents types de panels et entreprises")
    
    app.run(debug=True, port=8051, host="0.0.0.0")
