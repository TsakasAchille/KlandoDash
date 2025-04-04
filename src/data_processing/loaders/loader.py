import os
import json
import glob
from typing import Optional, Dict, Any, Tuple
from src.core.settings import OUTPUT_DIRS, ensure_dir

"""
Le but de cette classe est de charger les fichiers JSON créés par les subscribers
"""

class Loader:
    def __init__(self):
        """
        Initialise le loader avec les chemins de sortie configurés
        """
        # Utiliser les chemins définis dans settings.py
        self.output_dirs = OUTPUT_DIRS

    def load_json_to_dict(self, file_path=None, pattern=None) -> Tuple[Dict, Optional[str]]:
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

    def load_json_data(self, file_path) -> Dict:
        """
        Charge un fichier JSON
        Args:
            file_path (str): Chemin vers le fichier JSON
        Returns:
            dict: Dictionnaire contenant les données
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement du fichier {file_path}: {e}")
            return {}

    def get_latest_json_file(self, pattern) -> Optional[str]:
        """
        Récupère le fichier JSON le plus récent correspondant au pattern
        Args:
            pattern (str): Pattern de recherche
        Returns:
            str: Chemin vers le fichier le plus récent
        """
        files = glob.glob(pattern)
        if not files:
            return None
        return max(files, key=os.path.getmtime)

    def _check_json_file(self, file_path) -> bool:
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

    def find_latest_json_file_path(self, data_type: str) -> Optional[str]:
        """
        Cherche le fichier JSON le plus récent dans le dossier configuré
        Args:
            data_type (str): Type de données (ex: 'trips', 'users', 'chats')
        Returns:
            Optional[str]: Chemin vers le fichier le plus récent ou None si non trouvé
        """
        # Vérifier que le type de données est supporté
        if data_type not in self.output_dirs:
            raise ValueError(f"Type de données non supporté: {data_type}. Types disponibles: {list(self.output_dirs.keys())}")
        
        # Obtenir le chemin du dossier pour ce type de données
        data_dir = self.output_dirs[data_type]
        
        # Construire le pattern de recherche
        pattern = os.path.join(data_dir, f"{data_type}_data*.json")
        print(f"Recherche de fichiers avec le pattern: {pattern}")
        
        # Récupérer tous les fichiers correspondant au pattern
        files = glob.glob(pattern)
        if not files:
            print(f"Aucun fichier trouvé pour {data_type} dans {data_dir}")
            return None
            
        # Retourner le fichier le plus récent
        return max(files, key=os.path.getmtime)


if __name__ == "__main__":
    loader = Loader()
    
    # Exemple avec les trajets
    trips_file_path = loader.find_latest_json_file_path(data_type='trips')
    if trips_file_path:
        trips_data, _ = loader.load_json_to_dict(file_path=trips_file_path)
        print(f"Données chargées depuis {trips_file_path}")
        print(f"Nombre de trajets: {len(trips_data)}")
    
    # Exemple avec les utilisateurs
    users_file_path = loader.find_latest_json_file_path(data_type='users')
    if users_file_path:
        users_data, _ = loader.load_json_to_dict(file_path=users_file_path)
        print(f"Données chargées depuis {users_file_path}")
        print(f"Nombre d'utilisateurs: {len(users_data)}")
    
    # Exemple avec les chats
    chats_file_path = loader.find_latest_json_file_path(data_type='chats')
    if chats_file_path:
        chats_data, _ = loader.load_json_to_dict(file_path=chats_file_path)
        print(f"Données chargées depuis {chats_file_path}")
        print(f"Nombre de chats: {len(chats_data)}")