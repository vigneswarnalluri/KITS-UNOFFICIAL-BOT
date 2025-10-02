#!/usr/bin/env python3
"""
Supabase Environment Setup Helper
This script helps you configure your .env file with Supabase credentials
"""

import os

def create_env_file():
    """Create or update .env file with Supabase configuration"""
    
    print("🔧 SUPABASE ENVIRONMENT SETUP")
    print("=" * 40)
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ Found existing .env file")
        response = input("Do you want to update it with Supabase credentials? (y/n): ").lower().strip()
        if response != 'y':
            print("Setup cancelled.")
            return
    else:
        print("📝 Creating new .env file")
    
    print("\n📋 Please provide your Supabase credentials:")
    print("(You can find these in your Supabase project dashboard → Settings → Database)")
    
    # Get Supabase credentials from user
    supabase_host = input("Enter your Supabase Host (e.g., db.xxxxxxxxxxxxx.supabase.co): ").strip()
    supabase_password = input("Enter your Supabase Password: ").strip()
    
    # Get Telegram credentials
    print("\n📱 Please provide your Telegram Bot credentials:")
    bot_token = input("Enter your BOT_TOKEN: ").strip()
    api_id = input("Enter your API_ID: ").strip()
    api_hash = input("Enter your API_HASH: ").strip()
    
    # Get developer chat ID
    developer_chat_id = input("Enter your DEVELOPER_CHAT_ID (optional): ").strip()
    maintainer_chat_id = input("Enter your MAINTAINER_CHAT_ID (optional): ").strip()
    
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

# Supabase Database Configuration (Required for deployment)
# Get these from your Supabase project settings
SUPABASE_USER=postgres
SUPABASE_PASSWORD={supabase_password}
SUPABASE_DATABASE=postgres
SUPABASE_HOST={supabase_host}
SUPABASE_PORT=5432

# Legacy PostgreSQL Database Configuration (Optional)
# The bot will work with SQLite only if PostgreSQL is not configured
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
        
        print("\n✅ .env file created successfully!")
        print("📁 Your .env file contains:")
        print("   - Telegram Bot credentials")
        print("   - Supabase database credentials")
        print("   - Developer/Maintainer chat IDs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_supabase_connection():
    """Test Supabase connection"""
    print("\n🧪 Testing Supabase connection...")
    
    try:
        from load_env import load_environment
        from DATABASE.supabase_database import supabase_db
        
        # Load environment variables
        load_environment()
        
        # Test connection
        import asyncio
        async def test_connection():
            try:
                await supabase_db.create_pool()
                print("✅ Supabase connection successful!")
                return True
            except Exception as e:
                print(f"❌ Supabase connection failed: {e}")
                return False
            finally:
                await supabase_db.close_pool()
        
        result = asyncio.run(test_connection())
        return result
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed all requirements: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 KITS Bot - Supabase Connection Setup")
    print("=" * 50)
    
    # Step 1: Create .env file
    if create_env_file():
        print("\n" + "="*50)
        
        # Step 2: Test connection
        if test_supabase_connection():
            print("\n🎉 SUPABASE SETUP COMPLETED SUCCESSFULLY!")
            print("Your KITS Bot is now connected to Supabase!")
            print("\nNext steps:")
            print("1. Run: python setup_supabase.py")
            print("2. Run: python main.py")
            print("3. Your bot will use Supabase database!")
        else:
            print("\n⚠️ Setup completed but connection test failed.")
            print("Please check your Supabase credentials and try again.")
    else:
        print("\n❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main()
