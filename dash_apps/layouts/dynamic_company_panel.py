"""
Panel dynamique configurable pour afficher les informations d'entreprise
Inspiré du design user_profile avec logo et nom d'entreprise personnalisables
"""
from typing import Dict, Any, Optional
from dash import html
import dash_bootstrap_components as dbc
from dash_apps.utils.settings import load_json_config

# Styles inspirés du user_profile
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '28px',
    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
    'padding': '0px',
    'overflow': 'hidden',
    'marginBottom': '16px'
}

class DynamicCompanyPanel:
    """Classe pour générer des panels d'entreprise dynamiques et configurables"""
    
    @staticmethod
    def _load_company_config() -> Dict[str, Any]:
        """Charge la configuration des panels d'entreprise"""
        try:
            config = load_json_config('company_panel_config.json')
            return config
        except Exception as e:
            print(f"❌ Erreur chargement config company panel: {e}")
            return {}
    
    @staticmethod
    def render_company_panel(company_data: Dict[str, Any], panel_type: str = "default") -> html.Div:
        """
        Génère un panel d'entreprise dynamique selon la configuration
        
        Args:
            company_data: Données de l'entreprise (nom, logo, etc.)
            panel_type: Type de panel à générer selon la config
        """
        config = DynamicCompanyPanel._load_company_config()
        panel_config = config.get('panels', {}).get(panel_type, {})
        field_icons = config.get('field_icons', {})
        
        if not panel_config:
            return DynamicCompanyPanel._render_fallback_panel(company_data)
        
        # Configuration du panel
        layout_type = panel_config.get('layout', 'horizontal')
        show_logo = panel_config.get('show_logo', True)
        show_description = panel_config.get('show_description', True)
        show_contact = panel_config.get('show_contact', True)
        show_extra_fields = panel_config.get('show_extra_fields', False)
        fields_to_show = panel_config.get('fields', [])
        
        # Générer le contenu selon le layout
        if layout_type == 'vertical':
            return DynamicCompanyPanel._render_vertical_layout(
                company_data, field_icons, show_logo, show_description, 
                show_contact, show_extra_fields, fields_to_show
            )
        elif layout_type == 'card':
            return DynamicCompanyPanel._render_card_layout(
                company_data, field_icons, show_logo, show_description, 
                show_contact, show_extra_fields, fields_to_show
            )
        elif layout_type == 'stats':
            return DynamicCompanyPanel._render_stats_layout(
                company_data, field_icons, show_logo, show_description, 
                show_contact, show_extra_fields, fields_to_show
            )
        else:  # horizontal (default)
            return DynamicCompanyPanel._render_horizontal_layout(
                company_data, field_icons, show_logo, show_description, 
                show_contact, show_extra_fields, fields_to_show
            )
    
    @staticmethod
    def _render_horizontal_layout(company_data: Dict[str, Any], field_icons: Dict[str, str],
                                show_logo: bool, show_desc: bool, show_contact: bool,
                                show_extra: bool, fields_to_show: list) -> html.Div:
        """Layout horizontal avec logo à gauche et infos à droite"""
        
        name = company_data.get('name', 'Entreprise')
        logo_url = company_data.get('logo_url', '')
        
        # Section logo
        logo_section = []
        if show_logo and logo_url:
            logo_section = [
                html.Div([
                    html.Img(
                        src=logo_url,
                        style={
                            "width": "80px", "height": "80px", 
                            "borderRadius": "12px",
                            "objectFit": "cover", 
                            "backgroundColor": "#f8f9fa",
                            "border": "2px solid #e9ecef"
                        }
                    )
                ], className="d-flex justify-content-center align-items-center", 
                   style={"flex": "0 0 100px"})
            ]
        
        # Section informations
        info_items = [
            html.H4(name, className="mb-3", style={"color": "#2d3748", "fontWeight": "600"})
        ]
        
        # Générer les champs dynamiquement
        data_fields = DynamicCompanyPanel._generate_field_items(
            company_data, field_icons, show_desc, show_contact, show_extra, fields_to_show
        )
        info_items.extend(data_fields)
        
        info_section = html.Div(info_items, style={"flex": "1 1 auto"})
        
        # Assemblage final
        content = html.Div([
            *logo_section,
            info_section
        ], className="d-flex align-items-start gap-3 p-4")
        
        return html.Div(content, style=CARD_STYLE)
    
    @staticmethod
    def _render_vertical_layout(company_data: Dict[str, Any], field_icons: Dict[str, str],
                              show_logo: bool, show_desc: bool, show_contact: bool,
                              show_extra: bool, fields_to_show: list) -> html.Div:
        """Layout vertical avec logo en haut et infos en bas"""
        
        name = company_data.get('name', 'Entreprise')
        logo_url = company_data.get('logo_url', '')
        
        content_items = []
        
        # Logo centré en haut
        if show_logo and logo_url:
            content_items.append(
                html.Div([
                    html.Img(
                        src=logo_url,
                        style={
                            "width": "120px", "height": "120px",
                            "borderRadius": "16px",
                            "objectFit": "cover",
                            "backgroundColor": "#f8f9fa",
                            "border": "3px solid #e9ecef"
                        }
                    )
                ], className="text-center mb-3")
            )
        
        # Nom de l'entreprise
        content_items.append(
            html.H3(name, className="text-center mb-4", 
                   style={"color": "#2d3748", "fontWeight": "700"})
        )
        
        # Générer les champs dynamiquement
        data_fields = DynamicCompanyPanel._generate_field_items(
            company_data, field_icons, show_desc, show_contact, show_extra, fields_to_show, center=True
        )
        content_items.extend(data_fields)
        
        content = html.Div(content_items, className="p-4")
        return html.Div(content, style=CARD_STYLE)
    
    @staticmethod
    def _render_card_layout(company_data: Dict[str, Any], field_icons: Dict[str, str],
                          show_logo: bool, show_desc: bool, show_contact: bool,
                          show_extra: bool, fields_to_show: list) -> html.Div:
        """Layout card avec header coloré et body blanc"""
        
        name = company_data.get('name', 'Entreprise')
        logo_url = company_data.get('logo_url', '')
        
        # Header avec logo et nom
        header_content = []
        if show_logo and logo_url:
            header_content.extend([
                html.Img(
                    src=logo_url,
                    style={
                        "width": "50px", "height": "50px",
                        "borderRadius": "8px",
                        "objectFit": "cover",
                        "backgroundColor": "rgba(255,255,255,0.2)",
                        "border": "2px solid rgba(255,255,255,0.3)"
                    }
                ),
                html.H5(name, className="mb-0 ms-3", style={"color": "white", "fontWeight": "600"})
            ])
        else:
            header_content.append(
                html.H5(name, className="mb-0", style={"color": "white", "fontWeight": "600"})
            )
        
        header = html.Div(
            header_content,
            className="d-flex align-items-center p-3",
            style={
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "borderRadius": "28px 28px 0 0"
            }
        )
        
        # Body avec informations dynamiques
        body_items = DynamicCompanyPanel._generate_field_items(
            company_data, field_icons, show_desc, show_contact, show_extra, fields_to_show
        )
        
        body = html.Div(body_items, className="p-3")
        
        return html.Div([header, body], style={**CARD_STYLE, "padding": "0px"})
    
    @staticmethod
    def _render_fallback_panel(company_data: Dict[str, Any]) -> html.Div:
        """Panel de fallback simple si pas de configuration"""
        name = company_data.get('name', 'Entreprise')
        logo_url = company_data.get('logo_url', '')
        
        content = [
            html.H4(name, className="mb-3"),
            html.P("Configuration du panel non trouvée - affichage par défaut", 
                  className="text-muted")
        ]
        
        if logo_url:
            content.insert(0, html.Img(src=logo_url, style={"width": "60px", "height": "60px"}))
        
        return html.Div(content, className="p-3", style=CARD_STYLE)
    
    @staticmethod
    def _generate_field_items(company_data: Dict[str, Any], field_icons: Dict[str, str],
                            show_desc: bool, show_contact: bool, show_extra: bool, 
                            fields_to_show: list, center: bool = False) -> list:
        """Génère les éléments de champs avec icônes dynamiquement"""
        
        items = []
        
        # Mapping des labels français
        field_labels = {
            'name': 'Nom',
            'description': 'Description', 
            'website': 'Site web',
            'contact_email': 'Email',
            'phone': 'Téléphone',
            'address': 'Adresse',
            'employees': 'Employés',
            'revenue': 'Chiffre d\'affaires',
            'founded': 'Fondée en',
            'industry': 'Secteur',
            'status': 'Statut'
        }
        
        # Déterminer quels champs afficher
        if fields_to_show:
            # Utiliser la liste spécifique de la config
            fields_to_process = fields_to_show
        else:
            # Logique par défaut basée sur les flags
            fields_to_process = []
            
            if show_desc and company_data.get('description'):
                fields_to_process.append('description')
            
            if company_data.get('website'):
                fields_to_process.append('website')
            
            if show_contact:
                if company_data.get('contact_email'):
                    fields_to_process.append('contact_email')
                if company_data.get('phone'):
                    fields_to_process.append('phone')
            
            if show_extra:
                extra_fields = ['address', 'employees', 'founded', 'industry', 'status', 'revenue']
                for field in extra_fields:
                    if company_data.get(field):
                        fields_to_process.append(field)
        
        # Générer les éléments HTML pour chaque champ
        for field in fields_to_process:
            value = company_data.get(field)
            if not value:
                continue
            
            icon_class = field_icons.get(field, 'fas fa-info')
            label = field_labels.get(field, field.title())
            
            # Style selon le type de champ
            if field == 'website':
                field_element = html.Div([
                    html.I(className=f"{icon_class} me-2", style={"color": "#667eea", "width": "16px"}),
                    html.A(value, href=value, target="_blank",
                          style={"color": "#667eea", "textDecoration": "none"})
                ], className=f"mb-2 {'text-center' if center else ''}", 
                   style={"fontSize": "0.9rem"})
            
            elif field == 'description':
                field_element = html.Div([
                    html.I(className=f"{icon_class} me-2", style={"color": "#6c757d", "width": "16px"}),
                    html.Span(value)
                ], className=f"mb-2 {'text-center' if center else ''}", 
                   style={"fontSize": "0.9rem", "color": "#6c757d", "lineHeight": "1.5"})
            
            elif field in ['revenue', 'status']:
                # Champs avec style spécial
                color = "#28a745" if field == 'revenue' else "#17a2b8"
                field_element = html.Div([
                    html.I(className=f"{icon_class} me-2", style={"color": color, "width": "16px"}),
                    html.Strong(f"{label}: "),
                    html.Span(value, style={"color": color, "fontWeight": "600"})
                ], className=f"mb-2 {'text-center' if center else ''}", 
                   style={"fontSize": "0.9rem"})
            
            else:
                # Champs standards
                field_element = html.Div([
                    html.I(className=f"{icon_class} me-2", style={"color": "#6c757d", "width": "16px"}),
                    html.Strong(f"{label}: ", style={"color": "#4a5568"}),
                    html.Span(value, style={"color": "#6c757d"})
                ], className=f"mb-2 {'text-center' if center else ''}", 
                   style={"fontSize": "0.9rem"})
            
            items.append(field_element)
        
        return items
