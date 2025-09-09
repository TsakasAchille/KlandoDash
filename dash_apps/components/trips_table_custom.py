from dash import html, dcc, Input, Output, callback, callback_context, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash
import json
import math
from dash_apps.config import Config
# Removed TripRepository import - now using REST API via RepositoryFactory

def render_custom_trips_table(trips, current_page, total_trips, selected_trip_id=None):
    """Rendu d'un tableau personnalisé avec pagination manuelle pour les trajets
    
    Args:
        trips: Liste des trajets à afficher
        current_page: Page courante (1-indexed)
        total_trips: Nombre total de trajets
        selected_trip_id: ID du trajet sélectionné (optionnel, pour la persistance)
    
    Returns:
        Un composant HTML avec un tableau et des contrôles de pagination
    """
    # Rendu du tableau des trajets
    page_size = Config.USERS_TABLE_PAGE_SIZE
    page_count = math.ceil(total_trips / page_size) if total_trips > 0 else 1
    
    # Créer les en-têtes du tableau (Checkbox en première colonne, puis ID Trajet)
    headers = ["", "ID Trajet", "Origine", "Destination", "Date", "Heure", "Places", "Prix", "Statut"]
    
    # Créer les lignes du tableau
    table_rows = []
    for trip in trips:
        # Pour les objets Pydantic (TripSchema)
        if hasattr(trip, "model_dump"):
            # Convertir l'objet Pydantic en dictionnaire
            trip_dict = trip.model_dump()
            trip_id = trip_dict.get("trip_id", "")
            origin = trip_dict.get("departure_name", "")
            destination = trip_dict.get("destination_name", "")
            departure_date = trip_dict.get("departure_date", "")
            departure_time = trip_dict.get("departure_schedule", "")
            available_seats = trip_dict.get("seats_available", 0)
            price = trip_dict.get("passenger_price", 0)
            status = trip_dict.get("status", "")
        # Pour les dictionnaires
        elif isinstance(trip, dict):
            trip_id = trip.get("trip_id", "")
            origin = trip.get("departure_name", "")
            destination = trip.get("destination_name", "")
            departure_date = trip.get("departure_date", "")
            departure_time = trip.get("departure_schedule", "")
            available_seats = trip.get("seats_available", 0)
            price = trip.get("passenger_price", 0)
            status = trip.get("status", "")
        else:
            # Fallback pour d'autres types d'objets
            trip_id = getattr(trip, 'trip_id', "")
            origin = getattr(trip, 'departure_name', "")
            destination = getattr(trip, 'destination_name', "")
            departure_date = getattr(trip, 'departure_date', "")
            departure_time = getattr(trip, 'departure_schedule', "")
            available_seats = getattr(trip, 'seats_available', 0)
            price = getattr(trip, 'passenger_price', 0)
            status = getattr(trip, 'status', "")

        # Calculer si ce trajet est sélectionné
        is_selected = False
        if selected_trip_id:
            # Extraire l'ID si c'est un dict
            selected_id_value = selected_trip_id
            if isinstance(selected_trip_id, dict):
                selected_id_value = selected_trip_id.get("trip_id")
            
            # Comparaison des IDs
            if selected_id_value and str(trip_id) == str(selected_id_value):
                is_selected = True
        
        # Conversion en string pour l'affichage
        trip_id_str = str(trip_id)
        
        # Formatage des données
        formatted_date = str(departure_date) if departure_date else "-"
        formatted_time = str(departure_time) if departure_time else "-"
        formatted_price = f"{price} FCFA" if price else "-"
        
        # Badge de statut (nouvelles valeurs: PENDING, CONFIRMED, CANCELED)
        status_map_label = {
            "PENDING": "En attente",
            "CONFIRMED": "Confirmé",
            "CANCELED": "Annulé",
        }
        status_map_color = {
            "PENDING": "warning",
            "CONFIRMED": "success",
            "CANCELED": "danger",
        }
        status_upper = str(status).upper() if status else None
        status_badge = dbc.Badge(
            status_map_label.get(status_upper, status if status else "Inconnu"),
            color=status_map_color.get(status_upper, "secondary"),
            className="me-1"
        )

        # Style pour la ligne sélectionnée - en rouge très vif avec bordure
        row_style = {
            "backgroundColor": "#ff3547 !important" if is_selected else "transparent",
            "transition": "all 0.2s",
            "cursor": "pointer",
            "border": "2px solid #dc3545 !important" if is_selected else "none",
            "color": "white !important" if is_selected else "inherit",
            "fontWeight": "bold !important" if is_selected else "normal",
        }
        
        # Style pour chaque cellule de la ligne
        cell_style = {"backgroundColor": "#ff3547 !important" if is_selected else "transparent"}
        
        # Attributs pour la ligne
        row_class = "user-row selected-trip-row" if is_selected else "user-row"
        
        # Créer un ID string pour la ligne et convertir l'objet JSON en string
        row_id_obj = {"type": "trip-row", "index": trip_id}
        
        row_attributes = {
            "id": row_id_obj,  # Dash convertira automatiquement en JSON str
            "className": row_class,
            "title": "Cliquez pour sélectionner ce trajet",
            "style": row_style,
            "n_clicks": 0  # Permettre de capturer les clics sur la ligne
        }
        
        row = html.Tr([
            # Bouton de sélection (première colonne)
            html.Td(
                dbc.Button(
                    children=html.I(className="fas fa-check"),
                    id={"type": "select-trip-btn", "index": trip_id},
                    color="danger" if is_selected else "light",
                    outline=not is_selected,
                    size="sm",
                    style={
                        "width": "30px",
                        "height": "30px",
                        "padding": "0px",
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "center",
                        "margin": "0 auto"
                    }
                ),
                style={"width": "40px", "cursor": "pointer"}
            ),
            # ID du trajet (deuxième colonne)
            html.Td(trip_id_str, style=cell_style),
            # Autres colonnes
            html.Td(origin[:30] + "..." if len(origin) > 30 else origin, style=cell_style),
            html.Td(destination[:30] + "..." if len(destination) > 30 else destination, style=cell_style),
            html.Td(formatted_date, style=cell_style),
            html.Td(formatted_time, style=cell_style),
            html.Td(str(available_seats), style=cell_style),
            html.Td(formatted_price, style=cell_style),
            html.Td(status_badge, style=cell_style),
        ], **row_attributes)
        
        table_rows.append(row)
    
    # Si aucun trajet n'est disponible, afficher une ligne vide
    if not table_rows:
        table_rows = [html.Tr([html.Td("Aucun trajet trouvé", colSpan=9)])]
    
    # Construire le tableau
    table = html.Table(
        [
            # En-tête
            html.Thead(
                html.Tr([html.Th(header) for header in headers]),
                style={
                    "backgroundColor": "#f4f6f8",
                    "color": "#3a4654",
                    "fontWeight": "600",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px"
                }
            ),
            # Corps du tableau
            html.Tbody(table_rows)
        ],
        className="table table-hover",
        style={
            "width": "100%",
            "marginBottom": "0",
            "backgroundColor": "white",
            "borderCollapse": "collapse"
        }
    )
    
    # Contrôles de pagination avec flèches
    pagination = html.Div([
        dbc.Button([
            html.I(className="fas fa-arrow-left mr-2"),
            "Précédent"
        ],
            id="trips-prev-btn", 
            color="primary", 
            outline=False,
            disabled=current_page <= 1,
            style={"backgroundColor": "#4582ec", "borderColor": "#4582ec", "color": "white"}
        ),
        html.Span(
            f"Page {current_page} sur {page_count} (Total: {total_trips} trajets)", 
            style={"margin": "0 15px", "lineHeight": "38px"}
        ),
        dbc.Button([
            "Suivant",
            html.I(className="fas fa-arrow-right ml-2")
        ],
            id="trips-next-btn", 
            color="primary", 
            outline=False,
            disabled=current_page >= page_count,
            style={"backgroundColor": "#4582ec", "borderColor": "#4582ec", "color": "white"}
        )
    ], style={"marginTop": "20px", "textAlign": "center", "padding": "10px"})
    
    # Composant complet
    return html.Div([
        html.Div([
            html.H5("Liste des trajets", style={
                "marginBottom": "15px", 
                "color": "#3a4654",
                "fontWeight": "500",
                "fontSize": "18px"
            }),
            # Message d'aide pour indiquer que les lignes sont cliquables
            html.Div(
                html.Small("Cliquez sur une ligne pour sélectionner un trajet",
                    style={
                        "color": "#666", 
                        "fontStyle": "italic",
                        "marginBottom": "10px",
                        "display": "block"
                    }
                ),
                style={"marginBottom": "10px"}
            ),
            # Les styles sont maintenant appliqués directement aux lignes du tableau
            table
        ], style={
            "padding": "20px",
            "borderRadius": "6px",
            "backgroundColor": "white",
            "boxShadow": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
        }),
        pagination
    ])


