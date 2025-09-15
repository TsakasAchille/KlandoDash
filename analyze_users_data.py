#!/usr/bin/env python3
"""
Script pour analyser les données users en base SQL et comprendre les erreurs de validation.
"""
import os
import sys
import json
from collections import Counter

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(__file__))

# Activer le debug
os.environ['DEBUG_USERS'] = 'true'

from dash_apps.utils.supabase_client import supabase
from dash_apps.models.config_models import UserModel
from dash_apps.utils.callback_logger import CallbackLogger


def analyze_users_data():
    """Analyse les données users en base pour comprendre les erreurs de validation."""
    
    print("🔍 ANALYSE DES DONNÉES USERS EN BASE SQL")
    print("=" * 80)
    
    try:
        # Récupérer tous les users avec les champs problématiques
        print("📊 Récupération des données users...")
        
        response = supabase.table('users').select(
            'uid, display_name, email, role, gender, rating, rating_count, '
            'created_at, is_driver_doc_validated, phone_number'
        ).limit(100).execute()
        
        if not response.data:
            print("❌ Aucune donnée trouvée")
            return
        
        total_users = len(response.data)
        print(f"✅ {total_users} utilisateurs récupérés")
        
        # Analyser les erreurs de validation
        valid_users = []
        invalid_users = []
        validation_errors = Counter()
        gender_values = Counter()
        role_values = Counter()
        
        print("\n📋 ANALYSE DES VALIDATIONS PYDANTIC")
        print("-" * 50)
        
        for i, user_data in enumerate(response.data):
            try:
                # Tenter la validation Pydantic
                user = UserModel(**user_data)
                valid_users.append(user_data)
                
                # Compter les valeurs valides
                if user.gender:
                    gender_values[str(user.gender)] += 1
                if user.role:
                    role_values[str(user.role)] += 1
                    
            except Exception as e:
                invalid_users.append({
                    'user_data': user_data,
                    'error': str(e)
                })
                
                # Analyser le type d'erreur
                error_str = str(e)
                if 'gender' in error_str:
                    validation_errors['gender_invalid'] += 1
                    if user_data.get('gender'):
                        gender_values[user_data['gender']] += 1
                elif 'role' in error_str:
                    validation_errors['role_invalid'] += 1
                    if user_data.get('role'):
                        role_values[user_data['role']] += 1
                elif 'rating' in error_str:
                    validation_errors['rating_invalid'] += 1
                elif 'uid' in error_str:
                    validation_errors['uid_invalid'] += 1
                else:
                    validation_errors['other'] += 1
        
        # Afficher les résultats
        print(f"✅ Utilisateurs valides: {len(valid_users)}")
        print(f"❌ Utilisateurs invalides: {len(invalid_users)}")
        print(f"📊 Taux de validation: {len(valid_users)/total_users*100:.1f}%")
        
        print("\n🔍 TYPES D'ERREURS DE VALIDATION")
        print("-" * 40)
        for error_type, count in validation_errors.most_common():
            print(f"  {error_type}: {count} erreurs")
        
        print("\n👤 VALEURS GENDER TROUVÉES")
        print("-" * 30)
        for gender, count in gender_values.most_common():
            valid_marker = "✅" if gender in ['MALE', 'FEMALE', 'OTHER', 'NOT_SPECIFIED'] else "❌"
            print(f"  {valid_marker} '{gender}': {count} utilisateurs")
        
        print("\n🎭 VALEURS ROLE TROUVÉES")
        print("-" * 25)
        for role, count in role_values.most_common():
            valid_marker = "✅" if role in ['USER', 'DRIVER', 'ADMIN', 'MODERATOR'] else "❌"
            print(f"  {valid_marker} '{role}': {count} utilisateurs")
        
        # Afficher quelques exemples d'erreurs
        if invalid_users:
            print("\n🚨 EXEMPLES D'ERREURS DE VALIDATION")
            print("-" * 45)
            for i, invalid in enumerate(invalid_users[:5]):  # 5 premiers exemples
                user_data = invalid['user_data']
                error = invalid['error']
                print(f"\n  Exemple {i+1}:")
                print(f"    UID: {user_data.get('uid', 'N/A')[:20]}...")
                print(f"    Nom: {user_data.get('display_name', 'N/A')}")
                print(f"    Gender: '{user_data.get('gender', 'N/A')}'")
                print(f"    Role: '{user_data.get('role', 'N/A')}'")
                print(f"    Erreur: {error}")
        
        # Proposer des corrections
        print("\n💡 RECOMMANDATIONS DE CORRECTION")
        print("-" * 40)
        
        if validation_errors['gender_invalid'] > 0:
            print("🔧 GENDER:")
            print("  - Remplacer 'MAN' → 'MALE'")
            print("  - Remplacer 'WOMAN' → 'FEMALE'")
            print("  - Remplacer valeurs vides → 'NOT_SPECIFIED'")
        
        if validation_errors['role_invalid'] > 0:
            print("🔧 ROLE:")
            print("  - Normaliser en majuscules: 'user' → 'USER'")
            print("  - Vérifier les rôles non standard")
        
        # Générer un script de migration
        generate_migration_script(gender_values, role_values)
        
        CallbackLogger.log_callback(
            "users_data_analysis_complete",
            {
                "total_users": total_users,
                "valid_users": len(valid_users),
                "invalid_users": len(invalid_users),
                "validation_rate": len(valid_users)/total_users*100,
                "main_errors": dict(validation_errors.most_common(3))
            },
            status="SUCCESS",
            extra_info="Analyse des données users terminée"
        )
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        CallbackLogger.log_callback(
            "users_data_analysis_error",
            {"error": str(e)},
            status="ERROR",
            extra_info="Échec de l'analyse des données users"
        )


