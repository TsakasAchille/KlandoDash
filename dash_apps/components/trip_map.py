from dash import html
import polyline
import json
from dash_apps.config import Config

# Couleurs KLANDO
KLANDO_PRIMARY = "#4281ec"
KLANDO_RED = "#e63946"
KLANDO_BLUEGREY = "#3a4654"


def render_trip_map(trip_row):
    """
    Affiche le trajet via la même carte MapLibre que 00_map.
    Construit un container MapLibre + un GeoJSON (FeatureCollection) pour le trajet.
    Args:
        trip_row: Series ou dict contenant au moins 'polyline' OU les coords de départ/arrivée.
    """
    if trip_row is None:
        return None
        
    # Convertir le DataFrame row en dictionnaire si ce n'est pas déjà fait
    if hasattr(trip_row, 'to_dict'):
        trip_dict = trip_row.to_dict()
    else:
        trip_dict = dict(trip_row)
    
    # Construire le GeoJSON pour MapLibre
    def build_geojson_from_trip(trip: dict):
        color = KLANDO_PRIMARY
        features = []
        # Essayer via polyline
        coords_ll = []  # (lat, lon)
        if trip.get('polyline'):
            try:
                polyline_str = trip['polyline']
                if isinstance(polyline_str, bytes):
                    polyline_str = polyline_str.decode('utf-8')
                coords_ll = polyline.decode(polyline_str)
            except Exception:
                coords_ll = []

        # Fallback via points départ/arrivée
        if not coords_ll:
            try:
                lat1 = float(trip.get('departure_latitude'))
                lon1 = float(trip.get('departure_longitude'))
                lat2 = float(trip.get('destination_latitude'))
                lon2 = float(trip.get('destination_longitude'))
                coords_ll = [(lat1, lon1), (lat2, lon2)]
            except Exception:
                coords_ll = []

        if len(coords_ll) >= 2:
            # Convertir en [lon, lat] pour GeoJSON
            line_coords = [[lng, lat] for (lat, lng) in coords_ll]
            features.append({
                "type": "Feature",
                "properties": {
                    "trip_id": trip_dict.get('trip_id'),
                    "color": color
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": line_coords
                }
            })
            # Points départ/arrivée pour visibilité
            start = line_coords[0]
            end = line_coords[-1]
            features.append({
                "type": "Feature",
                "properties": {"role": "start", "color": color},
                "geometry": {"type": "Point", "coordinates": start}
            })
            features.append({
                "type": "Feature",
                "properties": {"role": "end", "color": color},
                "geometry": {"type": "Point", "coordinates": end}
            })

        if not features:
            return None
        return {"type": "FeatureCollection", "features": features}

    gj = build_geojson_from_trip(trip_dict)
    if not gj:
        return html.Div("Impossible d'afficher la carte du trajet")

    # Container MapLibre unifié (même que 00_map)
    style_url = Config.MAPLIBRE_STYLE_URL or "https://demotiles.maplibre.org/globe.json"
    api_key = Config.MAPLIBRE_API_KEY or ""

    # Container pour la carte
    map_inner = html.Div(
        id="trip-maplibre-container",
        className="maplibre-container",
        **{
            "data-style-url": style_url,
            "data-api-key": api_key,
            "data-geojson": json.dumps(gj),
        },
        style={
            'height': '500px',
            'width': '100%',
            'borderRadius': '18px',
            'overflow': 'hidden'
        }
    )
    
    # Container externe avec style unifié
    map_container = html.Div(
        map_inner,
        style={
            'backgroundColor': 'white',
            'borderRadius': '28px',
            'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
            'padding': '15px',
            'overflow': 'hidden',
            'marginBottom': '20px'
        }
    )

    return html.Div([
     
        html.Div(
            map_container,
            style={
                "backgroundColor": "#fafcfe",
                "borderRadius": "18px",
                "padding": "10px",
            }
        )
    ]
  
    
    )

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