#!/usr/bin/env python3
"""
Quick Supabase Setup
Sets up .env file with your Supabase credentials
"""

import os

def setup_supabase():
    """Set up Supabase connection with provided credentials"""
    
    print("Setting up Supabase connection...")
    print("Host: db.wecaohxjejimxhbcgmjp.supabase.co")
    print("Password: Viggu@2006")
    
    # Create .env content with your Supabase credentials
    env_content = """# Telegram Bot Configuration
# Get these from https://my.telegram.org/auth
API_ID=your_api_id_here
API_HASH=your_api_hash_here

# Get this from @BotFather on Telegram
BOT_TOKEN=your_bot_token_here

# Developer and Maintainer Chat IDs
# Get these from @RawDataBot on Telegram
DEVELOPER_CHAT_ID=your_developer_chat_id
MAINTAINER_CHAT_ID=your_maintainer_chat_id

# Supabase Database Configuration
SUPABASE_USER=postgres
SUPABASE_PASSWORD=Viggu@2006
SUPABASE_DATABASE=postgres
SUPABASE_HOST=db.wecaohxjejimxhbcgmjp.supabase.co
SUPABASE_PORT=5432

# Legacy PostgreSQL Database Configuration (Optional)
POSTGRES_USER_ID=postgres
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DATABASE=kits_bot_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
"""
    
    try:
        # Write .env file
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("SUCCESS: .env file created with Supabase credentials!")
        print("Your Supabase connection is configured:")
        print("- Host: db.wecaohxjejimxhbcgmjp.supabase.co")
        print("- Database: postgres")
        print("- Port: 5432")
        print("- User: postgres")
        print("- Password: Viggu@2006")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create .env file: {e}")
        return False

def test_connection():
    """Test Supabase connection"""
    print("\nTesting Supabase connection...")
    
    try:
        from load_env import load_environment
        from DATABASE.supabase_database import supabase_db
        import asyncio
        
        # Load environment
        load_environment()
        
        async def test():
            try:
                await supabase_db.create_pool()
                print("SUCCESS: Supabase connection successful!")
                
                # Create tables
                await supabase_db.create_all_tables()
                print("SUCCESS: Database tables created!")
                
                return True
            except Exception as e:
                print(f"ERROR: Connection failed: {e}")
                return False
            finally:
                await supabase_db.close_pool()
        
        result = asyncio.run(test())
        return result
        
    except ImportError as e:
        print(f"ERROR: Import failed: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("KITS Bot - Quick Supabase Setup")
    print("=" * 40)
    
    # Setup .env file
    if setup_supabase():
        print("\n" + "="*40)
        
        # Test connection
        if test_connection():
            print("\nSUCCESS: Supabase setup completed!")
            print("Your bot is now connected to Supabase!")
            print("\nNext steps:")
            print("1. Update your .env file with Telegram credentials")
            print("2. Run: python main.py")
            print("3. Your bot will use Supabase database!")
        else:
            print("\nWARNING: Setup completed but connection test failed.")
            print("Please check your Supabase credentials.")
    else:
        print("\nERROR: Setup failed. Please try again.")

if __name__ == "__main__":
    main()
