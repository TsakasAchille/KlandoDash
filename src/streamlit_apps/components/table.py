import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Callable
from .table_selection import TableSelection

# Import conditionnel pour éviter l'erreur
AGGRID_AVAILABLE = False
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, ColumnsAutoSizeMode, JsCode
    AGGRID_AVAILABLE = True
except ImportError:
    # Si le module n'est pas disponible, on continue sans lui
    pass

class Table:
    def __init__(self):
        self.load_table_styles()
    
    def load_table_styles(self):
        """Charge les styles CSS pour le tableau"""
        st.markdown("""
            <style>
            /* Style pour la ligne sélectionnée */
            .stDataFrame [data-testid="stDataFrameRow"]:has([role="checkbox"][aria-checked="true"]) {
                background-color: #e6f3ff !important;
            }
            
            /* Style pour le message de sélection */
            .table-selection-info {
                background-color: #e6f3ff;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                color: #1e3d59;
            }
            </style>
        """, unsafe_allow_html=True)
    
    def generate_column_config(self, df: pd.DataFrame, 
                           custom_columns: Optional[Dict] = None,
                           exclude_columns: Optional[List[str]] = None) -> Dict:
        """
        Génère la configuration des colonnes automatiquement
        Args:
            df: DataFrame à afficher
            custom_columns: Configuration personnalisée pour certaines colonnes
            exclude_columns: Colonnes à exclure de l'affichage
        """
        column_config = {}
        exclude_columns = exclude_columns or []
        
        for col in df.columns:
            if col in exclude_columns:
                continue
                
            # Si une config personnalisée existe pour cette colonne
            if custom_columns and col in custom_columns:
                column_config[col] = custom_columns[col]
                continue
            
            # Configuration automatique selon le type de données
            if pd.api.types.is_bool_dtype(df[col]):
                column_config[col] = st.column_config.CheckboxColumn(
                    col.replace('_', ' ').title()
                )
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                column_config[col] = st.column_config.DatetimeColumn(
                    col.replace('_', ' ').title(),
                    format="DD/MM/YYYY HH:mm"
                )
            elif pd.api.types.is_numeric_dtype(df[col]):
                if 'price' in col.lower():
                    column_config[col] = st.column_config.NumberColumn(
                        col.replace('_', ' ').title(),
                        format="%d XOF"
                    )
                elif 'distance' in col.lower():
                    column_config[col] = st.column_config.NumberColumn(
                        col.replace('_', ' ').title(),
                        format="%.1f km"
                    )
                else:
                    column_config[col] = st.column_config.NumberColumn(
                        col.replace('_', ' ').title()
                    )
            else:
                column_config[col] = st.column_config.TextColumn(
                    col.replace('_', ' ').title()
                )
                
        return column_config
    
    def show_selection_info(self, container, selection):
        """Affiche l'info de sélection"""
        container.markdown(
            f"<div class='table-selection-info'>🔍 Trajet sélectionné: {selection['trip_id'].iloc[0]}</div>",
            unsafe_allow_html=True
        )
                
    def handle_selection(self, selection: pd.DataFrame, container: st.container, 
                        on_select: Optional[Callable] = None) -> None:
        """Gère la sélection d'une ligne dans le tableau"""
        print("=== Debug Table.handle_selection ===")
        print("Selection reçue:", selection)
        print("Type de selection:", type(selection))
        if selection is not None:
            print("Shape de selection:", selection.shape)
        print("================================")
        
        table_selection = TableSelection(selection)
        print("TableSelection créé:", table_selection)
        
        if table_selection.selected:
            table_selection.show_info(container)
            if on_select:
                on_select(selection)


    def display(self, df: pd.DataFrame,
                custom_columns: Optional[Dict] = None,
                exclude_columns: Optional[List[str]] = None,
                height: int = 400,
                on_select: Optional[Callable] = None) -> None:
        """Affiche un DataFrame sous forme de tableau interactif"""
        # Générer la configuration des colonnes
        column_config = self.generate_column_config(df, custom_columns, exclude_columns)
        
        # Colonnes à afficher
        display_columns = [col for col in df.columns if col not in (exclude_columns or [])]
        
        # Créer un conteneur pour le message de sélection
        selection_container = st.container()

        # Afficher le tableau avec gestion des événements
        st.data_editor(
            df[display_columns],
            column_config=column_config,
            height=height,
            use_container_width=True,
            hide_index=True,
            key="data_editor",
            disabled=False,
            num_rows="fixed"
        )

        # Gérer la sélection après l'affichage du tableau
        if ("data_editor" in st.session_state and 
            isinstance(st.session_state.data_editor, dict) and 
            "selected_rows" in st.session_state.data_editor):
            selected_rows = st.session_state.data_editor["selected_rows"]
            if selected_rows:
                selected_index = selected_rows[0]
                selection = df.iloc[[selected_index]]
                self.handle_selection(selection, selection_container, on_select)
                
    def display_aggrid(self, df: pd.DataFrame,
                      exclude_columns: Optional[List[str]] = None,
                      height: int = 400,
                      on_select: Optional[Callable] = None,
                      on_cell_click: Optional[Callable] = None) -> None:
        """
        Affiche un tableau interactif AgGrid simplifié
        """
        # Vérifier si streamlit_aggrid est disponible
        if not AGGRID_AVAILABLE:
            st.warning("Le module streamlit-aggrid n'est pas installé. Installation avec : pip install streamlit-aggrid")
            self.display(df, exclude_columns=exclude_columns)
            return
        
        # Préparer les données
        display_df = self._prepare_display_data(df, exclude_columns)
        
        try:
            # Configuration basique pour le tableau
            gb = GridOptionsBuilder.from_dataframe(display_df)
            gb.configure_selection(selection_mode="single", use_checkbox=False)
            
            # Configuration simple pour détecter les clics
            js_code = JsCode("""
            function(e) {
                // Envoyer l'information du clic à Streamlit
                if (window.Streamlit) {
                    window.Streamlit.setComponentValue("clicked");
                }
            }
            """)
            gb.configure_grid_options(onCellClicked=js_code)
            
            # Afficher le tableau
            grid_response = AgGrid(
                display_df,
                gridOptions=gb.build(),
                height=height,
                fit_columns_on_grid_load=True,
                allow_unsafe_jscode=True,
                key="simple_grid"
            )
            
            # Vérifier si une cellule a été cliquée
            if st.session_state.get("simple_grid") == "clicked":
                st.write("Hello")  # Affiche simplement "Hello" sous le tableau quand on clique
                
            # Afficher les infos de la ligne sélectionnée si nécessaire
            selected_rows = grid_response.get("selected_rows", [])
            if selected_rows:
                st.write(f"Ligne sélectionnée: {selected_rows[0]}")
                
        except Exception as e:
            st.error(f"Erreur lors de l'affichage du tableau AgGrid: {e}")
            self.display(df, exclude_columns=exclude_columns)
    
    def _prepare_display_data(self, df: pd.DataFrame, exclude_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Prépare les données pour l'affichage"""
        exclude_columns = exclude_columns or []
        display_columns = [col for col in df.columns if col not in exclude_columns]
        return df[display_columns].copy()
    
    def _configure_grid_options(self, df: pd.DataFrame, on_cell_click: Optional[Callable] = None):
        """Configure les options de la grille AgGrid"""
        gb = GridOptionsBuilder.from_dataframe(df)
        
        # Configurer la sélection
        gb.configure_selection(selection_mode="single", use_checkbox=False)
        print("in conf")
        # Configurer la détection de clic sur cellule
        if on_cell_click:
            js_cell_click = JsCode("""
            function(e) {
                const detail = {
                    'column': e.column.colId,
                    'rowData': e.data
                };
                if (window.Streamlit) {
                    window.Streamlit.setComponentValue(detail);
                }
            }
            """)
            gb.configure_grid_options(onCellClicked=js_cell_click)
        
        # Définir propriétés UI
        gb.configure_grid_options(
            domLayout='normal',
            headerHeight=45,
            rowHeight=35,
            enableCellTextSelection=True
        )
        
        return gb.build()
    
    def _handle_row_selection(self, grid_response, original_df, display_df, on_select: Optional[Callable] = None):
        """Gère la sélection de lignes"""
        selected_rows = grid_response.get("selected_rows", [])
        if not selected_rows:
            return
            
        selected_row = selected_rows[0]
        
        # Afficher l'ID si disponible
        self._display_row_id(selected_row)
        
        # Appeler le callback si fourni
        if on_select:
            selection = self._find_matching_rows(original_df, display_df, selected_row)
            if not selection.empty:
                on_select(selection)
    
    def _display_row_id(self, row_data):
        """Affiche l'ID de la ligne sélectionnée"""
        id_col = next((col for col in row_data.keys() 
                      if col.lower() == 'id' or col.lower().endswith('_id')), None)
        if id_col:
            st.write(f"ID sélectionné: {row_data[id_col]}")
    
    def _find_matching_rows(self, original_df, display_df, row_data):
        """Trouve les lignes correspondantes dans le DataFrame original"""
        display_columns = display_df.columns
        
        # Créer un masque pour trouver les lignes correspondantes
        mask = pd.Series(True, index=original_df.index)
        
        # Vérifier chaque colonne présente dans row_data et dans display_columns
        for col in [c for c in display_columns if c in row_data]:
            selected_val = row_data.get(col)
            if pd.isna(selected_val):
                mask = mask & original_df[col].isna()
            else:
                mask = mask & (original_df[col] == selected_val)
        
        return original_df[mask]
    
    def _handle_cell_click(self, on_cell_click: Optional[Callable] = None):
        """Gère les clics sur cellules"""
        cell_clicked = st.session_state.get("aggrid")
        if not (on_cell_click and cell_clicked and isinstance(cell_clicked, dict)):
            return
        print("in cell click")
        column = cell_clicked.get('column')
        row_data = cell_clicked.get('rowData')
        
        if column and row_data:
            on_cell_click(row_data, column)