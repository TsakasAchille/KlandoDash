from dash import html
import dash_bootstrap_components as dbc

def render_user_profile(user):
    if user is None:
        return None
    # Photo de profil
    photo_url = user.get('photo_url', None)
    # Statut téléphone
    phone_verified = user.get('phone_verified', None)
    phone = user.get('phone', user.get('phone_number', ''))
    phone_status = "✅ Vérifié" if phone_verified else "❌ Non vérifié" if phone_verified is not None else "Non disponible"
    # Nom complet
    name = user.get('name') or user.get('display_name') or user.get('first_name') or ''
    # Profil infos
    profile_items = [
        ("Nom", name),
        ("Email", user.get('email', '')),
        ("Téléphone", phone)
    ]
    if phone_verified is not None and phone:
        profile_items.append(("Statut téléphone", phone_status))
    profile_items.append(("ID", user.get('uid', user.get('id', ''))))
    # Layout
    return dbc.Card([
        dbc.CardHeader("Profil utilisateur"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Ul([
                        html.Li(f"{label} : {value}") for label, value in profile_items
                    ])
                ], width=8),
                dbc.Col([
                    html.Img(src=photo_url, style={"maxWidth": "100px", "borderRadius": "8px"}) if photo_url else None
                ], width=4)
            ])
        ])
    ], className="klando-card")