# Callback pour la navigation entre les pages avec validation des limites
@callback(
    Output("trips-current-page", "data", allow_duplicate=True),
    Input("trips-prev-btn", "n_clicks"),
    Input("trips-next-btn", "n_clicks"),
    State("trips-current-page", "data"),
    prevent_initial_call=True
)
def handle_trips_pagination_buttons(prev_clicks, next_clicks, current_page):
    ctx = callback_context
    # Gestion de la pagination
    # Si aucun bouton n'a été cliqué
    if not ctx.triggered:
        raise PreventUpdate

    if prev_clicks is None and next_clicks is None:
        raise PreventUpdate
    
    # Déterminer quel bouton a été cliqué
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Valeur par défaut pour current_page si elle n'existe pas encore
    if not isinstance(current_page, (int, float)):
        current_page = 1
        
    # Mettre à jour la page en fonction du bouton cliqué
    if button_id == "trips-prev-btn":
        if current_page <= 1:
            # Déjà à la première page, ne pas changer
            print("[PAGINATION] Déjà à la première page, pas de changement")
            raise PreventUpdate
        new_page = current_page - 1
        print(f"[PAGINATION] Passage à la page {new_page}")
        return new_page
    elif button_id == "trips-next-btn":
        # Validation simple : ne pas dépasser la page courante + 1
        # La validation finale se fera dans render_trips_table
        new_page = current_page + 1
        print(f"[PAGINATION] Tentative passage à la page {new_page}")
        return new_page
    
    # Par défaut, ne pas changer de page
    raise PreventUpdate


