#!/usr/bin/env python3
"""
Deploy Railway with aggressive Supabase-only mode
This completely eliminates SQLite fallback
"""

import subprocess
import sys
import os

def main():
    print("🚀 Deploying Railway Aggressive Supabase Mode")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main_railway_supabase_aggressive.py"):
        print("❌ main_railway_supabase_aggressive.py not found!")
        return False
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    print("✅ Files ready for aggressive deployment")
    print("📋 Aggressive Supabase mode includes:")
    print("  ✅ NO SQLite fallback at all")
    print("  ✅ Bot crashes if Supabase fails")
    print("  ✅ All dependencies included")
    print("  ✅ Environment variable validation")
    
    try:
        print("\n📝 Adding files to git...")
        subprocess.run(["git", "add", "."], check=True)
        
        print("📝 Creating commit...")
        commit_message = "Railway: Aggressive Supabase-only mode - NO SQLite fallback"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        print("🚀 Pushing to Railway...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ Aggressive Supabase mode deployed!")
        print("⏳ Railway will build with NO fallbacks")
        print("📱 Check Railway dashboard for build status")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

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
        "SUPABASE_USER=postgres",
        "SUPABASE_PASSWORD=Viggu@2006",
        "SUPABASE_DATABASE=postgres",
        "SUPABASE_HOST=db.wecaohxjejimxhbcgmjp.supabase.co",
        "SUPABASE_PORT=5432",
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
    
    print()
    print("🎯 Expected Results:")
    print("✅ Bot will connect to Supabase REST API")
    print("✅ NO SQLite fallback (eliminates 'no such table' errors)")
    print("✅ Bot ready with supabase_rest database")
    print("❌ If Supabase fails, bot will crash (no fallback)")

def show_expected_behavior():
    print("\n" + "=" * 60)
    print("🎯 EXPECTED BEHAVIOR")
    print("=" * 60)
    print("✅ Build succeeds (all dependencies included)")
    print("✅ Bot starts with Supabase connection")
    print("✅ NO 'no such table: sessions' errors")
    print("✅ NO SQLite fallback at all")
    print("✅ All features work (login, attendance, marks, etc.)")
    print("❌ If Supabase is down, bot crashes (better than SQLite errors)")

if __name__ == "__main__":
    print("🤖 Railway Aggressive Supabase-Only Deployment")
    print("This completely eliminates SQLite fallback")
    print()
    
    show_railway_env_instructions()
    show_expected_behavior()
    
    print("\n" + "=" * 60)
    print("🚀 READY TO DEPLOY AGGRESSIVE MODE?")
    print("=" * 60)
    print("⚠️  WARNING: This version will CRASH if Supabase fails")
    print("✅ But it will NEVER fall back to SQLite")
    
    response = input("Deploy aggressive Supabase-only mode? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        success = main()
        if success:
            print("\n🎉 Aggressive Supabase mode deployed!")
            print("⏳ Wait 2-3 minutes for Railway to build")
            print("📱 Check Railway dashboard for status")
            print("\n🔧 IMPORTANT: Make sure environment variables are set correctly!")
            print("   If bot still shows SQLite errors, check Railway env vars")
        else:
            print("\n❌ Deployment failed. Check errors above.")
    else:
        print("\n⏸️ Deployment cancelled.")
