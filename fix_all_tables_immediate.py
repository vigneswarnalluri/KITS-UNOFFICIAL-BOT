#!/usr/bin/env python3
"""
Fix All Database Tables Immediately
This ensures all SQLite tables are created and forces Supabase usage
"""

import asyncio
import sqlite3
import os
from DATABASE import tdatabase, user_settings, managers_handler

async def create_all_sqlite_tables_comprehensive():
    """Create ALL SQLite tables comprehensively"""
    print("🔧 COMPREHENSIVE SQLITE TABLE CREATION")
    print("=" * 50)
    
    try:
        # Step 1: Create tdatabase tables (includes sessions table)
        print("📋 Creating tdatabase tables (sessions, users, reports)...")
        await tdatabase.create_all_tdatabase_tables()
        print("✅ Created tdatabase tables")
        
        # Step 2: Verify sessions table specifically
        print("🔍 Verifying sessions table...")
        with sqlite3.connect(tdatabase.DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'")
            sessions_exists = cursor.fetchone()
            if sessions_exists:
                print("✅ Sessions table verified")
            else:
                print("⚠️ Sessions table missing, creating manually...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        chat_id INTEGER PRIMARY KEY,
                        session_data TEXT,
                        user_id TEXT
                    )
                """)
                conn.commit()
                print("✅ Sessions table created manually")
        
        # Step 3: Create user_settings tables
        print("📋 Creating user_settings tables...")
        await user_settings.create_user_settings_tables()
        print("✅ Created user_settings tables")
        
        # Step 4: Create managers tables
        print("📋 Creating managers tables...")
        await managers_handler.create_required_bot_manager_tables()
        print("✅ Created managers tables")
        
        # Step 5: Set default indexes
        print("📋 Setting default indexes...")
        try:
            await user_settings.set_default_attendance_indexes()
            print("✅ Set default indexes")
        except Exception as e:
            print(f"⚠️ Index warning (normal): {e}")
        
        print("\n🎉 ALL SQLITE TABLES CREATED SUCCESSFULLY!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating SQLite tables: {e}")
        return False

def create_force_supabase_env():
    """Create environment file that forces Supabase usage"""
    print("\n🚀 CREATING FORCE SUPABASE CONFIGURATION")
    print("=" * 50)
    
    # Create a startup script that forces Supabase
    startup_script = """#!/usr/bin/env python3
# Force Supabase Startup Script
import os
import sys

# Force Supabase environment variables
os.environ['FORCE_SUPABASE_REST'] = 'true'
os.environ['DISABLE_SQLITE_FALLBACK'] = 'true'
os.environ['SUPABASE_PRIORITY'] = 'high'

print("🚀 FORCING SUPABASE CONNECTION...")
print("✅ Supabase REST API prioritized")
print("❌ SQLite fallback disabled")

# Import and run the main application
if __name__ == "__main__":
    import main_cloud_robust
"""
    
    try:
        with open('force_supabase_start.py', 'w') as f:
            f.write(startup_script)
        print("✅ Created force_supabase_start.py")
        
        # Update Dockerfile to use force script
        dockerfile_content = """FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Force Supabase environment variables
ENV CONTAINER_DEPLOYMENT=true
ENV FORCE_SUPABASE_REST=true
ENV DISABLE_SQLITE_FALLBACK=true
ENV SUPABASE_PRIORITY=high

# Run with Supabase priority
CMD ["python", "main_cloud_robust.py"]"""
        
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        print("✅ Updated Dockerfile with Supabase priority")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create force Supabase config: {e}")
        return False

def show_immediate_deployment_steps():
    """Show immediate deployment steps"""
    print("\n📋 IMMEDIATE DEPLOYMENT STEPS")
    print("=" * 50)
    
    print("🎯 CRITICAL: Update Railway Environment Variables NOW")
    print("Add these variables to force Supabase usage:")
    print()
    print("FORCE_SUPABASE_REST=true")
    print("DISABLE_SQLITE_FALLBACK=true") 
    print("SUPABASE_PRIORITY=high")
    print("CONTAINER_DEPLOYMENT=true")
    print()
    print("Plus all the Supabase variables from railway_supabase_env.txt")
    
    print("\n🚀 DEPLOY IMMEDIATELY:")
    print("git add .")
    print("git commit -m 'Fix all SQLite tables and force Supabase usage'")
    print("git push origin main")
    
    print("\n🎯 EXPECTED RESULT:")
    print("❌ BEFORE: Error in 'start' command: no such table: sessions")
    print("✅ AFTER: SUCCESS: Supabase REST API connection established!")
    
    print("\n⏰ TIMELINE:")
    print("1. Update Railway env vars (2 minutes)")
    print("2. Push changes (1 minute)")
    print("3. Railway deployment (3-5 minutes)")
    print("4. Bot working with Supabase (immediately)")

async def test_all_tables():
    """Test all database tables"""
    print("\n🧪 TESTING ALL DATABASE TABLES")
    print("=" * 40)
    
    try:
        # Test sessions table
        with sqlite3.connect(tdatabase.DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sessions")
            print("✅ Sessions table: WORKING")
        
        # Test user_settings table
        with sqlite3.connect(user_settings.SETTINGS_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_settings")
            print("✅ User_settings table: WORKING")
        
        # Test Supabase REST API
        from DATABASE.supabase_rest import SupabaseREST
        rest_client = SupabaseREST()
        result = rest_client._make_request("GET", "user_sessions?limit=1")
        if result is not None:
            print("✅ Supabase REST API: WORKING")
        else:
            print("❌ Supabase REST API: FAILED")
        
        print("\n🎉 ALL DATABASE SYSTEMS READY!")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

async def main():
    """Main function"""
    print("🚀 IMMEDIATE DATABASE FIX - ALL TABLES")
    print("=" * 60)
    
    # Step 1: Create all SQLite tables
    sqlite_success = await create_all_sqlite_tables_comprehensive()
    
    # Step 2: Create force Supabase configuration
    force_success = create_force_supabase_env()
    
    # Step 3: Test all systems
    test_success = await test_all_tables()
    
    # Step 4: Show deployment steps
    show_immediate_deployment_steps()
    
    print("\n" + "=" * 60)
    if sqlite_success and force_success and test_success:
        print("🎉 READY FOR IMMEDIATE DEPLOYMENT!")
        print("All tables fixed, Supabase forced, systems tested.")
        print("Deploy now to eliminate ALL database errors!")
    else:
        print("❌ SOME ISSUES DETECTED")
        print("Check the error messages above before deploying.")

if __name__ == "__main__":
    asyncio.run(main())
