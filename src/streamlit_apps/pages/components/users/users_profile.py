import streamlit as st
import pandas as pd
from datetime import datetime
from src.streamlit_apps.components.modern_card import modern_card

class UsersProfileManager:
    """Gère l'affichage des informations de profil des utilisateurs"""
    
    def display_profile_info(self, user_data):
        """Affiche les informations de profil de l'utilisateur
        
        Args:
            user_data: Données de l'utilisateur à afficher
        """
        try:
            # Extraire les informations de base de l'utilisateur
            user_id = user_data.get('id', 'Non disponible')
            first_name = user_data.get('first_name', 'Non disponible')
            display_name = user_data.get('display_name', 'Non disponible')
            name = user_data.get('name', 'Non disponible')
            email = user_data.get('email', 'Non disponible')
            phone = user_data.get('phone_number', 'Non disponible')
            uid = user_data.get('uid', 'Non disponible')
            phone_verified = user_data.get('phone_verified', None)
            photo_url = user_data.get('photo_url', None)
            
            # Formater le nom complet - utiliser la meilleure information disponible
            if name != 'Non disponible':
                full_name = name
            elif display_name != 'Non disponible':
                full_name = display_name
            elif first_name != 'Non disponible':
                full_name = first_name
            else:
                full_name = "Non disponible"
            
            # Formater le statut de vérification du téléphone
            phone_status = "✅ Vérifié" if phone_verified else "❌ Non vérifié" if phone_verified is not None else "Non disponible"
            
            # Créer une mise en page à deux colonnes pour la photo et les informations
            cols = st.columns([3, 1]) if photo_url else [st.container()]
            
            with cols[0]:
                # Préparer les informations de profil
                profile_items = [
                    ("Nom", full_name),
                    ("Prénom", first_name),
                    ("Email", email),
                    ("Téléphone", phone)
                ]
                
                # Ajouter le statut de vérification du téléphone si disponible
                if phone_verified is not None and phone != 'Non disponible':
                    profile_items.append(("Statut téléphone", phone_status))
                    
                # Ajouter l'ID utilisateur
                profile_items.append(("ID", user_id))
                profile_items.append(("UID", uid))
                
                # Afficher les informations de profil avec modern_card
                modern_card(
                    title="Profil Utilisateur",
                    icon="👤",  # Emoji personne
                    items=profile_items,
                    accent_color="#3498db"  # Bleu pour le profil
                )
            
            # Afficher la photo de profil dans la colonne de droite si disponible
            if photo_url and len(cols) > 1:
                with cols[1]:
                    st.image(photo_url, width=150, caption="Photo de profil")
            
            # Afficher des informations supplémentaires si disponibles
            self._display_additional_info(user_data)
            
        except Exception as e:
            st.error(f"Erreur lors de l'affichage du profil: {str(e)}")
    
    def _display_additional_info(self, user_data):
        """Affiche des informations supplémentaires sur l'utilisateur si disponibles
        
        Args:
            user_data: Données de l'utilisateur à afficher
        """
        # Vérifier si des informations supplémentaires sont disponibles
        additional_fields = [
            ('short_description', 'Description'),
            ('address', 'Adresse'),
            ('city', 'Ville'),
            ('country', 'Pays'),
            ('birth', 'Date de naissance'),
            ('created_at', 'Compte créé le')
            # Nous ne montrons plus photo_url ici car il est affiché à côté du profil
        ]
        
        # Collecter les informations disponibles
        available_info = []
        for field, label in additional_fields:
            if field in user_data and user_data[field]:
                value = user_data[field]
                
                # Formater les dates
                if field in ['birth', 'created_at']:
                    try:
                        # Gérer différents formats de date
                        if isinstance(value, (datetime, pd.Timestamp)):
                            value = value.strftime("%d/%m/%Y")
                        elif isinstance(value, str):
                            # Gérer les formats ISO et PostgreSQL
                            if 'T' in value:
                                # Format ISO
                                date_part = value.split('T')[0]
                                date_obj = datetime.strptime(date_part, "%Y-%m-%d")
                                value = date_obj.strftime("%d/%m/%Y")
                            elif ' ' in value:
                                # Format PostgreSQL timestamp
                                date_part = value.split(' ')[0]
                                date_obj = datetime.strptime(date_part, "%Y-%m-%d")
                                value = date_obj.strftime("%d/%m/%Y")
                            else:
                                # Format simple date
                                date_obj = datetime.strptime(value, "%Y-%m-%d")
                                value = date_obj.strftime("%d/%m/%Y")
                    except Exception as e:
                        # En cas d'erreur, garder la valeur originale
                        st.warning(f"Erreur de formatage de date pour {field}: {str(e)}")
                
                # Ajouter à la liste des informations disponibles
                available_info.append((label, value))
        
        # Afficher les informations supplémentaires si disponibles
        if available_info:
            modern_card(
                title="Informations Complémentaires",
                icon="📃",  # Emoji document
                items=available_info,
                accent_color="#3498db"  # Bleu pour le profil
            )
