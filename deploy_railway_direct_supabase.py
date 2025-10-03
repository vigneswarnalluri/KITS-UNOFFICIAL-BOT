#!/usr/bin/env python3
"""
Deploy Railway with DIRECT Supabase mode
This completely bypasses all other database modules
"""

import subprocess
import sys
import os

def main():
    print("🚀 Deploying Railway DIRECT Supabase Mode")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main_railway_direct_supabase.py"):
        print("❌ main_railway_direct_supabase.py not found!")
        return False
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    print("✅ Files ready for direct deployment")
    print("📋 Direct Supabase mode includes:")
    print("  ✅ Completely bypasses all other database modules")
    print("  ✅ Direct Supabase REST API implementation")
    print("  ✅ NO SQLite, NO PostgreSQL, NO other databases")
    print("  ✅ Simplified bot with core features")
    
    try:
        print("\n📝 Adding files to git...")
        subprocess.run(["git", "add", "."], check=True)
        
        print("📝 Creating commit...")
        commit_message = "Railway: DIRECT Supabase mode - bypass all other databases"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        print("🚀 Pushing to Railway...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ DIRECT Supabase mode deployed!")
        print("⏳ Railway will build with direct Supabase only")
        print("📱 Check Railway dashboard for build status")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_direct_mode_explanation():
    print("\n" + "=" * 60)
    print("🔧 DIRECT SUPABASE MODE EXPLANATION")
    print("=" * 60)
    print("This version COMPLETELY BYPASSES all other database modules:")
    print("✅ No tdatabase, no pgdatabase, no user_settings imports")
    print("✅ Direct Supabase REST API implementation")
    print("✅ Simplified bot with core features only")
    print("✅ NO SQLite, NO PostgreSQL, NO other databases")
    print("✅ Bot will either work with Supabase or crash")
    print()
    print("🎯 This should FINALLY eliminate ALL database fallback issues!")

def show_railway_env_instructions():
    print("\n" + "=" * 60)
    print("🔧 CRITICAL: RAILWAY ENVIRONMENT VARIABLES")
    print("=" * 60)
    print("Copy these EXACTLY to your Railway project environment variables:")
    print()
    
    env_vars = [
        "CONTAINER_DEPLOYMENT=true",
        "API_ID=27523374",
        "API_HASH=b7a72638255400c7107abd58b1f79711",
        "BOT_TOKEN=8007204996:AAGbfj4e6sEefgdI8Ixncl3tVoI6kKnZo28",
        "SUPABASE_URL=https://wecaohxjejimxhbcgmjp.supabase.co",
        "SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndlY2FvaHhqZWppbXhoYmNnbWpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkyMjk1NzQsImV4cCI6MjA3NDgwNTU3NH0.MPOSqIjbPLd1zoqwjsCZQBQSeUBMQdRND7lnMOmbCfk",
        "FORCE_SUPABASE_REST=true",
        "DISABLE_SQLITE_FALLBACK=true",
        "SUPABASE_PRIORITY=rest",
        "RAILWAY_SUPABASE_ONLY=true"
    ]
    
    for var in env_vars:
        print(f"  {var}")
    
    print()
    print("⚠️  CRITICAL: Do NOT set these variables (they cause localhost fallback):")
    print("  ❌ POSTGRES_HOST=localhost")
    print("  ❌ POSTGRES_USER_ID=postgres") 
    print("  ❌ POSTGRES_PASSWORD=viggu")
    print("  ❌ POSTGRES_DATABASE=kits_bot_db")

def show_expected_results():
    print("\n" + "=" * 60)
    print("🎯 EXPECTED RESULTS")
    print("=" * 60)
    print("✅ Build succeeds (all dependencies included)")
    print("✅ Bot starts with DIRECT Supabase connection")
    print("✅ NO 'no such table: sessions' errors")
    print("✅ NO SQLite, NO PostgreSQL fallback")
    print("✅ Core features work (login, logout, help)")
    print("✅ Advanced features show 'coming soon' messages")
    print("❌ If Supabase fails, bot crashes (better than SQLite errors)")

def show_features_status():
    print("\n" + "=" * 60)
    print("📱 FEATURES STATUS")
    print("=" * 60)
    print("✅ /start - Welcome message")
    print("✅ /login - Login with credentials")
    print("✅ /logout - Logout from account")
    print("✅ /help - Help message")
    print("⏳ /attendance - Coming soon (Supabase-only mode)")
    print("⏳ /marks - Coming soon (Supabase-only mode)")
    print("⏳ /timetable - Coming soon (Supabase-only mode)")
    print("❌ /labs - Disabled (requires complex implementation)")
    print("❌ /settings - Disabled (requires complex implementation)")

if __name__ == "__main__":
    print("🤖 Railway DIRECT Supabase Deployment")
    print("This completely bypasses all other database modules")
    print()
    
    show_direct_mode_explanation()
    show_railway_env_instructions()
    show_expected_results()
    show_features_status()
    
    print("\n" + "=" * 60)
    print("🚀 READY TO DEPLOY DIRECT MODE?")
    print("=" * 60)
    print("⚠️  WARNING: This version will CRASH if Supabase fails")
    print("✅ But it will NEVER use SQLite or PostgreSQL")
    print("🎯 This should FINALLY fix the database fallback issue!")
    print("📱 Core features work, advanced features show 'coming soon'")
    
    response = input("Deploy DIRECT Supabase mode? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        success = main()
        if success:
            print("\n🎉 DIRECT Supabase mode deployed!")
            print("⏳ Wait 2-3 minutes for Railway to build")
            print("📱 Check Railway dashboard for status")
            print("\n🔧 IMPORTANT: Make sure environment variables are set correctly!")
            print("   This should FINALLY eliminate ALL database fallback issues!")
            print("📱 Bot will work with core features, advanced features show 'coming soon'")
        else:
            print("\n❌ Deployment failed. Check errors above.")
    else:
        print("\n⏸️ Deployment cancelled.")
