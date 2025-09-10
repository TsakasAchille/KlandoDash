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

# Import explicite des callbacks pour forcer leur enregistrement
from dash_apps.callbacks import map_callbacks, users_callbacks, trips_callbacks, support_callbacks, stats_callbacks, admin_callbacks

# Configurer l'authentification
login_manager = setup_authentication(server)

# Définir le layout principal
app.layout = create_main_layout()

# Validation layout pour multi-page apps - inclut tous les layouts des pages
from dash_apps.pages.map import layout as map_layout
from dash_apps.pages.users import layout as users_layout
from dash import html
app.validation_layout = html.Div([
    create_main_layout(),
    map_layout,
    users_layout
])

# Enregistrer tous les callbacks
register_callbacks(app)

# Point d'entrée pour l'exécution
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    debug = os.environ.get("DASH_DEBUG", "False").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)