import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def render_stats_financial(trips_data):
    """
    Rend les statistiques financières des trajets en utilisant un template Jinja2
    
    Args:
        trips_data: Données des trajets sous forme de liste de dictionnaires
    
    Returns:
        Un composant Dash pour afficher les statistiques financières
    """
    if not trips_data:
        return dbc.Alert("Aucune donnée de trajet disponible", color="warning")
    
    # Convertir en DataFrame
    trips_df = pd.DataFrame(trips_data)
    
    # Vérifier si les colonnes financières sont disponibles
    has_price_data = 'passenger_price' in trips_df.columns
    has_driver_price_data = 'driver_price' in trips_df.columns
    has_viator_data = False  # Pas de données Viator pour l'instant
    
    if not has_price_data and not has_viator_data:
        return dbc.Alert("Données financières insuffisantes pour l'analyse", color="warning")
    
    # Calculer les métriques financières
    avg_passenger_price = trips_df['passenger_price'].mean() if 'passenger_price' in trips_df.columns else 0
    total_passenger_price = trips_df['passenger_price'].sum() if 'passenger_price' in trips_df.columns else 0
    
    # Calculer les métriques du prix conducteur si disponibles
    avg_driver_price = trips_df['driver_price'].mean() if 'driver_price' in trips_df.columns else 0
    total_driver_price = trips_df['driver_price'].sum() if 'driver_price' in trips_df.columns else 0
    
    # Calculer le prix par kilomètre si les deux colonnes sont disponibles
    if 'passenger_price' in trips_df.columns and 'distance' in trips_df.columns:
        # Éviter la division par zéro
        valid_trips = trips_df[trips_df['distance'] > 0]
        if not valid_trips.empty:
            price_per_km = valid_trips['passenger_price'] / valid_trips['distance']
            avg_price_per_km = price_per_km.mean()
        else:
            avg_price_per_km = 0
    else:
        avg_price_per_km = 0
        
    # Créer les graphiques et les convertir en dictionnaires pour les rendre JSON-sérialisables
    import numpy as np
    import json
    
    class NumpyJSONEncoder(json.JSONEncoder):
        """Classe pour encoder les objets NumPy en JSON."""
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.bool_):
                return bool(obj)
            return super().default(obj)
    
    def fig_to_dict(fig):
        if fig is None:
            return None
            
        # Convertir la figure en dictionnaire
        fig_dict = {
            'data': [trace.to_plotly_json() for trace in fig.data],
            'layout': fig.layout.to_plotly_json()
        }
        
        # Utiliser notre encodeur personnalisé pour sérialiser/désérialiser
        # Cela convertira tous les tableaux NumPy en listes Python
        fig_json = json.dumps(fig_dict, cls=NumpyJSONEncoder)
        return json.loads(fig_json)
    
    price_distribution = fig_to_dict(create_price_distribution(trips_df)) if has_price_data else None
    driver_price_distribution = fig_to_dict(create_driver_price_distribution(trips_df)) if has_driver_price_data else None
    price_distance = fig_to_dict(create_price_vs_distance(trips_df)) if has_price_data and 'distance' in trips_df.columns else None
    income_time = fig_to_dict(create_income_time_series(trips_df)) if has_price_data and 'departure_date' in trips_df.columns else None
    
    # Préparer les données pour le template
    context = {
        "avg_price": avg_passenger_price,
        "total_price": total_passenger_price,
        "avg_price_per_km": avg_price_per_km,
        "avg_driver_price": avg_driver_price,
        "total_driver_price": total_driver_price,
        "price_distribution": price_distribution,
        "driver_price_distribution": driver_price_distribution,
        "price_distance": price_distance,
        "income_time": income_time,
        "viator_distribution": None  # Ajouter viator_distribution avec une valeur None
    }
    
    # Rendre le template
    import jinja2
    import os
    
    # Configurer Jinja2
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template('stats_financial_template.jinja2')
    
    # Rendre le template avec le contexte
    html_content = template.render(**context)
    
    # Créer un composant iframe pour afficher le HTML
    return html.Iframe(
        srcDoc=html_content,
        style={
            'width': '100%', 
            'height': '1200px',  # Adapter la hauteur selon les besoins
            'border': 'none',
        }
    )
    
    


