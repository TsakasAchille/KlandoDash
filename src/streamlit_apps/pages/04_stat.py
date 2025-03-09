import sys
import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Ajouter le dossier src au PYTHONPATH pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))) 

from src.data_processing.processors.trip_processor import TripProcessor
from src.data_processing.processors.user_processor import UserProcessor
from src.streamlit_apps.components import Table, Styles, setup_page
from src.streamlit_apps.pages.components.trips import TripsApp
from src.streamlit_apps.pages.components.page_01.trip_T2_C1 import TripMap

# Configuration de la page
setup_page()
st.title("Statistiques des Trajets")

# Chargement des données


trips_df = TripsApp().get_data()

if trips_df is None:
    st.error("Aucun trajet trouvé")
else:
    st.session_state["trip_df"] = trips_df



# Affichage du nombre total de trajets
st.write(f"**Nombre total de trajets**: {len(trips_df)}")

# Création des onglets pour différentes statistiques
tabs = st.tabs(["Vue générale", "Analyse temporelle", "Analyse géographique", "Analyse financière", "Carte des trajets"])

with tabs[0]:
    st.header("Vue générale des trajets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution des trip_distances
        st.subheader("Distribution des trip_distances")
        fig = px.histogram(trips_df, x="trip_distance", nbins=20, 
                           labels={"trip_distance": "Distance (km)"},
                           title="Distribution des trip_distances de trajets")
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribution du nombre de passagers
        st.subheader("Nombre de passagers par trajet")
        if "passenger_count" in trips_df.columns:
            fig = px.bar(trips_df["passenger_count"].value_counts().reset_index(), 
                         x="index", y="passenger_count",
                         labels={"index": "Nombre de passagers", "passenger_count": "Nombre de trajets"},
                         title="Répartition des trajets par nombre de passagers")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données sur le nombre de passagers non disponibles")
    
    with col2:
        # Trajets par statut
        st.subheader("Statut des trajets")
        if "status" in trips_df.columns:
            fig = px.pie(trips_df, names="status", hole=0.4,
                         title="Répartition des trajets par statut")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de statut non disponibles")
        
        # Top des villes de départ
      # Top des villes de départ
        st.subheader("Top 10 des villes de départ")
        if "departure_name" in trips_df.columns:
            top_departures = trips_df["departure_name"].value_counts().reset_index()
            top_departures.columns = ["departure_name", "count"]  # Renommer explicitement les colonnes
            top_departures = top_departures.head(10)
            
            fig = px.bar(top_departures, x="count", y="departure_name", orientation='h',
                        labels={"departure_name": "Ville de départ", "count": "Nombre de trajets"},
                        title="Top 10 des villes de départ")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données sur les villes de départ non disponibles")

with tabs[1]:
    st.header("Analyse temporelle")
    
    if "departure_date" in trips_df.columns:
        # Préparation des données temporelles
        trips_df['year_month'] = trips_df['departure_date'].dt.strftime('%Y-%m')
        trips_df['day_of_week'] = trips_df['departure_date'].dt.day_name()
        trips_df['hour'] = trips_df['departure_date'].dt.hour
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Trajets par mois
            monthly_trips = trips_df.groupby('year_month').size().reset_index(name='count')
            fig = px.line(monthly_trips, x='year_month', y='count', markers=True,
                          labels={"year_month": "Mois", "count": "Nombre de trajets"},
                          title="Évolution du nombre de trajets par mois")
            st.plotly_chart(fig, use_container_width=True)
            
            # Trajets par heure de la journée
            hourly_trips = trips_df.groupby('hour').size().reset_index(name='count')
            fig = px.bar(hourly_trips, x='hour', y='count',
                         labels={"hour": "Heure de la journée", "count": "Nombre de trajets"},
                         title="Répartition des trajets par heure")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Trajets par jour de la semaine
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            weekday_trips = trips_df.groupby('day_of_week').size().reset_index(name='count')
            weekday_trips['day_of_week'] = pd.Categorical(weekday_trips['day_of_week'], categories=days_order, ordered=True)
            weekday_trips = weekday_trips.sort_values('day_of_week')
            
            fig = px.bar(weekday_trips, x='day_of_week', y='count',
                         labels={"day_of_week": "Jour de la semaine", "count": "Nombre de trajets"},
                         title="Répartition des trajets par jour de la semaine")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Données temporelles non disponibles")

with tabs[2]:
    st.header("Analyse géographique")
    
    # Top des trajets par ville de départ et d'arrivée
    if "departure_name" in trips_df.columns and "destination_name" in trips_df.columns:
        # Création d'une colonne combinée départ-arrivée
    # Modification à appliquer autour de la ligne 139
        trips_df['route'] = trips_df['departure_name'] + ' → ' + trips_df['destination_name']
        top_routes = trips_df['route'].value_counts().reset_index()
        top_routes.columns = ["route", "count"]  # Renommer explicitement les colonnes
        top_routes = top_routes.head(15)
                
        fig = px.bar(top_routes, x="count", y="route", orientation='h',
                     labels={"route": "Trajet", "count": "Nombre de trajets"},
                     title="Top 15 des trajets les plus fréquents")
        st.plotly_chart(fig, use_container_width=True)
        
        # Carte des points de départ
        st.subheader("Carte des points de départ fréquents")
        if all(col in trips_df.columns for col in ['departure_latitude', 'departure_longitude']):
            departure_counts = trips_df.groupby(['departure_name', 'departure_latitude', 'departure_longitude']).size().reset_index(name='count')
            departure_counts = departure_counts.dropna(subset=['departure_latitude', 'departure_longitude'])
            
            fig = px.scatter_mapbox(departure_counts, 
                                   lat="departure_latitude", 
                                   lon="departure_longitude",
                                   size="count",
                                   hover_name="departure_name",
                                   color="count",
                                   zoom=5,
                                   mapbox_style="carto-positron")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Données de coordonnées non disponibles pour la carte")
    else:
        st.info("Données géographiques non disponibles")

with tabs[3]:
    st.header("Analyse financière")
    
    if "price" in trips_df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution des prix
            st.subheader("Distribution des prix")
            fig = px.histogram(trips_df, x="price", nbins=20,
                               labels={"price": "Prix (€)"},
                               title="Distribution des prix des trajets")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Prix moyen par trip_distance
            st.subheader("Rapport prix/trip_distance")
            
            # Création de tranches de trip_distance
            trips_df['trip_distance_bracket'] = pd.cut(trips_df['trip_distance'], 
                                                 bins=[0, 50, 100, 200, 300, 500, 1000, 2000],
                                                 labels=['0-50', '50-100', '100-200', '200-300', '300-500', '500-1000', '1000+'])
            
            price_by_trip_distance = trips_df.groupby('trip_distance_bracket')['price'].mean().reset_index()
            fig = px.bar(price_by_trip_distance, x='trip_distance_bracket', y='price',
                        labels={"trip_distance_bracket": "Distance (km)", "price": "Prix moyen (€)"},
                        title="Prix moyen par tranche de trip_distance")
            st.plotly_chart(fig, use_container_width=True)
        
        # Évolution des prix dans le temps
        if "departure_date" in trips_df.columns:
            st.subheader("Évolution des prix dans le temps")
            trips_df['year_month'] = trips_df['departure_date'].dt.strftime('%Y-%m')
            price_by_month = trips_df.groupby('year_month')['price'].mean().reset_index()
            
            fig = px.line(price_by_month, x='year_month', y='price', markers=True,
                         labels={"year_month": "Mois", "price": "Prix moyen (€)"},
                         title="Évolution du prix moyen des trajets par mois")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Données de prix non disponibles")

with tabs[4]:
    st.header("Carte des trajets")
    
    # Options de filtrage
    st.subheader("Filtres")
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtre par trip_distance
        min_dist, max_dist = st.slider("Filtrer par trip_distance (km)", 
                                      min_value=int(trips_df['trip_distance'].min()), 
                                      max_value=int(trips_df['trip_distance'].max()), 
                                      value=(0, int(trips_df['trip_distance'].max())))
    
    with col2:
        # Nombre de trajets à afficher
        max_trips = st.number_input("Nombre maximum de trajets à afficher", min_value=1, max_value=100, value=20)
    
    # Filtrer les données
    filtered_trips = trips_df[(trips_df['trip_distance'] >= min_dist) & (trips_df['trip_distance'] <= max_dist)]
    
    # Afficher des statistiques sur les trajets filtrés
    st.write(f"Nombre de trajets correspondants: {len(filtered_trips)}")
    
    # Si trop de trajets, prendre un échantillon aléatoire
    if len(filtered_trips) > max_trips:
        sampled_trips = filtered_trips.sample(max_trips)
        st.write(f"Affichage aléatoire de {max_trips} trajets")
    else:
        sampled_trips = filtered_trips
    
    # Afficher la carte
    if not sampled_trips.empty:
        st.subheader("Carte des trajets")
        trip_map = TripMap()
        trip_map.display_multiple_trips_map(sampled_trips, height=600, width=800)
    else:
        st.info("Aucun trajet ne correspond aux critères sélectionnés")