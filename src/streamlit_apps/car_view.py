import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class CarView:
    """
    Classe pour visualiser les sièges et les passagers d'une voiture
    basée sur les données du DataFrame trips.
    """
    
    def __init__(self):
        """Initialise la visualisation de la voiture"""
        self.seat_colors = {
            'available': '#95D5B2',  # vert clair pour les sièges disponibles
            'occupied': '#F08080',   # rouge pour les sièges occupés
        }
    
    def create_seat_gauge(self, total_seats, available_seats):
        """
        Crée un graphique en jauge montrant le taux d'occupation des sièges
        
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
            height=300,
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
            margin=dict(l=10, r=10, t=10, b=10),
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
            
            # Déterminer le nombre de passagers (peut être une ID chaîne de caractères ou une liste)
            passenger_count = 0
            if isinstance(all_passengers, list):
                passenger_count = len(all_passengers)
            elif isinstance(all_passengers, str) and all_passengers.strip():
                # Si c'est une chaîne non vide (ID utilisateur)
                passenger_count = 1
            
            # Calculer les sièges occupés
            occupied_seats = passenger_count
            if occupied_seats > total_seats - available_seats:
                # Si le nombre de passagers est incohérent avec les sièges disponibles
                occupied_seats = total_seats - available_seats
            
            # Afficher les informations textuelles
            st.subheader("Taux d'occupation des sièges")
            
            # Créer des colonnes pour les métriques
            col1, col2 = st.columns(2)
            col1.metric("Sièges totaux", total_seats)
            col2.metric("Sièges occupés", occupied_seats)
            
            # Afficher le graphique en jauge (avec les données corrigées)
            st.plotly_chart(self.create_seat_gauge(total_seats, total_seats - occupied_seats), use_container_width=True)
            
            # Afficher la représentation visuelle des sièges


            #information sur le driver

            if(isinstance(driver_id, str) and driver_id.strip()):
                st.subheader("Informations sur le conducteur")
                st.write(driver_id)

            # Informations sur les passagers si disponibles
            if (isinstance(all_passengers, list) and len(all_passengers) > 0) or (isinstance(all_passengers, str) and all_passengers.strip()):
                st.subheader("Informations sur les passagers")
                
                # Créer un DataFrame pour l'affichage
                passenger_data = []
                
                if isinstance(all_passengers, list):
                    # Si c'est une liste d'objets passagers
                    for i, passenger in enumerate(all_passengers):
                        if isinstance(passenger, dict):
                            passenger_data.append({
                                "Siège": i + 1,
                                "Nom": passenger.get('name', 'Inconnu'),
                                "Téléphone": passenger.get('phone', 'Non disponible'),
                                "Email": passenger.get('email', 'Non disponible')
                            })
                elif isinstance(all_passengers, str) and all_passengers.strip():
                    # Si c'est un ID utilisateur
                    passenger_data.append({
                        "Siège": 1,
                        "ID Utilisateur": all_passengers,
                        "Détails": "ID utilisateur uniquement"
                    })
                
                if passenger_data:
                    st.dataframe(pd.DataFrame(passenger_data))
            
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations sur les sièges: {str(e)}")
