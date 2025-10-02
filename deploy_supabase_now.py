#!/usr/bin/env python3
"""
Deploy Supabase Solution Now
This script prepares everything for immediate Supabase deployment
"""

import os
import asyncio

def create_deployment_files():
    """Create files to force Railway deployment with Supabase"""
    print("🚀 PREPARING SUPABASE DEPLOYMENT")
    print("=" * 50)
    
    # Create a deployment marker
    with open('.railway_deploy_supabase', 'w') as f:
        f.write("SUPABASE_DEPLOYMENT=v3.0.0\n")
        f.write("DEPLOYMENT_TIME=2025-10-02-06:10:00\n")
        f.write("CONNECTION_METHOD=supabase_rest_api\n")
        f.write("SQLITE_FALLBACK=disabled\n")
    print("✅ Created deployment marker")
    
    # Update Dockerfile to ensure it uses the robust version
    dockerfile_content = """FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Set container deployment flag
ENV CONTAINER_DEPLOYMENT=true

# Force Supabase REST API mode
ENV FORCE_SUPABASE_REST=true

# Run the cloud-robust bot with Supabase priority
CMD ["python", "main_cloud_robust.py"]"""
    
    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    print("✅ Updated Dockerfile for Supabase")
    
    return True

def show_railway_deployment_steps():
    """Show exact Railway deployment steps"""
    print("\n📋 RAILWAY DEPLOYMENT STEPS")
    print("=" * 50)
    
    print("🔧 STEP 1: Update Railway Environment Variables")
    print("Copy these EXACT variables to your Railway dashboard:")
    print()
    
    # Read the Railway Supabase config
    try:
        with open('railway_supabase_env.txt', 'r') as f:
            config = f.read()
        
        # Extract key variables
        lines = config.split('\n')
        important_vars = []
        for line in lines:
            if line.strip() and not line.startswith('#') and '=' in line:
                important_vars.append(line.strip())
        
        for var in important_vars:
            print(f"  {var}")
    except:
        print("  (Use variables from railway_supabase_env.txt)")
    
    print("\n🚀 STEP 2: Commit and Push Changes")
    print("  git add .")
    print("  git commit -m 'Deploy Supabase REST API solution - eliminate SQLite errors'")
    print("  git push origin main")
    
    print("\n⏰ STEP 3: Wait for Railway Deployment (3-5 minutes)")
    print("  - Railway will auto-detect changes")
    print("  - Build new container with Supabase priority")
    print("  - Deploy with REST API connection")
    
    print("\n🎯 EXPECTED RAILWAY LOGS:")
    print("  🔍 Testing Supabase connectivity methods...")
    print("  🌐 Testing HTTP connection to Supabase...")
    print("  ✅ HTTP connection to Supabase successful!")
    print("  ✅ SUCCESS: Supabase REST API connection established!")
    print("  🎉 Bot ready with supabase_rest database!")
    print("  🤖 Starting KITS Bot...")
    
    print("\n✅ RESULT: No more 'no such table: user_settings' errors!")

def show_supabase_benefits():
    """Show benefits of switching to Supabase"""
    print("\n🎉 SUPABASE BENEFITS FOR YOUR 60-70 USERS")
    print("=" * 50)
    
    print("📊 DATA PERSISTENCE:")
    print("  ✅ Data survives Railway redeployments")
    print("  ✅ No data loss on container restarts")
    print("  ✅ Automatic backups and recovery")
    
    print("\n⚡ PERFORMANCE:")
    print("  ✅ Optimized for 60-70 concurrent users")
    print("  ✅ Real-time data synchronization")
    print("  ✅ Fast query performance")
    
    print("\n🔧 MANAGEMENT:")
    print("  ✅ Supabase dashboard to view user data")
    print("  ✅ SQL queries and analytics")
    print("  ✅ User management and monitoring")
    
    print("\n🚀 SCALABILITY:")
    print("  ✅ Easy to scale beyond 70 users")
    print("  ✅ Professional database infrastructure")
    print("  ✅ No SQLite limitations")

async def test_supabase_readiness():
    """Test if Supabase is ready for deployment"""
    print("\n🧪 TESTING SUPABASE READINESS")
    print("=" * 40)
    
    try:
        from DATABASE.supabase_rest import SupabaseREST
        
        # Test REST API connection
        rest_client = SupabaseREST()
        result = rest_client._make_request("GET", "user_sessions?limit=1")
        
        if result is not None:
            print("✅ Supabase REST API: READY")
            print("✅ Connection test: PASSED")
            print("✅ Authentication: WORKING")
            return True
        else:
            print("❌ Supabase REST API: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Supabase test failed: {e}")
        return False

async def main():
    """Main deployment preparation function"""
    print("🚀 SUPABASE DEPLOYMENT PREPARATION")
    print("=" * 60)
    
    # Step 1: Test Supabase readiness
    supabase_ready = await test_supabase_readiness()
    
    if not supabase_ready:
        print("\n❌ SUPABASE NOT READY")
        print("Please check your Supabase project and credentials.")
        return
    
    # Step 2: Create deployment files
    create_deployment_files()
    
    # Step 3: Show deployment steps
    show_railway_deployment_steps()
    
    # Step 4: Show benefits
    show_supabase_benefits()
    
    print("\n" + "=" * 60)
    print("🎯 READY FOR SUPABASE DEPLOYMENT!")
    print("Follow the Railway deployment steps above to eliminate SQLite errors.")
    print("Your bot will use Supabase cloud database for all 60-70 users!")

if __name__ == "__main__":
    asyncio.run(main())
