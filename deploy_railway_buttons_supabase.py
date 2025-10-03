#!/usr/bin/env python3
"""
Deploy Railway with BUTTONS Supabase mode + KITS integration
This includes the original button interface with Supabase-only database
"""

import subprocess
import sys
import os

def main():
    print("🚀 Deploying Railway BUTTONS Supabase + KITS Mode")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("main_railway_buttons_supabase.py"):
        print("❌ main_railway_buttons_supabase.py not found!")
        return False
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    print("✅ Files ready for buttons deployment")
    print("📋 Buttons Supabase + KITS mode includes:")
    print("  ✅ Original button interface")
    print("  ✅ Interactive inline keyboards")
    print("  ✅ Supabase-only database (no SQLite fallback)")
    print("  ✅ All original bot functionality")
    print("  ✅ Robust KITS integration")
    
    try:
        print("\n📝 Adding files to git...")
        subprocess.run(["git", "add", "."], check=True)
        
        print("📝 Creating commit...")
        commit_message = "Railway: BUTTONS Supabase + KITS integration - original UI"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        print("🚀 Pushing to Railway...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ BUTTONS Supabase + KITS mode deployed!")
        print("⏳ Railway will build with button interface")
        print("📱 Check Railway dashboard for build status")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_button_features():
    print("\n" + "=" * 60)
    print("🔘 BUTTON INTERFACE FEATURES")
    print("=" * 60)
    print("✅ Interactive inline keyboards")
    print("✅ Main menu with buttons:")
    print("   - 📊 Attendance")
    print("   - 📈 Marks")
    print("   - 📅 Timetable")
    print("   - ⚙️ Settings")
    print("   - ❓ Help")
    print("   - 🚪 Logout")
    print("✅ Login help buttons")
    print("✅ Callback query handling")
    print("✅ Original user experience")

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
    print("✅ Bot starts with BUTTON INTERFACE + Supabase")
    print("✅ NO 'no such table: sessions' errors")
    print("✅ NO SQLite, NO PostgreSQL fallback")
    print("✅ Interactive buttons work")
    print("✅ All features accessible via buttons")
    print("✅ Original user experience restored")

def show_user_experience():
    print("\n" + "=" * 60)
    print("👤 USER EXPERIENCE")
    print("=" * 60)
    print("✅ /start shows welcome message with buttons")
    print("✅ Login works (stores credentials in Supabase)")
    print("✅ After login, main menu appears with buttons")
    print("✅ Attendance, marks, timetable accessible via buttons")
    print("✅ Settings and help buttons work")
    print("✅ Logout button works")
    print("✅ Original button interface restored")

if __name__ == "__main__":
    print("🤖 Railway BUTTONS Supabase + KITS Deployment")
    print("This restores the original button interface with Supabase-only database")
    print()
    
    show_button_features()
    show_railway_env_instructions()
    show_expected_results()
    show_user_experience()
    
    print("\n" + "=" * 60)
    print("🚀 READY TO DEPLOY BUTTONS MODE?")
    print("=" * 60)
    print("⚠️  WARNING: This version will CRASH if Supabase fails")
    print("✅ But it will NEVER use SQLite or PostgreSQL")
    print("🎯 This restores the original button interface!")
    print("📱 Interactive buttons with Supabase-only database")
    
    response = input("Deploy BUTTONS Supabase + KITS mode? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        success = main()
        if success:
            print("\n🎉 BUTTONS Supabase + KITS mode deployed!")
            print("⏳ Wait 2-3 minutes for Railway to build")
            print("📱 Check Railway dashboard for status")
            print("\n🔧 IMPORTANT: Make sure environment variables are set correctly!")
            print("   This restores the original button interface!")
            print("📱 Interactive buttons with Supabase-only database")
        else:
            print("\n❌ Deployment failed. Check errors above.")
    else:
        print("\n⏸️ Deployment cancelled.")
