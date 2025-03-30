import os
import json
import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    """Initialise Firebase en utilisant soit un fichier local (développement) 
    soit des variables d'environnement (déploiement)"""
    
    try:
        # Option 1: Fichier de credentials local (pour développement)
        cred_path = "src/keys/klando-d3cb3-firebase-adminsdk-uak7b-7af3798d36.json"
        if os.path.exists(cred_path):
            print("Initialisation Firebase depuis le fichier local")
            cred = credentials.Certificate(cred_path)
        
        # Option 2: Variable d'environnement (pour Render)
        elif os.environ.get('FIREBASE_CREDENTIALS'):
            print("Initialisation Firebase depuis la variable d'environnement")
            cred_dict = json.loads(os.environ.get('FIREBASE_CREDENTIALS'))
            cred = credentials.Certificate(cred_dict)
        
        else:
            raise Exception("Aucune information d'authentification Firebase trouvée")
            
        # Initialiser l'application Firebase
        return firebase_admin.initialize_app(cred)
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation de Firebase: {e}")
        return None