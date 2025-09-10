import sys
import os

# Ajouter le répertoire racine du projet au PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Importer les modules centraux de l'application
from dash_apps.core.app_factory import create_app
from dash_apps.core.auth_manager import setup_authentication
from dash_apps.core.layout_manager import create_main_layout
from dash_apps.core.callbacks import register_callbacks

# Créer l'application Dash et le serveur Flask
app, server = create_app()

# Import des pages APRÈS création de l'app (requis pour dash.register_page)
from dash_apps.pages import map, users

# Configurer l'authentification
login_manager = setup_authentication(server)

# Définir le layout principal
app.layout = create_main_layout()

# Enregistrer tous les callbacks
register_callbacks(app)

# Point d'entrée pour l'exécution
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DASH_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)