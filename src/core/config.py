import os
import json
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Config:
    """Class for managing application configuration"""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialisation de la configuration"""
        if not hasattr(self, '_initialized') or not self._initialized:
            self._config = {}
            self._initialize()
            self._initialized = True
    
    def _find_project_dir(self) -> str:
        """Trouve le répertoire racine du projet en cherchant le fichier .env
        
        Returns:
            str: Chemin absolu vers le répertoire racine du projet
        """
        # Démarrer par le répertoire courant
        current_dir = os.path.abspath(os.getcwd())
        
        # Remonter dans l'arborescence jusqu'à trouver le .env
        while current_dir != os.path.dirname(current_dir):  # S'arrêter au répertoire racine
            if os.path.isfile(os.path.join(current_dir, '.env')):
                return current_dir
            current_dir = os.path.dirname(current_dir)
        
        # Si on arrive ici, on n'a pas trouvé le .env
        # Utiliser le répertoire courant comme fallback
        return os.getcwd()
    
    def _initialize(self) -> None:
        """Initialise la configuration en chargeant les variables d'environnement seulement
        
        La configuration est uniquement basée sur les variables définies dans le fichier .env.
        """
        # Réinitialiser la configuration
        self._config = {}
        
        # Trouver le répertoire du projet en localisant le fichier .env
        self.project_dir = self._find_project_dir()
        print(f"Répertoire du projet détecté: {self.project_dir}")
        
        # Utiliser la valeur de PROJECT_DIR si elle est définie dans .env, sinon conserver le répertoire détecté
        env_project_dir = os.environ.get('PROJECT_DIR')
        if env_project_dir and os.path.isdir(env_project_dir):
            self.project_dir = env_project_dir
            print(f"Répertoire du projet remplacé par la valeur de PROJECT_DIR: {self.project_dir}")
        
        self.config_path = os.environ.get('CONFIG', 'resources/config/config.json')
        
        # Récupérer le chemin de la clé Firebase et le rendre relatif au répertoire du projet
        firebase_key_rel_path = os.environ.get('FIREBASE_KEY_PATH')
        if firebase_key_rel_path:
            self.firebase_key_path = os.path.join(self.project_dir, firebase_key_rel_path)
        else:
            self.firebase_key_path = None
        
        # Stocker les chemins de base dans la configuration
        self._config['paths'] = {
            'project_dir': self.project_dir,
            'config_path': self.config_path
        }
        
        if self.firebase_key_path:
            if 'firebase' not in self._config:
                self._config['firebase'] = {}
            self._config['firebase']['key_path'] = self.firebase_key_path
        
        print("Configuration initialisée depuis les variables d'environnement")
        if self.firebase_key_path:
            print(f"Clé Firebase configurée: {self.firebase_key_path}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur de configuration par sa clé
        
        Args:
            key (str): Clé de configuration à récupérer
            default (Any, optional): Valeur par défaut si la clé n'existe pas
            
        Returns:
            Any: Valeur de configuration
        """
        # Cas particulier pour les variables d'environnement
        if key == 'firebase.key_path':
            return self.firebase_key_path
        
        # Support for nested keys with dot notation
        if '.' in key:
            parts = key.split('.')
            config = self._config
            for part in parts[:-1]:
                if part not in config:
                    return default
                config = config[part]
            return config.get(parts[-1], default)
        
        return self._config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Récupère toutes les configurations
        
        Returns:
            Dict[str, Any]: Dictionnaire de configuration complet
        """
        # Créer une copie pour éviter les modifications directes
        return self._config.copy()
    
    def set(self, key: str, value: Any) -> None:
        """Définit une valeur de configuration
        
        Args:
            key (str): Clé de configuration à définir
            value (Any): Valeur à associer à la clé
        """
        # Support for nested keys with dot notation
        if '.' in key:
            parts = key.split('.')
            config = self._config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            config[parts[-1]] = value
        else:
            self._config[key] = value
    
    def save(self, config_file: Optional[str] = None) -> bool:
        """Sauvegarde la configuration dans un fichier JSON
        
        Args:
            config_file (str, optional): Chemin du fichier où sauvegarder. Si None, utilise le chemin par défaut.
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        if config_file is None:
            config_file = self.config_path
            if not os.path.isabs(config_file):
                config_file = os.path.join(self.project_dir, config_file)
        
        try:
            # Créer le répertoire parent si nécessaire
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
            print(f"Configuration sauvegardée dans: {config_file}")
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def load_json(self, json_file: str) -> Dict[str, Any]:
        """Charge un fichier JSON
        
        Args:
            json_file (str): Chemin vers le fichier JSON à charger
            
        Returns:
            Dict[str, Any]: Contenu du fichier JSON, ou dictionnaire vide en cas d'erreur
        """
        # Si le chemin n'est pas absolu, le construire relatif au répertoire du projet
        if not os.path.isabs(json_file):
            json_file = os.path.join(self.project_dir, json_file)
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Fichier JSON chargé depuis: {json_file}")
            return data
        except FileNotFoundError:
            print(f"Fichier JSON introuvable: {json_file}")
            return {}
        except json.JSONDecodeError:
            print(f"Format de fichier JSON invalide: {json_file}")
            return {}
        except Exception as e:
            print(f"Erreur lors du chargement du fichier JSON: {e}")
            return {}
    
    def merge_config(self, config_data: Dict[str, Any]) -> None:
        """Fusionne les données de configuration avec la configuration existante
        
        Args:
            config_data (Dict[str, Any]): Données de configuration à fusionner
        """
        def deep_merge(source, destination):
            """Fusion récursive de dictionnaires"""
            for key, value in source.items():
                if key in destination and isinstance(destination[key], dict) and isinstance(value, dict):
                    deep_merge(value, destination[key])
                else:
                    destination[key] = value
            return destination
        
        self._config = deep_merge(config_data, self._config)
        print("Configuration fusionnée avec succès")