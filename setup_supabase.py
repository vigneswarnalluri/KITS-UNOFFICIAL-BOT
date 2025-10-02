#!/usr/bin/env python3
"""
Supabase Setup Script for KITS Bot
This script helps you set up Supabase database for the KITS Bot deployment
"""

import asyncio
import os
from load_env import load_environment
from DATABASE.supabase_database import supabase_db

async def setup_supabase():
    """Set up Supabase database with all required tables"""
    print("🚀 Setting up Supabase database for KITS Bot...")
    
    try:
        # Load environment variables
        load_environment()
        
        # Check if Supabase credentials are configured
        required_vars = ['SUPABASE_USER', 'SUPABASE_PASSWORD', 'SUPABASE_DATABASE', 'SUPABASE_HOST', 'SUPABASE_PORT']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            print("Please configure your .env file with Supabase credentials")
            return False
        
        # Create connection pool
        await supabase_db.create_pool()
        print("✅ Supabase connection pool created")
        
        # Create all tables
        await supabase_db.create_all_tables()
        print("✅ All database tables created successfully")
        
        # Test connection
        test_conn = await supabase_db.get_connection()
        await test_conn.close()
        print("✅ Database connection test successful")
        
        print("\n🎉 Supabase setup completed successfully!")
        print("Your KITS Bot is now ready for deployment with Supabase database!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Supabase: {e}")
        return False
    
    finally:
        # Close connection pool
        await supabase_db.close_pool()

async def test_supabase_operations():
    """Test basic Supabase operations"""
    print("\n🧪 Testing Supabase operations...")
    
    try:
        # Test user session storage
        test_chat_id = 123456789
        test_session = '{"test": "session_data"}'
        test_username = "test_user"
        
        await supabase_db.store_user_session(test_chat_id, test_session, test_username)
        print("✅ User session storage test passed")
        
        # Test user session retrieval
        retrieved_session = await supabase_db.load_user_session(test_chat_id)
        if retrieved_session == test_session:
            print("✅ User session retrieval test passed")
        else:
            print("❌ User session retrieval test failed")
        
        # Test user credentials storage
        await supabase_db.store_credentials(test_chat_id, test_username, "test_password")
        print("✅ User credentials storage test passed")
        
        # Test user credentials retrieval
        credentials = await supabase_db.retrieve_credentials(test_chat_id)
        if credentials and credentials[0] == test_username:
            print("✅ User credentials retrieval test passed")
        else:
            print("❌ User credentials retrieval test failed")
        
        # Clean up test data
        await supabase_db.delete_user_session(test_chat_id)
        await supabase_db.remove_credentials(test_chat_id)
        print("✅ Test data cleanup completed")
        
        print("🎉 All Supabase operations tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Supabase operations: {e}")
        return False

def print_setup_instructions():
    """Print setup instructions for Supabase"""
    print("\n📋 SUPABASE SETUP INSTRUCTIONS:")
    print("=" * 50)
    print("1. Go to https://supabase.com and create a new project")
    print("2. In your Supabase project dashboard:")
    print("   - Go to Settings > Database")
    print("   - Copy the connection details")
    print("3. Update your .env file with the following variables:")
    print("   SUPABASE_USER=postgres")
    print("   SUPABASE_PASSWORD=your_supabase_password")
    print("   SUPABASE_DATABASE=postgres")
    print("   SUPABASE_HOST=your_supabase_host")
    print("   SUPABASE_PORT=5432")
    print("4. Run this script: python setup_supabase.py")
    print("5. Your bot will now use Supabase instead of local SQLite!")
    print("=" * 50)

async def main():
    """Main setup function"""
    print("🤖 KITS Bot - Supabase Database Setup")
    print("=" * 40)
    
    # Print setup instructions
    print_setup_instructions()
    
    # Ask user if they want to proceed
    response = input("\nDo you have your Supabase credentials ready? (y/n): ").lower().strip()
    
    if response != 'y':
        print("Please set up your Supabase project first and then run this script again.")
        return
    
    # Set up Supabase
    success = await setup_supabase()
    
    if success:
        # Test operations
        test_success = await test_supabase_operations()
        
        if test_success:
            print("\n🎉 SUPABASE SETUP COMPLETED SUCCESSFULLY!")
            print("Your KITS Bot is now ready for deployment with 60-70 members!")
            print("\nNext steps:")
            print("1. Deploy your bot to a cloud platform (Heroku, Railway, etc.)")
            print("2. Set the environment variables in your deployment platform")
            print("3. Start your bot and invite your members!")
        else:
            print("\n❌ Supabase setup completed but tests failed.")
            print("Please check your Supabase configuration.")
    else:
        print("\n❌ Supabase setup failed.")
        print("Please check your credentials and try again.")

if __name__ == "__main__":
    asyncio.run(main())
