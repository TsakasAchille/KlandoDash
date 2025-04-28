import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))  # IMPORTANT: doit être en premier!

import streamlit as st
from src.streamlit_apps.components.password_protect import protect
protect()

# Importer la fonction de configuration de page
from src.streamlit_apps.components import setup_page
from src.data_processing.processors.user_processor import UserProcessor
from src.data_processing.processors.trip_processor import TripProcessor
from src.streamlit_apps.pages.components.stats.stats_financial import StatsFinancialManager

# Configurer la page et afficher le logo (doit être appelée en premier)
setup_page()

st.title("Tableau de bord KlandoDash")
st.markdown("""
    Bienvenue sur le tableau de bord Klando. Utilisez la navigation pour explorer les données.
""")

# Chargement des données principales
users_df = UserProcessor.get_all_users()
trips_df = TripProcessor.get_all_trips()

# Bloc métriques globales
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Utilisateurs", len(users_df) if users_df is not None else "N/A")
with col2:
    st.metric("Trajets", len(trips_df) if trips_df is not None else "N/A")
with col3:
    total_km = trips_df['trip_distance'].sum() if trips_df is not None and 'trip_distance' in trips_df else "N/A"
    st.metric("Km parcourus", f"{total_km:.0f}" if isinstance(total_km, (int, float)) else total_km)
with col4:
    total_revenue = StatsFinancialManager()._calculate_total_revenue(trips_df) if trips_df is not None and not trips_df.empty and hasattr(StatsFinancialManager(), '_calculate_total_revenue') else "N/A"
    st.metric("Revenu total", f"{total_revenue:.0f} XOF" if isinstance(total_revenue, (int, float)) else total_revenue)

# Highlights - Derniers trajets
st.subheader("Derniers trajets créés")
if trips_df is not None and not trips_df.empty and 'created_at' in trips_df:
    st.dataframe(trips_df.sort_values("created_at", ascending=False).head(5)[[c for c in ["departure_name", "destination_name", "created_at"] if c in trips_df.columns]])
else:
    st.info("Aucun trajet disponible.")

# Carte des 10 derniers trajets
last_10_trips = trips_df.sort_values("created_at", ascending=False).head(10) if trips_df is not None and not trips_df.empty and 'created_at' in trips_df else pd.DataFrame()
st.subheader("Carte des 10 derniers trajets")
if last_10_trips is not None and not last_10_trips.empty:
    from src.streamlit_apps.pages.components.trip_map import TripMap
    trip_map = TripMap()
    trip_map.display_multiple_trips_map(last_10_trips, max_trips=10)
else:
    st.info("Aucun trajet disponible pour la carte.")

# Highlights - Nouveaux utilisateurs
st.subheader("Nouveaux utilisateurs")
if users_df is not None and not users_df.empty and 'created_at' in users_df:
    st.dataframe(users_df.sort_values("created_at", ascending=False).head(5)[[c for c in ["full_name", "email", "created_at"] if c in users_df.columns]])
else:
    st.info("Aucun utilisateur disponible.")

# Graphique miniature - Evolution du nombre de trajets
st.subheader("Evolution du nombre de trajets (30 derniers jours)")
if trips_df is not None and not trips_df.empty and "created_at" in trips_df:
    trips_df["created_at"] = pd.to_datetime(trips_df["created_at"])
    tz = trips_df["created_at"].dt.tz
    now = pd.Timestamp.now(tz=tz) if tz is not None else pd.Timestamp.now()
    last_30 = trips_df[trips_df["created_at"] > (now - pd.Timedelta(days=30))]
    if not last_30.empty:
        st.line_chart(last_30.groupby(last_30["created_at"].dt.date).size())
    else:
        st.info("Aucun trajet créé ces 30 derniers jours.")
else:
    st.info("Pas de données pour afficher la courbe.")