import firebase_admin
from firebase_admin import credentials, firestore
import json
import orjson
from datetime import datetime
import os
from dateutil import parser
from dateutil.relativedelta import relativedelta
import argparse

class FirebaseUsers:
    def __init__(self, 
                key_path=None, output_dir=None):
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

    def run(self, collection_name="users"):
        """
        Récupère les données brutes depuis Firebase
        Args:
            collection_name (str): Nom de la collection à récupérer
        Returns:
            list: Liste des documents bruts
        """
        try:
            print(f"Récupération des données de la collection {collection_name}...")
            collection_ref = self.db.collection(collection_name)
            docs = collection_ref.stream()
            raw_data = [(doc.id, doc.to_dict()) for doc in docs]
            print(f"Nombre de documents récupérés : {len(raw_data)}")
            return raw_data
        except Exception as e:
            print(f"Erreur lors de la récupération des données : {e}")
            return []

    def process(self, raw_data):
        """
        Traite les données brutes pour les formater
        Args:
            raw_data (list): Liste des tuples (id, data) bruts
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

    def save(self):
        """
        Sauvegarde les données traitées dans les fichiers
        """
        try:
            if not self.data_dict:
                raise ValueError("Aucune donnée à sauvegarder. Exécutez d'abord process().")

            # Créer le nom du fichier avec la date et l'heure
            timestamp = datetime.now()
            date_str = timestamp.strftime('%Y%m%d')
            filename = f"users_data_{date_str}.json"

            # Créer les chemins des dossiers
            users_dir = os.path.join(self.raw_dir, 'user')
            os.makedirs(users_dir, exist_ok=True)

            # Chemin pour le fichier daté dans le dossier users
            dated_path = os.path.join(users_dir, filename)
            
            # Sauvegarder les données dans le fichier daté
            with open(dated_path, 'w', encoding='utf-8') as f:
                json.dump(self.data_dict, f, ensure_ascii=False, indent=2)
            print(f"Données sauvegardées dans : {dated_path}")
            
            # Mettre à jour aussi users_data.json dans le dossier raw pour la compatibilité
            latest_path = os.path.join(self.raw_dir, 'users_data.json')
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(self.data_dict, f, ensure_ascii=False, indent=2)
            print(f"Données également sauvegardées dans : {latest_path}")
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données : {e}")
            return False

    def save_firestore_to_file(self, collection_name="users"):
        """
        Méthode combinée pour exécuter tout le processus
        """
        raw_data = self.run(collection_name)
        if raw_data and self.process(raw_data):
            return self.save()
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

    def serialize_firestore_data(self, data):
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
    parser.add_argument('--key', type=str, help='Chemin vers le fichier de clé Firebase (optionnel)')
    parser.add_argument('--output', type=str, help='Dossier de sauvegarde des fichiers (optionnel)')
    args = parser.parse_args()

    # Créer l'instance avec la clé et le dossier de sortie spécifiés ou les valeurs par défaut
    firebase_users = FirebaseUsers(key_path=args.key, output_dir=args.output)
    
    # Exécuter le processus complet
    firebase_users.save_firestore_to_file("users")


if __name__ == "__main__":
    main()
