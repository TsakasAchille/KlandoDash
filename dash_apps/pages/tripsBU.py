from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd

# Imports pour le traitement des données
from dash_apps.data_processing.processors.user_processor import UserProcessor
from dash_apps.components.trips_table import render_trips_table
from dash_apps.components.trip_details_layout import create_trip_details_layout

# Layout de la page des trajets avec des IDs uniques
def get_layout():
    """Génère le layout de la page des trajets avec des IDs uniquement pour cette page"""
    return dbc.Container([
        dcc.Location(id='trips-url', refresh=False),
        dcc.Store(id="klando-users-store"),
        dcc.Store(id="klando-trips-store"),
        dcc.Store(id="klando-selected-trip-id", storage_type="session"),
        dcc.Store(id="klando-page-current", data=0),
        dcc.Store(id="klando-url-trip-id", storage_type="memory"),
        
        html.H2("Dashboard utilisateurs et trajets", style={"marginTop": "20px"}),
        dbc.Row([
            dbc.Col([], width=9),
            dbc.Col([
                dbc.Button("🔄 Rafraîchir les données", id="klando-refresh-btn", color="primary", className="mb-2")
            ], width=3)
        ]),
        html.Div(id="klando-refresh-message"),
        
        # Zone principale qui sera mise à jour par les callbacks
        html.Div(id="klando-trips-main-area"),
        
        # Zone pour les détails
        html.Div(id="klando-trip-details-area")
    ], fluid=True)

# Chargement initial et rafraîchissement des données
@callback(
    [Output("klando-users-store", "data"),
     Output("klando-trips-store", "data")],
    [Input("klando-refresh-btn", "n_clicks")]
)
def load_data(n_clicks):
    # Charger les données utilisateurs et trajets
    users_df = UserProcessor.get_all_users()
    # get_trip_data doit retourner un DataFrame de trajets
    from dash_apps.utils.trip_data import get_trip_data
    trips_df = get_trip_data()
    
    users_data = users_df.to_dict("records") if users_df is not None else []
    trips_data = trips_df.to_dict("records") if trips_df is not None else []
    
    return users_data, trips_data

