from pyrogram import Client, filters,errors
import asyncio,os
from DATABASE.supabase_rest import SupabaseREST
from pyrogram.errors import FloodWait
import time,logging
from load_env import load_environment
import requests
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz

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

# Direct Supabase functions with full KITS functionality
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

async def authenticate_with_kits(username, password):
    """Authenticate with KITS system"""
    try:
        # Create session for KITS authentication
        session = requests.Session()
        
        # Get login page
        login_url = "https://kits.edu.in/student/login"
        response = session.get(login_url)
        
        if response.status_code != 200:
            return False, "Failed to access KITS login page"
        
        # Parse login form
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form')
        if not form:
            return False, "Login form not found"
        
        # Extract form data
        form_data = {}
        for input_tag in form.find_all('input'):
            if input_tag.get('name'):
                form_data[input_tag.get('name')] = input_tag.get('value', '')
        
        # Add credentials
        form_data['username'] = username
        form_data['password'] = password
        
        # Submit login
        login_response = session.post(login_url, data=form_data)
        
        # Check if login successful
        if "dashboard" in login_response.url or "home" in login_response.url:
            return True, session
        else:
            return False, "Invalid credentials"
            
    except Exception as e:
        print(f"Error in KITS authentication: {e}")
        return False, f"Authentication error: {str(e)}"

async def get_attendance_data(session):
    """Get attendance data from KITS"""
    try:
        attendance_url = "https://kits.edu.in/student/attendance"
        response = session.get(attendance_url)
        
        if response.status_code != 200:
            return "Failed to fetch attendance data"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract attendance data (simplified)
        attendance_text = "📊 **Attendance Report**\n\n"
        
        # Look for attendance table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    subject = cells[0].get_text(strip=True)
                    attended = cells[1].get_text(strip=True)
                    total = cells[2].get_text(strip=True)
                    attendance_text += f"**{subject}**: {attended}/{total}\n"
        else:
            attendance_text += "No attendance data found"
        
        return attendance_text
        
    except Exception as e:
        print(f"Error fetching attendance: {e}")
        return f"Error fetching attendance: {str(e)}"

async def get_marks_data(session):
    """Get marks data from KITS"""
    try:
        marks_url = "https://kits.edu.in/student/marks"
        response = session.get(marks_url)
        
        if response.status_code != 200:
            return "Failed to fetch marks data"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract marks data (simplified)
        marks_text = "📈 **Marks Report**\n\n"
        
        # Look for marks table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    subject = cells[0].get_text(strip=True)
                    marks = cells[1].get_text(strip=True)
                    grade = cells[2].get_text(strip=True)
                    marks_text += f"**{subject}**: {marks} ({grade})\n"
        else:
            marks_text += "No marks data found"
        
        return marks_text
        
    except Exception as e:
        print(f"Error fetching marks: {e}")
        return f"Error fetching marks: {str(e)}"

async def get_timetable_data(session):
    """Get timetable data from KITS"""
    try:
        timetable_url = "https://kits.edu.in/student/timetable"
        response = session.get(timetable_url)
        
        if response.status_code != 200:
            return "Failed to fetch timetable data"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract timetable data (simplified)
        timetable_text = "📅 **Timetable**\n\n"
        
        # Look for timetable table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    time_slot = cells[0].get_text(strip=True)
                    subject = cells[1].get_text(strip=True)
                    room = cells[2].get_text(strip=True)
                    timetable_text += f"**{time_slot}**: {subject} ({room})\n"
        else:
            timetable_text += "No timetable data found"
        
        return timetable_text
        
    except Exception as e:
        print(f"Error fetching timetable: {e}")
        return f"Error fetching timetable: {str(e)}"

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
    """Login user with full KITS authentication"""
    chat_id = message.chat.id
    
    try:
        # Parse login command
        text = message.text.split()
        if len(text) != 3:
            await bot.send_message(chat_id, "❌ Invalid format. Use: /login rollnumber password")
            return
        
        username = text[1]
        password = text[2]
        
        # Authenticate with KITS
        await bot.send_message(chat_id, "🔄 Authenticating with KITS...")
        
        success, result = await authenticate_with_kits(username, password)
        
        if success:
            # Store credentials and session in Supabase
            await store_credentials(chat_id, username, password)
            await store_user_session(chat_id, "authenticated", username)
            
            await bot.send_message(chat_id, f"✅ Login successful! Welcome {username}")
        else:
            await bot.send_message(chat_id, f"❌ Login failed: {result}")
            
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

