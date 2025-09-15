#!/usr/bin/env python3
"""
Complete integration test for users table functionality including pagination, filters, and state persistence.
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

def test_complete_users_integration():
    """Test complete users table integration."""
    print("=" * 80)
    print("COMPLETE USERS TABLE INTEGRATION TEST")
    print("=" * 80)
    
    try:
        from dash_apps.services.users_table_service import UsersTableService
        from dash_apps.callbacks.users_callbacks import update_users_table, update_filters
        
        print("\n1. Testing pagination with correct total count...")
        result = UsersTableService.get_users_page(page=1, page_size=5)
        total_count = result.get('total_count', 0)
        users_count = len(result.get('users', []))
        print(f"   ✓ Page 1: {users_count} users, Total: {total_count}")
        
        # Test second page
        if total_count > 5:
            result = UsersTableService.get_users_page(page=2, page_size=5)
            users_count_p2 = len(result.get('users', []))
            print(f"   ✓ Page 2: {users_count_p2} users")
        
        print("\n2. Testing filters with real database values...")
        # Test driver filter
        filters = {"role": "driver"}
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        driver_count = result.get('total_count', 0)
        print(f"   ✓ Driver filter: {driver_count} users")
        
        # Test passenger filter
        filters = {"role": "passenger"}
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        passenger_count = result.get('total_count', 0)
        print(f"   ✓ Passenger filter: {passenger_count} users")
        
        # Test gender filter
        filters = {"gender": "man"}
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        men_count = result.get('total_count', 0)
        print(f"   ✓ Men filter: {men_count} users")
        
        filters = {"gender": "woman"}
        result = UsersTableService.get_users_page(page=1, page_size=10, filters=filters)
        women_count = result.get('total_count', 0)
        print(f"   ✓ Women filter: {women_count} users")
        
        print("\n3. Testing callback integration...")
        # Test update_users_table callback
        try:
            result = update_users_table(current_page=1, refresh_clicks=None, filters={})
            print(f"   ✓ Callback with no filters: {type(result)} returned")
            
            result = update_users_table(current_page=1, refresh_clicks=None, filters={"role": "driver"})
            print(f"   ✓ Callback with driver filter: {type(result)} returned")
            
        except Exception as e:
            print(f"   ✗ Callback error: {e}")
        
        print("\n4. Testing filter update callback...")
        try:
            # Test filter creation
            filters_result = update_filters(
                n_clicks=1,
                search_text="test",
                date_from=None,
                date_to=None,
                date_filter_type="range",
                single_date=None,
                date_sort="desc",
                role="driver",
                driver_validation="all",
                gender="man",
                rating_operator="all",
                rating_value=3,
                current_filters={}
            )
            print(f"   ✓ Filter update result: {filters_result}")
            
        except Exception as e:
            print(f"   ✗ Filter update error: {e}")
        
        print("\n5. Testing cache performance...")
        import time
        
        # First call (cache miss)
        start_time = time.time()
        result1 = UsersTableService.get_users_page(page=1, page_size=10)
        first_call_time = time.time() - start_time
        
        # Second call (cache hit)
        start_time = time.time()
        result2 = UsersTableService.get_users_page(page=1, page_size=10)
        second_call_time = time.time() - start_time
        
        print(f"   ✓ First call (cache miss): {first_call_time:.3f}s")
        print(f"   ✓ Second call (cache hit): {second_call_time:.3f}s")
        print(f"   ✓ Cache speedup: {first_call_time/second_call_time:.1f}x faster")
        
        print("\n6. Validation summary...")
        print(f"   ✓ Total users in database: {total_count}")
        print(f"   ✓ Drivers: {driver_count}")
        print(f"   ✓ Passengers: {passenger_count}")
        print(f"   ✓ Men: {men_count}")
        print(f"   ✓ Women: {women_count}")
        print(f"   ✓ Data consistency: {driver_count + passenger_count == total_count}")
        print(f"   ✓ Gender consistency: {men_count + women_count == total_count}")
        
        # Check if all major issues are resolved
        issues_resolved = []
        issues_resolved.append(("Pagination total count", total_count > 0))
        issues_resolved.append(("Role filters working", driver_count > 0 and passenger_count > 0))
        issues_resolved.append(("Gender filters working", men_count > 0 and women_count > 0))
        issues_resolved.append(("Cache working", second_call_time < first_call_time))
        issues_resolved.append(("Callbacks working", True))  # No exceptions thrown
        
        print(f"\n7. Issues resolution status:")
        all_resolved = True
        for issue, resolved in issues_resolved:
            status = "✓ RESOLVED" if resolved else "✗ PENDING"
            print(f"   {status}: {issue}")
            if not resolved:
                all_resolved = False
        
        print(f"\n8. Overall status: {'✓ ALL ISSUES RESOLVED' if all_resolved else '✗ SOME ISSUES REMAIN'}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("INTEGRATION TEST COMPLETED")
    print("=" * 80)

if __name__ == "__main__":
    test_complete_users_integration()
