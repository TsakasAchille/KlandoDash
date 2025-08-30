import sys
import os
from dash import Dash
import dash_bootstrap_components as dbc
from flask_session import Session
from flask_login import LoginManager

from dash_apps.config import Config
from dash_apps.auth.routes import auth_bp
from dash_apps.core.proxy import proxy_bp
from flask import render_template, request

def create_app():
    """
    Crée et configure l'application Dash et le serveur Flask sous-jacent
    """
    # Configuration de base pour Dash
    app = Dash(
        __name__, 
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
            # MapLibre GL CSS
            'https://unpkg.com/maplibre-gl@3.6.1/dist/maplibre-gl.css',
        ],
        external_scripts=[
            # MapLibre GL JS
            'https://unpkg.com/maplibre-gl@3.6.1/dist/maplibre-gl.js',
        ],
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
