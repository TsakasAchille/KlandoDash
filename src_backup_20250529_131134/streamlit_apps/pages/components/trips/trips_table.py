import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

class TripsTableManager:
    """Gère l'affichage et l'interaction avec le tableau des trajets"""
    
    def __init__(self):
        self.grid_response = None
        self.selected_df = None
        
    def display_table(self, trips_df):
        """Affiche le tableau des trajets et gère la sélection
        
        Args:
            trips_df: DataFrame contenant les données des trajets
            
        Returns:
            list: Liste des trajets sélectionnés
        """
        # Vérification de sécurité pour éviter les erreurs avec des données vides
        if trips_df is None or len(trips_df) == 0:
            st.warning("Aucune donnée de trajet à afficher.")
            return None
            
        # Configuration de la grille avec case à cocher
        gb = GridOptionsBuilder.from_dataframe(trips_df)
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
            trips_df,
            gridOptions=gb.build(),
            fit_columns_on_grid_load=False,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            height=650,
            custom_css=custom_css
        )

        # Stocker les données sélectionnées dans la session state
        self.selected_df = self.grid_response["selected_rows"]
        
        return self.selected_df
