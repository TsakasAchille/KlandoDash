#!/usr/bin/env python3
"""
Test script to verify the stats panel fix is working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dash_apps.services.users_cache_service import UsersCacheService

def test_stats_panel():
    """Test the stats panel with a user ID to see the data structure"""
    print("=== TEST STATS PANEL FIX ===")
    
    # Test with a user ID
    test_uid = "2Zei7K3L6MWmeriARufNqEzW0kn1"
    
    print(f"Testing stats panel for user: {test_uid}")
    
    try:
        result = UsersCacheService.get_user_stats_panel(test_uid)
        print(f"Result type: {type(result)}")
        print("=== TEST COMPLETED ===")
        return result
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_stats_panel()
