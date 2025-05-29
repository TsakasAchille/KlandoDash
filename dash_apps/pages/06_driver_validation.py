import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import dash
import pandas as pd
from dash_apps.data_processing.processors.user_processor import UserProcessor
from dash_apps.utils.admin_db import is_admin
from dash_apps.utils.user_data import update_user_field
from flask import session

# Layout principal de la page de validation des documents conducteur

def serve_layout():
    user_email = session.get('user_email', None)
    if not is_admin(user_email):
        return dbc.Container([
            html.H2("Accès refusé", style={"marginTop": "20px"}),
            dbc.Alert("Vous n'êtes pas autorisé à accéder à cette page.", color="danger")
        ], fluid=True)
    else:
        return dbc.Container([
            html.H2("Validation des documents conducteur", style={"marginTop": "20px"}),
            html.P("Cette page permet aux administrateurs de vérifier et valider les documents soumis par les conducteurs.",
                   className="text-muted"),
            dbc.Card([
                dbc.CardHeader("Liste des documents à valider"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            dbc.Badge(id="documents-count-badge", color="primary", className="me-1"),
                            html.Span(" documents en attente de validation", className="text-muted")
                        ], width=6),
                        dbc.Col([
                            html.Div([
                                dbc.Label("Filtrer par statut:"),
                                dbc.RadioItems(
                                    options=[
                                        {"label": "En attente de validation", "value": "pending"},
                                        {"label": "Tous les documents", "value": "all"},
                                        {"label": "Documents validés", "value": "validated"}
                                    ],
                                    value="pending",
                                    id="validation-filter",
                                    inline=True
                                )
                            ])
                        ], width=6)
                    ])
                ]),
                html.Div(id="drivers-documents-container")
            ])
        ])

layout = serve_layout

# Chargement des données utilisateurs avec documents
@callback(
    [Output("drivers-documents-container", "children"),
     Output("documents-count-badge", "children")],
    [Input("validation-filter", "value")]
)
def load_drivers_data(filter_value):
    # S'assurer que l'utilisateur est admin
    user_email = session.get('user_email', None)
    if not is_admin(user_email):
        return dbc.Alert("Vous n'avez pas accès à cette page.", color="danger"), 0
    
    # Récupérer tous les utilisateurs
    users_df = UserProcessor.get_all_users()

    if "is_driver_doc_validate" not in users_df.columns:
        users_df["is_driver_doc_validate"] = None
    
    if users_df is None or users_df.empty:
        return dbc.Alert("Aucun utilisateur trouvé dans la base de données.", color="warning"), 0
    
    # Debug : afficher les colonnes pour comprendre le problème
    
    if "driver_licence_url" not in users_df.columns:
        return dbc.Alert("Erreur : la colonne 'driver_licence_url' est absente des données reçues.", color="danger"), 0
    # Garder seulement les utilisateurs avec un permis transmis
    users_df = users_df[users_df["driver_licence_url"].notnull()]

    # Filtrer selon les paramètres
    if filter_value == "pending":
        # Documents transmis mais pas encore validés
        filtered_df = users_df[(users_df["driver_documents_transmitted"] == True) & 
                              (users_df["is_driver_doc_validate"].isnull() | 
                               (users_df["is_driver_doc_validate"] == False))]
    elif filter_value == "validated":
        # Documents déjà validés
        filtered_df = users_df[(users_df["driver_documents_transmitted"] == True) & 
                              (users_df["is_driver_doc_validate"] == True)]
    else:  # "all"
        # Tous les utilisateurs ayant soumis des documents
        filtered_df = users_df[users_df["driver_documents_transmitted"] == True]
    
    # Nombre de documents en attente
    pending_count = len(filtered_df)
    
    if filtered_df.empty:
        return dbc.Alert("Aucun utilisateur correspondant aux critères de filtrage.", color="info"), pending_count
    
    # Construire les cards pour chaque utilisateur
    user_cards = []
    for _, user in filtered_df.iterrows():
        user_card = create_user_document_card(user)
        user_cards.append(user_card)
    
    return html.Div(user_cards), pending_count

