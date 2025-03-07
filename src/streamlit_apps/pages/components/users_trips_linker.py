import streamlit as st
import pandas as pd
from typing import Optional

class UsersTripsLinker:
    """
    Classe pour gérer la navigation entre les pages, notamment pour sélectionner
    un utilisateur sur la page des utilisateurs à partir d'une autre page.
    """
    
    @staticmethod
    def save_selected_user(user_id: str) -> None:
        """
        Sauvegarde l'ID de l'utilisateur à sélectionner dans la session Streamlit
        
        Args:
            user_id (str): ID de l'utilisateur à sélectionner
        """
        st.session_state["selected_user_id"] = user_id
        # Définir un flag pour indiquer que nous venons de faire une sélection
        st.session_state["select_user_on_load"] = True
    
    @staticmethod
    def get_selected_user_id() -> Optional[str]:
        """
        Récupère l'ID de l'utilisateur à sélectionner depuis la session
        
        Returns:
            Optional[str]: ID de l'utilisateur ou None
        """
        return st.session_state.get("selected_user_id")
    
    @staticmethod
    def should_select_user() -> bool:
        """
        Vérifie si un utilisateur doit être sélectionné automatiquement
        
        Returns:
            bool: True si un utilisateur doit être sélectionné, False sinon
        """
        return st.session_state.get("select_user_on_load", False)
    
    @staticmethod
    def clear_selection() -> None:
        """
        Efface la sélection d'utilisateur après qu'elle a été utilisée
        """
        if "select_user_on_load" in st.session_state:
            del st.session_state["select_user_on_load"]
    
    @staticmethod
    def create_user_link(user_id: str, display_text: Optional[str] = None) -> str:
        """
        Crée un lien cliquable vers la page utilisateur avec l'utilisateur présélectionné
        
        Args:
            user_id (str): ID de l'utilisateur à sélectionner
            display_text (Optional[str]): Texte à afficher pour le lien (défaut: user_id)
            
        Returns:
            str: HTML du lien cliquable
        """
        display_text = display_text or user_id
        
        # Quand l'utilisateur clique sur ce lien, il est dirigé vers la page 02_users.py
        # et l'identifiant de l'utilisateur est stocké dans la session
        return f"""
        <a href="#" onclick="
            window.parent.postMessage({{
                'type': 'streamlit:setSessionState',
                'session_state': {{ 'selected_user_id': '{user_id}', 'select_user_on_load': true }}
            }}, '*');
            window.open('/02_users', '_self');
            return false;
        ">{display_text}</a>
        """
    
    @staticmethod
    def display_user_link(user_id: str, display_text: Optional[str] = None) -> None:
        """
        Affiche un lien cliquable vers la page utilisateur avec l'utilisateur présélectionné
        
        Args:
            user_id (str): ID de l'utilisateur à sélectionner
            display_text (Optional[str]): Texte à afficher pour le lien (défaut: user_id)
        """
        link_html = UserNavigation.create_user_link(user_id, display_text)
        st.markdown(link_html, unsafe_allow_html=True)