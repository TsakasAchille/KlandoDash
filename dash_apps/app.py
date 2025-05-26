import sys
import os

# Ajouter le répertoire racine du projet au PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Importer les modules centraux de l'application
from dash_apps.core.app_factory import create_app
from dash_apps.core.auth_manager import setup_authentication
from dash_apps.core.layout_manager import create_main_layout
from dash_apps.core.page_manager import load_all_pages
from dash_apps.core.callbacks import register_callbacks

# Créer l'application Dash et le serveur Flask
app, server = create_app()

# Configurer l'authentification
login_manager = setup_authentication(server)

# Définir le layout principal
app.layout = create_main_layout()

# Charger toutes les pages
page_layouts = load_all_pages()

# Enregistrer tous les callbacks
register_callbacks(app)

# Point d'entrée pour l'exécution
if __name__ == "__main__":
    app.run(debug=True)