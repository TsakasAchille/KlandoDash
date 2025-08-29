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
    print(f"[PAGE_MANAGER] Tentative de chargement de la page: {page_name} (fichier: {file_name})")
    try:
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pages', file_name)
        print(f"[PAGE_MANAGER] Chemin résolu: {file_path}")
        if not os.path.exists(file_path):
            print(f"[PAGE_MANAGER][ERREUR] Fichier non trouvé: {file_path}")
            return None
        module_name = f"page_{file_name.replace('.py', '')}_module"
        print(f"[PAGE_MANAGER] Nom du module importé: {module_name}")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        page_module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = page_module
        try:
            spec.loader.exec_module(page_module)
            print(f"[PAGE_MANAGER] Module {module_name} exécuté avec succès.")
        except Exception as import_exc:
            print(f"[PAGE_MANAGER][ERREUR IMPORT] Exception lors de l'import de {file_name}: {import_exc}")
            import traceback
            traceback.print_exc()
            return None
        if hasattr(page_module, 'layout'):
            print(f"[PAGE_MANAGER][SUCCÈS] Layout trouvé pour {page_name} ({file_name})")
            return page_module.layout
        else:
            print(f"[PAGE_MANAGER][ERREUR] Pas de layout dans {file_name}")
            return None
    except Exception as e:
        print(f"[PAGE_MANAGER][ERREUR GLOBALE] Exception lors du chargement de {file_name}: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_all_pages():
    """
    Charge toutes les pages de l'application
    """
    # Page d'utilisateurs
    page_layouts['/users'] = load_page_from_file('01_users.py', 'Utilisateurs')

    # Page des trajets
    page_layouts['/trips'] = load_page_from_file('02_trips.py', 'Trajets')

    # Page de statistiques
    page_layouts['/stats'] = load_page_from_file('03_stats.py', 'Statistiques')

    # Page de support
    page_layouts['/support'] = load_page_from_file('04_support.py', 'Support')

    # Page d'administration
    page_layouts['/admin'] = load_page_from_file('05_admin.py', 'Administration')
    
    # Page de validation des documents conducteur
    page_layouts['/driver-validation'] = load_page_from_file('06_driver_validation.py', 'Validation Documents Conducteur')
    
    # Page de profil utilisateur
    page_layouts['/user-profile'] = load_page_from_file('05_user_profile.py', 'Profil')

    # Page principale: la page trajets
   # page_layouts['/'] = load_page_from_file('trips.py', 'Accueil/Trajets')
    #page_layouts['/trips'] = page_layouts['/']
    
    return page_layouts

def get_page_layout(pathname):
    """
    Retourne le layout de la page demandée ou None si la page n'existe pas
    """
    return page_layouts.get(pathname)
