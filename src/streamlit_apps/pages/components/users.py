import sys
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Ajouter le dossier src au PYTHONPATH pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))) 

from src.data_processing.processors.user_processor import UserProcessor
from src.streamlit_apps.components import Table, Styles, setup_page
from src.streamlit_apps.pages.components import UsersDisplay
from src.streamlit_apps.pages.components.users_trips_linker import UsersTripsLinker
from src.streamlit_apps.components import Cards  # Importez la nouvelle classe Cards
from typing import Optional

from st_aggrid import JsCode

class UserView:
    """
    Classe pour l'affichage des données utilisateurs dans un tableau interactif
    """
    
    def __init__(self):
        """Initialisation de la vue utilisateur"""
        self.user_processor = UserProcessor()
        self.table = Table()
        self.styles = Styles()
        self.users_display = UsersDisplay()  # Initialisation de la nouvelle classe d'affichage
        self.users_trips_linker = UsersTripsLinker()
        Cards.load_card_styles()



    def display_users_table(self, users_df, pre_selected_user_id=None):
        """
        Affiche le tableau des utilisateurs et gère la sélection
        
        Args:
            users_df: DataFrame contenant les données des utilisateurs
            pre_selected_user_id: ID de l'utilisateur à présélectionner
            
        Returns:
            bool: True si un utilisateur est sélectionné, False sinon
        """
        st.subheader("Tableau des Users")
    
        # Colonnes à afficher dans la table
        display_cols = [
            'user_id',
            'display_name',
            'age'
        ]
        
        # Filtrer les colonnes existantes
        valid_cols = [col for col in display_cols if col in users_df.columns]
            
        # CSS personnalisé
        custom_css = {
            ".ag-header": {
                "background-color": "#081C36 !important",
                "color": "white !important",
                "font-size": "18px !important"
            },
            ".ag-row-selected": {
                "background-color": "#7b1f2f !important",
                "color": "white !important"
            },
            ".ag-cell": {
                "font-size": "16px !important"
            },
            ".ag-header-cell-label": {
                "font-weight": "bold !important"
            }
        }
        
        # Configuration de la grille avec case à cocher
        gb = GridOptionsBuilder.from_dataframe(users_df[valid_cols])
        gb.configure_selection('single', use_checkbox=True)
        gb.configure_grid_options(suppressRowClickSelection=True)


    
        # Vérifier si un utilisateur est dans la session state
        """
        if "selected_user_id" in st.session_state:
            pre_selected_user_id = st.session_state["selected_user_id"]
            st.info(f"L'utilisateur ID {pre_selected_user_id} est présélectionné. Veuillez le sélectionner manuellement dans le tableau.")
        """
      # Créer un dictionnaire qui mappe les user_id à leurs indices dans le DataFrame


                
        # Afficher la grille
        self.grid_response = AgGrid(
            users_df[valid_cols],
            gridOptions=gb.build(),
            fit_columns_on_grid_load=False,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            height=700,
            custom_css=custom_css
        )
    
        # Stocker les données sélectionnées dans la session state
        selected_df = self.grid_response["selected_rows"]

        has_selection = False
        if isinstance(selected_df, list):
            has_selection = len(selected_df) > 0
        elif isinstance(selected_df, pd.DataFrame):
            has_selection = not selected_df.empty
        else:
            has_selection = selected_df is not None

     #Stockage de la sélection
        if has_selection:
            # Stocker la sélection dans la session state
            user_id = selected_df['user_id'].iloc[0]
            st.session_state["selected_user_id"] = user_id
            st.session_state["selected_user_df"] = selected_df[0] if isinstance(selected_df, list) else selected_df.iloc[0]

     



    def get_data(self):
        return self.user_processor.handler()



    def display_users_details(self, users_df):


        st.sidebar.title("Utilisateurs")
               

        if users_df is None:
            st.sidebar.error("Aucun utilisateur trouvé")
            return
        
        print("=== Debug UsersApp.run ===")
        
        # Vérifier si des données ont été chargées
        if users_df.empty:
            st.error("Aucun utilisateur n'a pu être chargé")
            return
            

       
        with st.container():

            st.subheader("Détails de l'utilisateur")

         
            self.users_display.user_display_handler(users_df)
                            

    def find_user_trips(self, user_data, trips_df: Optional[pd.DataFrame] = None):
        """
        Cherche les trajets correspondants à l'utilisateur dans le DataFrame des trajets
        
        Args:
            user_data: Dictionnaire ou série contenant les informations d'un utilisateur
            trips_df: DataFrame des trajets déjà chargé, optionnel
        Returns:
            pd.DataFrame: DataFrame des trajets correspondants à l'utilisateur
        """
        if trips_df is None or trips_df.empty:
            return pd.DataFrame()
        
        # Extraire l'ID utilisateur (format "user_X")
        user_id = user_data.get('user_id', "")
        user_id_short = user_id.split("/")[-1] if isinstance(user_id, str) and "/" in user_id else user_id
        
        # Colonnes à vérifier pour les correspondances exactes
        id_columns = ['driver_id', 'passenger_id', 'user_id']
        
        # Colonnes à vérifier pour les correspondances partielles (listes de passagers)
        list_columns = ['all_passengers', 'passengers']
        
        # Créer le masque pour les correspondances
        mask = pd.Series(False, index=trips_df.index)
        
        # Chercher les correspondances exactes
        for col in id_columns:
            if col in trips_df.columns:
                mask = mask | (trips_df[col] == user_id)
        
        # Chercher dans les listes de passagers de façon sécurisée
        for col in list_columns:
            if col in trips_df.columns:
                # Convertir la colonne en chaîne et remplacer NaN par chaîne vide
                str_col = trips_df[col].astype(str).fillna('')
                
                # Chercher les patterns dans la colonne convertie en chaîne
                pattern1 = f"users/{user_id_short}"
                pattern2 = user_id_short
                
                mask = mask | str_col.str.contains(pattern1, na=False)
                mask = mask | str_col.str.contains(pattern2, na=False)
        
        # Retourner les trajets filtrés
        return trips_df[mask].copy()





    def display_user_trip_infos(self, user_data, trips_df: Optional[pd.DataFrame] = None):
        """Affiche les informations de trajets d'un utilisateur
        
        Args:
            user_data: Dictionnaire ou série contenant les informations d'un utilisateur spécifique
            trips_df: DataFrame des trajets déjà chargé, optionnel
        """
        try:
            # Vérifier les données utilisateur
            if user_data is not None:
                # Extraire directement l'ID utilisateur (comme pour user_info)
                user_id = user_data.get('user_id')
                if not user_id:
                    st.error("ID utilisateur non disponible")
                    return
                    
                print(f"Traitement des trajets pour l'utilisateur: {user_id}")
                
                # Appeler la fonction find_user_trips pour filtrer le DataFrame
                user_trips_df = self.find_user_trips(user_data, trips_df)
                
                # Optionnel: afficher des informations de débogage
                print(f"Nombre de trajets trouvés: {len(user_trips_df) if user_trips_df is not None else 0}")



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
                
                # Données pour les metric cards
                metrics_data = [
                    ("Trajets effectués", str(nb_trips)),
                    ("Kilomètres parcourus", f"{total_distance:.1f} km"),
                    ("Économie de CO2", f"{total_co2:.1f} kg")
                ]
                
                # Créer et afficher les metric cards
                metrics_html = Cards.create_metric_cards(metrics_data)
                st.markdown(metrics_html, unsafe_allow_html=True)
                
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


                
                        st.markdown(f"{departure_date}: {origin} → {destination} ({role_icon} {role})")
                
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
            st.error(f"Erreur lors de l'affichage des trajets: {str(e)}")
            import traceback
            st.write(traceback.format_exc())



    def display_user_trip_infos0(self, user_data, trips_df: Optional[pd.DataFrame] = None):
        """Affiche les informations de trajets d'un utilisateur
        
        Args:
            user_data: Dictionnaire ou série contenant les informations d'un utilisateur spécifique
            trips_df: DataFrame des trajets déjà chargé, optionnel
        """
        try:
            # Vérifier les données utilisateur
            if user_data is not None:
                # Extraire directement l'ID utilisateur (comme pour user_info)
                user_id = user_data.get('user_id')
                if not user_id:
                    st.error("ID utilisateur non disponible")
                    return
                    
                print(f"Traitement des trajets pour l'utilisateur: {user_id}")
                
                # Appeler la fonction find_user_trips pour filtrer le DataFrame
                user_trips_df = self.find_user_trips(user_data, trips_df)
                
                # Optionnel: afficher des informations de débogage
                print(f"Nombre de trajets trouvés: {len(user_trips_df) if user_trips_df is not None else 0}")



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
                
                # Données pour les metric cards
                metrics_data = [
                    ("Trajets effectués", str(nb_trips)),
                    ("Kilomètres parcourus", f"{total_distance:.1f} km"),
                    ("Économie de CO2", f"{total_co2:.1f} kg")
                ]
                
                # Créer et afficher les metric cards
                metrics_html = Cards.create_metric_cards(metrics_data)
                st.markdown(metrics_html, unsafe_allow_html=True)
                
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
            st.error(f"Erreur lors de l'affichage des trajets: {str(e)}")
            import traceback
            st.write(traceback.format_exc())


    def display_user_info(self, user_data):
        """Affiche les informations détaillées sur un utilisateur
        
        Args:
            user_data: Dictionnaire ou série contenant les informations de l'utilisateur
        """
        try:
            # Vérifier que les données utilisateur sont valides
            if user_data is not None:
                # Extraire les informations directement
                user_id = user_data.get('user_id', "Non disponible")
                
                # Extraire les autres champs
                display_name = user_data.get('display_name', "Non disponible")
                email = user_data.get('email', "Non disponible")
                phone = user_data.get('phone_number', "Non disponible")
                birth_date = user_data.get('birth', "Non disponible")
                created_at = user_data.get('created_time', "Non disponible")
                updated_at = user_data.get('updated_at', "Non disponible")
                age = user_data.get('age', "Non disponible")
                
                # Formater l'âge pour l'affichage
                age_display = f"{age} ans" if age and age != "Non disponible" else "Non disponible"
                
                # Formater les dates pour l'affichage
                birth_formatted = self.format_date(birth_date) if birth_date and birth_date != "Non disponible" else "Non disponible"
                created_formatted = self.format_date(created_at) if created_at and created_at != "Non disponible" else "Non disponible"
                updated_formatted = self.format_date(updated_at) if updated_at and updated_at != "Non disponible" else "Non disponible"
                
                # Créer le contenu pour info_cards (liste de tuples)
                user_content = [
                    ("ID", user_id),
                    ("Nom", display_name),
                    ("Email", email),
                    ("Téléphone", phone),
                    ("Âge", age_display),
                    ("Date de naissance", birth_formatted),
                    ("Date de création", created_formatted),
                    ("Dernière mise à jour", updated_formatted)
                ]
                
                # Format attendu par create_info_cards: [(titre, contenu, icône)]
                info_data = [("Profil utilisateur", user_content, "👤")]
                
                # Afficher avec Cards.create_info_cards
                card_html = Cards.create_info_cards(
                    info_data,
                    color="#EBC33F",
                    label_size="14px",
                    value_size="16px",
                    background_color="#102844"
                )
                st.markdown(card_html, unsafe_allow_html=True)
                
            else:
                st.error("Aucune donnée utilisateur disponible")
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations de l'utilisateur: {str(e)}")
            import traceback
            st.write(traceback.format_exc())



    def format_detail(self, label: str, value, is_value: bool = True) -> str:
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
    
    def calculate_age(self, birth_date) :
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

    def format_date(self, date_str) -> str:
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

    def run(self):
        """
        Exécute l'application d'affichage des utilisateurs
        """
     
        st.sidebar.title("Utilisateurs")
        
        # Charger les données des utilisateurs
        users_df = self.user_processor.handler()

        if users_df is None:
            st.sidebar.error("Aucun utilisateur trouvé")
            return
        
        print("=== Debug UsersApp.run ===")
        print(f"Types dans users_df: {users_df.dtypes}")    
        
        # Vérifier si des données ont été chargées
        if users_df.empty:
            st.error("Aucun utilisateur n'a pu être chargé")
            return
            
        # Vérifier si un utilisateur doit être sélectionné automatiquement
        pre_selected_user_id = None
        if UsersTripsLinker.should_select_user():
            pre_selected_user_id = UsersTripsLinker.get_selected_user_id()
            if pre_selected_user_id:
                st.info(f"Affichage automatique de l'utilisateur: {pre_selected_user_id}")
            # Effacer la sélection pour ne pas la refaire à chaque rechargement
            UsersTripsLinker.clear_selection()
       
        with st.container():



            st.subheader("Détails de l'utilisateur")

            try:
                # Récupérer les lignes sélectionnées
                selected_df = self.grid_response["selected_rows"]
                    
                # Vérifier s'il y a une sélection valide (liste non vide ou DataFrame non vide)
                has_selection = False
                if isinstance(selected_df, list):
                    has_selection = len(selected_df) > 0
                elif isinstance(selected_df, pd.DataFrame):
                    has_selection = not selected_df.empty
                else:
                    has_selection = selected_df is not None
                    
                if has_selection:
                    # Récupérer la première ligne sélectionnée (adapter selon le type)
                    if isinstance(selected_df, list):
                        user = selected_df[0]  # Liste de dictionnaires
                    else:
                        user = selected_df.iloc[0]  # DataFrame
                        
                    # Vérifier si user_id est présent
                    if 'user_id' in user:
                        user_id = user['user_id']
                        print(f"Traitement des trajets pour l'utilisateur: {user_id}")
                            
                        # Récupérer les données complètes de l'utilisateur si nécessaire
                        # (Optionnel: si vous avez besoin de données supplémentaires non présentes dans la ligne sélectionnée)
                        user_data = users_df[users_df['user_id'] == user_id]
                        print(f"Traitement des données pour l'utilisateur: {user_data}")
                            
                        if not user_data.empty:
                            # Afficher les détails de l'utilisateur avec la nouvelle classe
                            self.users_display.user_display_handler(user_data)
                            
                        else:
                            st.info("Données complètes de l'utilisateur non trouvées")
                    else:
                        st.info("ID utilisateur manquant dans la sélection")
                else:
                    # Message d'instruction
                    st.info("Sélectionnez un utilisateur dans le tableau pour voir ses détails")
            except Exception as e:
                st.error(f"Erreur: {str(e)}")
                import traceback
                st.write(traceback.format_exc())

        # Option de débogage - Aller directement à la page des trajets
        if 'debug_mode' in st.session_state and st.session_state['debug_mode']:
            with st.expander("Options de débogage"):
                st.subheader("Navigation rapide vers un trajet")
                direct_trip_id = st.text_input("ID du trajet à afficher", "trip_1")
                if st.button("Aller au trajet"):
                    # Enregistrer dans la session
                    st.session_state["selected_trip_id"] = direct_trip_id
                    st.session_state["select_trip_on_load"] = True
                    
                    # Afficher un message explicatif pour l'utilisation du menu
                    st.info(f'''
                    L'ID du trajet {direct_trip_id} a été stocker en mémoire. 
                    
                    Veuillez maintenant cliquer sur 'Trajets' dans le menu de navigation pour voir les détails du trajet.
                    ''')
                    
                    # Expliquer la structure des pages Streamlit
                    with st.expander("Pour comprendre la navigation Streamlit"):
                        st.markdown('''
                        **Navigation entre pages dans Streamlit**
                        
                        Streamlit utilise un menu de navigation latéral pour passer d'une page à l'autre.
                        Il n'est pas possible de naviguer directement par une URL personnalisée avec des paramètres comme `/01_trips`.
                        
                        Au lieu de cela, il faut:
                        1. Stocker les données nécessaires en session comme nous venons de le faire
                        2. Cliquer sur le menu 'Trajets' dans la barre latérale pour aller à cette page 
                        3. La page 'Trajets' détectera alors les données en session et affichera le bon trajet
                        ''')  
if __name__ == "__main__":
    app = UserView()

    
    app.run()