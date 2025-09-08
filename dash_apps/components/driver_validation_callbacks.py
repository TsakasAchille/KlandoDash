"""
Callbacks et utilitaires pour la page de validation des documents conducteur (06_driver_validation.py)
Refactorisé pour séparation logique UI/callbacks, inspiré du pattern support_callbacks.py
"""
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, no_update
import dash
from flask import session
import json

from dash_apps.utils.admin_db_rest import is_admin
from dash_apps.utils.user_data_old import update_user_field
from dash_apps.repositories.user_repository import UserRepository
from dash_apps.components.driver_validation_components import create_pending_document_card, create_validated_document_card

refresh_store_id = "driver-validation-refresh"

@callback(
    Output("drivers-data-store", "data"),
    Input(refresh_store_id, "data"),
    prevent_initial_call=False
)
def load_all_drivers_to_store(refresh_trigger):
    # On charge tous les conducteurs à valider ET validés
    users = UserRepository.get_pending_drivers() + UserRepository.get_validated_drivers()
    # On ne garde que ceux qui ont un driver_license_url non nul
    users = [u for u in users if getattr(u, "driver_license_url", None)]
    return [u.dict() for u in users]

# Fonction utilitaire pour paginer une liste d'éléments
def paginate_list(items, page, items_per_page=10):
    """Découpe une liste en segments de taille items_per_page et renvoie le segment pour la page demandée"""
    # Calcul du nombre total de pages
    total_pages = (len(items) + items_per_page - 1) // items_per_page  # Arrondir au supérieur
    
    # Ajuster la page si nécessaire
    page = min(max(1, page), max(1, total_pages))
    
    # Calculer les indices pour la pagination
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(items))
    
    # Retourner les éléments pour la page courante et le nombre total de pages
    return items[start_idx:end_idx], total_pages, page

@callback(
    Output("documents-count-badge", "children"),
    [Input("drivers-data-store", "data")],
)
def update_total_documents_count(drivers_data):
    """Mise à jour du compteur total de documents"""
    if not drivers_data:
        return 0
        
    # Séparation des utilisateurs en deux catégories pour le comptage
    pending_users = [u for u in drivers_data if not u.get("is_driver_doc_validated") and (u.get("id_card_url") or u.get("driver_license_url"))]
    validated_users = [u for u in drivers_data if u.get("is_driver_doc_validated")]
    
    # Comptage du total des documents
    total_docs = len(pending_users) + len(validated_users)
    
    return total_docs

@callback(
    [Output("pending-documents-container", "children"),
     Output("pending-page", "max_value"),
     Output("pending-page", "active_page")],
    [Input("drivers-data-store", "data"),
     Input("pending-page", "active_page")],
    prevent_initial_call=False
)
def display_pending_documents(drivers_data, page_click):
    """Affiche les documents en attente de validation avec pagination"""
    if not drivers_data:
        return dbc.Alert("Aucune donnée utilisateur disponible.", color="info"), 1, 1, "Documents en attente (0)"
    
    # Déterminer la page courante
    page = page_click or 1
    
    # Filtrer les utilisateurs avec documents en attente
    pending_users = [u for u in drivers_data if not u.get("is_driver_doc_validated") and (u.get("id_card_url") or u.get("driver_license_url"))]
    
    # Pagination - 10 documents par page
    items_per_page = 10
    current_pending_users, total_pages, current_page = paginate_list(pending_users, page, items_per_page)
    
    # Création des cartes pour les documents de la page courante
    pending_cards = [create_pending_document_card(u) for u in current_pending_users]
    
    # Construction du layout sans recréer la pagination
    layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H4("Documents en attente", className="mb-3"), width=8),
            dbc.Col(html.Div(f"Page {current_page}/{max(1, total_pages)}", className="text-end text-muted pt-2"), width=4)
        ]),
        dbc.Container(pending_cards) if pending_cards else dbc.Alert("Aucun document en attente de validation", color="info")
    ])
    
    # Retour simplifié sans mise à jour du label de l'onglet
    return layout, total_pages, current_page

@callback(
    [Output("validated-documents-container", "children"),
     Output("validated-page", "max_value"),
     Output("validated-page", "active_page")],
    [Input("drivers-data-store", "data"),
     Input("validated-page", "active_page")],
    prevent_initial_call=False
)
def display_validated_documents(drivers_data, page_click):
    """Affiche les documents déjà validés avec pagination"""
    if not drivers_data:
        return dbc.Alert("Aucune donnée utilisateur disponible.", color="info"), 1, 1, "Documents validés (0)"
    
    # Déterminer la page courante
    page = page_click or 1
    
    # Filtrer les utilisateurs avec documents validés
    validated_users = [u for u in drivers_data if u.get("is_driver_doc_validated")]
    
    # Pagination - 10 documents par page
    items_per_page = 10
    current_validated_users, total_pages, current_page = paginate_list(validated_users, page, items_per_page)
    
    # Création des cartes pour les documents de la page courante
    validated_cards = [create_validated_document_card(u) for u in current_validated_users]
    
    # Construction du layout sans recréer la pagination
    layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H4("Documents validés", className="mb-3"), width=8),
            dbc.Col(html.Div(f"Page {current_page}/{max(1, total_pages)}", className="text-end text-muted pt-2"), width=4)
        ]),
        dbc.Container(validated_cards) if validated_cards else dbc.Alert("Aucun document validé", color="info")
    ])
    
    # Retour simplifié sans mise à jour du label de l'onglet
    return layout, total_pages, current_page

