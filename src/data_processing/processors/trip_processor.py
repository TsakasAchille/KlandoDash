from utils.backend import Backend
import pandas as pd
import os
from typing import *  # Ajoutez cet import en haut du fichier
from data_processing.loaders.loader import Loader
import json

class TripProcessor:
    def __init__(self):
        """
        Initialise le processor avec une instance de Backend
        """
        self.backend = Backend()
        self.loader = Loader()


    def convert_trips_json_to_dataframe(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Convertit le JSON des trips en DataFrame avec une structure aplatie
        Args:
            file_path (str): Chemin vers le fichier JSON des trips
        Returns:
            Optional[pd.DataFrame]: DataFrame structuré des trips ou None si erreur
        """
        if not self.loader._check_json_file(file_path):
            return None

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            trips_list = []
            for trip_id, trip_data in data.items():
                trip_dict = {
                    'trip_id': trip_id,
                    'updated_at': trip_data.get('updated_at'),
                    # Informations de base
                    'departure_date': trip_data['data'].get('departure_date'),
                    'departure_schedule': trip_data['data'].get('departure_schedule'),
                    'destination_schedule': trip_data['data'].get('destination_schedule'),
                    'price_per_seat': trip_data['data'].get('price_per_seat'),
                    'number_of_seats': trip_data['data'].get('number_of_seats'),
                    'available_seats': trip_data['data'].get('available_seats'),
                    'trip_distance': trip_data['data'].get('trip_distance'),
                    'auto_confirmation': trip_data['data'].get('auto_confirmation'),
                    
                    # Lieux
                    'departure_name': trip_data['data'].get('departure_name'),
                    'destination_name': trip_data['data'].get('destination_name'),
                    'departure_latitude': trip_data['data'].get('departure_location', {}).get('latitude'),
                    'departure_longitude': trip_data['data'].get('departure_location', {}).get('longitude'),
                    'destination_latitude': trip_data['data'].get('destination_location', {}).get('latitude'),
                    'destination_longitude': trip_data['data'].get('destination_location', {}).get('longitude'),

                    "region": trip_data['data'].get('region'),
                    "trip_polyline": trip_data['data'].get('trip_polyline'),
                    
                    # Références
                    'driver_reference': trip_data['data'].get('driver_reference'),
                    'all_passengers': ','.join(trip_data['data'].get('all_passengers', [])),
                    'passenger_reservations': json.dumps(trip_data['data'].get('passenger_reservations', []))
                }
                trips_list.append(trip_dict)
            
            df = pd.DataFrame(trips_list)
       
            
            # Conversion des dates - utiliser une méthode plus robuste
            date_columns = ['departure_date', 'departure_schedule', 'destination_schedule', 'updated_at']
            for col in date_columns:
                if col in df.columns:
                    # Utiliser le parsing sans spécifier de format explicite
                    # pandas essaiera de détecter automatiquement le format
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    
            return df

        except Exception as e:
            print(f"Erreur lors du parsing du fichier trips {file_path}: {e}")
            return None


    def filter_trips(self, df: pd.DataFrame, remove_columns: List[str]) -> pd.DataFrame:
        """
        Filtre le DataFrame des trajets en supprimant les colonnes spécifiées
        Args:
            df (pd.DataFrame): DataFrame des trajets
            remove_columns (List[str]): Liste des colonnes à supprimer
        Returns:
            pd.DataFrame: DataFrame filtré
        """
        return df.drop(columns=remove_columns)


    def handler(self):

        trips_df = None

        trips_file_path = self.loader.find_latest_json_file_path(data_type='trips')
        if trips_file_path is None:
            print("Erreur : Aucun fichier de trajets trouvé")
            return None

        print(f"Chargement des trajets depuis : {trips_file_path}")

        trips_df = self.convert_trips_json_to_dataframe(trips_file_path)

        if trips_df is None:
            print("Erreur : Impossible de charger les données des trajets")
            return None
        
        self.loader.save_dataframe_to_csv(trips_df, 'trips')

        return trips_df


    def get_trips(self, file_path=None):
        """
        Récupère et formate les données des trajets depuis un fichier spécifique ou le plus récent
        Args:
            file_path (str, optional): Chemin vers le fichier à utiliser. Si non fourni, utilise le plus récent -> pattern trips_data*.json
        Returns:
            list: Liste des trajets formatés
        """
        try:
            print("Getting trips data...")
            print(f"File path: {file_path}")

            # Utiliser le fichier spécifié ou trouver le plus récent
            if file_path and os.path.isfile(file_path):
                latest_trip_file = file_path
            else:
                files = self.get_all_data_files('trips_data*.json')
                if not files:
                    print("Aucun fichier de trajets trouvé")
                    return []
                latest_trip_file = files[0][0]

            print(f"Chargement des trajets depuis : {latest_trip_file}")
            
            with open(latest_trip_file, 'r') as f:
                trips_data = json.load(f)
                
            """
            Transforme les données brutes JSON en liste d'objets Trip structurés.
            
            Exemple:
            
            Supposons que trips_data contient:
            {
                "trip_123": {
                    "data": {
                        "departure_date": "2025-01-15T08:30:00.000Z",
                        "departure_name": "Dakar",
                        "destination_name": "Saint-Louis",
                        "price_per_seat": 5000,
                        "trip_distance": 193.4,
                        "number_of_seats": 4,
                        "driver_reference": "users/driver_456"
                    }
                }
            }
            
            Le processus:
            1. Parcourt chaque entrée de trips_data
            2. Pour trip_id="trip_123", trip_wrapper={"data": {...}}
            3. Crée un objet Trip avec trip_id et trip_wrapper["data"]
            4. Appelle to_dict() sur cet objet Trip
            5. Ajoute le dictionnaire résultant à la liste 'trips'
            
            Résultat dans 'trips':
            [
                {
                    'id': 'trip_123',
                    'departure_date': datetime(2025, 1, 15, 8, 30),
                    'formatted_date': '15/01/2025',
                    'departure_point': 'Dakar',
                    'destination': 'Saint-Louis',
                    'price': 5000,
                    'formatted_price': '5 000 XOF',
                    'distance': 193.4,
                    'driver_id': 'driver_456',
                    ...
                }
            ]
            """
            trips = []
            for trip_id, trip_wrapper in trips_data.items():
                if isinstance(trip_wrapper, dict) and 'data' in trip_wrapper:
                    trip = Trip(trip_id, trip_wrapper['data'])
                    trips.append(trip.to_dict())
            
            print(f"Retour des trajets : {len(trips)} trajets")
            return trips
            
        except Exception as e:
            print(f"Erreur lors du chargement des trajets : {e}")
            return []


if __name__ == "__main__":
    # Créer une instance du processor
    processor = TripProcessor()
    
    # Récupérer le DataFrame
    df_trips = processor.get_trips_dataframe("/home/tsakas/Desktop/KlandoDash/data/raw/trips/trips_data_20250224.json")
    
    # Afficher les informations sur le DataFrame
    print("\nInformations sur le DataFrame:")
    print(f"Nombre de lignes: {len(df_trips)}")
    print(f"Colonnes: {df_trips.columns.tolist()}")
    
    # Créer le dossier output s'il n'existe pas
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder en CSV
    output_file = os.path.join(output_dir, 'trips_data.csv')
    df_trips.to_csv(output_file, index=False)
    print(f"\nDataFrame sauvegardé dans: {output_file}")