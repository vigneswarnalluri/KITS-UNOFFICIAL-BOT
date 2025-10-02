from pyrogram import Client, filters,errors
import asyncio,os
from DATABASE import tdatabase,pgdatabase,user_settings,managers_handler
from DATABASE.supabase_database import supabase_db
from METHODS import labs_handler, operations,manager_operations,lab_operations,pdf_compressor
from Buttons import buttons,manager_buttons
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

async def main(bot):
    try:
        # Container deployment - ONLY try Supabase, no PostgreSQL fallback
        print("🚀 Container Deployment Mode - Connecting to Supabase...")
        
        # Check if we're in container deployment mode
        is_container = os.environ.get("CONTAINER_DEPLOYMENT", "false").lower() == "true"
        
        if is_container:
            print("📦 Container deployment detected - Using Supabase only")
            
            # Only try Supabase in container mode
            await supabase_db.create_pool()
            await supabase_db.create_all_tables()
            print("✅ SUCCESS: Supabase database initialized successfully")
            print("🎉 Bot ready for deployment with cloud database!")
            
        else:
            # Local development mode - try Supabase first, then fallback
            try:
                await supabase_db.create_pool()
                await supabase_db.create_all_tables()
                print("SUCCESS: Supabase database initialized successfully")
                print("Bot ready for deployment with cloud database!")
            except Exception as supabase_error:
                print(f"WARNING: Supabase not available, falling back to local databases: {supabase_error}")
                logging.warning("Supabase connection failed, using local databases: %s", supabase_error)
                
                # Fallback to local databases
                await tdatabase.create_all_tdatabase_tables()
                await user_settings.create_user_settings_tables()
                await managers_handler.create_required_bot_manager_tables()
                
                # Try to create PostgreSQL tables, but don't fail if PostgreSQL is not available
                try:
                    await pgdatabase.create_all_pgdatabase_tables()
                    print("PostgreSQL connection successful")
                except Exception as pg_error:
                    print(f"PostgreSQL not available, continuing with SQLite only: {pg_error}")
                    logging.warning("PostgreSQL connection failed, using SQLite only: %s", pg_error)
            
    except Exception as e:
        logging.error("Error in 'main' function: %s", e)
        print(f"❌ FATAL ERROR: {e}")
        print("🔧 Troubleshooting:")
        print("1. Check your Supabase credentials")
        print("2. Verify network connectivity")
        print("3. Ensure environment variables are set correctly")
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
    
    print("🤖 Starting KITS Bot...")
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
