#!/usr/bin/env python3
"""
Deploy Railway with FULL Supabase mode + KITS integration
This includes all original features with Supabase-only database
"""

import subprocess
import sys
import os

def main():
    print("🚀 Deploying Railway FULL Supabase + KITS Mode")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("main_railway_full_supabase.py"):
        print("❌ main_railway_full_supabase.py not found!")
        return False
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    print("✅ Files ready for full deployment")
    print("📋 Full Supabase + KITS mode includes:")
    print("  ✅ Complete KITS authentication")
    print("  ✅ Full attendance, marks, timetable features")
    print("  ✅ Supabase-only database (no SQLite fallback)")
    print("  ✅ All original bot functionality")
    
    try:
        print("\n📝 Adding files to git...")
        subprocess.run(["git", "add", "."], check=True)
        
        print("📝 Creating commit...")
        commit_message = "Railway: FULL Supabase + KITS integration - all features"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        print("🚀 Pushing to Railway...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ FULL Supabase + KITS mode deployed!")
        print("⏳ Railway will build with complete functionality")
        print("📱 Check Railway dashboard for build status")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_full_features():
    print("\n" + "=" * 60)
    print("🎯 FULL FEATURES INCLUDED")
    print("=" * 60)
    print("✅ /start - Welcome message")
    print("✅ /login - Full KITS authentication")
    print("✅ /logout - Logout from account")
    print("✅ /attendance - Get attendance data from KITS")
    print("✅ /marks - Get marks data from KITS")
    print("✅ /timetable - Get timetable data from KITS")
    print("✅ /help - Help message")
    print("✅ Supabase-only database (no SQLite fallback)")
    print("✅ Full KITS system integration")

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
    print("✅ Bot starts with FULL Supabase + KITS integration")
    print("✅ NO 'no such table: sessions' errors")
    print("✅ NO SQLite, NO PostgreSQL fallback")
    print("✅ All features work: login, attendance, marks, timetable")
    print("✅ Full KITS system authentication")
    print("❌ If Supabase fails, bot crashes (better than SQLite errors)")

def show_kits_integration():
    print("\n" + "=" * 60)
    print("🔗 KITS INTEGRATION FEATURES")
    print("=" * 60)
    print("✅ Real KITS authentication (not just credential storage)")
    print("✅ Live attendance data from KITS system")
    print("✅ Live marks data from KITS system")
    print("✅ Live timetable data from KITS system")
    print("✅ Session management with Supabase")
    print("✅ Credential storage with Supabase")
    print("✅ Error handling for KITS system issues")

if __name__ == "__main__":
    print("🤖 Railway FULL Supabase + KITS Deployment")
    print("This includes ALL original features with Supabase-only database")
    print()
    
    show_full_features()
    show_kits_integration()
    show_railway_env_instructions()
    show_expected_results()
    
    print("\n" + "=" * 60)
    print("🚀 READY TO DEPLOY FULL MODE?")
    print("=" * 60)
    print("⚠️  WARNING: This version will CRASH if Supabase fails")
    print("✅ But it will NEVER use SQLite or PostgreSQL")
    print("🎯 This includes ALL original bot features!")
    print("📱 Full KITS integration with attendance, marks, timetable")
    
    response = input("Deploy FULL Supabase + KITS mode? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        success = main()
        if success:
            print("\n🎉 FULL Supabase + KITS mode deployed!")
            print("⏳ Wait 2-3 minutes for Railway to build")
            print("📱 Check Railway dashboard for status")
            print("\n🔧 IMPORTANT: Make sure environment variables are set correctly!")
            print("   This includes ALL original bot features with Supabase-only database!")
            print("📱 Full KITS integration: login, attendance, marks, timetable")
        else:
            print("\n❌ Deployment failed. Check errors above.")
    else:
        print("\n⏸️ Deployment cancelled.")
