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
        """Crée un lien HTML cliquable vers la page de trajet
        
        Args:
            trip_id: ID du trajet
            
        Returns:
            HTML du lien cliquable
        """
        # Adapter cette fonction pour rediriger vers la page des trajets une fois qu'elle sera disponible
        return f"<a href='#' onclick=\"window.open('/01_trips', '_self'); return false;\">{trip_id} (voir trajet)</a>"
    
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
                user_id = user_df['user_id'].iloc[row] if 'user_id' in user_df.columns else 'Non disponible'
                print(f"user_id {user_id}")
                
                # Déboguer le format des IDs
                print(f"Format de l'ID utilisateur: {user_id}, type: {type(user_id)}")
                
                # Extraire les autres champs avec la même approche
                display_name = user_df['display_name'].iloc[row] if 'display_name' in user_df.columns else 'Non disponible'
                email = user_df['email'].iloc[row] if 'email' in user_df.columns else 'Non disponible'
                phone = user_df['phone_number'].iloc[row] if 'phone_number' in user_df.columns else 'Non disponible'
                birth_date = user_df['birth'].iloc[row] if 'birth' in user_df.columns else None
                created_at = user_df['created_time'].iloc[row] if 'created_time' in user_df.columns else None
                updated_at = user_df['updated_at'].iloc[row] if 'updated_at' in user_df.columns else None
                
                # Calculer l'âge à partir de la date de naissance
                age = user_df['age'].iloc[row] if 'age' in user_df.columns else self.calculate_age(birth_date)
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
                user_series = user_df.iloc[0]
                user_id = user_df['user_id'].iloc[row] if 'user_id' in user_df.columns else 'Non disponible'
                print(f"user_id {user_id}")
                

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
                    
                    # Créer un contenu HTML pour l'historique des trajets
                    trips_content = ""
                    for _, trip in recent_trips.iterrows():
                        trip_id = trip.get("trip_id", "")
                        departure_date = self.format_date(trip.get("departure_date", ""))
                        origin = trip.get("departure_name", "")
                        destination = trip.get("destination_name", "")
                        role = trip.get("user_role", "Passager")
                        
                        # Créer une ligne avec un lien cliquable vers le trajet
                        trip_link = self.create_trip_link(trip_id)
                        role_icon = "&#128663;" if role == "Conducteur" else "&#128100;"
                        trips_content += f"<div class='detail-row'><span class='label'>{departure_date}:</span> {origin} &rarr; {destination} ({role_icon} {role}) {trip_link}</div>"
                    
                    st.markdown(self.create_user_info_card(
                        "Derniers trajets",
                        trips_content,
                        icon="&#128665;"
                    ), unsafe_allow_html=True)
                    
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