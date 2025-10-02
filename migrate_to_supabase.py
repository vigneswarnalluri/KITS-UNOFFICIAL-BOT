#!/usr/bin/env python3
"""
Migration Script: Local Database to Supabase
This script helps migrate existing data from local SQLite to Supabase
"""

import asyncio
import os
import json
from load_env import load_environment
from DATABASE import tdatabase, user_settings, managers_handler
from DATABASE.supabase_database import supabase_db

async def migrate_user_sessions():
    """Migrate user sessions from SQLite to Supabase"""
    print("🔄 Migrating user sessions...")
    
    try:
        # Get all sessions from SQLite
        import sqlite3
        with sqlite3.connect("user_sessions.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id, session_data, user_id FROM sessions")
            sessions = cursor.fetchall()
        
        # Migrate to Supabase
        for chat_id, session_data, username in sessions:
            await supabase_db.store_user_session(chat_id, session_data, username)
            print(f"✅ Migrated session for user {username} (ID: {chat_id})")
        
        print(f"✅ Migrated {len(sessions)} user sessions")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating user sessions: {e}")
        return False

async def migrate_user_credentials():
    """Migrate user credentials from SQLite to Supabase"""
    print("🔄 Migrating user credentials...")
    
    try:
        # Get all credentials from SQLite
        import sqlite3
        with sqlite3.connect("credentials.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id, username, password FROM user_credentials")
            credentials = cursor.fetchall()
        
        # Migrate to Supabase
        for chat_id, username, password in credentials:
            await supabase_db.store_credentials(chat_id, username, password)
            print(f"✅ Migrated credentials for user {username} (ID: {chat_id})")
        
        print(f"✅ Migrated {len(credentials)} user credentials")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating user credentials: {e}")
        return False

async def migrate_user_settings():
    """Migrate user settings from SQLite to Supabase"""
    print("🔄 Migrating user settings...")
    
    try:
        # Get all settings from SQLite
        import sqlite3
        with sqlite3.connect("user_settings.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id, attendance_threshold, bio_threshold, ui, title FROM user_settings")
            settings = cursor.fetchall()
        
        # Migrate to Supabase
        for chat_id, attendance_threshold, bio_threshold, ui, title in settings:
            await supabase_db.store_user_settings(chat_id, attendance_threshold, bio_threshold, ui, title)
            print(f"✅ Migrated settings for user ID: {chat_id}")
        
        print(f"✅ Migrated {len(settings)} user settings")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating user settings: {e}")
        return False

async def migrate_reports():
    """Migrate reports from SQLite to Supabase"""
    print("🔄 Migrating reports...")
    
    try:
        # Get all reports from SQLite
        import sqlite3
        with sqlite3.connect("reports.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT report_id, username, report, chat_id, status FROM reports")
            reports = cursor.fetchall()
        
        # Migrate to Supabase
        for report_id, username, report, chat_id, status in reports:
            await supabase_db.store_report(report_id, username, report, chat_id, status)
            print(f"✅ Migrated report {report_id} from user {username}")
        
        print(f"✅ Migrated {len(reports)} reports")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating reports: {e}")
        return False

async def migrate_lab_uploads():
    """Migrate lab uploads from SQLite to Supabase"""
    print("🔄 Migrating lab uploads...")
    
    try:
        # Get all lab uploads from SQLite
        import sqlite3
        with sqlite3.connect("labuploads.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT chat_id, subject_code, week_no, title FROM lab_uploads")
            uploads = cursor.fetchall()
        
        # Migrate to Supabase
        for chat_id, subject_code, week_no, title in uploads:
            await supabase_db.store_lab_upload(chat_id, subject_code, week_no, title)
            print(f"✅ Migrated lab upload for user {chat_id}: {subject_code} Week {week_no}")
        
        print(f"✅ Migrated {len(uploads)} lab uploads")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating lab uploads: {e}")
        return False

async def main():
    """Main migration function"""
    print("🚀 KITS Bot - Database Migration to Supabase")
    print("=" * 50)
    
    # Load environment variables
    load_environment()
    
    # Check if Supabase is configured
    required_vars = ['SUPABASE_USER', 'SUPABASE_PASSWORD', 'SUPABASE_DATABASE', 'SUPABASE_HOST', 'SUPABASE_PORT']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing Supabase configuration: {', '.join(missing_vars)}")
        print("Please configure your .env file with Supabase credentials first.")
        return
    
    try:
        # Initialize Supabase
        await supabase_db.create_pool()
        await supabase_db.create_all_tables()
        print("✅ Supabase initialized successfully")
        
        # Migrate data
        migrations = [
            ("User Sessions", migrate_user_sessions),
            ("User Credentials", migrate_user_credentials),
            ("User Settings", migrate_user_settings),
            ("Reports", migrate_reports),
            ("Lab Uploads", migrate_lab_uploads)
        ]
        
        success_count = 0
        for name, migration_func in migrations:
            print(f"\n📦 Migrating {name}...")
            if await migration_func():
                success_count += 1
            else:
                print(f"❌ Failed to migrate {name}")
        
        print(f"\n🎉 Migration completed: {success_count}/{len(migrations)} successful")
        
        if success_count == len(migrations):
            print("✅ All data migrated successfully to Supabase!")
            print("🚀 Your bot is now ready for deployment with cloud database!")
        else:
            print("⚠️ Some migrations failed. Please check the errors above.")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
    
    finally:
        # Close Supabase connection
        await supabase_db.close_pool()

if __name__ == "__main__":
    asyncio.run(main())
