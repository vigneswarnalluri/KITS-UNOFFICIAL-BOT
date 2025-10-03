#!/usr/bin/env python3
"""
Final Railway deployment with all dependencies
This should resolve all import errors
"""

import subprocess
import sys
import os

def main():
    print("🚀 Final Railway Deployment")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("main_railway_supabase_only.py"):
        print("❌ main_railway_supabase_only.py not found!")
        return False
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    print("✅ Files ready for final deployment")
    print("📋 Complete fix includes:")
    print("  ✅ All missing dependencies (bs4, pyqrcode, etc.)")
    print("  ✅ No PIL/Pillow dependency")
    print("  ✅ Supabase-only mode")
    print("  ✅ Minimal but complete requirements")
    
    try:
        print("\n📝 Adding files to git...")
        subprocess.run(["git", "add", "."], check=True)
        
        print("📝 Creating commit...")
        commit_message = "Railway: Final fix - add all missing dependencies"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        print("🚀 Pushing to Railway...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ Final deployment initiated!")
        print("⏳ Railway will build with complete dependencies")
        print("📱 Check Railway dashboard for build status")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_dependencies():
    print("\n" + "=" * 50)
    print("📦 DEPENDENCIES INCLUDED")
    print("=" * 50)
    print("✅ pyrogram - Telegram bot framework")
    print("✅ asyncpg - PostgreSQL database")
    print("✅ beautifulsoup4 - Web scraping")
    print("✅ pyqrcode - QR code generation")
    print("✅ requests - HTTP requests")
    print("✅ supabase - Supabase client")
    print("✅ python-dotenv - Environment variables")
    print("✅ pytz - Timezone handling")
    print("❌ pillow - Removed (caused build issues)")

if __name__ == "__main__":
    print("🤖 Railway Final Deployment")
    print("This includes ALL required dependencies")
    print()
    
    show_dependencies()
    
    print("\n" + "=" * 50)
    print("🚀 READY FOR FINAL DEPLOYMENT?")
    print("=" * 50)
    
    response = input("Deploy the final fix? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        success = main()
        if success:
            print("\n🎉 Final deployment initiated!")
            print("⏳ Wait 2-3 minutes for Railway to build")
            print("📱 Check Railway dashboard for status")
            print("\n🎯 Expected Results:")
            print("✅ Build succeeds with all dependencies")
            print("✅ Bot starts with Supabase connection")
            print("✅ No more import errors")
            print("✅ No more SQLite fallback errors")
        else:
            print("\n❌ Deployment failed. Check errors above.")
    else:
        print("\n⏸️ Deployment cancelled.")
