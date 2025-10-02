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

@bot.on_message(filters.command(commands=['report']))
async def _report(bot,message):
    try:
        await operations.report(bot, message)
    except Exception as e:
        logging.error("Error in 'report' command: %s", e)
@bot.on_message(filters.command(commands=['help']))
async def _help(bot,message):
    try:
        await operations.help_command(bot, message)
    except Exception as e:
        logging.error("Error in 'help' command: %s", e)
@bot.on_message(filters.command(commands="settings"))
async def settings_buttons(bot,message):
    # Initializes settings for the user
    chat_id = message.chat.id
    try:
        if await user_settings.fetch_user_settings(chat_id) is None:
            await user_settings.set_user_default_settings(chat_id)
        await buttons.start_user_settings(bot, message)
    except Exception as e:
        logging.error("Error in 'settings' command: %s", e)

# @bot.on_message(filters.command(commands=['attendance']))
async def _attendance(bot,message):
    await operations.attendance(bot,message)
    await buttons.start_user_buttons(bot,message)
# @bot.on_message(filters.command(commands=['biometric']))
async def _biometric(bot,message):
    await operations.biometric(bot,message)
    await buttons.start_user_buttons(bot,message)
# @bot.on_message(filters.command(commands=['bunk']))
async def _bunk(bot,message):
    await operations.bunk(bot,message)
    await buttons.start_user_buttons(bot,message)
# @bot.on_message(filters.command(commands=['profile']))
async def _profile_details(bot,message):
    await operations.profile_details(bot,message)
# @bot.on_message(filters.command(commands=['del_save']))
async def delete_login_details_pgdatabase(bot,message):
    chat_id = message.chat.id
    await pgdatabase.remove_saved_credentials(bot,chat_id)
# @bot.on_message(filters.command(commands="deletepdf"))
async def delete_pdf(bot,message):
    chat_id = message.chat.id
    if await labs_handler.remove_pdf_file(chat_id) is True:
        await bot.send_message(chat_id,"Deleted Successfully")
    else:
        await bot.send_message(chat_id,"Failed")
@bot.on_message(filters.command(commands=['reply']))
async def _reply(bot,message):
    try:
        await operations.reply_to_user(bot, message)
    except Exception as e:
        logging.error("Error in 'reply' command: %s", e)
@bot.on_message(filters.command(commands=['rshow']))
async def _show_requests(bot,message):
    try:
        await operations.show_reports(bot, message)
    except Exception as e:
        logging.error("Error in 'rshow' command: %s", e)

@bot.on_message(filters.command(commands=['announce']))
async def _announce(bot,message):
    try:
        await manager_operations.announcement_to_all_users(bot, message)
    except Exception as e:
        logging.error("Error in 'announce' command: %s", e)

@bot.on_message(filters.command(commands=['lusers']))
async def _users_list(bot,message):
    try:
        await operations.list_users(bot, message.chat.id)
    except Exception as e:
        logging.error("Error in 'lusers' command: %s", e)
@bot.on_message(filters.command(commands=['tusers']))
async def _total_users(bot,message):
    try:
        await operations.total_users(bot, message)
    except Exception as e:
        logging.error("Error in 'tusers' command: %s", e)
@bot.on_message(filters.command(commands=['rclear']))
async def _clear_requests(bot,message):
    try:
        await operations.clean_pending_reports(bot, message)
    except Exception as e:
        logging.error("Error in 'rclear' command: %s", e)
@bot.on_message(filters.command(commands=['reset']))
async def _reset_sqlite(bot,message):
    try:
        await operations.reset_user_sessions_database(bot, message)
    except Exception as e:
        logging.error("Error in 'reset' command: %s", e)
# @bot.on_message(filters.command(commands=["pgtusers"]))
async def _total_users_pg_database(bot,message):
    chat_id = message.chat.id
    await pgdatabase.total_users_pg_database(bot,chat_id)
@bot.on_message(filters.command(commands="admin"))
async def admin_buttons(bot,message):
    chat_id = message.chat.id
    try:
        admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
        if chat_id in admin_chat_ids:
            await manager_buttons.start_admin_buttons(bot, message)
    except Exception as e:
        logging.error("Error in 'admin' command: %s", e)

@bot.on_message(filters.command(commands="maintainer"))
async def maintainer_buttons(bot,message):
    try:
        await manager_buttons.start_maintainer_button(bot, message)
    except Exception as e:
        logging.error("Error in 'maintainer' command: %s", e)
@bot.on_message(filters.command(commands="ban"))
async def ban_username(bot,message):
    try:
        await manager_operations.ban_username(bot, message)
    except Exception as e:
        logging.error("Error in 'ban' command: %s", e)

@bot.on_message(filters.command(commands="unban"))
async def unban_username(bot,message):
    try:
        await manager_operations.unban_username(bot, message)
    except Exception as e:
        logging.error("Error in 'unban' command: %s", e)

@bot.on_message(filters.command(commands="authorize"))
async def authorize_and_add_admin(bot,message):
    try:
        await manager_operations.add_admin_by_authorization(bot, message)
    except Exception as e:
        logging.error("Error in 'authorize' command: %s", e)
@bot.on_message(filters.forwarded | filters.command(commands="add_maintainer"))
async def add_maintainer(bot, message):
    try:
        await labs_handler.download_pdf(bot, message, pdf_compress_scrape=pdf_compressor.use_pdf_compress_scrape)
        await manager_operations.verification_to_add_maintainer(bot, message)
    except Exception as e:
        logging.error("Error in 'add_maintainer' command: %s", e)