# Fonction pour créer une carte d'utilisateur avec ses documents
def create_user_document_card(user):
    uid = user.get("uid")
    name = user.get("name", "Sans nom")
    email = user.get("email", "Sans email")
    driver_licence = user.get("driver_licence_url")
    id_card = user.get("id_card_url")
    is_validated = user.get("is_driver_doc_validate", False)
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5(f"{name}", className="card-title"),
            html.H6(f"{email}", className="card-subtitle text-muted")
        ]),
        dbc.CardBody([
            dbc.Row([
                # Permis de conduire
                dbc.Col([
                    html.H6("Permis de conduire"),
                    html.Div([
                        dbc.Button("Voir le document", id={"type": "view-doc", "index": f"{uid}-licence"},
                                 color="primary", className="me-2") if driver_licence else 
                        html.Span("Document non disponible", className="text-danger")
                    ])
                ], width=6),
                # Carte d'identité
                dbc.Col([
                    html.H6("Carte d'identité"),
                    html.Div([
                        dbc.Button("Voir le document", id={"type": "view-doc", "index": f"{uid}-idcard"},
                                 color="primary", className="me-2") if id_card else 
                        html.Span("Document non disponible", className="text-danger")
                    ])
                ], width=6)
            ]),
            
            # Modal pour afficher les documents (sera activé par les boutons)
            dbc.Modal([
                dbc.ModalHeader("Document"),
                dbc.ModalBody([
                    html.Img(id={"type": "doc-img", "index": f"{uid}-licence"}, 
                             src=driver_licence, style={"width": "100%"}) if driver_licence else 
                    html.Div("Aucune image disponible")
                ]),
                dbc.ModalFooter(dbc.Button("Fermer", id={"type": "close-modal", "index": f"{uid}-licence"}, className="ms-auto"))
            ], id={"type": "modal", "index": f"{uid}-licence"}, size="lg"),
            
            dbc.Modal([
                dbc.ModalHeader("Document"),
                dbc.ModalBody([
                    html.Img(id={"type": "doc-img", "index": f"{uid}-idcard"}, 
                             src=id_card, style={"width": "100%"}) if id_card else 
                    html.Div("Aucune image disponible")
                ]),
                dbc.ModalFooter(dbc.Button("Fermer", id={"type": "close-modal", "index": f"{uid}-idcard"}, className="ms-auto"))
            ], id={"type": "modal", "index": f"{uid}-idcard"}, size="lg"),
            
            # Zone de validation
            html.Hr(),
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Valider les documents" if not is_validated else "Documents validés",
                        id={"type": "validate-docs", "index": uid},
                        color="success" if not is_validated else "secondary",
                        disabled=is_validated,
                        className="me-2"
                    ),
                    html.Span(id={"type": "validation-status", "index": uid},
                              children="Documents validés le XX/XX/XXXX" if is_validated else "")
                ], width=12, className="text-end")
            ])
        ])
    ], className="mb-4")

# Callback pour ouvrir le modal du permis de conduire
@callback(
    Output({"type": "modal", "index": dash.dependencies.MATCH}, "is_open"),
    [Input({"type": "view-doc", "index": dash.dependencies.MATCH}, "n_clicks"),
     Input({"type": "close-modal", "index": dash.dependencies.MATCH}, "n_clicks")],
    [State({"type": "modal", "index": dash.dependencies.MATCH}, "is_open")]
)
def toggle_modal(n_open, n_close, is_open):
    if n_open or n_close:
        return not is_open
    return is_open

# Callback pour valider les documents
@callback(
    [Output({"type": "validate-docs", "index": dash.dependencies.MATCH}, "disabled"),
     Output({"type": "validate-docs", "index": dash.dependencies.MATCH}, "children"),
     Output({"type": "validation-status", "index": dash.dependencies.MATCH}, "children")],
    [Input({"type": "validate-docs", "index": dash.dependencies.MATCH}, "n_clicks")],
    [State({"type": "validate-docs", "index": dash.dependencies.MATCH}, "id")],
    prevent_initial_call=True
)
def validate_driver_documents(n_clicks, button_id):
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update
    
    # Extraire l'ID utilisateur du bouton
    uid = button_id["index"]
    
    try:
        # Mettre à jour le statut de validation
        update_user_field(uid, "is_driver_doc_validate", True)
        
        import datetime
        validation_date = datetime.datetime.now().strftime("%d/%m/%Y")
        status_text = f"Documents validés le {validation_date}"
        
        return True, "Documents validés", status_text
    except Exception as e:
        print(f"Erreur lors de la validation des documents: {str(e)}")
        return False, "Échec de validation", f"Erreur: {str(e)}"

