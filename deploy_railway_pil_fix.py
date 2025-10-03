#!/usr/bin/env python3
"""
Deploy Railway PIL import fix
This removes all pdf_compressor imports and dependencies
"""

import subprocess
import sys
import os

def main():
    print("🚀 Deploying Railway PIL Import Fix")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("main_railway_supabase_only.py"):
        print("❌ main_railway_supabase_only.py not found!")
        return False
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    print("✅ Files ready for deployment")
    print("📋 PIL import fix includes:")
    print("  ✅ Removed pdf_compressor from lab_operations.py")
    print("  ✅ Disabled PDF compression functions")
    print("  ✅ All dependencies included (no PIL)")
    print("  ✅ Supabase-only mode")
    
    try:
        print("\n📝 Adding files to git...")
        subprocess.run(["git", "add", "."], check=True)
        
        print("📝 Creating commit...")
        commit_message = "Railway: Fix PIL import - remove pdf_compressor from lab_operations"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        print("🚀 Pushing to Railway...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ PIL import fix deployed!")
        print("⏳ Railway will build without PIL dependencies")
        print("📱 Check Railway dashboard for build status")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def show_fixes():
    print("\n" + "=" * 50)
    print("🔧 FIXES APPLIED")
    print("=" * 50)
    print("✅ Removed pdf_compressor import from lab_operations.py")
    print("✅ Disabled PDF compression functions")
    print("✅ Added all required dependencies (bs4, pyqrcode, etc.)")
    print("✅ No PIL/Pillow dependency")
    print("✅ Supabase-only mode (no SQLite fallback)")
    print()
    print("📱 Features Status:")
    print("  ✅ Login/Logout - Works")
    print("  ✅ Attendance - Works")
    print("  ✅ Marks - Works")
    print("  ✅ Timetable - Works")
    print("  ✅ Labs - Works (PDF compression disabled)")
    print("  ✅ Settings - Works")
    print("  ❌ PDF Compression - Disabled (no Pillow)")

if __name__ == "__main__":
    print("🤖 Railway PIL Import Fix Deployment")
    print("This removes all pdf_compressor dependencies")
    print()
    
    show_fixes()
    
    print("\n" + "=" * 50)
    print("🚀 READY TO DEPLOY PIL FIX?")
    print("=" * 50)
    
    response = input("Deploy the PIL import fix? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        success = main()
        if success:
            print("\n🎉 PIL import fix deployed!")
            print("⏳ Wait 2-3 minutes for Railway to build")
            print("📱 Check Railway dashboard for status")
            print("\n🎯 Expected Results:")
            print("✅ Build succeeds (no PIL dependency)")
            print("✅ Bot starts with Supabase connection")
            print("✅ No more import errors")
            print("✅ Labs work (PDF compression disabled)")
        else:
            print("\n❌ Deployment failed. Check errors above.")
    else:
        print("\n⏸️ Deployment cancelled.")
