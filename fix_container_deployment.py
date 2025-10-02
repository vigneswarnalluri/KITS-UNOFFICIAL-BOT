#!/usr/bin/env python3
"""
Fix Container Deployment Issues
This script helps fix the PostgreSQL localhost fallback issue in containers
"""

import os
import asyncio
from load_env import load_environment

def check_environment_variables():
    """Check current environment variables"""
    print("🔍 Checking Environment Variables...")
    print("=" * 50)
    
    load_environment()
    
    # Supabase variables
    supabase_vars = {
        'SUPABASE_HOST': os.environ.get('SUPABASE_HOST'),
        'SUPABASE_USER': os.environ.get('SUPABASE_USER'),
        'SUPABASE_PASSWORD': os.environ.get('SUPABASE_PASSWORD'),
        'SUPABASE_DATABASE': os.environ.get('SUPABASE_DATABASE'),
        'SUPABASE_PORT': os.environ.get('SUPABASE_PORT')
    }
    
    # PostgreSQL variables
    postgres_vars = {
        'POSTGRES_HOST': os.environ.get('POSTGRES_HOST'),
        'POSTGRES_USER_ID': os.environ.get('POSTGRES_USER_ID'),
        'POSTGRES_PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'POSTGRES_DATABASE': os.environ.get('POSTGRES_DATABASE'),
        'POSTGRES_PORT': os.environ.get('POSTGRES_PORT')
    }
    
    print("📊 Supabase Configuration:")
    for key, value in supabase_vars.items():
        status = "✅ SET" if value else "❌ NOT SET"
        display_value = value if key != 'SUPABASE_PASSWORD' else '***HIDDEN***'
        print(f"  {key}: {display_value} ({status})")
    
    print("\n📊 PostgreSQL Configuration:")
    for key, value in postgres_vars.items():
        status = "✅ SET" if value else "❌ NOT SET"
        display_value = value if key != 'POSTGRES_PASSWORD' else '***HIDDEN***'
        print(f"  {key}: {display_value} ({status})")
    
    return supabase_vars, postgres_vars

async def test_supabase_connection():
    """Test Supabase connection"""
    print("\n🧪 Testing Supabase Connection...")
    print("=" * 50)
    
    try:
        from DATABASE.supabase_database import supabase_db
        
        # Try to create connection pool
        await supabase_db.create_pool()
        print("✅ SUCCESS: Supabase connection pool created!")
        
        # Test basic operation
        conn = await supabase_db.get_connection()
        print("✅ SUCCESS: Got connection from pool!")
        
        # Close connection
        await conn.close()
        await supabase_db.close_pool()
        print("✅ SUCCESS: Connection closed properly!")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Supabase connection error: {e}")
        return False

def create_container_env_template():
    """Create environment template for container deployment"""
    print("\n📝 Creating Container Environment Template...")
    
    template = """# Container Deployment Environment Variables
# Copy these to your deployment platform (Railway, Render, Heroku, etc.)

# Telegram Bot Configuration
API_ID=27523374
API_HASH=b7a72638255400c7107abd58b1f79711
BOT_TOKEN=8007204996:AAGbfj4e6sEefgdI8Ixncl3tVoI6kKnZo28

# Supabase Database Configuration (Primary)
SUPABASE_USER=postgres
SUPABASE_PASSWORD=Viggu@2006
SUPABASE_DATABASE=postgres
SUPABASE_HOST=db.wecaohxjejimxhbcgmjp.supabase.co
SUPABASE_PORT=5432

# Supabase API Configuration
SUPABASE_URL=https://wecaohxjejimxhbcgmjp.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndlY2FvaHhqZWppbXhoYmNnbWpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkyMjk1NzQsImV4cCI6MjA3NDgwNTU3NH0.MPOSqIjbPLd1zoqwjsCZQBQSeUBMQdRND7lnMOmbCfk

# IMPORTANT: DO NOT SET THESE IN CONTAINER DEPLOYMENT
# These cause localhost fallback errors in containers:
# POSTGRES_HOST=localhost
# POSTGRES_USER_ID=postgres
# POSTGRES_PASSWORD=viggu
# POSTGRES_DATABASE=kits_bot_db
# POSTGRES_PORT=5432
"""
    
    try:
        with open('container_env_template.txt', 'w') as f:
            f.write(template)
        print("✅ Created: container_env_template.txt")
        print("📋 Use these environment variables in your deployment platform")
        return True
    except Exception as e:
        print(f"❌ Failed to create template: {e}")
        return False

def show_deployment_instructions():
    """Show deployment instructions"""
    print("\n🚀 Container Deployment Instructions")
    print("=" * 50)
    
    print("🔧 PROBLEM IDENTIFIED:")
    print("  Your container is trying to connect to localhost PostgreSQL")
    print("  which doesn't exist in the container, causing connection errors.")
    
    print("\n✅ SOLUTION:")
    print("  1. Use ONLY Supabase environment variables in your deployment")
    print("  2. DO NOT set POSTGRES_HOST=localhost in container")
    print("  3. The bot will use Supabase directly without PostgreSQL fallback")
    
    print("\n📋 DEPLOYMENT STEPS:")
    print("  1. Copy environment variables from 'container_env_template.txt'")
    print("  2. Set them in your deployment platform (Railway/Render/Heroku)")
    print("  3. Make sure NOT to include POSTGRES_* variables")
    print("  4. Deploy your container")
    
    print("\n🎯 EXPECTED RESULT:")
    print("  ✅ Bot connects directly to Supabase")
    print("  ✅ No localhost PostgreSQL fallback")
    print("  ✅ No connection errors")
    print("  ✅ Ready for 60-70 users")

async def main():
    """Main function"""
    print("🔧 KITS Bot - Container Deployment Fix")
    print("=" * 60)
    
    # Check environment variables
    supabase_vars, postgres_vars = check_environment_variables()
    
    # Test Supabase connection
    supabase_works = await test_supabase_connection()
    
    # Create container template
    create_container_env_template()
    
    # Show instructions
    show_deployment_instructions()
    
    print("\n" + "=" * 60)
    if supabase_works:
        print("🎉 READY FOR DEPLOYMENT!")
        print("Your Supabase connection works. Just fix the environment variables.")
    else:
        print("⚠️ SUPABASE CONNECTION ISSUE")
        print("Fix the Supabase connection first, then deploy.")

if __name__ == "__main__":
    asyncio.run(main())
