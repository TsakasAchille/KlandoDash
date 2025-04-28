import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from src.streamlit_apps.components.modern_card import modern_card

class StatsTemporalManager:
    """Gère l'affichage des statistiques temporelles des trajets"""
    
    def display_temporal_stats(self, trips_df):
        """Affiche les statistiques temporelles des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.header("Analyse temporelle")
        
        # Identifier la colonne de date (selon la migration PostgreSQL)
        date_column = None
        for col in ['departure_schedule', 'departure_time', 'created_at']:
            if col in trips_df.columns:
                date_column = col
                break
        
        if date_column is not None:
            # Préparer les données temporelles
            try:
                # S'assurer que la colonne est au format datetime
                trips_df[date_column] = pd.to_datetime(trips_df[date_column])
                
                # Extraire les composantes temporelles
                trips_df['year'] = trips_df[date_column].dt.year
                trips_df['month'] = trips_df[date_column].dt.month
                trips_df['day'] = trips_df[date_column].dt.day
                trips_df['weekday'] = trips_df[date_column].dt.weekday
                trips_df['hour'] = trips_df[date_column].dt.hour
                
                # Afficher les statistiques temporelles
                self._display_temporal_metrics(trips_df, date_column)
                
                # Afficher les graphiques temporels
                col1, col2 = st.columns(2)
                
                with col1:
                    self._display_monthly_distribution(trips_df)
                    self._display_hourly_distribution(trips_df)
                
                with col2:
                    self._display_weekday_distribution(trips_df)
                    self._display_time_series(trips_df, date_column)
                
            except Exception as e:
                st.error(f"Erreur lors de l'analyse temporelle: {str(e)}")
        else:
            st.info("Aucune colonne de date disponible pour l'analyse temporelle")
    
    def _display_temporal_metrics(self, trips_df, date_column):
        """Affiche les métriques temporelles des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
            date_column: Nom de la colonne contenant les dates
        """
        # Calculer les métriques temporelles
        min_date = trips_df[date_column].min().strftime('%d/%m/%Y')
        max_date = trips_df[date_column].max().strftime('%d/%m/%Y')
        date_range = (trips_df[date_column].max() - trips_df[date_column].min()).days
        
        # Calculer le jour de la semaine le plus fréquent
        weekday_mapping = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
        most_common_weekday = weekday_mapping[trips_df['weekday'].mode()[0]]
        
        # Calculer l'heure la plus fréquente
        most_common_hour = trips_df['hour'].mode()[0]
        
        # Afficher les métriques avec modern_card
        modern_card(
            title="Métriques temporelles",
            icon="📅",  # Calendrier
            items=[
                ("Premier trajet", min_date),
                ("Dernier trajet", max_date),
                ("Période couverte", f"{date_range} jours"),
                ("Jour le plus fréquent", most_common_weekday),
                ("Heure la plus fréquente", f"{most_common_hour}h")
            ],
            accent_color="#9b59b6"  # Violet pour les statistiques temporelles
        )
    
    def _display_monthly_distribution(self, trips_df):
        """Affiche la distribution mensuelle des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Distribution mensuelle")
        
        # Créer un DataFrame pour le graphique
        month_mapping = {1: 'Jan', 2: 'Fév', 3: 'Mar', 4: 'Avr', 5: 'Mai', 6: 'Juin', 
                        7: 'Juil', 8: 'Août', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Déc'}
        
        monthly_counts = trips_df['month'].value_counts().reset_index()
        monthly_counts.columns = ["Mois", "Nombre de trajets"]
        monthly_counts['Mois_nom'] = monthly_counts['Mois'].map(month_mapping)
        monthly_counts = monthly_counts.sort_values('Mois')
        
        fig = px.bar(monthly_counts, 
                    x="Mois_nom", 
                    y="Nombre de trajets",
                    title="Distribution mensuelle des trajets",
                    color_discrete_sequence=['#9b59b6'])
        
        # Améliorer le style du graphique
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_weekday_distribution(self, trips_df):
        """Affiche la distribution par jour de la semaine des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Distribution par jour de la semaine")
        
        # Créer un DataFrame pour le graphique
        weekday_mapping = {0: 'Lundi', 1: 'Mardi', 2: 'Mercredi', 3: 'Jeudi', 4: 'Vendredi', 5: 'Samedi', 6: 'Dimanche'}
        
        weekday_counts = trips_df['weekday'].value_counts().reset_index()
        weekday_counts.columns = ["Jour", "Nombre de trajets"]
        weekday_counts['Jour_nom'] = weekday_counts['Jour'].map(weekday_mapping)
        weekday_counts = weekday_counts.sort_values('Jour')
        
        fig = px.bar(weekday_counts, 
                    x="Jour_nom", 
                    y="Nombre de trajets",
                    title="Distribution par jour de la semaine",
                    color_discrete_sequence=['#9b59b6'])
        
        # Améliorer le style du graphique
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_hourly_distribution(self, trips_df):
        """Affiche la distribution horaire des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Distribution horaire")
        
        # Créer un DataFrame pour le graphique
        hourly_counts = trips_df['hour'].value_counts().reset_index()
        hourly_counts.columns = ["Heure", "Nombre de trajets"]
        hourly_counts = hourly_counts.sort_values('Heure')
        
        fig = px.bar(hourly_counts, 
                    x="Heure", 
                    y="Nombre de trajets",
                    title="Distribution horaire des trajets",
                    color_discrete_sequence=['#9b59b6'])
        
        # Améliorer le style du graphique
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_time_series(self, trips_df, date_column):
        """Affiche la série temporelle des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
            date_column: Nom de la colonne contenant les dates
        """
        st.subheader("Évolution temporelle")
        
        # Créer un DataFrame pour le graphique
        trips_df['date'] = trips_df[date_column].dt.date
        time_series = trips_df.groupby('date').size().reset_index()
        time_series.columns = ["Date", "Nombre de trajets"]
        
        fig = px.line(time_series, 
                    x="Date", 
                    y="Nombre de trajets",
                    title="Évolution du nombre de trajets dans le temps",
                    color_discrete_sequence=['#9b59b6'])
        
        # Améliorer le style du graphique
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        st.plotly_chart(fig, use_container_width=True)
