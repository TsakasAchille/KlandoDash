import streamlit as st
import pandas as pd
from src.streamlit_apps.pages.components.trip_map import TripMap
from src.streamlit_apps.pages.components.stats.region_mapper import RegionMapper
from src.streamlit_apps.pages.components.stats.heatmap_visualizer import HeatmapVisualizer
from src.streamlit_apps.pages.components.stats.graph_visualizer import GraphVisualizer
from src.streamlit_apps.pages.components.stats.map_metrics import MapMetrics

class StatsMapManager:
    """Gère l'affichage de la carte des trajets"""
    
    def __init__(self):
        """Initialise le gestionnaire de carte"""
        self.trip_map = TripMap()
        self.region_mapper = RegionMapper()
        self.heatmap_visualizer = HeatmapVisualizer(self.region_mapper)
        self.graph_visualizer = GraphVisualizer()
        self.map_metrics = MapMetrics()
    
    def display_map_stats(self, trips_df):
        """Affiche la carte des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.header("Carte des trajets")
        
        # Afficher les métriques de la carte
        self.map_metrics.display_map_metrics(trips_df)
        
        # Vérifier si les colonnes de coordonnées sont disponibles
        has_coordinates = all(col in trips_df.columns for col in ['departure_latitude', 'departure_longitude', 'destination_latitude', 'destination_longitude'])
        
        # Si les colonnes ont les anciens noms, les renommer pour compatibilité
        if not has_coordinates and all(col in trips_df.columns for col in ['departure_lat', 'departure_lng', 'destination_lat', 'destination_lng']):
            trips_df = trips_df.copy()
            # Créer un mapping des anciens noms vers les nouveaux noms
            column_mapping = {
                'departure_lat': 'departure_latitude',
                'departure_lng': 'departure_longitude',
                'destination_lat': 'destination_latitude',
                'destination_lng': 'destination_longitude'
            }
            # Renommer les colonnes
            trips_df.rename(columns=column_mapping, inplace=True)
            has_coordinates = True
        
        # Attribuer les régions de départ et d'arrivée
        trips_df = self.region_mapper.assign_regions_to_trips(trips_df)
        
        # Ajouter des options d'affichage pour la carte
        st.subheader("Options d'affichage")
        
        # Créer des options d'affichage interactives
        col1, col2 = st.columns(2)
        
        with col1:
            # Option pour choisir le type de visualisation
            map_type = st.selectbox(
                "Type de visualisation",
                ["Carte interactive", "Carte de chaleur des trajets", "Graphique des trajets"],
                index=0
            )
            
            # Option pour filtrer les trajets
            if 'departure_name' in trips_df.columns:
                # Filtrer les valeurs None et les remplacer par "Non spécifié"
                departure_names = trips_df['departure_name'].fillna("Non spécifié").unique().tolist()
                all_departures = ["Tous"] + sorted(departure_names)
                selected_departure = st.selectbox("Filtrer par lieu de départ", all_departures)
            else:
                selected_departure = "Tous"
        
        with col2:
            # Option pour limiter le nombre de trajets affichés
            max_trips = st.slider("Nombre maximum de trajets à afficher", 1, 50, 10)
            
            # Option pour filtrer les trajets
            if 'destination_name' in trips_df.columns:
                # Filtrer les valeurs None et les remplacer par "Non spécifié"
                destination_names = trips_df['destination_name'].fillna("Non spécifié").unique().tolist()
                all_destinations = ["Tous"] + sorted(destination_names)
                selected_destination = st.selectbox("Filtrer par destination", all_destinations)
            else:
                selected_destination = "Tous"
        
        # Filtrer les trajets selon les sélections
        filtered_trips = trips_df.copy()
        
        if selected_departure != "Tous" and 'departure_name' in filtered_trips.columns:
            filtered_trips = filtered_trips[filtered_trips['departure_name'] == selected_departure]
            
        if selected_destination != "Tous" and 'destination_name' in filtered_trips.columns:
            filtered_trips = filtered_trips[filtered_trips['destination_name'] == selected_destination]
        
        # Limiter le nombre de trajets
        filtered_trips = filtered_trips.head(max_trips)
        
        # Afficher le nombre de trajets filtrés
        st.info(f"Affichage de {len(filtered_trips)} trajets sur {len(trips_df)} au total")
        
        # Afficher la visualisation selon le type sélectionné
        if map_type == "Carte interactive" and has_coordinates:
            self._display_interactive_map(filtered_trips)
        elif map_type == "Carte de chaleur des trajets" and has_coordinates:
            self.heatmap_visualizer.display_heatmap(filtered_trips)
        elif map_type == "Graphique des trajets":
            self.graph_visualizer.display_trips_graph(filtered_trips)
        else:
            st.warning("Les coordonnées GPS sont manquantes pour afficher cette carte. Utilisation du graphique des trajets à la place.")
            self.graph_visualizer.display_trips_graph(filtered_trips)
    
    def _display_interactive_map(self, trips_df):
        """Affiche une carte interactive des trajets
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Carte interactive des trajets")
        
        try:
            # Afficher tous les trajets sur une seule carte interactive
            self.trip_map.display_multiple_trips_map(trips_df, max_trips=len(trips_df), height=600, width=800)
            
            # Afficher un tableau récapitulatif des trajets
            with st.expander("Détails des trajets", expanded=False):
                # Créer un tableau récapitulatif des trajets
                summary_df = trips_df.copy()
                
                # Sélectionner les colonnes pertinentes si elles existent
                display_columns = []
                for col in ['departure_name', 'destination_name', 'trip_distance', 'price_per_seat', 'departure_date']:
                    if col in summary_df.columns:
                        display_columns.append(col)
                
                if display_columns:
                    st.dataframe(summary_df[display_columns])
                else:
                    st.dataframe(summary_df)
                    
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la carte interactive: {str(e)}")
