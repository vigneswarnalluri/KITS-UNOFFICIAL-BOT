#!/usr/bin/env python3
"""
Create .env file with Supabase credentials
"""

def create_env_file():
    """Create .env file with Supabase credentials"""
    
    # Your Supabase credentials
    supabase_host = "db.wecaohxjejimxhbcgmjp.supabase.co"
    supabase_password = "Viggu@2006"
    
    # Get Telegram credentials
    print("Setting up .env file with your Supabase credentials...")
    print(f"Supabase Host: {supabase_host}")
    print(f"Supabase Password: {supabase_password}")
    print()
    
    # Get Telegram credentials
    bot_token = input("Enter your BOT_TOKEN: ").strip()
    api_id = input("Enter your API_ID: ").strip()
    api_hash = input("Enter your API_HASH: ").strip()
    
    # Optional chat IDs
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
SUPABASE_USER=postgres
SUPABASE_PASSWORD={supabase_password}
SUPABASE_DATABASE=postgres
SUPABASE_HOST={supabase_host}
SUPABASE_PORT=5432

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
        
        print("\nSUCCESS: .env file created with Supabase credentials!")
        print(f"Supabase Host: {supabase_host}")
        print(f"Supabase Database: postgres")
        print(f"Supabase Port: 5432")
        print("\nYour bot is now configured to use Supabase!")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create .env file: {e}")
        return False

if __name__ == "__main__":
    create_env_file()
