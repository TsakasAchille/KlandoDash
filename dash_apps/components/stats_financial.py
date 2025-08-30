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
        
    # Helper de formatage CFA pour KPIs
    def fmt_cfa(val):
        try:
            return ("{:,.0f}".format(float(val))).replace(",", " ") + " F CFA"
        except Exception:
            return str(val)

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
    income_time = fig_to_dict(create_income_time_series(trips_df)) if has_price_data else None
    top_destinations = fig_to_dict(create_top_destinations_by_revenue(trips_df)) if has_price_data and 'destination_name' in trips_df.columns else None
    
    # Préparer les données pour le template
    context = {
        "avg_price": fmt_cfa(avg_passenger_price),
        "total_price": fmt_cfa(total_passenger_price),
        "avg_price_per_km": ("{:,.0f}".format(avg_price_per_km).replace(",", " ") + " F CFA/km") if avg_price_per_km else "0 F CFA/km",
        "avg_driver_price": fmt_cfa(avg_driver_price),
        "total_driver_price": fmt_cfa(total_driver_price),
        "price_distribution": price_distribution,
        "driver_price_distribution": driver_price_distribution,
        "price_distance": price_distance,
        "income_time": income_time,
        "top_destinations": top_destinations,
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
        fig = px.histogram(
            trips_df,
            x="passenger_price",
            marginal="box",
            labels={"passenger_price": "Prix passager (F CFA)"},
            title="Distribution des prix passagers",
            color_discrete_sequence=['#f39c12']
        )

        # Mise en forme CFA: axe X en monnaie, hover unifié
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode="x unified",
        )
        fig.update_xaxes(tickprefix="F CFA ", separatethousands=True)
        fig.update_traces(hovertemplate="Prix: %{x:,.0f} F CFA<br>Comptes: %{y}")

        return fig
    else:
        # Graphique vide si les donnes ne sont pas disponibles
        return go.Figure()


def create_top_destinations_by_revenue(trips_df):
    """
    Top 10 destinations par revenu total (passenger_price)
    """
    if 'destination_name' in trips_df.columns and 'passenger_price' in trips_df.columns:
        df = trips_df.copy()
        grouped = (
            df.groupby('destination_name', dropna=False)['passenger_price']
              .sum()
              .reset_index()
              .sort_values('passenger_price', ascending=False)
              .head(10)
        )

        fig = px.bar(
            grouped,
            x='passenger_price',
            y='destination_name',
            orientation='h',
            labels={'passenger_price': 'Revenu (F CFA)', 'destination_name': 'Destination'},
            title='Top 10 destinations par revenu',
            color_discrete_sequence=['#4e79a7']
        )
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode='y unified'
        )
        fig.update_xaxes(tickprefix="F CFA ", separatethousands=True)
        fig.update_traces(hovertemplate="Destination: %{y}<br>Revenu: %{x:,.0f} F CFA")
        return fig
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
        fig = px.histogram(
            trips_df,
            x="driver_price",
            marginal="box",
            labels={"driver_price": "Prix conducteur (F CFA)"},
            title="Distribution des prix conducteurs",
            color_discrete_sequence=['#3366CC']
        )

        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode="x unified",
        )
        fig.update_xaxes(tickprefix="F CFA ", separatethousands=True)
        fig.update_traces(hovertemplate="Prix: %{x:,.0f} F CFA<br>Comptes: %{y}")

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
        fig = px.scatter(
            trips_df,
            x="distance",
            y="passenger_price",
            labels={"distance": "Distance (km)", "passenger_price": "Prix passager (F CFA)"},
            title="Relation entre prix passager et distance",
            color_discrete_sequence=['#f39c12']
        )

        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
            hovermode="x unified",
        )
        fig.update_yaxes(tickprefix="F CFA ", separatethousands=True)
        fig.update_xaxes(separatethousands=True)
        fig.update_traces(mode='markers', hovertemplate="Distance: %{x:,.1f} km<br>Prix: %{y:,.0f} F CFA")
        
        try:
            # Verifier qu'il y a suffisamment de donnes valides pour calculer une tendance
            valid_data = trips_df.dropna(subset=['distance', 'passenger_price'])
            
            # Verifier qu'il y a au moins 2 points de donnes diffrents
            if len(valid_data) >= 2 and valid_data['distance'].nunique() >= 2:
                z = np.polyfit(valid_data['distance'], valid_data['passenger_price'], 1)
                y_hat = np.poly1d(z)(valid_data['distance'])
                
                fig.add_traces(
                    go.Scatter(
                        x=valid_data['distance'],
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

            # Calcul MA 3 mois
            monthly_income['ma_3'] = monthly_income['passenger_price'].rolling(3).mean()

            fig = go.Figure()
            # Barres revenus
            fig.add_bar(
                x=monthly_income['month'],
                y=monthly_income['passenger_price'],
                name='Revenus',
                marker_color='#f39c12',
                hovertemplate="Mois: %{x|%Y-%m}<br>Revenus: %{y:,.0f} F CFA"
            )
            # Ligne MA 3M
            fig.add_scatter(
                x=monthly_income['month'],
                y=monthly_income['ma_3'],
                mode='lines',
                name='Moyenne mobile (3M)',
                line=dict(color='#2c3e50', width=2),
                hovertemplate="Mois: %{x|%Y-%m}<br>MA(3): %{y:,.0f} F CFA"
            )

            fig.update_layout(
                title="Évolution des revenus mensuels",
                xaxis_title='Mois',
                yaxis_title='Revenu total (F CFA)',
                margin=dict(l=40, r=40, t=40, b=40),
                hovermode='x unified',
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            fig.update_yaxes(tickprefix="F CFA ", separatethousands=True)

            return fig
        except Exception as e:
            print(f"Erreur lors de la creation du graphique temporel: {str(e)}")
            return go.Figure()
    else:
        # Graphique vide si les donnes ne sont pas disponibles
        return go.Figure()
