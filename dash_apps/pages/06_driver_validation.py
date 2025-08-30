import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash
from dash_apps.repositories.user_repository import UserRepository
from dash_apps.utils.admin_db import is_admin
from flask import session
from dash.exceptions import PreventUpdate
from dash_apps.components.driver_validation_table import render_driver_validation_table

# ID du store pour rafraîchissement
refresh_store_id = "driver-validation-refresh"

# Helper de log standardisé (aligné avec Users/Trips)
def log_callback(name, inputs, states=None):
    try:
        import json as _json
        def _short(s):
            s = str(s)
            return f"{s[:4]}…{s[-4:]}" if len(s) > 14 else s
        def _clean(v):
            if isinstance(v, dict):
                out = {}
                for k, val in v.items():
                    if val in (None, ""):
                        continue
                    if isinstance(val, str) and val == "all":
                        continue
                    out[k] = _clean(val)
                return out
            if isinstance(v, list):
                return [_clean(x) for x in v if x not in (None, "")]
            if isinstance(v, str):
                return _short(v)
            return v
        ins = _clean(inputs)
        sts = _clean(states or {})
        sep = "=" * 74
        print("\n" + sep)
        print(f"[CB] {name}")
        print("Inputs:")
        for k, v in ins.items():
            try:
                msg = _json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
            except Exception:
                msg = str(v)
            print(f"  - {k}: {msg}")
        print("States:")
        for k, v in sts.items():
            try:
                msg = _json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
            except Exception:
                msg = str(v)
            print(f"  - {k}: {msg}")
        print(sep)
    except Exception:
        pass


# Layout principal de la page de validation des documents conducteur
def serve_layout():
    user_email = session.get('user_email', None)
    if not is_admin(user_email):
        return dbc.Container([
            html.H2("Accès refusé", style={"marginTop": "20px"}),
            dbc.Alert("Vous n'êtes pas autorisé à accéder à cette page.", color="danger")
        ], fluid=True)
    else:
        return dbc.Container([
            html.H2("Validation des documents conducteur", style={"marginTop": "20px"}),
            html.P("Cette page permet aux administrateurs de vérifier et valider les documents soumis par les conducteurs.", className="text-muted"),
            # Stores (session) pour persister état
            dcc.Store(id="driver-selected-uid", storage_type="session", data=None, clear_data=False),
            dcc.Store(id="driver-current-page-pending", storage_type="session", data=1),
            dcc.Store(id="driver-current-page-validated", storage_type="session", data=1),
            dcc.Store(id="driver-validation-refresh", storage_type="session", data=0),
            # En-tête
            dbc.Card([
                dbc.CardHeader(
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Documents en attente", href="#", id="tab1-link", active=True, className="fw-bold")),
                        dbc.NavItem(dbc.NavLink("Documents validés", href="#", id="tab2-link")),
                    ], pills=True, card=True, className="nav-justified"),
                ),
                dbc.CardBody([
                    html.Div(id="pending-documents-container", className="mt-2"),
                    html.Div(id="validated-documents-container", className="mt-2", style={"display": "none"}),
                ]),
            ], className="mt-3")
        ])

layout = serve_layout

# DEBUG - Chargement du module 06_driver_validation.py
print("[DEBUG] 06_driver_validation.py chargé")

# DEBUG - Layout défini
print("[DEBUG] Layout de la page driver_validation défini")

# Callbacks

@callback(
    Output("tab1-link", "active"),
    Output("tab2-link", "active"),
    Output("pending-documents-container", "style"),
    Output("validated-documents-container", "style"),
    Input("tab1-link", "n_clicks"),
    Input("tab2-link", "n_clicks"),
    prevent_initial_call=False
)
def switch_tabs(tab1_clicks, tab2_clicks):
    ctx = callback_context
    triggered = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else "tab1-link"
    tab1_active = triggered != "tab2-link"
    tab2_active = not tab1_active
    return tab1_active, tab2_active, ({"display": "block"} if tab1_active else {"display": "none"}), ({"display": "block"} if tab2_active else {"display": "none"})


@callback(
    Output("pending-documents-container", "children"),
    Input("driver-current-page-pending", "data"),
    Input("driver-selected-uid", "data"),
    Input("driver-validation-refresh", "data"),
    prevent_initial_call=False
)
def render_pending_table(current_page, selected_uid, _refresh):
    log_callback("render_pending_table", {"page": current_page, "selected_uid": selected_uid}, {})
    try:
        users = UserRepository.get_pending_drivers() or []
    except Exception:
        users = []
    total = len(users)
    page = current_page if isinstance(current_page, (int, float)) and current_page >= 1 else 1
    page_size =  UserRepository.__dict__.get("PAGE_SIZE_OVERRIDE", None) or 10
    # Align with Config.USERS_TABLE_PAGE_SIZE for consistency
    try:
        from dash_apps.config import Config as _Cfg
        page_size = getattr(_Cfg, "USERS_TABLE_PAGE_SIZE", page_size)
    except Exception:
        pass
    start = (page - 1) * page_size
    end = start + page_size
    page_users = users[start:end]
    return render_driver_validation_table(page_users, page, total, selected_uid=selected_uid, tab="pending")


@callback(
    Output("validated-documents-container", "children"),
    Input("driver-current-page-validated", "data"),
    Input("driver-selected-uid", "data"),
    Input("driver-validation-refresh", "data"),
    prevent_initial_call=False
)
def render_validated_table(current_page, selected_uid, _refresh):
    log_callback("render_validated_table", {"page": current_page, "selected_uid": selected_uid}, {})
    try:
        users = UserRepository.get_validated_drivers() or []
    except Exception:
        users = []
    total = len(users)
    page = current_page if isinstance(current_page, (int, float)) and current_page >= 1 else 1
    page_size =  UserRepository.__dict__.get("PAGE_SIZE_OVERRIDE", None) or 10
    try:
        from dash_apps.config import Config as _Cfg
        page_size = getattr(_Cfg, "USERS_TABLE_PAGE_SIZE", page_size)
    except Exception:
        pass
    start = (page - 1) * page_size
    end = start + page_size
    page_users = users[start:end]
    return render_driver_validation_table(page_users, page, total, selected_uid=selected_uid, tab="validated")


@callback(
    Output("driver-selected-uid", "data", allow_duplicate=True),
    Input({"type": "dv-select-pending", "index": dash.ALL}, "n_clicks"),
    Input({"type": "dv-select-validated", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def select_driver_from_row(pending_clicks, validated_clicks):
    ctx = callback_context
    log_callback("select_driver_from_row", {"pending_clicks": pending_clicks, "validated_clicks": validated_clicks}, {})
    if not ctx.triggered:
        raise PreventUpdate
    # Ignore initial zeros
    clicks = pending_clicks or []
    clicks2 = validated_clicks or []
    if (not any((c or 0) > 0 for c in clicks)) and (not any((c or 0) > 0 for c in clicks2)):
        raise PreventUpdate
    clicked_id = ctx.triggered[0]["prop_id"].split(".")[0]
    try:
        import json as _json
        id_dict = _json.loads(clicked_id)
        uid = id_dict.get("index")
        if uid is None:
            raise PreventUpdate
        return uid
    except Exception:
        raise PreventUpdate

