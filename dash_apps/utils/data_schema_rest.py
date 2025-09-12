"""
Utilitaires pour accéder aux schémas de données via l'API REST Supabase
Version adaptée de data_schema.py qui utilise l'API REST au lieu de la connexion PostgreSQL directe
"""
import json
import os
import pandas as pd
from pathlib import Path
import logging
from dash_apps.utils.supabase_client import supabase

# Logger
logger = logging.getLogger(__name__)

# Chemin vers les fichiers de définition basé sur la structure du projet
BASE_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DEF_DIR = BASE_DIR / "dash_apps" / "utils" / "data_definition"

# Créer le répertoire s'il n'existe pas
os.makedirs(DATA_DEF_DIR, exist_ok=True)

def get_type_mapping(type_str):
    """Convertit le type de données PostgreSQL en type Python"""
    type_map = {
        'text': str,
        'varchar': str,
        'integer': int,
        'bigint': int,
        'double precision': float,
        'numeric': float,
        'boolean': bool,
        'date': str,  # On garde les dates comme des chaînes
        'timestamp with time zone': str,
        'timestamp without time zone': str,
        'uuid': str,
    }
    return type_map.get(type_str.lower(), str)

def load_table_definition(table_name):
    """Charge la définition d'une table à partir du fichier JSON correspondant"""
    try:
        file_path = DATA_DEF_DIR / f"{table_name}.json"
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la définition de {table_name}: {e}")
        return []

def load_keys():
    """Charge les relations de clés étrangères à partir du fichier keys.json"""
    try:
        file_path = DATA_DEF_DIR / "keys.json"
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement des clés: {e}")
        return []

def get_table_schema(table_name):
    """Retourne le schéma d'une table basé sur sa définition JSON"""
    table_def = load_table_definition(table_name)
    return {col["column_name"]: col["data_type"] for col in table_def}

def get_all_from_table(table_name, conditions=None, limit=None):
    """Récupère toutes les données d'une table avec conditions optionnelles"""
    try:
        query = supabase.table(table_name).select("*")
        
        # Appliquer les conditions si spécifiées (simplifié - ne gère pas toutes les conditions SQL)
        if conditions:
            # Pour garder la compatibilité, on accepte une chaîne simple mais idéalement
            # les conditions devraient être un dictionnaire {colonne: valeur}
            if isinstance(conditions, dict):
                for col, val in conditions.items():
                    query = query.eq(col, val)
            elif isinstance(conditions, str) and "=" in conditions:
                # Tentative simple de parser une condition de type "colonne = valeur"
                parts = conditions.split("=")
                if len(parts) == 2:
                    col = parts[0].strip()
                    val = parts[1].strip().replace("'", "")  # Enlever les guillemets simples
                    query = query.eq(col, val)
        
        # Appliquer la limite si spécifiée
        if limit:
            query = query.limit(limit)
            
        response = query.execute()
        
        # Convertir en DataFrame
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données de {table_name}: {e}")
        return pd.DataFrame()

def get_trips():
    """Récupère tous les trajets de la base de données"""
    return get_all_from_table("trips")

def get_trip_by_id(trip_id):
    """Récupère un trajet par son ID"""
    try:
        logger.info(f"[TRIP_DEBUG] Recherche du trajet {trip_id} dans Supabase")
        response = supabase.table("trips").select("*").eq("trip_id", trip_id).execute()
        
        if response.data:
            logger.info(f"[TRIP_DEBUG] Trajet {trip_id} trouvé avec {len(response.data)} résultats")
            return response.data[0]
        
        logger.warning(f"[TRIP_DEBUG] Trajet {trip_id} non trouvé dans la base de données")
        return None
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du trajet {trip_id}: {e}")
        return None

def get_bookings_for_trip(trip_id):
    """Récupère toutes les réservations pour un trajet donné"""
    try:
        response = supabase.table("bookings").select("*").eq("trip_id", trip_id).execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des réservations pour le trajet {trip_id}: {e}")
        return pd.DataFrame()