# 2. Gestion des clics sur les lignes
@callback(
    Output("selected-trip-id", "data", allow_duplicate=True),
    Input({"type": "trip-row", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True  # Ceci ne suffit pas toujours avec les pattern-matching callbacks
)
def handle_trip_row_selection(row_clicks):
    # Gestion de la sélection de ligne
    
    ctx = callback_context
    if not ctx.triggered:
        # Pas de déclencheur
        raise PreventUpdate
    
    # Vérifier si le callback est déclenché lors du chargement initial
    # Les clicks seront tous à zéro lors du chargement initial
    if not any(clicks > 0 for clicks in row_clicks):
        # Chargement initial, ignorer
        raise PreventUpdate
    
    # Déterminer ce qui a été cliqué
    clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]
    # ID cliqué identifié
    
    try:
        # Extraire l'index (trip_id) de l'ID JSON
        id_dict = json.loads(clicked_id)
        trip_id = id_dict["index"]
        # Trip ID extrait avec succès
        
        # Retourner l'ID extrait
        return trip_id
    except Exception as e:
        print(f"\n[ERROR] Erreur extraction trip_id: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise PreventUpdate


# 3. Nouveau callback pour gérer uniquement la mise en surbrillance des lignes
@callback(
    Output({"type": "trip-row", "index": dash.ALL}, "style"),
    Output({"type": "trip-row", "index": dash.ALL}, "className"),
    Output({"type": "select-trip-btn", "index": dash.ALL}, "color"),
    Output({"type": "select-trip-btn", "index": dash.ALL}, "outline"),
    Input("selected-trip-id", "data"),
    State({"type": "trip-row", "index": dash.ALL}, "id"),
    State({"type": "select-trip-btn", "index": dash.ALL}, "id"),
    prevent_initial_call=False
)
def highlight_selected_trip_row(selected_trip, row_ids, button_ids):
    # Mise en surbrillance de la ligne sélectionnée
    
    if not selected_trip or not row_ids:
        raise PreventUpdate
    
    # Extraire l'id du trajet sélectionné
    selected_trip_id = None
    if isinstance(selected_trip, dict) and "trip_id" in selected_trip:
        selected_trip_id = selected_trip["trip_id"]
    else:
        selected_trip_id = selected_trip
    
    # Trajet sélectionné pour mise en surbrillance
    
    # Préparer les styles pour chaque ligne
    styles = []
    classes = []
    button_colors = []
    button_outlines = []
    
    # Styles pour les lignes
    for row_id in row_ids:
        if isinstance(row_id, dict) and "index" in row_id:
            trip_id = row_id["index"]
            is_selected = str(trip_id) == str(selected_trip_id)
            
            # Exactement les mêmes styles que ceux définis initialement
            style = {
                "backgroundColor": "#ff3547 !important" if is_selected else "transparent",
                "transition": "all 0.2s",
                "cursor": "pointer",
                "border": "2px solid #dc3545 !important" if is_selected else "none",
                "color": "white !important" if is_selected else "inherit",
                "fontWeight": "bold !important" if is_selected else "normal",
            }
            
            # Classe pour la ligne
            class_name = "user-row selected-trip-row" if is_selected else "user-row"
            
            styles.append(style)
            classes.append(class_name)
        else:
            # Valeur par défaut si row_id n'est pas au format attendu
            styles.append({})
            classes.append("user-row")
    
    # Styles pour les boutons
    for button_id in button_ids:
        if isinstance(button_id, dict) and "index" in button_id:
            trip_id = button_id["index"]
            is_selected = str(trip_id) == str(selected_trip_id)
            
            # Couleur et outline du bouton
            button_colors.append("danger" if is_selected else "light")
            button_outlines.append(not is_selected)
        else:
            # Valeur par défaut
            button_colors.append("light")
            button_outlines.append(True)
    
    return styles, classes, button_colors, button_outlines
