"""
Composants UI pour la page de validation des documents conducteur (utilisé par validation_callbacks.py)
"""
import dash_bootstrap_components as dbc
from dash import html

def create_pending_document_card(user):
    """Crée une carte pour un document en attente de validation."""
    uid = user.get("uid")
    name = user.get("name", "Sans nom")
    email = user.get("email", "Sans email")
    driver_licence = user.get("driver_licence_url")
    id_card = user.get("id_card_url")
    
    print(f"Carte en attente - uid: {uid}, name: {name}, email: {email}")
    
    return create_document_card(uid, name, email, driver_licence, id_card, is_validated=False)


def create_validated_document_card(user):
    """Crée une carte pour un document déjà validé."""
    uid = user.get("uid")
    name = user.get("name", "Sans nom")
    email = user.get("email", "Sans email")
    driver_licence = user.get("driver_licence_url")
    id_card = user.get("id_card_url")
    
    print(f"Carte validée - uid: {uid}, name: {name}, email: {email}")
    
    return create_document_card(uid, name, email, driver_licence, id_card, is_validated=True)


def create_document_card(uid, name, email, driver_licence, id_card, is_validated):
    """Fonction sous-jacente pour créer la carte de document."""
    # Détermination du texte et de la couleur du bouton
    if is_validated:
        btn_text = "Dévalider les documents"
        btn_color = "danger"
        status_text = "Documents validés"
    else:
        btn_text = "Valider les documents"
        btn_color = "success"
        status_text = ""

    print(f"Bouton: {btn_text}, Couleur: {btn_color}")

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
                        dbc.Button(
                            "Voir le document" if driver_licence else "Document non disponible", 
                            id={"type": "view-doc", "index": f"{uid}-licence"},
                            color="primary" if driver_licence else "secondary", 
                            className="me-2",
                            disabled=not driver_licence
                        )
                    ])
                ], width=6),
                # Carte d'identité
                dbc.Col([
                    html.H6("Carte d'identité"),
                    html.Div([
                        dbc.Button(
                            "Voir le document" if id_card else "Document non disponible", 
                            id={"type": "view-doc", "index": f"{uid}-idcard"},
                            color="primary" if id_card else "secondary", 
                            className="me-2",
                            disabled=not id_card
                        )
                    ])
                ], width=6)
            ]),
            
            # Modal pour afficher les documents (sera activé par les boutons)
            dbc.Modal([
                dbc.ModalHeader("Document"),
                dbc.ModalBody([
                    html.Img(id={"type": "doc-img", "index": f"{uid}-licence"}, 
                             src=driver_licence if driver_licence else "", 
                             style={"width": "100%", "display": "block" if driver_licence else "none"}) if driver_licence else 
                    html.Div("Aucune image disponible")
                ]),
                dbc.ModalFooter(dbc.Button("Fermer", id={"type": "close-modal", "index": f"{uid}-licence"}, className="ms-auto"))
            ], id={"type": "modal", "index": f"{uid}-licence"}, size="lg"),
            
            dbc.Modal([
                dbc.ModalHeader("Document"),
                dbc.ModalBody([
                    html.Img(id={"type": "doc-img", "index": f"{uid}-idcard"}, 
                             src=id_card if id_card else "", 
                             style={"width": "100%", "display": "block" if id_card else "none"}) if id_card else 
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
                            html.Img(src=driver_licence if driver_licence else "", 
                                   style={"width": "100%", "border": "1px solid #ddd", "borderRadius": "8px", "display": "block" if driver_licence else "none"}) if driver_licence else 
                            html.Div("Document non disponible", className="text-danger")
                        ], width=6),
                        dbc.Col([
                            html.H6("Carte d'identité"),
                            html.Img(src=id_card if id_card else "", 
                                   style={"width": "100%", "border": "1px solid #ddd", "borderRadius": "8px", "display": "block" if id_card else "none"}) if id_card else 
                            html.Div("Document non disponible", className="text-danger")
                        ], width=6)
                    ])
                ]),
                dbc.ModalFooter(
                    dbc.Button("Fermer", id={"type": "close-compare-modal", "index": uid}, className="ms-auto")
                )
            ], id={"type": "compare-modal", "index": uid}, size="xl")
        ])
    ], className="mb-4")

__all__ = ["create_pending_document_card", "create_validated_document_card"]
