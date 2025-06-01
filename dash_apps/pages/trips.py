from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

# Imports pour le traitement des données
from dash_apps.models.user import User
from dash_apps.repositories.trip_repository import TripRepository
from dash_apps.schemas.trip import TripSchema
from dash_apps.core.database import get_session
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
    # Charger les données utilisateurs et trajets via SQLAlchemy
    with get_session() as session:
        users = session.query(User).all()
        users_data = [u.to_dict() for u in users] if users else []
        trips = TripRepository.list_trips(session)
        trips_data = [t.model_dump() for t in trips] if trips else []
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

    # Préparer les données pour affichage (plus de pandas)
    preselect_row = []
    trips_list = trips_data if trips_data else []
    # Trouver l'index du trajet sélectionné
    if selected_trip_id and trips_list and isinstance(trips_list, list):
        selected_trip_id_str = str(selected_trip_id)
        for idx, trip in enumerate(trips_list):
            if str(trip.get('trip_id')) == selected_trip_id_str:
                preselect_row = [idx]
                page_size = 10
                calculated_page = idx // page_size
                if page_current != calculated_page:
                    page_current = calculated_page
                break
    # Créer le tableau des trajets (en passant la liste de dicts)
    import pandas as pd
    trips_df = pd.DataFrame(trips_list) if trips_list else pd.DataFrame()
    table = render_trips_table(trips_df, selected_rows=preselect_row, table_id="klando-trips-table", page_current=page_current)
    # Message d'instruction
    instruction = html.P("Trajet sélectionné. Les détails sont affichés ci-dessous.", className="text-success fst-italic") if preselect_row else html.P("Sélectionnez un trajet dans le tableau pour voir les détails.", className="text-muted fst-italic")
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

# Mise à jour de l'ID du trajet sélectionné depuis l'URL
@callback(
    Output("klando-selected-trip-id", "data", allow_duplicate=True),
    [Input("trips-url", "search")],
    [State("klando-trips-store", "data")],
    prevent_initial_call=True
)
def update_selected_trip_id_from_url(url_search, trips_data):
    import urllib.parse
    
    if not url_search:
        return None
        
    params = urllib.parse.parse_qs(url_search.lstrip('?'))
    trip_id_list = params.get('trip_id')
    
    if not trip_id_list:
        return None
        
    trip_id = trip_id_list[0]
    print(f"Sélection du trajet {trip_id} depuis l'URL")
    return trip_id

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
        
    # Trouver l'index du trajet sélectionné sans pandas
    if selected_trip_id and trips_data:
        selected_trip_id_str = str(selected_trip_id)
        for idx, trip in enumerate(trips_data):
            if str(trip.get('trip_id')) == selected_trip_id_str:
                page_size = 10
                calculated_page = idx // page_size
                print(f"Trajet {selected_trip_id} trouvé à l'indice {idx}, page {calculated_page}")
                return calculated_page
    return current_page

# Mise à jour de l'ID du trajet sélectionné depuis le tableau
@callback(
    Output("klando-selected-trip-id", "data"),
    [Input("klando-trips-table", "selected_rows")],
    [State("klando-trips-store", "data")]
)
def update_selected_trip_id(selected_rows, trips_data):
    if selected_rows and trips_data:
        try:
            selected_trip = trips_data[selected_rows[0]]
            selected_trip_id = selected_trip.get('trip_id')
            print(f"Sélection du trajet {selected_trip_id} depuis le tableau")
            return selected_trip_id
        except Exception as e:
            print(f"Erreur lors de la sélection du trajet : {e}")
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
