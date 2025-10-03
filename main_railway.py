"""
Railway-optimized main.py for Telegram bots
This version is configured specifically for Railway deployment
"""

from pyrogram import Client, filters,errors
import asyncio,os
from DATABASE import tdatabase,pgdatabase,user_settings,managers_handler
from METHODS import labs_handler, operations,manager_operations,lab_operations
# Use simplified PDF compressor for Railway deployment
from METHODS.pdf_compressor_simple import compress_pdf_scrape as pdf_compressor
from Buttons import buttons,manager_buttons
from pyrogram.errors import FloodWait
import time,logging,glob,threading
from load_env import load_environment

# Load environment variables
load_environment()

def cleanup_old_files():
    """Clean up old session files and temporary files"""
    try:
        # Remove old session files (but not the current one)
        current_session = "KITS_BOT.session"
        for session_file in glob.glob("KITS_BOT_*.session*"):
            if os.path.exists(session_file) and session_file != current_session:
                try:
                    os.remove(session_file)
                    print(f"🧹 Cleaned up old session file: {session_file}")
                except PermissionError:
                    print(f"⚠️ Could not remove {session_file} (file in use)")
                except Exception as e:
                    print(f"⚠️ Could not remove {session_file}: {e}")
        
        # Clean up log files if they get too large (>10MB)
        log_file = "bot_errors.log"
        if os.path.exists(log_file) and os.path.getsize(log_file) > 10 * 1024 * 1024:
            try:
                os.remove(log_file)
                print(f"🧹 Cleaned up large log file: {log_file}")
            except Exception as e:
                print(f"⚠️ Could not clean log file: {e}")
                
    except Exception as e:
        print(f"⚠️ Warning: Could not clean up old files: {e}")

# Clean up old files on startup
cleanup_old_files()

def start_railway_keep_alive():
    """Start Railway keep-alive service in background thread"""
    def keep_alive_worker():
        import requests
        while True:
            try:
                # Ping external service to keep Railway awake
                response = requests.get("https://httpbin.org/get", timeout=10)
                if response.status_code == 200:
                    print("✅ Railway keep-alive ping successful")
                else:
                    print(f"⚠️ Railway ping failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Railway keep-alive error: {e}")
            
            # Wait 5 minutes before next ping
            time.sleep(300)
    
    # Start keep-alive in background thread
    keep_alive_thread = threading.Thread(target=keep_alive_worker, daemon=True)
    keep_alive_thread.start()
    print("🚀 Railway keep-alive service started")

# Start Railway keep-alive service
start_railway_keep_alive()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
import time
session_name = "KITS_BOT"
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
        await operations.login_user(bot, message)
    except Exception as e:
        logging.error("Error in 'login' command: %s", e)

@bot.on_message(filters.command(commands=['help']))
async def _help(bot,message):
    try:
        await operations.help_user(bot, message)
    except Exception as e:
        logging.error("Error in 'help' command: %s", e)

@bot.on_message(filters.command(commands=['status']))
async def _status(bot,message):
    try:
        await operations.status_user(bot, message)
    except Exception as e:
        logging.error("Error in 'status' command: %s", e)

@bot.on_message(filters.command(commands=['admin']))
async def _admin(bot,message):
    try:
        await manager_operations.admin_panel(bot, message)
    except Exception as e:
        logging.error("Error in 'admin' command: %s", e)

@bot.on_message(filters.command(commands=['announce']))
async def _announce(bot,message):
    try:
        await manager_operations.announce_to_all_users(bot, message)
    except Exception as e:
        logging.error("Error in 'announce' command: %s", e)

@bot.on_message(filters.command(commands=['ban']))
async def _ban(bot,message):
    try:
        await manager_operations.ban_user(bot, message)
    except Exception as e:
        logging.error("Error in 'ban' command: %s", e)

@bot.on_message(filters.command(commands=['unban']))
async def _unban(bot,message):
    try:
        await manager_operations.unban_user(bot, message)
    except Exception as e:
        logging.error("Error in 'unban' command: %s", e)

@bot.on_message(filters.command(commands=['authorize']))
async def _authorize(bot,message):
    try:
        await manager_operations.authorize_user(bot, message)
    except Exception as e:
        logging.error("Error in 'authorize' command: %s", e)

@bot.on_message(filters.command(commands=['rshow']))
async def _rshow(bot,message):
    try:
        await manager_operations.show_requests(bot, message)
    except Exception as e:
        logging.error("Error in 'rshow' command: %s", e)

@bot.on_message(filters.command(commands=['rclear']))
async def _rclear(bot,message):
    try:
        await manager_operations.clear_requests(bot, message)
    except Exception as e:
        logging.error("Error in 'rclear' command: %s", e)

@bot.on_message(filters.command(commands=['lusers']))
async def _lusers(bot,message):
    try:
        await manager_operations.list_users(bot, message)
    except Exception as e:
        logging.error("Error in 'lusers' command: %s", e)

@bot.on_message(filters.command(commands=['tusers']))
async def _tusers(bot,message):
    try:
        await manager_operations.total_users(bot, message)
    except Exception as e:
        logging.error("Error in 'tusers' command: %s", e)

@bot.on_message(filters.command(commands=['reset']))
async def _reset(bot,message):
    try:
        await manager_operations.reset_database(bot, message)
    except Exception as e:
        logging.error("Error in 'reset' command: %s", e)

@bot.on_message(filters.document)
async def handle_document(bot, message):
    try:
        await labs_handler.handle_lab_upload(bot, message)
    except Exception as e:
        logging.error("Error handling document: %s", e)

@bot.on_callback_query()
async def handle_callback_query(bot, callback_query):
    try:
        if callback_query.data.startswith("manager_"):
            await manager_buttons.callback_function(bot, callback_query)
        else:
            await buttons.callback_function(bot, callback_query)
    except Exception as e:
        logging.error("Error handling callback query: %s", e)
        try:
            await callback_query.answer("Error processing request")
        except:
            pass

async def main(bot):
    try:
        # Initialize local databases
        print("📋 Creating SQLite tables...")
        await tdatabase.create_all_tdatabase_tables()
        print("✅ Created tdatabase tables")
        
        await user_settings.create_user_settings_tables()
        print("✅ Created user_settings tables")
        
        await managers_handler.create_required_bot_manager_tables()
        print("✅ Created managers tables")
        
        # Set default indexes for user settings
        try:
            await user_settings.set_default_attendance_indexes()
            print("✅ Set default attendance indexes")
        except Exception as idx_error:
            print(f"⚠️ Warning: Could not set default indexes: {idx_error}")
        
        print("✅ SUCCESS: Local SQLite databases initialized!")
        
        # Try to create PostgreSQL tables, but don't fail if PostgreSQL is not available
        try:
            await pgdatabase.create_all_pgdatabase_tables()
            print("PostgreSQL connection successful")
        except Exception as pg_error:
            print(f"PostgreSQL not available, continuing with SQLite only: {pg_error}")
            logging.warning("PostgreSQL connection failed, using SQLite only: %s", pg_error)
            
    except Exception as e:
        logging.error("Error in 'main' function: %s", e)

    # Start the bot
    print("🚀 Starting IARE Bot on Railway...")
    await bot.start()
    print("✅ Bot started successfully!")
    print("🔄 Bot is now running 24/7 with keep-alive!")
    
    # Keep the bot running
    await bot.idle()

if __name__ == "__main__":
    try:
        asyncio.run(main(bot))
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    except Exception as e:
        logging.error("Fatal error: %s", e)
        print(f"❌ Fatal error: {e}")
