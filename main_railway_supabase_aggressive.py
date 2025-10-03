from pyrogram import Client, filters,errors
import asyncio,os
from DATABASE import tdatabase,pgdatabase,user_settings,managers_handler
from DATABASE.supabase_database import supabase_db
from DATABASE.supabase_rest import SupabaseREST
from METHODS import labs_handler, operations,manager_operations,lab_operations
from Buttons import buttons,manager_buttons
from pyrogram.errors import FloodWait
import time,logging
from load_env import load_environment
import requests

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

# Global database handler
db_handler = None
db_type = None

@bot.on_message(filters.command(commands=['start']))
async def _start(bot,message):
    try:
        await operations.get_random_greeting(bot, message)
    except Exception as e:
        logging.error("Error in 'start' command: %s", e)
@bot.on_message(filters.command(commands=['login']))
async def _login(bot,message):
    try:
        await operations.login(bot, message)
    except Exception as e:
        logging.error("Error in 'login' command: %s", e)
@bot.on_message(filters.command(commands=['logout']))
async def _logout(bot,message):
    try:
        await operations.logout(bot, message)
    except Exception as e:
        logging.error("Error in 'logout' command: %s", e)
@bot.on_message(filters.command(commands=['attendance']))
async def _attendance(bot,message):
    try:
        await operations.attendance(bot, message)
    except Exception as e:
        logging.error("Error in 'attendance' command: %s", e)
@bot.on_message(filters.command(commands=['marks']))
async def _marks(bot,message):
    try:
        await operations.marks(bot, message)
    except Exception as e:
        logging.error("Error in 'marks' command: %s", e)
@bot.on_message(filters.command(commands=['timetable']))
async def _timetable(bot,message):
    try:
        await operations.timetable(bot, message)
    except Exception as e:
        logging.error("Error in 'timetable' command: %s", e)

@bot.on_message(filters.command(commands=['settings']))
async def _settings(bot,message):
    try:
        await operations.settings(bot, message)
    except Exception as e:
        logging.error("Error in 'settings' command: %s", e)

@bot.on_message(filters.command(commands=['labs']))
async def _labs(bot,message):
    try:
        await labs_handler.labs(bot, message)
    except Exception as e:
        logging.error("Error in 'labs' command: %s", e)

@bot.on_message(filters.command(commands=['uploadlab']))
async def _uploadlab(bot,message):
    try:
        await lab_operations.upload_lab(bot, message)
    except Exception as e:
        logging.error("Error in 'uploadlab' command: %s", e)

@bot.on_message(filters.command(commands=['myuploads']))
async def _myuploads(bot,message):
    try:
        await lab_operations.my_uploads(bot, message)
    except Exception as e:
        logging.error("Error in 'myuploads' command: %s", e)

@bot.on_message(filters.command(commands=['report']))
async def _report(bot,message):
    try:
        await operations.report(bot, message)
    except Exception as e:
        logging.error("Error in 'report' command: %s", e)

@bot.on_message(filters.command(commands=['manager']))
async def _manager(bot,message):
    try:
        await manager_operations.manager(bot, message)
    except Exception as e:
        logging.error("Error in 'manager' command: %s", e)

@bot.on_message(filters.command(commands=['addmanager']))
async def _addmanager(bot,message):
    try:
        await manager_operations.add_manager(bot, message)
    except Exception as e:
        logging.error("Error in 'addmanager' command: %s", e)

@bot.on_message(filters.command(commands=['removemanager']))
async def _removemanager(bot,message):
    try:
        await manager_operations.remove_manager(bot, message)
    except Exception as e:
        logging.error("Error in 'removemanager' command: %s", e)

@bot.on_message(filters.command(commands=['managerusers']))
async def _managerusers(bot,message):
    try:
        await manager_operations.manager_users(bot, message)
    except Exception as e:
        logging.error("Error in 'managerusers' command: %s", e)

@bot.on_message(filters.command(commands=['managerlogs']))
async def _managerlogs(bot,message):
    try:
        await manager_operations.manager_logs(bot, message)
    except Exception as e:
        logging.error("Error in 'managerlogs' command: %s", e)

@bot.on_message(filters.command(commands=['managerreports']))
async def _managerreports(bot,message):
    try:
        await manager_operations.manager_reports(bot, message)
    except Exception as e:
        logging.error("Error in 'managerreports' command: %s", e)

@bot.on_message(filters.command(commands=['managersettings']))
async def _managersettings(bot,message):
    try:
        await manager_operations.manager_settings(bot, message)
    except Exception as e:
        logging.error("Error in 'managersettings' command: %s", e)

# PDF compression disabled (Pillow not available)
# @bot.on_message(filters.command(commands=['compresspdfs']))
# async def _compresspdfs(bot,message):
#     try:
#         await pdf_compressor.compress_pdfs(bot, message)
#     except Exception as e:
#         logging.error("Error in 'compresspdfs' command: %s", e)

