import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

class HeatmapVisualizer:
    """Classe responsable de la visualisation des cartes de chaleur"""
    
    def __init__(self, region_mapper):
        """Initialise le visualiseur de carte de chaleur
        
        Args:
            region_mapper: Instance de RegionMapper pour accu00e9der aux donnu00e9es de ru00e9gions
        """
        self.region_mapper = region_mapper
    
    def display_heatmap(self, trips_df):
        """Affiche une carte de chaleur des trajets par région
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Carte de chaleur des trajets par région")
        
        try:
            # Attribuer les régions aux trajets si ce n'est pas déjà fait
            if not ('departure_region' in trips_df.columns and 'destination_region' in trips_df.columns):
                trips_df = self.region_mapper.assign_regions_to_trips(trips_df)
            
            # Afficher des informations de débogage
            with st.expander("Informations de débogage", expanded=False):
                st.write("Colonnes disponibles:", trips_df.columns.tolist())
                st.write("Nombre de trajets avec régions attribuées:", 
                         trips_df.dropna(subset=['departure_region', 'destination_region']).shape[0])
                st.write("Régions de départ uniques:", trips_df['departure_region'].unique().tolist())
                st.write("Régions de destination uniques:", trips_df['destination_region'].unique().tolist())
                
                # Afficher un échantillon des données
                st.write("Échantillon des données:")
                st.dataframe(trips_df[['departure_name', 'departure_region', 'departure_latitude', 'departure_longitude', 
                                       'destination_name', 'destination_region', 'destination_latitude', 'destination_longitude']].head())
            
            # Vérifier si des régions ont été attribuées
            has_regions = 'departure_region' in trips_df.columns and 'destination_region' in trips_df.columns
            region_df = trips_df.copy()
            
            if has_regions:
                # Créer un DataFrame pour la carte de chaleur par région
                # Compter les trajets par région de départ
                if 'departure_region' in region_df.columns:
                    departure_counts = region_df.groupby('departure_region').size().reset_index()
                    departure_counts.columns = ['region', 'count']
                    departure_counts['type'] = 'Départ'
                
                # Compter les trajets par région de destination
                if 'destination_region' in region_df.columns:
                    destination_counts = region_df.groupby('destination_region').size().reset_index()
                    destination_counts.columns = ['region', 'count']
                    destination_counts['type'] = 'Destination'
                
                # Combiner les comptages
                if 'departure_region' in region_df.columns and 'destination_region' in region_df.columns:
                    region_counts = pd.concat([departure_counts, destination_counts])
                elif 'departure_region' in region_df.columns:
                    region_counts = departure_counts
                else:
                    region_counts = destination_counts
                
                # Agréger les comptages par région (somme des départements et destinations)
                total_by_region = region_counts.groupby('region')['count'].sum().reset_index()
                
                # Afficher un tableau des trajets par région
                with st.expander("Détails par région", expanded=False):
                    st.dataframe(total_by_region.sort_values('count', ascending=False))
                    
                    # Afficher les flux entre régions
                    if 'departure_region' in region_df.columns and 'destination_region' in region_df.columns:
                        st.subheader("Flux entre régions")
                        region_flow = region_df.groupby(['departure_region', 'destination_region']).size().reset_index()
                        region_flow.columns = ['Région de départ', 'Région de destination', 'Nombre de trajets']
                        st.dataframe(region_flow.sort_values('Nombre de trajets', ascending=False))
                
                self._display_region_heatmap(total_by_region)
                self._display_region_flow(region_df)
            else:
                # Si pas de données de région, utiliser la carte de chaleur standard
                st.warning("Données de région non disponibles. Affichage de la carte de chaleur standard.")
                self._display_standard_heatmap(trips_df)
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de la carte de chaleur: {str(e)}")
            # Afficher la trace de l'erreur pour débogage
            import traceback
            st.code(traceback.format_exc())
    
    def _display_region_heatmap(self, total_by_region):
        """Affiche une carte de chaleur par région
        
        Args:
            total_by_region: DataFrame avec le nombre de trajets par région
        """
        st.subheader("Carte de chaleur du Sénégal")
        
        # Créer un DataFrame avec les coordonnées des régions
        region_coords = self.region_mapper.get_region_coordinates()
        
        # Fusionner avec les comptages de trajets
        region_map_data = pd.merge(region_coords, total_by_region, on='region', how='left')
        region_map_data['count'] = region_map_data['count'].fillna(0)
        
        # Afficher les données pour débogage
        with st.expander("Données de la carte", expanded=False):
            st.dataframe(region_map_data)
        
        # Créer une carte de chaleur centrée sur le Sénégal
        fig = px.scatter_mapbox(region_map_data,
                              lat="lat",
                              lon="lon",
                              size="count",
                              color="count",
                              hover_name="region",
                              size_max=50,  
                              zoom=6,
                              center=self.region_mapper.get_senegal_center(),  
                              mapbox_style="carto-positron",
                              title="Nombre de trajets par région au Sénégal")
        
        # Améliorer la mise en page et augmenter la hauteur
        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            coloraxis_colorbar=dict(title="Nombre de trajets"),
            height=700,  
            coloraxis=dict(colorscale="Viridis", colorbar=dict(thickness=20))
        )
        
        # Afficher la carte
        st.plotly_chart(fig, use_container_width=True)
    
    def _display_region_flow(self, region_df):
        """Affiche une carte de flux entre régions
        
        Args:
            region_df: DataFrame avec les régions de départ et d'arrivée
        """
        if 'departure_region' in region_df.columns and 'destination_region' in region_df.columns:
            st.subheader("Flux de trajets entre régions")
            
            # Préparer les données de flux
            flow_data = region_df.groupby(['departure_region', 'destination_region']).size().reset_index()
            flow_data.columns = ['origin', 'destination', 'count']
            
            # Ne garder que les flux avec des régions connues
            known_regions = list(self.region_mapper.senegal_regions.keys())
            flow_data = flow_data[
                flow_data['origin'].isin(known_regions) & 
                flow_data['destination'].isin(known_regions)
            ]
            
            if not flow_data.empty:
                # Obtenir les coordonnées des régions
                region_coords = self.region_mapper.get_region_coordinates()
                
                # Ajouter les coordonnées
                flow_data = flow_data.merge(
                    region_coords.rename(columns={'region': 'origin', 'lat': 'lat_origin', 'lon': 'lon_origin'}),
                    on='origin'
                )
                flow_data = flow_data.merge(
                    region_coords.rename(columns={'region': 'destination', 'lat': 'lat_dest', 'lon': 'lon_dest'}),
                    on='destination'
                )
                
                # Afficher les données de flux pour débogage
                with st.expander("Données de flux", expanded=False):
                    st.dataframe(flow_data)
                
                # Créer la carte de flux
                fig = go.Figure()
                
                # Ajouter les points pour les régions
                fig.add_trace(go.Scattermapbox(
                    lat=region_coords['lat'],
                    lon=region_coords['lon'],
                    mode='markers',
                    marker=dict(size=10, color='red'),
                    text=region_coords['region'],
                    hoverinfo='text'
                ))
                
                # Ajouter les lignes pour les flux
                for _, row in flow_data.iterrows():
                    fig.add_trace(go.Scattermapbox(
                        lat=[row['lat_origin'], row['lat_dest']],
                        lon=[row['lon_origin'], row['lon_dest']],
                        mode='lines',
                        line=dict(width=1 + row['count']/5, color='blue'),
                        opacity=0.6,
                        hoverinfo='text',
                        text=f"{row['origin']} u2192 {row['destination']}: {row['count']} trajets"
                    ))
                
                # Configuration de la carte
                fig.update_layout(
                    mapbox=dict(
                        style="carto-positron",
                        zoom=6,
                        center=self.region_mapper.get_senegal_center()  
                    ),
                    margin=dict(l=0, r=0, t=50, b=0),
                    height=700,  
                    title="Flux de trajets entre les régions du Sénégal"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Pas de données de flux entre les régions connues du Sénégal.")
    
    def _display_standard_heatmap(self, trips_df):
        """Affiche une carte de chaleur standard basu00e9e sur les coordonnu00e9es GPS
        
        Args:
            trips_df: DataFrame contenant les donnu00e9es des trajets
        """
        # Cru00e9er un DataFrame pour la carte de chaleur
        departures = trips_df[['departure_latitude', 'departure_longitude']].copy()
        departures.columns = ['lat', 'lon']
        departures['count'] = 1
        
        destinations = trips_df[['destination_latitude', 'destination_longitude']].copy()
        destinations.columns = ['lat', 'lon']
        destinations['count'] = 1
        
        # Combiner les points
        heatmap_data = pd.concat([departures, destinations])
        
        # Agru00e9ger les points pour la carte de chaleur
        heatmap_data = heatmap_data.groupby(['lat', 'lon']).sum().reset_index()
        
        # Afficher la carte de chaleur avec Plotly
        fig = px.density_mapbox(heatmap_data, 
                            lat="lat", 
                            lon="lon", 
                            z="count",
                            radius=15,  
                            zoom=6,
                            center=self.region_mapper.get_senegal_center(),  
                            mapbox_style="carto-positron",
                            color_continuous_scale="Viridis",  
                            opacity=0.8,  
                            title="Carte de chaleur des trajets au Sénégal")
        
        # Augmenter la hauteur de la carte
        fig.update_layout(
            height=700,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
