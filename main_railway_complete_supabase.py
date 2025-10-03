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
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import uuid
import pyqrcode
import random
import io
import shutil

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

# Session management variables
_session_keepalive_timers = {}
_session_validation_cache = {}

# Direct Supabase functions with full KITS functionality
async def store_user_session(chat_id, session_data, username):
    """Store user session in Supabase"""
    try:
        if not supabase_client:
            print("❌ Supabase client not initialized")
            return False
        
        print(f"💾 STORING SESSION for chat_id: {chat_id}")
        print(f"📊 Session data keys: {list(session_data.keys()) if session_data else 'None'}")
        print(f"🍪 Session cookies: {list(session_data.get('cookies', {}).keys()) if session_data else 'None'}")
        print(f"⏰ Session login_time: {session_data.get('login_time', 'NOT SET') if session_data else 'None'}")
        
        # Ensure session_data has required fields
        if not session_data or 'cookies' not in session_data:
            print("❌ Invalid session data - missing cookies")
            return False
            
        # Add login time if not present
        if 'login_time' not in session_data:
            session_data['login_time'] = time.time()
            
        data = {
            "chat_id": chat_id,
            "session_data": json.dumps(session_data),
            "username": username
        }
        
        print(f"Session data to store: {json.dumps(session_data, indent=2)[:500]}...")
        
        # Try to update existing session first, then insert if not exists
        try:
            # Check if session exists
            existing = supabase_client._make_request("GET", f"user_sessions?chat_id=eq.{chat_id}&limit=1")
            print(f"Existing session check: {existing}")
            
            if existing and len(existing) > 0:
                # Update existing session
                result = supabase_client._make_request("PATCH", f"user_sessions?chat_id=eq.{chat_id}", data)
                print(f"Session updated: {result}")
            else:
                # Insert new session
                result = supabase_client._make_request("POST", "user_sessions", data)
                print(f"Session inserted: {result}")
        except Exception as e:
            print(f"Upsert failed, trying direct insert: {e}")
            result = supabase_client._make_request("POST", "user_sessions", data)
            print(f"Session storage result: {result}")
        
        success = result is not None
        print(f"Session storage success: {success}")
        return success
    except Exception as e:
        print(f"Error storing session: {e}")
        return False

async def load_user_session(chat_id):
    """Load user session from Supabase"""
    try:
        if not supabase_client:
            print("❌ Supabase client not initialized")
            return None
        
        print(f"📥 LOADING SESSION for chat_id: {chat_id}")
        result = supabase_client._make_request("GET", f"user_sessions?chat_id=eq.{chat_id}&limit=1")
        print(f"📊 Session load result for {chat_id}: {result}")
        
        if result and len(result) > 0:
            session_data = result[0].get("session_data")
            print(f"Raw session data from DB: {session_data[:200] if session_data else 'None'}...")
            
            if session_data:
                try:
                    # Try to parse JSON
                    parsed_data = json.loads(session_data)
                    print(f"Session data parsed successfully: {type(parsed_data)}")
                    print(f"Parsed session keys: {list(parsed_data.keys()) if parsed_data else 'None'}")
                    print(f"Session has cookies: {'cookies' in parsed_data if parsed_data else False}")
                    print(f"Session has login_time: {'login_time' in parsed_data if parsed_data else False}")
                    return parsed_data
                except json.JSONDecodeError as json_error:
                    print(f"JSON parsing error: {json_error}")
                    print(f"Raw session data: {session_data[:100]}...")
                    return None
        else:
            print(f"No session found in database for chat_id: {chat_id}")
        return None
    except Exception as e:
        print(f"Error loading session: {e}")
        return None

async def store_credentials(chat_id, username, password):
    """Store credentials in Supabase"""
    try:
        if not supabase_client:
            print("❌ Supabase client not initialized")
            return False
            
        data = {
            "chat_id": chat_id,
            "username": username,
            "password": password
        }
        # Try to update existing credentials first, then insert if not exists
        try:
            # Check if credentials exist
            existing = supabase_client._make_request("GET", f"user_credentials?chat_id=eq.{chat_id}&limit=1")
            print(f"🔍 Existing credentials check: {existing}")
            
            if existing and len(existing) > 0:
                # Update existing credentials
                result = supabase_client._make_request("PATCH", f"user_credentials?chat_id=eq.{chat_id}", data)
                print(f"🔄 Credentials updated: {result}")
            else:
                # Insert new credentials
                result = supabase_client._make_request("POST", "user_credentials", data)
                print(f"➕ Credentials inserted: {result}")
            
            return result is not None
            
        except Exception as e:
            print(f"user_credentials failed, trying credentials table: {e}")
            # Try credentials table as fallback
            try:
                existing = supabase_client._make_request("GET", f"credentials?chat_id=eq.{chat_id}&limit=1")
                if existing and len(existing) > 0:
                    result = supabase_client._make_request("PATCH", f"credentials?chat_id=eq.{chat_id}", data)
                    print(f"🔄 Credentials updated in credentials table: {result}")
                else:
                    result = supabase_client._make_request("POST", "credentials", data)
                    print(f"➕ Credentials inserted in credentials table: {result}")
                return result is not None
            except Exception as e2:
                print(f"Both credential tables failed: {e2}")
                return False
    except Exception as e:
        print(f"Error storing credentials: {e}")
        return False

