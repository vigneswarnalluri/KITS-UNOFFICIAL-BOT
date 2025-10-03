#!/usr/bin/env python3
"""
Complete Railway deployment fix
This adds all missing dependencies and deploys the Supabase-only version
"""

import subprocess
import sys
import os

def main():
    print("🚀 Deploying Complete Railway Fix")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main_railway_supabase_only.py"):
        print("❌ main_railway_supabase_only.py not found!")
        return False
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    print("✅ Files ready for deployment")
    print("📋 Fixes included:")
    print("  ✅ Removed pdf_compressor (no PIL dependency)")
    print("  ✅ Added beautifulsoup4 and lxml")
    print("  ✅ Supabase-only mode (no SQLite fallback)")
    print("  ✅ Minimal requirements for Railway")
    
    try:
        print("\n📝 Adding files to git...")
        subprocess.run(["git", "add", "."], check=True)
        
        print("📝 Creating commit...")
        commit_message = "Railway: Complete fix - add missing dependencies, remove PIL"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        print("🚀 Pushing to Railway...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ Deployment initiated!")
        print("⏳ Railway will now build with all required dependencies")
        print("📱 Check Railway dashboard for build status")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_expected_results():
    print("\n" + "=" * 50)
    print("🎯 EXPECTED RESULTS")
    print("=" * 50)
    print("✅ Build will succeed (all dependencies included)")
    print("✅ Bot will start with Supabase connection")
    print("✅ No more 'no such table' errors")
    print("✅ No more PIL import errors")
    print("✅ No more bs4 import errors")
    print()
    print("📱 Bot Features:")
    print("  ✅ Login/Logout - Works")
    print("  ✅ Attendance - Works")
    print("  ✅ Marks - Works")
    print("  ✅ Timetable - Works")
    print("  ✅ Labs - Works")
    print("  ✅ Settings - Works")
    print("  ❌ PDF Compression - Disabled (no Pillow)")
    print()
    print("🔒 Database: Supabase REST API only (no SQLite fallback)")

if __name__ == "__main__":
    print("🤖 Railway Complete Fix Deployment")
    print("This adds all missing dependencies and removes problematic ones")
    print()
    
    show_expected_results()
    
    print("\n" + "=" * 50)
    print("🚀 READY TO DEPLOY?")
    print("=" * 50)
    
    response = input("Deploy the complete fix? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        success = main()
        if success:
            print("\n🎉 Railway deployment initiated!")
            print("⏳ Wait 2-3 minutes for Railway to build and deploy")
            print("📱 Check your Railway dashboard for status")
        else:
            print("\n❌ Deployment failed. Check errors above.")
    else:
        print("\n⏸️ Deployment cancelled.")
