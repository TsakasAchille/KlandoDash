import math
import pandas as pd

# Note: Ce fichier a été simplifié suite à la migration vers PostgreSQL/Supabase
# Seules les fonctionnalités encore utilisées ont été conservées

class Backend:
    def __init__(self):
        # Coordonnées des régions du Sénégal pour la détermination de région
        self.REGIONS = {
            'Dakar': (14.6937, -17.4441),
            'Thiès': (14.7910, -16.9359),
            'Diourbel': (14.6479, -16.2332),
            'Fatick': (14.3390, -16.4041),
            'Kaolack': (14.1652, -16.0726),
            'Kaffrine': (14.1059, -15.5508),
            'Tambacounda': (13.7707, -13.6673),
            'Kédougou': (12.5605, -12.1747),
            'Kolda': (12.8983, -14.9412),
            'Sédhiou': (12.7044, -15.5569),
            'Ziguinchor': (12.5665, -16.2733),
            'Saint-Louis': (16.0326, -16.4818),
            'Louga': (15.6173, -16.2240),
            'Matam': (15.6559, -13.2548)
        }

    def determine_region(self, lat, lon):
        """
        Détermine la région en fonction des coordonnées données
        en trouvant la région la plus proche
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            
        Returns:
            str: Nom de la région la plus proche
        """
        if not lat or not lon:
            return "Inconnu"

        min_distance = float('inf')
        closest_region = "Inconnu"

        for region, (reg_lat, reg_lon) in self.REGIONS.items():
            distance = math.sqrt((lat - reg_lat)**2 + (lon - reg_lon)**2)
            if distance < min_distance:
                min_distance = distance
                closest_region = region

        return closest_region

# Note: Les autres méthodes liées au chargement de données depuis Firebase
# ont été supprimées car elles ne sont plus utilisées dans l'application
# qui utilise maintenant PostgreSQL/Supabase pour l'accès aux données.