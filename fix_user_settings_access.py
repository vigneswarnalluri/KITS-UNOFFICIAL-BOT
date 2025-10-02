#!/usr/bin/env python3
"""
Fix User Settings Access
This script patches the user_settings access to handle missing tables gracefully
"""

import asyncio
import sqlite3
import os
from DATABASE import user_settings

async def ensure_user_settings_table():
    """Ensure user_settings table exists and is properly initialized"""
    try:
        # Create the user_settings tables if they don't exist
        await user_settings.create_user_settings_tables()
        print("✅ User settings tables created/verified")
        
        # Set default indexes
        await user_settings.set_default_attendance_indexes()
        print("✅ Default attendance indexes set")
        
        return True
    except Exception as e:
        print(f"❌ Error creating user_settings tables: {e}")
        return False

async def test_user_settings_access():
    """Test user_settings table access"""
    try:
        # Test with a dummy chat_id
        test_chat_id = 123456789
        
        # Try to fetch UI settings
        ui_mode = await user_settings.fetch_ui_bool(test_chat_id)
        print(f"✅ UI mode fetch test: {ui_mode}")
        
        # If no settings exist, create default settings
        if ui_mode is None:
            await user_settings.set_user_default_settings(test_chat_id)
            print("✅ Default settings created for test user")
            
            # Try fetching again
            ui_mode = await user_settings.fetch_ui_bool(test_chat_id)
            print(f"✅ UI mode after default creation: {ui_mode}")
        
        # Clean up test data
        with sqlite3.connect(user_settings.SETTINGS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_settings WHERE chat_id = ?", (test_chat_id,))
            conn.commit()
        print("✅ Test data cleaned up")
        
        return True
    except Exception as e:
        print(f"❌ Error testing user_settings access: {e}")
        return False

async def main():
    """Main function to fix user_settings issues"""
    print("🔧 Fixing User Settings Access Issues")
    print("=" * 50)
    
    # Step 1: Ensure tables exist
    if await ensure_user_settings_table():
        print("✅ User settings tables are ready")
    else:
        print("❌ Failed to create user settings tables")
        return False
    
    # Step 2: Test access
    if await test_user_settings_access():
        print("✅ User settings access is working")
    else:
        print("❌ User settings access test failed")
        return False
    
    print("\n🎉 User Settings Fix Complete!")
    print("The bot should now handle user_settings access properly.")
    return True

if __name__ == "__main__":
    asyncio.run(main())
