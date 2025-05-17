from dash import html
import dash_bootstrap_components as dbc
from jinja2 import Environment, FileSystemLoader
import pandas as pd
from pathlib import Path
import json


def render_stats_geographic(trips_data):
    """
    Rend les statistiques géographiques des trajets en utilisant un template Jinja2
    
    Args:
        trips_data: Données des trajets sous forme de liste de dictionnaires
    
    Returns:
        Un composant Dash pour afficher les statistiques géographiques
    """
    if not trips_data:
        return dbc.Alert("Aucune donnée de trajet disponible", color="warning")
    
    # Préparer le template Jinja2
    templates_folder = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(templates_folder))
    template = env.get_template("stats_geographic_template.jinja2")
    
    # Convertir en DataFrame
    trips_df = pd.DataFrame(trips_data)
    
    # Vérifier si les colonnes géographiques sont disponibles
    has_geo_data = all(col in trips_df.columns for col in ['departure_name', 'destination_name'])
    
    if not has_geo_data:
        return dbc.Alert("Données géographiques insuffisantes pour l'analyse", color="warning")
    
    # Calculer les métriques géographiques
    unique_departures = trips_df['departure_name'].nunique() if 'departure_name' in trips_df.columns else 0
    unique_destinations = trips_df['destination_name'].nunique() if 'destination_name' in trips_df.columns else 0
    
    # Distance moyenne
    avg_distance = 0
    if 'trip_distance' in trips_df.columns and not trips_df['trip_distance'].empty:
        # Filtrer les valeurs NaN/None
        clean_df = trips_df.dropna(subset=['trip_distance'])
        if len(clean_df) > 0:
            avg_distance = round(clean_df['trip_distance'].mean(), 1)
    
    # Top lieux de départ
    top_departures = []
    if 'departure_name' in trips_df.columns:
        departure_counts = trips_df['departure_name'].value_counts().nlargest(10).reset_index()
        departure_counts.columns = ['name', 'count']
        top_departures = departure_counts.to_dict('records')
    
    # Top destinations
    top_destinations = []
    if 'destination_name' in trips_df.columns:
        dest_counts = trips_df['destination_name'].value_counts().nlargest(10).reset_index()
        dest_counts.columns = ['name', 'count']
        top_destinations = dest_counts.to_dict('records')
    
    # Top routes
    top_routes = []
    popular_route_count = 0
    if all(col in trips_df.columns for col in ['departure_name', 'destination_name']):
        # Créer une colonne pour la route
        trips_df['route'] = trips_df['departure_name'] + ' → ' + trips_df['destination_name']
        route_counts = trips_df['route'].value_counts().nlargest(10).reset_index()
        route_counts.columns = ['route', 'count']
        top_routes = route_counts.to_dict('records')
        
        if len(route_counts) > 0:
            popular_route_count = route_counts.iloc[0]['count']
    
    # Préparer les données pour la carte géographique
    map_points = []
    
    # Vérifier si les données géographiques sont disponibles
    geo_cols_origin = all(col in trips_df.columns for col in ['departure_name', 'departure_lat', 'departure_lng'])
    geo_cols_dest = all(col in trips_df.columns for col in ['destination_name', 'destination_lat', 'destination_lng'])
    
    if geo_cols_origin or geo_cols_dest:
        # Points d'origine (départs)
        if geo_cols_origin:
            # Calculer les nombres de trajets par point de départ
            origin_counts = trips_df.groupby(['departure_name', 'departure_lat', 'departure_lng']).size().reset_index()
            origin_counts.columns = ['name', 'lat', 'lng', 'count']
            
            # Ajouter le type "origin" pour distinguer départ/destination sur la carte
            origin_points = [{
                'name': row['name'],
                'lat': row['lat'],
                'lng': row['lng'],
                'count': int(row['count']),
                'type': 'origin'
            } for _, row in origin_counts.iterrows() if pd.notna(row['lat']) and pd.notna(row['lng'])]
            
            map_points.extend(origin_points)
        
        # Points de destination
        if geo_cols_dest:
            # Calculer les nombres de trajets par destination
            dest_counts = trips_df.groupby(['destination_name', 'destination_lat', 'destination_lng']).size().reset_index()
            dest_counts.columns = ['name', 'lat', 'lng', 'count']
            
            # Ajouter le type "destination" pour distinguer sur la carte
            dest_points = [{
                'name': row['name'],
                'lat': row['lat'],
                'lng': row['lng'],
                'count': int(row['count']),
                'type': 'destination'
            } for _, row in dest_counts.iterrows() if pd.notna(row['lat']) and pd.notna(row['lng'])]
            
            map_points.extend(dest_points)
    
    # Si pas de coordonnées, essayons de géocoder les noms de lieux
    elif all(col in trips_df.columns for col in ['departure_name', 'destination_name']):
        # Utiliser des coordonnées approximatives basées sur le nom de ville/lieu
        # Ceci est une version simplifiée - normalement on utiliserait une API de géocodage
        from collections import defaultdict
        
        # Compter les occurrences de chaque lieu
        all_places = defaultdict(int)
        
        # Compter les occurrences de départs
        for name, count in trips_df['departure_name'].value_counts().items():
            all_places[name] += count
            
        # Compter les occurrences de destinations
        for name, count in trips_df['destination_name'].value_counts().items():
            all_places[name] += count
        
        # Créer des points fictifs (pour l'exemple)
        # En pratique, tu voudrais utiliser une API de géocodage ici
        import random
        
        # Carte centrée sur la France
        center_lat, center_lng = 46.603354, 1.888334
        
        for place_name, count in all_places.items():
            if count > 2:  # filtrer les lieux peu fréquents
                # Générer des coordonnées aléatoires pour la démo
                # En production, tu utiliserais un géocodeur réel
                lat = center_lat + (random.random() - 0.5) * 5
                lng = center_lng + (random.random() - 0.5) * 8
                
                map_points.append({
                    'name': place_name,
                    'lat': lat,
                    'lng': lng,
                    'count': count,
                    'type': 'mixed'
                })
    
    # Préparer les données pour le template
    context = {
        "unique_departures": unique_departures,
        "unique_destinations": unique_destinations,
        "popular_route_count": popular_route_count,
        "avg_distance": avg_distance,
        "top_departures": top_departures,
        "top_destinations": top_destinations,
        "top_routes": top_routes,
        "map_points": map_points
    }
    
    # Rendre le template
    rendered_html = template.render(**context)
    
    # Retourner l'iframe avec le template rendu
    return html.Iframe(
        srcDoc=rendered_html,
        style={
            "width": "100%", 
            "height": "900px", 
            "border": "none", 
            "overflow": "hidden",
            "borderRadius": "18px"
        },
        id="stats-geographic-iframe",
        sandbox="allow-scripts",
    )
