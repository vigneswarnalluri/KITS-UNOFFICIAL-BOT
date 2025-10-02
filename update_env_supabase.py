#!/usr/bin/env python3
"""
Update .env file with Supabase configuration
"""

def update_env_file():
    """Update .env file with Supabase configuration"""
    
    print("Updating .env file with Supabase configuration...")
    
    # Your actual credentials from the image
    env_content = """# Telegram Bot Configuration
API_ID=27523374
API_HASH=b7a72638255400c7107abd58b1f79711
BOT_TOKEN=8007204996:AAGbfj4e6sEefgdI8Ixncl3tVoI6kKnZo28

# KITS ERP Credentials (for testing)
KITS_USERNAME=23JR1A43B6P
KITS_PASSWORD=23JR1A43B6P

# Supabase Database Configuration
SUPABASE_USER=postgres
SUPABASE_PASSWORD=Viggu@2006
SUPABASE_DATABASE=postgres
SUPABASE_HOST=db.wecaohxjejimxhbcgmjp.supabase.co
SUPABASE_PORT=5432

# Legacy PostgreSQL Database Configuration (Optional)
POSTGRES_USER_ID=postgres
POSTGRES_PASSWORD=viggu
POSTGRES_DATABASE=kits_bot_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
"""
    
    try:
        # Write the updated .env file
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("SUCCESS: .env file updated with Supabase configuration!")
        print("Your bot is now configured to use Supabase database!")
        print("\nConfiguration:")
        print("- Telegram Bot: Configured")
        print("- Supabase Host: db.wecaohxjejimxhbcgmjp.supabase.co")
        print("- Supabase Database: postgres")
        print("- Supabase Password: Viggu@2006")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to update .env file: {e}")
        return False

def test_supabase():
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
        
    except Exception as e:
        print(f"ERROR: Test failed: {e}")
        return False

def main():
    """Main function"""
    print("KITS Bot - Supabase Configuration Update")
    print("=" * 50)
    
    # Update .env file
    if update_env_file():
        print("\n" + "="*50)
        
        # Test connection
        if test_supabase():
            print("\nSUCCESS: Supabase setup completed!")
            print("Your bot is now ready to use Supabase database!")
            print("\nNext steps:")
            print("1. Run: python main.py")
            print("2. Test with /start and /login commands")
            print("3. Your bot will use Supabase for all data storage!")
        else:
            print("\nWARNING: Setup completed but connection test failed.")
            print("This might be due to network issues. Try running the bot anyway.")
    else:
        print("\nERROR: Setup failed. Please try again.")

if __name__ == "__main__":
    main()
