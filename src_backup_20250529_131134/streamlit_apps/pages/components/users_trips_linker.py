"""Module pour lier les pages utilisateurs et trajets via l'ID de trajet."""

import streamlit as st
from typing import Optional

class UsersTripsLinker:
    """Classe pour partager les données de trajet sélectionné entre les pages."""
    
    @staticmethod
    def select_trip(trip_id: str) -> None:
        """Sélectionne un trajet pour qu'il soit affiché lorsque l'utilisateur va sur la page trajets
        
        Args:
            trip_id: ID du trajet à afficher
        """
        st.session_state["selected_trip_id"] = trip_id
        st.session_state["select_trip_on_load"] = True
        print(f"DEBUG: Trajet {trip_id} sélectionné pour affichage ultérieur")
    
    @staticmethod
    def should_select_trip() -> bool:
        """Vérifie si un trajet a été sélectionné pour affichage
        
        Returns:
            bool: True si un trajet doit être sélectionné, False sinon
        """
        return "select_trip_on_load" in st.session_state and st.session_state["select_trip_on_load"]
    
    @staticmethod
    def get_selected_trip_id() -> Optional[str]:
        """Récupère l'ID du trajet sélectionné
        
        Returns:
            str or None: ID du trajet sélectionné ou None
        """
        if "selected_trip_id" in st.session_state:
            return st.session_state["selected_trip_id"]
        return None
    
    @staticmethod
    def clear_trip_selection() -> None:
        """Efface la sélection de trajet pour ne pas le re-sélectionner à chaque rechargement"""
        if "select_trip_on_load" in st.session_state:
            st.session_state["select_trip_on_load"] = False
            print("DEBUG: Sélection de trajet effacée")
    
    @staticmethod
    def create_trip_info_message(trip_id: str) -> None:
        """Crée un message d'information sur la navigation vers un trajet
        
        Args:
            trip_id: ID du trajet à afficher
        """
        # Sélectionner le trajet pour qu'il soit prêt à l'affichage
        UsersTripsLinker.select_trip(trip_id)
        
        # Afficher un message explicatif
        st.info(f'''
        L'ID du trajet {trip_id} a été stocké en mémoire. 
        
        **Pour voir le trajet:** Cliquez sur "Trajets" dans le menu de navigation à gauche.
        ''')
    
    # Méthodes pour la sélection d'utilisateurs
    
    @staticmethod
    def select_user(user_id: str) -> None:
        """Sélectionne un utilisateur pour qu'il soit affiché lorsqu'on va sur la page utilisateurs
        
        Args:
            user_id: ID de l'utilisateur à afficher
        """
        st.session_state["selected_user_id"] = user_id
        st.session_state["select_user_on_load"] = True
        print(f"DEBUG: Utilisateur {user_id} sélectionné pour affichage ultérieur")
    
    @staticmethod
    def should_select_user() -> bool:
        """Vérifie si un utilisateur a été sélectionné pour affichage
        
        Returns:
            bool: True si un utilisateur doit être sélectionné, False sinon
        """
        return "select_user_on_load" in st.session_state and st.session_state["select_user_on_load"]
    
    @staticmethod
    def get_selected_user_id() -> Optional[str]:
        """Récupère l'ID de l'utilisateur sélectionné
        
        Returns:
            str or None: ID de l'utilisateur sélectionné ou None
        """
        if "selected_user_id" in st.session_state:
            return st.session_state["selected_user_id"]
        return None
    
    @staticmethod
    def clear_user_selection() -> None:
        """Efface la sélection d'utilisateur pour ne pas la re-sélectionner à chaque rechargement"""
        if "select_user_on_load" in st.session_state:
            st.session_state["select_user_on_load"] = False
            print("DEBUG: Sélection d'utilisateur effacée")
    
    @staticmethod
    def clear_selection() -> None:
        """Efface toutes les sélections (utilisateur et trajet)"""
        UsersTripsLinker.clear_user_selection()
        UsersTripsLinker.clear_trip_selection()
        print("DEBUG: Toutes les sélections ont été effacées")
    
    @staticmethod
    def create_user_info_message(user_id: str) -> None:
        """Crée un message d'information sur la navigation vers un utilisateur
        
        Args:
            user_id: ID de l'utilisateur à afficher
        """
        # Sélectionner l'utilisateur pour qu'il soit prêt à l'affichage
        UsersTripsLinker.select_user(user_id)
        
        # Afficher un message explicatif
        st.info(f'''
        L'ID de l'utilisateur {user_id} a été stocké en mémoire. 
        
        **Pour voir l'utilisateur:** Cliquez sur "Users" dans le menu de navigation à gauche.
        ''')
    
    @staticmethod
    def create_user_link(user_id: str, display_text: Optional[str] = None) -> str:
        """Crée un lien HTML vers la page d'un utilisateur
        
        Args:
            user_id (str): ID de l'utilisateur à afficher
            display_text (Optional[str]): Texte d'affichage pour le lien (défaut: user_id)
            
        Returns:
            str: HTML du lien cliquable ou simplement le texte
        """
        # Utiliser l'ID comme texte par défaut si non fourni
        display_text = display_text or user_id
        
        # Retourner simplement un texte forté pour l'ID utilisateur
        # Cette approche est plus simple et plus fiable que les tentatives de JS
        return f'<strong>{display_text}</strong> (Pour voir l\'utilisateur, allez dans le menu "Users")'