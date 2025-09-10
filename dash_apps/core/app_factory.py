import sys
import os
import logging
from dash import Dash
import dash_bootstrap_components as dbc
from flask_session import Session
from flask_login import LoginManager

from dash_apps.config import Config
from dash_apps.auth.routes import auth_bp
from dash_apps.core.proxy import proxy_bp
from dash_apps.api.support_api import support_api_bp
from dash_apps.api.email_webhook import email_webhook_bp
from dash_apps.core.page_manager import load_all_pages
from flask import render_template, request

def create_app():
    """
    Crée et configure l'application Dash et le serveur Flask sous-jacent
    """
    # Configuration de base pour Dash avec Pages
    app = Dash(
        __name__, 
        use_pages=True,
        pages_folder="",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
            "https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css"
        ],
        external_scripts=[],
        suppress_callback_exceptions=True,
        url_base_pathname='/',
        assets_folder=os.path.join(os.path.dirname(__file__), 'assets')
    )
    server = app.server

    # Configuration du serveur Flask sous-jacent
    server.config['SECRET_KEY'] = Config.SECRET_KEY
    server.config['SESSION_TYPE'] = 'filesystem'
    server.config['SESSION_PERMANENT'] = True
    # Assure le dossier de templates: dash_apps/templates
    try:
        server.template_folder = os.path.join(os.path.dirname(__file__), '..', 'templates')
    except Exception:
        pass

    # Initialiser Flask-Session
    Session(server)
    
    # Enregistrer le blueprint d'authentification
    server.register_blueprint(auth_bp, url_prefix='/auth')
    # Enregistrer le blueprint proxy (CORS bypass pour MapLibre)
    server.register_blueprint(proxy_bp, url_prefix='/proxy')
    # Enregistrer le blueprint API support (pour N8N)
    server.register_blueprint(support_api_bp)
    # Enregistrer le blueprint webhook email
    server.register_blueprint(email_webhook_bp)

    # Enregistrer les pages manuellement après la création de l'app
    import dash
    
    # Importer et enregistrer chaque page (sauf admin et driver_validation qui sont gérées séparément)
    from dash_apps.pages import map, users, trips, stats, support, admin, driver_validation
    
    dash.register_page("home", path='/', layout=map.layout, name='Carte')
    dash.register_page("users", path='/users', layout=users.layout, name='Utilisateurs')
    dash.register_page("trips", path='/trips', layout=trips.layout, name='Trajets')
    dash.register_page("stats", path='/stats', layout=stats.layout, name='Statistiques')
    dash.register_page("support", path='/support', layout=support.layout, name='Support')
    
    # Pages admin enregistrées sans être dans le registre public (pas de name pour éviter l'affichage automatique)
    dash.register_page("admin", path='/admin', layout=admin.layout)
    dash.register_page("driver_validation", path='/driver-validation', layout=driver_validation.serve_layout)


    # --- Logging configuration ---
    try:
        # Ensure Flask logger propagates to Gunicorn and set level from env or default to INFO
        log_level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
        log_level = getattr(logging, log_level_name, logging.INFO)
        server.logger.setLevel(log_level)
        # If no handlers (e.g., in some envs), add a stream handler
        if not server.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(log_level)
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
            handler.setFormatter(formatter)
            server.logger.addHandler(handler)
        # Also set Dash's logger
        app.logger.setLevel(log_level)
    except Exception as e:
        server.logger.warning("[APP_FACTORY][LOGGING] Failed to configure logging: %s", e)

    # Log URL map (routes) at startup
    try:
        routes_dump = []
        for rule in server.url_map.iter_rules():
            routes_dump.append(f"{rule.methods} -> {rule.rule} -> {rule.endpoint}")
        server.logger.info("[ROUTES] Registered routes (count=%d):\n%s", len(routes_dump), "\n".join(sorted(routes_dump)))
    except Exception as e:
        server.logger.warning("[ROUTES] Failed to dump url_map: %s", e)

  
    @server.after_request
    def _log_response(resp):
        try:
            server.logger.debug("[RESPONSE] %s %s -> %s", request.method, request.path, resp.status)
        except Exception:
            pass
        return resp

    # Error handler for 404 to log missing paths
    @server.errorhandler(404)
    def _handle_404(e):
        try:
            server.logger.warning("[404] Path not found: %s (referrer=%s)", request.path, request.referrer)
        except Exception:
            pass
        # Let Dash render its own 404 inside the app content when applicable
        return e, 404

    # Endpoint pour rendre le popup trajet (Jinja)
    @server.route('/popup/trip', methods=['POST'])
    def render_trip_popup():
        try:
            data = request.get_json(force=True) or {}
        except Exception:
            data = {}
        # Champs attendus (tolérance aux manquants)
        ctx = {
            'driver_name': data.get('driver_name') or 'Conducteur',
            'departure_name': data.get('departure_name') or '-',
            'destination_name': data.get('destination_name') or '-',
            'passenger_price': data.get('passenger_price'),
            'seats_booked': data.get('seats_booked'),
            'seats_available': data.get('seats_available'),
            'driver_avatar_url': data.get('driver_avatar_url') or '',
            'trip_id': data.get('trip_id') or '',
            'driver_id': data.get('driver_id') or '',
        }
        return render_template('popup_trip.jinja2', **ctx)

    return app, server
