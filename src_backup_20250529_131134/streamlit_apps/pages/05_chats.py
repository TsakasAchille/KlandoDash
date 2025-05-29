import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import streamlit as st
from src.streamlit_apps.components.password_protect import protect
protect()

from src.streamlit_apps.components import setup_page
from src.streamlit_apps.pages.components.chats import ChatManager

# Configuration de la page
setup_page()

# Titre de la page
st.title("Chat")

# Fonction principale qui sera appelée au démarrage
def display_chat_interface():
    # Instanciation de la classe ChatManager et appel de sa méthode principale
    chat_manager = ChatManager()
    chat_manager.display_chat_interface()

# Point d'entrée de l'application
if __name__ == "__main__":
    display_chat_interface()