def get_passengers_for_trip(trip_id):
    """Récupère tous les passagers d'un trajet (avec leurs informations)"""
    try:
        # Cette requête est plus complexe car elle nécessite une jointure
        # Pour l'API REST, nous devons la décomposer en deux requêtes
        
        # 1. Récupérer les IDs des passagers
        bookings_response = supabase.table("bookings").select("user_id").eq("trip_id", trip_id).execute()
        
        if not bookings_response.data:
            return pd.DataFrame()
        
        # 2. Récupérer les informations des utilisateurs pour ces IDs
        user_ids = [booking["user_id"] for booking in bookings_response.data]
        
        # Supabase ne supporte pas directement les requêtes IN, nous devons faire des requêtes multiples
        # ou utiliser le filtrage côté client
        all_users = []
        for user_id in user_ids:
            user_response = supabase.table("users").select("*").eq("uid", user_id).execute()
            if user_response.data:
                all_users.extend(user_response.data)
        
        return pd.DataFrame(all_users)
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des passagers pour le trajet {trip_id}: {e}")
        return pd.DataFrame()

def get_trips_for_user(user_id, as_driver=False, as_passenger=False):
    """
    Récupère tous les trajets d'un utilisateur
    Si as_driver=True, retourne uniquement les trajets où l'utilisateur est conducteur
    Si as_passenger=True, retourne uniquement les trajets où l'utilisateur est passager
    Si les deux sont False, retourne tous les trajets de l'utilisateur
    """
    try:
        trips_data = []
        
        # Trajets en tant que conducteur
        if as_driver or (not as_driver and not as_passenger):
            driver_response = supabase.table("trips").select("*").eq("driver_id", user_id).execute()
            if driver_response.data:
                trips_data.extend(driver_response.data)
        
        # Trajets en tant que passager
        if as_passenger or (not as_driver and not as_passenger):
            # 1. Récupérer les IDs des trajets où l'utilisateur est passager
            bookings_response = supabase.table("bookings").select("trip_id").eq("user_id", user_id).execute()
            
            if bookings_response.data:
                # 2. Récupérer les détails des trajets
                trip_ids = [booking["trip_id"] for booking in bookings_response.data]
                
                # Récupérer les trajets un par un (limitation de l'API Supabase)
                for trip_id in trip_ids:
                    trip_response = supabase.table("trips").select("*").eq("trip_id", trip_id).execute()
                    if trip_response.data:
                        trips_data.extend(trip_response.data)
        
        # Éliminer les doublons (si l'utilisateur est à la fois conducteur et passager)
        unique_trips = []
        trip_ids_seen = set()
        
        for trip in trips_data:
            if trip["trip_id"] not in trip_ids_seen:
                unique_trips.append(trip)
                trip_ids_seen.add(trip["trip_id"])
        
        # Trier par date de départ (ordre descendant)
        sorted_trips = sorted(unique_trips, key=lambda x: x.get("departure_schedule", ""), reverse=True)
        
        return pd.DataFrame(sorted_trips)
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des trajets pour l'utilisateur {user_id}: {e}")
        return pd.DataFrame()

def get_user_profile(user_id):
    """
    Récupère les données de profil d'un utilisateur par son ID
    """
    try:
        logger.info(f"[PROFILE_DEBUG] Récupération du profil pour l'utilisateur {user_id}")
        response = supabase.table("users").select("*").eq("uid", user_id).execute()
        
        if response.data:
            user_data = response.data[0]
            # Vérifier et traiter le champ photo_url
            if 'photo_url' in user_data:
                logger.info(f"[PROFILE_DEBUG] Photo URL trouvée: {user_data['photo_url']}")
            else:
                logger.warning(f"[PROFILE_DEBUG] Aucune photo_url trouvée pour l'utilisateur {user_id}")
                # Si l'API renvoie un champ avec un autre nom contenant l'URL de la photo
                for field in ['avatar', 'profile_picture', 'picture', 'image', 'avatar_url']:
                    if field in user_data and user_data[field]:
                        logger.info(f"[PROFILE_DEBUG] Champ alternatif trouvé pour la photo: {field}")
                        user_data['photo_url'] = user_data[field]
                        break
            
            # Afficher tous les champs disponibles pour le débogage
            logger.info(f"[PROFILE_DEBUG] Champs disponibles: {list(user_data.keys())}")
            return user_data
        
        logger.warning(f"[PROFILE_DEBUG] Aucune donnée trouvée pour l'utilisateur {user_id}")
        return None
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil utilisateur {user_id}: {e}")
        return None

