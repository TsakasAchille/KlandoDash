"""APIs pour la gestion des utilisateurs admin"""

from flask import jsonify, request, session
from dash_apps.utils.admin_db import (
    add_authorized_user, update_user_status, update_user_role,
    is_admin, delete_user
)

def setup_admin_api(server):
    """Configure tous les points d'API pour l'administration des utilisateurs"""
    
    # API pour ajouter un utilisateur
    @server.route('/api/admin/add-user', methods=['POST'])
    def add_user_api():
        # Vérifier que l'utilisateur est admin
        user_email = session.get('user_email')
        if not is_admin(user_email):
            return jsonify({
                'success': False,
                'message': 'Vous n\'êtes pas autorisé à effectuer cette action'
            }), 403
            
        # Récupérer les données de la requête
        data = request.get_json()
        if not data or 'email' not in data or 'role' not in data:
            return jsonify({
                'success': False,
                'message': 'Paramètres manquants'
            }), 400
            
        # Récupérer les informations de l'utilisateur à ajouter
        target_email = data.get('email')
        role = data.get('role')
        notes = data.get('notes', '')
        
        # Vérifier que le rôle est valide
        valid_roles = ['admin', 'user', 'viewer']
        if role not in valid_roles:
            return jsonify({
                'success': False,
                'message': f'Rôle invalide. Les rôles valides sont: {", ".join(valid_roles)}'
            }), 400
            
        # Ajouter l'utilisateur à la base de données
        success, message = add_authorized_user(target_email, role, user_email, notes)
        
        return jsonify({
            'success': success,
            'message': message
        })

    # API pour activer/désactiver un utilisateur
    @server.route('/api/admin/toggle-user-status', methods=['POST'])
    def toggle_user_status_api():
        # Vérifier que l'utilisateur est admin
        user_email = session.get('user_email')
        if not is_admin(user_email):
            return jsonify({
                'success': False,
                'message': 'Vous n\'êtes pas autorisé à effectuer cette action'
            }), 403

        # Récupérer les données de la requête
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'message': 'Paramètres manquants'
            }), 400

        # Récupérer l'email de l'utilisateur et son statut actuel
        target_email = data.get('email')
        active = data.get('active', None)

        # Mettre à jour le statut
        success, message = update_user_status(target_email, active, user_email)

        return jsonify({
            'success': success,
            'message': message
        })

    # API pour changer le rôle d'un utilisateur
    @server.route('/api/admin/change-user-role', methods=['POST'])
    def change_user_role_api():
        # Vérifier que l'utilisateur est admin
        user_email = session.get('user_email')
        if not is_admin(user_email):
            return jsonify({
                'success': False,
                'message': 'Vous n\'êtes pas autorisé à effectuer cette action'
            }), 403
            
        # Récupérer les données de la requête
        data = request.get_json()
        if not data or 'email' not in data or 'role' not in data:
            return jsonify({
                'success': False,
                'message': 'Paramètres manquants'
            }), 400

        # Récupérer l'email de l'utilisateur et le nouveau rôle
        target_email = data.get('email')
        new_role = data.get('role')

        # Vérifier que le rôle est valide
        valid_roles = ['admin', 'user', 'viewer']
        if new_role not in valid_roles:
            return jsonify({
                'success': False,
                'message': f'Rôle invalide. Les rôles valides sont: {", ".join(valid_roles)}'
            }), 400

        # Mettre à jour le rôle
        success, message = update_user_role(target_email, new_role, user_email)

        return jsonify({
            'success': success,
            'message': message
        })

    # API pour supprimer un utilisateur
    @server.route('/api/admin/delete-user', methods=['POST'])
    def delete_user_api():
        # Vérifier que l'utilisateur est admin
        user_email = session.get('user_email')
        if not is_admin(user_email):
            return jsonify({
                'success': False,
                'message': 'Vous n\'êtes pas autorisé à effectuer cette action'
            }), 403
            
        # Récupérer les données de la requête
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'message': 'Paramètres manquants'
            }), 400

        # Récupérer l'email de l'utilisateur à supprimer
        target_email = data.get('email')

        # Supprimer l'utilisateur
        success, message = delete_user(target_email, user_email)

        return jsonify({
            'success': success,
            'message': message
        })

    return server
