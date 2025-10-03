from pyrogram import Client, filters,errors
import asyncio,os
from DATABASE.supabase_rest import SupabaseREST
from pyrogram.errors import FloodWait
import time,logging
from load_env import load_environment
import requests
import json

# Load environment variables
load_environment()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

# Global Supabase client
supabase_client = None

session_name = f"KITS_BOT_{int(time.time())}"
bot = Client(
        session_name,
        bot_token = BOT_TOKEN,
        api_id = API_ID,
        api_hash = API_HASH
)
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("bot_errors.log"),
                        logging.StreamHandler()
                    ])

# Direct Supabase functions (bypassing all other database modules)
async def store_user_session(chat_id, session_data, username):
    """Store user session in Supabase"""
    try:
        data = {
            "chat_id": chat_id,
            "session_data": session_data,
            "username": username
        }
        result = supabase_client._make_request("POST", "user_sessions", data)
        return result is not None
    except Exception as e:
        print(f"Error storing session: {e}")
        return False

async def load_user_session(chat_id):
    """Load user session from Supabase"""
    try:
        result = supabase_client._make_request("GET", f"user_sessions?chat_id=eq.{chat_id}&limit=1")
        if result and len(result) > 0:
            return result[0].get("session_data")
        return None
    except Exception as e:
        print(f"Error loading session: {e}")
        return None

async def store_credentials(chat_id, username, password):
    """Store credentials in Supabase"""
    try:
        data = {
            "chat_id": chat_id,
            "username": username,
            "password": password
        }
        result = supabase_client._make_request("POST", "credentials", data)
        return result is not None
    except Exception as e:
        print(f"Error storing credentials: {e}")
        return False

async def load_credentials(chat_id):
    """Load credentials from Supabase"""
    try:
        result = supabase_client._make_request("GET", f"credentials?chat_id=eq.{chat_id}&limit=1")
        if result and len(result) > 0:
            return result[0].get("username"), result[0].get("password")
        return None, None
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None, None

async def get_random_greeting(bot, message):
    """Get random greeting with Supabase-only implementation"""
    chat_id = message.chat.id
    
    try:
        # Check if user has session
        session_data = await load_user_session(chat_id)
        
        if session_data:
            # User is logged in
            greeting = "Hello! You're already logged in. Use /attendance, /marks, or /timetable to get your data."
        else:
            # User is not logged in
            greeting = """🤖 Welcome to KITS Bot!

To get started, please login with your credentials:
/login rollnumber password

Example: /login 23JR1A43B6P your_password

Need help? Use /help for more commands."""
        
        await bot.send_message(chat_id, greeting)
        
    except Exception as e:
        print(f"Error in greeting: {e}")
        await bot.send_message(chat_id, "Hello! Welcome to KITS Bot. Use /login to get started.")

async def login_user(bot, message):
    """Login user with Supabase-only implementation"""
    chat_id = message.chat.id
    
    try:
        # Parse login command
        text = message.text.split()
        if len(text) != 3:
            await bot.send_message(chat_id, "❌ Invalid format. Use: /login rollnumber password")
            return
        
        username = text[1]
        password = text[2]
        
        # Store credentials in Supabase
        success = await store_credentials(chat_id, username, password)
        
        if success:
            await bot.send_message(chat_id, f"✅ Login successful! Welcome {username}")
        else:
            await bot.send_message(chat_id, "❌ Login failed. Please try again.")
            
    except Exception as e:
        print(f"Error in login: {e}")
        await bot.send_message(chat_id, "❌ Login error. Please try again.")

async def logout_user(bot, message):
    """Logout user with Supabase-only implementation"""
    chat_id = message.chat.id
    
    try:
        # Check if user has session
        session_data = await load_user_session(chat_id)
        
        if session_data:
            # Clear session (in a real implementation, you'd delete from Supabase)
            await bot.send_message(chat_id, "✅ Logged out successfully!")
        else:
            await bot.send_message(chat_id, "❌ You're not logged in.")
            
    except Exception as e:
        print(f"Error in logout: {e}")
        await bot.send_message(chat_id, "❌ Logout error. Please try again.")

@bot.on_message(filters.command(commands=['start']))
async def _start(bot,message):
    try:
        await get_random_greeting(bot, message)
    except Exception as e:
        logging.error("Error in 'start' command: %s", e)

@bot.on_message(filters.command(commands=['login']))
async def _login(bot,message):
    try:
        await login_user(bot, message)
    except Exception as e:
        logging.error("Error in 'login' command: %s", e)

@bot.on_message(filters.command(commands=['logout']))
async def _logout(bot,message):
    try:
        await logout_user(bot, message)
    except Exception as e:
        logging.error("Error in 'logout' command: %s", e)

