#!/usr/bin/env python3
"""
Script pour lire et afficher les informations basic_info depuis trip_details_config.json
Affichage en ligne (layout horizontal)
"""
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from dash_apps.utils.settings import load_json_config
from jinja2 import Environment, FileSystemLoader
import os

# Initialiser l'app Dash
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    "/dash_apps/assets/icons.css"
])

def load_basic_info_config():
    """Charge la configuration basic_info depuis trip_details_config.json"""
    try:
        config = load_json_config('trip_details_config.json')
        basic_info = config.get('trip_details', {}).get('fields', {}).get('basic_info', {})
        print(f"🔧 Configuration chargée: {len(basic_info)} champs trouvés")
        for field_name, field_config in basic_info.items():
            icon = field_config.get('icon', 'AUCUNE')
            print(f"   - {field_name}: icône = '{icon}'")
        return basic_info
    except Exception as e:
        print(f"Erreur chargement config: {e}")
        return {}

def create_basic_info_display(trip_data):
    """
    Crée l'affichage des informations basic_info en utilisant le template existant trip_details_template.jinja2
    """
    # Charger la configuration complète pour récupérer les paramètres de layout
    try:
        config = load_json_config('trip_details_config.json')
        layout_config = config.get('trip_details', {}).get('layout', {})
        card_height = layout_config.get('card_height', '400px')
        card_width = layout_config.get('card_width', '100%')
        card_min_height = layout_config.get('card_min_height', '300px')
    except Exception as e:
        print(f"Erreur chargement layout config: {e}")
        card_height = "400px"
        card_width = "100%"
        card_min_height = "300px"
    
    # Configurer Jinja2
    template_dir = os.path.join(os.path.dirname(__file__), 'dash_apps', 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('trip_details_template.jinja2')
    
    # Compléter le dictionnaire trip_data avec les données manquantes si nécessaire
    complete_trip_data = {
        "trip_id": trip_data.get("trip_id", "TRIP-1234567890-abcdef"),
        "departure_name": trip_data.get("departure_name", "Paris"),
        "destination_name": trip_data.get("destination_name", "Lyon"),
        "departure_date": trip_data.get("departure_date", "15/09/2025"),
        "departure_schedule": trip_data.get("departure_schedule", "14:30")
    }
    
    # Rendre le template existant avec les paramètres de layout
    html_content = template.render(
        trip=complete_trip_data,
        layout={
            'card_height': card_height,
            'card_width': card_width,
            'card_min_height': card_min_height
        }
    )
    
    # Retourner le HTML rendu dans un composant Dash
    return html.Div([
        html.Iframe(
            srcDoc=html_content,
            style={
                "width": card_width,
                "height": card_height,
                "minHeight": card_min_height,
                "border": "none",
                "borderRadius": "12px"
            }
        )
    ])

# Données d'exemple pour tester
sample_trip_data = {
    "trip_id": "TRIP-1234567890-abcdef",
    "departure_name": "Paris",
    "destination_name": "Lyon", 
    "departure_date": "15/09/2025",
    "departure_schedule": "14:30"
}

def create_input_layout():
    """Crée le layout des inputs en utilisant les labels du JSON"""
    basic_info_config = load_basic_info_config()
    
    if not basic_info_config:
        return html.Div("Configuration non trouvée", className="alert alert-warning")
    
    # Trier les champs par ordre
    sorted_fields = sorted(
        basic_info_config.items(), 
        key=lambda x: x[1].get('order', 999)
    )
    
    # Créer les inputs dynamiquement
    input_rows = []
    current_row = []
    
    for field_name, field_config in sorted_fields:
        if not field_config.get('display', True):
            continue
            
        label = field_config.get('label', field_name)
        
        input_col = dbc.Col([
            html.Label(f"{label}:", className="fw-bold"),
            dcc.Input(
                id=f"{field_name}-input",
                value=sample_trip_data.get(field_name, ""),
                className="form-control mb-2"
            )
        ], width=6)
        
        current_row.append(input_col)
        
        # Créer une nouvelle ligne tous les 2 éléments
        if len(current_row) == 2:
            input_rows.append(dbc.Row(current_row))
            current_row = []
    
    # Ajouter la dernière ligne si elle n'est pas vide
    if current_row:
        input_rows.append(dbc.Row(current_row))
    
    return input_rows

# Layout de l'app
app.layout = dbc.Container([
    html.H1("Test Affichage Basic Info", className="mb-4 text-center"),
    
    # Contrôles générés dynamiquement
    html.Div(id="input-controls"),
    
    html.Hr(),
    
    # Zone d'affichage
    html.Div(id="basic-info-display"),
    
    # Debug info
    html.Hr(),
    html.H4("Configuration chargée:", className="mb-2"),
    html.Pre(id="config-debug", style={"backgroundColor": "#f8f9fa", "padding": "10px"})
    
], fluid=True, className="py-4")

@callback(
    [Output("input-controls", "children"),
     Output("basic-info-display", "children"),
     Output("config-debug", "children")],
    [Input("input-controls", "id")]  # Trigger initial load
)
def update_display(_):
    """Met à jour l'affichage initial avec les données par défaut"""
    
    # Créer les contrôles d'input
    input_layout = create_input_layout()
    
    # Utiliser les données d'exemple
    trip_data = sample_trip_data
    
    # Générer l'affichage
    display = create_basic_info_display(trip_data)
    
    # Info de debug
    config = load_basic_info_config()
    debug_info = f"""Configuration basic_info chargée:
{len(config)} champs trouvés

Champs:
"""
    for field_name, field_config in config.items():
        debug_info += f"- {field_name}: {field_config.get('label', 'N/A')} (ordre: {field_config.get('order', 'N/A')})\n"
    
    return input_layout, display, debug_info

if __name__ == "__main__":
    import json
    print("🚀 Démarrage du test basic_info...")
    print("📱 Ouvrez http://localhost:8052 dans votre navigateur")
    print("🎨 Testez l'affichage des informations basic_info en ligne")
    
    app.run(debug=True, port=8052, host="0.0.0.0")
