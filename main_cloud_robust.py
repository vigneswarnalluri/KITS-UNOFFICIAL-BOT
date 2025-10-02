from pyrogram import Client, filters,errors
import asyncio,os
from DATABASE import tdatabase,pgdatabase,user_settings,managers_handler
from DATABASE.supabase_database import supabase_db
from DATABASE.supabase_rest import SupabaseREST
from METHODS import labs_handler, operations,manager_operations,lab_operations,pdf_compressor
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

@bot.on_message(filters.command(commands=['help']))
async def _help(bot,message):
    try:
        await operations.help_command(bot, message)
    except Exception as e:
        logging.error("Error in 'help' command: %s", e)

@bot.on_message(filters.command(commands=['attendance']))
async def _attendance(bot,message):
    try:
        await operations.attendance(bot, message)
    except Exception as e:
        logging.error("Error in 'attendance' command: %s", e)

@bot.on_message(filters.command(commands=['bioattendance']))
async def _bioattendance(bot,message):
    try:
        await operations.bioattendance(bot, message)
    except Exception as e:
        logging.error("Error in 'bioattendance' command: %s", e)

@bot.on_message(filters.command(commands=['cgpa']))
async def _cgpa(bot,message):
    try:
        await operations.cgpa(bot, message)
    except Exception as e:
        logging.error("Error in 'cgpa' command: %s", e)

@bot.on_message(filters.command(commands=['cie']))
async def _cie(bot,message):
    try:
        await operations.cie(bot, message)
    except Exception as e:
        logging.error("Error in 'cie' command: %s", e)

@bot.on_message(filters.command(commands=['fee']))
async def _fee(bot,message):
    try:
        await operations.fee(bot, message)
    except Exception as e:
        logging.error("Error in 'fee' command: %s", e)

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

@bot.on_message(filters.command(commands=['compresspdfs']))
async def _compresspdfs(bot,message):
    try:
        await pdf_compressor.compress_pdfs(bot, message)
    except Exception as e:
        logging.error("Error in 'compresspdfs' command: %s", e)

@bot.on_message(filters.document)
async def _document_handler(bot,message):
    try:
        await pdf_compressor.handle_document(bot, message)
    except Exception as e:
        logging.error("Error in document handler: %s", e)

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
    
    elif data == "compress_pdf":
        await pdf_compressor.handle_compress_callback(bot, callback_query)
    
    else:
        # Unknown callback - just answer it
        await callback_query.answer("Unknown command")

async def test_supabase_connectivity():
    """Test different methods to connect to Supabase"""
    print("🔍 Testing Supabase connectivity methods...")
    
    # Method 1: Test HTTP connectivity to Supabase
    try:
        supabase_url = os.environ.get("SUPABASE_URL")
        if supabase_url:
            print(f"🌐 Testing HTTP connection to: {supabase_url}")
            response = requests.get(f"{supabase_url}/rest/v1/", timeout=10)
            if response.status_code in [200, 401, 403]:  # 401/403 means server is reachable
                print("✅ HTTP connection to Supabase successful!")
                return "http"
            else:
                print(f"⚠️ HTTP connection returned: {response.status_code}")
        else:
            print("❌ SUPABASE_URL not set")
    except Exception as e:
        print(f"❌ HTTP connection failed: {e}")
    
    # Method 2: Test direct PostgreSQL connection
    try:
        print("🔌 Testing direct PostgreSQL connection...")
        await supabase_db.create_pool()
        print("✅ Direct PostgreSQL connection successful!")
        return "postgres"
    except Exception as e:
        print(f"❌ Direct PostgreSQL connection failed: {e}")
    
    return None

async def initialize_database():
    """Initialize database with fallback methods"""
    global db_handler, db_type
    
    print("🚀 Cloud Deployment - Initializing Database...")
    
    # Test connectivity methods
    connection_method = await test_supabase_connectivity()
    
    if connection_method == "postgres":
        # Use direct PostgreSQL connection
        try:
            await supabase_db.create_pool()
            await supabase_db.create_all_tables()
            db_handler = supabase_db
            db_type = "supabase_postgres"
            print("✅ SUCCESS: Supabase PostgreSQL connection established!")
            return True
        except Exception as e:
            print(f"❌ Supabase PostgreSQL failed: {e}")
    
    elif connection_method == "http":
        # Use Supabase REST API
        try:
            rest_client = SupabaseREST()
            # Test the REST connection
            test_result = rest_client._make_request("GET", "user_sessions?limit=1")
            if test_result is not None:
                db_handler = rest_client
                db_type = "supabase_rest"
                print("✅ SUCCESS: Supabase REST API connection established!")
                return True
            else:
                print("❌ Supabase REST API test failed")
        except Exception as e:
            print(f"❌ Supabase REST API failed: {e}")
    
    # Fallback to local SQLite databases
    print("⚠️ Falling back to local SQLite databases...")
    try:
        # Create all SQLite tables in the correct order
        print("📋 Creating SQLite tables...")
        await tdatabase.create_all_tdatabase_tables()
        print("✅ Created tdatabase tables")
        
        await user_settings.create_user_settings_tables()
        print("✅ Created user_settings tables")
        
        await managers_handler.create_required_bot_manager_tables()
        print("✅ Created managers tables")
        
        # Set default indexes for user settings
        await user_settings.set_default_attendance_indexes()
        print("✅ Set default attendance indexes")
        
        db_type = "sqlite"
        print("✅ SUCCESS: Local SQLite databases initialized!")
        return True
    except Exception as e:
        print(f"❌ SQLite fallback failed: {e}")
        print(f"Error details: {str(e)}")
        return False

async def main(bot):
    try:
        # Initialize database with multiple fallback methods
        success = await initialize_database()
        
        if not success:
            print("❌ FATAL: All database initialization methods failed!")
            raise Exception("Database initialization failed")
        
        print(f"🎉 Bot ready with {db_type} database!")
        print("🚀 Starting bot services...")
        
    except Exception as e:
        logging.error("Error in 'main' function: %s", e)
        print(f"❌ FATAL ERROR: {e}")
        print("🔧 Troubleshooting:")
        print("1. Check your Supabase project status")
        print("2. Verify network connectivity")
        print("3. Ensure environment variables are set correctly")
        print("4. Bot will attempt to continue with local storage")
        
        # Last resort: try to continue with basic SQLite
        try:
            await tdatabase.create_all_tdatabase_tables()
            print("⚠️ Continuing with basic SQLite storage...")
        except:
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
    
    print("🤖 Starting KITS Bot (Cloud Robust Version)...")
    print(f"📱 Bot Token: {BOT_TOKEN[:10]}...")
    print(f"🔑 API ID: {API_ID}")
    
    try:
        loop.run_until_complete(main(bot))
        print("🚀 Bot initialized successfully! Starting...")
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        logging.error("Failed to start bot: %s", e)
