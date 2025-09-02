#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier le contenu de la base de données
"""
import os
import sys
sys.path.append('/home/tsakas/Desktop/KlandoDash')

from dash_apps.core.database import get_engine, SessionLocal
from dash_apps.models.user import User
from sqlalchemy import text
import traceback

def check_database():
    print("=== DIAGNOSTIC BASE DE DONNÉES ===")
    
    try:
        # Test de connexion
        engine = get_engine()
        print(f"✓ Engine créé: {engine.url}")
        
        # Test de connexion directe
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).fetchone()
            print(f"✓ Connexion réussie: {result}")
        
        # Test avec SessionLocal
        with SessionLocal() as db:
            print("✓ Session créée")
            
            # Vérifier si la table users existe
            try:
                result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")).fetchone()
                if result:
                    print("✓ Table 'users' existe")
                else:
                    print("✗ Table 'users' n'existe pas")
                    return
            except Exception as e:
                print(f"✗ Erreur vérification table: {e}")
                return
            
            # Compter les utilisateurs
            try:
                count = db.query(User).count()
                print(f"✓ Nombre d'utilisateurs: {count}")
            except Exception as e:
                print(f"✗ Erreur comptage utilisateurs: {e}")
                traceback.print_exc()
                return
            
            # Si pas d'utilisateurs, vérifier la structure
            if count == 0:
                print("\n--- STRUCTURE DE LA TABLE ---")
                try:
                    result = db.execute(text("PRAGMA table_info(users)")).fetchall()
                    for row in result:
                        print(f"  {row}")
                except Exception as e:
                    print(f"✗ Erreur structure table: {e}")
            else:
                # Afficher quelques utilisateurs
                print("\n--- PREMIERS UTILISATEURS ---")
                try:
                    users = db.query(User).limit(3).all()
                    for user in users:
                        print(f"  UID: {user.uid}, Email: {user.email}, Nom: {user.display_name}")
                except Exception as e:
                    print(f"✗ Erreur récupération utilisateurs: {e}")
                    traceback.print_exc()
    
    except Exception as e:
        print(f"✗ Erreur générale: {e}")
        traceback.print_exc()

def test_user_repository():
    print("\n=== TEST USER REPOSITORY ===")
    
    try:
        from dash_apps.repositories.user_repository import UserRepository
        
        # Test get_users_paginated
        result = UserRepository.get_users_paginated(page=0, page_size=5, filters={})
        print(f"✓ Repository result: {len(result.get('users', []))} utilisateurs")
        print(f"  Total count: {result.get('total_count', 0)}")
        print(f"  Table rows: {len(result.get('table_rows_data', []))}")
        
        if result.get('users'):
            print("  Premier utilisateur:", result['users'][0].get('email', 'N/A'))
    
    except Exception as e:
        print(f"✗ Erreur UserRepository: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    check_database()
    test_user_repository()
