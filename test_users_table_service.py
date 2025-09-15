#!/usr/bin/env python3
"""
Test script for UsersTableService to diagnose pagination and total count issues.
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

def test_users_table_service():
    """Test the UsersTableService with various scenarios."""
    print("=" * 80)
    print("TESTING USERS TABLE SERVICE")
    print("=" * 80)
    
    try:
        from dash_apps.services.users_table_service import UsersTableService
        from dash_apps.utils.supabase_client import supabase
        
        print("\n1. Testing direct Supabase connection...")
        # Test direct Supabase query to check if we can get total count
        try:
            response = supabase.table('users').select('uid', count='exact').limit(1).execute()
            print(f"   Direct Supabase query - Count: {response.count}")
            print(f"   Response has count attribute: {hasattr(response, 'count')}")
            print(f"   Response count value: {getattr(response, 'count', 'NOT_FOUND')}")
        except Exception as e:
            print(f"   ERROR in direct Supabase query: {e}")
        
        print("\n2. Testing UsersTableService.get_users_page()...")
        # Test the service method
        try:
            result = UsersTableService.get_users_page(page=1, page_size=10)
            print(f"   Service result keys: {list(result.keys())}")
            print(f"   Users count: {len(result.get('users', []))}")
            print(f"   Total count: {result.get('total_count', 'NOT_FOUND')}")
            print(f"   Total pages: {result.get('total_pages', 'NOT_FOUND')}")
            print(f"   Has next: {result.get('has_next', 'NOT_FOUND')}")
            print(f"   Has previous: {result.get('has_previous', 'NOT_FOUND')}")
            
            # Show first few users if available
            users = result.get('users', [])
            if users:
                print(f"\n   First user sample:")
                first_user = users[0]
                for key, value in first_user.items():
                    print(f"     {key}: {value}")
            else:
                print("   No users returned!")
                
        except Exception as e:
            print(f"   ERROR in service method: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n3. Testing with filters...")
        # Test with filters
        try:
            filters = {"role": "user"}
            result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
            print(f"   Filtered result - Users: {len(result.get('users', []))}")
            print(f"   Filtered result - Total: {result.get('total_count', 'NOT_FOUND')}")
        except Exception as e:
            print(f"   ERROR with filters: {e}")
        
        print("\n4. Testing cache behavior...")
        # Test cache
        try:
            # First call (should cache)
            result1 = UsersTableService.get_users_page(page=1, page_size=5)
            print(f"   First call - Total: {result1.get('total_count', 'NOT_FOUND')}")
            
            # Second call (should use cache)
            result2 = UsersTableService.get_users_page(page=1, page_size=5)
            print(f"   Second call - Total: {result2.get('total_count', 'NOT_FOUND')}")
            print(f"   Cache working: {result1.get('total_count') == result2.get('total_count')}")
        except Exception as e:
            print(f"   ERROR testing cache: {e}")
        
        print("\n5. Testing different page sizes...")
        # Test different page sizes
        for page_size in [5, 10, 20]:
            try:
                result = UsersTableService.get_users_page(page=1, page_size=page_size)
                print(f"   Page size {page_size} - Users: {len(result.get('users', []))}, Total: {result.get('total_count', 'NOT_FOUND')}")
            except Exception as e:
                print(f"   ERROR with page size {page_size}: {e}")
        
        print("\n6. Testing raw Supabase count query...")
        # Test raw count query
        try:
            count_response = supabase.table('users').select('*', count='exact').limit(0).execute()
            print(f"   Raw count query - Count: {getattr(count_response, 'count', 'NOT_FOUND')}")
            print(f"   Raw count query - Data length: {len(count_response.data or [])}")
        except Exception as e:
            print(f"   ERROR in raw count query: {e}")
            
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running from the project root directory.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_users_table_service()
