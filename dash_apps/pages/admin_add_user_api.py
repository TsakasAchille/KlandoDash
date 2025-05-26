from flask import jsonify, request, session
from dash_apps.utils.admin_db import add_authorized_user, is_admin

def setup_add_user_api(server):
    """Configure le point d'API pour l'ajout d'utilisateur"""
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
        
        # Ajouter l'utilisateur
        success, message = add_authorized_user(target_email, role, user_email, notes)
        
        return jsonify({
            'success': success,
            'message': message
        })
