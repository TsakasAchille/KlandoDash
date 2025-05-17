import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def render_stats_financial(trips_data):
    """
    Rend les statistiques financiu00e8res des trajets en utilisant des composants Dash
    
    Args:
        trips_data: Donnu00e9es des trajets sous forme de liste de dictionnaires
    
    Returns:
        Un composant Dash pour afficher les statistiques financieres
    """
    if not trips_data:
        return html.Div("Aucune donnée de trajet disponible")
    
    # Convertir en DataFrame
    trips_df = pd.DataFrame(trips_data)
    
    # Verifier si les colonnes financieres sont disponibles
    has_price_data = 'price_per_seat' in trips_df.columns
    has_viator_data = 'viator_income' in trips_df.columns
    
    if not has_price_data and not has_viator_data:
        return html.Div("Donnees financieres insuffisantes pour l'analyse")
    
    # Calculer les metriques financieres
    avg_price = trips_df['price_per_seat'].mean() if 'price_per_seat' in trips_df.columns else 0
    total_price = trips_df['price_per_seat'].sum() if 'price_per_seat' in trips_df.columns else 0
    
    # Calculer les metriques de Viator si disponibles
    avg_viator_income = trips_df['viator_income'].mean() if 'viator_income' in trips_df.columns else 0
    total_viator_income = trips_df['viator_income'].sum() if 'viator_income' in trips_df.columns else 0
    
    # Calculer le prix par kilomètre si les deux colonnes sont disponibles
    if 'price_per_seat' in trips_df.columns and 'trip_distance' in trips_df.columns:
        # éviter la division par zéro
        valid_trips = trips_df[trips_df['trip_distance'] > 0]
        if not valid_trips.empty:
            price_per_km = valid_trips['price_per_seat'] / valid_trips['trip_distance']
            avg_price_per_km = price_per_km.mean()
        else:
            avg_price_per_km = 0
    else:
        avg_price_per_km = 0
    
    # Metriques financieres
    finance_metrics = [
        html.Div([
            html.H4("Metriques financieres", className="card-title"),
            html.Div([
                html.P([html.Strong("Prix moyen par place: "), f"{avg_price:.0f} XOF"]),
                html.P([html.Strong("Revenu total: "), f"{total_price:.0f} XOF"]),
                html.P([html.Strong("Revenu Viator moyen: "), f"{avg_viator_income:.0f} XOF"]),
                html.P([html.Strong("Revenu Viator total: "), f"{total_viator_income:.0f} XOF"]),
                html.P([html.Strong("Prix moyen par km: "), f"{avg_price_per_km:.0f} XOF/km"]),
            ])
        ], className="card-body")
    ]
    
    finance_metrics_card = dbc.Card(finance_metrics, className="mb-4", style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})
    
    # Graphique de distribution des prix
    price_chart = create_price_distribution(trips_df)
    price_card = dbc.Card([
        dbc.CardBody([
            html.H4("Distribution des prix par place", className="card-title"),
            dcc.Graph(figure=price_chart)
        ])
    ], className="mb-4", style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})
    
    # Graphique de distribution des revenus Viator
    viator_chart = create_viator_income_distribution(trips_df) if has_viator_data else None
    viator_card = dbc.Card([
        dbc.CardBody([
            html.H4("Distribution des revenus Viator", className="card-title"),
            dcc.Graph(figure=viator_chart) if viator_chart else html.Div("Donnees de revenus Viator non disponibles")
        ])
    ], className="mb-4", style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})
    
    # Graphique prix vs distance
    price_distance_chart = create_price_vs_distance(trips_df)
    price_distance_card = dbc.Card([
        dbc.CardBody([
            html.H4("Prix vs Distance", className="card-title"),
            dcc.Graph(figure=price_distance_chart)
        ])
    ], className="mb-4", style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})
    
    # Graphique evolution des revenus
    income_time_chart = create_income_time_series(trips_df)
    income_time_card = dbc.Card([
        dbc.CardBody([
            html.H4("Evolution des revenus", className="card-title"),
            dcc.Graph(figure=income_time_chart)
        ])
    ], className="mb-4", style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})
    
    # Layout final
    return html.Div([
        html.H3("Analyse financiere", className="mb-4"),
        finance_metrics_card,
        dbc.Row([
            dbc.Col(price_card, width=12, lg=6),
            dbc.Col(viator_card, width=12, lg=6) if has_viator_data else None,
        ]),
        dbc.Row([
            dbc.Col(price_distance_card, width=12, lg=6),
            dbc.Col(income_time_card, width=12, lg=6),
        ]),
    ])


def create_price_distribution(trips_df):
    """
    Cree un graphique de distribution des prix par place
    
    Args:
        trips_df: DataFrame contenant les donnes des trajets
    
    Returns:
        Un objet Figure de Plotly
    """
    if 'price_per_seat' in trips_df.columns:
        fig = px.histogram(trips_df, x="price_per_seat", nbins=20, 
                         labels={"price_per_seat": "Prix par place (XOF)"},
                         title="Distribution des prix par place",
                         color_discrete_sequence=['#f39c12'])
        
        # Ameliorer le style du graphique
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        return fig
    else:
        # Graphique vide si les donnes ne sont pas disponibles
        return go.Figure()


def create_viator_income_distribution(trips_df):
    """
    Cree un graphique de distribution des revenus Viator
    
    Args:
        trips_df: DataFrame contenant les donnes des trajets
    
    Returns:
        Un objet Figure de Plotly
    """
    if 'viator_income' in trips_df.columns:
        fig = px.histogram(trips_df, x="viator_income", nbins=20, 
                         labels={"viator_income": "Revenu Viator (XOF)"},
                         title="Distribution des revenus Viator",
                         color_discrete_sequence=['#f39c12'])
        
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
    if 'price_per_seat' in trips_df.columns and 'trip_distance' in trips_df.columns:
        fig = px.scatter(trips_df, x="trip_distance", y="price_per_seat", 
                       labels={"trip_distance": "Distance (km)", "price_per_seat": "Prix par place (XOF)"},
                       title="Relation entre prix et distance",
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
    
    if date_column is not None and 'price_per_seat' in trips_df.columns:
        try:
            # S'assurer que la colonne est au format datetime
            trips_df[date_column] = pd.to_datetime(trips_df[date_column])
            
            # Grouper par mois (ou autre periode selon la quantite de donnes)
            trips_df['month'] = trips_df[date_column].dt.to_period('M')
            monthly_income = trips_df.groupby('month')['price_per_seat'].sum().reset_index()
            monthly_income['month'] = monthly_income['month'].dt.to_timestamp()
            
            fig = px.line(monthly_income, x='month', y='price_per_seat',
                        labels={'month': 'Mois', 'price_per_seat': 'Revenu total (XOF)'},
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
