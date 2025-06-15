"""
Composants UI pour la page de validation des documents conducteur (utilisé par validation_callbacks.py)
"""
import dash_bootstrap_components as dbc
from dash import html

def create_user_document_card(user):
    uid = user.get("uid")
    name = user.get("name", "Sans nom")
    email = user.get("email", "Sans email")
    driver_licence = user.get("driver_licence_url")
    id_card = user.get("id_card_url")
    is_validated = user.get("is_driver_doc_validate", False)
    
    # Détermination du texte et de la couleur du bouton
    if is_validated:
        btn_text = "Dévalider les documents"
        btn_color = "danger"
        btn_disabled = False
        status_text = "Documents validés"
    else:
        btn_text = "Valider les documents"
        btn_color = "success"
        btn_disabled = False
        status_text = ""
    
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
                        btn_text,
                        id={"type": "validate-docs", "index": uid},
                        color=btn_color,
                        disabled=btn_disabled,
                        className="me-2"
                    ),
                    dbc.Button(
                        "Comparer",
                        id={"type": "compare-docs", "index": uid},
                        color="info",
                        className="me-2"
                    ),
                    html.Span(id={"type": "validation-status", "index": uid},
                              children=status_text if not is_validated else "")
                ], width=12, className="text-end")
            ]),
            # Modal de comparaison des documents
            dbc.Modal([
                dbc.ModalHeader("Comparer les documents"),
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col([
                            html.H6("Permis de conduire"),
                            html.Img(src=driver_licence, style={"width": "100%", "border": "1px solid #ddd", "borderRadius": "8px"}) if driver_licence else html.Div("Document non disponible", className="text-danger")
                        ], width=6),
                        dbc.Col([
                            html.H6("Carte d'identité"),
                            html.Img(src=id_card, style={"width": "100%", "border": "1px solid #ddd", "borderRadius": "8px"}) if id_card else html.Div("Document non disponible", className="text-danger")
                        ], width=6)
                    ])
                ]),
                dbc.ModalFooter(
                    dbc.Button("Fermer", id={"type": "close-compare-modal", "index": uid}, className="ms-auto")
                )
            ], id={"type": "compare-modal", "index": uid}, size="xl")
        ])
    ], className="mb-4")

__all__ = ["create_user_document_card"]
