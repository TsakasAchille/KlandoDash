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
    headers = ["", "#", "Départ", "Arrivée", "Date", "TripID", "Action"]

    rows = []
    for i, t in enumerate(trips, start=1):
        # Support both dict and object formats
        if isinstance(t, dict):
            trip_id = t.get("trip_id", "-") or "-"
            dep_raw = t.get("departure_name", "-") or "-"
            arr_raw = t.get("destination_name", "-") or "-"
            created_at = t.get("created_at", "-") or "-"
        else:
            trip_id = getattr(t, "trip_id", "-") or "-"
            dep_raw = getattr(t, "departure_name", "-") or "-"
            arr_raw = getattr(t, "destination_name", "-") or "-"
            created_at = getattr(t, "created_at", "-") or "-"

        is_active = (str(trip_id) == str(active_id)) if active_id is not None else False
        dep = _short(dep_raw)
        arr = _short(arr_raw)
        
        # Format date
        try:
            if hasattr(created_at, 'strftime'):
                date_str = created_at.strftime("%d/%m/%Y")
            elif isinstance(created_at, str) and created_at != "-":
                from datetime import datetime
                # Try to parse ISO format
                if 'T' in created_at:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_str = dt.strftime("%d/%m/%Y")
                else:
                    date_str = created_at[:10]  # Take first 10 chars if already formatted
            else:
                date_str = "-"
        except Exception:
            date_str = "-"
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
                html.Td(date_str),
                html.Td(str(trip_id)),
                html.Td(link),
            ], className=("table-active" if is_active else None))
        )

    if not rows:
        rows = [html.Tr([html.Td("Aucun trajet", colSpan=7)])]

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
