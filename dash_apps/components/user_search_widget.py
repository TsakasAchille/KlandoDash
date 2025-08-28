from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

def render_search_widget():
    """
    Génère un widget de recherche avancée pour les utilisateurs
    """
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # Recherche textuelle
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Input(id="users-search-input", placeholder="Rechercher par nom, prénom ou email...", type="text"),
                        dbc.InputGroupText(html.I(className="fas fa-search")),
                    ])
                ], width=6),
                
                # Bouton pour filtres avancés
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-filter me-2"), "Filtres avancés"], 
                        id="users-advanced-filters-btn", 
                        color="secondary", 
                        outline=True,
                        className="w-100"
                    ),
                ], width=3),
                
                # Bouton de réinitialisation des filtres
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-undo me-2"), "Réinitialiser"], 
                        id="users-reset-filters-btn", 
                        color="danger", 
                        outline=True,
                        className="w-100"
                    ),
                ], width=3),
            ]),
            
            # Collapse pour les filtres avancés
            dbc.Collapse([
                html.Hr(),
                dbc.Row([
                    # Filtrage par date d'inscription
                    dbc.Col([
                        html.Label("Date d'inscription"),
                        dcc.DatePickerRange(
                            id="users-registration-date-filter",
                            start_date_placeholder_text="Début",
                            end_date_placeholder_text="Fin",
                            display_format="DD/MM/YYYY",
                            clearable=True
                        )
                    ], width=6),
                    
                    # Filtrage par rôle
                    dbc.Col([
                        html.Label("Rôle"),
                        dcc.Dropdown(
                            id="users-role-filter",
                            options=[
                                {"label": "Tous", "value": "all"},
                                {"label": "Admin", "value": "admin"},
                                {"label": "Conducteur", "value": "driver"},
                                {"label": "Passager", "value": "passenger"},
                                {"label": "Utilisateur", "value": "user"},
                            ],
                            value="all",
                            clearable=False
                        )
                    ], width=3),
                    
                    # Filtrage par validation conducteur (basé sur is_driver_doc_validated)
                    dbc.Col([
                        html.Label("Validation conducteur"),
                        dcc.Dropdown(
                            id="users-driver-validation-filter",
                            options=[
                                {"label": "Tous", "value": "all"},
                                {"label": "Validés", "value": "validated"},
                                {"label": "Non validés", "value": "not_validated"},
                            ],
                            value="all",
                            clearable=False
                        )
                    ], width=3),
                    
                    # Filtrage par rating
                    dbc.Col([
                        html.Label("Notation"),
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(
                                    id="users-rating-operator-filter",
                                    options=[
                                        {"label": "Tous", "value": "all"},
                                        {"label": "Supérieur à", "value": "gt"},
                                        {"label": "Inférieur à", "value": "lt"},
                                    ],
                                    value="all",
                                    clearable=False
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Input(
                                    id="users-rating-value-filter",
                                    type="number",
                                    min=0,
                                    max=5,
                                    step=0.5,
                                    value=3,
                                    disabled=True
                                )
                            ], width=6)
                        ])
                    ], width=6)
                ])
            ], id="users-advanced-filters-collapse", is_open=False)
        ])
    ], className="mb-3")

def render_active_filters(filters):
    """
    Affiche un résumé des filtres actifs sous forme de badges
    
    Args:
        filters: Dictionnaire contenant les filtres actifs
        
    Returns:
        Un composant HTML affichant les filtres actifs, ou un div vide si aucun filtre
    """
    if not filters or not any(value for key, value in filters.items() if key not in ["role", "status"] or value not in ["all", "", None]):
        return html.Div()
    
    filters_badges = []
    
    # Filtre texte
    if filters.get("text"):
        filters_badges.append(dbc.Badge(f"Recherche: {filters['text']}", color="info", className="me-2"))
    
    # Filtre date
    if filters.get("date_from") or filters.get("date_to"):
        date_str = f"Inscription: "
        if filters.get("date_from"):
            date_str += f"du {filters.get('date_from')} "
        if filters.get("date_to"):
            date_str += f"au {filters.get('date_to')}"
        elif filters.get("date_from"):
            date_str += "à aujourd'hui"
            
        filters_badges.append(dbc.Badge(date_str, color="info", className="me-2"))
    
    # Filtre rôle
    if filters.get("role") and filters["role"] != "all":
        role_map = {
            "admin": "Administrateur", 
            "driver": "Conducteur", 
            "passenger": "Passager",
            "user": "Utilisateur"
        }
        role_label = role_map.get(filters["role"], filters["role"])
        filters_badges.append(dbc.Badge(f"Rôle: {role_label}", color="info", className="me-2"))
    
    # Filtre validation conducteur
    if filters.get("driver_validation") and filters["driver_validation"] != "all":
        validation_label = "Validés" if filters["driver_validation"] == "validated" else "Non validés"
        filters_badges.append(dbc.Badge(f"Validation conducteur: {validation_label}", color="info", className="me-2"))
        
    # Filtre rating
    if filters.get("rating_operator") and filters["rating_operator"] != "all" and filters.get("rating_value") is not None:
        operator_symbol = "≥" if filters["rating_operator"] == "gt" else "≤"
        filters_badges.append(dbc.Badge(f"Notation {operator_symbol} {filters.get('rating_value')}", color="info", className="me-2"))
        
    return html.Div(
        [html.Span("Filtres actifs: ", className="me-2")] + filters_badges,
        className="mb-3 mt-2"
    )


@callback(
    Output("users-rating-value-filter", "disabled"),
    Input("users-rating-operator-filter", "value")
)
def toggle_rating_value_input(operator):
    """Active ou désactive le champ de valeur de rating selon l'opérateur sélectionné"""
    # Désactiver le champ si aucun opérateur n'est sélectionné
    return operator == "all"
