import dash_leaflet as dl
from dash import html
import dash_bootstrap_components as dbc
import polyline

# Couleurs KLANDO
KLANDO_RED = "#730200"
KLANDO_BLUEGREY = "#3a4654"


def render_trip_map(trip_row):
    """
    Affiche une carte Leaflet du trajet à partir de la polyline.
    Args:
        trip_row: Series ou dict contenant au moins 'trip_polyline', 'departure_name', 'destination_name'
    """
    if trip_row is None:
        return None
    # Si polyline présente et non vide, affiche le trajet complet
    if 'trip_polyline' in trip_row and trip_row['trip_polyline']:
        try:
            coords = polyline.decode(trip_row['trip_polyline'])  # [(lat, lon), ...]
            if not coords:
                raise ValueError("Décodage polyline vide")
            line_positions = coords
            departure = coords[0]
            arrival = coords[-1]
            departure_name = trip_row.get('departure_name', 'Départ')
            arrival_name = trip_row.get('destination_name', 'Arrivée')
            center = coords[len(coords)//2]
            return dbc.Card([
                dbc.CardHeader("Trajet sur la carte", className="klando-card-header"),
                dbc.CardBody([
                    dl.Map([
                        dl.TileLayer(),
                        dl.Polyline(positions=line_positions, color=KLANDO_RED, weight=5),
                        dl.Marker(position=departure, children=[dl.Tooltip(f"Départ: {departure_name}")]),
                        dl.Marker(position=arrival, children=[dl.Tooltip(f"Arrivée: {arrival_name}")]),
                    ], center=center, zoom=11, className="klando-map-card")
                ], className="klando-card-body")
            ], className="klando-card")
        except Exception as e:
            print(f"[render_trip_map] Erreur décodage polyline: {e}")
            # On tombe sur le fallback ligne droite
    # Fallback : ligne droite entre départ et arrivée
    try:
        lat1 = float(trip_row.get('departure_latitude'))
        lon1 = float(trip_row.get('departure_longitude'))
        lat2 = float(trip_row.get('destination_latitude'))
        lon2 = float(trip_row.get('destination_longitude'))
        departure = (lat1, lon1)
        arrival = (lat2, lon2)
        departure_name = trip_row.get('departure_name', 'Départ')
        arrival_name = trip_row.get('destination_name', 'Arrivée')
        center = ((lat1+lat2)/2, (lon1+lon2)/2)
        return dbc.Card([
            dbc.CardHeader("Trajet sur la carte", className="klando-card-header"),
            dbc.CardBody([
                dl.Map([
                    dl.TileLayer(),
                    dl.Polyline(positions=[departure, arrival], color=KLANDO_RED, weight=5, dashArray="10,10"),
                    dl.Marker(position=departure, children=[dl.Tooltip(f"Départ: {departure_name}")]),
                    dl.Marker(position=arrival, children=[dl.Tooltip(f"Arrivée: {arrival_name}")]),
                ], center=center, zoom=9, className="klando-map-card"),
                html.Div("Aucune polyline disponible : affichage d'une ligne droite entre départ et arrivée.", style={"color": "#B00", "fontSize": "12px", "marginTop": "6px"})
            ], className="klando-card-body")
        ], className="klando-card")
    except Exception as e:
        return dbc.Card([
            dbc.CardHeader("Trajet sur la carte", className="klando-card-header"),
            dbc.CardBody([
                html.Div("Impossible d'afficher la carte (pas de coordonnées valides)", style={"color": "#B00"})
            ], className="klando-card-body")
        ], className="klando-card")