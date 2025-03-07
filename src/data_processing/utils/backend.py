import json
import os
import glob
from datetime import datetime
import math
import pandas as pd

class Trip:
    def __init__(self, trip_id, trip_data):
        """
        Initialise un objet Trip à partir des données brutes
        Args:
            trip_id (str): Identifiant du trajet
            trip_data (dict): Données brutes du trajet
        """
        self.id = trip_id
        self.departure_date = self._parse_date(trip_data.get('departure_date', ''))
        self.departure_point = trip_data.get('departure_name', '')
        self.destination = trip_data.get('destination_name', '')
        self.region = trip_data.get('region', '')
        self.driver_id = trip_data.get('driver_reference', '').replace('users/', '')
        self.distance = float(trip_data.get('trip_distance', 0))
        self.price_per_seat = float(trip_data.get('price_per_seat', 0))
        self.total_seats = int(trip_data.get('number_of_seats', 0))
        self.reserved_seats = len(trip_data.get('all_passengers', []))
        
    def _parse_date(self, date_str):
        """Parse une date ISO en datetime"""
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            return None
            
    @property
    def available_seats(self):
        """Retourne le nombre de places disponibles"""
        return self.total_seats - self.reserved_seats
        
    @property
    def formatted_date(self):
        """Retourne la date formatée en français"""
        return self.departure_date.strftime('%d/%m/%Y') if self.departure_date else ''
        
    @property
    def formatted_distance(self):
        """Retourne la distance formatée"""
        return f"{self.distance:.1f} km"
        
    @property
    def formatted_price(self):
        """Retourne le prix formaté"""
        return f"{self.price_per_seat:,.0f} XOF"
        
    @property
    def formatted_seats(self):
        """Retourne les places formatées"""
        return f"{self.available_seats}/{self.total_seats}"
        
    def to_dict(self):
        """Convertit l'objet en dictionnaire pour l'affichage"""
        return {
            'id': self.id,
            'departure_date': self.departure_date,  # Date brute pour le tri
            'formatted_date': self.formatted_date,  # Date formatée pour l'affichage
            'departure_point': self.departure_point,
            'destination': self.destination,
            'region': self.region,
            'driver_id': self.driver_id,
            'distance': self.distance,  # Nombre pour le tri
            'formatted_distance': self.formatted_distance,  # Pour l'affichage
            'price': self.price_per_seat,  # Nombre pour le tri
            'formatted_price': self.formatted_price,  # Pour l'affichage
            'total_seats': self.total_seats,
            'reserved_seats': self.reserved_seats,
            'available_seats': self.available_seats,
            'formatted_seats': self.formatted_seats
        }

