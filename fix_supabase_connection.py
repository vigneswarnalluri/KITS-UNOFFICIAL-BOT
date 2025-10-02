#!/usr/bin/env python3
"""
Fix Supabase Connection Issues
This script helps resolve Supabase connection problems
"""

import asyncio
import os
import socket
from load_env import load_environment

def test_network_connectivity():
    """Test network connectivity to Supabase"""
    print("Testing network connectivity...")
    
    host = "db.wecaohxjejimxhbcgmjp.supabase.co"
    port = 5432
    
    try:
        # Test if we can resolve the hostname
        ip = socket.gethostbyname(host)
        print(f"✅ Hostname resolved to: {ip}")
        
        # Test if we can connect to the port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Port {port} is accessible")
            return True
        else:
            print(f"❌ Port {port} is not accessible")
            return False
            
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_supabase_with_ipv4():
    """Test Supabase connection with IPv4 preference"""
    print("\nTesting Supabase connection with IPv4 preference...")
    
    try:
        from DATABASE.supabase_database import supabase_db
        import asyncpg
        
        # Load environment
        load_environment()
        
        async def test_connection():
            try:
                # Try connecting with IPv4 preference
                connection = await asyncpg.connect(
                    user=os.environ.get("SUPABASE_USER"),
                    password=os.environ.get("SUPABASE_PASSWORD"),
                    database=os.environ.get("SUPABASE_DATABASE"),
                    host=os.environ.get("SUPABASE_HOST"),
                    port=int(os.environ.get("SUPABASE_PORT")),
                    command_timeout=10
                )
                
                print("✅ Supabase connection successful!")
                
                # Test a simple query
                result = await connection.fetchval("SELECT 1")
                print(f"✅ Database query successful: {result}")
                
                await connection.close()
                return True
                
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return False
        
        result = asyncio.run(test_connection())
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def create_alternative_env():
    """Create alternative .env with different connection settings"""
    print("\nCreating alternative connection configuration...")
    
    # Read current .env
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # Add alternative connection settings
        additional_config = """

# Alternative Supabase Configuration (if main connection fails)
SUPABASE_ALT_HOST=db.wecaohxjejimxhbcgmjp.supabase.co
SUPABASE_ALT_PORT=5432
SUPABASE_ALT_USER=postgres
SUPABASE_ALT_PASSWORD=Viggu@2006
SUPABASE_ALT_DATABASE=postgres
"""
        
        # Append to .env
        with open('.env', 'a') as f:
            f.write(additional_config)
        
        print("✅ Alternative configuration added to .env")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env: {e}")
        return False

def main():
    """Main troubleshooting function"""
    print("🔧 Supabase Connection Troubleshooting")
    print("=" * 50)
    
    # Test 1: Network connectivity
    if test_network_connectivity():
        print("\n✅ Network connectivity is working")
        
        # Test 2: Direct Supabase connection
        if test_supabase_with_ipv4():
            print("\n🎉 Supabase connection is working!")
            print("Your bot should be able to connect to Supabase.")
        else:
            print("\n⚠️ Direct connection failed, but network is working.")
            print("This might be a Supabase project configuration issue.")
            print("Check your Supabase project settings.")
    else:
        print("\n❌ Network connectivity issues detected.")
        print("Possible solutions:")
        print("1. Check your internet connection")
        print("2. Try a different DNS server (8.8.8.8, 8.8.4.4)")
        print("3. Check if your firewall is blocking the connection")
        print("4. Try connecting from a different network")
    
    # Create alternative configuration
    create_alternative_env()
    
    print("\n📋 Next Steps:")
    print("1. If connection works: Run 'python main.py'")
    print("2. If connection fails: Use local PostgreSQL (already working)")
    print("3. For deployment: Fix network issues or use cloud platform")

if __name__ == "__main__":
    main()
