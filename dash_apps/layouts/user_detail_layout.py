"""
Layout pour les détails d'utilisateur
Responsable du rendu HTML des panels de détails utilisateur
"""
from typing import Dict, Any
from dash import html
import dash_bootstrap_components as dbc
from dash_apps.utils.settings import load_json_config


class UserDetailLayout:
    """Classe responsable du rendu des layouts de détails utilisateur"""
    
    @staticmethod
    def _load_config() -> Dict[str, Any]:
        """Charge la configuration JSON des détails utilisateur"""
        try:
            config = load_json_config('user_details.json')
            print(f"🔧 [CONFIG_DEBUG] Config chargée: {list(config.keys())}")
            if 'user_details' in config and 'fields' in config['user_details']:
                print(f"🔧 [CONFIG_DEBUG] Fields trouvés: {list(config['user_details']['fields'].keys())}")
            if 'user_details' in config and 'rendering' in config['user_details']:
                print(f"🔧 [CONFIG_DEBUG] Rendering trouvé: {list(config['user_details']['rendering'].keys())}")
            return config
        except Exception as e:
            print(f"❌ Erreur lors du chargement de la config: {e}")
            return {}
    
    @staticmethod
    def render_user_details_layout(user_id: str, data: Dict[str, Any]) -> html.Div:
        """Génère le layout HTML dynamiquement selon la configuration JSON"""
        config = UserDetailLayout._load_config()
        user_details_config = config.get('user_details', {})
        fields_config = user_details_config.get('fields', {})
        rendering_config = user_details_config.get('rendering', {})
        
        sections = []
        
        # Générer les sections selon la configuration
        for section_config in rendering_config.get('sections', []):
            section_title = section_config.get('title', 'Section')
            section_fields = section_config.get('fields', [])
            
            section_items = []
            
            for field_name in section_fields:
                # Trouver la configuration du champ dans tous les groupes
                field_config = None
                for group_name, group_fields in fields_config.items():
                    if field_name in group_fields:
                        field_config = group_fields[field_name]
                        break
                
                if not field_config:
                    continue
                
                # Récupérer la valeur depuis les données
                field_value = data.get(field_name, 'N/A')
                field_label = field_config.get('label', field_name)
                field_type = field_config.get('type', 'string')
                
                # Formater la valeur selon le type
                formatted_value = UserDetailLayout._format_field_value(field_value, field_config)
                
                section_items.append(
                    dbc.Row([
                        dbc.Col([
                            html.Strong(f"{field_label}:", className="text-muted")
                        ], width=4),
                        dbc.Col([
                            html.Span(formatted_value)
                        ], width=8)
                    ], className="mb-2")
                )
            
            if section_items:
                sections.append(
                    dbc.Card([
                        dbc.CardHeader([
                            html.H5(section_title, className="mb-0")
                        ]),
                        dbc.CardBody(section_items)
                    ], className="mb-3")
                )
        
        return html.Div([
            html.H4("Détails de l'utilisateur", className="mb-3"),
            html.Div(sections)
        ], className="user-details-panel")
    
    @staticmethod
    def _format_field_value(value: Any, field_config: Dict[str, Any]) -> str:
        """Formate une valeur selon sa configuration"""
        if value is None or value == '':
            return 'N/A'
        
        field_type = field_config.get('type', 'string')
        
        if field_type == 'datetime':
            try:
                from datetime import datetime
                if isinstance(value, str):
                    # Essayer de parser la date
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    format_str = field_config.get('format', 'DD/MM/YYYY HH:mm')
                    if format_str == 'DD/MM/YYYY HH:mm':
                        return dt.strftime('%d/%m/%Y %H:%M')
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                return str(value)
            except Exception:
                return str(value)
        
        elif field_type == 'enum':
            values_map = field_config.get('values', {})
            return values_map.get(str(value), str(value))
        
        elif field_type == 'phone':
            # Formater le numéro de téléphone
            phone_str = str(value)
            if len(phone_str) >= 8:
                return f"{phone_str[:2]} {phone_str[2:4]} {phone_str[4:6]} {phone_str[6:]}"
            return phone_str
        
        elif field_type == 'email':
            # Masquer partiellement l'email pour la confidentialité
            email_str = str(value)
            if '@' in email_str:
                local, domain = email_str.split('@', 1)
                if len(local) > 3:
                    masked_local = local[:2] + '*' * (len(local) - 3) + local[-1]
                    return f"{masked_local}@{domain}"
            return email_str
        
        elif field_type == 'rating':
            try:
                rating_value = float(value)
                stars = '⭐' * int(rating_value)
                return f"{stars} ({rating_value:.1f}/5.0)"
            except (ValueError, TypeError):
                return str(value)
        
        elif field_type == 'boolean':
            return '✅ Oui' if value else '❌ Non'
        
        return str(value)
    
    @staticmethod
    def render_user_details_panel(user_id: str, data: Dict[str, Any]) -> html.Div:
        """Point d'entrée principal pour le rendu du panel de détails utilisateur"""
        return UserDetailLayout.render_user_details_layout(user_id, data)
    
    @staticmethod
    def render_error_panel(error_message: str, error_type: str = "danger") -> html.Div:
        """Génère un panel d'erreur standardisé"""
        return html.Div([
            dbc.Alert([
                html.H5("Erreur lors du chargement des détails", className="alert-heading"),
                html.P(error_message),
                html.Hr(),
                html.P("Vérifiez l'ID de l'utilisateur ou contactez l'administrateur.", className="mb-0")
            ], color=error_type)
        ])
