from dash import html
import dash_bootstrap_components as dbc

# Affiche la liste des passagers/réservations d'un trajet

def render_trip_passengers(passengers):
    """
    Affiche la liste des passagers (déjà enrichie, issue de la base SQL ou d'une liste).
    Paramètres :
        passengers : list[dict] | None
    """
    if passengers is None:
        passengers = []
    if not passengers or not isinstance(passengers, list):
        return dbc.Alert("Aucun passager à afficher pour ce trajet.", color="secondary", className="mb-3")
    # Fiches individuelles (cartes)
    cards = []
    for i, res in enumerate(passengers):
        nom = res.get("name", f"Passager {i+1}")
        email = res.get("email", "-")
        tel = res.get("phone", "-")
        places = res.get("seats", "-")
        statut = res.get("status", "-")
        cards.append(
            html.Div([
                html.Div([
                    html.Span("👤", style={"fontSize": "1.3em", "marginRight": "8px"}),
                    html.Strong(nom)
                ], style={"borderBottom": "1px solid #eee", "paddingBottom": "6px", "marginBottom": "8px"}),
                html.Ul([
                    html.Li([html.Strong("Email : "), email]),
                    html.Li([html.Strong("Téléphone : "), tel]),
                    html.Li([html.Strong("Places réservées : "), str(places)]),
                    html.Li([html.Strong("Statut : "), html.Span(statut, style={"fontWeight": "bold", "color": "#007bff" if statut=="confirmé" else "#B00"})]),
                ], style={"listStyle": "none", "padding": 0, "margin": 0})
            ], className="klando-passenger-card", style={"background": "#fff", "borderRadius": "10px", "boxShadow": "0 2px 8px #0001", "padding": "14px", "marginBottom": "12px", "height": "100%"})
        )
    # Disposition responsive (cartes en grille)
    return dbc.Row([
        dbc.Col(card, md=6, xs=12) for card in cards
    ], className="g-2")
