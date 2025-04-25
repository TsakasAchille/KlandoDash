import pandas as pd
from typing import Optional
from datetime import datetime
import math
from src.core.database import get_session, Trip

class TripsSubscriber:
    def __init__(self):
        """
        Initialise la classe pour accéder aux données des trajets via PostgreSQL
        """
        # Régions et leurs coordonnées
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

    def determine_region(self, lat: float, lon: float) -> str:
        """Détermine la région en fonction des coordonnées données"""
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

    def run(self) -> pd.DataFrame:
        """
        Récupère les données des trajets directement depuis la base de données
        et les renvoie sous forme de DataFrame
        
        Returns:
            pd.DataFrame: DataFrame contenant les données des trajets
        """
        try:
            print(f"Récupération des trajets depuis PostgreSQL...")
            return self.get_trips_dataframe()
        except Exception as e:
            print(f"Erreur lors de la récupération des trajets: {e}")
            return pd.DataFrame()  # Retourner un DataFrame vide en cas d'erreur
            
    def retrieve_raw_data(self):
        """Récupère les données brutes des trajets depuis la base de données PostgreSQL"""
        try:
            print("Récupération des trajets depuis PostgreSQL...")
            session = get_session()
            trips = session.query(Trip).all()
            result = [trip.to_dict() for trip in trips]
            session.close()
            print(f"Nombre de trajets récupérés : {len(result)}")
            return result
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            return []
            
    def get_trips_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Convertit les données des trajets en DataFrame pandas directement depuis PostgreSQL
        
        Returns:
            Optional[pd.DataFrame]: DataFrame des trajets ou None en cas d'erreur
        """
        try:
            # Récupérer les données brutes
            raw_trips = self.retrieve_raw_data()
            
            if not raw_trips:
                print("Aucun trajet trouvé dans la base de données.")
                return None
                
            # Créer le DataFrame directement à partir des données brutes
            df = pd.DataFrame(raw_trips)
            
            # Ajouter la région si elle n'existe pas déjà
            if 'region' not in df.columns and 'destination_latitude' in df.columns and 'destination_longitude' in df.columns:
                df['region'] = df.apply(lambda row: 
                    self.determine_region(row['destination_latitude'], row['destination_longitude']), 
                    axis=1)
            
            # Conversion des dates
            date_columns = ['departure_date', 'departure_schedule', 'destination_schedule', 'updated_at']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    
            # Renommer l'id en trip_id pour maintenir la compatibilité
            if 'id' in df.columns and 'trip_id' not in df.columns:
                df = df.rename(columns={'id': 'trip_id'})
                    
            print(f"DataFrame créé avec {len(df)} trajets")
            return df
        except Exception as e:
            print(f"Erreur lors de la création du DataFrame : {e}")
            return None


if __name__ == "__main__":
    # Exemple d'utilisation simple
    subscriber = TripsSubscriber()
    trips_df = subscriber.run()
    
    if not trips_df.empty:
        print(f"Colonnes disponibles : {trips_df.columns.tolist()}")
        print(f"Nombre total de trajets : {len(trips_df)}")
    else:
        print("Aucun trajet n'a été récupéré")