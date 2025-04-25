from src.data_processing.utils.backend import Backend
import pandas as pd
import os
from typing import *  
from src.data_processing.loaders.loader import Loader
import json
from src.core.database import get_session, Trip
import streamlit as st

class TripProcessor:
    def __init__(self):
        """
        Initialise le processor
        """
        self.backend = Backend()
        self.loader = Loader()


    def convert_trips_json_to_dataframe(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Convertit le JSON des trips en DataFrame avec une structure aplatie
        Args:
            file_path (str): Chemin vers le fichier JSON des trips
        Returns:
            Optional[pd.DataFrame]: DataFrame structuré des trips ou None si erreur
        """
        if not self.loader._check_json_file(file_path):
            return None

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            trips_list = []
            for trip_id, trip_data in data.items():
                trip_dict = {
                    'trip_id': trip_id,
                    'updated_at': trip_data.get('updated_at'),
                    # Informations de base
                    'departure_date': trip_data['data'].get('departure_date'),
                    'departure_schedule': trip_data['data'].get('departure_schedule'),
                    'destination_schedule': trip_data['data'].get('destination_schedule'),
                    'price_per_seat': trip_data['data'].get('price_per_seat'),
                    'number_of_seats': trip_data['data'].get('number_of_seats'),
                    'available_seats': trip_data['data'].get('available_seats'),
                    'trip_distance': trip_data['data'].get('trip_distance'),
                    'auto_confirmation': trip_data['data'].get('auto_confirmation'),
                    
                    # Lieux
                    'departure_name': trip_data['data'].get('departure_name'),
                    'destination_name': trip_data['data'].get('destination_name'),
                    'departure_latitude': trip_data['data'].get('departure_location', {}).get('latitude'),
                    'departure_longitude': trip_data['data'].get('departure_location', {}).get('longitude'),
                    'destination_latitude': trip_data['data'].get('destination_location', {}).get('latitude'),
                    'destination_longitude': trip_data['data'].get('destination_location', {}).get('longitude'),

                    "region": trip_data['data'].get('region'),
                    "trip_polyline": trip_data['data'].get('trip_polyline'),
                    
                    # Références
                    'driver_reference': trip_data['data'].get('driver_reference'),
                    'all_passengers': ','.join(trip_data['data'].get('all_passengers', [])),
                    'passenger_reservations': json.dumps(trip_data['data'].get('passenger_reservations', [])),
                    'viator_income': trip_data['data'].get('viator_income'),
                    'passengers': len(trip_data['data'].get('all_passengers', [])),  
                }
                trips_list.append(trip_dict)
            
            df = pd.DataFrame(trips_list)
       
            
            # Conversion des dates - utiliser une méthode plus robuste
            date_columns = ['departure_date', 'departure_schedule', 'destination_schedule', 'updated_at']
            for col in date_columns:
                if col in df.columns:
                    # Utiliser le parsing sans spécifier de format explicite
                    # pandas essaiera de détecter automatiquement le format
                    df[col] = pd.to_datetime(df[col], errors='coerce')


         
                
            return df

        except Exception as e:
            print(f"Erreur lors du parsing du fichier trips {file_path}: {e}")
            return None


    def filter_trips(self, df: pd.DataFrame, remove_columns: List[str]) -> pd.DataFrame:
        """
        Filtre le DataFrame des trajets en supprimant les colonnes spécifiées
        Args:
            df (pd.DataFrame): DataFrame des trajets
            remove_columns (List[str]): Liste des colonnes à supprimer
        Returns:
            pd.DataFrame: DataFrame filtré
        """
        return df.drop(columns=remove_columns)


    @st.cache_data(ttl=300)  # Cache les données pendant 5 minutes
    def handler(_self):
        """
        Récupère les données des trajets directement depuis la base de données PostgreSQL
        
        Returns:
            pd.DataFrame: DataFrame des trajets ou None en cas d'erreur
        """
        try:
            print("Récupération des trajets depuis PostgreSQL...")
            session = get_session()
            trips = session.query(Trip).all()
            trips_data = [trip.to_dict() for trip in trips]
            session.close()
            
            if not trips_data:
                print("Aucun trajet trouvé dans la base de données.")
                return None
                
            # Créer le DataFrame directement à partir des données
            trips_df = pd.DataFrame(trips_data)
            
            # Conversion des dates
            date_columns = ['departure_date', 'departure_schedule', 'destination_schedule', 'created_at']
            for col in date_columns:
                if col in trips_df.columns:
                    trips_df[col] = pd.to_datetime(trips_df[col], errors='coerce')
            
            print(f"Chargement réussi de {len(trips_df)} trajets")
            return trips_df
            
        except Exception as e:
            print(f"Erreur lors du chargement des trajets: {e}")
            return None


    def get_trips(self, file_path=None):
        """
        Récupère et formate les données des trajets depuis la base de données
        
        Returns:
            list: Liste des trajets formatés
        """
        try:
            print("Récupération des trajets depuis PostgreSQL...")
            session = get_session()
            trips = session.query(Trip).all()
            
            formatted_trips = []
            for trip in trips:
                trip_dict = trip.to_dict()
                
                # Créer un objet Trip formaté comme l'ancienne méthode
                formatted_trip = {
                    'id': trip_dict.get('id'),
                    'departure_date': trip_dict.get('departure_date'),
                    'departure_point': trip_dict.get('departure_name'),
                    'destination': trip_dict.get('destination_name'),
                    'price': trip_dict.get('price_per_seat'),
                    'formatted_price': f"{trip_dict.get('price_per_seat', 0):,} XOF".replace(',', ' ') if trip_dict.get('price_per_seat') else "N/A",
                    'distance': trip_dict.get('trip_distance'),
                    'driver_id': trip_dict.get('driver_reference').split('/')[-1] if trip_dict.get('driver_reference') else None,
                    'seats': trip_dict.get('number_of_seats'),
                    'available_seats': trip_dict.get('available_seats')
                }
                
                # Formatter la date si elle existe
                if formatted_trip['departure_date']:
                    if isinstance(formatted_trip['departure_date'], str):
                        try:
                            dt = pd.to_datetime(formatted_trip['departure_date'])
                            formatted_trip['formatted_date'] = dt.strftime('%d/%m/%Y')
                        except:
                            formatted_trip['formatted_date'] = "Date invalide"
                    else:
                        formatted_trip['formatted_date'] = formatted_trip['departure_date'].strftime('%d/%m/%Y')
                
                formatted_trips.append(formatted_trip)
            
            print(f"Retour des trajets : {len(formatted_trips)} trajets")
            return formatted_trips
        except Exception as e:
            print(f"Erreur lors de la récupération des trajets: {e}")
            return []


    @st.cache_data(ttl=300)
    def get_user_trips(_self, user_id: str, trips_df: Optional[pd.DataFrame] = None, page: int = 1, items_per_page: int = 50):
        """
        Retrouve tous les trajets associés à un utilisateur (conducteur ou passager) avec pagination
        
        Args:
            user_id (str): ID de l'utilisateur à rechercher
            trips_df (Optional[pd.DataFrame]): DataFrame des trajets existant (déprécié, utilisez page et items_per_page pour la pagination)
            page (int): Numéro de la page à afficher (commencé à 1)
            items_per_page (int): Nombre d'éléments par page
            
        Returns:
            Optional[Dict]: Dictionnaire contenant les trajets de l'utilisateur et les informations de pagination
        """
        if not user_id:
            print("ID d'utilisateur non fourni")
            return None
        
        # Nettoyer l'ID utilisateur (enlever les espaces et autres caractères indésirables)
        clean_user_id = str(user_id).strip()
        print(f"Recherche des trajets pour l'utilisateur : {clean_user_id}")
        
        try:
            from src.core.database import get_session, Trip, TripPassenger, Base
            from sqlalchemy import or_, cast, String, func, Integer, BigInteger
            from sqlalchemy.sql.expression import text
            import json
            
            # Calculer l'offset pour la pagination
            offset = (page - 1) * items_per_page
            
            with get_session() as session:
                # Convertir user_id en entier si possible pour la comparaison avec BigInteger
                try:
                    numeric_user_id = int(clean_user_id)
                except ValueError:
                    numeric_user_id = None
                
                # Requête pour compter le nombre total de trajets où l'utilisateur est conducteur
                driver_count_query = session.query(func.count(Trip.trip_id))
                if numeric_user_id is not None:
                    # Si l'ID est numérique, essayer les deux formats
                    driver_count_query = driver_count_query.filter(
                        or_(
                            Trip.driver_id == clean_user_id,
                            Trip.driver_id == numeric_user_id,
                            cast(Trip.driver_id, BigInteger) == numeric_user_id
                        )
                    )
                else:
                    # Sinon, utiliser uniquement la chaîne
                    driver_count_query = driver_count_query.filter(Trip.driver_id == clean_user_id)
                
                total_driver_trips = driver_count_query.scalar() or 0
                
                # Requête pour les trajets où l'utilisateur est conducteur avec pagination
                driver_trips_query = session.query(Trip)
                if numeric_user_id is not None:
                    # Si l'ID est numérique, essayer les deux formats
                    driver_trips_query = driver_trips_query.filter(
                        or_(
                            Trip.driver_id == clean_user_id,
                            Trip.driver_id == numeric_user_id,
                            cast(Trip.driver_id, BigInteger) == numeric_user_id
                        )
                    )
                else:
                    # Sinon, utiliser uniquement la chaîne
                    driver_trips_query = driver_trips_query.filter(Trip.driver_id == clean_user_id)
                
                driver_trips_query = driver_trips_query.limit(items_per_page).offset(offset)
                driver_trips = driver_trips_query.all()
                
                # Conversion des objets Trip en dictionnaires
                driver_trips_list = [trip.to_dict() for trip in driver_trips]
                
                # Vérifier si la table trip_passengers existe
                check_table_sql = text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'trip_passengers');"
                )
                table_exists = session.execute(check_table_sql).scalar()
                
                total_passenger_trips = 0
                passenger_trips_list = []
                
                if table_exists:
                    # Utiliser la table trip_passengers pour trouver les trajets où l'utilisateur est passager
                    print(f"Recherche des trajets passager dans la table trip_passengers pour l'utilisateur {clean_user_id}")
                    
                    # Requête pour compter les trajets passager
                    if numeric_user_id is not None:
                        passenger_count_query = session.query(func.count(TripPassenger.trip_id)).filter(
                            TripPassenger.passenger_id == numeric_user_id
                        )
                        total_passenger_trips = passenger_count_query.scalar() or 0
                        
                        # Requête pour obtenir les trajets passager avec pagination
                        passenger_trips_query = session.query(Trip).join(
                            TripPassenger, Trip.trip_id == TripPassenger.trip_id
                        ).filter(
                            TripPassenger.passenger_id == numeric_user_id
                        ).limit(items_per_page).offset(offset)
                        
                        passenger_trips = passenger_trips_query.all()
                        passenger_trips_list = [trip.to_dict() for trip in passenger_trips]
                    else:
                        print("Impossible de convertir l'ID utilisateur en nombre pour la recherche dans trip_passengers")
                else:
                    print("La table trip_passengers n'existe pas, utilisation de la recherche dans passenger_reservations")
                    # Méthode de secours : recherche dans le champ JSON passenger_reservations
                    passenger_count_sql = text(
                        "SELECT COUNT(*) FROM trips WHERE passenger_reservations::text LIKE :pattern"
                    )
                    
                    passenger_sql = text(
                        "SELECT * FROM trips WHERE passenger_reservations::text LIKE :pattern LIMIT :limit OFFSET :offset"
                    )
                    
                    search_pattern = f'%{clean_user_id}%'
                    
                    # Exécuter les requêtes pour les passagers
                    total_passenger_result = session.execute(passenger_count_sql, {"pattern": search_pattern})
                    total_passenger_trips = total_passenger_result.scalar() or 0
                    
                    passenger_result = session.execute(
                        passenger_sql, 
                        {"pattern": search_pattern, "limit": items_per_page, "offset": offset}
                    )
                    
                    # Convertir le résultat en dictionnaires
                    for row in passenger_result:
                        # Convertir la ligne (Row) en dictionnaire
                        trip_dict = {}
                        for column, value in row._mapping.items():
                            trip_dict[column] = value
                        passenger_trips_list.append(trip_dict)
            
            # Ajouter le rôle de l'utilisateur dans chaque trajet
            for trip in driver_trips_list:
                trip['user_role'] = 'Conducteur'
                
            for trip in passenger_trips_list:
                trip['user_role'] = 'Passager'
            
            # Combiner les trajets et convertir en DataFrame
            all_trips_list = driver_trips_list + passenger_trips_list
            
            if all_trips_list:
                all_trips_df = pd.DataFrame(all_trips_list)
                
                # Trier les trajets par date (plus récents en premier)
                if 'departure_date' in all_trips_df.columns:
                    all_trips_df = all_trips_df.sort_values(by='departure_date', ascending=False)
                    
                # Information de pagination
                pagination_info = {
                    'page': page,
                    'items_per_page': items_per_page,
                    'total_driver': total_driver_trips,
                    'total_passenger': total_passenger_trips,
                    'total_items': total_driver_trips + total_passenger_trips,
                    'total_pages': (total_driver_trips + total_passenger_trips + items_per_page - 1) // items_per_page
                }
                
                return {
                    'trips_df': all_trips_df,
                    'pagination': pagination_info
                }
            else:
                return {
                    'trips_df': pd.DataFrame(),
                    'pagination': {
                        'page': page,
                        'items_per_page': items_per_page,
                        'total_driver': total_driver_trips,
                        'total_passenger': total_passenger_trips,
                        'total_items': total_driver_trips + total_passenger_trips,
                        'total_pages': 0
                    }
                }
                
        except Exception as e:
            import traceback
            print(f"Erreur lors de la recherche des trajets de l'utilisateur: {e}")
            print(traceback.format_exc())
            return None


if __name__ == "__main__":
    # Créer une instance du processor
    processor = TripProcessor()
    
    # Récupérer le DataFrame
    df_trips = processor.handler()
    
    # Afficher les informations sur le DataFrame
    print("\nInformations sur le DataFrame:")
    print(f"Nombre de lignes: {len(df_trips)}")
    print(f"Colonnes: {df_trips.columns.tolist()}")
    
    # Créer le dossier output s'il n'existe pas
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # Sauvegarder en CSV
    output_file = os.path.join(output_dir, 'trips_data.csv')
    df_trips.to_csv(output_file, index=False)
    print(f"\nDataFrame sauvegardé dans: {output_file}")