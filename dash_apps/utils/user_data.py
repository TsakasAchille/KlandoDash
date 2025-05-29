import pandas as pd
from dash_apps.core.database import engine

# Fonctions de traitement des données utilisateur

def update_user_field(uid, field_name, field_value):
    """
    Met à jour un champ spécifique pour un utilisateur dans la base de données.
    
    Args:
        uid (str): Identifiant unique de l'utilisateur
        field_name (str): Nom du champ à mettre à jour
        field_value: Nouvelle valeur pour le champ
    
    Returns:
        bool: True si la mise à jour a réussi, False sinon
    """
    # Vérifier que l'uid est valide
    if not uid:
        print("Erreur: UID utilisateur non valide.")
        return False
        
    try:
        # Établir une connexion à la base de données
        conn = engine.connect()
        if not conn:
            print("Erreur: Impossible de se connecter à la base de données.")
            return False
            
        # Préparer la requête SQL pour mettre à jour le champ spécifique
        cursor = conn.cursor()
        query = f"UPDATE users SET {field_name} = %s, updated_at = CURRENT_TIMESTAMP WHERE uid = %s"
        cursor.execute(query, (field_value, uid))
        
        # Vérifier si la mise à jour a réussi
        if cursor.rowcount > 0:
            conn.commit()
            cursor.close()
            conn.close()
            print(f"Champ '{field_name}' mis à jour avec succès pour l'utilisateur {uid}.")
            return True
        else:
            conn.rollback()
            cursor.close()
            conn.close()
            print(f"Aucune mise à jour effectuée pour l'utilisateur {uid}. L'utilisateur n'existe peut-être pas.")
            return False
            
    except Exception as e:
        print(f"Erreur lors de la mise à jour du champ '{field_name}' pour l'utilisateur {uid}: {str(e)}")
        # Assurer que la connexion est fermée même en cas d'erreur
        if 'conn' in locals() and conn:
            conn.rollback()
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()
        return False
