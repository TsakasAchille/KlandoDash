import math
import json
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from dash_apps.config import Config
# Import du nouveau composant personnalisé à la place du DataTable
from dash_apps.components.users_table import render_custom_users_table
from dash_apps.components.user_profile import render_user_profile
from dash_apps.components.user_stats import render_user_stats
from dash_apps.components.user_trips import render_user_trips
from dash_apps.components.user_search_widget import render_search_widget, render_active_filters
from dash_apps.utils.layout_config import create_responsive_col
from dash_apps.repositories.repository_factory import RepositoryFactory
from dash_apps.services.redis_cache import redis_cache
from dash_apps.services.users_cache_service import UsersCacheService
from dash_apps.services.user_panels_preloader import UserPanelsPreloader

# L'enregistrement se fera dans app_factory après la création de l'app

# Utiliser la factory pour obtenir le repository approprié
user_repository = RepositoryFactory.get_user_repository()

# Constante pour l'espacement entre les layouts
ROW_SPACING = "mb-4"


# Helper de log standardisé pour tous les callbacks (compatible Python < 3.10)
def log_callback(name, inputs, states=None):
    def _short_str(s):
        try:
            s = str(s)
        except Exception:
            return s
        if len(s) > 14:
            return f"{s[:4]}…{s[-4:]}"
        return s

    def _clean(value):
        # Nettoyage récursif: supprime None, "", et valeurs par défaut "all"
        if isinstance(value, dict):
            cleaned = {}
            for k, v in value.items():
                if v is None or v == "":
                    continue
                if isinstance(v, str) and v == "all":
                    continue
                # Flatten pour selected_user
                if k in ("selected_user", "selected_user_uid") and isinstance(v, dict) and "uid" in v:
                    cleaned["selected_uid"] = _short_str(v.get("uid"))
                    continue
                cleaned[k] = _clean(v)
            return cleaned
        if isinstance(value, list):
            return [_clean(v) for v in value if v is not None and v != ""]
        if isinstance(value, str):
            return _short_str(value)
        return value

    def _kv_lines(dct):
        if not dct:
            return ["  (none)"]
        lines = []
        for k, v in dct.items():
            try:
                if isinstance(v, (dict, list)):
                    v_str = json.dumps(v, ensure_ascii=False)
                else:
                    v_str = str(v)
            except Exception:
                v_str = str(v)
            lines.append(f"  - {k}: {v_str}")
        return lines

    try:
        c_inputs = _clean(inputs)
        c_states = _clean(states or {})
        sep = "=" * 74
        print("\n" + sep)
        print(f"[CB] {name}")
        print("Inputs:")
        for line in _kv_lines(c_inputs):
            print(line)
        print("States:")
        for line in _kv_lines(c_states):
            print(line)
        print(sep)
    except Exception:
        sep = "=" * 74
        print("\n" + sep)
        print(f"[CB] {name}")
        print(f"Inputs: {inputs}")
        print(f"States: {states or {}}")
        print(sep)


def find_user_page_index(uid, page_size):
    """Trouve l'index de page sur lequel se trouve l'utilisateur avec l'UID donné
    
    Args:
        uid: UID de l'utilisateur à trouver
        page_size: Taille de chaque page
        
    Returns:
        Index de la page (0-based) ou None si non trouvé
    """
    try:
        position = user_repository.get_user_position(uid)
        if position is not None:
            page_index = position // page_size
            return page_index
        return None
    except Exception as e:
        print(f"[ERROR] Erreur lors de la recherche de l'utilisateur {uid}: {e}")
        return None


# Helper: rendre JSON-serializable (datetime -> isoformat, Pydantic -> dict)
def _to_jsonable(obj):
    """Convertit récursivement un objet en structure JSON-serializable.
    - datetime/date -> isoformat()
    - Pydantic v2 -> model_dump()
    - Pydantic v1 -> dict()
    - Decimal -> float
    - set -> list
    - objets inconnus -> str(obj)
    """
    try:
        import datetime as _dt
        import decimal as _dec
    except Exception:
        pass

    # Déballer Pydantic models
    if hasattr(obj, "model_dump") and callable(getattr(obj, "model_dump")):
        try:
            obj = obj.model_dump()
        except Exception:
            obj = dict(obj)
    elif hasattr(obj, "dict") and callable(getattr(obj, "dict")) and not isinstance(obj, dict):
        try:
            obj = obj.dict()
        except Exception:
            try:
                obj = dict(obj)
            except Exception:
                obj = str(obj)

    # Types simples
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # datetime/date
    try:
        import datetime as _dt2
        if isinstance(obj, (_dt2.datetime, _dt2.date)):
            return obj.isoformat()
    except Exception:
        pass

    # Decimal
    try:
        import decimal as _dec2
        if isinstance(obj, _dec2.Decimal):
            return float(obj)
    except Exception:
        pass

    # list/tuple
    if isinstance(obj, (list, tuple, set)):
        return [_to_jsonable(v) for v in list(obj)]

    # dict
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}

    # fallback
    try:
        return str(obj)
    except Exception:
        return None