def generate_migration_script(gender_values, role_values):
    """Génère un script de migration pour corriger les données."""
    
    print("\n📝 GÉNÉRATION DU SCRIPT DE MIGRATION")
    print("-" * 45)
    
    migration_script = """
-- Script de migration pour corriger les données users
-- Généré automatiquement par analyze_users_data.py

-- Correction des valeurs GENDER
UPDATE users SET gender = 'MALE' WHERE gender = 'MAN';
UPDATE users SET gender = 'FEMALE' WHERE gender = 'WOMAN';
UPDATE users SET gender = 'NOT_SPECIFIED' WHERE gender IS NULL OR gender = '';

-- Correction des valeurs ROLE (normalisation en majuscules)
UPDATE users SET role = 'USER' WHERE LOWER(role) = 'user';
UPDATE users SET role = 'DRIVER' WHERE LOWER(role) = 'driver';
UPDATE users SET role = 'ADMIN' WHERE LOWER(role) = 'admin';
UPDATE users SET role = 'MODERATOR' WHERE LOWER(role) = 'moderator';
UPDATE users SET role = 'USER' WHERE role IS NULL OR role = '';

-- Vérification post-migration
SELECT 
    gender, COUNT(*) as count 
FROM users 
GROUP BY gender 
ORDER BY count DESC;

SELECT 
    role, COUNT(*) as count 
FROM users 
GROUP BY role 
ORDER BY count DESC;
"""
    
    # Sauvegarder le script
    script_path = "migration_users_data.sql"
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(migration_script)
    
    print(f"✅ Script de migration généré: {script_path}")
    
    # Créer aussi un validateur Pydantic amélioré
    create_improved_validator()


def create_improved_validator():
    """Crée un validateur Pydantic amélioré pour gérer les valeurs invalides."""
    
    validator_code = '''
@field_validator('gender', mode='before')
@classmethod
def validate_gender_with_normalization(cls, v):
    """Normalise le genre avec gestion des valeurs invalides."""
    if v is None or v == '':
        return UserGender.NOT_SPECIFIED
    
    # Normalisation des valeurs courantes
    gender_mapping = {
        'MAN': 'MALE',
        'WOMAN': 'FEMALE',
        'man': 'MALE',
        'woman': 'FEMALE',
        'male': 'MALE',
        'female': 'FEMALE',
        'M': 'MALE',
        'F': 'FEMALE',
        'H': 'MALE',  # Homme
        'F': 'FEMALE'  # Femme
    }
    
    if isinstance(v, str):
        normalized = gender_mapping.get(v.strip(), v.upper())
        try:
            return UserGender(normalized)
        except ValueError:
            # Si la valeur n'est pas reconnue, utiliser NOT_SPECIFIED
            return UserGender.NOT_SPECIFIED
    
    return v

@field_validator('role', mode='before')
@classmethod
def validate_role_with_normalization(cls, v):
    """Normalise le rôle avec gestion des valeurs invalides."""
    if v is None or v == '':
        return UserRole.USER
    
    if isinstance(v, str):
        normalized = v.strip().upper()
        try:
            return UserRole(normalized)
        except ValueError:
            # Si le rôle n'est pas reconnu, utiliser USER par défaut
            return UserRole.USER
    
    return v
'''
    
    print("💡 Validateur Pydantic amélioré généré (voir console)")
    print("   À ajouter dans UserModel pour gérer automatiquement les valeurs invalides")


if __name__ == "__main__":
    analyze_users_data()
