import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime
import os
import argparse
from typing import Any, Dict, List, Optional, Tuple
from src.core.settings import FIREBASE_CONFIG, OUTPUT_DIRS, ensure_dir


class ChatsSubscriber:
    def __init__(self):
        """
        Initialise la connexion Firebase avec la configuration depuis settings.py
        qui supporte à la fois les fichiers locaux et les variables d'environnement
        """
        # Utiliser directement les constantes de settings.py
        self.output_dir = OUTPUT_DIRS["chats"]
        
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

    def run(self, collection_name: str = "chats", save_data: bool = True) -> Dict[str, Any]:
        """Récupère, traite et sauvegarde les données des chats en une seule opération
        
        Args:
            collection_name (str): Nom de la collection Firestore pour les chats
            save_data (bool): Si True, sauvegarde automatiquement les données traitées
            
        Returns:
            Dict[str, Any]: Données traitées ou dictionnaire vide en cas d'erreur
        """
        try:
            print(f"Récupération des chats...")
            chats_collection = self.db.collection(collection_name)
            chats_docs = chats_collection.stream()
            
            raw_data = []
            for chat_doc in chats_docs:
                chat_id = chat_doc.id
                chat_data = chat_doc.to_dict()
                
                # Récupérer les messages de ce chat
                print(f"Récupération des messages pour le chat {chat_id}...")
                messages_collection = chat_doc.reference.collection("chat_messages")
                messages = []
                
                for msg_doc in messages_collection.stream():
                    msg_id = msg_doc.id
                    msg_data = msg_doc.to_dict()
                    messages.append({
                        "id": msg_id,
                        "data": msg_data
                    })
                
                raw_data.append((chat_id, chat_data, messages))
                
            print(f"Nombre de chats récupérés : {len(raw_data)}")
            
            # Traitement des données immédiatement
            if self.process(raw_data):
                # Sauvegarde des données si demandé
                if save_data:
                    saved = self.save()
                    if saved:
                        print(f"Données des chats sauvegardées avec succès")
                    else:
                        print("Avertissement: échec de la sauvegarde des données")
                return self.data_dict
            else:
                print("Erreur lors du traitement des chats")
                return {}
        except Exception as e:
            print(f"Erreur lors de la récupération des chats: {e}")
            return {}
            
    def retrieve_raw_data(self, collection_name: str = "chats") -> List[Tuple[str, Dict[str, Any], List[Dict[str, Any]]]]:
        """Récupère uniquement les données brutes des chats et leurs messages sans traitement
        
        Args:
            collection_name (str): Nom de la collection Firestore
            
        Returns:
            List[Tuple[str, Dict[str, Any], List[Dict[str, Any]]]]: Données brutes des chats
        """
        try:
            print(f"Récupération des données brutes des chats...")
            chats_collection = self.db.collection(collection_name)
            chats_docs = chats_collection.stream()
            
            result = []
            for chat_doc in chats_docs:
                chat_id = chat_doc.id
                chat_data = chat_doc.to_dict()
                
                # Récupérer les messages de ce chat
                print(f"Récupération des messages pour le chat {chat_id}...")
                messages_collection = chat_doc.reference.collection("chat_messages")
                messages = []
                
                for msg_doc in messages_collection.stream():
                    msg_id = msg_doc.id
                    msg_data = msg_doc.to_dict()
                    messages.append({
                        "id": msg_id,
                        "data": msg_data
                    })
                
                result.append((chat_id, chat_data, messages))
                
            print(f"Nombre de chats récupérés : {len(result)}")
            return result
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            return []

    def process(self, raw_data: List[Tuple[str, Dict[str, Any], List[Dict[str, Any]]]]) -> bool:
        """Traite les données des chats et leurs messages"""
        try:
            print("Traitement des chats et messages...")
            self.data_dict = {}
            
            for chat_id, chat_data, messages in raw_data:
                # Convertir les données du chat
                serialized_chat = self.serialize_firestore_data(chat_data)
                
                # Convertir les messages
                serialized_messages = []
                for message in messages:
                    serialized_message = self.serialize_firestore_data(message)
                    serialized_messages.append(serialized_message)
                
                # Stocker les données
                self.data_dict[chat_id] = {
                    "data": serialized_chat,
                    "messages": serialized_messages,
                    "updated_at": datetime.now().isoformat()
                }
            
            print(f"Chats traités : {len(self.data_dict)}")
            return True
        except Exception as e:
            print(f"Erreur lors du traitement : {e}")
            return False

    def save(self) -> bool:
        """Sauvegarde les données des chats"""
        try:
            if not self.data_dict:
                raise ValueError("Aucune donnée à sauvegarder. Exécutez d'abord process().")

            timestamp = datetime.now()
            date_str = timestamp.strftime('%Y%m%d')
            filename = f"chats_data_{date_str}.json"

            # Créer les chemins des dossiers
            ensure_dir(self.output_dir)

            # Sauvegarder la version datée
            dated_path = os.path.join(self.output_dir, filename)
            with open(dated_path, 'w', encoding='utf-8') as f:
                json.dump(self.data_dict, f, ensure_ascii=False, indent=2)
            print(f"Données sauvegardées dans : {dated_path}")
            
            # Sauvegarder la version courante
            latest_path = os.path.join(self.output_dir, 'chats_data.json')
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(self.data_dict, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde : {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Synchronise les chats depuis Firebase')
    parser.add_argument('--output', type=str, help='Dossier de sauvegarde des fichiers (optionnel)')
    args = parser.parse_args()

    # Créer l'instance
    firebase_chats = ChatsSubscriber()
    
    # Récupérer et sauvegarder les chats
    data = firebase_chats.run()
    if data:
        print("Données des chats récupérées et sauvegardées avec succès")
    else:
        print("Erreur lors de la récupération ou de la sauvegarde des chats")


if __name__ == "__main__":
    main()