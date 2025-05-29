import os
import importlib.util
import sys
from dash import no_update

# Dictionnaire pour stocker les layouts de page
page_layouts = {}

def load_page_from_file(file_name, page_name):
    """
    Charge une page à partir d'un fichier Python et retourne son layout
    """
    try:
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pages', file_name)
        if not os.path.exists(file_path):
            print(f"Fichier non trouvé: {file_path}")
            return None
            
        # Définir un nom de module unique
        module_name = f"page_{file_name.replace('.py', '')}_module"
        
        # Charger le module via spec_from_file_location
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        page_module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = page_module
        spec.loader.exec_module(page_module)
        
        # Vérifier si le layout existe
        if hasattr(page_module, 'layout'):
            print(f"Page chargée: {page_name} ({file_name})")
            return page_module.layout
        else:
            print(f"Pas de layout dans {file_name}")
            return None
    except Exception as e:
        print(f"Erreur de chargement de {file_name}: {str(e)}")
        return None

def load_all_pages():
    """
    Charge toutes les pages de l'application
    """
    # Page d'utilisateurs
    page_layouts['/users'] = load_page_from_file('01_users.py', 'Utilisateurs')

    # Page de statistiques
    page_layouts['/stats'] = load_page_from_file('03_stats.py', 'Statistiques')

    # Page de support
    page_layouts['/support'] = load_page_from_file('04_support.py', 'Support')

    # Pages d'administration
    page_layouts['/admin'] = load_page_from_file('05_admin.py', 'Administration')
    
    # Page de validation des documents conducteur
    try:
        driver_validation_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pages', 'admin', 'driver_validation.py')
        spec = importlib.util.spec_from_file_location('driver_validation_module', driver_validation_path)
        driver_validation_module = importlib.util.module_from_spec(spec)
        sys.modules['driver_validation_module'] = driver_validation_module
        spec.loader.exec_module(driver_validation_module)
        
        if hasattr(driver_validation_module, 'layout'):
            print("Page chargée: Validation Documents Conducteur (admin/driver_validation.py)")
            page_layouts['/admin/driver-validation'] = driver_validation_module.layout
        else:
            print("Pas de layout dans admin/driver_validation.py")
    except Exception as e:
        print(f"Erreur de chargement de admin/driver_validation.py: {str(e)}")

    # Page de profil utilisateur
    page_layouts['/user-profile'] = load_page_from_file('05_user_profile.py', 'Profil')

    # Page principale: la page trajets
    page_layouts['/'] = load_page_from_file('02_trips.py', 'Accueil/Trajets')
    page_layouts['/trips'] = page_layouts['/']
    
    return page_layouts

def get_page_layout(pathname):
    """
    Retourne le layout de la page demandée ou None si la page n'existe pas
    """
    return page_layouts.get(pathname)
