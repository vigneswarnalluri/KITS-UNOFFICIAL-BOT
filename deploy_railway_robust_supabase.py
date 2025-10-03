#!/usr/bin/env python3
"""
Deploy Railway with ROBUST Supabase mode + KITS integration
This handles KITS connectivity issues with fallbacks
"""

import subprocess
import sys
import os

def main():
    print("🚀 Deploying Railway ROBUST Supabase + KITS Mode")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("main_railway_robust_supabase.py"):
        print("❌ main_railway_robust_supabase.py not found!")
        return False
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    print("✅ Files ready for robust deployment")
    print("📋 Robust Supabase + KITS mode includes:")
    print("  ✅ Multiple KITS URL fallbacks")
    print("  ✅ Sample data when KITS is unavailable")
    print("  ✅ Robust error handling")
    print("  ✅ Supabase-only database (no SQLite fallback)")
    print("  ✅ All original bot functionality")
    
    try:
        print("\n📝 Adding files to git...")
        subprocess.run(["git", "add", "."], check=True)
        
        print("📝 Creating commit...")
        commit_message = "Railway: ROBUST Supabase + KITS integration - handles connectivity issues"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        print("🚀 Pushing to Railway...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ ROBUST Supabase + KITS mode deployed!")
        print("⏳ Railway will build with robust KITS handling")
        print("📱 Check Railway dashboard for build status")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_robust_features():
    print("\n" + "=" * 60)
    print("🛡️ ROBUST FEATURES INCLUDED")
    print("=" * 60)
    print("✅ Multiple KITS URL fallbacks")
    print("✅ Sample data when KITS is unavailable")
    print("✅ Robust error handling for network issues")
    print("✅ Proper HTTP headers for KITS access")
    print("✅ Timeout handling for slow connections")
    print("✅ Graceful degradation when KITS is down")
    print("✅ Supabase-only database (no SQLite fallback)")

def show_kits_fallbacks():
    print("\n" + "=" * 60)
    print("🔗 KITS FALLBACK STRATEGY")
    print("=" * 60)
    print("✅ Tries multiple KITS URLs:")
    print("   - https://kits.edu.in/student/login")
    print("   - https://kits.edu.in/login")
    print("   - https://kits.edu.in/student")
    print("   - https://kits.edu.in")
    print("✅ If KITS is unavailable, shows sample data")
    print("✅ Proper error messages for users")
    print("✅ Bot continues working even if KITS is down")

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
    print("✅ Bot starts with ROBUST Supabase + KITS integration")
    print("✅ NO 'no such table: sessions' errors")
    print("✅ NO SQLite, NO PostgreSQL fallback")
    print("✅ Handles KITS connectivity issues gracefully")
    print("✅ Shows sample data when KITS is unavailable")
    print("✅ All features work even if KITS is down")

def show_user_experience():
    print("\n" + "=" * 60)
    print("👤 USER EXPERIENCE")
    print("=" * 60)
    print("✅ Login works (stores credentials in Supabase)")
    print("✅ Attendance shows data (real or sample)")
    print("✅ Marks shows data (real or sample)")
    print("✅ Timetable shows data (real or sample)")
    print("✅ Clear messages when KITS is unavailable")
    print("✅ Bot continues working regardless of KITS status")

if __name__ == "__main__":
    print("🤖 Railway ROBUST Supabase + KITS Deployment")
    print("This handles KITS connectivity issues with fallbacks")
    print()
    
    show_robust_features()
    show_kits_fallbacks()
    show_railway_env_instructions()
    show_expected_results()
    show_user_experience()
    
    print("\n" + "=" * 60)
    print("🚀 READY TO DEPLOY ROBUST MODE?")
    print("=" * 60)
    print("⚠️  WARNING: This version will CRASH if Supabase fails")
    print("✅ But it will NEVER use SQLite or PostgreSQL")
    print("🎯 This handles KITS connectivity issues gracefully!")
    print("📱 Bot works even if KITS system is down")
    
    response = input("Deploy ROBUST Supabase + KITS mode? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        success = main()
        if success:
            print("\n🎉 ROBUST Supabase + KITS mode deployed!")
            print("⏳ Wait 2-3 minutes for Railway to build")
            print("📱 Check Railway dashboard for status")
            print("\n🔧 IMPORTANT: Make sure environment variables are set correctly!")
            print("   This handles KITS connectivity issues gracefully!")
            print("📱 Bot works even if KITS system is down")
        else:
            print("\n❌ Deployment failed. Check errors above.")
    else:
        print("\n⏸️ Deployment cancelled.")
