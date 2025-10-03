#!/usr/bin/env python3
"""
Deploy Railway fix for PIL import error
This removes pdf_compressor dependency and uses minimal requirements
"""

import subprocess
import sys
import os

def main():
    print("🚀 Deploying Railway PIL Fix")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("main_railway_supabase_only.py"):
        print("❌ main_railway_supabase_only.py not found!")
        return False
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return False
    
    print("✅ Files ready for deployment")
    
    try:
        print("📝 Adding files to git...")
        subprocess.run(["git", "add", "."], check=True)
        
        print("📝 Creating commit...")
        commit_message = "Railway: Fix PIL import error - remove pdf_compressor dependency"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        print("🚀 Pushing to Railway...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ Deployment initiated!")
        print("⏳ Railway will now build with minimal requirements (no Pillow)")
        print("📱 Check Railway dashboard for build status")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Railway PIL Fix Deployment")
    print("This removes pdf_compressor dependency to fix PIL import error")
    print()
    
    response = input("Deploy the fix? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        success = main()
        if success:
            print("\n🎉 Railway deployment initiated!")
            print("📋 Changes:")
            print("  ✅ Removed pdf_compressor imports")
            print("  ✅ Disabled PDF compression commands")
            print("  ✅ Using minimal requirements (no Pillow)")
            print("  ✅ Supabase-only mode (no SQLite fallback)")
        else:
            print("\n❌ Deployment failed. Check errors above.")
    else:
        print("\n⏸️ Deployment cancelled.")
