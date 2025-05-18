"""
Module d'authentification admin pour KlandoDash
"""
from dash_apps.config import Config
from dash_apps.auth.models import User
from flask import redirect, request, flash, session
from flask_login import login_user

def login_admin(username, password):
    """
    Authentifie un administrateur avec les identifiants fournis
    """
    # Vérifier les identifiants admin
    if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
        # Créer un utilisateur admin
        admin_user = User(
            id='admin',
            email='admin@klando-sn.com',  # Email fictif mais valide pour la vérification du domaine
            name='Administrateur',
            admin=True
        )
        
        # Connecter l'utilisateur admin
        login_user(admin_user, remember=True)
        
        # Stocker les informations dans la session
        session['logged_in'] = True
        session['user_id'] = 'admin'
        session['user_email'] = 'admin@klando-sn.com'
        session['user_name'] = 'Administrateur'
        session['is_admin'] = True
        session.modified = True
        
        flash('Connecté en tant qu\'administrateur', 'success')
        return True
    
    return False

def handle_admin_login_request():
    """
    Traite une requête d'authentification admin
    """
    username = request.form.get('username')
    password = request.form.get('password')
    
    if login_admin(username, password):
        return redirect('/')
    else:
        flash('Identifiants administrateur incorrects', 'error')
        return redirect('/login')

def is_admin_user():
    """
    Vérifie si l'utilisateur actuel est un administrateur
    """
    from flask_login import current_user
    
    # Vérifier si c'est un admin via l'objet current_user
    is_admin_attr = getattr(current_user, 'admin', False)
    if is_admin_attr:
        return True
        
    # Vérifier via la session
    return session.get('is_admin', False)
