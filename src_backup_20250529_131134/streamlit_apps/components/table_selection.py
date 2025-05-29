import streamlit as st
import pandas as pd
from typing import Optional
from dataclasses import dataclass

@dataclass
class TableSelection:
    """Classe pour gérer la sélection dans un tableau"""
    selection: pd.DataFrame

    def __post_init__(self):
        """Initialise les propriétés après la création de l'instance"""
        print("=== Debug TableSelection.__post_init__ ===")
        print("Selection reçue dans TableSelection:", self.selection)
        if self.selection is not None:
            print("Shape de selection:", self.selection.shape)
        
        self.selected = self._is_selected()
        print("Is selected:", self.selected)
        
        self.selected_row = self._get_selected_row()
        print("Selected row:", self.selected_row)
        
        self.selected_id = self._get_selected_id()
        print("Selected ID:", self.selected_id)
        print("=====================================")
    def __str__(self) -> str:
        """Représentation string de la sélection"""
        if not self.selected:
            return "Aucune ligne sélectionnée"
        return f"Ligne sélectionnée - ID: {self.selected_id}"

    def __repr__(self) -> str:
        """Représentation détaillée de la sélection"""
        if not self.selected:
            return "TableSelection(selected=False)"
        return f"TableSelection(selected=True, id={self.selected_id})"

    def _is_selected(self) -> bool:
        """Vérifie si une ligne est sélectionnée"""
        print("=== Debug _is_selected ===")
        print("Selection type:", type(self.selection))
        print("Selection empty?", self.selection.empty if isinstance(self.selection, pd.DataFrame) else "N/A")
        print("Selection attrs:", getattr(self.selection, 'attrs', {}))
        print("========================")
        
        # Vérifie si une sélection existe dans l'éditeur
        if not isinstance(self.selection, pd.DataFrame):
            return False
        if self.selection.empty:
            return False
        # Vérifie si l'éditeur a une sélection active
        if hasattr(self.selection, 'attrs') and 'edited_rows' in self.selection.attrs:
            return bool(self.selection.attrs['edited_rows'])
        return False
    def _get_selected_row(self) -> Optional[pd.Series]:
        """Récupère la ligne sélectionnée"""
        if self.selected:
            return self.selection.iloc[0]
        return None

    def _get_selected_id(self) -> Optional[str]:
        """Récupère l'ID de la ligne sélectionnée"""
        if self.selected and 'trip_id' in self.selection.columns:
            return self.selection['trip_id'].iloc[0]
        return None

    def show_info(self, container: st.container) -> None:
        """Affiche l'info de sélection"""
        if self.selected and self.selected_id:
            container.markdown(
                f"<div class='table-selection-info'>🔍 Trajet sélectionné: {self.selected_id}</div>",
                unsafe_allow_html=True
            )

    def debug_info(self) -> None:
        """Affiche les informations de debug"""
        st.write("--- Debug Selection Info ---")
        st.write(f"Selected: {self.selected}")
        st.write(f"Selected ID: {self.selected_id}")
        if self.selected_row is not None:
            st.write("Selected Row Data:")
            st.write(self.selected_row)

    def print_info(self) -> None:
        """Affiche les informations dans la console"""
        print("=== Table Selection Info ===")
        print(f"Selected: {self.selected}")
        print(f"Selected ID: {self.selected_id}")
        if self.selected_row is not None:
            print("\nSelected Row Data:")
            print(self.selected_row)