import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.streamlit_apps.components.modern_card import modern_card

class StatsFinancialManager:
    """Gère l'affichage des statistiques financières des trajets"""
    
    def display_financial_stats(self, trips_df):
        """Affiche les statistiques financières des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.header("Analyse financière")
        
        # Vérifier si les colonnes financières sont disponibles
        has_price_data = 'price_per_seat' in trips_df.columns
        has_viator_data = 'viator_income' in trips_df.columns
        
        if has_price_data or has_viator_data:
            # Afficher les métriques financières
            self._display_financial_metrics(trips_df)
            
            # Afficher les graphiques financiers
            col1, col2 = st.columns(2)
            
            with col1:
                self._display_price_distribution(trips_df)
                if has_viator_data:
                    self._display_viator_income_distribution(trips_df)
            
            with col2:
                self._display_price_vs_distance(trips_df)
                self._display_income_time_series(trips_df)
        else:
            st.info("Données financières insuffisantes pour l'analyse")
    
    def _display_financial_metrics(self, trips_df):
        """Affiche les métriques financières des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        # Calculer les métriques financières
        avg_price = trips_df['price_per_seat'].mean() if 'price_per_seat' in trips_df.columns else 0
        total_price = trips_df['price_per_seat'].sum() if 'price_per_seat' in trips_df.columns else 0
        
        # Calculer les métriques de Viator si disponibles
        avg_viator_income = trips_df['viator_income'].mean() if 'viator_income' in trips_df.columns else 0
        total_viator_income = trips_df['viator_income'].sum() if 'viator_income' in trips_df.columns else 0
        
        # Calculer le prix par kilomètre si les deux colonnes sont disponibles
        if 'price_per_seat' in trips_df.columns and 'trip_distance' in trips_df.columns:
            # Éviter la division par zéro
            valid_trips = trips_df[trips_df['trip_distance'] > 0]
            price_per_km = valid_trips['price_per_seat'] / valid_trips['trip_distance']
            avg_price_per_km = price_per_km.mean()
        else:
            avg_price_per_km = 0
        
        # Afficher les métriques avec modern_card
        modern_card(
            title="Métriques financières",
            icon="💰",  # Argent
            items=[
                ("Prix moyen par place", f"{avg_price:.0f} XOF"),
                ("Revenu total", f"{total_price:.0f} XOF"),
                ("Revenu Viator moyen", f"{avg_viator_income:.0f} XOF"),
                ("Revenu Viator total", f"{total_viator_income:.0f} XOF"),
                ("Prix moyen par km", f"{avg_price_per_km:.0f} XOF/km")
            ],
            accent_color="#f39c12"  # Orange pour les statistiques financières
        )
    
    def _display_price_distribution(self, trips_df):
        """Affiche la distribution des prix par place
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Distribution des prix par place")
        
        if 'price_per_seat' in trips_df.columns:
            fig = px.histogram(trips_df, x="price_per_seat", nbins=20, 
                            labels={"price_per_seat": "Prix par place (XOF)"},
                            title="Distribution des prix par place",
                            color_discrete_sequence=['#f39c12'])
            
            # Améliorer le style du graphique
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(l=40, r=40, t=40, b=40),
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de prix non disponibles")
    
    def _display_viator_income_distribution(self, trips_df):
        """Affiche la distribution des revenus Viator
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Distribution des revenus Viator")
        
        if 'viator_income' in trips_df.columns:
            fig = px.histogram(trips_df, x="viator_income", nbins=20, 
                            labels={"viator_income": "Revenu Viator (XOF)"},
                            title="Distribution des revenus Viator",
                            color_discrete_sequence=['#f39c12'])
            
            # Améliorer le style du graphique
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(l=40, r=40, t=40, b=40),
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de revenus Viator non disponibles")
    
    def _display_price_vs_distance(self, trips_df):
        """Affiche la relation entre prix et distance
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Prix vs Distance")
        
        if 'price_per_seat' in trips_df.columns and 'trip_distance' in trips_df.columns:
            fig = px.scatter(trips_df, x="trip_distance", y="price_per_seat", 
                           labels={"trip_distance": "Distance (km)", "price_per_seat": "Prix par place (XOF)"},
                           title="Relation entre prix et distance",
                           color_discrete_sequence=['#f39c12'])
            
            # Ajouter une ligne de tendance
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(l=40, r=40, t=40, b=40),
            )
            
            # Ajouter une ligne de tendance
            fig.update_traces(mode='markers')
            
            try:
                # Vérifier qu'il y a suffisamment de données valides pour calculer une tendance
                valid_data = trips_df.dropna(subset=['trip_distance', 'price_per_seat'])
                
                # Vérifier qu'il y a au moins 2 points de données différents
                if len(valid_data) >= 2 and valid_data['trip_distance'].nunique() >= 2:
                    z = np.polyfit(valid_data['trip_distance'], valid_data['price_per_seat'], 1)
                    y_hat = np.poly1d(z)(valid_data['trip_distance'])
                    
                    fig.add_traces(
                        go.Scatter(
                            x=valid_data['trip_distance'],
                            y=y_hat,
                            mode='lines',
                            name='Tendance',
                            line=dict(color='red')
                        )
                    )
                else:
                    st.info("Pas assez de données pour calculer une ligne de tendance")
            except Exception as e:
                st.warning(f"Impossible de calculer la ligne de tendance: {str(e)}")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de prix ou de distance non disponibles")   
    
    def _display_income_time_series(self, trips_df):
        """Affiche l'évolution des revenus dans le temps
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Évolution des revenus")
        
        # Identifier la colonne de date (selon la migration PostgreSQL)
        date_column = None
        for col in ['departure_schedule', 'departure_time', 'created_at']:
            if col in trips_df.columns:
                date_column = col
                break
        
        if date_column is not None and 'price_per_seat' in trips_df.columns:
            try:
                # S'assurer que la colonne est au format datetime
                trips_df[date_column] = pd.to_datetime(trips_df[date_column])
                
                # Extraire le mois et l'année
                trips_df['month_year'] = trips_df[date_column].dt.to_period('M')
                
                # Agréger par mois
                monthly_revenue = trips_df.groupby('month_year')['price_per_seat'].sum().reset_index()
                monthly_revenue['month_year'] = monthly_revenue['month_year'].astype(str)
                
                fig = px.line(monthly_revenue, 
                            x="month_year", 
                            y="price_per_seat",
                            labels={"month_year": "Mois", "price_per_seat": "Revenu total (XOF)"},
                            title="Évolution des revenus mensuels",
                            color_discrete_sequence=['#f39c12'])
                
                # Améliorer le style du graphique
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    margin=dict(l=40, r=40, t=40, b=40),
                )
                
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Erreur lors de l'analyse temporelle des revenus: {str(e)}")
        else:
            st.info("Données temporelles ou de prix non disponibles")
