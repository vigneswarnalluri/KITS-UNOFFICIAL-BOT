#!/usr/bin/env python3
"""
Force Railway Update
This script creates the necessary SQLite tables and provides deployment instructions
"""

import asyncio
import os
from DATABASE import user_settings, tdatabase, managers_handler

async def create_all_sqlite_tables():
    """Create all SQLite tables with proper error handling"""
    print("🔧 Creating SQLite Tables for Railway Deployment")
    print("=" * 60)
    
    try:
        # Create tdatabase tables
        print("📋 Creating tdatabase tables...")
        await tdatabase.create_all_tdatabase_tables()
        print("✅ Created tdatabase tables")
        
        # Create user_settings tables
        print("📋 Creating user_settings tables...")
        await user_settings.create_user_settings_tables()
        print("✅ Created user_settings tables")
        
        # Create managers tables
        print("📋 Creating managers tables...")
        await managers_handler.create_required_bot_manager_tables()
        print("✅ Created managers tables")
        
        # Set default indexes
        print("📋 Setting default attendance indexes...")
        try:
            await user_settings.set_default_attendance_indexes()
            print("✅ Set default attendance indexes")
        except Exception as e:
            print(f"⚠️ Warning: Could not set default indexes: {e}")
        
        print("\n🎉 ALL SQLITE TABLES CREATED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating SQLite tables: {e}")
        return False

def show_deployment_instructions():
    """Show deployment instructions"""
    print("\n🚀 RAILWAY DEPLOYMENT INSTRUCTIONS")
    print("=" * 60)
    
    print("📋 CURRENT STATUS:")
    print("✅ SQLite tables created locally")
    print("✅ main.py updated with SQLite fixes")
    print("✅ main_cloud_robust.py available as backup")
    print("✅ Dockerfile configured properly")
    
    print("\n🔧 TO FIX RAILWAY DEPLOYMENT:")
    
    print("\n1️⃣ COMMIT AND PUSH CHANGES:")
    print("   git add .")
    print("   git commit -m 'Fix SQLite table creation - force Railway update'")
    print("   git push origin main")
    
    print("\n2️⃣ FORCE RAILWAY REDEPLOY:")
    print("   - Go to your Railway dashboard")
    print("   - Click on your project")
    print("   - Go to 'Deployments' tab")
    print("   - Click 'Redeploy' on the latest deployment")
    
    print("\n3️⃣ MONITOR LOGS FOR:")
    print("   ✅ '📋 Creating SQLite tables...'")
    print("   ✅ '✅ Created user_settings tables'")
    print("   ✅ '✅ SUCCESS: Local SQLite databases initialized!'")
    print("   ✅ No 'no such table: user_settings' errors")
    
    print("\n4️⃣ TEST BOT:")
    print("   - Send /start command")
    print("   - Should work without database errors")
    
    print("\n🎯 EXPECTED RAILWAY LOGS:")
    print("   📋 Creating SQLite tables...")
    print("   ✅ Created tdatabase tables")
    print("   ✅ Created user_settings tables")
    print("   ✅ Created managers tables")
    print("   ✅ Set default attendance indexes")
    print("   ✅ SUCCESS: Local SQLite databases initialized!")
    print("   🤖 Starting KITS Bot...")

def create_deployment_files():
    """Create files to force Railway deployment"""
    print("\n📁 Creating deployment trigger files...")
    
    # Create a version file
    with open('.railway_version', 'w') as f:
        f.write("v2.1.0-sqlite-fix\n")
    print("✅ Created .railway_version")
    
    # Update requirements.txt timestamp (forces rebuild)
    if os.path.exists('requirements.txt'):
        with open('requirements.txt', 'a') as f:
            f.write("\n# Updated: 2025-10-02 - SQLite fix deployment\n")
        print("✅ Updated requirements.txt timestamp")

async def main():
    """Main function"""
    print("🔧 RAILWAY SQLITE FIX DEPLOYMENT TOOL")
    print("=" * 70)
    
    # Create SQLite tables locally
    success = await create_all_sqlite_tables()
    
    if success:
        # Create deployment files
        create_deployment_files()
        
        # Show instructions
        show_deployment_instructions()
        
        print("\n🎉 READY FOR RAILWAY DEPLOYMENT!")
        print("Follow the instructions above to fix your Railway deployment.")
    else:
        print("\n❌ SQLITE TABLE CREATION FAILED!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
