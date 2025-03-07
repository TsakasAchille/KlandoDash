import streamlit as st
import os
import sys

# Ajouter le dossier src au PYTHONPATH pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Importer la fonction de configuration de page
from src.streamlit_apps.components import setup_page

# Configurer la page et afficher le logo (doit être appelée en premier)
setup_page()

st.title("Tableau de bord Klando")
st.markdown("""
    Bienvenue sur le tableau de bord Klando. Utilisez la navigation pour explorer les données.
""")