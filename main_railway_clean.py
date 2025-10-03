from pyrogram import Client, filters,errors
import asyncio,os
from DATABASE import tdatabase,user_settings,managers_handler
from DATABASE.supabase_database import supabase_db
from METHODS import operations
from Buttons import buttons
from pyrogram.errors import FloodWait
import time,logging
from load_env import load_environment

# Load environment variables
load_environment()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
import time
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

@bot.on_message(filters.command(commands=['start']))
async def _start(bot,message):
    try:
        await operations.get_random_greeting(bot, message)
    except Exception as e:
        logging.error("Error in 'start' command: %s", e)

@bot.on_message(filters.command(commands=['login']))
async def _login(bot,message):
    try:
        await operations.login(bot,message)
    except Exception as e:
        logging.error("Error in 'login' command: %s", e)

@bot.on_message(filters.command(commands=['logout']))
async def _logout(bot,message):
    try:
        await operations.logout(bot,message)
    except Exception as e:
        logging.error("Error in 'logout' command: %s", e)

@bot.on_message(filters.command(commands=['attendance']))
async def _attendance(bot,message):
    try:
        await operations.attendance(bot,message)
    except Exception as e:
        logging.error("Error in 'attendance' command: %s", e)

@bot.on_message(filters.command(commands=['bunk']))
async def _bunk(bot,message):
    try:
        await operations.bunk(bot,message)
    except Exception as e:
        logging.error("Error in 'bunk' command: %s", e)

@bot.on_message(filters.command(commands=['biometric']))
async def _biometric(bot,message):
    try:
        await operations.biometric(bot,message)
    except Exception as e:
        logging.error("Error in 'biometric' command: %s", e)

@bot.on_message(filters.command(commands=['marks']))
async def _marks(bot,message):
    try:
        await operations.cie_marks(bot,message,1)
    except Exception as e:
        logging.error("Error in 'marks' command: %s", e)

@bot.on_message(filters.command(commands=['gpa']))
async def _gpa(bot,message):
    try:
        await operations.gpa_kits_erp(bot,message)
    except Exception as e:
        logging.error("Error in 'gpa' command: %s", e)

@bot.on_message(filters.command(commands=['profile']))
async def _profile(bot,message):
    try:
        await operations.profile_kits_erp(bot,message)
    except Exception as e:
        logging.error("Error in 'profile' command: %s", e)

@bot.on_message(filters.command(commands=['timetable']))
async def _timetable(bot,message):
    try:
        await operations.timetable_kits_erp(bot,message)
    except Exception as e:
        logging.error("Error in 'timetable' command: %s", e)

@bot.on_message(filters.command(commands=['settings']))
async def settings_buttons(bot,message):
    try:
        await user_settings.set_user_default_settings(message.chat.id)
        await buttons.start_user_settings(bot,message)
    except Exception as e:
        logging.error("Error in 'settings' command: %s", e)

@bot.on_message(filters.command(commands=['help']))
async def _help(bot,message):
    try:
        await operations.help(bot,message)
    except Exception as e:
        logging.error("Error in 'help' command: %s", e)

@bot.on_callback_query()
async def _callback_function(bot,callback_query):
    try:
        await buttons.callback_function(bot,callback_query)
    except Exception as e:
        logging.error("Error in '_callback_function': %s", e)

async def main(bot):
    try:
        print("🤖 Starting KITS Bot (Railway Clean Version)...")
        print("📱 Bot Token: " + BOT_TOKEN[:10] + "...")
        print("🔑 API ID: " + str(API_ID))
        
        # Try to initialize Supabase first (preferred for deployment)
        try:
            # Check if we have Supabase environment variables
            supabase_url = os.environ.get('SUPABASE_URL')
            supabase_key = os.environ.get('SUPABASE_ANON_KEY')
            
            if supabase_url and supabase_key:
                print("🌐 Initializing Supabase...")
                await supabase_db.create_pool()
                await supabase_db.create_all_tables()
                print("✅ SUCCESS: Supabase database initialized successfully")
                print("🚀 Bot ready for deployment with cloud database!")
            else:
                print("⚠️ WARNING: Supabase environment variables not found, using local databases")
                raise Exception("Supabase environment variables missing")
        except Exception as supabase_error:
            print(f"⚠️ WARNING: Supabase not available, falling back to local databases: {supabase_error}")
            logging.warning("Supabase connection failed, using local databases: %s", supabase_error)
            
            # Fallback to local databases
            print("📋 Creating local SQLite databases...")
            await tdatabase.create_all_tdatabase_tables()
            await user_settings.create_user_settings_tables()
            await managers_handler.create_required_bot_manager_tables()
            print("✅ SUCCESS: Local SQLite databases initialized!")

    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        logging.error("Database initialization error: %s", e)
        print("⚠️ Bot will continue with limited functionality")

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
    
    try:
        loop.run_until_complete(main(bot))
        print("🚀 Bot initialized successfully! Starting...")
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        logging.error("Failed to start bot: %s", e)
