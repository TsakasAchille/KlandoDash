import firebase_admin
from firebase_admin import credentials, firestore
import json
import orjson
from datetime import datetime
import os
from dateutil import parser
from dateutil.relativedelta import relativedelta
import argparse
from typing import Any, Dict, List, Optional, Union, Tuple
from src.core.settings import FIREBASE_CONFIG, OUTPUT_DIRS, ensure_dir

class UsersSubscriber:
    def __init__(self):
        """
        Initialise la connexion Firebase avec la configuration depuis settings.py
        qui supporte à la fois les fichiers locaux et les variables d'environnement
        """
        # Utiliser directement les constantes de settings.py
        self.output_dir = OUTPUT_DIRS["users"]
        
        # S'assurer que le répertoire de sortie existe
        ensure_dir(self.output_dir)
        
        # Initialiser Firebase en fonction de la configuration disponible
        if "key_path" in FIREBASE_CONFIG:
            self.db = firestore.Client.from_service_account_json(FIREBASE_CONFIG["key_path"])
        elif "credentials_json" in FIREBASE_CONFIG:
            # Utiliser directement le dictionnaire d'identifiants
            cred = credentials.Certificate(FIREBASE_CONFIG["credentials_json"])
            # Initialiser l'application Firebase si ce n'est pas déjà fait
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        else:
            raise Exception("Configuration Firebase incorrecte ou manquante")
            
        print("Projet connecté :", self.db.project)
        self.data_dict = {}

    def run(self, collection_name="users", save_data: bool = True) -> Dict[str, Any]:
        """
        Récupère, traite et sauvegarde les données des utilisateurs en une seule opération
        
        Args:
            collection_name (str): Nom de la collection à récupérer
            save_data (bool): Si True, sauvegarde automatiquement les données traitées
            
        Returns:
            Dict[str, Any]: Dictionnaire des utilisateurs traités ou dictionnaire vide en cas d'erreur
        """
        try:
            print(f"Récupération des données de la collection {collection_name}...")
            collection_ref = self.db.collection(collection_name)
            docs = collection_ref.stream()
            raw_data = [(doc.id, doc.to_dict()) for doc in docs]
            print(f"Nombre de documents récupérés : {len(raw_data)}")
            
            # Traitement des données immédiatement
            if self.process(raw_data):
                # Sauvegarde des données si demandé
                if save_data:
                    saved_path = self.save()
                    if saved_path:
                        print(f"Données des utilisateurs sauvegardées avec succès")
                    else:
                        print("Avertissement: échec de la sauvegarde des données")
                return self.data_dict
            else:
                print("Erreur lors du traitement des utilisateurs")
                return {}
        except Exception as e:
            print(f"Erreur lors de la récupération des utilisateurs: {e}")
            return {}
            
    def retrieve_raw_data(self, collection_name="users") -> List[Tuple[str, Dict[str, Any]]]:
        """
        Récupère uniquement les données brutes depuis Firebase sans traitement
        
        Args:
            collection_name (str): Nom de la collection à récupérer
        Returns:
            list: Liste des documents bruts
        """
        try:
            print(f"Récupération des données brutes de la collection {collection_name}...")
            collection_ref = self.db.collection(collection_name)
            docs = collection_ref.stream()
            raw_data = [(doc.id, doc.to_dict()) for doc in docs]
            print(f"Nombre de documents récupérés : {len(raw_data)}")
            return raw_data
        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")
            return []

    def process(self, raw_data) -> bool:
        """
        Traite les données brutes pour les formater
        Args:
            raw_data (list): Liste des tuples (id, data) bruts
        Returns:
            bool: True si le traitement a réussi, False sinon
        """
        try:
            print("Traitement des données...")
            self.data_dict = {}
            
            for doc_id, doc_data in raw_data:
                # Calculer l'âge si la date de naissance est présente
                if 'birth' in doc_data:
                    age = self.calculate_age(doc_data['birth'])
                    if age is not None:
                        doc_data['age'] = age
                
                # Stocker les données dans un format compatible avec l'application
                self.data_dict[doc_id] = {
                    "data": self.serialize_firestore_data(doc_data),
                    "updated_at": datetime.now().isoformat()
                }
            
            print(f"Données traitées : {len(self.data_dict)} documents")
            return True
        except Exception as e:
            print(f"Erreur lors du traitement des données : {e}")
            return False

    def save(self) -> bool:
        """
        Sauvegarde les données traitées dans les fichiers
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            if not self.data_dict:
                raise ValueError("Aucune donnée à sauvegarder. Exécutez d'abord process().")

            timestamp = datetime.now()
            date_str = timestamp.strftime('%Y%m%d')
            filename = f"users_data_{date_str}.json"

            # Créer les chemins des dossiers
            ensure_dir(self.output_dir)

            # Chemin pour le fichier daté dans le dossier users
            dated_path = os.path.join(self.output_dir, filename)
            
            # Sauvegarder les données dans le fichier daté
            with open(dated_path, 'w', encoding='utf-8') as f:
                json.dump(self.data_dict, f, ensure_ascii=False, indent=2)
            print(f"Données sauvegardées dans : {dated_path}")
            
            # Mettre à jour aussi users_data.json pour l'accès courant
            latest_path = os.path.join(self.output_dir, 'users_data.json')
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(self.data_dict, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données : {e}")
            return False

    def calculate_age(self, birth_date):
        """Calcule l'âge à partir d'une date de naissance"""
        if not birth_date:
            return None
            
        try:
            # Si c'est déjà un objet datetime
            if isinstance(birth_date, datetime):
                birth_date = birth_date
            # Sinon, essayer de parser la chaîne
            else:
                birth_date = parser.parse(birth_date)
                
            # Convertir en datetime naïf (sans fuseau horaire)
            if birth_date.tzinfo:
                birth_date = birth_date.replace(tzinfo=None)
                
            today = datetime.now()
            age = relativedelta(today, birth_date).years
            return age
        except Exception as e:
            print(f"Erreur lors du calcul de l'âge : {e}")
            return None

    def serialize_firestore_data(self, data: Any) -> Any:
        """Convertit les objets Firestore non sérialisables"""
        if isinstance(data, firestore.DocumentReference):
            # Convertir DocumentReference en chemin de document
            return data.path
        elif isinstance(data, firestore.GeoPoint):
            # Convertir GeoPoint en un dictionnaire avec latitude et longitude
            return {"latitude": data.latitude, "longitude": data.longitude}
        elif isinstance(data, datetime):
            # Convertir Datetime en chaîne ISO 8601
            return data.isoformat()
        elif isinstance(data, list):
            # Traiter les listes récursivement
            return [self.serialize_firestore_data(v) for v in data]
        elif isinstance(data, dict):
            # Traiter les dictionnaires récursivement
            return {key: self.serialize_firestore_data(value) for key, value in data.items()}
        else:
            # Retourner la valeur telle quelle si elle est déjà sérialisable
            return data


def main():
    parser = argparse.ArgumentParser(description='Synchronise les utilisateurs depuis Firebase')
    parser.add_argument('--output', type=str, help='Dossier de sauvegarde des fichiers (optionnel)')
    args = parser.parse_args()

    # Créer l'instance avec la clé et le dossier de sortie spécifiés ou les valeurs par défaut
    firebase_users = UsersSubscriber()
    
    # Récupérer et sauvegarder les utilisateurs
    raw_data = firebase_users.run()
    if raw_data:
        print("Utilisateurs récupérés avec succès")


if __name__ == "__main__":
    main()