def get_user_stats_optimized(user_id):
    """
    Récupère les statistiques d'un utilisateur
    """
    try:
        # Cette requête complexe avec jointures doit être décomposée en requêtes plus simples
        logger.info(f"[STATS_DEBUG] Calcul des statistiques pour l'utilisateur {user_id}")
        
        # 1. Statistiques en tant que conducteur
        driver_trips_response = supabase.table("trips").select("*").eq("driver_id", user_id).execute()
        driver_trips = driver_trips_response.data if driver_trips_response.data else []
        
        driver_trips_count = len(driver_trips)
        driver_distance = sum(trip.get("distance", 0) or 0 for trip in driver_trips)
        
        logger.info(f"[STATS_DEBUG] Trajets conducteur: {driver_trips_count}, distance: {driver_distance}")
        logger.info(f"[STATS_DEBUG] URL requête conducteur: {driver_trips_response.url if hasattr(driver_trips_response, 'url') else 'N/A'}")
        
        # 2. Statistiques en tant que passager
        # a. Récupérer les réservations de l'utilisateur
        bookings_response = supabase.table("bookings").select("trip_id").eq("user_id", user_id).execute()
        passenger_trips_ids = [booking["trip_id"] for booking in bookings_response.data] if bookings_response.data else []
        
        logger.info(f"[STATS_DEBUG] Nombre de réservations trouvées: {len(passenger_trips_ids)}")
        
        # b. Récupérer les détails des trajets
        passenger_trips = []
        for trip_id in passenger_trips_ids:
            trip_response = supabase.table("trips").select("*").eq("trip_id", trip_id).execute()
            if trip_response.data:
                passenger_trips.extend(trip_response.data)
        
        passenger_trips_count = len(passenger_trips)
        passenger_distance = sum(trip.get("distance", 0) or 0 for trip in passenger_trips)
        
        logger.info(f"[STATS_DEBUG] Trajets passager: {passenger_trips_count}, distance: {passenger_distance}")
        
        # 3. Calculer les totaux
        total_trips = driver_trips_count + passenger_trips_count
        total_distance = driver_distance + passenger_distance
        
        logger.info(f"[STATS_DEBUG] Totaux - trajets: {total_trips}, distance: {total_distance}")
        
        return {
            'driver_trips_count': driver_trips_count,
            'driver_distance': driver_distance,
            'passenger_trips_count': passenger_trips_count,
            'passenger_distance': passenger_distance,
            'total_trips': total_trips,
            'total_distance': total_distance
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques pour l'utilisateur {user_id}: {e}")
        return {
            'driver_trips_count': 0,
            'driver_distance': 0,
            'passenger_trips_count': 0,
            'passenger_distance': 0,
            'total_trips': 0,
            'total_distance': 0
        }

def get_trip_stats_optimized(trip_id):
    """
    Récupère les statistiques d'un trajet
    """
    try:
        # 1. Récupérer les détails du trajet
        trip_response = supabase.table("trips").select("*").eq("trip_id", trip_id).execute()
        
        if not trip_response.data:
            return {}
        
        trip_data = trip_response.data[0]
        
        # 2. Récupérer les réservations pour ce trajet
        bookings_response = supabase.table("bookings").select("*").eq("trip_id", trip_id).execute()
        bookings = bookings_response.data if bookings_response.data else []
        
        # 3. Calculer les statistiques
        passenger_count = len(bookings)
        total_revenue = sum(trip_data.get("passenger_price", 0) * booking.get("seats", 0) for booking in bookings)
        
        # 4. Ajouter les statistiques au dictionnaire du trajet
        trip_stats = dict(trip_data)
        trip_stats["passenger_count"] = passenger_count
        trip_stats["total_revenue"] = total_revenue
        
        return trip_stats
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques pour le trajet {trip_id}: {e}")
        return {}

def get_user_trips_with_role(user_id, limit=None):
    """
    Récupère tous les trajets d'un utilisateur avec leur rôle
    """
    try:
        all_trips = []
        
        # 1. Trajets en tant que conducteur
        driver_response = supabase.table("trips").select("*").eq("driver_id", user_id).execute()
        if driver_response.data:
            for trip in driver_response.data:
                trip_with_role = dict(trip)
                trip_with_role["role"] = "driver"
                all_trips.append(trip_with_role)
        
        # 2. Trajets en tant que passager
        # a. Récupérer les réservations
        bookings_response = supabase.table("bookings").select("trip_id").eq("user_id", user_id).execute()
        
        if bookings_response.data:
            # b. Récupérer les détails des trajets
            for booking in bookings_response.data:
                trip_id = booking["trip_id"]
                trip_response = supabase.table("trips").select("*").eq("trip_id", trip_id).execute()
                
                if trip_response.data:
                    trip_with_role = dict(trip_response.data[0])
                    trip_with_role["role"] = "passenger"
                    all_trips.append(trip_with_role)
        
        # 3. Trier par date de départ (ordre descendant)
        sorted_trips = sorted(all_trips, key=lambda x: x.get("departure_schedule", ""), reverse=True)
        
        # 4. Appliquer la limite si spécifiée
        if limit and limit > 0:
            sorted_trips = sorted_trips[:limit]
        
        return pd.DataFrame(sorted_trips)
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des trajets avec rôle pour l'utilisateur {user_id}: {e}")
        return pd.DataFrame()

def get_support_tickets(user_id=None):
    """Récupère tous les tickets de support, optionnellement filtrés par utilisateur"""
    try:
        query = supabase.table("support_tickets").select("*")
        
        if user_id:
            query = query.eq("user_id", user_id)
        
        response = query.execute()
        
        if response.data:
            return pd.DataFrame(response.data)
        else:
            return pd.DataFrame()
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tickets de support: {e}")
        return pd.DataFrame()


def get_signalements_for_trip(trip_id):
    """Récupère les signalements associés à un trajet"""
    try:
        # Note: support_tickets table doesn't have trip_id column in current schema
        # Return empty list for now until schema is updated or alternative approach is implemented
        logger.info(f"Signalements pour trajet {trip_id}: fonctionnalité non disponible (colonne trip_id manquante)")
        return []
        
        # TODO: Implement proper trip-support ticket relationship
        # Either add trip_id column to support_tickets or use alternative linking method
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des signalements pour le trajet {trip_id}: {e}")
        return []

def get_trip_details_configured(trip_id):
    """
    Récupère les détails d'un trajet selon la configuration JSON avec validation Pydantic
    """
    try:
        # 1. Charger la configuration via settings.py
        from dash_apps.utils.settings import load_json_config
        
        config = load_json_config('trip_details_config.json')
        trip_config = config.get('trip_details', {})
        fields_config = trip_config.get('fields', {})
        
        # 2. Extraire tous les champs configurés
        configured_fields = []
        for section_name, section_fields in fields_config.items():
            configured_fields.extend(section_fields.keys())
        
        logger.info(f"[TRIP_CONFIGURED] Champs configurés: {configured_fields}")
        
        # 3. Récupérer les données brutes de Supabase
        response = supabase.table("trips").select("*").eq("trip_id", trip_id).execute()
        
        if not response.data:
            logger.warning(f"[TRIP_CONFIGURED] Trajet {trip_id} non trouvé")
            return None
        
        raw_data = response.data[0]
        logger.info(f"[TRIP_CONFIGURED] Données brutes récupérées pour {trip_id}")
        
        # 4. Filtrer selon la configuration (garder seulement les champs configurés)
        filtered_data = {}
        for field in configured_fields:
            if field in raw_data:
                filtered_data[field] = raw_data[field]
            else:
                logger.warning(f"[TRIP_CONFIGURED] Champ '{field}' configuré mais absent des données")
        
        # 5. Validation avec Pydantic
        from dash_apps.models.config_models import TripDataModel
        from dash_apps.utils.validation_utils import validate_data
        
        # Valider les données filtrées avec le modèle Pydantic
        validation_result = validate_data(TripDataModel, filtered_data)
        
        if not validation_result.success:
            logger.error(f"[TRIP_CONFIGURED] Erreurs de validation: {validation_result.get_error_summary()}")
            logger.error(f"[TRIP_CONFIGURED] Données invalides pour {trip_id}, retour None")
            return None  # Propager l'erreur vers le cache service
        
        # 6. Formater les données selon la configuration
        from dash_apps.utils.data_formatter import DataFormatter
        formatted_data = DataFormatter.format_trip_data(filtered_data)
        
        logger.info(f"[TRIP_CONFIGURED] Données validées, filtrées et formatées pour {trip_id}")
        return formatted_data
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération configurée du trajet {trip_id}: {e}")
        # Fallback vers la méthode classique
        return get_trip_by_id(trip_id)
