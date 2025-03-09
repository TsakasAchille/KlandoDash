import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
from src.streamlit_apps.components.cards import Cards
import datetime
from typing import Dict, Any, Optional, List, Union
from src.data_processing.processors.trip_processor import TripProcessor

class UsersDisplay:
    """
    Classe pour afficher les détails d'un utilisateur dans la page 02_users.py.
    """
    
    def __init__(self):
        """Initialise l'affichage des utilisateurs"""
        # Importer Cards pour le style des cartes
        self.cards = Cards()
        # S'assurer que les styles CSS sont chargés
        self.load_user_styles()
        self.trip_processor = TripProcessor()
    
    def load_user_styles(self):
        """Charge les styles CSS pour les cartes d'information des utilisateurs"""
        # Utiliser la méthode statique de Cards pour charger les styles
        Cards.load_card_styles()
        
        # Charger également le CSS spécifique aux utilisateurs si existant
        users_css_path = os.path.join('assets', 'css', 'users.css')
        if os.path.exists(users_css_path):
            with open(users_css_path, 'r') as f:
                css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    def create_user_info_card(self, title: str, content: str, icon: str = "U", card_class: str = "") -> str:
        """Crée une carte d'information utilisateur stylée
        
        Args:
            title: Titre de la carte
            content: Contenu HTML de la carte
            icon: Icône à afficher (lettre ou texte simple)
            card_class: Classe CSS additionnelle
        
        Returns:
            HTML formaté pour la carte d'information
        """
        return f"""
        <div class="info-card {card_class}">
            <div class="info-title">
                <span class="icon">{icon}</span> {title}
            </div>
            <div class="info-content">
                {content}
            </div>
        </div>
        """
    
    def format_detail(self, label: str, value: Any, is_value: bool = True) -> str:
        """Formate une ligne de détail pour les cartes d'information
        
        Args:
            label: Label du détail
            value: Valeur du détail
            is_value: Si True, applique les styles de valeur
            
        Returns:
            HTML formaté pour la ligne de détail
        """
        value_class = 'value' if is_value else ''
        return f"<div class='detail-row'><span class='label'>{label}:</span> <span class='{value_class}'>{value}</span></div>"
    
    def create_trip_link(self, trip_id: str) -> str:
        """
        Crée un lien HTML cliquable vers la page de trajet
        
        Args:
            trip_id: ID du trajet
            
        Returns:
            HTML du lien cliquable ou chaîne vide si utilisation du bouton
        """
        from src.streamlit_apps.pages.components.users_trips_linker import UsersTripsLinker
        
        # Créer un bouton plus fiable qu'un lien HTML
        button_key = f"goto_trip_{trip_id}_{id(trip_id)}"
        if st.button(f"Voir trajet {trip_id}", key=button_key):
            print(f"DEBUG: Bouton cliqué pour trajet {trip_id}")
            
            # Utiliser la méthode de navigation améliorée
            UsersTripsLinker.navigate_to_trip(trip_id)
            
            # Message de confirmation
            st.success(f"Navigation vers le trajet {trip_id}...")
            
            # Lien de secours direct
            st.markdown(f"Si la redirection automatique ne fonctionne pas, [cliquez ici](/01_trips?trip_id={trip_id})")
        
        # Retourner une chaîne vide car l'action est gérée par le bouton
        return ""
    
    def calculate_age(self, birth_date: Optional[str]) -> Optional[int]:
        """Calcule l'âge à partir de la date de naissance
        
        Args:
            birth_date: Date de naissance au format 'YYYY-MM-DD'
            
        Returns:
            Âge calculé ou None si la date est invalide
        """
        if not birth_date:
            return None
        
        try:
            # Convertir la date de naissance en objet datetime
            if isinstance(birth_date, str):
                birth = datetime.datetime.strptime(birth_date.split('T')[0], "%Y-%m-%d").date()
            else:
                birth = birth_date.date() if hasattr(birth_date, 'date') else birth_date
            
            # Calculer l'âge
            today = datetime.date.today()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, today.day))
            return age
        except (ValueError, TypeError, AttributeError):
            return None
    
    def format_date(self, date_str: Optional[str]) -> str:
        """Formate une date pour l'affichage
        
        Args:
            date_str: Date au format 'YYYY-MM-DDThh:mm:ss.sssZ'
            
        Returns:
            Date formatée en 'DD/MM/YYYY' ou texte original si invalide
        """
        if not date_str:
            return "Non disponible"
        
        try:
            if isinstance(date_str, str):
                date_obj = datetime.datetime.strptime(date_str.split('T')[0], "%Y-%m-%d")
                return date_obj.strftime("%d/%m/%Y")
            else:
                # Si c'est déjà un objet datetime
                return date_str.strftime("%d/%m/%Y") if hasattr(date_str, 'strftime') else str(date_str)
        except (ValueError, TypeError):
            return str(date_str) if date_str else "Non disponible"
    
    def display_user_info(self, user_df: pd.DataFrame) -> None:
        """Affiche les informations détaillées sur un utilisateur
        
        Args:
            user_df: DataFrame contenant les informations de l'utilisateur
        """
        try:
            # Extraire les informations directement à partir du DataFrame
            if len(user_df) > 0:
                # Utilisation directe des méthodes du DataFrame pour extraire les valeurs
                row = 0  # Index de la première ligne
                
                user_id = user_df['user_id'].iloc[0]

                print(f"Contenu du DataFrame user_df: {user_df}")

                
                # Déboguer le format des IDs
                print(f"Format de l'ID utilisateur: {user_id}, type: {type(user_id)}")
                
                # Extraire les autres champs avec la même approche
                display_name = user_df['display_name'].iloc[0] if not user_df['display_name'].empty else "Non disponible"
                email = user_df['email'].iloc[0] if not user_df['email'].empty else "Non disponible"
                phone = user_df['phone_number'].iloc[0] if not user_df['phone_number'].empty else "Non disponible"
                birth_date = user_df['birth'].iloc[0] if not user_df['birth'].empty else "Non disponible"
                created_at = user_df['created_time'].iloc[0] if not user_df['created_time'].empty else "Non disponible"
                updated_at = user_df['updated_at'].iloc[0] if not user_df['updated_at'].empty else "Non disponible"

                print(f"Contenu du DataFrame birth_date: {birth_date}")
                print(f"Contenu du DataFrame created_at: {created_at}")
                print(f"Contenu du DataFrame updated_at: {updated_at}")
                
                # Calculer l'âge à partir de la date de naissance
                age = user_df['age'].iloc[0] if not user_df['age'].empty else "Non disponible"
                #age_display = f"{age} ans" if age else "Non disponible"
                # If age is a Series with a single value
                age_display = f"{age} ans" if age else "Non disponible"
                # Formater les dates pour l'affichage
                birth_formatted = self.format_date(birth_date) if birth_date else "Non disponible"
                created_formatted = self.format_date(created_at) if created_at else "Non disponible"
                updated_formatted = self.format_date(updated_at) if updated_at else "Non disponible"
                
                # Créer le contenu pour la carte d'information en utilisant format_detail
                content = ""
                content += self.format_detail("ID", user_id)
                content += self.format_detail("Nom", display_name)
                content += self.format_detail("Email", email)
                content += self.format_detail("Téléphone", phone)
                content += self.format_detail("Âge", age_display)
                content += self.format_detail("Date de naissance", birth_formatted)
                content += self.format_detail("Date de création", created_formatted) 
                content += self.format_detail("Dernière mise à jour", updated_formatted)
                
                # Afficher le tout dans une seule carte
                st.markdown(self.create_user_info_card(
                    "Informations utilisateur",
                    content,
                    icon="I"
                ), unsafe_allow_html=True)
                
            else:
                st.error("Aucune donnée utilisateur disponible")
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations de l'utilisateur: {str(e)}")
            import traceback
            st.write(traceback.format_exc())
        

    def user_display_handler(self, user_df: Optional[pd.DataFrame] = None) -> None:
        """Affiche les informations détaillées sur un utilisateur
        
        Args:
            user_df: DataFrame contenant les informations de l'utilisateur
        """
        if user_df is not None and not user_df.empty:
            # Afficher les informations de base sur l'utilisateur
            self.display_user_info(user_df)
            
            # Afficher les informations sur les trajets de l'utilisateur
            self.display_user_trip_infos(user_df)
        else:
            st.error("Aucune donnée utilisateur disponible")









    def display_user_trip_infos(self, user_df: pd.DataFrame, trips_df: Optional[pd.DataFrame] = None):
        """Affiche les informations de trajets d'un utilisateur
        
        Args:
            user_df: DataFrame contenant les informations de l'utilisateur
            trips_df: DataFrame des trajets déjà chargé, optionnel
        """
        try:
            # Extraire l'ID utilisateur à partir du DataFrame
            if len(user_df) > 0:
                row = 0

                user_id = user_df['user_id'].iloc[0]
                print(f"Traitement des trajets pour l'utilisateur: {user_id}")
                        


                user_trips_df = self.trip_processor.get_user_trips(user_id, trips_df)
                
                # Statistiques de l'utilisateur basées sur les trajets réels
                st.subheader("Statistiques")
                
                # Calculer les statistiques si des trajets existent
                nb_trips = 0
                total_distance = 0
                total_co2 = 0
                
                if user_trips_df is not None and not user_trips_df.empty:
                    nb_trips = len(user_trips_df)
                    # Calculer la distance totale si disponible
                    if 'trip_distance' in user_trips_df.columns:
                        total_distance = user_trips_df['trip_distance'].sum()
                    # Estimer l'économie de CO2 (exemple: 150g par km)
                    total_co2 = total_distance * 0.15  # 150g/km converti en kg
                    
                # Afficher les métriques
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Trajets effectués", str(nb_trips))
                with cols[1]:
                    st.metric("Kilomètres parcourus", f"{total_distance:.1f} km")
                with cols[2]:
                    st.metric("Économie de CO2", f"{total_co2:.1f} kg")
                    
                # Historique des trajets
                st.subheader("Historique des trajets")
                
                if user_trips_df is not None and not user_trips_df.empty:
                    # Limiter aux 5 derniers trajets pour l'affichage
                    recent_trips = user_trips_df.head(5)
                    
                    st.markdown("🚙 **Derniers trajets**")
                    
                    # Pour chaque trajet, afficher les informations et un bouton pour y accéder
                    for _, trip in recent_trips.iterrows():
                        trip_id = trip.get("trip_id", "")
                        departure_date = self.format_date(trip.get("departure_date", ""))
                        origin = trip.get("departure_name", "None")
                        destination = trip.get("destination_name", "None")
                        role = trip.get("user_role", "Passager")
                        
                        # Icône en fonction du rôle
                        role_icon = "👤" if role == "Passager" else "🚗"
                        
                        # Créer un conteneur pour chaque trajet
                        with st.container():
                            cols = st.columns([3, 1])
                            with cols[0]:
                                st.markdown(f"{departure_date}: {origin} → {destination} ({role_icon} {role})")
                            with cols[1]:
                                # Stocker l'ID dans la session avant de naviguer
                                if st.button(f"Voir trajet", key=f"goto_{trip_id}"):
                                    # Stocker le trip_id dans la session
                                    st.session_state["selected_trip_id"] = trip_id
                                    st.session_state["select_trip_on_load"] = True
                                    
                                    # Utiliser le menu principal de navigation
                                    st.info(f"Veuillez cliquer sur le menu 'Trajets' dans la barre latérale pour voir le trajet {trip_id}.")
                    
                    # Afficher aussi un tableau complet des trajets si nombreux
                    if len(user_trips_df) > 5:
                        with st.expander(f"Voir tous les trajets ({len(user_trips_df)} au total)"):
                            # Sélectionner et renommer les colonnes pertinentes
                            display_cols = [
                                'trip_id', 'departure_date', 'departure_name', 'destination_name',
                                'trip_distance', 'price_per_seat', 'user_role'
                            ]
                            cols_to_show = [col for col in display_cols if col in user_trips_df.columns]
                            
                            # Renommer les colonnes pour l'affichage
                            rename_dict = {
                                'trip_id': 'ID du trajet',
                                'departure_date': 'Date de départ', 
                                'departure_name': 'Origine',
                                'destination_name': 'Destination',
                                'trip_distance': 'Distance (km)',
                                'price_per_seat': 'Prix par siège',
                                'user_role': 'Rôle'
                            }
                            
                            # Afficher le tableau avec les colonnes renommées
                            st.dataframe(user_trips_df[cols_to_show].rename(columns=rename_dict))
                else:
                    st.info("Aucun trajet trouvé pour cet utilisateur.")
            


        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations de l'utilisateur: {str(e)}")
            import traceback
            st.write(traceback.format_exc())