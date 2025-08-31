from flask import Blueprint, redirect, url_for, session, request, flash, current_app, render_template
from flask_login import login_required, current_user, login_user
from dash_apps.auth.oauth import google_login, google_callback, logout as oauth_logout
from dash_apps.auth.models import User
from dash_apps.auth.admin_auth import login_admin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dash_apps.config import Config

# Configuration SQLAlchemy pour l'API des tags
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
DBSession = sessionmaker(bind=engine)

# Création du Blueprint pour l'authentification
auth_bp = Blueprint('auth', __name__, template_folder='../templates')

# Route pour afficher la page de login
@auth_bp.route('/login-page')
def show_login():
    """Affiche la page de login"""
    # Pour débugging, forcer la déconnexion de l'utilisateur actuel
    from flask_login import logout_user
    logout_user()
    session.clear()
    
    # Rediriger vers la page de login Dash
    return redirect('/login')

@auth_bp.route('/login')
def login():
    """Route pour l'authentification Google"""
    return google_login()
    
# Route pour l'authentification admin    
@auth_bp.route('/admin-login', methods=['POST'])
def admin_login():
    """Authentification par identifiants admin"""
    import sys
    try:
        sys.stderr.write("=== ADMIN LOGIN BLUEPRINT APPELÉ ===\n")
        sys.stderr.flush()
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        sys.stderr.write(f"DEBUG Admin Login - Username: '{username}', Password: '{password}'\n")
        sys.stderr.flush()
        
        if login_admin(username, password):
            sys.stderr.write("DEBUG: Connexion admin réussie\n")
            sys.stderr.flush()
            return redirect('/')
        else:
            sys.stderr.write("DEBUG: Échec connexion admin\n")
            sys.stderr.flush()
            flash('Identifiants administrateur incorrects', 'error')
            return redirect('/login')
    except Exception as e:
        sys.stderr.write(f"ERREUR DANS ADMIN LOGIN: {str(e)}\n")
        sys.stderr.flush()
        import traceback
        sys.stderr.write(f"TRACEBACK: {traceback.format_exc()}\n")
        sys.stderr.flush()
        return redirect('/login')

@auth_bp.route('/login/google/callback')
def google_auth():
    """Route de callback pour l'authentification Google"""
    # Utiliser la fonction du module oauth.py
    return google_callback()

@auth_bp.route('/logout')
@login_required
def logout():
    """Route de déconnexion"""
    # Utiliser la fonction du module oauth.py
    return oauth_logout()

# Routes pour la gestion des utilisateurs (admin)
@auth_bp.route('/users/manage')
@login_required
def manage_users():
    if not current_user.admin:
        flash('Accès refusé. Vous devez être administrateur.', 'danger')
        return redirect('/')
    users = db_session.query(User).all()
    return users  # Ce sera géré par un callback Dash

# API pour gérer les tags d'utilisateurs
@auth_bp.route('/api/users/<int:user_id>/tags', methods=['POST'])
@login_required
def add_user_tag(user_id):
    if not current_user.admin:
        return {"success": False, "error": "Accès refusé"}, 403

    user = db_session.query(User).get(user_id)
    if not user:
        return {"success": False, "error": "Utilisateur non trouvé"}, 404

    tag = request.json.get('tag')
    if not tag:
        return {"success": False, "error": "Tag non spécifié"}, 400

    success = user.add_tag(tag)
    if success:
        db_session.commit()
        return {"success": True, "tags": user.get_tags_list()}
    return {"success": False, "error": "Le tag existe déjà"}, 400

@auth_bp.route('/api/users/<int:user_id>/tags/<tag>', methods=['DELETE'])
@login_required
def remove_user_tag(user_id, tag):
    if not current_user.admin:
        return {"success": False, "error": "Accès refusé"}, 403

    user = db_session.query(User).get(user_id)
    if not user:
        return {"success": False, "error": "Utilisateur non trouvé"}, 404

    success = user.remove_tag(tag)
    if success:
        db_session.commit()
        return {"success": True, "tags": user.get_tags_list()}
    return {"success": False, "error": "Tag non trouvé"}, 404
