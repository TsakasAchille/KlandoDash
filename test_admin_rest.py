#!/usr/bin/env python3
"""
Script pour tester les fonctions d'administration avec l'API REST Supabase
"""
from dash_apps.utils.admin_db_rest import (
    get_all_authorized_users,
    is_user_authorized,
    get_user_role
)

print("Test des fonctions d'administration avec l'API REST Supabase")
print("-----------------------------------------------------------\n")

# Test 1: Récupérer tous les utilisateurs
print("Test 1: Récupérer tous les utilisateurs")
users = get_all_authorized_users()
print(f"Nombre d'utilisateurs: {len(users)}")
for i, user in enumerate(users[:3], 1):  # Limiter à 3 pour éviter un affichage trop long
    email = user.get('email')
    masked_email = f"{email[:3]}***@***{email.split('@')[1][-3:]}" if email else "N/A"
    print(f"  {i}. {masked_email} - Rôle: {user.get('role')} - Actif: {user.get('active')}")
if len(users) > 3:
    print(f"  ... et {len(users) - 3} autres utilisateurs")
print()

# Test 2: Vérifier si un utilisateur est autorisé
print("Test 2: Vérifier si un utilisateur est autorisé")
# Testez avec un email qui existe dans votre base
test_email = "admin@klando-sn.com"  # Email qui devrait exister
is_authorized = is_user_authorized(test_email)
print(f"L'utilisateur {test_email} est autorisé: {is_authorized}")
print()

# Test 3: Récupérer le rôle d'un utilisateur
print("Test 3: Récupérer le rôle d'un utilisateur")
role = get_user_role(test_email)
print(f"Le rôle de {test_email} est: {role}")
print()

print("Tests terminés !")
