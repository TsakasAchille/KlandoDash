import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.streamlit_apps.components.modern_card import modern_card

class StatsGeographicManager:
    """Gu00e8re l'affichage des statistiques gu00e9ographiques des trajets"""
    
    def display_geographic_stats(self, trips_df):
        """Affiche les statistiques géographiques des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.header("Analyse géographique")
        
        # Vérifier si les colonnes géographiques sont disponibles
        has_geo_data = all(col in trips_df.columns for col in ['departure_name', 'destination_name'])
        has_coordinates = all(col in trips_df.columns for col in ['departure_lat', 'departure_lng', 'destination_lat', 'destination_lng'])
        
        if has_geo_data:
            # Afficher les métriques géographiques
            self._display_geographic_metrics(trips_df)
            
            # Afficher les graphiques géographiques
            col1, col2 = st.columns(2)
            
            with col1:
                self._display_departure_distribution(trips_df)
            
            with col2:
                self._display_destination_distribution(trips_df)
                
            # Afficher la matrice origine-destination si les données sont disponibles
            self._display_origin_destination_matrix(trips_df)
        else:
            st.info("Données géographiques insuffisantes pour l'analyse")
    
    def _display_geographic_metrics(self, trips_df):
        """Affiche les métriques géographiques des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        # Calculer les métriques géographiques
        unique_departures = trips_df['departure_name'].nunique() if 'departure_name' in trips_df.columns else 0
        unique_destinations = trips_df['destination_name'].nunique() if 'destination_name' in trips_df.columns else 0
        
        # Trouver les lieux les plus fréquents
        most_common_departure = trips_df['departure_name'].mode()[0] if 'departure_name' in trips_df.columns else "Non disponible"
        most_common_destination = trips_df['destination_name'].mode()[0] if 'destination_name' in trips_df.columns else "Non disponible"
        
        # Calculer la distance moyenne si disponible
        avg_distance = trips_df['trip_distance'].mean() if 'trip_distance' in trips_df.columns else 0
        
        # Afficher les métriques avec modern_card
        modern_card(
            title="Métriques de la ville",
            icon="🏙️",  # Ville ou géographie
            items=[
                ("Lieux de départ uniques", unique_departures),
                ("Destinations uniques", unique_destinations),
                ("Départ le plus fréquent", most_common_departure),
                ("Destination la plus fréquente", most_common_destination),
                ("Distance moyenne", f"{avg_distance:.1f} km")
            ],
            accent_color="#e74c3c"  # Rouge pour les statistiques géographiques
        )
    
    def _display_departure_distribution(self, trips_df):
        """Affiche la distribution des lieux de départ
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Lieux de départ les plus fréquents")
        
        if 'departure_name' in trips_df.columns:
            # Créer un DataFrame pour le graphique
            departure_counts = trips_df['departure_name'].value_counts().reset_index()
            departure_counts.columns = ["Lieu de départ", "Nombre de trajets"]
            
            # Limiter aux 10 premiers pour la lisibilité
            departure_counts = departure_counts.head(10)
            
            fig = px.bar(departure_counts, 
                        x="Nombre de trajets", 
                        y="Lieu de départ",
                        title="Top 10 des lieux de départ",
                        color_discrete_sequence=['#e74c3c'],
                        orientation='h')
            
            # Améliorer le style du graphique
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(l=40, r=40, t=40, b=40),
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de lieux de départ non disponibles")
    
    def _display_destination_distribution(self, trips_df):
        """Affiche la distribution des destinations
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Destinations les plus fréquentes")
        
        if 'destination_name' in trips_df.columns:
            # Créer un DataFrame pour le graphique
            destination_counts = trips_df['destination_name'].value_counts().reset_index()
            destination_counts.columns = ["Destination", "Nombre de trajets"]
            
            # Limiter aux 10 premiers pour la lisibilité
            destination_counts = destination_counts.head(10)
            
            fig = px.bar(destination_counts, 
                        x="Nombre de trajets", 
                        y="Destination",
                        title="Top 10 des destinations",
                        color_discrete_sequence=['#e74c3c'],
                        orientation='h')
            
            # Améliorer le style du graphique
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(l=40, r=40, t=40, b=40),
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de destinations non disponibles")
    
    def _display_origin_destination_matrix(self, trips_df):
        """Affiche la matrice origine-destination
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Matrice Origine-Destination")
        
        if 'departure_name' in trips_df.columns and 'destination_name' in trips_df.columns:
            # Créer la matrice origine-destination
            od_matrix = pd.crosstab(trips_df['departure_name'], trips_df['destination_name'])
            
            # Limiter aux 10 origines et destinations les plus fréquentes pour la lisibilité
            top_origins = trips_df['departure_name'].value_counts().head(10).index
            top_destinations = trips_df['destination_name'].value_counts().head(10).index
            
            od_matrix_filtered = od_matrix.loc[od_matrix.index.isin(top_origins), od_matrix.columns.isin(top_destinations)]
            
            # Créer la heatmap
            fig = px.imshow(od_matrix_filtered,
                           labels=dict(x="Destination", y="Origine", color="Nombre de trajets"),
                           title="Matrice Origine-Destination (Top 10)",
                           color_continuous_scale='Reds')
            
            # Améliorer le style du graphique
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(l=40, r=40, t=40, b=40),
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données d'origine-destination non disponibles")
