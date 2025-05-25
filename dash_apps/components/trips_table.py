from dash import dash_table, html
import dash_bootstrap_components as dbc

# Couleurs KLANDO
KLANDO_PRIMARY = "#3366CC"  # Bleu principal
KLANDO_RED = "#730200"     # Rouge accent
KLANDO_BLUEGREY = "#3a4654" # Bleu-gris

# Styles communs pour une cohérence visuelle
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '28px',
    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
    'padding': '15px',
    'overflow': 'hidden',
    'marginBottom': '16px'
}

def render_trips_table(trips_df, columns=None, selected_rows=None, table_id="trips-table", page_current=0):
    """
    Retourne un dash_table.DataTable stylé selon le design moderne de l'application.
    
    Args:
        trips_df: DataFrame des trajets
        columns: liste de colonnes Dash (optionnel)
        selected_rows: Lignes sélectionnées initialement
    """
    if selected_rows is None:
        selected_rows = []
    
    # Masquer la colonne 'polyline' et autres colonnes techniques si elles existent
    hide_columns = ['polyline', 'geometry', 'coordinates']
    display_columns = [col for col in trips_df.columns if col not in hide_columns]
    
    # Ajoute Trip ID si absent
    if 'trip_id' not in trips_df.columns:
        trips_df['trip_id'] = ''
    
    # Colonnes formatees
    if columns is None:
        # Renommer les colonnes pour plus de lisibilité
        column_mapping = {
            'trip_id': 'ID Trajet',
            'departure_name': 'Départ',
            'destination_name': 'Destination',
            'departure_date': 'Date de départ',
            'departure_schedule': 'Heure de départ',
            'driver_id': 'Conducteur',
            'passenger_price': 'Prix passager',
            'driver_price': 'Prix conducteur',
            'seats_available': 'Places disponibles',
            'seats_booked': 'Places réservées',
            'seats_published': 'Places publiées',
            'distance': 'Distance',
            'status': 'Statut'
        }
        
        columns = []
        for col in display_columns:
            name = column_mapping.get(col, col.replace('_', ' ').title())
            columns.append({"name": name, "id": col})
    
    # Table stylisee avec la meme apparence que les autres composants
    table = dash_table.DataTable(
        id=table_id,
        columns=columns,
        data=trips_df.to_dict("records"),
        filter_action='native',
        sort_action='native',
        row_selectable="single",
        selected_rows=selected_rows,
        # Centrer les cases à cocher
        css=[{
            'selector': 'input[type="checkbox"]',
            'rule': 'margin: auto; display: block;'
        }],
        style_table={
            "overflowX": "auto",
            "width": "100%",
        },
        style_cell={
            "textAlign": "left",
            "fontSize": "14px",
            "fontFamily": "'Roboto', 'Helvetica Neue', sans-serif",
            "color": "#333",
            "backgroundColor": "white",
            "padding": "14px 15px",  # Légèrement plus d'espace vertical
            "borderBottom": "1px solid #e0e0e0",
            "lineHeight": "1.5"  # Améliore la lisibilité
        },
        style_header={
            "backgroundColor": "#f4f6f8",  # Légèrement plus contrasté
            "color": "#3a4654",  # Utilisation du bleu-gris Klando
            "fontWeight": "600",
            "fontSize": "15px",
            "padding": "16px 15px",  # Plus d'espace pour l'en-tête
            "borderBottom": "2px solid #dee2e6",
            "textTransform": "uppercase",
            "letterSpacing": "0.5px"
        },
        style_data_conditional=[
            # Styliser les lignes paires/impaires
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f9fafb"
            },
            # Style de la ligne sélectionnée (plus léger)
            {
                "if": {"state": "selected"},
                "backgroundColor": "rgba(51, 102, 204, 0.05)",  # Très léger
                "color": "#333",
                "fontWeight": "500",  # Plus léger que semi-bold
                "border": f"1px solid {KLANDO_PRIMARY}"
            },
            # Effet au survol
            {
                "if": {"state": "active"},
                "backgroundColor": "rgba(51, 102, 204, 0.02)",  # Encore plus léger
                "border": f"1px solid #dee2e6"  # Bordure plus subtile
            },
            # Curseur pointer pour toutes les lignes
            {
                "if": {"state": None},
                "cursor": "pointer"
            }
        ],
        page_size=10,
        page_current=page_current,
    )
    
    # Envelopper la table dans un conteneur style avec le meme design que les autres composants
    return html.Div([
        html.Div([
            html.H5("Liste des trajets", style={
                "marginBottom": "15px", 
                "color": "#3a4654",
                "fontWeight": "500",
                "fontSize": "18px"
            }),
            table
        ], style=CARD_STYLE)
    ])
