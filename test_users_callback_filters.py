#!/usr/bin/env python3
"""
Test script for users callback filters to diagnose filter flow issues.
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

def test_users_callback_filters():
    """Test the users callback filter processing."""
    print("=" * 80)
    print("TESTING USERS CALLBACK FILTERS")
    print("=" * 80)
    
    try:
        from dash_apps.callbacks.users_callbacks import update_users_table
        from dash_apps.services.users_table_service import UsersTableService
        
        print("\n1. Testing callback with no filters...")
        try:
            result = update_users_table(current_page=1, refresh_clicks=None, filters={})
            print(f"   No filters result: {type(result)}")
            if isinstance(result, list) and len(result) > 0:
                print(f"   Result has {len(result)} components")
            else:
                print("   No result components")
        except Exception as e:
            print(f"   ERROR with no filters: {e}")
        
        print("\n2. Testing callback with role filter...")
        try:
            filters = {"role": "user"}
            result = update_users_table(current_page=1, refresh_clicks=None, filters=filters)
            print(f"   Role filter result: {type(result)}")
            if isinstance(result, list) and len(result) > 0:
                print(f"   Result has {len(result)} components")
            else:
                print("   No result components")
        except Exception as e:
            print(f"   ERROR with role filter: {e}")
        
        print("\n3. Testing callback with gender filter...")
        try:
            filters = {"gender": "man"}
            result = update_users_table(current_page=1, refresh_clicks=None, filters=filters)
            print(f"   Gender filter result: {type(result)}")
            if isinstance(result, list) and len(result) > 0:
                print(f"   Result has {len(result)} components")
            else:
                print("   No result components")
        except Exception as e:
            print(f"   ERROR with gender filter: {e}")
        
        print("\n4. Testing callback with text filter...")
        try:
            filters = {"text": "test"}
            result = update_users_table(current_page=1, refresh_clicks=None, filters=filters)
            print(f"   Text filter result: {type(result)}")
            if isinstance(result, list) and len(result) > 0:
                print(f"   Result has {len(result)} components")
            else:
                print("   No result components")
        except Exception as e:
            print(f"   ERROR with text filter: {e}")
        
        print("\n5. Testing filter update callback...")
        try:
            from dash_apps.callbacks.users_callbacks import update_filters
            
            # Test role filter update
            result = update_filters(
                n_clicks=1,
                search_text="",
                date_from=None,
                date_to=None,
                date_filter_type="range",
                single_date=None,
                date_sort="desc",
                role="user",
                driver_validation="all",
                gender="all",
                rating_operator="all",
                rating_value=3,
                current_filters={}
            )
            print(f"   Filter update result: {result}")
            
        except Exception as e:
            print(f"   ERROR in filter update: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n6. Testing direct service calls with different filter formats...")
        # Test if the service handles different filter formats correctly
        test_filters = [
            {},
            {"role": "user"},
            {"role": "all"},  # Should be ignored
            {"gender": "man"},
            {"gender": "all"},  # Should be ignored
            {"text": "test"},
            {"text": ""},  # Should be ignored
            {"role": "user", "gender": "man"},
        ]
        
        for i, filters in enumerate(test_filters):
            try:
                result = UsersTableService.get_users_page(page=1, page_size=5, filters=filters)
                count = result.get('total_count', 0)
                users = len(result.get('users', []))
                print(f"   Test {i+1} - Filters: {filters} -> Users: {users}, Total: {count}")
            except Exception as e:
                print(f"   Test {i+1} - ERROR: {e}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("CALLBACK FILTER TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_users_callback_filters()
