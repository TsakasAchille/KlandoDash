import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from src.streamlit_apps.components.cards import Cards
from src.streamlit_apps.pages.components.users_trips_linker import UsersTripsLinker

class TripUsers:
    """
    Classe pour visualiser les séges et les passagers d'une voiture
    basée sur les données du DataFrame trips.
    """
    
    def __init__(self):
        """Initialise la visualisation de la voiture"""
        self.seat_colors = {
            'available': '#95D5B2',  # vert clair pour les sièges disponibles
            'occupied': '#F08080',   # rouge pour les sièges occupés
        }
        # Importer la classe Cards qui gère du chargement des CSS
        self.cards = Cards()
        # S'assurer que les styles CSS sont chargés
        self.load_car_styles()
        
        # Importer UsersTripsLinker pour créer des liens cliquables
        self.users_trips_linker = UsersTripsLinker()
    
    def load_car_styles(self):
        """Charge les styles CSS pour les cartes d'information de voiture"""
        # Utiliser la méthode statique de Cards pour charger les styles
        Cards.load_card_styles()
        
        # Charger également le CSS spécifique aux voitures si existant
        cars_css_path = os.path.join('assets', 'css', 'cars.css')
        if os.path.exists(cars_css_path):
            with open(cars_css_path, 'r') as f:
                css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    def create_car_info_card(self, title, content, icon="A", card_class=""):
        """Crée une carte d'information de voiture stylée
        
        Args:
            title: Titre de la carte
            content: Contenu HTML de la carte
            icon: Icône à afficher (lettre ou texte simple)
            card_class: Classe CSS additionnelle
        
        Returns:
            HTML formaté pour la carte d'information
        """
        return f"""
        <div class="info-card {card_class}">
            <div class="info-title">
                <span class="icon">{icon}</span> {title}
            </div>
            <div class="info-content">
                {content}
            </div>
        </div>
        """
    
    def format_detail(self, label, value, is_value=True):
        """Formate une ligne de détail pour les cartes d'information
        
        Args:
            label: Label du détail
            value: Valeur du détail
            is_value: Si True, applique les styles de valeur
            
        Returns:
            HTML formaté pour la ligne de détail
        """
        value_class = 'value' if is_value else ''
        return f"<div class='detail-row'><span class='label'>{label}:</span> <span class='{value_class}'>{value}</span></div>"
    
    def create_user_link(self, user_id):
        """Crée un lien HTML cliquable vers la page utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            HTML du lien cliquable
        """
        return self.users_trips_linker.create_user_link(user_id, f"{user_id} (voir fiche)")
    
    def create_seat_gauge(self, total_seats, available_seats):
        """
        Crée un graphique en jauge montrant le taux d'occupation des séges
        
        Args:
            total_seats: Nombre total de sièges
            available_seats: Nombre de sièges disponibles
            
        Returns:
            Une figure Plotly
        """
        occupied_seats = total_seats - available_seats
        occupation_percentage = (occupied_seats / total_seats) * 100 if total_seats > 0 else 0
        
        # Créer la jauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=occupation_percentage,
            title={'text': "Taux d'occupation (%)"},
            delta={'reference': 0, 'increasing': {'color': "#F08080"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#F08080"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 50], 'color': '#D4F1DD'},
                    {'range': [50, 75], 'color': '#FFEBB2'},
                    {'range': [75, 100], 'color': '#FADCC7'}
                ],
            }
        ))
        
       
        # Configurer la taille et la disposition
        fig.update_layout(
            height=200,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        
        return fig
    
    def create_seat_indicators(self, total_seats, available_seats):
        """
        Crée une représentation visuelle simple des sièges
        
        Args:
            total_seats: Nombre total de sièges
            available_seats: Nombre de sièges disponibles
            
        Returns:
            Une figure Plotly
        """
        occupied_seats = total_seats - available_seats
        
        # Créer un tableau qui représente les sièges
        rows = (total_seats + 1) // 2  # 2 sièges par rangée (arrondi supérieur)
        
        # Créer la figure avec une subplot pour chaque siège en spécifiant le type 'indicator'
        specs = [[{"type": "indicator"} for _ in range(2)] for _ in range(rows)]
        fig = make_subplots(
            rows=rows, 
            cols=2, 
            specs=specs,
            subplot_titles=[f"Siège {i+1}" for i in range(total_seats)],
            vertical_spacing=0.1
        )
        
        # Ajouter les indicateurs de sièges
        for i in range(total_seats):
            row = (i // 2) + 1
            col = (i % 2) + 1
            
            # Définir le statut et la couleur du siège
            is_occupied = i < occupied_seats
            color = self.seat_colors['occupied'] if is_occupied else self.seat_colors['available']
            status = "Occupé" if is_occupied else "Libre"
            
            # Ajouter l'indicateur pour ce siège
            fig.add_trace(
                go.Indicator(
                    mode="number+delta",
                    value=i+1,
                    delta={"reference": 0, "valueformat": ".0f"},
                    title={"text": status},
                    number={"font": {"color": color}},
                ),
                row=row, col=col
            )
        
        # Configurer la taille et la disposition
        fig.update_layout(
            height=rows*120,
            margin=dict(l=50, r=10, t=10, b=10),
            showlegend=False,
        )
        
        return fig

    

    #NEWWWw----------------------------------------------------------------------------



    def display_seat_occupation_info0(self, trip_data, info_cols=None):
        """
        Affiche les informations sur l'occupation des sièges
        
        Args:
            trip_data: Données du trajet sélectionné
            info_cols: Colonnes Streamlit pour l'affichage (optionnel)
        """
        try:
            # Extraire les informations nécessaires
            total_seats = int(trip_data.get('number_of_seats', 0))
            available_seats = int(trip_data.get('available_seats', 0))
            all_passengers = trip_data.get('all_passengers', '')
            
            # Traiter la variable all_passengers
            if isinstance(all_passengers, str):
                if ',' in all_passengers:
                    all_passengers = all_passengers.split(',')
                elif all_passengers.strip():
                    all_passengers = [all_passengers.strip()]
                else:
                    all_passengers = []
                    
            # Nettoyer les IDs utilisateurs
            if isinstance(all_passengers, list):
                all_passengers = [p.replace('users/', '') for p in all_passengers]
            
            # Déterminer le nombre de passagers
            passenger_count = len(all_passengers) if isinstance(all_passengers, list) else 0
            
            # Calculer les sièges occupés
            occupied_seats = passenger_count
            if occupied_seats > total_seats - available_seats:
                occupied_seats = total_seats - available_seats
            
            # Créer le contenu d'information
            seat_info_content = ""
            seat_info_content += self.format_detail("Total sièges", total_seats)
            seat_info_content += self.format_detail("Sièges occupés", occupied_seats)
            
            # Ajouter le pourcentage d'occupation en gras
            occupation_percentage = (occupied_seats / total_seats) * 100 if total_seats > 0 else 0
            seat_info_content += self.format_detail("Taux d'occupation", f"<strong>{occupation_percentage:.0f}%</strong>", is_value=False)
            
            # Utiliser un autre emoji selon le taux d'occupation
            icon = "💺"  # siège            
            card_class = ""
            if occupation_percentage > 75:
                card_class = "success"
            
            # Affichage dans la première colonne si colonnes fournies
            if info_cols and len(info_cols) > 0:
                with info_cols[0]:
                    st.markdown(self.create_car_info_card(
                        "Occupation des sièges", 
                        seat_info_content,
                        icon=icon,
                        card_class=card_class
                    ), unsafe_allow_html=True)
            else:
                st.markdown(self.create_car_info_card(
                    "Occupation des sièges", 
                    seat_info_content,
                    icon=icon,
                    card_class=card_class
                ), unsafe_allow_html=True)
                
            return occupied_seats, total_seats
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations d'occupation: {str(e)}")
            return 0, 0
    

    def display_seat_occupation_info(self, trip_data, info_cols=None):
        """
        Affiche les informations sur l'occupation des sièges
        
        Args:
            trip_data: Données du trajet sélectionné
            info_cols: Colonnes Streamlit pour l'affichage (optionnel)
        """
        try:
            # Extraire les informations nécessaires
            total_seats = int(trip_data.get('number_of_seats', 0))
            available_seats = int(trip_data.get('available_seats', 0))
            all_passengers = trip_data.get('all_passengers', '')
            
            # Traiter la variable all_passengers
            if isinstance(all_passengers, str):
                if ',' in all_passengers:
                    all_passengers = all_passengers.split(',')
                elif all_passengers.strip():
                    all_passengers = [all_passengers.strip()]
                else:
                    all_passengers = []
                    
            # Nettoyer les IDs utilisateurs
            if isinstance(all_passengers, list):
                all_passengers = [p.replace('users/', '') for p in all_passengers]
            
            # Déterminer le nombre de passagers
            passenger_count = len(all_passengers) if isinstance(all_passengers, list) else 0
            
            # Calculer les sièges occupés
            occupied_seats = passenger_count
            if occupied_seats > total_seats - available_seats:
                occupied_seats = total_seats - available_seats
            
            # Calculer le pourcentage d'occupation
            occupation_percentage = (occupied_seats / total_seats) * 100 if total_seats > 0 else 0
            
            # Préparer les items pour la carte d'information
            content_items = [
                ("Total sièges", f"{total_seats}"),
                ("Sièges occupés", f"{occupied_seats}"),
                ("Taux d'occupation", f"{occupation_percentage:.0f}%")
            ]
            
            # Déterminer l'icône et la couleur selon le taux d'occupation
            icon = "💺"  # siège
            color = "#4CAF50" if occupation_percentage > 75 else "#7B1F2F"  # vert si >75%, sinon rouge par défaut
            
            # Préparer les données pour create_info_cards
            info_data = [("Occupation des sièges", content_items, icon)]
            
            # Affichage selon les colonnes fournies
            if info_cols and len(info_cols) > 0:
                with info_cols[0]:
                    st.markdown(Cards.create_info_cards(
                        info_data,
                        color=color,
                        label_size="9px",
                        value_size="14px",
                        vertical_layout=True
                    ), unsafe_allow_html=True)
            else:
                st.markdown(Cards.create_info_cards(
                    info_data,
                    color=color,
                    label_size="9px", 
                    value_size="14px",
                    vertical_layout=True
                ), unsafe_allow_html=True)
                
            return occupied_seats, total_seats
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations d'occupation: {str(e)}")
            return 0, 0




    def display_people_info0(self, trip_data, info_cols=None):
        """
        Affiche les informations sur le conducteur et les passagers
        
        Args:
            trip_data: Données du trajet sélectionné
            info_cols: Colonnes Streamlit pour l'affichage (optionnel)
        """
        try:
            from streamlit_apps.components.cards import Cards
            
            driver_id = trip_data.get('driver_reference', '').replace('users/', '')
            all_passengers = trip_data.get('all_passengers', '')
            
            # Traiter la variable all_passengers
            if isinstance(all_passengers, str):
                if ',' in all_passengers:
                    all_passengers = all_passengers.split(',')
                elif all_passengers.strip():
                    all_passengers = [all_passengers.strip()]
                else:
                    all_passengers = []
                    
            # Nettoyer les IDs utilisateurs
            if isinstance(all_passengers, list):
                all_passengers = [p.replace('users/', '') for p in all_passengers]
            
            if not info_cols:
                # Créer les colonnes pour l'affichage si non fournies
                all_elements = 1 + (1 if driver_id else 0) + len(all_passengers)  # Passagers + conducteur (si présent)
                info_cols = st.columns(all_elements)
            
            col_index = 0
            
            # Conducteur
            if isinstance(driver_id, str) and driver_id.strip():
                with info_cols[col_index]:
                    # Préparer les données pour create_info_cards
                    driver_content = [("ID", driver_id)]
                    info_data = [("Conducteur", driver_content, "🧑‍✈️")]
                    
                    st.markdown(Cards.create_info_cards(
                        info_data,
                        color="#00BFA5",
                        label_size="14px",
                        value_size="16px",
                        background_color="#102844"
                    ), unsafe_allow_html=True)
                    
                    # Ajouter un bouton pour voir le profil du conducteur
                    if st.button("Voir profil", key=f"driver_profile_{driver_id}"):
                        st.session_state["selected_user_id"] = driver_id
                        st.session_state["show_user_profile"] = True
                        
                col_index += 1
    
            # Passagers
            if isinstance(all_passengers, list) and len(all_passengers) > 0:
                for i, passenger in enumerate(all_passengers):
                    with info_cols[col_index]:
                        passenger_content = []
                        
                        if isinstance(passenger, dict):
                            passenger_content.append(("Passager", passenger.get('name', f'Passager {i+1}')))
                            if 'phone' in passenger:
                                passenger_content.append(("Téléphone", passenger['phone']))
                            passenger_id = passenger.get('id', '')
                        else:
                            passenger_id = passenger
                            passenger_content.append(("ID", passenger_id))
                        
                        info_data = [(f"Passager {i+1}", passenger_content, "👥")]
                        
                        st.markdown(Cards.create_info_cards(
                            info_data,
                            color="#00BFA5",
                            label_size="14px",
                            value_size="16px",
                            background_color="#102844"
                        ), unsafe_allow_html=True)
                        
                        # Ajouter un bouton pour voir le profil du passager
                        if st.button("Voir profil", key=f"passenger_profile_{i}_{passenger_id}"):
                            st.session_state["selected_user_id"] = passenger_id
                            st.session_state["show_user_profile"] = True
                            
                    col_index += 1
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations sur les personnes: {str(e)}")

    def display_people_info(self, trip_data, info_cols=None):
        """
        Affiche les informations sur le conducteur et les passagers
        
        Args:
            trip_data: Données du trajet sélectionné
            info_cols: Colonnes Streamlit pour l'affichage (optionnel)
        """
        try:
            from streamlit_apps.components.cards import Cards
            import json
            import os
            
            # Charger les données utilisateurs pour obtenir les noms
            users_data = {}
            try:
                users_file = os.path.join('data', 'raw', 'users', 'users_data_20250305.json')
                with open(users_file, 'r') as f:
                    users_data = json.load(f)
            except Exception as e:
                print(f"Erreur lors du chargement des données utilisateurs: {str(e)}")
            
            # Fonction pour obtenir le nom d'un utilisateur à partir de son ID
            def get_user_name(user_id):
                if not user_id or not users_data:
                    return "Inconnu"
                
                # Vérifier si users_data est un dictionnaire avec des clés d'ID
                if isinstance(users_data, dict):
                    user = users_data.get(user_id, {})
                    return user.get('name', "Inconnu")
                
                # Si users_data est une liste d'objets utilisateur
                elif isinstance(users_data, list):
                    for user in users_data:
                        if isinstance(user, dict) and user.get('id') == user_id:
                            return user.get('name', "Inconnu")
                
                return "Inconnu"
            
            driver_id = trip_data.get('driver_reference', '').replace('users/', '')
            all_passengers = trip_data.get('all_passengers', '')
            
            # Traiter la variable all_passengers
            if isinstance(all_passengers, str):
                if ',' in all_passengers:
                    all_passengers = all_passengers.split(',')
                elif all_passengers.strip():
                    all_passengers = [all_passengers.strip()]
                else:
                    all_passengers = []
                    
            # Nettoyer les IDs utilisateurs
            if isinstance(all_passengers, list):
                all_passengers = [p.replace('users/', '') for p in all_passengers]
            
            if not info_cols:
                # Créer les colonnes pour l'affichage si non fournies
                all_elements = 1 + (1 if driver_id else 0) + len(all_passengers)  # Passagers + conducteur (si présent)
                info_cols = st.columns(all_elements)
            
            col_index = 0
            
            # Conducteur
            if isinstance(driver_id, str) and driver_id.strip():
                with info_cols[col_index]:
                    # Obtenir le nom du conducteur
                    driver_name = get_user_name(driver_id)
                    
                    # Préparer les données pour create_info_cards
                    driver_content = [
                        ("Nom", driver_name),
                        ("ID", driver_id)
                    ]
                    info_data = [("Conducteur", driver_content, "🧑‍✈️")]
                    
                    st.markdown(Cards.create_info_cards(
                        info_data,
                        color="#00BFA5",
                        label_size="14px",
                        value_size="16px",
                        background_color="#102844"
                    ), unsafe_allow_html=True)
                    
                    # Ajouter un bouton pour voir le profil du conducteur
                    if st.button("Voir profil", key=f"driver_profile_{driver_id}"):
                        st.session_state["selected_user_id"] = driver_id
                        st.session_state["show_user_profile"] = True
                        
                col_index += 1
    
            # Passagers
            if isinstance(all_passengers, list) and len(all_passengers) > 0:
                for i, passenger in enumerate(all_passengers):
                    with info_cols[col_index]:
                        passenger_content = []
                        
                        if isinstance(passenger, dict):
                            passenger_name = passenger.get('name', f'Passager {i+1}')
                            passenger_id = passenger.get('id', '')
                            passenger_content.append(("Nom", passenger_name))
                            passenger_content.append(("ID", passenger_id))
                            if 'phone' in passenger:
                                passenger_content.append(("Téléphone", passenger['phone']))
                        else:
                            passenger_id = passenger
                            passenger_name = get_user_name(passenger_id)
                            passenger_content.append(("Nom", passenger_name))
                            passenger_content.append(("ID", passenger_id))
                        
                        info_data = [(f"Passager {i+1}", passenger_content, "👥")]
                        
                        st.markdown(Cards.create_info_cards(
                            info_data,
                            color="#00BFA5",
                            label_size="14px",
                            value_size="16px",
                            background_color="#102844"
                        ), unsafe_allow_html=True)
                        
                        # Ajouter un bouton pour voir le profil du passager
                        if st.button("Voir profil", key=f"passenger_profile_{i}_{passenger_id}"):
                            st.session_state["selected_user_id"] = passenger_id
                            st.session_state["show_user_profile"] = True
                            
                    col_index += 1
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations sur les personnes: {str(e)}")