@bot.on_message(filters.private & filters.document)
async def _download_pdf(bot,message):
    try:
        await labs_handler.download_pdf(bot, message, pdf_compress_scrape=pdf_compressor.use_pdf_compress_scrape)
    except Exception as e:
        logging.error("Error in '_download_pdf' function: %s", e)


@bot.on_message(filters.private & ~filters.service)
async def _get_title_from_user(bot,message):
    try:
        if message.text:
            await labs_handler.get_title_from_user(bot, message)
    except Exception as e:
        logging.error("Error in '_get_title_from_user' function: %s", e)
            
@bot.on_callback_query()
async def _callback_function(bot,callback_query):
    try:
        # Answer the callback query immediately to prevent duplicate processing
        await callback_query.answer()
        
        if "manager" in callback_query.data:
            await manager_buttons.manager_callback_function(bot, callback_query)
        else:
            # Central callback router
            await handle_callback_query(bot, callback_query)
    except Exception as e:
        logging.error("Error in '_callback_function': %s", e)

async def handle_callback_query(bot, callback_query):
    """
    Central callback router that routes button presses to appropriate handlers
    """
    callback_data = callback_query.data
    message = callback_query.message
    chat_id = message.chat.id
    
    # Route to appropriate operation handler
    if callback_data == "attendance":
        await operations.handle_attendance(bot, message, callback_query)
    elif callback_data == "bunk":
        await operations.handle_bunk(bot, message, callback_query)
    elif callback_data == "biometric":
        await operations.handle_biometric(bot, message, callback_query)
    elif callback_data == "user_gpa":
        await operations.handle_gpa(bot, message, callback_query)
    elif callback_data.startswith("user_gpa_sem-"):
        await operations.handle_gpa_sem_select(bot, message, callback_query)
    elif callback_data == "student_profile":
        await operations.handle_student_profile(bot, message, callback_query)
    elif callback_data == "user_cie":
        await operations.handle_cie(bot, message, callback_query)
    elif callback_data == "logout":
        await operations.handle_logout(bot, message, callback_query)
    elif callback_data == "saved_username":
        await operations.handle_saved_username(bot, message, callback_query)
    elif callback_data == "student_info":
        await operations.handle_student_info(bot, message, callback_query)
    elif callback_data == "payment_details":
        await operations.handle_payment_details(bot, message, callback_query)
    elif callback_data == "certificates_start":
        await operations.handle_certificates_start(bot, message, callback_query)
    elif callback_data.startswith("get_"):
        await operations.handle_certificate_download(bot, message, callback_query)
    elif callback_data == "user_back":
        await operations.handle_user_back(bot, message, callback_query)
    elif callback_data == "settings":
        await operations.handle_settings(bot, message, callback_query)
    elif callback_data in ["attendance_in_pat_button", "pat_attendance"]:
        # Handle PAT attendance callbacks
        await buttons.callback_function(bot, callback_query)
    elif callback_data in ["remove_saved_cred", "remove_logout_saved_cred"]:
        # Handle credential removal callbacks
        await buttons.callback_function(bot, callback_query)
    elif callback_data.startswith("save_credentials"):
        # Handle save credentials callbacks
        await buttons.callback_function(bot, callback_query)
    elif callback_data in ["no_save", "username_saved_options", "attendance_threshold", "biometric_threshold", 
                           "title_extract", "back_settings", "set_auto_title", "set_man_title", "ui", 
                           "save_changes_settings", "labs_data", "clear_labs_data", "lab_record_subject",
                           "lab_upload_start", "lab_upload"]:
        # Handle other button callbacks
        await buttons.callback_function(bot, callback_query)
    else:
        # Only handle specific complex operations that aren't covered by the central router
        if (callback_data.startswith("lab_") or 
            callback_data.startswith("bio_") or 
            callback_data.startswith("manager_") or
            callback_data.startswith("get_") or
            callback_data.startswith("pat_")):
            await buttons.callback_function(bot, callback_query)
        else:
            # Unknown callback - just answer it
            await callback_query.answer("Unknown command")

async def main(bot):
    try:
        # Try to initialize Supabase first (preferred for deployment)
        try:
            await supabase_db.create_pool()
            await supabase_db.create_all_tables()
            print("SUCCESS: Supabase database initialized successfully")
            print("Bot ready for deployment with cloud database!")
        except Exception as supabase_error:
            print(f"WARNING: Supabase not available, falling back to local databases: {supabase_error}")
            logging.warning("Supabase connection failed, using local databases: %s", supabase_error)
            
            # Fallback to local databases with proper initialization
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

    # while True:
    #     cgpa_tracker_chat_ids = await managers_handler.get_all_cgpa_tracker_chat_ids()
    #     cie_tracker_chat_ids = await managers_handler.get_all_cie_tracker_chat_ids()
    #     if cgpa_tracker_chat_ids:
    #         for chat_id in cgpa_tracker_chat_ids:
    #             await manager_operations.cgpa_tracker(bot,chat_id)
    #     if cie_tracker_chat_ids:
    #         for chat_id in cie_tracker_chat_ids:
    #             await manager_operations.cie_tracker(bot,chat_id)
    #     await asyncio.sleep(300)

if __name__ == "__main__":
    # Initialize the bot properly
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(bot))
    bot.run()