# PDF document handling disabled (Pillow not available)
# @bot.on_message(filters.document)
# async def _document_handler(bot,message):
#     try:
#         await pdf_compressor.handle_document(bot, message)
#     except Exception as e:
#         logging.error("Error in document handler: %s", e)

@bot.on_callback_query()
async def _callback_query(bot, callback_query):
    try:
        await handle_callback_query(bot, callback_query)
    except Exception as e:
        logging.error("Error in '_callback_function': %s", e)

async def handle_callback_query(bot, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.id
    
    if data.startswith("attendance_threshold_"):
        threshold = int(data.split("_")[-1])
        await operations.set_attendance_threshold(bot, callback_query, threshold)
    
    elif data.startswith("bio_threshold_"):
        threshold = int(data.split("_")[-1])
        await operations.set_bio_threshold(bot, callback_query, threshold)
    
    elif data.startswith("ui_"):
        ui_setting = data.split("_")[-1] == "true"
        await operations.set_ui_setting(bot, callback_query, ui_setting)
    
    elif data.startswith("title_"):
        title_setting = data.split("_")[-1] == "true"
        await operations.set_title_setting(bot, callback_query, title_setting)
    
    elif data.startswith("lab_"):
        await labs_handler.handle_lab_callback(bot, callback_query)
    
    elif data.startswith("upload_"):
        await lab_operations.handle_upload_callback(bot, callback_query)
    
    elif data.startswith("manager_"):
        await manager_operations.handle_manager_callback(bot, callback_query)
    
    # PDF compression disabled (Pillow not available)
    # elif data == "compress_pdf":
    #     await pdf_compressor.handle_compress_callback(bot, callback_query)
    
    else:
        # Unknown callback - just answer it
        await callback_query.answer("Unknown command")

async def initialize_supabase_aggressive():
    """Initialize ONLY Supabase - NO FALLBACKS AT ALL"""
    global db_handler, db_type
    
    print("🚀 Railway Aggressive Supabase Mode")
    print("🔒 ABSOLUTELY NO FALLBACKS - SUPABASE REQUIRED!")
    
    # Check environment variables first
    required_supabase_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    missing_vars = [var for var in required_supabase_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"❌ FATAL: Missing Supabase environment variables: {missing_vars}")
        print("🔧 Please set these environment variables in Railway:")
        print("   SUPABASE_URL=https://wecaohxjejimxhbcgmjp.supabase.co")
        print("   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        raise Exception(f"Missing required Supabase environment variables: {missing_vars}")
    
    print("✅ Supabase environment variables found")
    
    # Method 1: Try Supabase REST API first (most reliable on Railway)
    try:
        print("🌐 Attempting Supabase REST API connection...")
        rest_client = SupabaseREST()
        
        # Test the REST connection with a simple query
        test_result = rest_client._make_request("GET", "user_sessions?limit=1")
        if test_result is not None:
            db_handler = rest_client
            db_type = "supabase_rest"
            print("✅ SUCCESS: Supabase REST API connection established!")
            print("🎉 Bot ready with Supabase REST API!")
            return True
        else:
            print("❌ Supabase REST API test failed - no data returned")
    except Exception as e:
        print(f"❌ Supabase REST API failed: {e}")
    
    # Method 2: Try direct PostgreSQL connection
    try:
        print("🔌 Attempting direct Supabase PostgreSQL connection...")
        await supabase_db.create_pool()
        await supabase_db.create_all_tables()
        db_handler = supabase_db
        db_type = "supabase_postgres"
        print("✅ SUCCESS: Supabase PostgreSQL connection established!")
        print("🎉 Bot ready with Supabase PostgreSQL!")
        return True
    except Exception as e:
        print(f"❌ Supabase PostgreSQL failed: {e}")
    
    # NO FALLBACK - CRASH IF SUPABASE DOESN'T WORK
    print("❌ FATAL: Supabase connection failed!")
    print("🔧 Troubleshooting steps:")
    print("1. Check your Supabase project status")
    print("2. Verify environment variables are set correctly in Railway")
    print("3. Ensure network connectivity to Supabase")
    print("4. Check Railway logs for network issues")
    print("5. Verify Supabase credentials are correct")
    
    raise Exception("Supabase connection required but failed - no fallback available")

async def main(bot):
    try:
        # Initialize ONLY Supabase - no fallbacks
        success = await initialize_supabase_aggressive()
        
        if not success:
            print("❌ FATAL: Supabase initialization failed!")
            raise Exception("Supabase initialization failed")
        
        print(f"🎉 Bot ready with {db_type} database!")
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
    
    print("🤖 Starting KITS Bot (Railway Aggressive Supabase-Only Version)...")
    print(f"📱 Bot Token: {BOT_TOKEN[:10]}...")
    print(f"🔑 API ID: {API_ID}")
    print("🔒 ABSOLUTELY NO FALLBACKS - SUPABASE REQUIRED!")
    
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
