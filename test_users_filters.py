#!/usr/bin/env python3
"""
Test script for users table filters to diagnose filter issues.
"""
import os
import sys
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set debug environment
os.environ['DEBUG_USERS'] = 'true'

def test_users_filters():
    """Test the users table filters with various scenarios."""
    print("=" * 80)
    print("TESTING USERS TABLE FILTERS")
    print("=" * 80)
    
    try:
        from dash_apps.services.users_table_service import UsersTableService
        from dash_apps.utils.supabase_client import supabase
        
        print("\n1. Testing no filters (baseline)...")
        result = UsersTableService.get_users_page(page=1, page_size=10)
        baseline_count = result.get('total_count', 0)
        baseline_users = len(result.get('users', []))
        print(f"   No filters - Users: {baseline_users}, Total: {baseline_count}")
        
        print("\n2. Testing role filter...")
        # Test role filter
        filters = {"role": "user"}
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        role_count = result.get('total_count', 0)
        role_users = len(result.get('users', []))
        print(f"   Role 'user' - Users: {role_users}, Total: {role_count}")
        
        # Test driver role
        filters = {"role": "driver"}
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        driver_count = result.get('total_count', 0)
        driver_users = len(result.get('users', []))
        print(f"   Role 'driver' - Users: {driver_users}, Total: {driver_count}")
        
        print("\n3. Testing gender filter...")
        # Test gender filter
        filters = {"gender": "man"}
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        gender_count = result.get('total_count', 0)
        gender_users = len(result.get('users', []))
        print(f"   Gender 'man' - Users: {gender_users}, Total: {gender_count}")
        
        print("\n4. Testing text search...")
        # Test text search
        filters = {"text": "test"}
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        text_count = result.get('total_count', 0)
        text_users = len(result.get('users', []))
        print(f"   Text 'test' - Users: {text_users}, Total: {text_count}")
        
        # Test with actual user data
        if baseline_users > 0:
            first_user = result.get('users', [{}])[0] if result.get('users') else {}
            if first_user.get('display_name'):
                search_term = first_user['display_name'][:3]  # First 3 chars
                filters = {"text": search_term}
                result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
                search_count = result.get('total_count', 0)
                search_users = len(result.get('users', []))
                print(f"   Text '{search_term}' - Users: {search_users}, Total: {search_count}")
        
        print("\n5. Testing combined filters...")
        # Test combined filters
        filters = {"role": "user", "gender": "man"}
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        combined_count = result.get('total_count', 0)
        combined_users = len(result.get('users', []))
        print(f"   Role 'user' + Gender 'man' - Users: {combined_users}, Total: {combined_count}")
        
        print("\n6. Testing direct Supabase queries...")
        # Test direct Supabase queries to verify filters work at DB level
        try:
            # Test role filter directly
            response = supabase.table('users').select('uid', count='exact').eq('role', 'user').execute()
            direct_role_count = getattr(response, 'count', 0)
            print(f"   Direct Supabase role 'user' count: {direct_role_count}")
            
            # Test gender filter directly
            response = supabase.table('users').select('uid', count='exact').eq('gender', 'man').execute()
            direct_gender_count = getattr(response, 'count', 0)
            print(f"   Direct Supabase gender 'man' count: {direct_gender_count}")
            
            # Test text search directly
            response = supabase.table('users').select('uid', count='exact').ilike('display_name', '%test%').execute()
            direct_text_count = getattr(response, 'count', 0)
            print(f"   Direct Supabase text search 'test' count: {direct_text_count}")
            
        except Exception as e:
            print(f"   ERROR in direct Supabase queries: {e}")
        
        print("\n7. Testing invalid filters...")
        # Test invalid filters
        filters = {"role": "invalid_role"}
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        invalid_count = result.get('total_count', 0)
        invalid_users = len(result.get('users', []))
        print(f"   Invalid role - Users: {invalid_users}, Total: {invalid_count}")
        
        print("\n8. Testing empty filters...")
        # Test empty filters
        filters = {"role": "", "gender": "", "text": ""}
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        empty_count = result.get('total_count', 0)
        empty_users = len(result.get('users', []))
        print(f"   Empty filters - Users: {empty_users}, Total: {empty_count}")
        
        print(f"\n9. Summary:")
        print(f"   Baseline (no filters): {baseline_count} users")
        print(f"   Role filtering working: {'✓' if role_count != baseline_count or driver_count != baseline_count else '✗'}")
        print(f"   Gender filtering working: {'✓' if gender_count != baseline_count else '✗'}")
        print(f"   Text search working: {'✓' if text_count != baseline_count else '✗'}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("FILTER TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_users_filters()
