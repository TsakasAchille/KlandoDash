import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime

class BaseSubscriber:
    def __init__(self, key_path=None, output_dir=None):
        """
        Classe de base pour tous les subscribers Firebase
        """
        if key_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            key_path = os.path.join(base_dir, 'src', 'keys', 'klando-d3cb3-firebase-adminsdk-uak7b-7af3798d36.json')
        
        if output_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.raw_dir = os.path.join(base_dir, 'data', 'raw')
        else:
            self.raw_dir = output_dir
            
        self.db = firestore.Client.from_service_account_json(key_path)
        self.data_dict = {}
        self.collection_name = None
    
    def serialize_firestore_data(self, data):
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
    
    def run(self):
        """À implémenter dans les classes enfants"""
        raise NotImplementedError
        
    def process(self, raw_data):
        """À implémenter dans les classes enfants"""
        raise NotImplementedError
        
    def save(self, prefix):
        """Sauvegarde générique des données"""
        try:
            if not self.data_dict:
                raise ValueError("Aucune donnée à sauvegarder. Exécutez d'abord process().")

            timestamp = datetime.now()
            date_str = timestamp.strftime('%Y%m%d')
            filename = f"{prefix}_data_{date_str}.json"

            # Créer les chemins des dossiers
            type_dir = os.path.join(self.raw_dir, prefix)
            os.makedirs(type_dir, exist_ok=True)

            # Sauvegarder la version datée
            dated_path = os.path.join(type_dir, filename)
            with open(dated_path, 'w', encoding='utf-8') as f:
                json.dump(self.data_dict, f, ensure_ascii=False, indent=2)
            print(f"Données sauvegardées dans : {dated_path}")
            
            # Sauvegarder la version courante
            latest_path = os.path.join(self.raw_dir, f'{prefix}_data.json')
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(self.data_dict, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")
            return False