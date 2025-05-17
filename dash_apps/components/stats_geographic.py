import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_stats_geographic(trips_data):
    """
    Rend les statistiques géographiques des trajets en utilisant des composants Dash
    
    Args:
        trips_data: Données des trajets sous forme de liste de dictionnaires
    
    Returns:
        Un composant Dash pour afficher les statistiques géographiques
    """
    if not trips_data:
        return html.Div("Aucune donnée de trajet disponible")
    
    # Convertir en DataFrame
    trips_df = pd.DataFrame(trips_data)
    
    # Vérifier si les colonnes géographiques sont disponibles
    has_geo_data = all(col in trips_df.columns for col in ['departure_name', 'destination_name'])
    
    if not has_geo_data:
        return html.Div("Données géographiques insuffisantes pour l'analyse")
    
    # Calculer les métriques géographiques
    unique_departures = trips_df['departure_name'].nunique() if 'departure_name' in trips_df.columns else 0
    unique_destinations = trips_df['destination_name'].nunique() if 'destination_name' in trips_df.columns else 0
    
    # Trouver les lieux les plus fréquents
    most_common_departure = trips_df['departure_name'].mode()[0] if 'departure_name' in trips_df.columns and not trips_df['departure_name'].empty else "Non disponible"
    most_common_destination = trips_df['destination_name'].mode()[0] if 'destination_name' in trips_df.columns and not trips_df['destination_name'].empty else "Non disponible"
    
    # Calculer la distance moyenne si disponible
    avg_distance = trips_df['trip_distance'].mean() if 'trip_distance' in trips_df.columns else 0
    
    # Métriques géographiques
    geo_metrics = [
        html.Div([
            html.H4("Métriques de la ville", className="card-title"),
            html.Div([
                html.P([html.Strong("Lieux de départ uniques: "), f"{unique_departures}"]),
                html.P([html.Strong("Destinations uniques: "), f"{unique_destinations}"]),
                html.P([html.Strong("Départ le plus fréquent: "), f"{most_common_departure}"]),
                html.P([html.Strong("Destination la plus fréquente: "), f"{most_common_destination}"]),
                html.P([html.Strong("Distance moyenne: "), f"{avg_distance:.1f} km"]),
            ])
        ], className="card-body")
    ]
    
    geo_metrics_card = dbc.Card(geo_metrics, className="mb-4", style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})
    
    # Graphique de distribution des lieux de départ
    departure_chart = create_departure_distribution(trips_df)
    departure_card = dbc.Card([
        dbc.CardBody([
            html.H4("Lieux de départ les plus fréquents", className="card-title"),
            dcc.Graph(figure=departure_chart)
        ])
    ], className="mb-4", style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})
    
    # Graphique de distribution des destinations
    destination_chart = create_destination_distribution(trips_df)
    destination_card = dbc.Card([
        dbc.CardBody([
            html.H4("Destinations les plus fréquentes", className="card-title"),
            dcc.Graph(figure=destination_chart)
        ])
    ], className="mb-4", style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})
    
    # Matrice origine-destination
    od_matrix_chart = create_origin_destination_matrix(trips_df)
    od_matrix_card = dbc.Card([
        dbc.CardBody([
            html.H4("Matrice Origine-Destination", className="card-title"),
            dcc.Graph(figure=od_matrix_chart)
        ])
    ], className="mb-4", style={"boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)"})
    
    # Layout final
    return html.Div([
        html.H3("Analyse géographique", className="mb-4"),
        geo_metrics_card,
        dbc.Row([
            dbc.Col(departure_card, width=12, lg=6),
            dbc.Col(destination_card, width=12, lg=6),
        ]),
        od_matrix_card
    ])


def create_departure_distribution(trips_df):
    """
    Crée un graphique de distribution des lieux de départ
    
    Args:
        trips_df: DataFrame contenant les données des trajets
    
    Returns:
        Un objet Figure de Plotly
    """
    if 'departure_name' in trips_df.columns:
        # Créer un DataFrame pour le graphique
        departure_counts = trips_df['departure_name'].value_counts().reset_index()
        departure_counts.columns = ["Lieu de départ", "Nombre de trajets"]
        
        # Limiter aux 10 premiers pour la lisibilité
        departure_counts = departure_counts.head(10)
        
        fig = px.bar(departure_counts, 
                     x="Nombre de trajets", 
                     y="Lieu de départ",
                     title="Top 10 des lieux de départ",
                     color_discrete_sequence=['#e74c3c'],
                     orientation='h')
        
        # Améliorer le style du graphique
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        return fig
    else:
        # Graphique vide si les données ne sont pas disponibles
        return go.Figure()


def create_destination_distribution(trips_df):
    """
    Crée un graphique de distribution des destinations
    
    Args:
        trips_df: DataFrame contenant les données des trajets
    
    Returns:
        Un objet Figure de Plotly
    """
    if 'destination_name' in trips_df.columns:
        # Créer un DataFrame pour le graphique
        destination_counts = trips_df['destination_name'].value_counts().reset_index()
        destination_counts.columns = ["Destination", "Nombre de trajets"]
        
        # Limiter aux 10 premiers pour la lisibilité
        destination_counts = destination_counts.head(10)
        
        fig = px.bar(destination_counts, 
                     x="Nombre de trajets", 
                     y="Destination",
                     title="Top 10 des destinations",
                     color_discrete_sequence=['#e74c3c'],
                     orientation='h')
        
        # Améliorer le style du graphique
        fig.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
        )
        
        return fig
    else:
        # Graphique vide si les données ne sont pas disponibles
        return go.Figure()


def create_origin_destination_matrix(trips_df):
    """
    Crée une matrice origine-destination
    
    Args:
        trips_df: DataFrame contenant les données des trajets
    
    Returns:
        Un objet Figure de Plotly
    """
    if 'departure_name' in trips_df.columns and 'destination_name' in trips_df.columns:
        try:
            # Créer la matrice origine-destination
            od_matrix = pd.crosstab(trips_df['departure_name'], trips_df['destination_name'])
            
            # Limiter aux 10 origines et destinations les plus fréquentes pour la lisibilité
            top_origins = trips_df['departure_name'].value_counts().head(10).index
            top_destinations = trips_df['destination_name'].value_counts().head(10).index
            
            od_matrix_filtered = od_matrix.loc[od_matrix.index.isin(top_origins), od_matrix.columns.isin(top_destinations)]
            
            # Créer la heatmap
            fig = px.imshow(od_matrix_filtered,
                           labels=dict(x="Destination", y="Origine", color="Nombre de trajets"),
                           title="Matrice Origine-Destination (Top 10)",
                           color_continuous_scale='Reds')
            
            # Améliorer le style du graphique
            fig.update_layout(
                margin=dict(l=40, r=40, t=40, b=40),
            )
            
            return fig
        except Exception as e:
            print(f"Erreur lors de la création de la matrice: {str(e)}")
            return go.Figure()
    else:
        # Graphique vide si les données ne sont pas disponibles
        return go.Figure()
