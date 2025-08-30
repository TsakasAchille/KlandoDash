from dash import html, dcc
import dash_bootstrap_components as dbc


def _short(text: str, n: int = 30) -> str:
    try:
        s = str(text) if text is not None else "-"
    except Exception:
        s = "-"
    return s if len(s) <= n else s[: n - 1] + "…"


def render_map_trips_table(trips, selected_ids=None, active_id=None):
    """Tableau compact pour la page Carte, listant les derniers trajets
    avec un bouton "Voir trajet" qui renvoie vers /trips?trip_id=<id>.
    """
    selected_ids = set(selected_ids or [])
    headers = ["", "#", "Départ", "Arrivée", "TripID", "Action"]

    rows = []
    for i, t in enumerate(trips, start=1):
        trip_id = getattr(t, "trip_id", "-") or "-"
        is_active = (str(trip_id) == str(active_id)) if active_id is not None else False
        dep = _short(getattr(t, "departure_name", "-") or "-")
        arr = _short(getattr(t, "destination_name", "-") or "-")
        link = dcc.Link(
            dbc.Button("Voir trajet", color="primary", size="sm"),
            href=f"/trips?trip_id={trip_id}",
            refresh=False,
        )
        rows.append(
            html.Tr([
                # Checkbox de sélection
                html.Td(
                    dbc.Checkbox(
                        id={"type": "map-trip-check", "index": str(trip_id)},
                        value=str(trip_id) in selected_ids,
                    ),
                    style={"width": "32px", "textAlign": "center"}
                ),
                html.Td(i),
                html.Td(dep),
                html.Td(arr),
                html.Td(str(trip_id)),
                html.Td(link),
            ], className=("table-active" if is_active else None))
        )

    if not rows:
        rows = [html.Tr([html.Td("Aucun trajet", colSpan=6)])]

    table = html.Table(
        [
            html.Thead(
                html.Tr([html.Th(h) for h in headers]),
                style={
                    "backgroundColor": "#f4f6f8",
                    "color": "#3a4654",
                    "fontWeight": "600",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.5px",
                },
            ),
            html.Tbody(rows),
        ],
        className="table table-hover",
        style={
            "width": "100%",
            "marginBottom": "0",
            "backgroundColor": "white",
            "borderCollapse": "collapse",
        },
    )

    return html.Div(
        [
            html.H5(
                "Derniers trajets",
                style={
                    "marginBottom": "12px",
                    "color": "#3a4654",
                    "fontWeight": "500",
                    "fontSize": "16px",
                },
            ),
            table,
        ],
        style={
            "padding": "16px",
            "borderRadius": "6px",
            "backgroundColor": "white",
            "boxShadow": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
        },
    )