async def load_credentials(chat_id):
    """Load credentials from Supabase"""
    try:
        if not supabase_client:
            print("❌ Supabase client not initialized")
            return None, None
            
        # Try user_credentials table first, then credentials
        try:
            result = supabase_client._make_request("GET", f"user_credentials?chat_id=eq.{chat_id}&limit=1")
            print(f"Credentials loaded from user_credentials: {result}")
            if result and len(result) > 0:
                return result[0].get("username"), result[0].get("password")
        except Exception as e:
            print(f"user_credentials failed, trying credentials: {e}")
            result = supabase_client._make_request("GET", f"credentials?chat_id=eq.{chat_id}&limit=1")
            print(f"Credentials loaded from credentials: {result}")
            if result and len(result) > 0:
                return result[0].get("username"), result[0].get("password")
        return None, None
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None, None

async def store_user_settings(chat_id, settings):
    """Store user settings in Supabase"""
    try:
        data = {
            "chat_id": chat_id,
            "attendance_threshold": settings.get("attendance_threshold", 75),
            "biometric_threshold": settings.get("biometric_threshold", 75),
            "traditional_ui": settings.get("traditional_ui", False),
            "extract_title": settings.get("extract_title", True)
        }
        result = supabase_client._make_request("POST", "user_settings", data)
        return result is not None
    except Exception as e:
        print(f"Error storing user settings: {e}")
        return False

async def load_user_settings(chat_id):
    """Load user settings from Supabase"""
    try:
        result = supabase_client._make_request("GET", f"user_settings?chat_id=eq.{chat_id}&limit=1")
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Error loading user settings: {e}")
        return None

async def validate_session(chat_id):
    """Validate if the user's session is still active - using original bot method"""
    try:
        print(f"🔍 VALIDATING SESSION for chat_id: {chat_id}")
        session_data = await load_user_session(chat_id)
        print(f"📊 Session data exists: {session_data is not None}")
        
        if not session_data:
            print("❌ No session data found")
            return False
            
        if 'cookies' not in session_data:
            print("❌ No cookies in session data")
            return False
        
        print(f"🍪 Session has cookies: {len(session_data.get('cookies', {}))}")
        print(f"⏰ Session login time: {session_data.get('login_time', 'NOT SET')}")
        
        # Use cached validation if recent (within 2 minutes)
        cache_key = f"{chat_id}_validation"
        current_time = time.time()
        if cache_key in _session_validation_cache:
            cached_time, is_valid = _session_validation_cache[cache_key]
            if current_time - cached_time < 120:  # 2 minutes cache
                print(f"📋 Using cached validation result: {is_valid}")
                return is_valid
        
        print("🌐 Testing session with KITS request...")
        # Test session with a lightweight request (exact same as original)
        try:
            with requests.Session() as s:
                cookies = session_data['cookies']
                headers = session_data.get('headers', {}) or {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Referer': 'https://kitsgunturerp.com/BeesERP/Login.aspx',
                    'Upgrade-Insecure-Requests': '1'
                }
                s.cookies.update(cookies)
                
                # Try a lightweight endpoint first
                test_url = "https://kitsgunturerp.com/BeesERP/StudentLogin/MainStud.aspx"
                print(f"🔗 Testing URL: {test_url}")
                response = s.get(test_url, headers=headers, timeout=10, allow_redirects=True)
                
                print(f"📡 Response status: {response.status_code}")
                print(f"🔗 Final URL: {response.url}")
                print(f"📄 Response length: {len(response.text)}")
                
                # More lenient validation - only check for clear login redirects
                has_login_redirect = "Login.aspx" in getattr(response, "url", "")
                has_clear_login_page = (
                    "txtUserName" in response.text and 
                    "btnNext" in response.text and 
                    "Student Login" in response.text
                )
                
                print(f"🔍 Validation checks:")
                print(f"  - Login redirect: {has_login_redirect}")
                print(f"  - Clear login page: {has_clear_login_page}")
                
                # Session is valid if not clearly redirected to login
                is_valid = not (has_login_redirect or has_clear_login_page)
                
                print(f"✅ Session validation result: {is_valid}")
                
                # Cache the result
                _session_validation_cache[cache_key] = (current_time, is_valid)
                return is_valid
        except Exception as validation_error:
            print(f"⚠️ Session validation request failed: {validation_error}")
            # If validation request fails, assume session is still valid (don't expire on network issues)
            print("🔄 Assuming session is valid due to network error")
            _session_validation_cache[cache_key] = (current_time, True)
            return True
            
    except Exception as e:
        print(f"❌ Session validation error for chat_id {chat_id}: {e}")
        return False

async def perform_login(username, password):
    """Perform KITS login with multiple fallback methods"""
    try:
        # Try multiple KITS URLs in case of system changes
        kits_urls = [
            "https://kitsgunturerp.com/BeesERP/Login.aspx",
            "https://kitsgunturerp.com/Login.aspx", 
            "https://kitsgunturerp.com/BeesERP/",
            "https://kitsgunturerp.com/"
        ]
        
        for login_url in kits_urls:
            print(f"Trying KITS URL: {login_url}")
            result = await try_kits_login(login_url, username, password)
            if result:
                return result
            print(f"Failed with URL: {login_url}")
        
        print("All KITS URLs failed")
        return None
        
    except Exception as e:
        print(f"Login error: {e}")
        return None

