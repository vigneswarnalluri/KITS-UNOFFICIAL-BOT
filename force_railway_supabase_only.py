#!/usr/bin/env python3
"""
Force Railway to redeploy with Supabase-only configuration
This script ensures Railway uses the new main_railway_supabase_only.py
"""

import os
import time
import subprocess
import sys

def main():
    print("🚀 Forcing Railway Supabase-Only Deployment")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main_railway_supabase_only.py"):
        print("❌ main_railway_supabase_only.py not found!")
        print("Please run this script from the project root directory.")
        return False
    
    # Check if Dockerfile is updated
    with open("Dockerfile", "r") as f:
        dockerfile_content = f.read()
        if "main_railway_supabase_only.py" not in dockerfile_content:
            print("❌ Dockerfile not updated!")
            print("Please update Dockerfile to use main_railway_supabase_only.py")
            return False
    
    print("✅ Files are ready for Railway deployment")
    
    # Create a commit to trigger Railway redeploy
    try:
        print("📝 Creating commit to trigger Railway redeploy...")
        
        # Add all files
        subprocess.run(["git", "add", "."], check=True)
        
        # Create commit
        commit_message = "Railway: Force Supabase-only mode (no SQLite fallback)"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        print("✅ Commit created successfully")
        
        # Push to trigger Railway deployment
        print("🚀 Pushing to trigger Railway deployment...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ Push completed - Railway should start deploying now")
        print("⏳ Please wait 2-3 minutes for Railway to build and deploy")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_railway_env_instructions():
    """Show instructions for setting Railway environment variables"""
    print("\n" + "=" * 50)
    print("🔧 RAILWAY ENVIRONMENT VARIABLES")
    print("=" * 50)
    print("Copy these to your Railway project environment variables:")
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
    print("⚠️  IMPORTANT: Do NOT set these variables (they cause localhost fallback):")
    print("  ❌ POSTGRES_HOST=localhost")
    print("  ❌ POSTGRES_USER_ID=postgres") 
    print("  ❌ POSTGRES_PASSWORD=viggu")
    print("  ❌ POSTGRES_DATABASE=kits_bot_db")
    
    print()
    print("🎯 Expected Results:")
    print("✅ Bot will connect to Supabase REST API")
    print("✅ No SQLite fallback (eliminates 'no such table' errors)")
    print("✅ Bot ready with supabase_rest database")
    print("❌ If Supabase fails, bot will crash (no fallback)")

if __name__ == "__main__":
    print("🤖 Railway Supabase-Only Deployment Script")
    print("This will force Railway to use Supabase and disable SQLite fallback")
    print()
    
    # Show environment variable instructions first
    show_railway_env_instructions()
    
    print("\n" + "=" * 50)
    print("🚀 READY TO DEPLOY?")
    print("=" * 50)
    
    response = input("Do you want to proceed with Railway deployment? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        success = main()
        if success:
            print("\n🎉 Railway deployment initiated!")
            print("📱 Check your Railway dashboard for deployment status")
            print("⏳ Wait 2-3 minutes for the build to complete")
        else:
            print("\n❌ Deployment failed. Please check the errors above.")
    else:
        print("\n⏸️  Deployment cancelled. You can run this script again when ready.")
