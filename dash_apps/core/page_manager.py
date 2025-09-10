import os
import importlib.util
import sys
from dash import no_update

# Dictionnaire pour stocker les layouts de page
page_layouts = {}

def load_page_from_file(file_name, page_name):
    """
    Charge une page et retourne son layout
    """
    try:
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pages', file_name)
        
        if not os.path.exists(file_path):
            print(f"[PAGE_MANAGER] Fichier non trouvé: {file_name}")
            return None
            
        # Import dynamique du module
        spec = importlib.util.spec_from_file_location(f"page_{file_name[:-3]}", file_path)
        page_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(page_module)
        
        # Cas spécial pour la page map : importer les callbacks
        if file_name == 'map.py':
            try:
                from dash_apps.callbacks import map_callbacks
                print(f"[PAGE_MANAGER] Map callbacks importés")
            except Exception as e:
                print(f"[PAGE_MANAGER] Erreur import callbacks: {e}")
        
        # Retourner le layout
        return getattr(page_module, 'layout', None)
        
    except Exception as e:
        print(f"[PAGE_MANAGER] Erreur chargement {file_name}: {e}")
        return None

def load_all_pages():
    """
    Charge toutes les pages de l'application
    """
    pages = {
        '/': ('map.py', 'Carte MapLibre'),
        '/map': ('map.py', 'Carte MapLibre'),
        '/users': ('users.py', 'Utilisateurs'),
        '/trips': ('trips.py', 'Trajets'),
        '/stats': ('stats.py', 'Statistiques'),
        '/support': ('support.py', 'Support'),
        '/admin': ('admin.py', 'Administration'),
        '/driver-validation': ('driver_validation.py', 'Validation Documents Conducteur'),
        '/user-profile': ('user_profile.py', 'Profil'),
    }
    
    for route, (filename, title) in pages.items():
        page_layouts[route] = load_page_from_file(filename, title)
    
    return page_layouts

def get_page_layout(pathname):
    """
    Retourne le layout de la page demandée ou None si la page n'existe pas
    """
    return page_layouts.get(pathname)
