"""
Railway Debug Script
This script helps identify what's causing the bot to not work on Railway
"""

import os
import sys
import asyncio
from pyrogram import Client

def debug_environment():
    """Debug environment variables"""
    print("🔍 DEBUGGING RAILWAY ENVIRONMENT")
    print("=" * 50)
    
    # Check environment variables
    bot_token = os.environ.get("BOT_TOKEN")
    api_id = os.environ.get("API_ID")
    api_hash = os.environ.get("API_HASH")
    
    print(f"BOT_TOKEN: {'✅ Set' if bot_token else '❌ Missing'}")
    if bot_token:
        print(f"   Length: {len(bot_token)} characters")
        print(f"   Starts with: {bot_token[:10]}...")
    
    print(f"API_ID: {'✅ Set' if api_id else '❌ Missing'}")
    if api_id:
        try:
            api_id_int = int(api_id)
            print(f"   Value: {api_id_int}")
        except ValueError:
            print(f"   ❌ Invalid format: {api_id}")
    
    print(f"API_HASH: {'✅ Set' if api_hash else '❌ Missing'}")
    if api_hash:
        print(f"   Length: {len(api_hash)} characters")
        print(f"   Starts with: {api_hash[:10]}...")
    
    print("\n🔍 SYSTEM INFO")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Platform: {sys.platform}")
    
    # Check if we can import pyrogram
    try:
        import pyrogram
        print(f"Pyrogram version: {pyrogram.__version__}")
    except ImportError as e:
        print(f"❌ Pyrogram import error: {e}")
    
    return bot_token, api_id, api_hash

async def test_bot_connection():
    """Test bot connection"""
    print("\n🤖 TESTING BOT CONNECTION")
    print("=" * 50)
    
    bot_token = os.environ.get("BOT_TOKEN")
    api_id = os.environ.get("API_ID")
    api_hash = os.environ.get("API_HASH")
    
    if not all([bot_token, api_id, api_hash]):
        print("❌ Missing required environment variables")
        return False
    
    try:
        # Create bot client
        bot = Client(
            "debug_bot",
            bot_token=bot_token,
            api_id=int(api_id),
            api_hash=api_hash
        )
        
        print("✅ Bot client created successfully")
        
        # Test connection
        await bot.start()
        print("✅ Bot started successfully")
        
        # Get bot info
        me = await bot.get_me()
        print(f"✅ Bot info retrieved:")
        print(f"   Name: {me.first_name}")
        print(f"   Username: @{me.username}")
        print(f"   ID: {me.id}")
        
        await bot.stop()
        print("✅ Bot stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot connection error: {e}")
        return False

def main():
    """Main debug function"""
    print("🚀 RAILWAY BOT DEBUG SCRIPT")
    print("=" * 50)
    
    # Debug environment
    bot_token, api_id, api_hash = debug_environment()
    
    if not all([bot_token, api_id, api_hash]):
        print("\n❌ CRITICAL: Missing required environment variables!")
        print("Please set BOT_TOKEN, API_ID, and API_HASH in Railway dashboard")
        return
    
    # Test bot connection
    try:
        result = asyncio.run(test_bot_connection())
        if result:
            print("\n🎉 SUCCESS: Bot connection test passed!")
            print("Your bot should work on Railway now.")
        else:
            print("\n❌ FAILED: Bot connection test failed!")
            print("Check your BOT_TOKEN, API_ID, and API_HASH values.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    main()
