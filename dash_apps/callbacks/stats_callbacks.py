import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

# Importer les composants avec templates Jinja2
from dash_apps.components.stats_general import render_stats_general
from dash_apps.components.stats_temporal import render_stats_temporal
from dash_apps.components.stats_geographic import render_stats_geographic
from dash_apps.components.stats_financial import render_stats_financial


# Callback pour charger automatiquement les données au chargement de la page
@callback(
    Output("stats-trips-store", "data"),
    Input("stats-refresh-btn", "n_clicks"),
    # Force le chargement automatique au démarrage
    prevent_initial_call=False
)
def load_stats_data(n_clicks):
    """Charge les données des trajets pour les statistiques"""
    # Indiquer dans les logs qu'on essaie de charger les données
    print(f"[DEBUG] Tentative de chargement des données... (n_clicks={n_clicks})")
    try:
        # Obtenir les données de trajet du processeur
        from dash_apps.utils.trip_data import get_trip_data
        trips_df = get_trip_data()
        
        # Vérifier si les données ont été chargées correctement
        if trips_df is None or trips_df.empty:
            print("Aucune donnée de trajet n'a été trouvée.")
            return None
            
        # Convertir en dict pour stockage
        trips_data = trips_df.to_dict("records")
        
        # Données chargées avec succès
        print(f"[DEBUG] Données chargées avec succès ! ({len(trips_data)} enregistrements)")
        return trips_data
    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")
        # Ne retourner que None en cas d'erreur
        return None


@callback(
    Output("stats-general-container", "children"),
    Input("stats-trips-store", "data")
)
def update_stats_general(trips_data):
    print(f"[DEBUG] Mise à jour des statistiques générales avec {len(trips_data) if trips_data else 0} enregistrements")
    return render_stats_general(trips_data)


@callback(
    Output("stats-temporal-container", "children"),
    Input("stats-trips-store", "data")
)
def update_stats_temporal(trips_data):
    print(f"[DEBUG] Mise à jour des statistiques temporelles avec {len(trips_data) if trips_data else 0} enregistrements")
    return render_stats_temporal(trips_data)


@callback(
    Output("stats-geographic-container", "children"),
    Input("stats-trips-store", "data")
)
def update_stats_geographic(trips_data):
    print("[DEBUG] Mise à jour des statistiques géographiques avec", len(trips_data) if trips_data else 0, "enregistrements")
    return render_stats_geographic(trips_data)


@callback(
    Output("stats-financial-container", "children"),
    Input("stats-trips-store", "data")
)
def update_stats_financial(trips_data):
    print("[DEBUG] Mise à jour des statistiques financières avec", len(trips_data) if trips_data else 0, "enregistrements")
    return render_stats_financial(trips_data)