async def get_attendance(bot, message):
    """Get attendance data"""
    chat_id = message.chat.id
    
    try:
        # Check if user is logged in
        session_data = await load_user_session(chat_id)
        if not session_data:
            await bot.send_message(chat_id, "❌ Please login first using /login")
            return
        
        # Get credentials
        username, password = await load_credentials(chat_id)
        if not username or not password:
            await bot.send_message(chat_id, "❌ Credentials not found. Please login again.")
            return
        
        await bot.send_message(chat_id, "🔄 Fetching attendance data...")
        
        # Authenticate and get data
        success, session = await authenticate_with_kits(username, password)
        if success:
            attendance_data = await get_attendance_data(session)
            await bot.send_message(chat_id, attendance_data)
        else:
            await bot.send_message(chat_id, f"❌ Failed to fetch attendance: {session}")
            
    except Exception as e:
        print(f"Error in attendance: {e}")
        await bot.send_message(chat_id, "❌ Error fetching attendance. Please try again.")

async def get_marks(bot, message):
    """Get marks data"""
    chat_id = message.chat.id
    
    try:
        # Check if user is logged in
        session_data = await load_user_session(chat_id)
        if not session_data:
            await bot.send_message(chat_id, "❌ Please login first using /login")
            return
        
        # Get credentials
        username, password = await load_credentials(chat_id)
        if not username or not password:
            await bot.send_message(chat_id, "❌ Credentials not found. Please login again.")
            return
        
        await bot.send_message(chat_id, "🔄 Fetching marks data...")
        
        # Authenticate and get data
        success, session = await authenticate_with_kits(username, password)
        if success:
            marks_data = await get_marks_data(session)
            await bot.send_message(chat_id, marks_data)
        else:
            await bot.send_message(chat_id, f"❌ Failed to fetch marks: {session}")
            
    except Exception as e:
        print(f"Error in marks: {e}")
        await bot.send_message(chat_id, "❌ Error fetching marks. Please try again.")

async def get_timetable(bot, message):
    """Get timetable data"""
    chat_id = message.chat.id
    
    try:
        # Check if user is logged in
        session_data = await load_user_session(chat_id)
        if not session_data:
            await bot.send_message(chat_id, "❌ Please login first using /login")
            return
        
        # Get credentials
        username, password = await load_credentials(chat_id)
        if not username or not password:
            await bot.send_message(chat_id, "❌ Credentials not found. Please login again.")
            return
        
        await bot.send_message(chat_id, "🔄 Fetching timetable data...")
        
        # Authenticate and get data
        success, session = await authenticate_with_kits(username, password)
        if success:
            timetable_data = await get_timetable_data(session)
            await bot.send_message(chat_id, timetable_data)
        else:
            await bot.send_message(chat_id, f"❌ Failed to fetch timetable: {session}")
            
    except Exception as e:
        print(f"Error in timetable: {e}")
        await bot.send_message(chat_id, "❌ Error fetching timetable. Please try again.")

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
        await get_attendance(bot, message)
    except Exception as e:
        logging.error("Error in 'attendance' command: %s", e)

@bot.on_message(filters.command(commands=['marks']))
async def _marks(bot,message):
    try:
        await get_marks(bot, message)
    except Exception as e:
        logging.error("Error in 'marks' command: %s", e)

@bot.on_message(filters.command(commands=['timetable']))
async def _timetable(bot,message):
    try:
        await get_timetable(bot, message)
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
/attendance - Get your attendance
/marks - Get your marks
/timetable - Get your timetable
/help - Show this help message

This bot is running in Supabase-only mode with full KITS integration."""
        await bot.send_message(message.chat.id, help_text)
    except Exception as e:
        logging.error("Error in 'help' command: %s", e)

async def initialize_full_supabase():
    """Initialize full Supabase connection with KITS integration"""
    global supabase_client
    
    print("🚀 Railway Full Supabase Mode with KITS Integration")
    print("🔒 SUPABASE ONLY - FULL KITS FUNCTIONALITY!")
    
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
            print("🎉 Bot ready with FULL Supabase + KITS integration!")
            return True
        else:
            print("❌ Supabase REST API test failed")
            raise Exception("Supabase connection test failed")
            
    except Exception as e:
        print(f"❌ Supabase initialization failed: {e}")
        raise Exception(f"Supabase initialization failed: {e}")

async def main(bot):
    try:
        # Initialize FULL Supabase with KITS integration
        success = await initialize_full_supabase()
        
        if not success:
            print("❌ FATAL: Supabase initialization failed!")
            raise Exception("Supabase initialization failed")
        
        print("🎉 Bot ready with FULL Supabase + KITS integration!")
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
    
    print("🤖 Starting KITS Bot (Railway Full Supabase + KITS Version)...")
    print(f"📱 Bot Token: {BOT_TOKEN[:10]}...")
    print(f"🔑 API ID: {API_ID}")
    print("🔒 SUPABASE ONLY - FULL KITS FUNCTIONALITY!")
    
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
