from dash import callback_context, no_update
from dash.dependencies import Input, Output, State, ALL
from flask import jsonify, request, session
from dash_apps.utils.admin_db import update_user_status, update_user_role, is_admin, delete_user

def setup_admin_api(app, server):
    """Configure les points d'API pour l'administration des utilisateurs"""
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

        # Si le statut n'est pas fourni, inverser le statut actuel
        # Nous gérons cela du côté serveur car nous ne voulons pas envoyer
        # le statut actuel au client JavaScript pour éviter les manipulations
        success, message = update_user_status(target_email, not active, user_email)

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
        
        # Ne pas permettre la suppression de son propre compte
        if target_email == user_email:
            return jsonify({
                'success': False,
                'message': 'Vous ne pouvez pas supprimer votre propre compte'
            }), 400
            
        # Supprimer l'utilisateur
        success, message = delete_user(target_email, user_email)
        
        return jsonify({
            'success': success,
            'message': message
        })