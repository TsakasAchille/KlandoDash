import streamlit as st

class Styles:
    """Classe pour gérer les styles de l'application"""
    
    def __init__(self):
        self.load_default_styles()
    
    @staticmethod
    def load_default_styles():
        """Charge les styles par défaut pour l'application"""
        st.markdown("""
            <style>
            /* Conteneur d'information */
            .info-container {
                background-color: #e6f3ff;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                color: #2c3e50;
            }
            
            /* Message de sélection */
            .selection-info {
                background-color: #e6f3ff;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                color: #2c3e50;
            }
            
            /* Message d'erreur */
            .error-info {
                background-color: #ffe6e6;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                color: #c0392b;
            }
            
            /* Message de succès */
            .success-info {
                background-color: #e6ffe6;
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                color: #27ae60;
            }
            </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_info(container, message, style_class="info-container", color=None):
        """
        Affiche un message dans un conteneur stylisé
        Args:
            container: Le conteneur Streamlit
            message: Le message à afficher
            style_class: La classe CSS à utiliser
            color: Couleur optionnelle du texte (hex ou nom)
        """
        style = f"color: {color};" if color else ""
        container.markdown(
            f"<div class='{style_class}' style='{style}'>{message}</div>",
            unsafe_allow_html=True
        )