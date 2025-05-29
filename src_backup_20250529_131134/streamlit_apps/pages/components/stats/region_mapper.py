import pandas as pd
from math import radians, sin, cos, sqrt, atan2

class RegionMapper:
    """Classe responsable de la cartographie des coordonnées GPS vers les régions"""
    
    def __init__(self):
        """Initialise le mappeur de régions avec les coordonnées des régions du Sénégal"""
        # Coordonnées des régions du Sénégal
        self.senegal_regions = {
            'Dakar': [14.6937, -17.4441],
            'Thiès': [14.7910, -16.9359],
            'Diourbel': [14.7295, -16.2327],
            'Fatick': [14.3390, -16.4110],
            'Kaolack': [14.1652, -16.0726],
            'Kaffrine': [14.1059, -15.5425],
            'Tambacounda': [13.7707, -13.6673],
            'Kédougou': [12.5598, -12.1747],
            'Kolda': [12.8983, -14.9414],
            'Sédhiou': [12.7080, -15.5569],
            'Ziguinchor': [12.5598, -16.2733],
            'Saint-Louis': [16.0326, -16.4818],
            'Louga': [15.6173, -16.2240],
            'Matam': [15.6559, -13.2548]
        }
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calcule la distance entre deux points géographiques en kilomètres (formule de Haversine)
        
        Args:
            lat1: Latitude du point 1
            lon1: Longitude du point 1
            lat2: Latitude du point 2
            lon2: Longitude du point 2
            
        Returns:
            Distance en kilomètres
        """
        # Rayon de la Terre en kilomètres
        R = 6371.0
        
        # Convertir les degrés en radians
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        # Différence de longitude et latitude
        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad
        
        # Formule de Haversine
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        
        return distance
    
    def find_nearest_region(self, lat, lon):
        """Trouve la région la plus proche d'un point géographique
        
        Args:
            lat: Latitude du point
            lon: Longitude du point
            
        Returns:
            Nom de la région la plus proche
        """
        min_distance = float('inf')
        nearest_region = None
        
        for region, coords in self.senegal_regions.items():
            region_lat, region_lon = coords
            distance = self.calculate_distance(lat, lon, region_lat, region_lon)
            
            if distance < min_distance:
                min_distance = distance
                nearest_region = region
        
        return nearest_region
    
    def assign_regions_to_trips(self, trips_df):
        """Attribue les régions de départ et d'arrivée à chaque trajet
        
        Args:
            trips_df: DataFrame contenant les données des trajets
            
        Returns:
            DataFrame avec les régions attribuées
        """
        # Créer une copie pour ne pas modifier le DataFrame original
        df = trips_df.copy()
        
        # Vérifier si les colonnes de coordonnées sont disponibles
        if all(col in df.columns for col in ['departure_latitude', 'departure_longitude', 'destination_latitude', 'destination_longitude']):
            # Attribuer les régions en fonction des coordonnées
            df['departure_region'] = df.apply(
                lambda row: self.find_nearest_region(row['departure_latitude'], row['departure_longitude']), 
                axis=1
            )
            
            df['destination_region'] = df.apply(
                lambda row: self.find_nearest_region(row['destination_latitude'], row['destination_longitude']), 
                axis=1
            )
        
        return df
    
    def get_region_coordinates(self):
        """Retourne un DataFrame avec les coordonnées des régions
        
        Returns:
            DataFrame avec les coordonnées des régions
        """
        return pd.DataFrame([(region, lat, lon) for region, (lat, lon) in self.senegal_regions.items()],
                          columns=['region', 'lat', 'lon'])
    
    def get_senegal_center(self):
        """Retourne les coordonnées du centre du Sénégal
        
        Returns:
            Dictionnaire avec les coordonnées du centre
        """
        return {"lat": 14.4974, "lon": -14.4524}
