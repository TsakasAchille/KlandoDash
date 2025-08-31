# Standard libraries
import os
import json
import secrets

# Autoriser HTTP pour le développement local uniquement
# Ne jamais activer ceci en production !
if not os.environ.get('RENDER'):  # Seulement en développement local
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Third-party libraries
import requests
from flask import session, redirect, flash, url_for, request
from flask_login import login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient

# Internal imports
from dash_apps.config import Config
from dash_apps.auth.models import User
from dash_apps.core.database import get_session
from dash_apps.models.authorized_user import DashAuthorizedUser

# Configuration OAuth pour Google
GOOGLE_CLIENT_ID = Config.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = Config.GOOGLE_CLIENT_SECRET
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Client OAuth 2
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def setup_oauth(app):
    """
    Configure l'authentification OAuth avec les clés d'API Google
    """
    # Augmenter la durée de session pour éviter les problèmes de state
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 heure
    app.config['SESSION_COOKIE_SECURE'] = False  # Permet les cookies en HTTP
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Protège les cookies des scripts

def get_google_provider_cfg():
    """
    Récupère la configuration du fournisseur Google OAuth
    """
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def google_login():
    """
    Démarre le processus d'authentification Google
    en suivant le flux OAuth2 standard
    """
    # Nettoyer la session et la rendre permanente
    session.clear()
    session.permanent = True
    
    # Récupérer l'endpoint d'autorisation de Google
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    # Préparer la requête pour la connexion Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=Config.OAUTH_REDIRECT_URI,  # Le /callback est déjà inclus dans la config
        scope=["openid", "email", "profile"],
    )
    
    # Rediriger l'utilisateur vers Google
    return redirect(request_uri)

def google_callback():
    """
    Fonction de callback après l'authentification Google
    Suit le flux OAuth2 standard pour échanger le code contre un token
    """
    try:
        # Récupérer le code d'autorisation envoyé par Google
        code = request.args.get("code")
        if not code:
            raise Exception("Code d'autorisation manquant dans la réponse de Google")
            
        # Récupérer l'endpoint de token depuis la configuration Google
        google_provider_cfg = get_google_provider_cfg()
        token_endpoint = google_provider_cfg["token_endpoint"]
        
        # Préparer la requête pour obtenir les tokens
        token_url, headers, body = client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=request.base_url,
            code=code
        )
        
        # Envoyer la requête pour obtenir les tokens
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        
        # Analyser la réponse du token
        client.parse_request_body_response(json.dumps(token_response.json()))
        
        # Récupérer les informations de l'utilisateur
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)
        user_info = userinfo_response.json()
        
        # Vérifier que l'email est vérifié
        if not user_info.get("email_verified", False):
            raise Exception("Email non vérifié par Google")
            
        # Extraire les informations nécessaires
        email = user_info.get('email', '')
        name = user_info.get('name', '')
        picture = user_info.get('picture', '')
        user_id = user_info.get('sub', '')  # ID unique Google
        
    except Exception as e:
        error_str = str(e)
        print(f"Erreur d'authentification: {str(e)}")
        
        # Créer un message d'erreur approprié
        if "access_denied" in error_str.lower():
            error_msg = "⚠️ ATTENTION : ÉCHEC DE CONNEXION - Accès refusé par Google. Veuillez vérifier votre compte ou contacter l'administrateur."
            error_category = "danger"
        elif "mismatching_state" in error_str.lower():
            error_msg = "⚠️ ATTENTION : ÉCHEC DE CONNEXION - Erreur de sécurité. Veuillez réessayer ou vider le cache de votre navigateur."
            error_category = "warning"
        elif "invalid_client" in error_str.lower():
            error_msg = "⚠️ ATTENTION : ÉCHEC DE CONNEXION - Configuration incorrecte de l'authentification. Contactez l'administrateur."
            error_category = "danger"
        elif "missing_token" in error_str.lower():
            error_msg = "⚠️ ATTENTION : ÉCHEC DE CONNEXION - Vous n'êtes pas autorisé à accéder à cette application. Veuillez contacter l'administrateur."
            error_category = "danger"
        else:
            error_msg = f"⚠️ ATTENTION : ÉCHEC DE CONNEXION - Une erreur s'est produite : {error_str}"
            error_category = "danger"
        
        # Nettoyer la session
        session.clear()
        session.modified = True
        
        # Afficher le message d'erreur uniquement via flash
        flash(error_msg, error_category)
        return redirect('/login')
    
    # Si on n'a pas pu récupérer l'email, c'est une erreur
    if not email:
        error_msg = f"⚠️ ATTENTION : ÉCHEC DE CONNEXION - Impossible de récupérer l'email de l'utilisateur."
        session.clear()
        session.modified = True
        flash(error_msg, "danger")
        return redirect('/login')
    
    # Vérifier si l'email est autorisé dans la base de données Supabase
    authorized_user = None
    try:
        with get_session() as db_session:
            authorized_user = db_session.query(DashAuthorizedUser).filter(
                DashAuthorizedUser.email == email,
                DashAuthorizedUser.active == True
            ).first()
    except Exception as e:
        print(f"Erreur lors de la vérification de l'autorisation dans la base de données: {str(e)}")
        error_msg = f"⚠️ ATTENTION : ERREUR INTERNE - Une erreur s'est produite lors de la vérification de vos droits d'accès. Veuillez contacter l'administrateur."
        session.clear()
        session.modified = True
        flash(error_msg, "danger")
        return redirect('/login')
    
    # Vérifier si l'utilisateur est autorisé
    if not authorized_user:
        print(f"Email non autorisé: {email} - Non présent dans la table dash_authorized_users ou compte inactif")
        error_msg = f"⚠️ ATTENTION : ÉCHEC DE CONNEXION - Vous n'êtes pas autorisé à accéder à cette application. Veuillez contacter l'administrateur."
        
        # Nettoyer la session
        session.clear()
        # Ne pas stocker le message d'erreur dans la session pour u00e9viter les doublons
        session.modified = True
        
        # Afficher le message d'erreur uniquement via flash
        flash(error_msg, "danger")
        return redirect('/login')
    
    # Sans base de données, on crée un User en mémoire
    user = User(
        id=user_id,
        email=email,
        name=name,
        profile_pic=picture,
        tags=''
    )
    
    # Connecter l'utilisateur avec remember=True pour maintenir la session plus longtemps
    login_user(user, remember=True)
    
    # Stockage dans la session
    session['logged_in'] = True
    session['user_id'] = user_id
    session['user_email'] = email
    session['user_name'] = name
    session['profile_pic'] = picture
    session.modified = True
    
    print(f"Utilisateur connecté: {email}")
    return redirect('/')

def logout():
    """
    Déconnexion complète de l'utilisateur - supprime toutes les sessions
    """
    # Déconnecter l'utilisateur via Flask-Login
    logout_user()
    
    # Effacer complètement la session
    session.clear()
    session.modified = True
    
    # Rediriger vers la page de login
    return redirect('/login')