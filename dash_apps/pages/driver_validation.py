import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash
from dash_apps.repositories.repository_factory import RepositoryFactory

# L'enregistrement se fera dans app_factory après la création de l'app
from dash_apps.utils.admin_db_rest import is_admin
from flask import session
from dash.exceptions import PreventUpdate
from dash_apps.components.driver_validation_table import render_driver_validation_table
from urllib.parse import parse_qs

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
    try:
        is_admin_flag = bool(is_admin(user_email) or session.get('is_admin', False))
    except Exception:
        is_admin_flag = bool(session.get('is_admin', False))
    if not is_admin_flag:
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
            dcc.Store(id="driver-tab-pref", storage_type="session", data="pending"),
            dcc.Store(id="driver-go-to", storage_type="session", data=None),
            dcc.Location(id="driver-validation-url", refresh=False),
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
    Input("driver-tab-pref", "data"),
    prevent_initial_call=False
)
def switch_tabs(tab1_clicks, tab2_clicks, tab_pref):
    ctx = callback_context
    triggered = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else "tab1-link"
    tab_pref = (tab_pref or "pending")
    if triggered == "tab2-link" or (triggered == "driver-tab-pref" and tab_pref == "validated"):
        tab1_active = False
        tab2_active = True
    else:
        tab1_active = True
        tab2_active = False
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
    page = int(current_page) if isinstance(current_page, (int, float)) and current_page >= 1 else 1
    page_size = 10  # Default page size
    try:
        from dash_apps.config import Config as _Cfg
        page_size = getattr(_Cfg, "USERS_TABLE_PAGE_SIZE", page_size)
    except Exception:
        pass
    # Use repository factory with driver_validation filter (not_validated)
    try:
        user_repository = RepositoryFactory.get_user_repository()
        data = user_repository.get_users_paginated(page=page-1, page_size=page_size, filters={"driver_validation": "not_validated"})
        page_users = data.get("users", [])
        total = data.get("total_count", 0)
    except Exception:
        page_users, total = [], 0
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
    page = int(current_page) if isinstance(current_page, (int, float)) and current_page >= 1 else 1
    page_size = 10  # Default page size
    try:
        from dash_apps.config import Config as _Cfg
        page_size = getattr(_Cfg, "USERS_TABLE_PAGE_SIZE", page_size)
    except Exception:
        pass
    # Use repository factory with driver_validation filter (validated)
    try:
        user_repository = RepositoryFactory.get_user_repository()
        data = user_repository.get_users_paginated(page=page-1, page_size=page_size, filters={"driver_validation": "validated"})
        page_users = data.get("users", [])
        total = data.get("total_count", 0)
    except Exception:
        page_users, total = [], 0
    return render_driver_validation_table(page_users, page, total, selected_uid=selected_uid, tab="validated")


@callback(
    Output("driver-selected-uid", "data", allow_duplicate=True),
    Output("driver-tab-pref", "data"),
    Output("driver-go-to", "data"),
    Input("driver-validation-url", "search"),
    prevent_initial_call="initial_duplicate"
)
def bootstrap_from_url(search):
    """Parse URL (?uid=&tab=) to preselect driver and compute proper page per tab."""
    try:
        q = parse_qs((search or "").lstrip("?")) if search else {}
        uid = (q.get("uid", [None]) or [None])[0]
        tab = (q.get("tab", [None]) or [None])[0]
        if tab not in ("pending", "validated"):
            tab = None
        # Default outputs
        sel_out = dash.no_update
        tab_out = dash.no_update
        goto_out = dash.no_update

        # Always set a default tab if none specified
        if tab is None:
            tab_out = "pending"
        else:
            tab_out = tab

        # If we have uid and a valid tab, compute page where user lies (DB-consistent)
        if uid and tab:
            try:
                page_size = 10  # Default page size
                try:
                    from dash_apps.config import Config as _Cfg
                    page_size = getattr(_Cfg, "USERS_TABLE_PAGE_SIZE", page_size)
                except Exception:
                    pass
                user_repository = RepositoryFactory.get_user_repository()
                idx = user_repository.get_user_position_in_validation_group(uid, "validated" if tab == "validated" else "pending")
                if isinstance(idx, int) and idx >= 0:
                    page = (idx // page_size) + 1
                    goto_out = {"tab": tab, "page": page}
                sel_out = uid
            except Exception:
                pass
        return sel_out, tab_out, goto_out
    except Exception:
        # Fallback safe
        return dash.no_update, "pending", dash.no_update

@callback(
    Output("driver-current-page-pending", "data", allow_duplicate=True),
    Output("driver-current-page-validated", "data", allow_duplicate=True),
    Input("driver-go-to", "data"),
    prevent_initial_call=True
)
def apply_goto(goto):
    if not goto or not isinstance(goto, dict):
        raise PreventUpdate
    tab = goto.get("tab")
    page = goto.get("page")
    if not page or not isinstance(page, (int, float)):
        raise PreventUpdate
    if tab == "pending":
        return int(page), dash.no_update
    elif tab == "validated":
        return dash.no_update, int(page)
    raise PreventUpdate

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

