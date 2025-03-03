import firebase_admin
from firebase_admin import credentials, firestore
import json
import orjson
from datetime import datetime
import os
import math
import argparse
from typing import Any, Dict, List, Optional, Union, Tuple

class FirebaseTrips:
    def __init__(self, key_path: Optional[str] = None, output_dir: Optional[str] = None):
        """
        Initialise la connexion Firebase avec la clé fournie ou la clé par défaut
        Args:
            key_path (str, optional): Chemin vers le fichier de clé Firebase. Si non fourni, utilise le chemin par défaut.
            output_dir (str, optional): Dossier de sauvegarde des fichiers. Si non fourni, utilise le dossier par défaut.
        """
        # Configuration de la clé Firebase
        if key_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            key_path = os.path.join(base_dir, 'src', 'keys', 'klando-d3cb3-firebase-adminsdk-uak7b-7af3798d36.json')
        
        # Configuration du dossier de sortie
        if output_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.raw_dir = os.path.join(base_dir, 'data', 'raw')
        else:
            self.raw_dir = output_dir
            
        self.db = firestore.Client.from_service_account_json(key_path)
        print("Projet connecté :", self.db.project)
        self.data_dict = {}
        
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

    def serialize_firestore_data(self, data: Any) -> Any:
        """Convertit les objets Firestore non sérialisables"""
        if isinstance(data, firestore.DocumentReference):
            return data.path
        elif isinstance(data, firestore.GeoPoint):
            return {"latitude": data.latitude, "longitude": data.longitude}
        elif isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, list):
            return [self.serialize_firestore_data(v) for v in data]
        elif isinstance(data, dict):
            return {key: self.serialize_firestore_data(value) for key, value in data.items()}
        else:
            return data

    def run(self, collection_name: str = "trips") -> List[Tuple[str, Dict[str, Any]]]:
        """Récupère les données des trajets"""
        try:
            print(f"Récupération des trajets...")
            collection_ref = self.db.collection(collection_name)
            docs = collection_ref.stream()
            raw_data = [(doc.id, doc.to_dict()) for doc in docs]
            print(f"Nombre de trajets récupérés : {len(raw_data)}")
            return raw_data
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            return []

    def process(self, raw_data: List[Tuple[str, Dict[str, Any]]]) -> bool:
        """Traite les données des trajets"""
        try:
            print("Traitement des trajets...")
            self.data_dict = {}
            
            for doc_id, doc_data in raw_data:
                # Convertir d'abord les données pour gérer les types Firestore
                serialized_data = self.serialize_firestore_data(doc_data)
                
                # Ajouter la région pour chaque trajet
                if 'destination_location' in serialized_data:
                    dest = serialized_data['destination_location']
                    if isinstance(dest, dict) and 'latitude' in dest and 'longitude' in dest:
                        serialized_data['region'] = self.determine_region(
                            dest['latitude'], 
                            dest['longitude']
                        )
                
                # Stocker les données
                self.data_dict[doc_id] = {
                    "data": serialized_data,
                    "updated_at": datetime.now().isoformat()
                }
            
            print(f"Trajets traités : {len(self.data_dict)}")
            return True
        except Exception as e:
            print(f"Erreur lors du traitement : {e}")
            return False

    def save(self) -> bool:
        """Sauvegarde les données des trajets"""
        try:
            if not self.data_dict:
                raise ValueError("Aucune donnée à sauvegarder. Exécutez d'abord process().")

            timestamp = datetime.now()
            date_str = timestamp.strftime('%Y%m%d')
            filename = f"trips_data_{date_str}.json"

            # Créer les chemins des dossiers
            trips_dir = os.path.join(self.raw_dir, 'trips')
            os.makedirs(trips_dir, exist_ok=True)

            # Sauvegarder la version datée
            dated_path = os.path.join(trips_dir, filename)
            with open(dated_path, 'w', encoding='utf-8') as f:
                json.dump(self.data_dict, f, ensure_ascii=False, indent=2)
            print(f"Données sauvegardées dans : {dated_path}")
            
            # Sauvegarder la version courante
            latest_path = os.path.join(self.raw_dir, 'trips_data.json')
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(self.data_dict, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Synchronise les trajets depuis Firebase')
    parser.add_argument('--key', type=str, help='Chemin vers le fichier de clé Firebase (optionnel)')
    parser.add_argument('--output', type=str, help='Dossier de sauvegarde des fichiers (optionnel)')
    args = parser.parse_args()

    # Créer l'instance avec la clé et le dossier de sortie spécifiés ou les valeurs par défaut
    firebase_trips = FirebaseTrips(key_path=args.key, output_dir=args.output)
    
    # Récupérer et sauvegarder les trajets
    raw_data = firebase_trips.run()
    if raw_data and firebase_trips.process(raw_data):
        firebase_trips.save()


if __name__ == "__main__":
    main()