# Message de rafraîchissement
@callback(
    Output("klando-refresh-message", "children"),
    Input("klando-refresh-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_refresh_message(n_clicks):
    return dbc.Alert("Données rafraîchies! Les nouveaux voyages sont maintenant visibles.", 
                     color="success", 
                     dismissable=True,
                     duration=4000)  # Disparait après 4 secondes

# Affichage du contenu principal
@callback(
    Output("klando-trips-main-area", "children"),
    [Input("klando-users-store", "data"),
     Input("klando-trips-store", "data"),
     Input("klando-selected-trip-id", "data"),
     Input("klando-page-current", "data")],
    prevent_initial_call=False
)
def update_trips_content(users_data, trips_data, selected_trip_id, page_current):
    # Vérifier si les données sont disponibles
    if not trips_data:
        return dbc.Alert(
            "Chargement des données... Si ce message persiste, vérifiez la connexion à la base de données.",
            color="warning",
            className="mt-3"
        )

    # Préparer les données pour affichage
    trips_df = pd.DataFrame(trips_data)
    
    # Présélectionner une ligne si un trajet est déjà sélectionné
    preselect_row = []
    if selected_trip_id and 'trip_id' in trips_df.columns:
        # Convertir selected_trip_id en string pour assurer la compatibilité des types
        selected_trip_id_str = str(selected_trip_id)
        
        # Convertir les trip_id en string pour une comparaison fiable
        if 'trip_id' in trips_df.columns:
            trips_df['trip_id_str'] = trips_df['trip_id'].astype(str)
            idx = trips_df.index[trips_df['trip_id_str'] == selected_trip_id_str].tolist()
            
            if idx:
                preselect_row = [idx[0]]
                # Assurez-vous que la page actuelle est celle où se trouve le trajet sélectionné
                page_size = 10  # Même valeur que dans render_trips_table
                calculated_page = idx[0] // page_size
                if page_current != calculated_page:
                    page_current = calculated_page
    
    # Créer le tableau des trajets
    table = render_trips_table(trips_df, selected_rows=preselect_row, table_id="klando-trips-table", page_current=page_current)
    
    # Message d'instruction adapté selon qu'un trajet est sélectionné ou non
    if preselect_row:
        instruction = html.P("Trajet sélectionné. Les détails sont affichés ci-dessous.", 
                          className="text-success fst-italic")
    else:
        instruction = html.P("Sélectionnez un trajet dans le tableau pour voir les détails.", 
                          className="text-muted fst-italic")
    
    return html.Div([
        instruction, 
        table, 
        html.Hr(className="my-4")
    ])

# Mise à jour de l'ID du trajet sélectionné à partir de l'URL
@callback(
    Output("klando-selected-trip-id", "data", allow_duplicate=True),
    [Input("klando-url-trip-id", "data")],
    [State("klando-trips-store", "data"),
     State("klando-selected-trip-id", "data")],
    prevent_initial_call=True
)
def update_selected_trip_id_from_url(url_trip_id, trips_data, current_trip_id):
    # Sélection via l'URL (prioritaire)
    if url_trip_id is not None:
        print(f"Sélection du trajet {url_trip_id} depuis l'URL")
        return url_trip_id
    
    # Sinon, conserver la sélection actuelle
    return current_trip_id

# Capturer le paramètre trip_id dans l'URL et le stocker séparément
@callback(
    Output("klando-url-trip-id", "data"),
    [Input("trips-url", "search")],
    prevent_initial_call=False
)
def capture_trip_id_from_url(url_search):
    import urllib.parse
    
    if url_search:
        params = urllib.parse.parse_qs(url_search.lstrip('?'))
        trip_id_list = params.get('trip_id')
        if trip_id_list:
            return trip_id_list[0]
    return None

# Ce callback a été fusionné avec update_selected_trip_id_combined

# Mise à jour de la page courante du tableau en fonction du trajet sélectionné
@callback(
    Output("klando-page-current", "data", allow_duplicate=True),
    [Input("klando-selected-trip-id", "data")],
    [State("klando-trips-store", "data"),
     State("klando-page-current", "data")],
    prevent_initial_call=True
)
def update_page_from_selected_trip(selected_trip_id, trips_data, current_page):
    # Si aucun trajet n'est sélectionné ou pas de données, on garde la page courante
    if not selected_trip_id or not trips_data:
        return current_page
        
    try:
        # Trouver l'index du trajet sélectionné
        trips_df = pd.DataFrame(trips_data)
        if 'trip_id' in trips_df.columns:
            # Convertir en string pour éviter les problèmes de types
            trips_df['trip_id_str'] = trips_df['trip_id'].astype(str)
            selected_trip_id_str = str(selected_trip_id)
            
            # Trouver l'indice du trajet sélectionné
            idx = trips_df.index[trips_df['trip_id_str'] == selected_trip_id_str].tolist()
            if idx:
                # Calculer la page correspondante
                page_size = 10  # Taille de page par défaut dans render_trips_table
                calculated_page = idx[0] // page_size
                print(f"Trajet {selected_trip_id} trouvé à l'indice {idx[0]}, page {calculated_page}")
                return calculated_page
    except Exception as e:
        print(f"Erreur lors du calcul de la page: {str(e)}")
    
    # Par défaut, on garde la page courante
    return current_page

# Mise à jour de l'ID du trajet à partir de la sélection dans le tableau
@callback(
    Output("klando-selected-trip-id", "data", allow_duplicate=True),
    [Input("klando-trips-table", "selected_rows")],
    [State("klando-trips-store", "data")],
    prevent_initial_call=True
)
def update_selected_trip_id(selected_rows, trips_data):
    if selected_rows and trips_data:
        trips_df = pd.DataFrame(trips_data)
        selected_trip_id = trips_df.iloc[selected_rows[0]]['trip_id']
        print(f"Sélection du trajet {selected_trip_id} depuis le tableau")
        return selected_trip_id
    return None

# Capturer les changements manuels de page
@callback(
    Output("klando-page-current", "data", allow_duplicate=True),
    Input("klando-trips-table", "page_current"),
    prevent_initial_call=True
)
def update_page_from_pagination(page_current):
    return page_current

# Affichage des détails du trajet sélectionné
@callback(
    Output("klando-trip-details-area", "children"),
    [Input("klando-selected-trip-id", "data"),
     Input("klando-trips-store", "data")]
)
def show_trip_details(selected_trip_id, trips_data):
    # Déléguer la création du layout à la fonction existante
    return create_trip_details_layout(selected_trip_id, trips_data)

# Exporter le layout pour l'application principale
layout = get_layout()
