import os
import json
import pandas as pd

from typing import Optional  # Ajoutez cet import en haut du fichier

from ressources.config import CONFIG
import glob

"""
Le but de cette classe est de souscrire au fichier Json souscrit et créer par les subscriber

"""

class Loader:
    def __init__(self):

        self.raw_data_trips_path  = CONFIG['data_raw_trips']
        self.raw_data_users_path = CONFIG['data_raw_users']

    def load_json_to_dict(self, file_path=None, pattern=None):
        """
        Charge un fichier JSON et le convertit en dictionnaire
        Args:
            file_path (str, optional): Chemin direct vers le fichier
            pattern (str, optional): Pattern pour chercher le fichier le plus récent
        Returns:
            dict: Dictionnaire contenant les données
            str: Chemin du fichier utilisé
        """
        if file_path and os.path.isfile(file_path):
            file_used = file_path
            data = self.load_json_data(file_path)
        else:
            if pattern:
                file_used = self.get_latest_json_file(pattern)
                if file_used:
                    data = self.load_json_data(file_used)
                else:
                    print("Aucun fichier trouvé")
                    return {}, None
            else:
                print("Aucun fichier ou pattern fourni")
                return {}, None
        
        return data, file_used


    def _check_json_file(self, file_path):
       """
       Vérifie si un fichier JSON existe et est valide
       Args:
           file_path (str): Chemin vers le fichier JSON
       Returns:
           bool: True si le fichier existe et est un JSON valide, False sinon
       """
       # Vérifier que le chemin existe
       if not os.path.exists(file_path):
           print(f"Erreur: Le fichier {file_path} n'existe pas")
           return False
           
       # Vérifier que c'est bien un fichier JSON
       if not file_path.endswith('.json'):
           print(f"Erreur: Le fichier {file_path} n'est pas un fichier JSON")
           return False
       
       return True


    def save_dataframe_to_csv(self, df: pd.DataFrame, data_type: str) -> Optional[str]:
        """
        Sauvegarde un DataFrame en CSV dans le dossier approprié
        Args:
            df (pd.DataFrame): DataFrame à sauvegarder
            data_type (str): Type de données ('trips' ou 'users')
        Returns:
            Optional[str]: Chemin du fichier CSV créé ou None si erreur
        """
        try:
            # Créer le nom du fichier avec la date
            timestamp = pd.Timestamp.now().strftime('%Y%m%d')
            filename = f"{data_type}_data_{timestamp}.csv"
            
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


    def find_latest_json_file_path(self, data_type: str) -> Optional[str]:
        """
        Cherche le fichier JSON le plus récent dans le dossier configuré
        Args:
            data_type (str): Type de données (ex: 'trips', 'users', etc.)
        Returns:
            Optional[str]: Chemin vers le fichier le plus récent ou None si non trouvé
        """
        # Mapping des types de données vers leurs chemins
        data_paths = {
            'trips': self.raw_data_trips_path,
            'users': self.raw_data_users_path
            # Ajouter d'autres types ici si nécessaire
        }
        
        if data_type not in data_paths:
            raise ValueError(f"Type de données non supporté: {data_type}. Types disponibles: {list(data_paths.keys())}")
        
        # Obtenir le chemin absolu du projet
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # Construire le chemin complet
        base_path = os.path.join(project_root, data_paths[data_type])
        
        # Construire le pattern de recherche
        pattern = os.path.join(base_path, f"{data_type}_data*.json")
        
        files = glob.glob(pattern)
        if not files:
            print(f"Aucun fichier trouvé pour {data_type} dans {base_path}")
            return None
            
        return max(files, key=os.path.getmtime)

    def convert_json_to_dataframe(self,file_path: str, record_path: str = None, meta: list = None) -> Optional[pd.DataFrame]:
        """
        Charge un fichier JSON et le convertit en DataFrame
        
        Args:
            file_path (str): Chemin vers le fichier JSON à charger
            record_path (str, optional): Chemin vers les enregistrements dans le JSON
            meta (list, optional): Liste des métadonnées à inclure
            
        Returns:
            Optional[pd.DataFrame]: DataFrame contenant les données du JSON,
                                  None si une erreur survient
        """
        if not self._check_json_file(file_path):
            return None
    
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return pd.json_normalize(
                data=data,
                record_path=record_path,
                meta=meta,
                errors='ignore'
            )
        except Exception as e:
            print(f"Erreur lors du chargement du fichier {file_path}: {e}")
            return None


    


if __name__ == "__main__":
    loader = Loader()
    trips_file_path = loader.find_latest_json_file_path(data_type='trips')
    # trips_df = loader.convert_trips_json_to_dataframe(trips_file_path)
    
    loader.save_dataframe_to_csv(trips_df, 'trips')

    print("\n=== Aperçu du DataFrame des Trips ===")
    print(f"Forme : {trips_df.shape}")
    print("\nColonnes :")
    print(trips_df.columns.tolist())
    print("\nPremières lignes :")
    print(trips_df.head())