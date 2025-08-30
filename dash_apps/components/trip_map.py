import dash_leaflet as dl
from dash import html
import polyline
from statistics import mean

# Couleurs KLANDO
KLANDO_PRIMARY = "#4281ec"
KLANDO_RED = "#e63946"
KLANDO_BLUEGREY = "#3a4654"


def render_trip_map(trip_row):
    """
    Affiche une carte Leaflet du trajet à partir de la polyline.
    Args:
        trip_row: Series ou dict contenant au moins 'polyline', 'departure_name', 'destination_name'
    """
    if trip_row is None:
        return None
        
    # Convertir le DataFrame row en dictionnaire si ce n'est pas déjà fait
    if hasattr(trip_row, 'to_dict'):
        trip_dict = trip_row.to_dict()
    else:
        trip_dict = dict(trip_row)
    
    # Si polyline présente et non vide, affiche le trajet complet
    if 'polyline' in trip_dict and trip_dict['polyline']:
        try:
            # Décoder la polyline
            polyline_str = trip_dict['polyline']
            if isinstance(polyline_str, bytes):
                polyline_str = polyline_str.decode('utf-8')

            coords = polyline.decode(polyline_str)  # [(lat, lon), ...]
            print(f"[DEBUG] Polyline décodée. Longueur: {len(coords)} points")

            if not coords or len(coords) < 2:
                raise ValueError("Polyline trop courte")

            line_positions = coords
            departure = coords[0]
            arrival = coords[-1]
            departure_name = trip_dict.get('departure_name', 'Départ')
            arrival_name = trip_dict.get('destination_name', 'Arrivée')
            center = coords[len(coords)//2]

            # Utiliser directement le composant Leaflet de Dash avec un style moderne
            return html.Div([
                html.Div(
                    className="card-header",
                    children=[
                        html.Div(
                            className="header-icon",
                            children="🗺️"
                        ),
                        html.H2("Trajet sur la carte", className="card-title", style={
                            "fontSize": "22px",
                            "fontWeight": "600",
                            "color": "#333",
                            "margin": "0",
                            "marginLeft": "15px"
                        })
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "marginBottom": "20px",
                    }
                ),
                html.Div(
                    dl.Map([
                        dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
                                    attribution='&copy; OpenStreetMap & CARTO'),
                        dl.Polyline(positions=line_positions, color=KLANDO_PRIMARY, weight=5, opacity=0.85),
                        dl.Marker(position=departure, children=[dl.Tooltip(f"Départ: {departure_name}")]),
                        dl.Marker(position=arrival, children=[dl.Tooltip(f"Arrivée: {arrival_name}")]),
                    ], center=center, zoom=12, style={
                        'height': '500px',
                        'width': '100%',
                        'borderRadius': '18px',
                        'overflow': 'hidden'
                    }),
                    style={
                        "backgroundColor": "#fafcfe",
                        "borderRadius": "18px",
                        "padding": "10px",
                    }
                )
            ], style={
                "backgroundColor": "white",
                "borderRadius": "28px",
                "boxShadow": "rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px",
                "padding": "25px",
                "overflow": "hidden",
                "marginBottom": "20px"
            })
        except Exception:
            return html.Div("Impossible d'afficher la carte du trajet")
    
    # Fallback si pas de polyline
    return html.Div("Aucune polyline disponible pour ce trajet")

def render_trips_map(trips_df, max_trips=10, show_heat=True, height="600px"):
    """
    Affiche une carte avec les X derniers trajets (polylines si disponibles) et une couche de bulles de densité.
    Args:
        trips_df: DataFrame de trajets
        max_trips: nombre maximum de trajets à afficher
        show_heat: afficher une couche bulles (agrégation des destinations)
        height: hauteur CSS de la carte
    Returns:
        Composant Dash (html.Div) contenant une dl.Map
    """
    try:
        if trips_df is None or getattr(trips_df, 'empty', True):
            return html.Div("Aucune donnée de trajet disponible")

        df = trips_df.copy()
        # Trier par date si dispo pour prendre les derniers
        sort_col = None
        for c in ["departure_date", "created_at", "date"]:
            if c in df.columns:
                sort_col = c
                break
        if sort_col:
            df = df.sort_values(sort_col, ascending=False)
        df = df.head(max_trips)

        layers = []
        centers = []

        # Fond de carte
        layers.append(dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
                                   attribution='&copy; OpenStreetMap & CARTO'))

        # Polylines ou fallback lignes droites
        for _, row in df.iterrows():
            try:
                if row.get('polyline'):
                    p = row['polyline']
                    if isinstance(p, bytes):
                        p = p.decode('utf-8')
                    coords = polyline.decode(p)
                    if len(coords) >= 2:
                        layers.append(dl.Polyline(positions=coords, color=KLANDO_PRIMARY, weight=4, opacity=0.75))
                        centers.extend(coords[:: max(1, len(coords)//5)])
                        # marqueurs départ/arrivée (discrets)
                        layers.append(dl.CircleMarker(center=coords[0], radius=3, color="#2ecc71", fill=True, fillOpacity=1))
                        layers.append(dl.CircleMarker(center=coords[-1], radius=3, color="#e67e22", fill=True, fillOpacity=1))
                        continue
            except Exception:
                pass

            # Fallback si pas de polyline
            try:
                lat1 = float(row.get('departure_latitude'))
                lon1 = float(row.get('departure_longitude'))
                lat2 = float(row.get('destination_latitude'))
                lon2 = float(row.get('destination_longitude'))
                seg = [(lat1, lon1), (lat2, lon2)]
                layers.append(dl.Polyline(positions=seg, color=KLANDO_RED, weight=3, opacity=0.6, dashArray="8,6"))
                centers.extend(seg)
                layers.append(dl.CircleMarker(center=seg[0], radius=3, color="#2ecc71", fill=True, fillOpacity=1))
                layers.append(dl.CircleMarker(center=seg[1], radius=3, color="#e67e22", fill=True, fillOpacity=1))
            except Exception:
                continue

        # Couche bulles agrégée sur destinations
        if show_heat and 'destination_latitude' in df.columns and 'destination_longitude' in df.columns:
            try:
                agg = df.groupby(['destination_latitude', 'destination_longitude']).size().reset_index(name='count')
                # Normaliser rayon
                max_count = agg['count'].max() if not agg.empty else 1
                for _, r in agg.iterrows():
                    radius = 4 + 10 * (r['count'] / max_count)
                    layers.append(
                        dl.CircleMarker(
                            center=(float(r['destination_latitude']), float(r['destination_longitude'])),
                            radius=radius,
                            color="#d62728",
                            fill=True,
                            fillOpacity=0.35,
                            children=[dl.Tooltip(f"Trajets: {int(r['count'])}")]
                        )
                    )
            except Exception:
                pass

        # Centre de la carte
        if centers:
            clat = mean([c[0] for c in centers])
            clon = mean([c[1] for c in centers])
            center = (clat, clon)
        else:
            center = (0, 0)

        return html.Div(
            dl.Map(layers, center=center, zoom=8, style={'height': height, 'width': '100%', 'borderRadius': '18px', 'overflow': 'hidden'}),
            style={
                "backgroundColor": "white",
                "borderRadius": "28px",
                "boxShadow": "rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px",
                "padding": "10px",
                "overflow": "hidden",
            }
        )
    except Exception:
        return html.Div("Impossible d'afficher la carte multi-trajets")