from dash import html
import dash_bootstrap_components as dbc

def render_trip_stats(trip_row):
    """
    Affiche les stats principales du trajet (financier, occupation, etc.)
    """
    if trip_row is None:
        return None
    # Extraction des infos
    price = trip_row.get("price_per_seat", "-")
    total_seats = trip_row.get("number_of_seats", "-")
    available_seats = trip_row.get("available_seats", "-")
    passenger_count = trip_row.get("passenger_count", "-")
    # Bloc stats
    stats = [
        ("Prix par place", f"{price} €" if price != "-" else "-"),
        ("Nombre de places", total_seats),
        ("Places disponibles", available_seats),
        ("Réservations", passenger_count),
    ]
    return html.Ul([
        html.Li([
            html.Span(label + " : ", className="klando-label"),
            html.Span(str(value), className="klando-value")
        ], style={"marginBottom": "2px", "fontSize": "1.15em"})
        for label, value in stats
    ], style={"listStyle": "none", "padding": 0, "margin": 0})
