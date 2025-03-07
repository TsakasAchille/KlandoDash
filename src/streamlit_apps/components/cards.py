import streamlit as st
import os

class Cards:
    """Classe pour gérer les cartes d'information stylisées"""
    
    @staticmethod
    def load_card_styles():
        """Charge les styles CSS pour les cartes d'information"""
        # Chemin vers le fichier CSS des cartes
        css_path = os.path.join('assets', 'css', 'cards.css')
        
        # Vérifier si le fichier existe
        if os.path.exists(css_path):
            with open(css_path, 'r') as f:
                css = f.read()
                st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        else:
            # Fallback vers le CSS intégré en cas d'absence du fichier
            st.markdown("""
            <style>
                .info-card {
                    border-radius: 10px;
                    padding: 20px;
                    margin: 10px 0px;
                    background-color: rgba(49, 51, 63, 0.7);
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    border-left: 5px solid #4169E1;
                    transition: transform 0.3s;
                }
                .info-card:hover {
                    transform: translateY(-5px);
                }
                .info-card.warning {
                    border-left: 5px solid #FF9800;
                }
                .info-title {
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                    padding-bottom: 10px;
                }
                .info-content {
                    color: #E0E0E0;
                    font-size: 16px;
                    line-height: 1.5;
                }
                .icon {
                    font-size: 22px;
                    margin-right: 10px;
                    vertical-align: middle;
                }
                .route-icon {
                    color: #4CAF50;
                }
                .detail-icon {
                    color: #2196F3;
                }
                .warning-icon {
                    color: #FF9800;
                }
                .value {
                    font-weight: bold;
                    color: white;
                }
            </style>
            """, unsafe_allow_html=True)

    @staticmethod
    def create_route_card(departure, destination):
        """
        Crée une carte d'itinéraire
        
        Args:
            departure: Nom du point de départ
            destination: Nom de la destination
        
        Returns:
            HTML formaté pour la carte d'itinéraire
        """
        return f"""
        <div class="info-card">
            <div class="info-title">
                <span class="icon route-icon">🚗</span> Itinéraire
            </div>
            <div class="info-content">
                <p><strong>Départ:</strong> <span class="value">{departure}</span></p>
                <p><strong>Destination:</strong> <span class="value">{destination}</span></p>
            </div>
        </div>
        """

    @staticmethod
    def create_details_card(details_list):
        """
        Crée une carte de détails
        
        Args:
            details_list: Liste des détails à afficher (HTML formaté)
        
        Returns:
            HTML formaté pour la carte de détails
        """
        details_content = "\n".join(details_list)
        return f"""
        <div class="info-card">
            <div class="info-title">
                <span class="icon detail-icon">📊</span> Détails du trajet
            </div>
            <div class="info-content">
                {details_content}
            </div>
        </div>
        """

    @staticmethod
    def create_info_card(title, content, icon="ℹ️", card_class="warning"):
        """
        Crée une carte d'information personnalisée
        
        Args:
            title: Titre de la carte
            content: Contenu HTML de la carte
            icon: Icône à afficher (emoji)
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

    @staticmethod
    def format_detail(label, value, is_value=True):
        """
        Formate un détail avec label et valeur
        
        Args:
            label: Libellé du détail
            value: Valeur à afficher
            is_value: Si True, applique le style "value"
        
        Returns:
            HTML formaté pour le détail
        """
        value_class = 'class="value"' if is_value else ''
        return f"<p><strong>{label}:</strong> <span {value_class}>{value}</span></p>"