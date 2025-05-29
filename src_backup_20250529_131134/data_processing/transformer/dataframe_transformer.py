import os
import json
import pandas as pd
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

class DataFrameTransformer:
    """
    Classe responsable de la transformation des données en DataFrames pandas
    """
    
    def __init__(self):
        """Initialise le transformateur de données"""
        pass
    
    def convert_dict_to_dataframe(self, data: Dict, record_path: str = None, meta: List = None) -> Optional[pd.DataFrame]:
        """
        Convertit un dictionnaire en DataFrame
        
        Args:
            data (Dict): Dictionnaire à convertir
            record_path (str, optional): Chemin vers les enregistrements dans le dictionnaire
            meta (List, optional): Liste des métadonnées à inclure
            
        Returns:
            Optional[pd.DataFrame]: DataFrame contenant les données du dictionnaire
        """
        try:
            return pd.json_normalize(
                data=data,
                record_path=record_path,
                meta=meta,
                errors='ignore'
            )
        except Exception as e:
            print(f"Erreur lors de la conversion du dictionnaire en DataFrame: {e}")
            return None
    
    def convert_trips_to_dataframe(self, data: Dict) -> Optional[pd.DataFrame]:
        """
        Convertit spécifiquement les données de trajets en DataFrame avec une structure adaptée
        
        Args:
            data (Dict): Dictionnaire contenant les données de trajets
            
        Returns:
            Optional[pd.DataFrame]: DataFrame formaté pour les trajets
        """
        try:
            # Extraire et aplatir les données
            trips_list = []
            for trip_id, trip_info in data.items():
                trip_data = trip_info.get('data', {})
                trip_data['id'] = trip_id
                trip_data['updated_at'] = trip_info.get('updated_at')
                trips_list.append(trip_data)
            
            # Créer le DataFrame
            df = pd.DataFrame(trips_list)
            
            # Conversion des colonnes de date/heure
            date_columns = ['created_at', 'updated_at', 'departure_date', 'arrival_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
        except Exception as e:
            print(f"Erreur lors de la conversion des trajets en DataFrame: {e}")
            return None
    
    def convert_users_to_dataframe(self, data: Dict) -> Optional[pd.DataFrame]:
        """
        Convertit spécifiquement les données d'utilisateurs en DataFrame avec une structure adaptée
        
        Args:
            data (Dict): Dictionnaire contenant les données d'utilisateurs
            
        Returns:
            Optional[pd.DataFrame]: DataFrame formaté pour les utilisateurs
        """
        try:
            # Extraire et aplatir les données
            users_list = []
            for user_id, user_info in data.items():
                user_data = user_info.get('data', {})
                user_data['id'] = user_id
                user_data['updated_at'] = user_info.get('updated_at')
                users_list.append(user_data)
            
            # Créer le DataFrame
            df = pd.DataFrame(users_list)
            
            # Conversion des colonnes de date/heure
            date_columns = ['created_at', 'updated_at', 'birth']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return df
        except Exception as e:
            print(f"Erreur lors de la conversion des utilisateurs en DataFrame: {e}")
            return None
    
    def convert_chats_to_dataframe(self, data: Dict) -> Union[pd.DataFrame, Dict[str, pd.DataFrame], None]:
        """
        Convertit spécifiquement les données de chats en DataFrame avec une structure adaptée
        Retourne soit un DataFrame des chats, soit un dictionnaire contenant deux DataFrames:
        - 'chats': DataFrame des chats
        - 'messages': DataFrame des messages
        
        Args:
            data (Dict): Dictionnaire contenant les données de chats
            
        Returns:
            Union[pd.DataFrame, Dict[str, pd.DataFrame], None]: DataFrame des chats ou dictionnaire de DataFrames
        """
        try:
            # Extraire et aplatir les données des chats
            chats_list = []
            messages_list = []
            
            for chat_id, chat_info in data.items():
                # Données du chat
                chat_data = chat_info.get('data', {})
                chat_data['id'] = chat_id
                chat_data['updated_at'] = chat_info.get('updated_at')
                chats_list.append(chat_data)
                
                # Messages du chat
                if 'messages' in chat_info:
                    for message in chat_info['messages']:
                        msg_data = message.get('data', {})
                        msg_data['id'] = message.get('id')
                        msg_data['chat_id'] = chat_id
                        messages_list.append(msg_data)
            
            # Créer les DataFrames
            chats_df = pd.DataFrame(chats_list) if chats_list else pd.DataFrame()
            messages_df = pd.DataFrame(messages_list) if messages_list else pd.DataFrame()
            
            # Conversion des colonnes de date/heure
            date_columns = ['created_at', 'updated_at', 'timestamp']
            for col in date_columns:
                if col in chats_df.columns:
                    chats_df[col] = pd.to_datetime(chats_df[col], errors='coerce')
                if col in messages_df.columns:
                    messages_df[col] = pd.to_datetime(messages_df[col], errors='coerce')
            
            # Retourner soit le DataFrame des chats, soit un dictionnaire des deux DataFrames
            if not messages_df.empty:
                return {
                    'chats': chats_df,
                    'messages': messages_df
                }
            else:
                return chats_df
                
        except Exception as e:
            print(f"Erreur lors de la conversion des chats en DataFrame: {e}")
            return None
    
    def save_dataframe_to_csv(self, df: pd.DataFrame, data_type: str, output_dir: str = None) -> Optional[str]:
        """
        Sauvegarde un DataFrame en CSV dans le dossier approprié
        Args:
            df (pd.DataFrame): DataFrame à sauvegarder
            data_type (str): Type de données ('trips', 'users' ou 'chats')
            output_dir (str, optional): Répertoire de sortie personnalisé
        Returns:
            Optional[str]: Chemin du fichier CSV créé ou None si erreur
        """
        try:
            # Créer le nom du fichier avec la date
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f"{data_type}_data_{timestamp}.csv"
            
            # Déterminer le répertoire de sortie
            if output_dir is None:
                # Obtenir le chemin du projet
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                # Construire le chemin de sortie (dans un dossier processed)
                output_dir = os.path.join(project_root, 'data', 'processed', data_type)
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Chemin complet du fichier
            output_path = os.path.join(output_dir, filename)
            
            # Sauvegarder en CSV
            df.to_csv(output_path, index=False)
            print(f"Fichier CSV sauvegardé : {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde en CSV : {e}")
            return None


if __name__ == "__main__":
    from src.data_processing.loaders.loader import Loader
    
    # Charger les données
    loader = Loader()
    transformer = DataFrameTransformer()
    
    # Exemple avec les trajets
    trips_file_path = loader.find_latest_json_file_path(data_type='trips')
    if trips_file_path:
        trips_data, _ = loader.load_json_to_dict(file_path=trips_file_path)
        trips_df = transformer.convert_trips_to_dataframe(trips_data)
        if trips_df is not None:
            print("\n=== Aperçu du DataFrame des Trips ===")
            print(f"Forme : {trips_df.shape}")
            print("\nColonnes :")
            print(trips_df.columns.tolist())
            print("\nPremières lignes :")
            print(trips_df.head())
            
            # Sauvegarder en CSV
            transformer.save_dataframe_to_csv(trips_df, 'trips')
    
    # Exemple avec les utilisateurs
    users_file_path = loader.find_latest_json_file_path(data_type='users')
    if users_file_path:
        users_data, _ = loader.load_json_to_dict(file_path=users_file_path)
        users_df = transformer.convert_users_to_dataframe(users_data)
        if users_df is not None:
            print("\n=== Aperçu du DataFrame des Utilisateurs ===")
            print(f"Forme : {users_df.shape}")
            print("\nColonnes :")
            print(users_df.columns.tolist())
            
    # Exemple avec les chats
    chats_file_path = loader.find_latest_json_file_path(data_type='chats')
    if chats_file_path:
        chats_data, _ = loader.load_json_to_dict(file_path=chats_file_path)
        chats_result = transformer.convert_chats_to_dataframe(chats_data)
        if isinstance(chats_result, dict):
            print("\n=== Aperçu du DataFrame des Chats ===")
            print(f"Forme des chats : {chats_result['chats'].shape}")
            print(f"Forme des messages : {chats_result['messages'].shape}")