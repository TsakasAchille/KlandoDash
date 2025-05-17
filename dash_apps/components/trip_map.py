import dash_leaflet as dl
from dash import html
import dash_bootstrap_components as dbc
import polyline
import jinja2
import os

# Couleurs KLANDO
KLANDO_PRIMARY = "#4281ec"
KLANDO_RED = "#e63946"
KLANDO_BLUEGREY = "#3a4654"


def render_trip_map(trip_row):
    """
    Affiche une carte Leaflet du trajet à partir de la polyline.
    Args:
        trip_row: Series ou dict contenant au moins 'trip_polyline', 'departure_name', 'destination_name'
    """
    if trip_row is None:
        return None
        
    # Convertir le DataFrame row en dictionnaire si ce n'est pas déjà fait
    if hasattr(trip_row, 'to_dict'):
        trip_dict = trip_row.to_dict()
    else:
        trip_dict = dict(trip_row)
    
    # Si polyline présente et non vide, affiche le trajet complet
    try:
        if 'trip_polyline' in trip_dict and trip_dict['trip_polyline']:
            # Décoder la polyline
            polyline_str = trip_dict['trip_polyline']
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
                        # Style de carte plus épuré et moderne (CartoDB Positron)
                        #dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
                                   # attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'),
                        
                        # Autres styles de cartes modernes disponibles en commentaire:
                        # Style Voyager (élegant avec plus de détails)
                        dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
                                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'),
                        
                        # Style Dark Matter (mode sombre)
                        # dl.TileLayer(url='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                        #            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'),
                        dl.Polyline(positions=line_positions, color=KLANDO_PRIMARY, weight=5, opacity=0.85),
                        # Marqueurs personnalisés
                        dl.Marker(position=departure, children=[dl.Tooltip(f"Départ: {departure_name}")], 
                                icon=dict(iconUrl='', iconSize=[18, 18], className='custom-div-icon', 
                                        html=f'<div style="background-color:{KLANDO_PRIMARY}; width:12px; height:12px; border-radius:50%; border:3px solid white; box-shadow:0 0 5px rgba(0,0,0,0.2);"></div>')),
                        dl.Marker(position=arrival, children=[dl.Tooltip(f"Arrivée: {arrival_name}")], 
                                icon=dict(iconUrl='', iconSize=[18, 18], className='custom-div-icon', 
                                        html=f'<div style="background-color:{KLANDO_RED}; width:12px; height:12px; border-radius:50%; border:3px solid white; box-shadow:0 0 5px rgba(0,0,0,0.2);"></div>')),
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
    
    except Exception as e:
        print(f"[render_trip_map] Erreur décodage polyline: {e}")
    
    # Fallback : ligne droite entre départ et arrivée
    try:
        lat1 = float(trip_dict.get('departure_latitude'))
        lon1 = float(trip_dict.get('departure_longitude'))
        lat2 = float(trip_dict.get('destination_latitude'))
        lon2 = float(trip_dict.get('destination_longitude'))
        
        departure = (lat1, lon1)
        arrival = (lat2, lon2)
        departure_name = trip_dict.get('departure_name', 'Départ')
        arrival_name = trip_dict.get('destination_name', 'Arrivée')
        center = ((lat1+lat2)/2, (lon1+lon2)/2)
        
        return html.Div([
            html.Div(
                className="card-header",
                children=[
                    html.Div(
                        className="header-icon",
                        children=html.I(className="fas fa-map-marked-alt", style={"color": "#4281ec"})
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
                [
                    dl.Map([
                        dl.TileLayer(),
                        dl.Polyline(positions=[departure, arrival], color=KLANDO_RED, weight=5, dashArray="10,10", opacity=0.8),
                        dl.Marker(position=departure, children=[dl.Tooltip(f"Départ: {departure_name}")]),
                        dl.Marker(position=arrival, children=[dl.Tooltip(f"Arrivée: {arrival_name}")]),
                    ], center=center, zoom=10, style={
                        'height': '500px', 
                        'width': '100%',
                        'borderRadius': '18px',
                        'overflow': 'hidden'
                    }),
                    html.Div("Aucune polyline disponible : affichage d'une ligne droite.", 
                             style={"color": "#B00", "fontSize": "12px", "marginTop": "10px", "textAlign": "center"})
                ],
                style={
                    "backgroundColor": "#fafcfe",
                    "borderRadius": "18px",
                    "padding": "10px",
                }
            )
        ], style={
            "backgroundColor": "white",
            "borderRadius": "28px",
            "boxShadow": "0 10px 30px rgba(0,0,0,0.1)",
            "padding": "25px",
            "overflow": "hidden",
            "marginBottom": "20px"
        })
        
    except Exception as e:
        return html.Div([
            html.Div(
                className="card-header",
                children=[
                    html.Div(
                        className="header-icon",
                        children="⚠️"
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
                html.Div("Impossible d'afficher la carte (pas de coordonnées valides)", 
                         style={"color": "#B00", "padding": "30px", "textAlign": "center", "fontSize": "16px"}),
                style={
                    "backgroundColor": "#fafcfe",
                    "borderRadius": "18px",
                    "padding": "10px",
                }
            )
        ], style={
            "backgroundColor": "white",
            "borderRadius": "28px",
            "boxShadow": "0 10px 30px rgba(0,0,0,0.1)",
            "padding": "25px",
            "overflow": "hidden",
            "marginBottom": "20px"
        })