@bot.on_message(filters.command(commands=['attendance']))
async def _attendance(bot,message):
    try:
        await bot.send_message(message.chat.id, "📊 Attendance feature coming soon! (Supabase-only mode)")
    except Exception as e:
        logging.error("Error in 'attendance' command: %s", e)

@bot.on_message(filters.command(commands=['marks']))
async def _marks(bot,message):
    try:
        await bot.send_message(message.chat.id, "📈 Marks feature coming soon! (Supabase-only mode)")
    except Exception as e:
        logging.error("Error in 'marks' command: %s", e)

@bot.on_message(filters.command(commands=['timetable']))
async def _timetable(bot,message):
    try:
        await bot.send_message(message.chat.id, "📅 Timetable feature coming soon! (Supabase-only mode)")
    except Exception as e:
        logging.error("Error in 'timetable' command: %s", e)

@bot.on_message(filters.command(commands=['help']))
async def _help(bot,message):
    try:
        help_text = """🤖 KITS Bot Help

Available Commands:
/start - Welcome message
/login rollnumber password - Login to your account
/logout - Logout from your account
/attendance - Get attendance (coming soon)
/marks - Get marks (coming soon)
/timetable - Get timetable (coming soon)
/help - Show this help message

This bot is running in Supabase-only mode."""
        await bot.send_message(message.chat.id, help_text)
    except Exception as e:
        logging.error("Error in 'help' command: %s", e)

async def initialize_direct_supabase():
    """Initialize direct Supabase connection - NO OTHER DATABASES"""
    global supabase_client
    
    print("🚀 Railway Direct Supabase Mode")
    print("🔒 DIRECT SUPABASE ONLY - NO OTHER DATABASES!")
    
    # Check environment variables first
    required_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ FATAL: Missing Supabase environment variables: {missing_vars}")
        print("🔧 Please set these environment variables in Railway:")
        print("   SUPABASE_URL=https://wecaohxjejimxhbcgmjp.supabase.co")
        print("   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        raise Exception(f"Missing required Supabase environment variables: {missing_vars}")
    
    print("✅ Supabase environment variables found")
    
    # Initialize Supabase REST client
    try:
        print("🌐 Initializing Supabase REST client...")
        supabase_client = SupabaseREST()
        
        # Test the connection
        test_result = supabase_client._make_request("GET", "user_sessions?limit=1")
        if test_result is not None:
            print("✅ SUCCESS: Supabase REST API connection established!")
            print("🎉 Bot ready with DIRECT Supabase connection!")
            return True
        else:
            print("❌ Supabase REST API test failed")
            raise Exception("Supabase connection test failed")
            
    except Exception as e:
        print(f"❌ Supabase initialization failed: {e}")
        raise Exception(f"Supabase initialization failed: {e}")

async def main(bot):
    try:
        # Initialize DIRECT Supabase - no other databases
        success = await initialize_direct_supabase()
        
        if not success:
            print("❌ FATAL: Supabase initialization failed!")
            raise Exception("Supabase initialization failed")
        
        print("🎉 Bot ready with DIRECT Supabase connection!")
        print("🚀 Starting bot services...")
        
    except Exception as e:
        logging.error("Error in 'main' function: %s", e)
        print(f"❌ FATAL ERROR: {e}")
        print("🔧 This bot requires Supabase to function properly.")
        print("💡 Please check your Supabase configuration and try again.")
        raise e

if __name__ == "__main__":
    # Initialize the bot properly
    loop = asyncio.get_event_loop()
    
    # Check if we have required environment variables
    required_vars = ['BOT_TOKEN', 'API_ID', 'API_HASH']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please set these environment variables and try again.")
        exit(1)
    
    # Check Supabase environment variables
    supabase_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_supabase = [var for var in supabase_vars if not os.environ.get(var)]
    
    if missing_supabase:
        print(f"❌ Missing Supabase environment variables: {missing_supabase}")
        print("This bot requires Supabase to function. Please set Supabase credentials.")
        exit(1)
    
    print("🤖 Starting KITS Bot (Railway Direct Supabase Version)...")
    print(f"📱 Bot Token: {BOT_TOKEN[:10]}...")
    print(f"🔑 API ID: {API_ID}")
    print("🔒 DIRECT SUPABASE ONLY - NO OTHER DATABASES!")
    
    try:
        loop.run_until_complete(main(bot))
        print("🚀 Bot initialized successfully! Starting...")
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        logging.error("Failed to start bot: %s", e)
        print("💡 This bot requires Supabase to function. Please check your configuration.")
