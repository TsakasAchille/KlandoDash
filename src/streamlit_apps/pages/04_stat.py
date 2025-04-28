import streamlit as st
import os
from src.streamlit_apps.components.password_protect import protect
protect()

import sys
import os
import streamlit as st
import pandas as pd

# Ajouter le dossier src au PYTHONPATH pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.streamlit_apps.components import setup_page, set_page_background
from src.streamlit_apps.pages.components.stats import (
    display_general_stats,
    display_temporal_stats,
    display_geographic_stats,
    display_financial_stats,
    display_map_stats
)
from src.data_processing.processors.trip_processor import TripProcessor

# Fonctions d'accès aux données statistiques (analogue à get_trip_data, get_user_data)
def get_stats_data():
    """Charge les données des trajets pour les statistiques (caché pour performance)"""
    return TripProcessor.get_all_trips()

# Initialisation de la page
setup_page()
set_page_background()

# Titre principal
st.title("Statistiques des Trajets")

# Chargement des données statistiques
trips_df = get_stats_data()

# Gestion d'erreur si aucune donnée
if trips_df is None or trips_df.empty:
    st.error("Aucun trajet trouvé")
    st.stop()

# Stockage dans session_state pour cohérence
st.session_state["trips_df"] = trips_df

# Affichage principal via onglets, logique directe comme trips/users
tabs = st.tabs([
    "Vue générale",
    "Analyse temporelle",
    "Analyse géographique",
    "Analyse financière",
    "Carte des trajets"
])

with tabs[0]:
    display_general_stats(trips_df)
with tabs[1]:
    display_temporal_stats(trips_df)
with tabs[2]:
    display_geographic_stats(trips_df)
with tabs[3]:
    display_financial_stats(trips_df)
with tabs[4]:
    display_map_stats(trips_df)