class Backend:
    def __init__(self):
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
        self.kpi_data = None
        self.load_kpi_data()

    def determine_region(self, lat, lon):
        """
        Détermine la région en fonction des coordonnées données
        en trouvant la région la plus proche
        """
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

    def get_all_data_files(self, pattern):
        """
        Trouve tous les fichiers de données correspondant au pattern et les trie par date.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        raw_dir = os.path.join(base_dir, 'data', 'raw')
        trips_dir = os.path.join(raw_dir, 'trips')
        user_dir = os.path.join(raw_dir, 'user')
        
        files = []
        
        if os.path.exists(trips_dir) and pattern.startswith('trips'):
            trip_files = glob.glob(os.path.join(trips_dir, pattern))
            files.extend(trip_files)
        
        if os.path.exists(user_dir) and pattern.startswith('users'):
            user_files = glob.glob(os.path.join(user_dir, pattern))
            files.extend(user_files)
        
        raw_files = glob.glob(os.path.join(raw_dir, pattern))
        files.extend(raw_files)
        
        if not files:
            return []

        def extract_date(filename):
            try:
                basename = os.path.basename(filename)
                date_str = basename.split('_')[-1].split('.')[0]
                if len(date_str) == 8 and date_str.isdigit():
                    return datetime.strptime(date_str + "235959", '%Y%m%d%H%M%S')
                else:
                    return datetime.fromtimestamp(os.path.getmtime(filename))
            except:
                return datetime.fromtimestamp(os.path.getmtime(filename))

        return sorted([(f, extract_date(f)) for f in files], key=lambda x: x[1], reverse=True)

    def load_kpi_data(self):
        """
        Charge les données KPI depuis le fichier le plus récent
        """
        files = self.get_all_data_files('kpi_data*.json')
        if files:
            latest_file = files[0][0]
            try:
                with open(latest_file, 'r') as f:
                    self.kpi_data = json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement des données KPI: {e}")
                self.kpi_data = {}

    def get_kpi_data(self):
        """
        Retourne les données KPI
        """
        return self.kpi_data or {}

    def get_trips(self, file_path=None):
        """
        Récupère et formate les données des trajets depuis un fichier spécifique ou le plus récent
        Args:
            file_path (str, optional): Chemin vers le fichier à utiliser. Si non fourni, utilise le plus récent.
        Returns:
            list: Liste des trajets formatés
        """
        try:
            print("Getting trips data...")
            print(f"File path: {file_path}")

            # Utiliser le fichier spécifié ou trouver le plus récent
            if file_path and os.path.isfile(file_path):
                latest_trip_file = file_path
            else:
                files = self.get_all_data_files('trips_data*.json')
                if not files:
                    print("Aucun fichier de trajets trouvé")
                    return []
                latest_trip_file = files[0][0]

            print(f"Chargement des trajets depuis : {latest_trip_file}")
            
            with open(latest_trip_file, 'r') as f:
                trips_data = json.load(f)
                
            # Convertir les données brutes en objets Trip
            trips = []
            for trip_id, trip_wrapper in trips_data.items():
                if isinstance(trip_wrapper, dict) and 'data' in trip_wrapper:
                    trip = Trip(trip_id, trip_wrapper['data'])
                    trips.append(trip.to_dict())
            
            print(f"Retour des trajets : {len(trips)} trajets")
            return trips
            
        except Exception as e:
            print(f"Erreur lors du chargement des trajets : {e}")
            return []

    def get_latest_json_file(pattern: str) -> str:
        """Trouve le fichier JSON le plus récent correspondant au pattern."""
        files = glob.glob(pattern)
        return max(files, key=os.path.getctime) if files else None

    def load_json_data(self, file_path: str) -> dict:
        """Charge les données depuis un fichier JSON."""
        with open(file_path, 'r') as f:
            return json.load(f)

    def json_to_dataframe(self, json_data, record_path=None, meta=None):
        """
        Convertit des données JSON en DataFrame pandas
        Args:
            json_data (dict): Données JSON à convertir
            record_path (str/list): Chemin vers les enregistrements dans le JSON imbriqué
            meta (list): Liste des métadonnées à inclure du niveau supérieur
        Returns:
            pd.DataFrame: DataFrame contenant les données
        """
        try:
            if not json_data:
                print("Aucune donnée JSON fournie")
                return pd.DataFrame()
            
            # Utiliser json_normalize pour aplatir le JSON
            df = pd.json_normalize(
                data=json_data,
                record_path=record_path,
                meta=meta,
                errors='ignore'
            )
            
            return df
            
        except Exception as e:
            print(f"Erreur lors de la conversion en DataFrame : {e}")
            return pd.DataFrame()

    def load_json_to_dataframe(self, file_path=None, pattern=None, record_path=None, meta=None):
        """
        Charge un fichier JSON et le convertit directement en DataFrame
        Args:
            file_path (str, optional): Chemin direct vers le fichier
            pattern (str, optional): Pattern pour chercher le fichier le plus récent
            record_path (str/list): Chemin vers les enregistrements dans le JSON
            meta (list): Liste des métadonnées à inclure
        Returns:
            pd.DataFrame: DataFrame contenant les données
            str: Chemin du fichier utilisé
        """
        # Charger le JSON
        data, file_used = self.load_json_to_dict(file_path, pattern)
        
        # Convertir en DataFrame
        df = self.json_to_dataframe(data, record_path, meta)
        
        return df, file_used

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

    def get_users(self):
        """
        Récupère et formate les données des utilisateurs depuis le fichier le plus récent
        Returns:
            list: Liste des utilisateurs formatés
        """
        print("Getting users data...")
        try:
            # Trouver le fichier d'utilisateurs le plus récent
            user_files = self.get_all_data_files('users_data*.json')
            
            if not user_files:
                raise FileNotFoundError("Aucun fichier d'utilisateurs trouvé")
            
            # Trier par date de modification (le plus récent en premier)
            latest_user_file = max(user_files, key=lambda x: x[1])[0]
            print(f"Chargement des utilisateurs depuis : {latest_user_file}")
            
            with open(latest_user_file, 'r') as f:
                users_data = json.load(f)
                
            # Formater les données pour le tableau
            formatted_users = []
            for user_id, user_wrapper in users_data.items():
                if isinstance(user_wrapper, dict) and 'data' in user_wrapper:
                    user_data = user_wrapper['data']
                    formatted_user = {
                        'id': user_id,
                        'full_name': user_data.get('display_name', ''),
                        'email': user_data.get('email', ''),
                        'age': user_data.get('age', ''),
                        'phone': user_data.get('phone_number', ''),
                        'registration_date': user_data.get('created_time', ''),
                        'status': 'active'
                    }
                    formatted_users.append(formatted_user)
            
            print(f"Retour des utilisateurs : {len(formatted_users)} utilisateurs")
            return formatted_users
            
        except Exception as e:
            print(f"Erreur lors du chargement des utilisateurs : {e}")
            return []

def main():
    """Test la récupération des trajets"""
    backend = Backend()
    trips = backend.get_trips()
    if trips:
        print(f"Nombre de trajets trouvés : {len(trips)}")
        print("Premier trajet :")
        print(json.dumps(trips[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()