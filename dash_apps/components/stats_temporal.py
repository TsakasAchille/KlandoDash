from dash import html
import dash_bootstrap_components as dbc
from jinja2 import Environment, FileSystemLoader
import os
import pandas as pd
import json
from datetime import datetime

# Initialisation de Jinja2 pour le template
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
env = Environment(loader=FileSystemLoader(template_dir))
stats_temporal_template = env.get_template("stats_temporal_template.jinja2")

# Styles communs
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '28px',
    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
    'padding': '0px',
    'overflow': 'hidden',
    'marginBottom': '16px'
}

def render_stats_temporal(trips_data):
    """
    Affiche les statistiques temporelles des trajets en utilisant un template Jinja2.
    
    Args:
        trips_data: Données des trajets (liste de dictionnaires ou DataFrame)
    
    Returns:
        dash.html.Div: Composant Dash contenant les statistiques temporelles
    """
    if not trips_data:
        # Rendu du template HTML avec Jinja2 sans données de trajet
        html_content = stats_temporal_template.render(
            time_data=[],
            first_date=None,
            last_date=None,
            trend_percentage=None,
            busiest_date=None,
            busiest_count=None
        )
        
        # Afficher le template dans un iframe
        return html.Div(
            html.Iframe(
                srcDoc=html_content,
                style={
                    'width': '100%',
                    'height': '450px',
                    'border': 'none',
                    'overflow': 'hidden',
                    'backgroundColor': 'transparent',
                    'borderRadius': '18px'
                },
                id='stats-temporal-iframe',
                sandbox='allow-scripts',
            ),
            style=CARD_STYLE
        )
    
    # Convertir en DataFrame si nécessaire
    if isinstance(trips_data, list):
        trips_df = pd.DataFrame(trips_data)
    else:
        trips_df = trips_data
    
    # Identifier la colonne de date
    date_columns = ['datetime', 'date', 'departure_date', 'created_at', 'trip_date']
    date_col = None
    for col in date_columns:
        if col in trips_df.columns:
            date_col = col
            break
    
    if date_col is None:
        # Pas de données temporelles disponibles
        html_content = stats_temporal_template.render(
            time_data=[],
            first_date=None,
            last_date=None,
            trend_percentage=None,
            busiest_date=None,
            busiest_count=None
        )
    else:
        # Convertir la colonne en datetime et trier
        try:
            trips_df[date_col] = pd.to_datetime(trips_df[date_col])
            trips_df = trips_df.sort_values(date_col)
            
            # Grouper par date
            trips_by_date = trips_df.groupby(trips_df[date_col].dt.date).size().reset_index(name="count")
            trips_by_date.columns = ["date", "count"]
            
            # Formater les dates pour le template
            trips_by_date["date_str"] = trips_by_date["date"].apply(lambda x: x.strftime("%Y-%m-%d"))
            
            # Préparer les données pour le graphique
            time_data = [
                {"date": row["date_str"], "count": int(row["count"])}
                for _, row in trips_by_date.iterrows()
            ]
            
            # Calculer des métriques supplémentaires
            first_date = trips_by_date["date"].min().strftime("%d/%m/%Y")
            last_date = trips_by_date["date"].max().strftime("%d/%m/%Y")
            
            # Calculer la tendance
            if len(trips_by_date) >= 2:
                first_week_count = trips_by_date["count"].iloc[0:min(7, len(trips_by_date)//3)].mean()
                last_week_count = trips_by_date["count"].iloc[-min(7, len(trips_by_date)//3):].mean()
                
                if first_week_count > 0:
                    trend_percentage = round(((last_week_count - first_week_count) / first_week_count) * 100, 1)
                else:
                    trend_percentage = None
            else:
                trend_percentage = None
            
            # Trouver le jour le plus chargé
            busiest_idx = trips_by_date["count"].idxmax()
            busiest_date = trips_by_date.loc[busiest_idx, "date"].strftime("%d/%m/%Y")
            busiest_count = int(trips_by_date.loc[busiest_idx, "count"])
            
            # Rendu du template
            html_content = stats_temporal_template.render(
                time_data=time_data,
                first_date=first_date,
                last_date=last_date,
                trend_percentage=trend_percentage,
                busiest_date=busiest_date,
                busiest_count=busiest_count
            )
        except Exception as e:
            print(f"Erreur lors du traitement des données temporelles: {str(e)}")
            # En cas d'erreur, afficher un template vide
            html_content = stats_temporal_template.render(
                time_data=[],
                first_date=None,
                last_date=None,
                trend_percentage=None,
                busiest_date=None,
                busiest_count=None
            )
    
    # Afficher le template dans un iframe
    return html.Div(
        html.Iframe(
            srcDoc=html_content,
            style={
                'width': '100%',
                'height': '450px',
                'border': 'none',
                'overflow': 'hidden',
                'backgroundColor': 'transparent',
                'borderRadius': '18px'
            },
            id='stats-temporal-iframe',
            sandbox='allow-scripts',
        ),
        style=CARD_STYLE
    )
