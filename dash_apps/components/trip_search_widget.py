from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

def render_trip_search_widget():
    """
    Génère un widget de recherche avancée pour les trajets
    """
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # Recherche textuelle
                dbc.Col([
                    dbc.InputGroup([
                        dbc.Input(id="trips-search-input", placeholder="Rechercher par origine, destination ou ID trajet...", type="text"),
                        dbc.InputGroupText(html.I(className="fas fa-search")),
                    ])
                ], width=5),
                
                # Bouton pour filtres avancés
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-filter me-2"), "Filtres avancés"], 
                        id="trips-advanced-filters-btn", 
                        color="secondary", 
                        outline=True,
                        className="w-100"
                    ),
                ], width=3),
                
                # Bouton appliquer les filtres
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-check me-2"), "Appliquer"], 
                        id="trips-apply-filters-btn", 
                        color="success", 
                        className="w-100"
                    ),
                ], width=2),
                
                # Bouton de réinitialisation des filtres
                dbc.Col([
                    dbc.Button(
                        [html.I(className="fas fa-undo me-2"), "Réinitialiser"], 
                        id="trips-reset-filters-btn", 
                        color="danger", 
                        outline=True,
                        className="w-100"
                    ),
                ], width=1),
            ]),
            
            # Collapse pour les filtres avancés
            dbc.Collapse([
                html.Hr(),
                
                # 1. Date de création
                dbc.Row([
                    dbc.Col([
                        html.Label("Date de création"),
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(
                                    id="trips-date-filter-type",
                                    options=[
                                        {"label": "Période", "value": "range"},
                                        {"label": "Après le", "value": "after"},
                                        {"label": "Avant le", "value": "before"},
                                    ],
                                    value="range",
                                    clearable=False
                                )
                            ], width=4),
                            dbc.Col([
                                dcc.DatePickerRange(
                                    id="trips-creation-date-filter",
                                    start_date_placeholder_text="Début",
                                    end_date_placeholder_text="Fin",
                                    display_format="DD/MM/YYYY",
                                    clearable=True
                                ),
                                dcc.DatePickerSingle(
                                    id="trips-single-date-filter",
                                    placeholder="Sélectionner une date",
                                    display_format="DD/MM/YYYY",
                                    clearable=True,
                                    style={"display": "none"}
                                )
                            ], width=8)
                        ])
                    ], width=12)
                ], className="mb-3"),
                
                # 2. Tri par date de départ
                dbc.Row([
                    dbc.Col([
                        html.Label("Tri par date de départ"),
                        dcc.Dropdown(
                            id="trips-departure-sort-filter",
                            options=[
                                {"label": "Plus récent au plus ancien", "value": "desc"},
                                {"label": "Plus ancien au plus récent", "value": "asc"},
                            ],
                            value="desc",
                            clearable=False
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Tri par date de création"),
                        dcc.Dropdown(
                            id="trips-creation-sort-filter",
                            options=[
                                {"label": "Plus récent au plus ancien", "value": "desc"},
                                {"label": "Plus ancien au plus récent", "value": "asc"},
                            ],
                            value="desc",
                            clearable=False
                        )
                    ], width=6)
                ], className="mb-3"),
                
                # 3. Statut
                dbc.Row([
                    dbc.Col([
                        html.Label("Statut"),
                        dcc.Dropdown(
                            id="trips-status-filter",
                            options=[
                                {"label": "Tous", "value": "all"},
                                {"label": "En attente", "value": "PENDING"},
                                {"label": "Confirmé", "value": "CONFIRMED"},
                                {"label": "Annulé", "value": "CANCELED"},
                            ],
                            value="all",
                            clearable=False
                        )
                    ], width=12)
                ], className="mb-3"),

                # 4. Avec signalement
                dbc.Row([
                    dbc.Col([
                        dbc.Checkbox(
                            id="trips-has-signalement-filter",
                            label="Avec signalement",
                            value=False,
                        )
                    ], width=12)
                ], className="mb-1"),
            ], id="trips-advanced-filters-collapse", is_open=False)
        ])
    ], className="mb-3")

def render_active_trip_filters(filters):
    """
    Affiche un résumé des filtres actifs sous forme de badges
    
    Args:
        filters: Dictionnaire contenant les filtres actifs
        
    Returns:
        Un composant HTML affichant les filtres actifs, ou un div vide si aucun filtre
    """
    if not filters or not any(value for key, value in filters.items() if key not in ["status"] or value not in ["all", "", None]):
        return html.Div()
    
    filters_badges = []
    
    # Filtre texte
    if filters.get("text"):
        filters_badges.append(dbc.Badge(f"Recherche: {filters['text']}", color="info", className="me-2"))
    
    # Filtre date
    if filters.get("date_from") or filters.get("date_to") or filters.get("single_date"):
        date_str = f"Création: "
        if filters.get("date_filter_type") == "after" and filters.get("single_date"):
            date_str += f"après le {filters.get('single_date')}"
        elif filters.get("date_filter_type") == "before" and filters.get("single_date"):
            date_str += f"avant le {filters.get('single_date')}"
        else:
            if filters.get("date_from"):
                date_str += f"du {filters.get('date_from')} "
            if filters.get("date_to"):
                date_str += f"au {filters.get('date_to')}"
            elif filters.get("date_from"):
                date_str += "à aujourd'hui"
            
        filters_badges.append(dbc.Badge(date_str, color="info", className="me-2"))
        
    # Filtre tri par date
    if filters.get("date_sort") and filters["date_sort"] != "desc":
        sort_label = "Plus ancien au plus récent"
        filters_badges.append(dbc.Badge(f"Tri: {sort_label}", color="secondary", className="me-2"))
    
    # Filtre statut
    if filters.get("status") and filters["status"] != "all":
        status_map = {
            "PENDING": "En attente",
            "CONFIRMED": "Confirmé",
            "CANCELED": "Annulé",
        }
        status_label = status_map.get(filters["status"], str(filters["status"]))
        filters_badges.append(dbc.Badge(f"Statut: {status_label}", color="info", className="me-2"))

    # Filtre signalement
    if filters.get("has_signalement"):
        filters_badges.append(dbc.Badge("Avec signalement", color="warning", className="me-2"))
        
    return html.Div(
        [html.Span("Filtres actifs: ", className="me-2")] + filters_badges,
        className="mb-3 mt-2"
    )


@callback(
    [Output("trips-creation-date-filter", "style"),
     Output("trips-single-date-filter", "style")],
    Input("trips-date-filter-type", "value")
)
def toggle_trip_date_filter_inputs(filter_type):
    """Affiche le bon composant de date selon le type de filtre sélectionné"""
    if filter_type == "range":
        return {"display": "block"}, {"display": "none"}
    else:  # after ou before
        return {"display": "none"}, {"display": "block"}
