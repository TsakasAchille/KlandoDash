import os
from typing import Dict, Optional, Union, List, Any, Tuple
import pandas as pd
from datetime import datetime

from src.data_processing.loaders.loader import Loader
from src.data_processing.transformer.dataframe_transformer import DataFrameTransformer
from src.data_processing.subscribers.trips_subscriber import TripsSubscriber
from src.data_processing.subscribers.users_subscriber import UsersSubscriber
from src.data_processing.subscribers.chats_subscriber import ChatsSubscriber
from src.core.settings import OUTPUT_DIRS


class DataManager:
    """
    Classe qui orchestre tout le processus de traitement des données:
    1. Collecte des données via les subscribers
    2. Chargement des fichiers JSON via le loader
    3. Transformation des données en DataFrames via le transformer
    4. Sauvegarde des résultats
    """
    
    def __init__(self):
        """Initialise le gestionnaire de données avec tous les composants nécessaires"""
        # Initialiser les subscribers
        self.trips_subscriber = TripsSubscriber()
        self.users_subscriber = UsersSubscriber()
        self.chats_subscriber = ChatsSubscriber()
        
        # Initialiser le loader et le transformer
        self.loader = Loader()
        self.transformer = DataFrameTransformer()
        
        # Attributs pour stocker les DataFrames
        self.df_trips = None
        self.df_users = None
        self.df_chats = None
        self.df_messages = None
        
        # Dictionnaire pour stocker les DataFrames (mantenu pour compatibilité)
        self.dataframes = {}
        
    def collect_data(self, data_type: str) -> bool:
        """
        Collecte les données depuis Firebase via le subscriber approprié
        
        Args:
            data_type (str): Type de données à collecter ('trips', 'users' ou 'chats')
            
        Returns:
            bool: True si la collecte a réussi, False sinon
        """
        try:
            if data_type == 'trips':
                # Utiliser directement run() qui combine récupération, traitement et sauvegarde
                return bool(self.trips_subscriber.run())
            
            elif data_type == 'users':
                # Utiliser directement run() qui combine récupération, traitement et sauvegarde
                return bool(self.users_subscriber.run())
            
            elif data_type == 'chats':
                # Utiliser directement run() qui combine récupération, traitement et sauvegarde
                return bool(self.chats_subscriber.run())
            
            else:
                print(f"Type de données non supporté: {data_type}")
                return False
                
        except Exception as e:
            print(f"Erreur lors de la collecte des données {data_type}: {e}")
            return False
    
    def load_data(self, data_type: str, file_path: str = None) -> Dict:
        """
        Charge les données depuis un fichier JSON ou le fichier le plus récent
        
        Args:
            data_type (str): Type de données à charger ('trips', 'users' ou 'chats')
            file_path (str, optional): Chemin vers un fichier spécifique à charger
            
        Returns:
            Dict: Dictionnaire contenant les données chargées
        """
        try:
            if file_path:
                data, _ = self.loader.load_json_to_dict(file_path=file_path)
            else:
                latest_file = self.loader.find_latest_json_file_path(data_type)
                if not latest_file:
                    print(f"Aucun fichier trouvé pour {data_type}")
                    return {}
                
                data, _ = self.loader.load_json_to_dict(file_path=latest_file)
                
            return data
        except Exception as e:
            print(f"Erreur lors du chargement des données {data_type}: {e}")
            return {}
    
    def transform_data(self, data_type: str, data: Dict) -> Dict[str, pd.DataFrame]:
        """
        Transforme les données en DataFrame selon leur type
        
        Args:
            data_type (str): Type de données à transformer ('trips', 'users' ou 'chats')
            data (Dict): Dictionnaire contenant les données à transformer
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionnaire de DataFrames transformés
        """
        try:
            if data_type == 'trips':
                df = self.transformer.convert_trips_to_dataframe(data)
                return {'trips': df} if df is not None else None
            
            elif data_type == 'users':
                df = self.transformer.convert_users_to_dataframe(data)
                return {'users': df} if df is not None else None
            
            elif data_type == 'chats':
                result = self.transformer.convert_chats_to_dataframe(data)
                if result is not None and isinstance(result, dict) and 'chats' in result and 'messages' in result:
                    return result
                return None
            
            else:
                print(f"Type de données non pris en charge: {data_type}")
                return None
        except Exception as e:
            print(f"Erreur lors de la transformation des données {data_type}: {e}")
            return None
    
    def save_dataframe(self, df: pd.DataFrame, data_type: str) -> Optional[str]:
        """
        Sauvegarde un DataFrame en CSV
        
        Args:
            df (pd.DataFrame): DataFrame à sauvegarder
            data_type (str): Type de données ('trips', 'users' ou 'chats')
            
        Returns:
            Optional[str]: Chemin du fichier sauvegardé ou None si erreur
        """
        return self.transformer.save_dataframe_to_csv(df, data_type)
    
    def process_data_type(self, data_type: str, collect: bool = False, file_path: str = None) -> Optional[Dict[str, pd.DataFrame]]:
        """
        Traite un type de données spécifique (collecte, chargement, transformation)
        
        Args:
            data_type (str): Type de données à traiter ('trips', 'users' ou 'chats')
            collect (bool): Si True, collecte de nouvelles données depuis Firebase
            file_path (str, optional): Chemin vers un fichier spécifique à charger
            
        Returns:
            Optional[Dict[str, pd.DataFrame]]: Dictionnaire de DataFrames résultants
        """
        # Étape 1: Collecter les données si demandé
        if collect:
            if not self.collect_data(data_type):
                print(f"Échec de la collecte des données {data_type}")
                return None
        
        # Étape 2: Charger les données
        data = self.load_data(data_type, file_path)
        if not data:
            print(f"Aucune donnée chargée pour {data_type}")
            return None
        
        # Étape 3: Transformer les données
        df_dict = self.transform_data(data_type, data)
        if df_dict is not None:
            # Stocker les DataFrames pour une utilisation ultérieure
            if data_type == 'trips' and 'trips' in df_dict:
                self.df_trips = df_dict['trips']
            elif data_type == 'users' and 'users' in df_dict:
                self.df_users = df_dict['users']
            elif data_type == 'chats':
                if 'chats' in df_dict:
                    self.df_chats = df_dict['chats']
                if 'messages' in df_dict:
                    self.df_messages = df_dict['messages']
            
            # Stocker le dictionnaire de DataFrames (pour compatibilité)
            self.dataframes[data_type] = df_dict
            
            # Afficher des informations sur les DataFrames
            for name, df in df_dict.items():
                if df is not None:
                    print(f"\n=== DataFrame {name} ===")
                    print(f"Forme: {df.shape}")
                    print(f"Colonnes: {df.columns.tolist()[:10]}{'...' if len(df.columns) > 10 else ''}")
        
        return df_dict
    
    def process_all_data(self, collect: bool = False) -> Dict[str, Any]:
        """
        Traite tous les types de données supportés
        
        Args:
            collect (bool): Si True, collecte de nouvelles données pour tous les types
            
        Returns:
            Dict[str, Any]: Dictionnaire contenant tous les DataFrames générés
        """
        result = {}
        
        for data_type in ['trips', 'users', 'chats']:
            print(f"\nTraitement des données {data_type}...")
            df = self.process_data_type(data_type, collect)
            if df is not None:
                result[data_type] = df
        
        return result
    
    def get_dataframe(self, data_type: str) -> Optional[Union[pd.DataFrame, Dict[str, pd.DataFrame]]]:
        """
        Récupère un DataFrame précédemment généré
        
        Args:
            data_type (str): Type de données ('trips', 'users' ou 'chats')
            
        Returns:
            Optional[Union[pd.DataFrame, Dict[str, pd.DataFrame]]]: DataFrame(s) demandé(s)
        """
        if data_type == 'trips':
            return self.df_trips
        elif data_type == 'users':
            return self.df_users
        elif data_type == 'chats':
            return {'chats': self.df_chats, 'messages': self.df_messages}
        else:
            return None


# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le gestionnaire de données
    data_manager = DataManager()
    
    # Exemples d'utilisation:
    """
    # Option 1: Traiter un type de données spécifique
    print("=== Traitement des trajets ===")
    trips_df = data_manager.process_data_type('trips')
    
    # Option 2: Collecter de nouvelles données et les traiter
    print("\n=== Collecte et traitement des utilisateurs ===")
    users_df = data_manager.process_data_type('users', collect=True)
    
    # Option 3: Traiter tous les types de données
    print("\n=== Traitement de toutes les données ===")
    all_data = data_manager.process_all_data()
    """
    

    
    # Utiliser les données
    """
    if trips_df is not None:
        # Exemple: Sauvegarder en CSV
        data_manager.save_dataframe(trips_df, 'trips')
    """
