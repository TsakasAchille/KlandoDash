from dash import html, dcc, Input, Output, State, callback, callback_context
import dash
import json
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash_apps.config import Config
from dash_apps.repositories.repository_factory import RepositoryFactory


# Helper de log standardisé (aligné avec users/trips)
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


def render_driver_validation_table(users, current_page, total_count, selected_uid=None, tab="pending"):
    """Tableau custom pour la validation conducteur (pending ou validated)
    - users: liste d'utilisateurs (déjà paginée côté callback appelant)
    - current_page: 1-indexed
    - total_count: total items for the current tab
    - selected_uid: uid sélectionné
    - tab: "pending" ou "validated" (pour namespacer les IDs)
    """
    page_size = Config.USERS_TABLE_PAGE_SIZE
    page_count = (total_count - 1) // page_size + 1 if total_count > 0 else 1

    headers = ["", "Nom", "Email", "Profil", "Permis", "CNI", "Comparer", "Statut", "Action"]

    rows = []
    modals = []
    def _has_doc(x):
        """Return True only if x is a non-empty, non-placeholder URL/string.
        Handles cases where DB stores '', 'None', 'null', or None.
        """
        if x is None:
            return False
        if isinstance(x, str):
            s = x.strip().lower()
            if s in ("", "none", "null", "undefined", "na", "n/a"):
                return False
            return True
        return bool(x)

    for u in users:
        if hasattr(u, "model_dump"):
            d = u.model_dump()
        elif isinstance(u, dict):
            d = u
        else:
            # objet modèle
            d = {
                "uid": getattr(u, "uid", ""),
                "name": getattr(u, "name", ""),
                "email": getattr(u, "email", ""),
                "driver_license_url": getattr(u, "driver_license_url", None),
                "id_card_url": getattr(u, "id_card_url", None),
                "is_driver_doc_validated": getattr(u, "is_driver_doc_validated", False),
            }
        uid = d.get("uid")
        name = d.get("name") or d.get("display_name") or "-"
        email = d.get("email") or "-"
        driver_license = d.get("driver_license_url")
        id_card = d.get("id_card_url")
        is_validated = bool(d.get("is_driver_doc_validated"))

        is_selected = str(uid) == str(selected_uid) if selected_uid else False
        row_style = {
            "backgroundColor": "#ff3547 !important" if is_selected else "transparent",
            "transition": "all 0.2s",
            "cursor": "pointer",
            "border": "2px solid #dc3545 !important" if is_selected else "none",
            "color": "white !important" if is_selected else "inherit",
            "fontWeight": "bold !important" if is_selected else "normal",
        }
        cell_style = {"backgroundColor": "#ff3547 !important" if is_selected else "transparent"}
        row_id_obj = {"type": f"dv-row-{tab}", "index": uid}

        # Buttons IDs
        view_lic_id = {"type": f"dv-view-lic-{tab}", "index": uid}
        view_idc_id = {"type": f"dv-view-idc-{tab}", "index": uid}
        compare_id = {"type": f"dv-compare-{tab}", "index": uid}
        validate_id = {"type": f"dv-validate-{tab}", "index": uid}
        unvalidate_id = {"type": f"dv-unvalidate-{tab}", "index": uid}

        # Row
        rows.append(html.Tr([
            html.Td(
                dbc.Button(
                    children=html.I(className="fas fa-check"),
                    id={"type": f"dv-select-{tab}", "index": uid},
                    color="danger" if is_selected else "light",
                    outline=not is_selected,
                    size="sm",
                    style={"width": "30px", "height": "30px", "padding": "0px", "display": "flex", "alignItems": "center", "justifyContent": "center", "margin": "0 auto"}
                ),
                style={"width": "40px", "cursor": "pointer"}
            ),
            html.Td(name, style=cell_style),
            html.Td(email, style=cell_style),
            html.Td(
                dcc.Link(
                    dbc.Button("Voir profil", color="primary", size="sm"),
                    href=f"/users?uid={uid}",
                    refresh=False,
                ),
                style=cell_style
            ),
            html.Td(
                (
                    dbc.Button("Voir", id=view_lic_id, color="primary", size="sm", disabled=False)
                    if _has_doc(driver_license)
                    else dbc.Badge("Manquant", color="secondary", pill=True)
                ),
                style=cell_style
            ),
            html.Td(
                (
                    dbc.Button("Voir", id=view_idc_id, color="primary", size="sm", disabled=False)
                    if _has_doc(id_card)
                    else dbc.Badge("Manquant", color="secondary", pill=True)
                ),
                style=cell_style
            ),
            html.Td(
                dbc.Button(
                    "Comparer",
                    id=compare_id,
                    color="info",
                    size="sm",
                    disabled=not (_has_doc(driver_license) or _has_doc(id_card)),
                    title=(
                        "Au moins un document requis" if not (_has_doc(driver_license) or _has_doc(id_card)) else ""
                    ),
                ),
                style=cell_style
            ),
            html.Td("Validé" if is_validated else "En attente", style=cell_style),
            html.Td(
                dbc.Button(
                    "Dévalider" if is_validated else "Valider",
                    id=unvalidate_id if is_validated else validate_id,
                    color="danger" if is_validated else "success",
                    size="sm",
                    disabled=not (_has_doc(driver_license) or _has_doc(id_card)) and not is_validated,
                    title=(
                        "Au moins un document requis pour valider"
                        if (not is_validated and not (_has_doc(driver_license) or _has_doc(id_card))) else ""
                    ),
                ),
                style=cell_style
            ),
        ], id=row_id_obj, className="dv-row", style=row_style))

        # Modals for view and compare
        modals += [
            dbc.Modal([
                dbc.ModalHeader("Permis de conduire"),
                dbc.ModalBody(
                    html.Img(src=driver_license or "", style={"width": "100%"}) if driver_license else html.Div("Aucune image disponible", className="text-muted")
                ),
                dbc.ModalFooter(dbc.Button("Fermer", id={"type": f"dv-close-lic-{tab}", "index": uid}, className="ms-auto")),
            ], id={"type": f"dv-modal-lic-{tab}", "index": uid}, is_open=False, size="lg"),

            dbc.Modal([
                dbc.ModalHeader("Carte d'identité"),
                dbc.ModalBody(
                    html.Img(src=id_card or "", style={"width": "100%"}) if id_card else html.Div("Aucune image disponible", className="text-muted")
                ),
                dbc.ModalFooter(dbc.Button("Fermer", id={"type": f"dv-close-idc-{tab}", "index": uid}, className="ms-auto")),
            ], id={"type": f"dv-modal-idc-{tab}", "index": uid}, is_open=False, size="lg"),

            dbc.Modal([
                dbc.ModalHeader("Comparer les documents"),
                dbc.ModalBody(
                    dbc.Row([
                        dbc.Col([
                            html.H6("Permis de conduire"),
                            (html.Img(src=driver_license or "", style={"width": "100%", "border": "1px solid #ddd", "borderRadius": "8px"}) if driver_license else html.Div("Document non disponible", className="text-danger"))
                        ], width=6),
                        dbc.Col([
                            html.H6("Carte d'identité"),
                            (html.Img(src=id_card or "", style={"width": "100%", "border": "1px solid #ddd", "borderRadius": "8px"}) if id_card else html.Div("Document non disponible", className="text-danger"))
                        ], width=6)
                    ])
                ),
                dbc.ModalFooter(dbc.Button("Fermer", id={"type": f"dv-close-compare-{tab}", "index": uid}, className="ms-auto")),
            ], id={"type": f"dv-modal-compare-{tab}", "index": uid}, is_open=False, size="xl"),
        ]

    if not rows:
        rows = [html.Tr([html.Td("Aucun élément", colSpan=9)])]

    table = html.Table([
        html.Thead(
            html.Tr([html.Th(h) for h in headers]),
            style={"backgroundColor": "#f4f6f8", "color": "#3a4654", "fontWeight": "600", "textTransform": "uppercase", "letterSpacing": "0.5px"}
        ),
        html.Tbody(rows)
    ], className="table table-hover", style={"width": "100%", "marginBottom": "0", "backgroundColor": "white", "borderCollapse": "collapse"})

    pagination = html.Div([
        dbc.Button([html.I(className="fas fa-arrow-left mr-2"), "Précédent"], id=f"dv-prev-{tab}", color="primary", outline=False, disabled=current_page <= 1, style={"backgroundColor": "#4582ec", "borderColor": "#4582ec", "color": "white"}),
        html.Span(f"Page {current_page} sur {page_count} (Total: {total_count})", style={"margin": "0 15px", "lineHeight": "38px"}),
        dbc.Button(["Suivant", html.I(className="fas fa-arrow-right ml-2")], id=f"dv-next-{tab}", color="primary", outline=False, disabled=current_page >= page_count, style={"backgroundColor": "#4582ec", "borderColor": "#4582ec", "color": "white"})
    ], style={"marginTop": "20px", "textAlign": "center", "padding": "10px"})

    return html.Div([
        html.Div([
            html.H5("Documents conducteurs", style={"marginBottom": "15px", "color": "#3a4654", "fontWeight": "500", "fontSize": "18px"}),
            table
        ], style={"padding": "20px", "borderRadius": "6px", "backgroundColor": "white", "boxShadow": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)"}),
        pagination,
        # Attach modals
        html.Div(modals)
    ])


@callback(
    Output("driver-current-page-pending", "data", allow_duplicate=True),
    Input("dv-prev-pending", "n_clicks"),
    Input("dv-next-pending", "n_clicks"),
    State("driver-current-page-pending", "data"),
    prevent_initial_call=True
)
def dv_paginate_pending(prev_clicks, next_clicks, current_page):
    ctx = callback_context
    log_callback("dv_paginate_pending", {"prev": prev_clicks, "next": next_clicks}, {"page": current_page})
    if not ctx.triggered:
        raise PreventUpdate
    if (prev_clicks is None and next_clicks is None) or (prev_clicks == 0 and next_clicks == 0):
        raise PreventUpdate
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    try:
        page = int(current_page or 1)
    except Exception:
        page = 1
    if button_id == "dv-prev-pending":
        return max(1, page - 1)
    elif button_id == "dv-next-pending":
        return page + 1
    raise PreventUpdate


# ----------------------
# Validate / Unvalidate actions
# ----------------------

@callback(
    Output("driver-validation-refresh", "data", allow_duplicate=True),
    Input({"type": "dv-validate-pending", "index": dash.ALL}, "n_clicks"),
    State("driver-validation-refresh", "data"),
    prevent_initial_call=True
)
def on_validate_pending(clicks, refresh_val):
    ctx = callback_context
    clicks = clicks or []
    if not ctx.triggered or not any((c or 0) > 0 for c in clicks):
        raise PreventUpdate
    try:
        import json as _json
        tid = ctx.triggered[0]["prop_id"].split(".")[0]
        data = _json.loads(tid)
        uid = data.get("index")
        # Normalize UID to avoid hidden whitespace/mismatched types
        if uid is not None:
            try:
                uid_norm = str(uid).strip()
            except Exception:
                uid_norm = uid
            if uid_norm:
                user_repository = RepositoryFactory.get_user_repository()
                user_repository.validate_driver_documents(uid_norm)
        return (refresh_val or 0) + 1
    except Exception:
        return (refresh_val or 0) + 1


@callback(
    Output("driver-validation-refresh", "data", allow_duplicate=True),
    Input({"type": "dv-unvalidate-validated", "index": dash.ALL}, "n_clicks"),
    State("driver-validation-refresh", "data"),
    prevent_initial_call=True
)
def on_unvalidate_validated(clicks, refresh_val):
    ctx = callback_context
    clicks = clicks or []
    if not ctx.triggered or not any((c or 0) > 0 for c in clicks):
        raise PreventUpdate
    try:
        import json as _json
        tid = ctx.triggered[0]["prop_id"].split(".")[0]
        data = _json.loads(tid)
        uid = data.get("index")
        if uid is not None:
            try:
                uid_norm = str(uid).strip()
            except Exception:
                uid_norm = uid
            if uid_norm:
                user_repository = RepositoryFactory.get_user_repository()
                user_repository.unvalidate_driver_documents(uid_norm)
        return (refresh_val or 0) + 1
    except Exception:
        return (refresh_val or 0) + 1



# ----------------------
# Modals - Pending tab
# ----------------------

@callback(
    Output({"type": "dv-modal-lic-pending", "index": dash.MATCH}, "is_open"),
    Input({"type": "dv-view-lic-pending", "index": dash.MATCH}, "n_clicks"),
    Input({"type": "dv-close-lic-pending", "index": dash.MATCH}, "n_clicks"),
    State({"type": "dv-modal-lic-pending", "index": dash.MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_lic_modal_pending(open_clicks, close_clicks, is_open):
    if not open_clicks and not close_clicks:
        raise PreventUpdate
    return not bool(is_open)


@callback(
    Output({"type": "dv-modal-idc-pending", "index": dash.MATCH}, "is_open"),
    Input({"type": "dv-view-idc-pending", "index": dash.MATCH}, "n_clicks"),
    Input({"type": "dv-close-idc-pending", "index": dash.MATCH}, "n_clicks"),
    State({"type": "dv-modal-idc-pending", "index": dash.MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_idc_modal_pending(open_clicks, close_clicks, is_open):
    if not open_clicks and not close_clicks:
        raise PreventUpdate
    return not bool(is_open)


@callback(
    Output({"type": "dv-modal-compare-pending", "index": dash.MATCH}, "is_open"),
    Input({"type": "dv-compare-pending", "index": dash.MATCH}, "n_clicks"),
    Input({"type": "dv-close-compare-pending", "index": dash.MATCH}, "n_clicks"),
    State({"type": "dv-modal-compare-pending", "index": dash.MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_compare_modal_pending(open_clicks, close_clicks, is_open):
    if not open_clicks and not close_clicks:
        raise PreventUpdate
    return not bool(is_open)


# ----------------------
# Modals - Validated tab
# ----------------------

@callback(
    Output({"type": "dv-modal-lic-validated", "index": dash.MATCH}, "is_open"),
    Input({"type": "dv-view-lic-validated", "index": dash.MATCH}, "n_clicks"),
    Input({"type": "dv-close-lic-validated", "index": dash.MATCH}, "n_clicks"),
    State({"type": "dv-modal-lic-validated", "index": dash.MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_lic_modal_validated(open_clicks, close_clicks, is_open):
    if not open_clicks and not close_clicks:
        raise PreventUpdate
    return not bool(is_open)


@callback(
    Output({"type": "dv-modal-idc-validated", "index": dash.MATCH}, "is_open"),
    Input({"type": "dv-view-idc-validated", "index": dash.MATCH}, "n_clicks"),
    Input({"type": "dv-close-idc-validated", "index": dash.MATCH}, "n_clicks"),
    State({"type": "dv-modal-idc-validated", "index": dash.MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_idc_modal_validated(open_clicks, close_clicks, is_open):
    if not open_clicks and not close_clicks:
        raise PreventUpdate
    return not bool(is_open)


@callback(
    Output({"type": "dv-modal-compare-validated", "index": dash.MATCH}, "is_open"),
    Input({"type": "dv-compare-validated", "index": dash.MATCH}, "n_clicks"),
    Input({"type": "dv-close-compare-validated", "index": dash.MATCH}, "n_clicks"),
    State({"type": "dv-modal-compare-validated", "index": dash.MATCH}, "is_open"),
    prevent_initial_call=True
)
def toggle_compare_modal_validated(open_clicks, close_clicks, is_open):
    if not open_clicks and not close_clicks:
        raise PreventUpdate
    return not bool(is_open)
    if prev_clicks is None and next_clicks is None:
        raise PreventUpdate
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if not isinstance(current_page, (int, float)):
        current_page = 1
    if button_id == "dv-prev-pending":
        return max(1, current_page - 1)
    elif button_id == "dv-next-pending":
        return current_page + 1
    raise PreventUpdate


@callback(
    Output("driver-current-page-validated", "data", allow_duplicate=True),
    Input("dv-prev-validated", "n_clicks"),
    Input("dv-next-validated", "n_clicks"),
    State("driver-current-page-validated", "data"),
    prevent_initial_call=True
)
def dv_paginate_validated(prev_clicks, next_clicks, current_page):
    ctx = callback_context
    log_callback("dv_paginate_validated", {"prev": prev_clicks, "next": next_clicks}, {"page": current_page})
    if not ctx.triggered:
        raise PreventUpdate
    if prev_clicks is None and next_clicks is None:
        raise PreventUpdate
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if not isinstance(current_page, (int, float)):
        current_page = 1
    if button_id == "dv-prev-validated":
        return max(1, current_page - 1)
    elif button_id == "dv-next-validated":
        return current_page + 1
    raise PreventUpdate
