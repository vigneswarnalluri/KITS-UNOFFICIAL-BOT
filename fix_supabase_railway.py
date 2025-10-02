#!/usr/bin/env python3
"""
Fix Supabase Connection on Railway
This script diagnoses and fixes Supabase connectivity issues
"""

import asyncio
import os
import requests
from load_env import load_environment

def check_supabase_project_status():
    """Check if Supabase project is active and accessible"""
    print("🔍 Checking Supabase Project Status...")
    
    load_environment()
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_host = os.environ.get("SUPABASE_HOST")
    
    if not supabase_url or not supabase_host:
        print("❌ Missing Supabase environment variables")
        return False
    
    print(f"📡 Supabase URL: {supabase_url}")
    print(f"🔗 Supabase Host: {supabase_host}")
    
    # Test 1: HTTP connectivity to Supabase
    try:
        print("🌐 Testing HTTP connection to Supabase...")
        response = requests.get(f"{supabase_url}/rest/v1/", timeout=10)
        if response.status_code in [200, 401, 403]:
            print(f"✅ HTTP connection successful (Status: {response.status_code})")
            return True
        else:
            print(f"⚠️ HTTP connection returned: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ HTTP connection failed: {e}")
        return False

async def test_supabase_direct_connection():
    """Test direct PostgreSQL connection to Supabase"""
    print("\n🔌 Testing Direct PostgreSQL Connection...")
    
    try:
        from DATABASE.supabase_database import supabase_db
        
        # Try to create connection pool
        await supabase_db.create_pool()
        print("✅ Direct PostgreSQL connection successful!")
        
        # Test basic query
        conn = await supabase_db.get_connection()
        result = await conn.fetchval("SELECT 1")
        print(f"✅ Database query successful: {result}")
        
        await conn.close()
        await supabase_db.close_pool()
        return True
        
    except Exception as e:
        print(f"❌ Direct PostgreSQL connection failed: {e}")
        return False

async def test_supabase_rest_api():
    """Test Supabase REST API connection"""
    print("\n🌐 Testing Supabase REST API...")
    
    try:
        from DATABASE.supabase_rest import SupabaseREST
        
        rest_client = SupabaseREST()
        
        # Test a simple API call
        result = rest_client._make_request("GET", "user_sessions?limit=1")
        if result is not None:
            print("✅ Supabase REST API connection successful!")
            return True
        else:
            print("❌ Supabase REST API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Supabase REST API test failed: {e}")
        return False

def create_railway_supabase_config():
    """Create optimized Railway configuration for Supabase"""
    print("\n🚀 Creating Railway-Optimized Supabase Configuration...")
    
    # Railway-specific environment variables
    railway_env = """# Railway-Optimized Supabase Configuration

# Container Deployment Flag
CONTAINER_DEPLOYMENT=true

# Telegram Bot Configuration  
API_ID=27523374
API_HASH=b7a72638255400c7107abd58b1f79711
BOT_TOKEN=8007204996:AAGbfj4e6sEefgdI8Ixncl3tVoI6kKnZo28

# Supabase Configuration (Primary Method)
SUPABASE_USER=postgres
SUPABASE_PASSWORD=Viggu@2006
SUPABASE_DATABASE=postgres
SUPABASE_HOST=db.wecaohxjejimxhbcgmjp.supabase.co
SUPABASE_PORT=5432

# Supabase REST API (Fallback Method)
SUPABASE_URL=https://wecaohxjejimxhbcgmjp.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndlY2FvaHhqZWppbXhoYmNnbWpwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkyMjk1NzQsImV4cCI6MjA3NDgwNTU3NH0.MPOSqIjbPLd1zoqwjsCZQBQSeUBMQdRND7lnMOmbCfk

# Railway Network Optimization
DATABASE_URL=postgresql://postgres:Viggu@2006@db.wecaohxjejimxhbcgmjp.supabase.co:5432/postgres
PGHOST=db.wecaohxjejimxhbcgmjp.supabase.co
PGPORT=5432
PGDATABASE=postgres
PGUSER=postgres
PGPASSWORD=Viggu@2006

# Connection Pool Settings (for Railway)
DB_POOL_MIN=1
DB_POOL_MAX=5
DB_TIMEOUT=30

# CRITICAL: Do NOT set these (they cause localhost fallback)
# POSTGRES_HOST=localhost
# POSTGRES_USER_ID=postgres
# POSTGRES_PASSWORD=viggu
"""
    
    try:
        with open('railway_supabase_env.txt', 'w') as f:
            f.write(railway_env)
        print("✅ Created railway_supabase_env.txt")
        return True
    except Exception as e:
        print(f"❌ Failed to create Railway config: {e}")
        return False

def show_supabase_solutions():
    """Show solutions for Supabase connectivity"""
    print("\n🔧 SUPABASE CONNECTION SOLUTIONS")
    print("=" * 50)
    
    print("🎯 OPTION 1: Fix Railway-Supabase Connection")
    print("  1. Use the environment variables from railway_supabase_env.txt")
    print("  2. Add DATABASE_URL for Railway compatibility")
    print("  3. Set connection pool limits for Railway")
    print("  4. Redeploy with optimized settings")
    
    print("\n🎯 OPTION 2: Alternative Deployment Platforms")
    print("  • Render.com - Often has better Supabase connectivity")
    print("  • Heroku - Excellent network infrastructure")
    print("  • DigitalOcean App Platform - Reliable connections")
    
    print("\n🎯 OPTION 3: Supabase Project Optimization")
    print("  1. Check Supabase project region (should match Railway)")
    print("  2. Verify project is not paused")
    print("  3. Check connection limits in Supabase dashboard")
    print("  4. Enable connection pooling in Supabase")
    
    print("\n🎯 OPTION 4: Hybrid Approach (Recommended)")
    print("  • Primary: Supabase REST API (more reliable)")
    print("  • Fallback: Direct PostgreSQL connection")
    print("  • Emergency: SQLite (current working state)")

async def main():
    """Main diagnostic and fix function"""
    print("🔧 SUPABASE-RAILWAY CONNECTION DIAGNOSTIC")
    print("=" * 60)
    
    # Step 1: Check Supabase project status
    http_works = check_supabase_project_status()
    
    # Step 2: Test direct PostgreSQL connection
    postgres_works = await test_supabase_direct_connection()
    
    # Step 3: Test REST API connection
    rest_works = await test_supabase_rest_api()
    
    # Step 4: Create optimized configuration
    config_created = create_railway_supabase_config()
    
    # Step 5: Show solutions
    show_supabase_solutions()
    
    # Summary
    print("\n📊 CONNECTION TEST RESULTS")
    print("=" * 40)
    print(f"HTTP Connection: {'✅' if http_works else '❌'}")
    print(f"PostgreSQL Direct: {'✅' if postgres_works else '❌'}")
    print(f"REST API: {'✅' if rest_works else '❌'}")
    print(f"Railway Config: {'✅' if config_created else '❌'}")
    
    if http_works and (postgres_works or rest_works):
        print("\n🎉 SUPABASE IS WORKING LOCALLY!")
        print("The issue is Railway-specific network connectivity.")
        print("Use the optimized Railway configuration to fix this.")
    elif http_works and rest_works:
        print("\n✅ SUPABASE REST API WORKS!")
        print("Switch to REST API mode for Railway deployment.")
    else:
        print("\n⚠️ SUPABASE CONNECTION ISSUES DETECTED")
        print("Check your Supabase project status and credentials.")

if __name__ == "__main__":
    asyncio.run(main())
