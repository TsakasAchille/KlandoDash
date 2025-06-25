from dash import dash_table, html
import dash_bootstrap_components as dbc

# Couleurs KLANDO
KLANDO_PRIMARY = "#3366CC"  # Bleu principal
KLANDO_RED = "#730200"     # Rouge accent
KLANDO_BLUEGREY = "#3a4654" # Bleu-gris

# Styles communs pour une cohérence visuelle avec la page trajets
CARD_STYLE = {
    'backgroundColor': 'white',
    'borderRadius': '28px',
    'boxShadow': 'rgba(0, 0, 0, 0.1) 0px 1px 3px, rgba(0, 0, 0, 0.1) 0px 10px 30px',
    'padding': '15px',
    'overflow': 'hidden',
    'marginBottom': '16px'
}

def render_users_table(users_df, columns=None, selected_rows=None, page_current=0):
    """
    Génère un tableau d'utilisateurs avec un style moderne et cohérent.
    
    Args:
        users_df: DataFrame des utilisateurs
        columns: Liste de colonnes Dash (optionnel)
        selected_rows: Lignes sélectionnées par défaut (optionnel)
    """
    if selected_rows is None:
        selected_rows = []
        
    # Préparation des colonnes
    # Afficher toutes les colonnes du schéma users.json
    display_columns = [
        'uid', 'display_name', 'email', 'first_name', 'name', 'phone_number', 'birth', 'photo_url', 'bio',
        'driver_license_url', 'gender', 'id_card_url', 'rating', 'rating_count',
        'role', 'updated_at', 'created_at', 'is_driver_doc_validated'
    ]
    
    if columns is None:
        # Renommage des colonnes pour plus de lisibilité
        column_mapping = {
            'uid': 'ID Utilisateur',
            'name': 'Nom',
            'email': 'Email',
            'phone_number': 'Téléphone',
            'role': 'Rôle',
            'status': 'Statut',
            'created_at': 'Date de création'
        }
        
        columns = []
        for col in display_columns:
            name = column_mapping.get(col, col.replace('_', ' ').title())
            columns.append({"name": name, "id": col})
    
    # Création du tableau avec un style moderne et cohérent
    table = dash_table.DataTable(
        id="users-table",
        columns=columns,
        data=users_df.to_dict("records"),
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
            "padding": "14px 15px",
            "borderBottom": "1px solid #e0e0e0",
            "lineHeight": "1.5"
        },
        style_header={
            "backgroundColor": "#f4f6f8",
            "color": "#3a4654",
            "fontWeight": "600",
            "fontSize": "15px",
            "padding": "16px 15px",
            "borderBottom": "2px solid #dee2e6",
            "textTransform": "uppercase",
            "letterSpacing": "0.5px"
        },
        style_data_conditional=[
            # Lignes paires/impaires
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#f9fafb"
            },
            # Sélection
            {
                "if": {"state": "selected"},
                "backgroundColor": "rgba(51, 102, 204, 0.05)",
                "color": "#333",
                "fontWeight": "500",
                "border": f"1px solid {KLANDO_PRIMARY}"
            },
            # Survol
            {
                "if": {"state": "active"},
                "backgroundColor": "rgba(51, 102, 204, 0.02)",
                "border": f"1px solid #dee2e6"
            },
            # Curseur pointer
            {
                "if": {"state": None},
                "cursor": "pointer"
            }
        ],
        page_size=10,
        page_current=page_current,
    )
    
    # Encapsulation du tableau dans une carte pour cohérence visuelle
    return html.Div([
        html.Div([
            html.H5("Liste des utilisateurs", style={
                "marginBottom": "15px", 
                "color": "#3a4654",
                "fontWeight": "500",
                "fontSize": "18px"
            }),
            table
        ], style=CARD_STYLE)
    ])
