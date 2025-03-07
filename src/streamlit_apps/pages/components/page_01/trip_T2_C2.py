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
    
    def display_seat_info(self, trip_data):
        """
        Affiche les informations sur les sièges pour un trajet spécifique
        
        Args:
            trip_data: Données du trajet sélectionné
        """
        try:
            # Extraire les informations nécessaires
            total_seats = int(trip_data.get('number_of_seats', 0))
            available_seats = int(trip_data.get('available_seats', 0))
            all_passengers = trip_data.get('all_passengers', '')
            driver_id = trip_data.get('driver_reference', '').replace('users/', '')
            
            # Traiter la variable all_passengers
            if isinstance(all_passengers, str):
                # Si la chaîne contient une virgule, c'est probablement une liste sérialisée
                if ',' in all_passengers:
                    all_passengers = all_passengers.split(',')
                # Sinon, convertir en liste à un élément si non vide
                elif all_passengers.strip():
                    all_passengers = [all_passengers.strip()]
                # Si vide, créer liste vide
                else:
                    all_passengers = []
                    
            # Nettoyer les IDs utilisateurs (supprimer le préfixe 'users/')
            if isinstance(all_passengers, list):
                all_passengers = [p.replace('users/', '') for p in all_passengers]
            
            # Déterminer le nombre de passagers
            passenger_count = len(all_passengers) if isinstance(all_passengers, list) else 0
            
            # Calculer les sièges occupés
            occupied_seats = passenger_count
            if occupied_seats > total_seats - available_seats:
                # Si le nombre de passagers est incohérent avec les sièges disponibles
                occupied_seats = total_seats - available_seats
            
            # Créer la carte d'informations sur l'occupation des sièges
            seat_info_content = ""
            seat_info_content += self.format_detail("Total sièges", total_seats)
            seat_info_content += self.format_detail("Sièges occupés", occupied_seats)
            #seat_info_content += self.format_detail("Sièges disponibles", available_seats)
            
            # Ajouter le pourcentage d'occupation en gras
            occupation_percentage = (occupied_seats / total_seats) * 100 if total_seats > 0 else 0
            seat_info_content += self.format_detail("Taux d'occupation", f"<strong>{occupation_percentage:.0f}%</strong>", is_value=False)
            
            # Utiliser un autre emoji selon le taux d'occupation
            icon = "A"
            card_class = ""
            if occupation_percentage > 75:
                icon = "B"
                card_class = "warning"
                
            # Créer deux colonnes pour l'affichage
            col1, col2 = st.columns(2)
            
            with col1:
                # Afficher la carte d'information avec le style CSS
                st.markdown(self.create_car_info_card(
                    "Occupation des sièges", 
                    seat_info_content,
                    icon=icon,
                    card_class=card_class
                ), unsafe_allow_html=True)
            
            with col2:
                # Afficher le graphique en jauge
                pass
               # st.plotly_chart(self.create_seat_gauge(total_seats, total_seats - occupied_seats), use_container_width=True)
            
            # Afficher la représentation visuelle des sièges

            col1, col2 = st.columns(2)

            with col1:



            # Informations sur le conducteur si disponible
                if isinstance(driver_id, str) and driver_id.strip():
                    # Créer un lien cliquable pour l'ID du conducteur
                    driver_link_html = self.create_user_link(driver_id)
                    
                    # Créer le contenu HTML pour les informations du conducteur
                    driver_content = f"<div class='detail-row'><span class='label'>ID Conducteur:</span> {driver_link_html}</div>"
                    
                    # Afficher la carte d'information du conducteur
                    st.markdown(self.create_car_info_card(
                        "Informations sur le conducteur", 
                        driver_content,
                        icon="C",
                    ), unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
            
                # Informations sur les passagers si disponibles
                if isinstance(all_passengers, list) and len(all_passengers) > 0:
                    
                    # Créer une ligne pour afficher le nombre total de passagers
                    st.markdown(f"<div style='margin-top: 15px; margin-bottom: 5px;'><strong>Passagers ({len(all_passengers)})</strong></div>", unsafe_allow_html=True)
                    
                    # Afficher chaque passager dans sa propre carte
                    for i, passenger in enumerate(all_passengers):
                        # Préparer le contenu pour ce passager spécifique
                        passenger_content = ""
                        
                        if isinstance(passenger, dict):
                            # Si les passagers sont des objets complexes
                            passenger_content += self.format_detail(f"Passager", passenger.get('name', f'Passager {i+1}'))
                            passenger_content += self.format_detail(f"Siège", f"{i+1}")
                            # Ajouter d'autres informations si disponibles
                            if 'phone' in passenger:
                                passenger_content += self.format_detail("Téléphone", passenger['phone'])
                        else:
                            # Si les passagers sont des IDs utilisateur - créer un lien cliquable
                            passenger_link_html = self.create_user_link(passenger)
                            passenger_content += f"<div class='detail-row'><span class='label'>ID Utilisateur:</span> {passenger_link_html}</div>"
                            passenger_content += self.format_detail(f"Siège", f"{i+1}")
                        
                        # Afficher une carte individuelle pour ce passager
                        st.markdown(self.create_car_info_card(
                            f"Passager {i+1}", 
                            passenger_content,
                            icon="P",
                        ), unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations sur les sièges: {str(e)}")
