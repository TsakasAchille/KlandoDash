#!/usr/bin/env python3
"""
Debug script to check what role and gender values exist in the users table.
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_user_roles():
    """Check what role and gender values exist in the database."""
    print("=" * 80)
    print("DEBUGGING USER ROLES AND GENDERS")
    print("=" * 80)
    
    try:
        from dash_apps.utils.supabase_client import supabase
        
        print("\n1. Checking all unique role values...")
        try:
            # Get all users with their roles
            response = supabase.table('users').select('role').execute()
            roles = [user.get('role') for user in response.data if user.get('role') is not None]
            unique_roles = list(set(roles))
            print(f"   Unique roles found: {unique_roles}")
            print(f"   Total users with roles: {len(roles)}")
            
            # Count each role
            from collections import Counter
            role_counts = Counter(roles)
            for role, count in role_counts.items():
                print(f"   - '{role}': {count} users")
                
        except Exception as e:
            print(f"   ERROR checking roles: {e}")
        
        print("\n2. Checking all unique gender values...")
        try:
            # Get all users with their genders
            response = supabase.table('users').select('gender').execute()
            genders = [user.get('gender') for user in response.data if user.get('gender') is not None]
            unique_genders = list(set(genders))
            print(f"   Unique genders found: {unique_genders}")
            print(f"   Total users with genders: {len(genders)}")
            
            # Count each gender
            from collections import Counter
            gender_counts = Counter(genders)
            for gender, count in gender_counts.items():
                print(f"   - '{gender}': {count} users")
                
        except Exception as e:
            print(f"   ERROR checking genders: {e}")
        
        print("\n3. Checking sample user data...")
        try:
            # Get first 5 users with role and gender
            response = supabase.table('users').select('uid, display_name, role, gender').limit(5).execute()
            print(f"   Sample users:")
            for user in response.data:
                print(f"   - {user.get('display_name', 'No name')}: role='{user.get('role')}', gender='{user.get('gender')}'")
                
        except Exception as e:
            print(f"   ERROR getting sample users: {e}")
        
        print("\n4. Testing specific role queries...")
        # Test queries with actual role values found
        try:
            response = supabase.table('users').select('role').execute()
            roles = [user.get('role') for user in response.data if user.get('role') is not None]
            unique_roles = list(set(roles))
            
            for role in unique_roles[:3]:  # Test first 3 unique roles
                try:
                    count_response = supabase.table('users').select('uid', count='exact').eq('role', role).execute()
                    count = getattr(count_response, 'count', 0)
                    print(f"   Role '{role}' query: {count} users")
                except Exception as e:
                    print(f"   Role '{role}' query ERROR: {e}")
                    
        except Exception as e:
            print(f"   ERROR testing role queries: {e}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("DEBUG COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    debug_user_roles()
