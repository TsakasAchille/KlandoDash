"""
Module d'authentification admin pour KlandoDash
"""
from dash_apps.config import Config
import sys
import os
from flask import request, session, redirect, url_for, render_template_string, flash
from dash_apps.core.database import SessionLocal
from dash_apps.utils.admin_db import add_authorized_user
from dash_apps.models.user import User
from werkzeug.security import check_password_hash

# Mode debug pour les logs (désactivé en production)
_debug_mode = os.getenv('DASH_DEBUG', 'False').lower() == 'true'

def login_admin(username, password):
    """
    Authentifie un administrateur avec les identifiants fournis
    """
    if _debug_mode:
        print(f"DEBUG Admin Login - Username: '{username}', Password: '{password}'")
        print(f"DEBUG Admin Login - Config Username: '{Config.ADMIN_USERNAME}', Config Password: '{Config.ADMIN_PASSWORD}'")
    
    # Vérifier les identifiants admin
    if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
        if _debug_mode:
            print("DEBUG: Identifiants admin corrects, création de l'utilisateur...")
        
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
        
        if _debug_mode:
            print("DEBUG: Session admin créée")
        # S'assurer que l'admin est présent dans la base des utilisateurs autorisés
        try:
            _ok, _msg = add_authorized_user('admin@klando-sn.com', 'admin', 'system', notes='Auto-added via admin login')
            if _debug_mode:
                print(f"DEBUG: add_authorized_user -> ok={_ok} msg={_msg}")
        except Exception as e:
            if _debug_mode:
                print(f"[WARN] Impossible d'ajouter l'admin dans dash_authorized_users: {e}")
        flash('Connecté en tant qu\'administrateur', 'success')
        return True
    
    if _debug_mode:
        print("DEBUG: Identifiants admin incorrects")
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
