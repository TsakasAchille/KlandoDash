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
                    background-color: rgba(8, 28, 54, 1);
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    border-left: 5px solid #7b1f2f;
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
                    color: #D1D5DB;
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
                    color: #C04050;
                    font-size: 18px;
                    font-family: 'Montserrat', sans-serif;
                }
                .metric-card {
                    text-align: center;
                    background-color: rgba(8, 28, 54, 1);
                    border-radius: 5px;
                    padding: 10px;
                    border-left: 5px solid #7b1f2f;
                    transition: transform 0.3s;
                }
                .metric-card:hover {
                    transform: translateY(-5px);
                }
                .metric-label {
                    color: #BBB;
                    margin: 0;
                    font-size: 14px;
                }
                .metric-value {
                    font-size: 24px;
                    font-weight: bold;
                    margin: 0;
                    color: white;
                }
            </style>
            """, unsafe_allow_html=True)

    @staticmethod
    def create_route_card0(departure, destination):
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
    def create_route_card(departure, destination):
        """
        Crée une carte d'itinéraire avec un style moderne
        
        Args:
            departure: Nom du point de départ
            destination: Nom de la destination
        
        Returns:
            HTML formaté pour la carte d'itinéraire
        """
        return f"""
        <div style="border-radius: 10px; padding: 20px; background-color: #081C36; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin: 10px 0; border-left: 5px solid #7B1F2F;">
            <h3 style="margin-top: 0; font-size: 20px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px;">
                <span style="font-size: 22px; margin-right: 10px;">🚗</span> Itinéraire
            </h3>
            <div style="padding: 10px 0;">
                <div style="margin-bottom: 15px;">
                    <p style="color: #999; margin: 0; font-size: 14px;">Départ</p>
                    <p style="font-weight: bold; margin: 0; font-size: 18px; color: #EBC33F;">{departure}</p>
                </div>
                <div style="display: flex; justify-content: center; margin: 10px 0;">
                    <span style="font-size: 24px;">⬇️</span>
                </div>
                <div>
                    <p style="color: #999; margin: 0; font-size: 14px;">Destination</p>
                    <p style="font-weight: bold; margin: 0; font-size: 18px; color: #EBC33F;">{destination}</p>
                </div>
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
    def format_detail_indented(label, value):
        """
        Formate un détail avec indentation des lignes après la première
        """
        # Diviser le texte en lignes
        lines = value.strip().split(',')
        
        # Première ligne normalement
        formatted_text = f"<div class='detail-row' style='margin-bottom: 15px;'><span class='label'>{label}:</span> <span class='value'>{lines[0]}</span>"
        
        # Ajouter les lignes suivantes avec indentation
        if len(lines) > 1:
            for line in lines[1:]:
                formatted_text += f"<br><span class='value' style='margin-left: 30px; margin-top: 5px; display: inline-block;'>{line}</span>"
        
        formatted_text += "</div>"
        return formatted_text

    @staticmethod
    def create_custom_card(title, content, icon="📝", card_class="", top_offset=0):
        """
        Crée une carte personnalisée avec contenu personnalisé
        
        Args:
            title: Titre de la carte
            content: Contenu HTML de la carte (peut inclure n'importe quelle structure HTML)
            icon: Icône à afficher (emoji ou code HTML)
            card_class: Classe CSS additionnelle
            top_offset: Décalage vertical en pixels (peut être négatif pour remonter)
        
        Returns:
            HTML formaté pour la carte personnalisée
        """
        style = f"style='margin-top: {top_offset}px;'" if top_offset != 0 else ""
        return f"""
        <div class="info-card {card_class}" {style}>
            <div class="info-title">
                <span class="icon">{icon}</span> {title}
            </div>
            <div class="info-content">
                {content}
            </div>
        </div>
        """

    @staticmethod
    def format_detail(label, value):
        """
        Format un détail avec une étiquette et une valeur (style moderne)
        
        Args:
            label: Libellé du détail
            value: Valeur à afficher
        
        Returns:
            HTML formaté pour le détail
        """
        return f"""
        <div style="margin-bottom: 10px;">
            <p style="color: #999; margin: 0; font-size: 14px;">{label}</p>
            <p style="font-weight: bold; margin: 0; font-size: 20px;">{value}</p>
        </div>
        """
    
    @staticmethod
    def create_card(title, content, color="#7B1F2F"):
        """
        Crée une carte HTML moderne avec un titre et un contenu
        
        Args:
            title: Titre de la carte
            content: Contenu HTML de la carte
            color: Couleur de fond de la carte (format hex)
        
        Returns:
            HTML formaté pour la carte moderne
        """
        return f"""
        <div style="border-radius: 10px; padding: 15px; background-color: {color}; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); height: 100%;">
            <h3 style="margin-top: 0; margin-bottom: 15px; font-size: 18px;">{title}</h3>
            {content}
        </div>
        """
    
    @staticmethod
    def display_card(title, content, color="#7B1F2F"):
        """
        Affiche une carte directement dans Streamlit
        
        Args:
            title: Titre de la carte
            content: Contenu HTML de la carte
            color: Couleur de fond de la carte (format hex)
        """
        st.markdown(
            Cards.create_card(title, content, color),
            unsafe_allow_html=True
        )



    @staticmethod
    def create_metric_cards0(metrics_data, color="#7B1F2F"):
        """
        Crée une rangée de cartes de métriques à partir d'une liste de données
        """
        cards_html = []
        width = f"{100/len(metrics_data) - 2}%"
        
        for label, value in metrics_data:
            card = f'<div style="width: {width}; margin: 0 5px;"><div class="info-card" style="text-align: center; border-left: 5px solid {color}; padding: 10px;"><p style="color: #BBB; margin: 0; font-size: 14px;">{label}</p><p style="font-size: 24px; font-weight: bold; margin: 0; color: white;">{value}</p></div></div>'
            cards_html.append(card)
        
        html = f'<div style="display: flex; flex-direction: row; justify-content: space-between; align-items: stretch; margin: 10px 0;">{"".join(cards_html)}</div>'
        return html



    @staticmethod
    def create_metric_cards(metrics_data, color="#7B1F2F"):
        """
        Crée une rangée de cartes de métriques à partir d'une liste de données
        """
        cards_html = []
        width = f"{100/len(metrics_data) - 2}%"
        
        for label, value in metrics_data:
            card = f'<div style="width: {width}; margin: 0 5px;"><div class="metric-card" style="border-left-color: {color};"><p class="metric-label">{label}</p><p class="metric-value">{value}</p></div></div>'
            cards_html.append(card)
        
        html = f'<div style="display: flex; flex-direction: row; justify-content: space-between; align-items: stretch; margin: 10px 0;">{"".join(cards_html)}</div>'
        return html