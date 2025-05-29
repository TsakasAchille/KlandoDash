import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src.streamlit_apps.components.modern_card import modern_card

class StatsGeneralManager:
    """Gère l'affichage des statistiques générales des trajets"""
    
    def display_general_stats(self, trips_df):
        """Affiche les statistiques générales des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.header("Vue générale des trajets")
        
        # Afficher les métriques globales avec modern_card
        self._display_global_metrics(trips_df)
        
        # Afficher les distributions
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des distances
            self._display_distance_distribution(trips_df)
            
        with col2:
            # Distribution du nombre de passagers
            self._display_passenger_distribution(trips_df)
    
    def _display_global_metrics(self, trips_df):
        """Affiche les métriques globales des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        # Calculer les métriques globales
        total_trips = len(trips_df)
        total_distance = trips_df['trip_distance'].sum() if 'trip_distance' in trips_df.columns else 0
        avg_distance = trips_df['trip_distance'].mean() if 'trip_distance' in trips_df.columns else 0
        
        # Calculer le nombre total de passagers si disponible
        if 'passenger_count' in trips_df.columns:
            total_passengers = trips_df['passenger_count'].sum()
            avg_passengers = trips_df['passenger_count'].mean()
        else:
            total_passengers = "Non disponible"
            avg_passengers = "Non disponible"
        
        # Afficher les métriques avec modern_card
        modern_card(
            title="Statistiques globales",
            icon="📊",  # Graphique
            items=[
                ("Total trajets", total_trips),
                ("Distance totale", f"{total_distance:.1f} km"),
                ("Distance moyenne", f"{avg_distance:.1f} km"),
                ("Total passagers", total_passengers if isinstance(total_passengers, str) else f"{total_passengers:.0f}"),
            ],
            accent_color="#3498db"  # Bleu pour les statistiques générales
        )
    
    def _display_distance_distribution(self, trips_df):
        """Affiche la distribution des distances des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Distribution des distances")
        
        if 'trip_distance' in trips_df.columns:
            fig = px.histogram(trips_df, x="trip_distance", nbins=20, 
                            labels={"trip_distance": "Distance (km)"},
                            title="Distribution des distances de trajets",
                            color_discrete_sequence=['#3498db'])
            
            # Améliorer le style du graphique
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(l=40, r=40, t=40, b=40),
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de distance non disponibles")
    
    def _display_passenger_distribution(self, trips_df):
        """Affiche la distribution du nombre de passagers par trajet
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Nombre de passagers par trajet")
        
        if "passenger_count" in trips_df.columns:
            # Créer un DataFrame pour le graphique
            passenger_counts = trips_df["passenger_count"].value_counts().reset_index()
            passenger_counts.columns = ["Nombre de passagers", "Nombre de trajets"]
            
            fig = px.bar(passenger_counts, 
                        x="Nombre de passagers", 
                        y="Nombre de trajets",
                        title="Distribution du nombre de passagers par trajet",
                        color_discrete_sequence=['#2ecc71'])
            
            # Améliorer le style du graphique
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(l=40, r=40, t=40, b=40),
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de passagers non disponibles")
