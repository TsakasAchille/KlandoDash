import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import json
from datetime import datetime, timedelta
from typing import Dict, Optional
# Changer l'import pour utiliser un chemin relatif
from src.data_processing.loaders.loader import Loader
from src.data_processing.utils.backend import Backend

class UserProcessor:
    """
    Classe pour visualiser les profils des utilisateurs
    et leurs statistiques dans l'application Streamlit.
    """
    
    def __init__(self):
        """Initialise la visualisation des profils utilisateurs"""
        # Utiliser Loader au lieu de s'instancier soi-même
        self.loader = Loader()
        self.backend = Backend()
    
    def handler(self) -> dict:
        """Charge et traite les données des utilisateurs
        Returns:
            dict: Dictionnaire contenant les données utilisateurs
        """
        # Trouver le fichier utilisateur le plus récent
        users_file_path = self.loader.find_latest_json_file_path(data_type='users')
        if users_file_path is None:
            print("Erreur : Aucun fichier d'utilisateurs trouvé")
            return None
            
        print(f"Chargement des utilisateurs depuis : {users_file_path}")
        
        users_df = self.convert_users_json_to_dataframe(users_file_path)

        if users_df is None:
            print("Erreur : Impossible de charger les données des utilisateurs")
            return None


        return users_df

    
    def load_data(self) -> pd.DataFrame:
        """Charge les données des utilisateurs
        Returns:
            pd.DataFrame: DataFrame des utilisateurs
        """
        users_dict = self.handler()
        
        if not users_dict:
            return pd.DataFrame()
        
        # Convertir le dictionnaire en DataFrame
        users_list = []
        for user_id, user_info in users_dict.items():
            user_data = user_info.get('data', {})
            user_data['user_id'] = user_id  # Ajouter l'ID utilisateur
            
            # Convertir les dates si nécessaire
            if 'created_time' in user_data and isinstance(user_data['created_time'], str):
                try:
                    user_data['created_time'] = datetime.fromisoformat(user_data['created_time'].replace('Z', '+00:00'))
                except ValueError:
                    pass
            
            users_list.append(user_data)
        
        users_df = pd.DataFrame(users_list)
        return users_df
    
    def get_user_stats(self, users_df: pd.DataFrame) -> Dict:
        """Calcule les statistiques sur les utilisateurs
        Args:
            users_df: DataFrame des utilisateurs
        Returns:
            Dict: Dictionnaire des statistiques
        """
        stats = {
            'total_users': len(users_df)
        }
        
        # Calculer l'âge moyen si disponible
        if 'age' in users_df.columns:
            valid_ages = users_df['age'].dropna()
            if not valid_ages.empty:
                stats['avg_age'] = round(valid_ages.mean(), 1)
        
        # Autres statistiques utiles
        if 'created_time' in users_df.columns:
            now = datetime.now()
            stats['recent_users'] = len(users_df[users_df['created_time'] > (now - timedelta(days=30))])
        
        return stats
    
    def display_overview_metrics(self, stats: Dict, users_df: pd.DataFrame):
        """
        Affiche les métriques principales
        Args:
            stats: Dictionnaire des statistiques utilisateurs
            users_df: DataFrame des utilisateurs
        """
        col1, col2, col3 = st.columns(3)
        
        # Afficher les métriques principales
        col1.metric("Utilisateurs totaux", stats.get('total_users', 'N/A'))
        
        # Calcul et affichage de l'âge moyen (si disponible)
        avg_age = stats.get('avg_age', 'N/A')
        col2.metric("Âge moyen", avg_age)
        
        # Afficher le nombre d'utilisateurs récents (derniers 30 jours)
        if 'created_time' in users_df.columns:
            import datetime as dt
            now = dt.datetime.now()
            thirty_days_ago = now - dt.timedelta(days=30)
            recent_users = users_df[users_df['created_time'] > thirty_days_ago]
            col3.metric("Nouveaux utilisateurs (30j)", len(recent_users))
        else:
            col3.metric("Nouveaux utilisateurs (30j)", "N/A")
    
    def display_age_distribution(self, users_df: pd.DataFrame):
        """
        Affiche la distribution des âges des utilisateurs
        Args:
            users_df: DataFrame des utilisateurs
        """
        if 'age' in users_df.columns:
            # Filtrer les âges valides
            age_df = users_df[users_df['age'].notna()]
            
            if not age_df.empty:
                # Créer un histogramme de la distribution des âges
                fig = px.histogram(
                    age_df, 
                    x='age',
                    nbins=15,
                    labels={'age': 'Âge', 'count': 'Nombre d\'utilisateurs'},
                    title='Distribution des âges'
                )
                
                # Mettre à jour la mise en page
                fig.update_layout(
                    height=350,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée d'âge disponible")
    
    def display_creation_time_chart(self, users_df: pd.DataFrame):
        """
        Affiche un graphique des inscriptions au fil du temps
        Args:
            users_df: DataFrame des utilisateurs
        """
        if 'created_time' in users_df.columns:
            # S'assurer que les valeurs de date sont valides
            valid_df = users_df[users_df['created_time'].notna()].copy()
            
            if not valid_df.empty:
                # Extraire juste la date (sans l'heure)
                valid_df['creation_date'] = valid_df['created_time'].dt.date
                
                # Compter les utilisateurs par date
                counts = valid_df.groupby('creation_date').size().reset_index(name='count')
                counts = counts.sort_values('creation_date')
                
                # Calculer le cumul
                counts['cumulative'] = counts['count'].cumsum()
                
                # Créer le graphique
                fig = px.line(
                    counts,
                    x='creation_date',
                    y='cumulative',
                    title='Croissance des inscriptions',
                    labels={'creation_date': 'Date', 'cumulative': 'Utilisateurs cumulés'}
                )
                
                # Ajouter les inscriptions quotidiennes comme barres
                fig.add_bar(
                    x=counts['creation_date'],
                    y=counts['count'],
                    name='Inscriptions quotidiennes',
                    opacity=0.5
                )
                
                # Mettre à jour la mise en page
                fig.update_layout(
                    height=350,
                    margin=dict(l=20, r=20, t=40, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune donnée de date d'inscription disponible")
    
    def display_user_table(self, users_df: pd.DataFrame) -> None:
        """
        Affiche le tableau des utilisateurs avec les informations de base
        
        Args:
            users_df (pd.DataFrame): DataFrame contenant les données des utilisateurs
        """
        if users_df is None or users_df.empty:
            st.error("Aucune donnée d'utilisateur à afficher")
            return
        
        # Définir les colonnes à afficher
        display_cols = [
            'user_id',
            'display_name', 
            'email',
            'phone_number',
            'age'
        ]
        
        # Filtrer uniquement les colonnes valides
        valid_cols = [col for col in display_cols if col in users_df.columns]
        
        # Configurer les options de la grille
        gb = GridOptionsBuilder.from_dataframe(users_df[valid_cols])
        gb.configure_selection('single', use_checkbox=True)
        gb.configure_grid_options(suppressRowClickSelection=True)
        
        # Appliquer des formateurs personnalisés pour certaines colonnes
        for col in valid_cols:
            # Configuration spécifique pour chaque type de colonne
            if col == 'display_name':
                gb.configure_column(col, header_name="Nom complet")
            elif col == 'user_id':
                gb.configure_column(col, header_name="ID Utilisateur")
            elif col == 'email':
                gb.configure_column(col, header_name="Email")
            elif col == 'phone_number':
                gb.configure_column(col, header_name="Téléphone")
            elif col == 'age':
                gb.configure_column(col, header_name="Âge")
        
        # Afficher le tableau
        grid_response = AgGrid(
            users_df[valid_cols],
            gridOptions=gb.build(),
            fit_columns_on_grid_load=True,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            height=400
        )
        
        # Traiter la sélection
        selected_rows = grid_response["selected_rows"]
        if selected_rows:
            selected_user = selected_rows[0]
            st.write("---")
            st.subheader("Détails de l'utilisateur")
            self.display_user_info(selected_user)
    
    def display_user_profile_tab(self):
        """
        Affiche l'onglet de profil utilisateur complet
        """
        st.header("Profil des utilisateurs")
        
        # Charger les données
        users_df = self.load_data()
        
        if users_df is None or users_df.empty:
            st.error("Impossible de charger les données utilisateurs")
            return
        
        # Calculer les statistiques
        stats = self.get_user_stats(users_df)
        
        # Afficher les métriques d'aperçu
        self.display_overview_metrics(stats, users_df)
        
        # Diviser l'écran en deux colonnes pour les graphiques
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Afficher la distribution des âges
            self.display_age_distribution(users_df)
        
        with col_right:
            # Afficher le graphique d'inscription
            self.display_creation_time_chart(users_df)
        
        # Afficher le tableau des utilisateurs
        self.display_user_table(users_df)


    def convert_users_json_to_dataframe(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Convertit le JSON des utilisateurs en DataFrame avec une structure aplatie
        Args:
            file_path (str): Chemin vers le fichier JSON des utilisateurs
        Returns:
            Optional[pd.DataFrame]: DataFrame structuré des utilisateurs ou None si erreur
        """
        if not self.loader._check_json_file(file_path):
            return None

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            users_list = []
            for user_id, user_data in data.items():
                # S'assurer que l'ID est correctement généré
                user_dict = {
                    'user_id': user_id,  # ID externe (clé principale dans le JSON)
                    'updated_at': user_data.get('updated_at'),
                    # Informations de base
                    'uid': user_id,  # Utiliser directement l'ID externe comme uid
                    'first_name': user_data['data'].get('first_name'),
                    'name': user_data['data'].get('name'),
                    'display_name': user_data['data'].get('display_name'),
                    'email': user_data['data'].get('email'),
                    'phone_number': user_data['data'].get('phone_number'),
                    'phone_verified': user_data['data'].get('phone_verified'),
                    'birth': user_data['data'].get('birth'),
                    'age': user_data['data'].get('age'),
                    'created_time': user_data['data'].get('created_time'),
                    'photo_url': user_data['data'].get('photo_url', ''),
                    'short_description': user_data['data'].get('short_description', '')
                }
                users_list.append(user_dict)
            
            df = pd.DataFrame(users_list)
            
            # Conversion des dates comme dans TripProcessor
            date_columns = ['birth', 'created_time', 'updated_at']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Formater les informations d'utilisateur
            # Ajouter des colonnes dérivées utiles si nécessaire
            if 'display_name' in df.columns and 'name' in df.columns and 'first_name' in df.columns:
                # S'assurer que display_name est rempli même si la valeur est None
                df['display_name'] = df.apply(
                    lambda row: row['display_name'] if pd.notna(row['display_name']) else 
                    f"{row['name'] or ''} {row['first_name'] or ''}".strip(), axis=1
                )
            
            return df

        except Exception as e:
            print(f"Erreur lors du parsing du fichier utilisateurs {file_path}: {e}")
            return None
