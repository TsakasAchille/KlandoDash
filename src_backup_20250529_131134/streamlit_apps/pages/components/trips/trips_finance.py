import streamlit as st
import pandas as pd
from src.streamlit_apps.components.modern_card import modern_card

class TripsFinanceManager:
    """Gu00e8re l'affichage des informations financiu00e8res des trajets"""
    
    def display_financial_info(self, trip_data):
        """Affiche les informations financiu00e8res du trajet
        
        Args:
            trip_data: Donnu00e9es du trajet su00e9lectionnu00e9
        """
        try:
            price_per_seat = None
            viator_income = None
            
            if 'price_per_seat' in trip_data:
                price = trip_data['price_per_seat'].values[0] if isinstance(trip_data['price_per_seat'], pd.Series) else trip_data['price_per_seat']
                if isinstance(price, (int, float)):
                    price_per_seat = f"{price:.2f} XOF"
                else:
                    price_per_seat = f"{price} XOF" if price else "Non disponible"
            else:
                price_per_seat = "Non disponible"
                
            if 'viator_income' in trip_data:
                income = trip_data['viator_income'].values[0] if isinstance(trip_data['viator_income'], pd.Series) else trip_data['viator_income']
                if isinstance(income, (int, float)):
                    viator_income = f"{income:.2f} XOF"
                else:
                    viator_income = f"{income} XOF" if income else "Non disponible"
            else:
                viator_income = "Non disponible"
            modern_card(
                title="Finances",
                icon="💸",
                items=[
                    ("Prix par place", price_per_seat),
                    ("Revenu Viator", viator_income)
                ],
                accent_color="#EBC33F"
            )
        except Exception as e:
            st.error(f"Erreur lors de l'affichage des informations financiu00e8res: {str(e)}")
