"""
Callbacks et utilitaires pour la page de validation des documents conducteur (06_driver_validation.py)
Refactorisé pour séparation logique UI/callbacks, inspiré du pattern support_callbacks.py
"""
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, no_update
import dash
from dash_apps.utils.admin_db import is_admin
from dash_apps.utils.user_data_old import update_user_field
from flask import session
import json

from dash_apps.utils.admin_db import is_admin
from dash_apps.utils.user_data_old import update_user_field
from dash_apps.components.driver_validation_components import create_user_document_card
from dash_apps.repositories.user_repository import UserRepository

refresh_store_id = "driver-validation-refresh"

@callback(
    Output("drivers-data-store", "data"),
    Input(refresh_store_id, "data"),
    prevent_initial_call=False
)
def load_all_drivers_to_store(refresh_trigger):
    # On charge tous les conducteurs à valider ET validés
    users = UserRepository.get_pending_drivers() + UserRepository.get_validated_drivers()
    # On ne garde que ceux qui ont un driver_licence_url non nul
    users = [u for u in users if getattr(u, "driver_licence_url", None)]
    return [u.dict() for u in users]

@callback(
    Output("drivers-documents-container", "children"),
    Output("documents-count-badge", "children"),
    Input("validation-filter", "value"),
    Input("drivers-data-store", "data"),
    prevent_initial_call=True
)
def load_drivers_data(filter_value, drivers_data):
    print("")
    print("[load_drivers_data]")
    user_email = session.get('user_email', None)
    if not is_admin(user_email):
        return dbc.Alert("Vous n'avez pas accès à cette page.", color="danger"), 0
    if not drivers_data:
        return dbc.Alert("Aucun utilisateur correspondant aux critères de filtrage.", color="info"), 0
    if filter_value == "pending":
        users = [u for u in drivers_data if u.get("driver_documents_transmitted") and not u.get("is_driver_doc_validated")]
    elif filter_value == "validated":
        users = [u for u in drivers_data if u.get("driver_documents_transmitted") and u.get("is_driver_doc_validated")]
    else:
        users = []
    if not users:
        return dbc.Alert("Aucun utilisateur correspondant aux critères de filtrage.", color="info"), 0
    user_cards = [create_user_document_card(u) for u in users]
    return dbc.Container(user_cards), len(users)

@callback(
    Output(refresh_store_id, "data"),
    [Input({"type": "validate-docs", "index": dash.dependencies.ALL}, "n_clicks")],
    [State(refresh_store_id, "data")],
    prevent_initial_call=True
)
def refresh_after_validation(all_n_clicks, refresh_count):
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

@callback(
    [Output({"type": "validate-docs", "index": dash.dependencies.MATCH}, "disabled"),
     Output({"type": "validate-docs", "index": dash.dependencies.MATCH}, "children"),
     Output({"type": "validation-status", "index": dash.dependencies.MATCH}, "children")],
    [Input({"type": "validate-docs", "index": dash.dependencies.MATCH}, "n_clicks")],
    [State({"type": "validate-docs", "index": dash.dependencies.MATCH}, "id")],
    prevent_initial_call=True
)
def validate_driver_documents(n_clicks, button_id):

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
            success = UserRepository.unvalidate_driver_documents(uid)
            if success:
                return False, "Valider les documents", ""
            else:
                return dash.no_update, "Échec de dévalidation", "Erreur lors de la dévalidation"
        else:
            success = UserRepository.validate_driver_documents(uid)
            if success:
                return False, "Dévalider les documents", "Documents validés"
            else:
                return dash.no_update, "Échec de validation", "Erreur lors de la validation"
    except Exception as e:
        print(f"Erreur lors de la validation/dévalidation des documents: {str(e)}")
        return dash.no_update, "Échec de validation", f"Erreur: {str(e)}"
