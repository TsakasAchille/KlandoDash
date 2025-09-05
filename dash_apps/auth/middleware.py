"""
Middleware d'authentification pour KlandoDash
"""
from flask import request, redirect, session
from flask_login import current_user

def auth_middleware():
    """
    Middleware qui vérifie si l'utilisateur est authentifié
    et redirige vers la page de login si nécessaire
    """
    # Liste des routes non protégées
    public_paths = [
        '/login',          # Redirection vers la page de login
        '/auth/login-page',  # Page de login
        '/auth/login',     # Authentification Google
        '/auth/login/google/callback',  # Callback Google
        '/auth/logout',    # Déconnexion
        '/auth/admin-login', # Auth admin
        '/favicon.ico',    # Favicon
        '/_dash-',         # Assets Dash (requis pour que le CSS fonctionne sur la page de login)
        '/assets/',        # Autres assets
        '/api/email/',     # Endpoints webhook email (pas d'auth requise)
        '/api/support/'    # Endpoints API support (pas d'auth requise)
    ]
    
    # Vérifier si l'utilisateur est authentifié ou si la route est publique
    if not current_user.is_authenticated:
        # Vérifier si le chemin actuel est public
        if not any(request.path.startswith(path) for path in public_paths):
            return redirect('/auth/login-page')  # Redirection vers la nouvelle page de login
    
    # Si tout est OK, continuer
    return None