def create_price_distribution(trips_df):
    """
    Cree un graphique de distribution des prix par place
    
    Args:
        trips_df: DataFrame contenant les donnes des trajets
    
    Returns:
        Un objet Figure de Plotly
    """
    if 'passenger_price' in trips_df.columns:
        fig = px.histogram(trips_df, x="passenger_price", nbins=20, 
                         labels={"passenger_price": "Prix passager (XOF)"},
                         title="Distribution des prix passagers",
                         color_discrete_sequence=['#f39c12'])
        
        # Ameliorer le style du graphique
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        return fig
    else:
        # Graphique vide si les donnes ne sont pas disponibles
        return go.Figure()


def create_driver_price_distribution(trips_df):
    """
    Cree un graphique de distribution des prix conducteur
    
    Args:
        trips_df: DataFrame contenant les donnes des trajets
    
    Returns:
        Un objet Figure de Plotly
    """
    if 'driver_price' in trips_df.columns:
        fig = px.histogram(trips_df, x="driver_price", nbins=20, 
                         labels={"driver_price": "Prix conducteur (XOF)"},
                         title="Distribution des prix conducteurs",
                         color_discrete_sequence=['#3366CC'])
        
        # Ameliorer le style du graphique
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        return fig
    else:
        # Graphique vide si les donnes ne sont pas disponibles
        return go.Figure()


def create_price_vs_distance(trips_df):
    """
    Cree un graphique montrant la relation entre prix et distance
    
    Args:
        trips_df: DataFrame contenant les donnes des trajets
    
    Returns:
        Un objet Figure de Plotly
    """
    if 'passenger_price' in trips_df.columns and 'distance' in trips_df.columns:
        fig = px.scatter(trips_df, x="distance", y="passenger_price", 
                       labels={"distance": "Distance (km)", "passenger_price": "Prix passager (XOF)"},
                       title="Relation entre prix passager et distance",
                       color_discrete_sequence=['#f39c12'])
        
        # Ameliorer le style du graphique
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        # Ajouter une ligne de tendance
        fig.update_traces(mode='markers')
        
        try:
            # Verifier qu'il y a suffisamment de donnes valides pour calculer une tendance
            valid_data = trips_df.dropna(subset=['trip_distance', 'price_per_seat'])
            
            # Verifier qu'il y a au moins 2 points de donnes diffrents
            if len(valid_data) >= 2 and valid_data['trip_distance'].nunique() >= 2:
                z = np.polyfit(valid_data['trip_distance'], valid_data['price_per_seat'], 1)
                y_hat = np.poly1d(z)(valid_data['trip_distance'])
                
                fig.add_traces(
                    go.Scatter(
                        x=valid_data['trip_distance'],
                        y=y_hat,
                        mode='lines',
                        name='Tendance',
                        line=dict(color='red')
                    )
                )
        except Exception as e:
            print(f"Impossible de calculer la ligne de tendance: {str(e)}")
        
        return fig
    else:
        # Graphique vide si les donnes ne sont pas disponibles
        return go.Figure()


def create_income_time_series(trips_df):
    """
    Cree un graphique montrant l'evolution des revenus dans le temps
    
    Args:
        trips_df: DataFrame contenant les donnes des trajets
    
    Returns:
        Un objet Figure de Plotly
    """
    # Identifier la colonne de date (selon la migration PostgreSQL)
    date_column = None
    for col in ['departure_schedule', 'departure_time', 'created_at']:
        if col in trips_df.columns:
            date_column = col
            break
    
    if date_column is not None and 'passenger_price' in trips_df.columns:
        try:
            # S'assurer que la colonne est au format datetime
            trips_df[date_column] = pd.to_datetime(trips_df[date_column])
            
            # Grouper par mois (ou autre periode selon la quantite de donnes)
            trips_df['month'] = trips_df[date_column].dt.to_period('M')
            monthly_income = trips_df.groupby('month')['passenger_price'].sum().reset_index()
            monthly_income['month'] = monthly_income['month'].dt.to_timestamp()
            
            fig = px.line(monthly_income, x='month', y='passenger_price',
                        labels={'month': 'Mois', 'passenger_price': 'Revenu total (XOF)'},
                        title="Evolution des revenus mensuels",
                        color_discrete_sequence=['#f39c12'])
            
            # Ameliorer le style du graphique
            fig.update_layout(
                margin=dict(l=40, r=40, t=40, b=40),
            )
            
            return fig
        except Exception as e:
            print(f"Erreur lors de la creation du graphique temporel: {str(e)}")
            return go.Figure()
    else:
        # Graphique vide si les donnes ne sont pas disponibles
        return go.Figure()
