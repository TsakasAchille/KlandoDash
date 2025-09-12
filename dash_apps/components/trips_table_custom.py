from dash import html, dcc, callback, Input, Output, State, callback_context, dash_table, ALL, MATCH
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional
from dash_apps.utils.callback_logger import CallbackLogger
from dash_apps.utils.settings import load_json_config
from dash_apps.utils.data_transformer import DataTransformer, TableConfigValidator
# Removed TripRepository import - now using REST API via RepositoryFactory
from dash_apps.config import Config
import math
def _load_table_config():
    """Charge et valide la configuration des colonnes depuis trips_table_config.json"""
    config = load_json_config('trips_table_config.json')
    
    # Valider la configuration contre le schéma SQL
    validator = TableConfigValidator('trips')
    is_valid, errors = validator.validate_config(config)
    
    if not is_valid:
        import warnings
        warnings.warn(f"Configuration de tableau invalide: {'; '.join(errors)}")
    
    return config


_TABLE_CONFIG = _load_table_config()
_DATA_TRANSFORMER = DataTransformer('trips')


def _extract_trip_value(trip, key, default=None):
    """Extrait une valeur d'un trip (dict, pydantic, objet)"""
    if hasattr(trip, "model_dump"):
        try:
            d = trip.model_dump()
            return d.get(key, default)
        except Exception:
            pass
    if isinstance(trip, dict):
        return trip.get(key, default)
    try:
        return getattr(trip, key, default)
    except Exception:
        return default


def _transform_cell_value(col_key, col_conf, trip):
    """Transforme les données via DataTransformer basé sur le schéma SQL."""
    ctype = (col_conf or {}).get("type", "string")
    
    # Récupérer la valeur (avec source alternative si spécifiée)
    transform_conf = (col_conf or {}).get("transform", {})
    source_key = transform_conf.get("source", col_key)
    value = _extract_trip_value(trip, source_key)
    
    # Appliquer les transformations selon le type et la config
    if transform_conf:
        # Utiliser le DataTransformer pour les transformations configurées
        return _DATA_TRANSFORMER.transform_value(col_key, value, transform_conf)
    
    # Fallbacks pour les types simples sans transformation explicite
    if ctype == "currency":
        unit = (col_conf or {}).get("unit", "")
        config = {"type": "currency", "unit": unit}
        return _DATA_TRANSFORMER.transform_value(col_key, value, config)
    
    if ctype == "enum":
        values_map = (col_conf or {}).get("values", {})
        config = {"type": "enum_badge", "values": values_map}
        return _DATA_TRANSFORMER.transform_value(col_key, value, config)
    
    if (col_conf or {}).get("truncate"):
        max_length = int((col_conf or {}).get("truncate"))
        config = {"type": "truncate", "max_length": max_length}
        return _DATA_TRANSFORMER.transform_value(col_key, value, config)
    
    # Type simple (string, number, etc.)
    return (str(value) if value not in (None, "") else "-"), {}


def _render_cell(col_key, col_conf, trip, is_selected=False):
    """Rendu de cellule: se contente de présenter la valeur déjà transformée."""
    cell_style = {"backgroundColor": "#ff3547 !important" if is_selected else "transparent"}
    value, meta = _transform_cell_value(col_key, col_conf, trip)
    if meta.get("as_badge"):
        badge = dbc.Badge(value, color=meta.get("badge_color", "secondary"), className="me-1")
        return html.Td(badge, style=cell_style)
    return html.Td(value, style=cell_style)