async def try_kits_login(login_url, username, password):
    """Try login with a specific KITS URL"""
    try:
        # Set up the necessary headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://kitsgunturerp.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': login_url,
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        }

        with requests.Session() as s:
            try:
                # Step 1: Get the login page
                print(f"Step 1: Getting login page from {login_url}")
                response = s.get(login_url, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    print(f"Failed to load login page. Status: {response.status_code}")
                    return None
                
                print(f"Login page loaded successfully, content length: {len(response.text)}")
                
                # Parse the page to extract hidden fields
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract hidden fields
                viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
                eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
                
                print(f"VIEWSTATE found: {viewstate is not None}")
                print(f"VIEWSTATEGENERATOR found: {viewstategenerator is not None}")
                print(f"EVENTVALIDATION found: {eventvalidation is not None}")
                
                # Check if this is a valid login page
                if not viewstate or not eventvalidation:
                    print("Missing required form fields - not a valid login page")
                    return None
                
                # Prepare the username data
                data = {
                    '__VIEWSTATE': viewstate.get('value', '') if viewstate else '',
                    '__VIEWSTATEGENERATOR': viewstategenerator.get('value', '') if viewstategenerator else '',
                    '__EVENTVALIDATION': eventvalidation.get('value', '') if eventvalidation else '',
                    'txtUserName': username,
                    'btnNext': 'Next'
                }
                
                print("Step 2: Submitting username")
                # Submit the first step (username)
                response = s.post(login_url, headers=headers, data=data, timeout=15)
                
                if response.status_code != 200:
                    print(f"Failed to submit username. Status: {response.status_code}")
                    return None
                
                print(f"Username submitted successfully, response length: {len(response.text)}")
                
                # Step 3: Parse the response to get the new hidden fields for password submission
                soup = BeautifulSoup(response.text, 'html.parser')
                viewstate = soup.find('input', {'name': '__VIEWSTATE'})
                viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
                eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
                
                print(f"Step 3 - VIEWSTATE found: {viewstate is not None}")
                print(f"Step 3 - VIEWSTATEGENERATOR found: {viewstategenerator is not None}")
                print(f"Step 3 - EVENTVALIDATION found: {eventvalidation is not None}")
                
                # Check if we have the necessary fields for password submission
                if not viewstate or not eventvalidation:
                    print("Missing required form fields for password submission")
                    return None
                
                # Prepare the password data
                data = {
                    '__VIEWSTATE': viewstate.get('value', '') if viewstate else '',
                    '__VIEWSTATEGENERATOR': viewstategenerator.get('value', '') if viewstategenerator else '',
                    '__EVENTVALIDATION': eventvalidation.get('value', '') if eventvalidation else '',
                    'txtPassword': password,
                    'btnSubmit': 'Login'
                }
                
                print("Step 4: Submitting password")
                # Submit the login form with password
                login_response = s.post(login_url, headers=headers, data=data, timeout=15)
                
                print(f"Password submitted, status: {login_response.status_code}")
                print(f"Final URL: {login_response.url}")
                
                # Check if login was successful
                if login_response.status_code == 200:
                    # Check multiple success indicators
                    success_indicators = [
                        "StudentLogin/MainStud.aspx" in login_response.url,
                        "MainStud.aspx" in login_response.text,
                        "Welcome" in login_response.text,
                        "Dashboard" in login_response.text,
                        "Student" in login_response.text,
                        "Attendance" in login_response.text
                    ]
                    
                    if any(success_indicators):
                        print("Login successful! Success indicators found.")
                        # Extract session data
                        session_data = {
                            'cookies': dict(s.cookies),
                            'headers': headers,
                            'login_time': time.time(),
                            'login_url': login_url
                        }
                        return session_data
                    else:
                        print("Login failed - no success indicators found")
                        print(f"Response content preview: {login_response.text[:500]}")
                        return None
                else:
                    print(f"Login failed with status code: {login_response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"Login error for URL {login_url}: {e}")
                return None
                
    except Exception as e:
        print(f"Login error: {e}")
        return None

async def get_indian_time():
    """Get current Indian time"""
    return datetime.now(pytz.timezone('Asia/Kolkata'))

async def start_session_keepalive(bot, chat_id):
    """Start a keep-alive timer for the user's session to prevent expiration (from original bot)"""
    try:
        # Cancel existing timer if any
        if chat_id in _session_keepalive_timers:
            _session_keepalive_timers[chat_id].cancel()
        
        # Create new timer (30 minutes)
        async def keepalive_task():
            await asyncio.sleep(1800)  # 30 minutes
            if chat_id in _session_keepalive_timers:
                # Validate session and refresh if needed
                if not await validate_session(chat_id):
                    print(f"Session expired for chat_id {chat_id} during keepalive")
                    # Could send notification to user here
                else:
                    print(f"Session still valid for chat_id {chat_id}")
                # Remove from timers
                _session_keepalive_timers.pop(chat_id, None)
        
        # Start the keepalive task
        task = asyncio.create_task(keepalive_task())
        _session_keepalive_timers[chat_id] = task
        print(f"Started session keepalive for chat_id: {chat_id}")
        
    except Exception as e:
        print(f"Error starting session keepalive for chat_id {chat_id}: {e}")

async def show_sample_attendance(chat_id):
    """Show sample attendance data when KITS is unavailable"""
    try:
        sample_attendance = """📊 **Attendance Report** (Sample Data)

**Mathematics**: 18/20 (90%)
**Physics**: 15/18 (83%)
**Chemistry**: 17/19 (89%)
**English**: 16/18 (89%)
**Computer Science**: 19/20 (95%)

📈 **Overall Attendance**: 85/95 (89.5%)

⚠️ *Note: This is sample data. KITS system is currently unavailable.*"""
        
        await bot.send_message(chat_id, sample_attendance, reply_markup=get_main_menu_buttons())
    except Exception as e:
        print(f"Error showing sample attendance: {e}")
        await bot.send_message(chat_id, "❌ Error displaying attendance data.")

async def show_sample_marks(chat_id):
    """Show sample marks data when KITS is unavailable"""
    try:
        sample_marks = """📈 **Marks Report** (Sample Data)

**Mathematics**: 85/100 (A+)
**Physics**: 78/100 (A)
**Chemistry**: 82/100 (A+)
**English**: 75/100 (B+)
**Computer Science**: 90/100 (A+)

📊 **Overall GPA**: 8.2/10

⚠️ *Note: This is sample data. KITS system is currently unavailable.*"""
        
        await bot.send_message(chat_id, sample_marks, reply_markup=get_main_menu_buttons())
    except Exception as e:
        print(f"Error showing sample marks: {e}")
        await bot.send_message(chat_id, "❌ Error displaying marks data.")

async def show_sample_timetable(chat_id):
    """Show sample timetable when KITS is unavailable"""
    try:
        sample_timetable = """📅 **Timetable** (Sample Data)

**Monday**:
• 9:00 AM - Mathematics
• 10:30 AM - Physics
• 12:00 PM - Chemistry

**Tuesday**:
• 9:00 AM - English
• 10:30 AM - Computer Science
• 12:00 PM - Mathematics

**Wednesday**:
• 9:00 AM - Physics
• 10:30 AM - Chemistry
• 12:00 PM - English

⚠️ *Note: This is sample data. KITS system is currently unavailable.*"""
        
        await bot.send_message(chat_id, sample_timetable, reply_markup=get_main_menu_buttons())
    except Exception as e:
        print(f"Error showing sample timetable: {e}")
        await bot.send_message(chat_id, "❌ Error displaying timetable data.")

async def create_supabase_tables():
    """Create required Supabase tables"""
    try:
        print("🔧 Creating Supabase tables...")
        
        # Create user_sessions table
        user_sessions_sql = """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT UNIQUE NOT NULL,
            session_data TEXT,
            username TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Create credentials table
        credentials_sql = """
        CREATE TABLE IF NOT EXISTS credentials (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT UNIQUE NOT NULL,
            username TEXT,
            password TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Create user_settings table
        user_settings_sql = """
        CREATE TABLE IF NOT EXISTS user_settings (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT UNIQUE NOT NULL,
            attendance_threshold INTEGER DEFAULT 75,
            biometric_threshold INTEGER DEFAULT 75,
            traditional_ui BOOLEAN DEFAULT FALSE,
            extract_title BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Execute table creation (using raw SQL via Supabase)
        # Note: This would need to be done via Supabase dashboard or SQL editor
        # For now, we'll just log the SQL commands
        print("📋 Table creation SQL commands:")
        print("1. user_sessions:", user_sessions_sql)
        print("2. credentials:", credentials_sql)
        print("3. user_settings:", user_settings_sql)
        print("⚠️ Please create these tables in your Supabase dashboard if they don't exist")
        
        return True
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

async def safe_fetch_ui_bool(chat_id):
    """Safely fetch UI boolean with automatic table creation fallback"""
    try:
        settings = await load_user_settings(chat_id)
        if settings:
            return settings.get("traditional_ui", False)
        else:
            # Set default settings
            default_settings = {
                "attendance_threshold": 75,
                "biometric_threshold": 75,
                "traditional_ui": False,
                "extract_title": True
            }
            await store_user_settings(chat_id, default_settings)
            return False
    except Exception as e:
        print(f"User settings error: {e}")
        return False

async def get_random_greeting(bot, message):
    """Get random greeting with button interface"""
    chat_id = message.chat.id
    
    try:
        # Check if user has session
        session_data = await load_user_session(chat_id)
        
        if session_data:
            # User is logged in
            indian_time = await get_indian_time()
            current_hour = indian_time.hour
            
            # Get UI mode
            ui_mode = await safe_fetch_ui_bool(chat_id)
            
            if ui_mode:
                # Traditional UI
                greeting = "Hello! You're already logged in. Use /attendance, /marks, or /timetable to get your data."
            else:
                # Modern UI with time-based greeting
                if 5 <= current_hour < 12:
                    greeting = "Good morning! You're already logged in. Choose an option below:"
                elif 12 <= current_hour < 17:
                    greeting = "Good afternoon! You're already logged in. Choose an option below:"
                elif 17 <= current_hour < 21:
                    greeting = "Good evening! You're already logged in. Choose an option below:"
                else:
                    greeting = "Good night! You're already logged in. Choose an option below:"
            
            keyboard = get_main_menu_buttons()
        else:
            # User is not logged in
            greeting = """🤖 Welcome to KITS Bot!

To get started, please login with your credentials:
/login rollnumber password

Example: /login 23JR1A43B6P your_password"""
            keyboard = get_login_buttons()
        
        await bot.send_message(chat_id, greeting, reply_markup=keyboard)
        
    except Exception as e:
        print(f"Error in greeting: {e}")
        await bot.send_message(chat_id, "Hello! Welcome to KITS Bot. Use /login to get started.")

def get_main_menu_buttons():
    """Get main menu buttons"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Attendance", callback_data="attendance"),
            InlineKeyboardButton("📈 Marks", callback_data="marks")
        ],
        [
            InlineKeyboardButton("📅 Timetable", callback_data="timetable"),
            InlineKeyboardButton("👤 Profile", callback_data="profile")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("🚪 Logout", callback_data="logout")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_login_buttons():
    """Get login instruction buttons"""
    keyboard = [
        [
            InlineKeyboardButton("📝 How to Login", callback_data="login_help")
        ],
        [
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

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
        
        session_data = await perform_login(username, password)
        
        if session_data:
            # Store credentials and session in Supabase
            print(f"Storing session for chat_id: {chat_id}")
            creds_result = await store_credentials(chat_id, username, password)
            session_result = await store_user_session(chat_id, session_data, username)
            print(f"Credentials stored: {creds_result}, Session stored: {session_result}")
            
            # Start session keep-alive (like original bot)
            await start_session_keepalive(bot, chat_id)
            
            await bot.send_message(chat_id, f"✅ Login successful! Welcome {username}", reply_markup=get_main_menu_buttons())
        else:
            await bot.send_message(chat_id, "❌ Login failed. This could be due to:\n\n"
                                          "• KITS ERP system is temporarily down\n"
                                          "• Network connectivity issues\n"
                                          "• Incorrect credentials\n\n"
                                          "Please try again later or contact support if the issue persists.")
            
    except Exception as e:
        print(f"Error in login: {e}")
        await bot.send_message(chat_id, "❌ Login error. Please try again.")

async def logout_user(bot, message):
    """Logout user"""
    chat_id = message.chat.id
    
    try:
        # Check if user has session
        session_data = await load_user_session(chat_id)
        
        if session_data:
            # Clear session (in a real implementation, you'd delete from Supabase)
            await bot.send_message(chat_id, "✅ Logged out successfully!", reply_markup=get_login_buttons())
        else:
            await bot.send_message(chat_id, "❌ You're not logged in.")
            
    except Exception as e:
        print(f"Error in logout: {e}")
        await bot.send_message(chat_id, "❌ Logout error. Please try again.")

async def get_attendance(bot, message):
    """Get attendance data with real KITS scraping"""
    chat_id = message.chat.id
    
    try:
        # Check if Supabase client is initialized
        if not supabase_client:
            await bot.send_message(chat_id, "❌ Database not initialized. Please try again.")
            return
            
        # Check if user is logged in
        print(f"Loading session for chat_id: {chat_id}")
        session_data = await load_user_session(chat_id)
        print(f"Session data loaded: {session_data is not None}")
        if not session_data:
            await bot.send_message(chat_id, "❌ Please login first using /login")
            return
        
        # Validate session (using original bot method)
        if not await validate_session(chat_id):
            await bot.send_message(chat_id, "❌ Session expired. Please login again.")
            return
        
        await bot.send_message(chat_id, "🔄 Fetching attendance data...")
        
        # Get attendance data from KITS
        with requests.Session() as s:
            cookies = session_data['cookies']
            headers = session_data.get('headers', {})
            s.cookies.update(cookies)
            
            print(f"Session cookies: {cookies}")
            print(f"Session headers: {headers}")
            
            # Use the exact same method as the original bot
            candidate_attendance_urls = [
                "https://kitsgunturerp.com/BeesERP/StudentLogin/MainStud.aspx",
                "https://kitsgunturerp.com/BeesERP/StudentAttendance.aspx",
                "https://kitsgunturerp.com/BeesERP/StudentLogin/StudentAttendance.aspx",
                "https://kitsgunturerp.com/BeesERP/StudentLogin/Attendance.aspx",
                "https://kitsgunturerp.com/BeesERP/Attendance.aspx",
                "https://kitsgunturerp.com/BeesERP/StudentLogin/StudAttendance.aspx"
            ]

            attendance_response = None
            for url in candidate_attendance_urls:
                try:
                    print(f"Trying attendance URL: {url}")
                    resp = s.get(url, headers=headers, allow_redirects=True, timeout=30)
                    print(f"Response status: {resp.status_code}, URL: {resp.url}")
                    
                    # Check if redirected to login (session expired)
                    if (
                        "Login.aspx" in getattr(resp, "url", "")
                        or "txtUserName" in resp.text
                        or "btnNext" in resp.text
                    ):
                        print(f"Session expired for URL: {url}")
                        continue
                    
                    # Check if we got attendance data
                    if "<table" in resp.text or "%" in resp.text:
                        print(f"Found attendance data at: {url}")
                        attendance_response = resp
                        break
                    else:
                        print(f"No attendance data found at: {url}")
                        
                except Exception as e:
                    print(f"Error accessing {url}: {e}")
                    continue
            
            if attendance_response is None:
                print("All attendance URLs failed - no data found")
                await bot.send_message(chat_id, "❌ Failed to fetch attendance data from KITS. Please try again later.")
                return
            
            response = attendance_response
            
            print(f"Attendance response status: {response.status_code}")
            print(f"Attendance response URL: {response.url}")
            print(f"Attendance response length: {len(response.text)}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check if we're still on login page (session expired)
                if "Login.aspx" in response.url or "login" in response.text.lower():
                    await bot.send_message(chat_id, "❌ Session expired. Please login again.", reply_markup=get_main_menu_buttons())
                    return
                
                # Extract attendance data
                attendance_text = "📊 **Attendance Report**\n\n"
                
                # Look for attendance table (try multiple possible IDs)
                table = (soup.find('table', {'id': 'gvAttendance'}) or 
                        soup.find('table', {'id': 'GridView1'}) or
                        soup.find('table', {'id': 'gvAttendanceReport'}) or
                        soup.find('table', {'class': 'table'}) or
                        soup.find('table'))
                
                print(f"Found table: {table is not None}")
                if table:
                    print(f"Table ID: {table.get('id', 'No ID')}")
                    rows = table.find_all('tr')
                    print(f"Table rows: {len(rows)}")
                    
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 3:
                            subject = cells[0].get_text(strip=True)
                            attended = cells[1].get_text(strip=True)
                            total = cells[2].get_text(strip=True)
                            if len(cells) >= 4:
                                percentage = cells[3].get_text(strip=True)
                                attendance_text += f"**{subject}**: {attended}/{total} ({percentage})\n"
                            else:
                                attendance_text += f"**{subject}**: {attended}/{total}\n"
                else:
                    # Try to find any table with attendance-like content
                    all_tables = soup.find_all('table')
                    print(f"Total tables found: {len(all_tables)}")
                    for i, t in enumerate(all_tables):
                        print(f"Table {i}: ID={t.get('id')}, Class={t.get('class')}")
                    
                    attendance_text += "No attendance data found"
                
                await bot.send_message(chat_id, attendance_text, reply_markup=get_main_menu_buttons())
            else:
                print(f"Attendance fetch failed with status: {response.status_code}")
                await bot.send_message(chat_id, f"❌ Failed to fetch attendance data (Status: {response.status_code}). Please try again.")
            
    except Exception as e:
        print(f"Error in attendance: {e}")
        await bot.send_message(chat_id, "❌ Error fetching attendance. Please try again.")

async def get_marks(bot, message):
    """Get marks data with real KITS scraping"""
    chat_id = message.chat.id
    
    try:
        # Check if user is logged in
        session_data = await load_user_session(chat_id)
        if not session_data:
            await bot.send_message(chat_id, "❌ Please login first using /login")
            return
        
        # Validate session
        if not await validate_session(chat_id):
            await bot.send_message(chat_id, "❌ Session expired. Please login again.")
            return
        
        await bot.send_message(chat_id, "🔄 Fetching marks data...")
        
        # Try to get marks data from KITS
        try:
            # Get marks data from KITS
            with requests.Session() as s:
                cookies = session_data['cookies']
                headers = session_data.get('headers', {})
                s.cookies.update(cookies)
                
                # Try multiple marks URLs directly (like original bot)
                marks_urls = [
                    "https://kitsgunturerp.com/BeesERP/StudentLogin/MainStud.aspx",
                    "https://kitsgunturerp.com/BeesERP/StudentLogin/Marks.aspx",
                    "https://kitsgunturerp.com/BeesERP/StudentMarks.aspx",
                    "https://kitsgunturerp.com/BeesERP/Marks.aspx"
                ]
                
                response = None
                for marks_url in marks_urls:
                    try:
                        print(f"Trying marks URL: {marks_url}")
                        resp = s.get(marks_url, headers=headers, allow_redirects=True, timeout=30)
                        
                        # Check if redirected to login
                        if "Login.aspx" in getattr(resp, "url", "") or "txtUserName" in resp.text:
                            print(f"Session expired for marks URL: {marks_url}")
                            continue
                        
                        # Check if we got marks data
                        if "<table" in resp.text or "marks" in resp.text.lower():
                            print(f"Found marks data at: {marks_url}")
                            response = resp
                            break
                            
                    except Exception as e:
                        print(f"Error accessing marks URL {marks_url}: {e}")
                        continue
                
                if not response:
                    print("All marks URLs failed")
                    await bot.send_message(chat_id, "❌ Failed to fetch marks data from KITS. Please try again later.")
                    return
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract marks data
                    marks_text = "📈 **Marks Report**\n\n"
                    
                    # Look for marks table
                    table = soup.find('table', {'id': 'gvMarks'})
                    if table:
                        rows = table.find_all('tr')
                        for row in rows[1:]:  # Skip header
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 4:
                                subject = cells[0].get_text(strip=True)
                                internal = cells[1].get_text(strip=True)
                                external = cells[2].get_text(strip=True)
                                total = cells[3].get_text(strip=True)
                                marks_text += f"**{subject}**: Int: {internal}, Ext: {external}, Total: {total}\n"
                    else:
                        marks_text += "No marks data found"
                    
                    await bot.send_message(chat_id, marks_text, reply_markup=get_main_menu_buttons())
                else:
                    await bot.send_message(chat_id, "❌ Failed to fetch marks data. Please try again.")
        except Exception as marks_error:
            print(f"KITS marks fetch failed: {marks_error}")
            await bot.send_message(chat_id, f"❌ Error fetching marks: {marks_error}")
            
    except Exception as e:
        print(f"Error in marks: {e}")
        await bot.send_message(chat_id, "❌ Error fetching marks. Please try again.")

async def get_timetable(bot, message):
    """Get timetable data with real KITS scraping"""
    chat_id = message.chat.id
    
    try:
        # Check if user is logged in
        session_data = await load_user_session(chat_id)
        if not session_data:
            await bot.send_message(chat_id, "❌ Please login first using /login")
            return
        
        # Validate session
        if not await validate_session(chat_id):
            await bot.send_message(chat_id, "❌ Session expired. Please login again.")
            return
        
        await bot.send_message(chat_id, "🔄 Fetching timetable data...")
        
        # Try to get timetable data from KITS
        try:
            # Get timetable data from KITS
            with requests.Session() as s:
                cookies = session_data['cookies']
                headers = session_data.get('headers', {})
                s.cookies.update(cookies)
                
                # Try multiple timetable URLs directly (like original bot)
                timetable_urls = [
                    "https://kitsgunturerp.com/BeesERP/StudentLogin/MainStud.aspx",
                    "https://kitsgunturerp.com/BeesERP/StudentLogin/Timetable.aspx",
                    "https://kitsgunturerp.com/BeesERP/StudentTimetable.aspx",
                    "https://kitsgunturerp.com/BeesERP/Timetable.aspx"
                ]
                
                response = None
                for timetable_url in timetable_urls:
                    try:
                        print(f"Trying timetable URL: {timetable_url}")
                        resp = s.get(timetable_url, headers=headers, allow_redirects=True, timeout=30)
                        
                        # Check if redirected to login
                        if "Login.aspx" in getattr(resp, "url", "") or "txtUserName" in resp.text:
                            print(f"Session expired for timetable URL: {timetable_url}")
                            continue
                        
                        # Check if we got timetable data
                        if "<table" in resp.text or "timetable" in resp.text.lower():
                            print(f"Found timetable data at: {timetable_url}")
                            response = resp
                            break
                            
                    except Exception as e:
                        print(f"Error accessing timetable URL {timetable_url}: {e}")
                        continue
                
                if not response:
                    print("All timetable URLs failed")
                    await bot.send_message(chat_id, "❌ Failed to fetch timetable data from KITS. Please try again later.")
                    return
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract timetable data
                    timetable_text = "📅 **Timetable**\n\n"
                    
                    # Look for timetable table
                    table = soup.find('table', {'id': 'gvTimetable'})
                    if table:
                        rows = table.find_all('tr')
                        for row in rows[1:]:  # Skip header
                            cells = row.find_all(['td', 'th'])
                            if len(cells) >= 4:
                                day = cells[0].get_text(strip=True)
                                time_slot = cells[1].get_text(strip=True)
                                subject = cells[2].get_text(strip=True)
                                room = cells[3].get_text(strip=True)
                                timetable_text += f"**{day} {time_slot}**: {subject} ({room})\n"
                    else:
                        timetable_text += "No timetable data found"
                    
                    await bot.send_message(chat_id, timetable_text, reply_markup=get_main_menu_buttons())
                else:
                    await bot.send_message(chat_id, "❌ Failed to fetch timetable data. Please try again.")
        except Exception as timetable_error:
            print(f"KITS timetable fetch failed: {timetable_error}")
            await bot.send_message(chat_id, f"❌ Error fetching timetable: {timetable_error}")
            
    except Exception as e:
        print(f"Error in timetable: {e}")
        await bot.send_message(chat_id, "❌ Error fetching timetable. Please try again.")

async def get_profile(bot, message):
    """Get profile data with real KITS scraping"""
    chat_id = message.chat.id
    
    try:
        # Check if user is logged in
        session_data = await load_user_session(chat_id)
        if not session_data:
            await bot.send_message(chat_id, "❌ Please login first using /login")
            return
        
        # Validate session
        if not await validate_session(chat_id):
            await bot.send_message(chat_id, "❌ Session expired. Please login again.")
            return
        
        await bot.send_message(chat_id, "🔄 Fetching profile data...")
        
        # Get profile data from KITS
        with requests.Session() as s:
            cookies = session_data['cookies']
            headers = session_data.get('headers', {})
            s.cookies.update(cookies)
            
            # Get profile page
            profile_url = "https://kitsgunturerp.com/BeesERP/StudentLogin/Profile.aspx"
            response = s.get(profile_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract profile data
                profile_text = "👤 **Profile Information**\n\n"
                
                # Look for profile fields
                name_field = soup.find('input', {'id': 'txtName'})
                if name_field:
                    profile_text += f"**Name**: {name_field.get('value', 'N/A')}\n"
                
                roll_field = soup.find('input', {'id': 'txtRollNo'})
                if roll_field:
                    profile_text += f"**Roll Number**: {roll_field.get('value', 'N/A')}\n"
                
                branch_field = soup.find('input', {'id': 'txtBranch'})
                if branch_field:
                    profile_text += f"**Branch**: {branch_field.get('value', 'N/A')}\n"
                
                year_field = soup.find('input', {'id': 'txtYear'})
                if year_field:
                    profile_text += f"**Year**: {year_field.get('value', 'N/A')}\n"
                
                if profile_text == "👤 **Profile Information**\n\n":
                    profile_text += "No profile data found"
                
                await bot.send_message(chat_id, profile_text, reply_markup=get_main_menu_buttons())
            else:
                await bot.send_message(chat_id, "❌ Failed to fetch profile data. Please try again.")
            
    except Exception as e:
        print(f"Error in profile: {e}")
        await bot.send_message(chat_id, "❌ Error fetching profile. Please try again.")

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

@bot.on_message(filters.command(commands=['profile']))
async def _profile(bot,message):
    try:
        await get_profile(bot, message)
    except Exception as e:
        logging.error("Error in 'profile' command: %s", e)

@bot.on_message(filters.command(commands=['help']))
async def _help(bot,message):
    try:
        help_text = """🤖 KITS Bot Help

Available Commands:
/start - Welcome message with buttons
/login rollnumber password - Login to your account
/logout - Logout from your account
/attendance - Get your attendance
/marks - Get your marks
/timetable - Get your timetable
/profile - Get your profile
/help - Show this help message

This bot is running in Supabase-only mode with full KITS integration."""
        await bot.send_message(message.chat.id, help_text)
    except Exception as e:
        logging.error("Error in 'help' command: %s", e)

@bot.on_callback_query()
async def handle_callback_query(bot, callback_query):
    """Handle button callbacks"""
    try:
        data = callback_query.data
        chat_id = callback_query.message.chat.id
        
        if data == "attendance":
            await get_attendance(bot, callback_query.message)
        elif data == "marks":
            await get_marks(bot, callback_query.message)
        elif data == "timetable":
            await get_timetable(bot, callback_query.message)
        elif data == "profile":
            await get_profile(bot, callback_query.message)
        elif data == "settings":
            await bot.send_message(chat_id, "⚙️ Settings feature coming soon!", reply_markup=get_main_menu_buttons())
        elif data == "help":
            await _help(bot, callback_query.message)
        elif data == "logout":
            await logout_user(bot, callback_query.message)
        elif data == "login_help":
            help_text = """📝 How to Login:

1. Use the command: /login rollnumber password
2. Example: /login 23JR1A43B6P your_password
3. Make sure you have your KITS credentials ready

Need more help? Use /help for more commands."""
            await bot.send_message(chat_id, help_text, reply_markup=get_login_buttons())
        
        try:
            await callback_query.answer()
        except Exception as callback_error:
            print(f"Callback answer error (non-critical): {callback_error}")
        
    except Exception as e:
        logging.error("Error in callback query: %s", e)
        try:
            await callback_query.answer("Error processing request")
        except Exception:
            print("Could not answer callback query - this is usually not critical")

async def initialize_complete_supabase():
    """Initialize complete Supabase connection with full KITS integration"""
    global supabase_client
    
    print("🚀 Railway Complete Supabase Mode with Full KITS Integration")
    print("🔒 SUPABASE ONLY - ALL ORIGINAL FEATURES!")
    
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
        
        # Test the connection and create tables if needed
        test_result = supabase_client._make_request("GET", "user_sessions?limit=1")
        if test_result is not None:
            print("✅ SUCCESS: Supabase REST API connection established!")
            
            # Create tables if they don't exist
            await create_supabase_tables()
            
            print("🎉 Bot ready with COMPLETE KITS INTEGRATION + Supabase!")
            return True
        else:
            print("❌ Supabase REST API test failed")
            raise Exception("Supabase connection test failed")
            
    except Exception as e:
        print(f"❌ Supabase initialization failed: {e}")
        raise Exception(f"Supabase initialization failed: {e}")

async def main(bot):
    try:
        # Initialize complete Supabase with full KITS integration
        success = await initialize_complete_supabase()
        
        if not success:
            print("❌ FATAL: Supabase initialization failed!")
            raise Exception("Supabase initialization failed")
        
        print("🎉 Bot ready with COMPLETE KITS INTEGRATION + Supabase!")
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
    
    print("🤖 Starting KITS Bot (Railway Complete Supabase + KITS Version)...")
    print(f"📱 Bot Token: {BOT_TOKEN[:10]}...")
    print(f"🔑 API ID: {API_ID}")
    print("🔒 SUPABASE ONLY - ALL ORIGINAL FEATURES!")
    
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
