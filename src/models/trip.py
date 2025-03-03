from datetime import datetime

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
        if not date_str:
            return None
            
        try:
            # Pour Python 3.8, utilisons un moyen plus robuste de parser les dates ISO
            from dateutil import parser
            return parser.isoparse(date_str)
        except ImportError:
            # Fallback si dateutil n'est pas disponible
            try:
                # Nettoyer le format de date pour être compatible avec fromisoformat
                if 'Z' in date_str:
                    date_str = date_str.replace('Z', '+00:00')
                return datetime.fromisoformat(date_str)
            except Exception as e:
                print(f"Erreur lors du parsing de la date '{date_str}': {e}")
                return None
        except Exception as e:
            print(f"Erreur lors du parsing de la date '{date_str}': {e}")
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