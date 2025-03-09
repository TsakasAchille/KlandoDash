from src.streamlit_apps.components.table import Table
from .table_selection import TableSelection
from .styles import Styles
from .cards import Cards
import os
import streamlit as st


# Importez ici les autres composants
__all__ = [
    "Table",
    "Styles",
    "TableSelection",
    "Cards"
]


def display_sidebar_logo():
    """Affiche le logo Klando dans la sidebar"""
    # Ajouter le logo dans la sidebar
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src/ressources/icons/logo-transparent.svg"))
    
    # Vérifier si le fichier logo existe
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=200)
    else:
        # Méthode alternative - utiliser le logo depuis le site web
        st.sidebar.image("https://klando.fr/wp-content/uploads/2023/11/Logo-Klando-site.png", width=180)


# Fonction de configuration commune pour toutes les pages
def setup_page():
    """Configure la page avec les paramètres standards et ajoute le logo"""
    # Cette fonction doit être appelée au début de chaque page
    st.set_page_config(
        page_title="KlandoDash",
        page_icon="ud83dude97",
        layout="wide"
    )
    
    # Afficher le logo après avoir configuré la page
    display_sidebar_logo()

def set_page_background():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #121212;  /* Couleur de fond principal */
        }
        .css-18e3th9 {
            background-color: #121212;  /* Sidebar et éléments principaux */
        }
        """,
        unsafe_allow_html=True
    )