#!/usr/bin/env python3
"""
Manual Supabase Setup
This script helps you configure Supabase with your connection string
"""

import os
import re

def parse_connection_string(connection_string):
    """Parse Supabase connection string to extract credentials"""
    # Format: postgresql://postgres:[YOUR-PASSWORD]@db.wecaohxjejimxhbcgmjp.supabase.co:5432/postgres
    
    pattern = r'postgresql://postgres:([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, connection_string)
    
    if match:
        password = match.group(1)
        host = match.group(2)
        port = match.group(3)
        database = match.group(4)
        
        return {
            'user': 'postgres',
            'password': password,
            'host': host,
            'port': port,
            'database': database
        }
    else:
        return None

def create_env_file(supabase_creds, bot_token=None, api_id=None, api_hash=None):
    """Create .env file with Supabase credentials"""
    
    print("Setting up .env file with Supabase credentials...")
    
    # Get Telegram credentials if not provided
    if not bot_token:
        bot_token = input("Enter your BOT_TOKEN: ").strip()
    if not api_id:
        api_id = input("Enter your API_ID: ").strip()
    if not api_hash:
        api_hash = input("Enter your API_HASH: ").strip()
    
    # Get optional chat IDs
    developer_chat_id = input("Enter DEVELOPER_CHAT_ID (optional): ").strip()
    maintainer_chat_id = input("Enter MAINTAINER_CHAT_ID (optional): ").strip()
    
    # Create .env content
    env_content = f"""# Telegram Bot Configuration
# Get these from https://my.telegram.org/auth
API_ID={api_id}
API_HASH={api_hash}

# Get this from @BotFather on Telegram
BOT_TOKEN={bot_token}

# Developer and Maintainer Chat IDs
# Get these from @RawDataBot on Telegram
DEVELOPER_CHAT_ID={developer_chat_id}
MAINTAINER_CHAT_ID={maintainer_chat_id}

# Supabase Database Configuration
SUPABASE_USER={supabase_creds['user']}
SUPABASE_PASSWORD={supabase_creds['password']}
SUPABASE_DATABASE={supabase_creds['database']}
SUPABASE_HOST={supabase_creds['host']}
SUPABASE_PORT={supabase_creds['port']}

# Legacy PostgreSQL Database Configuration (Optional)
POSTGRES_USER_ID=postgres
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DATABASE=kits_bot_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
"""
    
    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("SUCCESS: .env file created with Supabase credentials!")
        print(f"Host: {supabase_creds['host']}")
        print(f"Database: {supabase_creds['database']}")
        print(f"Port: {supabase_creds['port']}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create .env file: {e}")
        return False

def main():
    """Main setup function"""
    print("KITS Bot - Supabase Manual Setup")
    print("=" * 40)
    
    # Your connection string
    connection_string = "postgresql://postgres:[YOUR-PASSWORD]@db.wecaohxjejimxhbcgmjp.supabase.co:5432/postgres"
    
    print("I can see your Supabase connection string:")
    print(connection_string)
    print()
    print("However, I need you to replace [YOUR-PASSWORD] with your actual password.")
    print("Please provide your Supabase password:")
    
    # Get the actual password
    actual_password = input("Enter your Supabase password: ").strip()
    
    # Replace the placeholder with actual password
    actual_connection_string = connection_string.replace("[YOUR-PASSWORD]", actual_password)
    
    # Parse the connection string
    supabase_creds = parse_connection_string(actual_connection_string)
    
    if not supabase_creds:
        print("ERROR: Could not parse connection string. Please check the format.")
        return
    
    print("SUCCESS: Parsed Supabase credentials!")
    print(f"Host: {supabase_creds['host']}")
    print(f"Database: {supabase_creds['database']}")
    print(f"Port: {supabase_creds['port']}")
    
    # Create .env file
    if create_env_file(supabase_creds):
        print("\nSUCCESS: Supabase setup completed!")
        print("\nNext steps:")
        print("1. Run: python test_supabase_connection.py")
        print("2. Run: python setup_supabase.py")
        print("3. Run: python main.py")
        print("\nYour bot will now use Supabase database!")
    else:
        print("\nERROR: Setup failed. Please try again.")

if __name__ == "__main__":
    main()