def get_layout():
    """Génère le layout de la page utilisateurs avec des IDs uniquement pour cette page"""
    return dbc.Container([
    dcc.Location(id="users-url", refresh=False),
    #dcc.Store(id="users-pagination-info", data={"page_count": 1, "total_users": 0}),
    dcc.Store(id="users-current-page", storage_type="session", data=1),  # State pour stocker la page courante (persistant)
    dcc.Store(id="selected-user-uid", storage_type="session", data=None, clear_data=False),  # Store pour l'UID de l'utilisateur sélectionné (persistant)
    dcc.Store(id="selected-users-store", storage_type="session", data=[]),  # UIDs des utilisateurs sélectionnés avec cases à cocher
    # Cache session pour éviter les rechargements inutiles (clé = page + filtres)
    dcc.Store(id="users-page-cache", storage_type="session", data={}, clear_data=False),
    # Store session pour précharger les données nécessaires aux panneaux (profil, stats, aperçus trajets)
    dcc.Store(id="users-panels-store", storage_type="session", data={}, clear_data=False),
    dcc.Store(id="url-parameters", storage_type="memory", data=None),  # Store temporaire pour les paramètres d'URL
    dcc.Store(id="selected-user-from-url", storage_type="memory", data=None),  # State pour la sélection depuis l'URL
    dcc.Store(id="users-filter-store", storage_type="session", data={}, clear_data=False),  # Store pour les filtres de recherche
    # Interval pour déclencher la lecture des paramètres d'URL au chargement initial (astuce pour garantir l'exécution)
    dcc.Interval(id='url-init-trigger', interval=100, max_intervals=1),  # Exécute une seule fois au chargement
  
    html.H2("Dashboard utilisateurs", style={"marginTop": "20px"}),
    dbc.Row([
        dbc.Col([], width=9),
        dbc.Col([
            dbc.Button("🔄 Rafraîchir les données", id="refresh-users-btn", color="primary", className="mb-2")
        ], width=3)
    ]),
    html.Div(id="refresh-users-message"),
    # Widget de recherche
    render_search_widget(),
    # Affichage des filtres actifs
    html.Div(id="users-active-filters"),
    dbc.Row([
        dbc.Col([
            # Conteneur vide qui sera rempli par le callback render_users_table_callback
            html.Div(id="main-users-content")
        ], width=12)
    ]),
    dbc.Row([
        create_responsive_col(
            "user_details_panel",
            [
                # Header avec titre et icône
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-user-circle me-2", style={"color": "#007bff"}),
                        html.H5("Détails de l'utilisateur", className="mb-0", style={"color": "#333"})
                    ], style={"background-color": "#f8f9fa", "border-bottom": "2px solid #007bff"}),
                    dbc.CardBody([
                        dcc.Loading(
                            children=html.Div(id="user-details-panel"),
                            type="default"
                        )
                    ], style={"padding": "0"})
                ], style={"border": "1px solid #dee2e6", "border-radius": "8px"})
            ],
            config_file="user_details_config.json"
        ),
        create_responsive_col(
            "user_stats_panel",
            [
                # Header avec titre et icône
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-chart-bar me-2", style={"color": "#28a745"}),
                        html.H5("Statistiques", className="mb-0", style={"color": "#333"})
                    ], style={"background-color": "#f8f9fa", "border-bottom": "2px solid #28a745"}),
                    dbc.CardBody([
                        dcc.Loading(
                            children=html.Div(id="user-stats-panel"),
                            type="default"
                        )
                    ], style={"padding": "0"})
                ], style={"border": "1px solid #dee2e6", "border-radius": "8px"})
            ],
            config_file="user_details_config.json"
        ),
    ], className=ROW_SPACING),
    dbc.Row([
        create_responsive_col(
            "user_trips_panel",
            [
                # Header avec titre et icône
                dbc.Card([
                    dbc.CardHeader([
                        html.I(className="fas fa-route me-2", style={"color": "#17a2b8"}),
                        html.H5("Trajets de l'utilisateur", className="mb-0", style={"color": "#333"})
                    ], style={"background-color": "#f8f9fa", "border-bottom": "2px solid #17a2b8"}),
                    dbc.CardBody([
                        dcc.Loading(
                            children=html.Div(id="user-trips-panel"),
                            type="default"
                        )
                    ], style={"padding": "0"})
                ], style={"border": "1px solid #dee2e6", "border-radius": "8px"})
            ],
            config_file="user_details_config.json"
        ),
    ], className=ROW_SPACING)
], fluid=True)



# Note: Le store users-page-store n'est plus utilisé pour stocker tous les utilisateurs
# car nous utilisons maintenant un chargement à la demande page par page

# Les callbacks sont maintenant dans callbacks/users_callbacks.py
from dash_apps.callbacks import users_callbacks



layout = get_layout()
