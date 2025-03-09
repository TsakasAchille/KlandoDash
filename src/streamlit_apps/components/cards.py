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
                /* Classe de base pour tous les types de cartes */
                .card-base {
                    text-align: center;
                    background-color: rgba(8, 28, 54, 1);
                    border-radius: 5px;
                    padding: 0px 5px 5px 0px;
                    border-left: 5px solid #7b1f2f;
                    transition: transform 0.3s;
                }
                .card-base:hover {
                    transform: translateY(-5px);
                }
               

                /* Styles pour les cartes d'information */
                .info-card {
                    text-align: left;
                    padding: 5px 5px 5px 10px; /* haut droite bas gauche */
                    border-left: 5px solid #FFFFFF;
                }
                .info-card.warning {
                    border-left: 5px solid #FF9800
                }
                .info-title {
                    color: white;
                    font-size: 15px;
                    font-weight: bold;
                    margin-bottom: 8px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                    padding-bottom: 8px;
                }
                .info-content {
                    color: #D1D5DB;
                    font-size: 16px;
                    margin-top: 2px;
                    margin-bottom: 2px;
                    line-height: 1.2;
                }
                .info-card .value {
                    font-weight: bold;
                    color: white;
                    font-size: 15px;
                    margin: 0;
                    display: block;
                    margin-top: 2px;
                    margin-bottom: 2px;
                }
                .info-card .label {
                    font-weight: 600;
                    color: #A0A6B0;
                    font-size: 9px;
                    margin-right: 8px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                /* Styles pour les cartes métriques */
                .metric-card {
                    text-align: center;
                    padding: 5px;
                    border-left: 5px solid #7b1f2f;
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
                
                /* Styles pour les icônes */
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
                
                /* Autres styles */
                .value {
                    font-weight: bold;
                    color: #C04050;
                    font-size: 18px;
                    font-family: 'Montserrat', sans-serif;
                }
            </style>
            """, unsafe_allow_html=True)




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
    def create_info_card0(title, content, icon="ℹ️", card_class="warning"):
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
    def create_metric_cards(metrics_data, color="#7B1F2F"):
        """
        Crée une rangée de cartes de métriques à partir d'une liste de données
        """
        cards_html = []
        width = f"{100/len(metrics_data) - 2}%"
        

    


        for label, value in metrics_data:
            card = (
                f'<div style="width: {width}; margin: 0 5px;">'
                f'<div class="card-base" style="border-left-color: {color};">'
                f'<p class="metric-label" style="font-size: 12px;">{label}</p>'
                f'<p class="metric-value" style="font-size: 18px;">{value}</p>'
                f'</div>'
                f'</div>'
            )
            cards_html.append(card)
        
        html = f'<div style="display: flex; flex-direction: row; justify-content: space-between; align-items: stretch; margin: 10px 0;">{"".join(cards_html)}</div>'
        return html



    @staticmethod
    def create_info_cards(info_data, 
                        color="#7B1F2F", 
                        widths=None, 
                        label_size=None, 
                        value_size=None, 
                        vertical_layout=False,
                        max_height=None, 
                        background_color=None):
        """
        Crée une rangée de cartes d'informations à partir d'une liste de données
        
        Args:
            info_data: Liste de tuples (title, content_items, icon)
                où content_items est une liste de tuples (label, value)
            color: Couleur de la bordure gauche
            widths: Liste optionnelle des largeurs en % pour chaque carte
            label_size: Taille en px pour les labels (ex: "14px")
            value_size: Taille en px pour les valeurs (ex: "16px")
            vertical_layout: Si True, affiche les valeurs sous les labels au lieu de côte à côte
        
        Returns:
            HTML formaté pour les cartes d'information
        """
        cards_html = []
        max_height_style = f' style="max-height: {max_height}; overflow-y: auto;"' if max_height else ''
        bg_style = f"background-color: {background_color}; " if background_color else ""

        # Gestion des largeurs
        if widths is None:
            width = f"{100/len(info_data) - 2}%"
            widths = [width] * len(info_data)
        else:
            widths = [f"{w}%" for w in widths]
        
        # Style inline pour les tailles personnalisées
        label_style = f' style="font-size: {label_size};"' if label_size else ''
        value_style = f' style="font-size: {value_size};"' if value_size else ''
        
        for (title, content_items, icon), width in zip(info_data, widths):
            # Génération du contenu avec labels et values personnalisés
            content_html = ""
            for label, value in content_items:
                if vertical_layout:
                    # Affichage vertical (valeur sous le label)
                    content_html += f'<p><span class="label"{label_style}>{label}:</span> <span class="value"{value_style}>{value}</span></p>'
                else:
                    # Affichage horizontal (valeur à côté du label)
                    content_html += f'<p><span class="label"{label_style}>{label}</span> <span class="value"{value_style}>{value}</span></p>'
            
            card = (
                f'<div style="width: {width};margin: 0px 5px 0px 5px;">'
                f'<div class="card-base info-card" style="{bg_style}border-left-color: {color};">'
                f'<div class="info-title">'
                f'<span class="icon">{icon}</span> {title}'
                f'</div>'
                f'<div class="info-content"{max_height_style}>{content_html}</div>'
                f'</div>'
                f'</div>'
            )
            cards_html.append(card)
        
        html = f'<div style="display: flex; flex-direction: row; justify-content: space-between; align-items: stretch; margin: 0px 0;">{"".join(cards_html)}</div>'
        return html