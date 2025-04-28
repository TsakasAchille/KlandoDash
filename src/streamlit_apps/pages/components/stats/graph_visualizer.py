import streamlit as st
import pandas as pd
import plotly.express as px

class GraphVisualizer:
    """Classe responsable de la visualisation des graphiques de trajets"""
    
    def __init__(self):
        """Initialise le visualiseur de graphiques"""
        pass
    
    def display_trips_graph(self, trips_df):
        """Affiche un graphique des trajets (fonctionne même sans coordonnées GPS)
        
        Args:
            trips_df: DataFrame contenant les données des trajets
        """
        st.subheader("Graphique des trajets")
        
        if 'departure_name' in trips_df.columns and 'destination_name' in trips_df.columns:
            # Créer un DataFrame pour le graphique
            graph_data = trips_df.groupby(['departure_name', 'destination_name']).size().reset_index()
            graph_data.columns = ['Départ', 'Destination', 'Nombre de trajets']
            
            # Créer un graphique de réseau
            fig = px.scatter(graph_data, 
                           x="Départ", 
                           y="Destination",
                           size="Nombre de trajets",
                           color="Nombre de trajets",
                           hover_name="Destination",
                           size_max=40,  
                           color_continuous_scale="Viridis",
                           title="Réseau des trajets")
            
            # Ajouter des lignes entre les points
            for i, row in graph_data.iterrows():
                fig.add_shape(
                    type="line",
                    x0=row['Départ'],
                    y0=row['Destination'],
                    x1=row['Départ'],
                    y1=row['Destination'],
                    line=dict(color="RoyalBlue", width=1),
                )
            
            # Améliorer le style du graphique
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                margin=dict(l=40, r=40, t=40, b=40),
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Afficher aussi un tableau des trajets
            st.subheader("Tableau des trajets")
            st.dataframe(graph_data)
        else:
            st.info("Données insuffisantes pour afficher le graphique des trajets")
            
            # Afficher un tableau simple des trajets disponibles
            if not trips_df.empty:
                st.subheader("Tableau des trajets disponibles")
                st.dataframe(trips_df)
