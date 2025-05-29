import streamlit as st
import pandas as pd
from src.streamlit_apps.components.modern_card import modern_card

class TripsOccupationManager:
    """Gère l'affichage des informations sur l'occupation des sièges dans les trajets"""
    
    def display_seat_occupation_info(self, trip_data, info_cols=None):
        """Affiche les informations sur l'occupation des sièges
        
        Args:
            trip_data: Données du trajet sélectionné
            info_cols: Colonnes Streamlit pour l'affichage (optionnel)
        
        Returns:
            tuple: (occupied_seats, total_seats)
        """
        try:
            # Extraire les informations nécessaires
            total_seats = int(trip_data.get('number_of_seats', 0))
            available_seats = int(trip_data.get('available_seats', 0))
            
            trip_id = trip_data.get('trip_id', '')
            # Essayer de récupérer les passagers depuis la table trip_passengers (comme TripsPeople)
            all_passengers = []
            try:
                from src.core.database import execute_raw_query
                query = """
                SELECT passenger_id FROM trip_passengers WHERE trip_id = :trip_id
                """
                result = execute_raw_query(query, {"trip_id": trip_id})
                all_passengers = [row[0] for row in result]
            except Exception:
                # fallback: utiliser passenger_reservations
                passenger_reservations = trip_data.get('passenger_reservations', [])
                import json
                if passenger_reservations is None:
                    all_passengers = []
                elif isinstance(passenger_reservations, str):
                    try:
                        parsed_reservations = json.loads(passenger_reservations)
                        if isinstance(parsed_reservations, list):
                            all_passengers = [res.get('passenger_id', '').replace('users/', '') for res in parsed_reservations if res.get('passenger_id')]
                        else:
                            all_passengers = []
                    except json.JSONDecodeError:
                        all_passengers = []
                elif isinstance(passenger_reservations, list):
                    all_passengers = [res.get('passenger_id', '').replace('users/', '') for res in passenger_reservations if res.get('passenger_id')]
                else:
                    all_passengers = []

            # Déterminer le nombre de passagers
            passenger_count = len(all_passengers) if isinstance(all_passengers, list) else 0
            
            # Calculer les sièges occupés
            occupied_seats = passenger_count
            if occupied_seats > total_seats - available_seats:
                occupied_seats = total_seats - available_seats
            
            # Calculer le pourcentage d'occupation
            occupation_percentage = (occupied_seats / total_seats) * 100 if total_seats > 0 else 0
            
            modern_card(
                title="Occupation des sièges",
                icon="🧑‍🤝‍🧑",  # Icône plus moderne pour occupation/sièges
                items=[
                    ("Sièges totaux", total_seats),
                    ("Sièges occupés", occupied_seats),
                    ("Taux", f"{occupation_percentage:.0f}%")
                ],
                accent_color="#4CAF50" if occupation_percentage > 75 else ("#E67E22" if occupation_percentage > 50 else "#E74C3C")
            )
            st.progress(int(occupation_percentage))
            return occupied_seats, total_seats
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations d'occupation: {str(e)}")
            return 0, 0
