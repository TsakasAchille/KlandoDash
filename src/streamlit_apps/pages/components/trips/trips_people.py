import streamlit as st
import pandas as pd
import json
from src.streamlit_apps.components import Cards
from src.core.database import get_session, execute_raw_query
from src.streamlit_apps.components.modern_card import modern_card

class TripsPeople:
    """Classe responsable de la gestion des informations sur les personnes liées aux trajets"""
    
    def __init__(self):
        """Initialisation de la classe TripsPeople"""
        pass
        
    def display_people_info(self, trip_data, info_cols=None):
        """Affiche les informations sur le conducteur et les passagers
        
        Args:
            trip_data: Données du trajet sélectionné
            info_cols: Colonnes Streamlit pour l'affichage (optionnel)
        """
        try:
            # Récupérer les données utilisateurs depuis la session state
            if "user_df" not in st.session_state:
                st.error("Données utilisateurs non disponibles")
                return
                
            users_df = st.session_state["user_df"]

            # Extraire les IDs
            driver_id = trip_data.get('driver_id', '') or trip_data.get('driver_reference', '').replace('users/', '')
            trip_id = trip_data.get('trip_id', '')
            
            # Essayer de récupérer les passagers depuis la table trip_passengers
            all_passengers = self._get_passengers_from_db(trip_id)
            
            # Si aucun passager n'est trouvé dans la table, utiliser passenger_reservations
            if not all_passengers:
                # Récupérer les réservations de passagers
                passenger_reservations = trip_data.get('passenger_reservations', [])
                
                # Traiter passenger_reservations selon son type
                if passenger_reservations is None:
                    all_passengers = []
                elif isinstance(passenger_reservations, str):
                    try:
                        # Essayer de parser la chaîne JSON
                        parsed_reservations = json.loads(passenger_reservations)
                        if isinstance(parsed_reservations, list):
                            # Extraire les IDs des passagers des réservations
                            all_passengers = [res.get('passenger_id', '').replace('users/', '') 
                                            for res in parsed_reservations if res.get('passenger_id')]
                        else:
                            all_passengers = []
                    except json.JSONDecodeError:
                        all_passengers = []
                elif isinstance(passenger_reservations, list):
                    # Extraire les IDs des passagers des réservations
                    all_passengers = [res.get('passenger_id', '').replace('users/', '') 
                                    for res in passenger_reservations if res.get('passenger_id')]
                else:
                    all_passengers = []
            
            # Créer les colonnes pour l'affichage
            cols = st.columns(1 + len(all_passengers) if all_passengers else 1)
            
            # Conducteur
            if isinstance(driver_id, str) and driver_id.strip():
                with cols[0]:
                    # Récupérer directement le nom depuis le DataFrame
                    driver_name = "Inconnu"
                    # Chercher d'abord avec 'id' (PostgreSQL), puis avec 'user_id' (ancien format)
                    if 'id' in users_df.columns:
                        driver_row = users_df[users_df['id'] == driver_id]
                    elif 'user_id' in users_df.columns:
                        driver_row = users_df[users_df['user_id'] == driver_id]
                    else:
                        driver_row = pd.DataFrame()
                        
                    if not driver_row.empty:
                        # Chercher d'abord display_name, puis name pour assurer la meilleure donnée
                        if 'display_name' in driver_row.columns and not pd.isna(driver_row.iloc[0]['display_name']):
                            driver_name = driver_row.iloc[0]['display_name']
                        elif 'name' in driver_row.columns and not pd.isna(driver_row.iloc[0]['name']):
                            driver_name = driver_row.iloc[0]['name']
                    
                    # Afficher avec modern_card
                    modern_card(
                        title="Conducteur",
                        icon="👨‍🚗",  
                        items=[
                            ("Nom", driver_name),
                            ("ID", driver_id)
                        ],
                        bg_color="#102844",
                        accent_color="#00BFA5"
                    )
                    
                    # Ajouter un bouton pour voir le profil du conducteur
                    if st.button("Voir profil", key=f"driver_profile_{driver_id}"):
                        st.session_state["selected_user_id"] = driver_id
                        st.session_state["show_user_profile"] = True
            
            # Passagers
            if isinstance(all_passengers, list) and len(all_passengers) > 0:
                for i, passenger in enumerate(all_passengers):
                    if i + 1 < len(cols):  
                        with cols[i + 1]:
                            # Déterminer l'ID et le nom du passager
                            if isinstance(passenger, dict):
                                passenger_name = passenger.get('name', f'Passager {i+1}')
                                passenger_id = passenger.get('id', '')
                                passenger_phone = passenger.get('phone', '')
                            else:
                                passenger_id = passenger
                                passenger_name = "Inconnu"
                                passenger_phone = ""
                                
                                # Récupérer le nom depuis le DataFrame
                                if 'id' in users_df.columns:
                                    passenger_row = users_df[users_df['id'] == passenger_id]
                                elif 'user_id' in users_df.columns:
                                    passenger_row = users_df[users_df['user_id'] == passenger_id]
                                else:
                                    passenger_row = pd.DataFrame()
                                    
                                if not passenger_row.empty:
                                    if 'display_name' in passenger_row.columns and not pd.isna(passenger_row.iloc[0]['display_name']):
                                        passenger_name = passenger_row.iloc[0]['display_name']
                                    elif 'name' in passenger_row.columns and not pd.isna(passenger_row.iloc[0]['name']):
                                        passenger_name = passenger_row.iloc[0]['name']
                                    
                                    if 'phone_number' in passenger_row.columns and not pd.isna(passenger_row.iloc[0]['phone_number']):
                                        passenger_phone = passenger_row.iloc[0]['phone_number']
                            
                            # Préparer les items pour la carte
                            items = [("Nom", passenger_name), ("ID", passenger_id)]
                            if passenger_phone:
                                items.append(("Téléphone", passenger_phone))
                            
                            # Afficher avec modern_card
                            modern_card(
                                title=f"Passager {i+1}",
                                icon="👥",  
                                items=items,
                                bg_color="#102844",
                                accent_color="#00BFA5"
                            )
                            
                            # Ajouter les boutons pour voir le profil et le chat du passager
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Voir profil", key=f"passenger_profile_{i}_{passenger_id}"):
                                    st.session_state["selected_user_id"] = passenger_id
                                    st.session_state["show_user_profile"] = True
                            
                            with col2:
                                if st.button("📱 Chat", key=f"passenger_chat_{i}_{passenger_id}"):
                                    # Stocker l'ID du passager pour le chat
                                    st.session_state["chat_with_passenger_id"] = passenger_id
                                    st.session_state["show_chat_dialog"] = True
                                    # Stocker aussi les noms pour l'affichage et l'ID du trajet
                                    st.session_state["chat_passenger_name"] = passenger_name
                                    st.session_state["chat_trip_id"] = trip_data.get('trip_id', '')
                
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations sur les personnes: {str(e)}")
            
    def _get_passengers_from_db(self, trip_id):
        """Récupère les passagers depuis la table trip_passengers
        
        Args:
            trip_id: ID du trajet
            
        Returns:
            list: Liste des IDs des passagers
        """
        try:
            # Vérifier si la table trip_passengers existe
            check_query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'trip_passengers'
            );
            """
            
            exists = execute_raw_query(check_query)
            if not exists or not exists[0][0]:
                # La table n'existe pas, retourner une liste vide
                return []
                
            # Requête pour récupérer les passagers du trajet
            query = """
            SELECT passenger_id FROM trip_passengers 
            WHERE trip_id = :trip_id
            """
            
            results = execute_raw_query(query, {'trip_id': trip_id})
            
            # Convertir les résultats en liste d'IDs
            passenger_ids = [row[0] for row in results] if results else []
            return passenger_ids
            
        except Exception as e:
            st.warning(f"Erreur lors de la récupération des passagers depuis la base de données: {str(e)}")
            return []