def _visible_columns_order():
    """Détermine l'ordre des colonnes visibles à partir du JSON, avec fallback"""
    columns_conf = (_TABLE_CONFIG or {}).get("columns", {})
    # Utiliser strictement l'ordre déclaré dans le JSON (ordre d'insertion des clés)
    # Filtrer uniquement les colonnes visibles
    return [k for k, v in columns_conf.items() if v.get("visible", True)]


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
    
    # Colonnes dynamiques à partir du JSON (la première colonne est le bouton de sélection)
    columns_conf = (_TABLE_CONFIG or {}).get("columns", {})
    columns_order = _visible_columns_order()
    headers = [""] + [columns_conf[c].get("label", c) for c in columns_order]
    
    # Créer les lignes du tableau
    table_rows = []
    for trip in trips:
        # Extraire uniquement l'identifiant pour la logique de sélection
        trip_id = _extract_trip_value(trip, "trip_id", "")

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
        
        # Conversion en string pour l'affichage de l'ID
        trip_id_str = str(trip_id)

        # Style pour la ligne sélectionnée - en rouge très vif avec bordure
        row_style = {
            "backgroundColor": "#ff3547 !important" if is_selected else "transparent",
            "transition": "all 0.2s",
            "cursor": "pointer",
            "border": "2px solid #dc3545 !important" if is_selected else "none",
            "color": "white !important" if is_selected else "inherit",
            "fontWeight": "bold !important" if is_selected else "normal",
        }
        
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
        
        # Construire la ligne dynamiquement selon la config
        row_cells = [
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
            )
        ]

        # Colonnes dynamiques
        for col_key in columns_order:
            col_conf = columns_conf.get(col_key, {})
            # S'assurer que l'ID est affiché tel que string si col_key == 'trip_id'
            if col_key == 'trip_id':
                row_cells.append(html.Td(trip_id_str, style={"backgroundColor": "#ff3547 !important" if is_selected else "transparent"}))
            else:
                row_cells.append(_render_cell(col_key, col_conf, trip, is_selected))

        row = html.Tr(row_cells, **row_attributes)
        
        table_rows.append(row)
    
    # Si aucun trajet n'est disponible, afficher une ligne vide
    if not table_rows:
        table_rows = [html.Tr([html.Td("Aucun trajet trouvé", colSpan=len(headers))])]
    
    # Construire le tableau (en-têtes et corps)
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
    Input({"type": "trip-row", "index": ALL}, "n_clicks"),
    prevent_initial_call=True  # Ceci ne suffit pas toujours avec les pattern-matching callbacks
)
def handle_trip_row_selection(row_clicks):
    """Gestion de la sélection de ligne"""
    CallbackLogger.log_callback(
        "handle_trip_row_selection",
        {"row_clicks_count": len(row_clicks) if row_clicks else 0},
        status="INFO",
        extra_info="Processing row selection"
    )
    
    ctx = callback_context
    if not ctx.triggered:
        CallbackLogger.log_callback(
            "handle_trip_row_selection", 
            {}, 
            status="WARNING", 
            extra_info="No trigger context"
        )
        raise PreventUpdate
    
    # Vérifier si le callback est déclenché lors du chargement initial
    if not any(clicks > 0 for clicks in row_clicks):
        CallbackLogger.log_callback(
            "handle_trip_row_selection", 
            {"all_clicks_zero": True}, 
            status="INFO", 
            extra_info="Initial load, ignoring"
        )
        raise PreventUpdate
    
    # Déterminer ce qui a été cliqué
    clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    try:
        # Extraire l'index (trip_id) de l'ID JSON
        id_dict = json.loads(clicked_id)
        trip_id = id_dict["index"]
        
        CallbackLogger.log_callback(
            "handle_trip_row_selection",
            {"selected_trip_id": trip_id},
            status="SUCCESS",
            extra_info=f"Trip {trip_id} selected"
        )
        
        return trip_id
    except Exception as e:
        CallbackLogger.log_callback(
            "handle_trip_row_selection",
            {"error": str(e), "clicked_id": clicked_id},
            status="ERROR",
            extra_info="Failed to extract trip_id"
        )
        raise PreventUpdate


# 3. Nouveau callback pour gérer uniquement la mise en surbrillance des lignes
@callback(
    Output({"type": "trip-row", "index": ALL}, "style"),
    Output({"type": "trip-row", "index": ALL}, "className"),
    Output({"type": "select-trip-btn", "index": ALL}, "color"),
    Output({"type": "select-trip-btn", "index": ALL}, "outline"),
    Input("selected-trip-id", "data"),
    State({"type": "trip-row", "index": ALL}, "id"),
    State({"type": "select-trip-btn", "index": ALL}, "id"),
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
