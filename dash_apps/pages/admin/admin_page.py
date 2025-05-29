"""Page principale d'administration des utilisateurs"""

from dash import html, dcc, callback, Input, Output, State, ctx, ALL, no_update
import dash_bootstrap_components as dbc
from flask import session, render_template_string
import os
import json

# Chemin vers les templates
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates', 'admin')

# Préfixe pour éviter les conflits de callbacks
ADMIN_PREFIX = 'adm-'

from dash_apps.pages.admin.admin_templates import USER_FORM_TEMPLATE, USER_TABLE_TEMPLATE, ADMIN_JS, ADMIN_LAYOUT

# Layout de la page d'administration
layout = html.Div([
    # Signal que la page est chargu00e9e (pour le callback de vu00e9rification d'authentification)
    html.Div(id=f"{ADMIN_PREFIX}page-loaded", style={"display": "none"}),
    
    # Stores pour les donnu00e9es d'u00e9tat
    dcc.Store(id=f"{ADMIN_PREFIX}auth-store"),
    dcc.Store(id=f"{ADMIN_PREFIX}users-store"),
    dcc.Store(id=f"{ADMIN_PREFIX}toggle-status-result"),
    dcc.Store(id=f"{ADMIN_PREFIX}toggle-role-result"),
    dcc.Store(id=f"{ADMIN_PREFIX}delete-user-result"),
    
    # Message d'erreur pour les utilisateurs non autorisu00e9s
    html.Div(id=f"{ADMIN_PREFIX}auth-check"),
    
    # Contenu principal (rempli par le callback)
    html.Div(id=f"{ADMIN_PREFIX}content", className="container-fluid mt-4"),
])

# Les callbacks sont enregistru00e9s dans admin_callbacks.py
# Les API REST sont configuru00e9es dans admin_api.py

# L'initialisation sera effectuée par le core.page_manager lors du chargement des pages
# Cette approche permet d'éviter les erreurs de contexte d'application
# Pour ce faire, nous allons modifier core/page_manager.py pour qu'il initialise les callbacks et APIs

# Import statique uniquement (pas d'appel de fonctions)
from dash_apps.pages.admin.admin_api import setup_admin_api
from dash_apps.pages.admin.admin_callbacks import register_admin_callbacks

# Fonction d'initialisation qui sera appelée par le page_manager
def init_admin_components(app, server):
    """Initialise les composants d'administration (callbacks et APIs)"""
    try:
        # Configurer les API REST
        setup_admin_api(server)
        
        # Enregistrer les callbacks Dash
        
        print("Administration: Callbacks et APIs initialisés avec succès")
        return True
    except Exception as e:
        print(f"Erreur lors de l'initialisation de l'administration: {str(e)}")
        return False

