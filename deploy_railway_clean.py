#!/usr/bin/env python3
"""
Railway Deployment Script for KITS Bot (Clean Version)
This script deploys the bot using the clean version without PostgreSQL issues
"""

import os
import subprocess
import sys
from pathlib import Path

def check_railway_cli():
    """Check if Railway CLI is installed"""
    try:
        result = subprocess.run(['railway', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Railway CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Railway CLI not found")
            return False
    except FileNotFoundError:
        print("❌ Railway CLI not found")
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("📦 Installing Railway CLI...")
    try:
        subprocess.run(['npm', 'install', '-g', '@railway/cli'], check=True)
        print("✅ Railway CLI installed via npm")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Railway CLI via npm")
        print("Please install manually: https://docs.railway.app/develop/cli")
        return False

def create_railway_project():
    """Create a new Railway project"""
    print("🚀 Creating Railway project...")
    try:
        result = subprocess.run(['railway', 'login'], check=True, capture_output=True, text=True)
        print("✅ Logged into Railway")
        
        result = subprocess.run(['railway', 'init'], check=True, capture_output=True, text=True)
        print("✅ Railway project initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create Railway project: {e}")
        return False

def set_environment_variables():
    """Set environment variables for Railway"""
    print("🔧 Setting environment variables...")
    
    env_vars = {
        'BOT_TOKEN': '8007204996:AAGbfj4e6sEefgdI8Ixncl3tVoI6kKnZo28',
        'API_ID': '27523374',
        'API_HASH': 'b7a72638255400c7107abd58b1f79711',
        'SUPABASE_URL': 'https://wecaohxjejimxhbcgmjp.supabase.co',
        'SUPABASE_ANON_KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndlY2FvaHhqZWppbXhoYmNnbWpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkyMjk1NzQsImV4cCI6MjA3NDgwNTU3NH0.MPOSqIjbPLd1zoqwjsCZQBQSeUBMQdRND7lnMOmbCfk',
        'DATABASE_URL': 'postgresql://postgres:Viggu@2006@db.wecaohxjejimxhbcgmjp.supabase.co:5432/postgres',
        'PGHOST': 'db.wecaohxjejimxhbcgmjp.supabase.co',
        'PGPORT': '5432',
        'PGDATABASE': 'postgres',
        'PGUSER': 'postgres',
        'PGPASSWORD': 'Viggu@2006',
        'FORCE_SUPABASE_REST': 'true',
        'DISABLE_SQLITE_FALLBACK': 'true',
        'RAILWAY_SUPABASE_ONLY': 'true'
    }
    
    for key, value in env_vars.items():
        try:
            subprocess.run(['railway', 'variables', 'set', f'{key}={value}'], check=True)
            print(f"✅ Set {key}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Failed to set {key}: {e}")

def deploy_to_railway():
    """Deploy the bot to Railway"""
    print("🚀 Deploying to Railway...")
    try:
        result = subprocess.run(['railway', 'up'], check=True, capture_output=True, text=True)
        print("✅ Deployment successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🤖 KITS Bot Railway Deployment (Clean Version)")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('main_railway_clean.py').exists():
        print("❌ main_railway_clean.py not found. Please run from the project directory.")
        return False
    
    # Check Railway CLI
    if not check_railway_cli():
        if not install_railway_cli():
            return False
    
    # Create Railway project
    if not create_railway_project():
        return False
    
    # Set environment variables
    set_environment_variables()
    
    # Deploy
    if not deploy_to_railway():
        return False
    
    print("\n🎉 Deployment completed successfully!")
    print("Your bot should now be running on Railway with the clean version!")
    print("Check the Railway dashboard for logs and status.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
