import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime

# Ajouter le dossier src au PYTHONPATH pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))) 


from datetime import datetime

# Common components

#Trip components
from src.data_processing.processors.trip_processor import TripProcessor
from src.streamlit_apps.pages.components.trip_map import TripMap

#Common components
from src.streamlit_apps.components import Table, Styles, setup_page
from streamlit_folium import st_folium
try:
    import streamlit_aggrid as st_aggrid
    from streamlit_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode, JsCode
    AGGRID_AVAILABLE = True
except ImportError:
    AGGRID_AVAILABLE = False

import sys
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd
from src.streamlit_apps.components import Cards  # Importez la nouvelle classe Cards
from datetime import datetime
import locale
# Configurer la page et afficher le logo (doit être appelé en premier)


class TripsApp:


    """Application principale pour l'affichage des trajets"""


    def __init__(self):
        """Initialisation de l'application"""
        self.trip_processor = TripProcessor()
        self.trip_map = TripMap()
        Cards.load_card_styles()
        
                
    def load_style(self):
        """Charge les styles CSS personnalisés"""
        try:
            # Chemin vers le fichier CSS - Corrigé pour pointer vers le bon répertoire
            css_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "style.css")
            
            # Vérifier si le fichier existe
            if os.path.exists(css_path):
                with open(css_path, "r") as f:
                    css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
            else:
                st.warning(f"Le fichier CSS n'a pas été trouvé : {css_path}")
        except Exception as e:
            st.error(f"Erreur lors du chargement du CSS : {str(e)}")
            # Fallback au CSS intégré en cas d'erreur
            st.markdown("""
            <style>
                /* CSS de secours en cas d'erreur */
                .main .block-container {
                    max-width: 100% !important;
                    width: 100% !important;
                }
            </style>
            """, unsafe_allow_html=True)



    def display_trips_table(self, trips_df):
        """Affiche le tableau des trajets et gère la sélection
        
        Args:
            trips_df: DataFrame contenant les données des trajets
            
        Returns:
            bool: True si un trajet est sélectionné, False sinon
        """
            
        # Colonnes à afficher
        display_cols = [
            'trip_id',
            'trip_distance',
            'passengers',  # Utiliser la colonne prétraitée
            'departure_schedule'
        ]

   
        # Filtrer les colonnes existantes
        valid_cols = [col for col in display_cols if col in trips_df.columns]

        # Créer une copie du DataFrame avec seulement les colonnes nécessaires

        # Renommer les colonnes
            
        # Configuration de la grille avec case à cocher
        gb = GridOptionsBuilder.from_dataframe(trips_df[valid_cols])
        gb.configure_selection('single', use_checkbox=True)
        gb.configure_grid_options(suppressRowClickSelection=True)

        # CSS personnalisé pour la couleur et la taille du tableau
        custom_css = {
            ".ag-header": {
                "background-color": "#081C36 !important",
                "color": "white !important",
                "font-size": "14px !important"  # Taille de police pour les entêtes
            },
            ".ag-row-selected": {
                "background-color": "#7b1f2f !important",
                "color": "white !important"
            },
            ".ag-cell": {
                "font-size": "14px !important"  # Taille de police pour les cellules
            },
            ".ag-header-cell-label": {
                "font-weight": "bold !important"
            }
        }

        # Afficher la grille
        self.grid_response = AgGrid(
            trips_df[valid_cols],
            gridOptions=gb.build(),
            fit_columns_on_grid_load=False,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            height=650,
            custom_css=custom_css
        )



        # Stocker les données sélectionnées dans la session state
        self.selected_df = self.grid_response["selected_rows"]
        
        return self.selected_df
       
    
    def get_data(self):
        return self.trip_processor.handler()



    def display_distance_info(self,selected_trip):
        """
        Affiche les informations du trajet de manière élégante avec des cartes stylisées
        """
    
        if selected_trip is not None and 'trip_id' in selected_trip:            
            try:


                trip_distance = selected_trip['trip_distance'] if 'trip_distance' in selected_trip else 0

                        
                # Estimer l'économie de CO2 (exemple: 150g par km)            
              
                st.metric("Kilomètres parcourus", f"{trip_distance:.1f} km")
            
                
            except Exception as e:
                st.error(f"Erreur lors de l'affichage des informations du trajet: {str(e)}")


    def display_fuel_info(self,selected_trip):
        """
        Affiche les informations du trajet de manière élégante avec des cartes stylisées
        """
        
        if selected_trip is not None and 'trip_id' in selected_trip:            
            try:
                trip_distance = selected_trip['trip_distance'] if 'trip_distance' in selected_trip else 0
                
                # Estimer l'économie de carburant (exemple: 10L par km)
                total_fuel = trip_distance * 0.10  # 10L/km
                
                st.metric("Économie de carburant", f"{total_fuel:.1f} L")
                
            except Exception as e:
                st.error(f"Erreur lors de l'affichage des informations du trajet: {str(e)}")

    def display_CO2_info(self,selected_trip):
        """
        Affiche les informations du trajet de manière élégante avec des cartes stylisées
        """
        
        if selected_trip is not None and 'trip_id' in selected_trip:            
            try:
                trip_distance = selected_trip['trip_distance'] if 'trip_distance' in selected_trip else 0
                
                # Estimer l'économie de CO2 (exemple: 150g par km)
                total_co2 = trip_distance * 0.15  # 150g/km converti en kg
                
                st.metric("Économie de CO2", f"{total_co2:.1f} kg")
                
            except Exception as e:
                st.error(f"Erreur lors de l'affichage des informations du trajet: {str(e)}")

  
   

    def display_route_info(self, trip_data):
        """
        Affiche la carte d'itinéraire incluant départ, destination et distance
        """
        if 'departure_name' in trip_data and 'destination_name' in trip_data:
            try:
                # Accéder directement aux valeurs car trip_data est une série
                departure = trip_data['departure_name'] if trip_data['departure_name'] else "Non disponible"
                destination = trip_data['destination_name'] if trip_data['destination_name'] else "Non disponible"
                
                # Création des paires label/value pour la carte
                content_items = [
                    ("Départ", departure),
                    ("Destination", destination)
                ]
                
                # Création d'une liste avec un seul élément pour create_info_cards
                info_data = [("Itinéraire", content_items, "📍")]
                
                # Créer la carte avec la nouvelle fonction
                route_card = Cards.create_info_cards(info_data, label_size="9px", value_size="14px", max_height="180px")
                st.markdown(route_card, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Erreur lors de l'affichage de l'itinéraire: {str(e)}")

    def display_all_metrics(self, selected_trip):
        from streamlit_apps.components.cards import Cards
        
        if selected_trip is not None and 'trip_id' in selected_trip:
            trip_distance = selected_trip['trip_distance'] if 'trip_distance' in selected_trip else 0
            total_fuel = trip_distance * 0.10
            total_co2 = trip_distance * 0.15
            
            # Dans trips.py:
            metrics_data = [
                ("Kilomètres parcourus", f"{trip_distance:.1f} km"),
                ("Économie de carburant", f"{total_fuel:.1f} L"),
                ("Économie de CO2", f"{total_co2:.1f} kg")
            ]
            metrics_html = Cards.create_metric_cards(metrics_data)
            st.markdown(metrics_html, unsafe_allow_html=True)


    def display_time_metrics(self, selected_trip):
       
        
        # Tentative de définition de la locale française
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        except:
            pass  # Si la locale n'est pas disponible, continuer sans erreur
        
        if selected_trip is not None and 'trip_id' in selected_trip:
            date_str = selected_trip.get('departure_schedule')
            
            # Convertir la date ISO en format lisible
            date = "Non spécifiée"
            if date_str and date_str != 0:
                try:
                    # Gérer plusieurs formats de date possibles
                    if isinstance(date_str, str):
                        # Nettoyage du format pour compatibilité
                        clean_date_str = date_str.replace('Z', '+00:00')
                        date_obj = datetime.fromisoformat(clean_date_str)
                    elif isinstance(date_str, datetime):
                        date_obj = date_str
                    else:
                        raise ValueError(f"Format de date non reconnu: {type(date_str)}")
                    
                    # Reformater en format français
                    date = date_obj.strftime("%d %b %Y à %H:%M")
                except Exception as e:
                    st.write(f"Erreur format date: {e}")
                    date = str(date_str)
            
            # Affichage de la métrique
            metrics_data = [
                ("Date", date),
            ]
            metrics_html = Cards.create_metric_cards(metrics_data)
            st.markdown(metrics_html, unsafe_allow_html=True)



    def display_financial_info(self, trip_data):
        """
        Affiche les informations financières du trajet
        """
        try:
            content_items = []
            
            if 'price_per_seat' in trip_data:
                price = trip_data['price_per_seat'].values[0] if isinstance(trip_data['price_per_seat'], pd.Series) else trip_data['price_per_seat']
                if isinstance(price, (int, float)):
                    price_str = f"{price:.2f} XOF"
                else:
                    price_str = f"{price} XOF"
                content_items.append(("Prix/Place", price_str))
            
            # Ajouter d'autres informations financières si disponibles
            if 'viator_income' in trip_data:
                viator_income = trip_data['viator_income'].values[0] if isinstance(trip_data['viator_income'], pd.Series) else trip_data['viator_income']
                if isinstance(viator_income, (int, float)):
                    viator_income_str = f"{viator_income:.2f} XOF"
                else:
                    viator_income_str = f"{viator_income} XOF"
                content_items.append(("Viator Income", viator_income_str))
            
            if content_items:
                # Création d'une liste avec un seul élément pour create_info_cards
                info_data = [("Finances", content_items, "💵")]
                
                # Créer la carte avec la nouvelle fonction
                finance_card = Cards.create_info_cards(info_data, label_size="9px", value_size="14px",color="#EBC33F")
                st.markdown(finance_card, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations financières: {str(e)}")

    def display_map(self, trips_df, selected_trip):
       # st.subheader("Carte du trajet")
                
        if selected_trip is not None and 'trip_id' in selected_trip:
            # Récupérer l'ID du trajet sélectionné
            trip_id = selected_trip['trip_id']
            
            # Récupérer les données complètes du trajet
            trip_data = trips_df[trips_df['trip_id'] == trip_id]
            
            if not trip_data.empty:
                # Afficher la carte
                self.trip_map.display_trip_map(trip_data.iloc[0])
            else:
                st.info("Données complètes du trajet non trouvées")
        else:
            # Message d'instruction
            st.info("Sélectionnez un trajet dans le tableau pour voir sa carte")


    def display_multiple_map(self, trips_df):
       # st.subheader("Carte du trajet")
                
        # Afficher la carte
        self.trip_map.display_multiple_trips_map(trips_df)

  
        





    def display_seat_occupation_info(self, trip_data, info_cols=None):
        """
        Affiche les informations sur l'occupation des sièges
        
        Args:
            trip_data: Données du trajet sélectionné
            info_cols: Colonnes Streamlit pour l'affichage (optionnel)
        """
        try:
            # Extraire les informations nécessaires
            total_seats = int(trip_data.get('number_of_seats', 0))
            available_seats = int(trip_data.get('available_seats', 0))
            all_passengers = trip_data.get('all_passengers', '')
            
            # Traiter la variable all_passengers
            if isinstance(all_passengers, str):
                if ',' in all_passengers:
                    all_passengers = all_passengers.split(',')
                elif all_passengers.strip():
                    all_passengers = [all_passengers.strip()]
                else:
                    all_passengers = []
                    
            # Nettoyer les IDs utilisateurs
            if isinstance(all_passengers, list):
                all_passengers = [p.replace('users/', '') for p in all_passengers]
            
            # Déterminer le nombre de passagers
            passenger_count = len(all_passengers) if isinstance(all_passengers, list) else 0
            
            # Calculer les sièges occupés
            occupied_seats = passenger_count
            if occupied_seats > total_seats - available_seats:
                occupied_seats = total_seats - available_seats
            
            # Calculer le pourcentage d'occupation
            occupation_percentage = (occupied_seats / total_seats) * 100 if total_seats > 0 else 0
            
            # Préparer les items pour la carte d'information
            content_items = [
                ("Total sièges", f"{total_seats}"),
                ("Sièges occupés", f"{occupied_seats}"),
                ("Taux d'occupation", f"{occupation_percentage:.0f}%")
            ]
            
            # Déterminer l'icône et la couleur selon le taux d'occupation
            icon = "💺"  # siège
            color = "#4CAF50" if occupation_percentage > 75 else "#7B1F2F"  # vert si >75%, sinon rouge par défaut
            
            # Préparer les données pour create_info_cards
            info_data = [("Occupation des sièges", content_items, icon)]
            
            # Affichage selon les colonnes fournies
            if info_cols and len(info_cols) > 0:
                with info_cols[0]:
                    st.markdown(Cards.create_info_cards(
                        info_data,
                        color=color,
                        label_size="9px",
                        value_size="14px",
                        vertical_layout=True
                    ), unsafe_allow_html=True)
            else:
                st.markdown(Cards.create_info_cards(
                    info_data,
                    color=color,
                    label_size="9px", 
                    value_size="14px",
                    vertical_layout=True
                ), unsafe_allow_html=True)
                
            return occupied_seats, total_seats
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations d'occupation: {str(e)}")
            return 0, 0



    def display_people_info(self, trip_data, info_cols=None):
        """
        Affiche les informations sur le conducteur et les passagers
        
        Args:
            trip_data: Données du trajet sélectionné
            info_cols: Colonnes Streamlit pour l'affichage (optionnel)
        """
        try:
            from streamlit_apps.components.cards import Cards
            
            # Récupérer les données utilisateurs depuis la session state
            if "user_df" not in st.session_state:
                st.error("Données utilisateurs non disponibles")
                return
                
            users_df = st.session_state["user_df"]

            # Extraire les IDs
            driver_id = trip_data.get('driver_reference', '').replace('users/', '')
            all_passengers = trip_data.get('all_passengers', '')
            
            # Traiter la variable all_passengers
            if isinstance(all_passengers, str):
                if ',' in all_passengers:
                    all_passengers = all_passengers.split(',')
                elif all_passengers.strip():
                    all_passengers = [all_passengers.strip()]
                else:
                    all_passengers = []
                    
            # Nettoyer les IDs utilisateurs
            if isinstance(all_passengers, list):
                all_passengers = [p.replace('users/', '') for p in all_passengers]
            
            if not info_cols:
                # Créer les colonnes pour l'affichage si non fournies
                all_elements = 1 + (1 if driver_id else 0) + len(all_passengers)  # Titre + conducteur (si présent) + passagers
                info_cols = st.columns(all_elements)
            
            col_index = 0
            
            # Conducteur
            if isinstance(driver_id, str) and driver_id.strip():
                with info_cols[col_index]:
                    # Récupérer directement le nom depuis le DataFrame
                    driver_name = "Inconnu"
                    driver_row = users_df[users_df['user_id'] == driver_id]
                    if not driver_row.empty:
                        driver_name = driver_row.iloc[0].get('name', "Inconnu")
                    
                    # Préparer les données pour create_info_cards
                    driver_content = [
                        ("Nom", driver_name),
                        ("ID", driver_id)
                    ]
                    info_data = [("Conducteur", driver_content, "🧑‍✈️")]
                    
                    st.markdown(Cards.create_info_cards(
                        info_data,
                        color="#00BFA5",
                        label_size="10px",
                        value_size="13px",
                        background_color="#102844"
                    ), unsafe_allow_html=True)
                    
                    # Ajouter un bouton pour voir le profil du conducteur
                    if st.button("Voir profil", key=f"driver_profile_{driver_id}"):
                        st.session_state["selected_user_id"] = driver_id
                        st.session_state["show_user_profile"] = True
                        
                col_index += 1

            # Passagers
            if isinstance(all_passengers, list) and len(all_passengers) > 0:
                for i, passenger in enumerate(all_passengers):
                    with info_cols[col_index]:
                        passenger_content = []
                        
                        if isinstance(passenger, dict):
                            passenger_name = passenger.get('name', f'Passager {i+1}')
                            passenger_id = passenger.get('id', '')
                            passenger_content.append(("Nom", passenger_name))
                            passenger_content.append(("ID", passenger_id))
                            if 'phone' in passenger:
                                passenger_content.append(("Téléphone", passenger['phone']))
                        else:
                            passenger_id = passenger
                            # Récupérer directement le nom depuis le DataFrame
                            passenger_name = "Inconnu"
                            passenger_row = users_df[users_df['user_id'] == passenger_id]
                            if not passenger_row.empty:
                                passenger_name = passenger_row.iloc[0].get('name', "Inconnu")
                            
                            passenger_content.append(("Nom", passenger_name))
                            passenger_content.append(("ID", passenger_id))
                        
                        info_data = [(f"Passager {i+1}", passenger_content, "👥")]
                        
                        st.markdown(Cards.create_info_cards(
                            info_data,
                            color="#00BFA5",
                            label_size="10px",
                            value_size="13px",
                            background_color="#102844"
                        ), unsafe_allow_html=True)
                        
                        # Ajouter les boutons pour voir le profil et le chat du passager
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Voir profil", key=f"passenger_profile_{i}_{passenger_id}"):
                                st.session_state["selected_user_id"] = passenger_id
                                st.session_state["show_user_profile"] = True
                        
                        with col2:
                            if st.button("💬 Chat", key=f"passenger_chat_{i}_{passenger_id}"):
                                # Stocker l'ID du passager pour le chat
                                st.session_state["chat_with_passenger_id"] = passenger_id
                                st.session_state["show_chat_dialog"] = True
                                # Stocker aussi les noms pour l'affichage et l'ID du trajet
                                st.session_state["chat_passenger_name"] = passenger_name
                                st.session_state["chat_trip_id"] = trip_data.get('trip_id', '')
                        
                        # Afficher le popup de chat si demandé pour ce passager
                        if st.session_state.get("show_chat_dialog", False) and \
                           st.session_state.get("chat_with_passenger_id") == passenger_id:
                            self.display_chat_popup(passenger_id, passenger_name, trip_data.get('trip_id', ''))
                    
                    col_index += 1
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations sur les personnes: {str(e)}")

    def display_chat_popup(self, passenger_id, passenger_name, trip_id):
        """
        Affiche un dialogue de chat pour le passager sélectionné
        
        Args:
            passenger_id (str): ID du passager
            passenger_name (str): Nom du passager
            trip_id (str): ID du trajet
        """
        from src.streamlit_apps.pages.components.chats import ChatManager
        
        # Créer un grand dialogue modal pour le chat
        with st.container():
            # Ajouter un bouton pour fermer le dialogue
            st.markdown("""
            <style>
            .chat-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background-color: #102844;
                color: white;
                padding: 10px 15px;
                border-radius: 5px 5px 0 0;
            }
            .chat-dialog {
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
                background-color: white;
            }
            .chat-content {
                padding: 15px;
                max-height: 500px;
                overflow-y: auto;
            }
            </style>
            """, unsafe_allow_html=True)

            st.markdown(f'<div class="chat-dialog">', unsafe_allow_html=True)
            
            # Entête du dialogue avec le nom du passager et le bouton de fermeture
            header_cols = st.columns([3, 1])
            with header_cols[0]:
                st.markdown(f'<div class="chat-header"><h3>Chat avec {passenger_name}</h3></div>', unsafe_allow_html=True)
            with header_cols[1]:
                if st.button("Fermer", key="close_chat_dialog"):
                    # Réinitialiser les variables de session pour fermer le dialogue
                    st.session_state["show_chat_dialog"] = False
                    st.session_state["chat_with_passenger_id"] = None
                    st.rerun()
            
            # Contenu du chat
            st.markdown('<div class="chat-content">', unsafe_allow_html=True)
            
            # Utiliser le ChatManager pour récupérer et afficher les conversations
            chat_manager = ChatManager()
            
            # Charger les conversations et les filtrer pour ce passager et ce trajet
            chats_df, messages_df, _ = chat_manager.load_chat_data()
            
            if not chats_df.empty:
                # Filtrer les conversations pour ce passager
                # On cherche les conversations où le passager est soit user_a soit user_b
                filtered_chats = chats_df[(chats_df['user_a'] == passenger_id) | (chats_df['user_b'] == passenger_id)]
                
                if not filtered_chats.empty:
                    # Sélectionner la première conversation trouvée
                    selected_chat = filtered_chats.iloc[0]
                    chat_id = selected_chat['chat_id']
                    
                    # Récupérer les messages de cette conversation
                    chat_messages = messages_df[messages_df['chat_id'] == chat_id].copy()
                    
                    if not chat_messages.empty:
                        # Déterminer l'autre utilisateur dans la conversation
                        user_a = selected_chat['user_a']
                        user_b = selected_chat['user_b']
                        
                        # Afficher les messages avec le style approprié
                        chat_manager.display_chat_from_dataframe(chat_messages, user_a, user_b)
                    else:
                        st.info("Aucun message dans cette conversation.")
                else:
                    st.info(f"Aucune conversation trouvée pour {passenger_name}.")
            else:
                st.info("Aucune donnée de chat disponible.")
                
            st.markdown('</div>', unsafe_allow_html=True)  # Fermer chat-content
            st.markdown('</div>', unsafe_allow_html=True)  # Fermer chat-dialog


if __name__ == "__main__":
    app = TripsApp()

    
    app.run()