@callback(
    Output(refresh_store_id, "data"),
    [Input({"type": "validate-docs", "index": dash.dependencies.ALL}, "n_clicks")],
    [State(refresh_store_id, "data")],
    prevent_initial_call=True
)
def refresh_after_validation(all_n_clicks, refresh_count):

    print("refresh_after_validation")
    ctx = dash.callback_context
    if not ctx.triggered or all(v is None for v in all_n_clicks):
        return dash.no_update
    return (refresh_count or 0) + 1

@callback(
    Output({"type": "compare-modal", "index": dash.dependencies.ALL}, "is_open"),
    [Input({"type": "compare-docs", "index": dash.dependencies.ALL}, "n_clicks"),
     Input({"type": "close-compare-modal", "index": dash.dependencies.ALL}, "n_clicks")],
    [State({"type": "compare-modal", "index": dash.dependencies.ALL}, "is_open"),
     State({"type": "compare-docs", "index": dash.dependencies.ALL}, "id")],
    prevent_initial_call=True
)
def toggle_compare_modal(open_clicks, close_clicks, is_open_list, compare_docs_ids):
    ctx = dash.callback_context
    if not ctx.triggered:
        return is_open_list
    triggered = ctx.triggered[0]["prop_id"].split(".")[0]
    try:
        idx = json.loads(triggered)["index"]
    except Exception:
        return is_open_list
    new_states = list(is_open_list)
    input_ids = [i["index"] for i in compare_docs_ids]
    try:
        pos = input_ids.index(idx)
    except ValueError:
        return is_open_list
    if "compare-docs" in triggered:
        new_states[pos] = True
    elif "close-compare-modal" in triggered:
        new_states[pos] = False
    return new_states

@callback(
    Output({"type": "modal", "index": dash.dependencies.MATCH}, "is_open"),
    [Input({"type": "view-doc", "index": dash.dependencies.MATCH}, "n_clicks"),
     Input({"type": "close-modal", "index": dash.dependencies.MATCH}, "n_clicks")],
    [State({"type": "modal", "index": dash.dependencies.MATCH}, "is_open")]
)
def toggle_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

# Callback pour mettre à jour l'état des boutons et statuts après validation/dévalidation
@callback(
    [Output({"type": "validate-docs", "index": dash.dependencies.MATCH}, "disabled"),
     Output({"type": "validate-docs", "index": dash.dependencies.MATCH}, "children"),
     Output({"type": "validation-status", "index": dash.dependencies.MATCH}, "children")],
    [Input({"type": "validate-docs", "index": dash.dependencies.MATCH}, "n_clicks")],
    [State({"type": "validate-docs", "index": dash.dependencies.MATCH}, "id")],
    prevent_initial_call=True
)
def validate_driver_documents(n_clicks, button_id):
    print(f"Validation/Dévalidation pour {button_id['index']}")
    
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update
    
    uid = button_id["index"]
    # On récupère le statut actuel via get_user_by_id
    user_obj = UserRepository.get_user_by_id(uid)
    is_validated = False
    if user_obj:
        is_validated = getattr(user_obj, "is_driver_doc_validated", False)
    
    try:
        if is_validated:
            # Dévalidation
            success = UserRepository.unvalidate_driver_documents(uid)
            if success:
                # Déclenche le second callback pour le rafraîchissement
                return False, "Valider les documents", ""
            else:
                return dash.no_update, "Échec de dévalidation", "Erreur lors de la dévalidation"
        else:
            # Validation
            success = UserRepository.validate_driver_documents(uid)
            if success:
                # Déclenche le second callback pour le rafraîchissement
                return False, "Dévalider les documents", "Documents validés"
            else:
                return dash.no_update, "Échec de validation", "Erreur lors de la validation"
    except Exception as e:
        print(f"Erreur lors de la validation/dévalidation des documents: {str(e)}")
        return dash.no_update, "Échec de validation", f"Erreur: {str(e)}"


# Callback séparé pour forcer le rafraîchissement après validation/

"""
@callback(
    Output(refresh_store_id, "data", allow_duplicate=True),
    [Input({"type": "validate-docs", "index": dash.dependencies.ALL}, "children")],
    [State(refresh_store_id, "data")],
    prevent_initial_call=True
)
def force_refresh_after_validation(all_button_texts, refresh_count):
    #Ce callback surveille les changements de texte des boutons de validation
    #et force un rafraîchissement quand un bouton change d'état
    
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    
    print(f"Force refresh détecté, nouveau compteur: {(refresh_count or 0) + 1}")
    return (refresh_count or 0) + 1
"""

# Callback pour gérer la navigation entre onglets
@callback(
    [
        Output("tab-content-1", "style"),
        Output("tab-content-2", "style"),
        Output("tab1-link", "active"),
        Output("tab2-link", "active"),
    ],
    [Input("tab1-link", "n_clicks"),
     Input("tab2-link", "n_clicks")],
    prevent_initial_call=True
)
def toggle_tabs(n1, n2):
    ctx = dash.callback_context
    if not ctx.triggered:
        return {"display": "block"}, {"display": "none"}, True, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "tab1-link":
            return {"display": "block"}, {"display": "none"}, True, False
        else:
            return {"display": "none"}, {"display": "block"}, False, True

