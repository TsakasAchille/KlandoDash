"""
Utilitaires pour la gestion des configurations de layout Dash
"""

from dash_apps.utils.settings import load_json_config
from typing import Dict, Any, Optional

def get_panel_layout_config(config_file: str = 'trip_details_config.json') -> Dict[str, Any]:
    """
    Charge la configuration de layout des panneaux depuis un fichier JSON
    
    Args:
        config_file: Nom du fichier de configuration
        
    Returns:
        Dict contenant la configuration des panneaux
    """
    try:
        config = load_json_config(config_file)
        
        # Déterminer la clé racine selon le fichier de config
        if 'trip_driver_config.json' in config_file:
            return config.get('trip_driver', {}).get('bootstrap_layout', {})
        elif 'trip_stats_display_config.json' in config_file:
            return config.get('trip_stats', {}).get('dash_layout', {})
        elif 'trip_details_config.json' in config_file:
            return config.get('trip_details', {}).get('bootstrap_layout', {})
        else:
            # Par défaut pour trip_details_config.json
            return config.get('trip_details', {}).get('dash_layout', {})
    except Exception as e:
        print(f"Erreur lors du chargement de la config layout: {e}")
        return {}

def get_panel_width(panel_name: str, config_file: str = 'trip_details_config.json') -> int:
    """
    Récupère la largeur d'un panneau spécifique
    
    Args:
        panel_name: Nom du panneau (ex: 'trip_details_panel')
        config_file: Fichier de configuration
        
    Returns:
        Largeur du panneau (défaut: 12)
    """
    layout_config = get_panel_layout_config(config_file)
    panel_config = layout_config.get(panel_name, {})
    width = panel_config.get('width', 12)
    
    # Debug pour trip_driver_panel
    if panel_name == 'trip_driver_panel':
        print(f"🔧 DEBUG layout_config.py:")
        print(f"   - config_file: {config_file}")
        print(f"   - panel_name: {panel_name}")
        print(f"   - layout_config: {layout_config}")
        print(f"   - panel_config: {panel_config}")
        print(f"   - width: {width}")
    
    return width

def get_responsive_widths(panel_name: str, config_file: str = 'trip_details_config.json') -> Dict[str, int]:
    """
    Récupère les largeurs responsives d'un panneau
    
    Args:
        panel_name: Nom du panneau
        config_file: Fichier de configuration
        
    Returns:
        Dict avec les breakpoints responsive
    """
    layout_config = get_panel_layout_config(config_file)
    panel_config = layout_config.get(panel_name, {})
    return panel_config.get('responsive', {
        'xs': 12, 'sm': 12, 'md': 12, 'lg': 12, 'xl': 12
    })

def create_responsive_col(panel_name: str, children, config_file: str = 'trip_details_config.json'):
    """
    Crée une colonne Bootstrap avec largeurs configurables
    
    Args:
        panel_name: Nom du panneau dans la config
        children: Contenu de la colonne
        config_file: Fichier de configuration
        
    Returns:
        dbc.Col avec largeurs configurées
    """
    import dash_bootstrap_components as dbc
    
    width = get_panel_width(panel_name, config_file)
    responsive = get_responsive_widths(panel_name, config_file)
    
    return dbc.Col(
        children,
        width=width,
        xs=responsive.get('xs', 12),
        sm=responsive.get('sm', 12), 
        md=responsive.get('md', width),
        lg=responsive.get('lg', width),
        xl=responsive.get('xl', width)
    )
