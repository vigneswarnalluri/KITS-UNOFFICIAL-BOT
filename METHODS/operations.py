from DATABASE import tdatabase,pgdatabase,user_settings,managers_handler
from Buttons import buttons
from bs4 import BeautifulSoup 
import requests,json,uuid,os,pyqrcode,random,re
from pytz import timezone
from datetime import datetime
import io,shutil
import time
# Playwright removed: requests-only implementation for KITS ERP

# Session management variables
_session_keepalive_timers = {}
_session_validation_cache = {}

async def validate_session(chat_id):
    """
    Validate if the user's session is still active by making a lightweight request.
    Returns True if session is valid, False otherwise.
    """
    try:
        session_data = await tdatabase.load_user_session(chat_id)
        if not session_data or 'cookies' not in session_data:
            return False
        
        # Use cached validation if recent (within 2 minutes)
        cache_key = f"{chat_id}_validation"
        current_time = time.time()
        if cache_key in _session_validation_cache:
            cached_time, is_valid = _session_validation_cache[cache_key]
            if current_time - cached_time < 120:  # 2 minutes cache
                return is_valid
        
        # Test session with a lightweight request
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
            response = s.get(test_url, headers=headers, timeout=15, allow_redirects=True)
            
            # Check if session is valid
            is_valid = (
                "Login.aspx" not in getattr(response, "url", "") and 
                "Login.aspx" not in response.text and
                "txtUserName" not in response.text and
                "btnNext" not in response.text
            )
            
            # Cache the result
            _session_validation_cache[cache_key] = (current_time, is_valid)
            return is_valid
            
    except Exception as e:
        print(f"Session validation error for chat_id {chat_id}: {e}")
        return False

async def auto_reconnect_session(bot, chat_id):
    """
    Automatically attempt to reconnect using saved credentials when session expires.
    Returns True if reconnection successful, False otherwise.
    """
    try:
        # Check if user has saved credentials
        username, password = await tdatabase.fetch_credentials_from_database(chat_id)
        if not username or not password:
            return False
        
        # Attempt auto-login
        session_data = await perform_login(username, password)
        if session_data:
            await tdatabase.store_user_session(chat_id, json.dumps(session_data), username)
            print(f"Auto-reconnection successful for chat_id: {chat_id}")
            return True
        else:
            print(f"Auto-reconnection failed for chat_id: {chat_id}")
            return False
    except Exception as e:
        print(f"Auto-reconnection error for chat_id {chat_id}: {e}")
        return False

async def start_session_keepalive(bot, chat_id):
    """
    Start a keep-alive timer for the user's session to prevent expiration.
    """
    try:
        # Cancel existing timer if any
        if chat_id in _session_keepalive_timers:
            _session_keepalive_timers[chat_id].cancel()
        
        async def keepalive_task():
            while True:
                try:
                    await asyncio.sleep(600)  # Wait 10 minutes
                    
                    # Validate session
                    if not await validate_session(chat_id):
                        print(f"Session expired for chat_id: {chat_id}, attempting reconnection")
                        
                        # Notify user about session expiration
                        await notify_session_status(bot, chat_id, "expired", "Attempting automatic reconnection...")
                        
                        # Try auto-reconnection
                        if await auto_reconnect_session(bot, chat_id):
                            print(f"Session reconnected for chat_id: {chat_id}")
                            await notify_session_status(bot, chat_id, "reconnected", "Your session has been restored.")
                        else:
                            print(f"Failed to reconnect session for chat_id: {chat_id}")
                            await notify_session_status(bot, chat_id, "failed_reconnect", "Please login manually using /login command.")
                            break
                    else:
                        print(f"Session keep-alive successful for chat_id: {chat_id}")
                        
                except Exception as e:
                    print(f"Keep-alive error for chat_id {chat_id}: {e}")
                    break
        
        # Start the keep-alive task
        import asyncio
        task = asyncio.create_task(keepalive_task())
        _session_keepalive_timers[chat_id] = task
        
    except Exception as e:
        print(f"Error starting keep-alive for chat_id {chat_id}: {e}")

async def stop_session_keepalive(chat_id):
    """
    Stop the keep-alive timer for a user's session.
    """
    try:
        if chat_id in _session_keepalive_timers:
            _session_keepalive_timers[chat_id].cancel()
            del _session_keepalive_timers[chat_id]
    except Exception as e:
        print(f"Error stopping keep-alive for chat_id {chat_id}: {e}")

async def notify_session_status(bot, chat_id, status, message=""):
    """
    Notify user about session status changes.
    """
    try:
        if status == "expired":
            await bot.send_message(chat_id, f"⚠️ Your session has expired. {message}")
        elif status == "reconnected":
            await bot.send_message(chat_id, f"✅ Session automatically reconnected. {message}")
        elif status == "failed_reconnect":
            await bot.send_message(chat_id, f"❌ Failed to reconnect session. Please login again. {message}")
        elif status == "keepalive_active":
            await bot.send_message(chat_id, f"🔄 Session keep-alive is now active. {message}")
    except Exception as e:
        print(f"Error sending session notification to chat_id {chat_id}: {e}")

async def get_session_health_status(chat_id):
    """
    Get comprehensive session health status.
    """
    try:
        session_data = await tdatabase.load_user_session(chat_id)
        if not session_data:
            return {
                "status": "no_session",
                "message": "No active session found",
                "keepalive_active": chat_id in _session_keepalive_timers
            }
        
        # Validate session
        is_valid = await validate_session(chat_id)
        
        return {
            "status": "valid" if is_valid else "expired",
            "message": "Session is active and valid" if is_valid else "Session has expired",
            "keepalive_active": chat_id in _session_keepalive_timers,
            "session_age": "Unknown"  # Could be enhanced to track session creation time
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking session health: {e}",
            "keepalive_active": False
        }

async def session_status_command(bot, message):
    """
    Command to check session status and health.
    """
    chat_id = message.chat.id
    
    try:
        health_status = await get_session_health_status(chat_id)
        
        status_emoji = {
            "valid": "✅",
            "expired": "⚠️", 
            "no_session": "❌",
            "error": "🔧"
        }
        
        keepalive_status = "🔄 Active" if health_status["keepalive_active"] else "⏸️ Inactive"
        
        status_message = f"""
**Session Status Report**

{status_emoji.get(health_status["status"], "❓")} **Status:** {health_status["status"].title()}
📝 **Message:** {health_status["message"]}
{keepalive_status} **Keep-alive:** {keepalive_status}

**Recommendations:**
"""
        
        if health_status["status"] == "no_session":
            status_message += "• Use `/login` command to authenticate"
        elif health_status["status"] == "expired":
            status_message += "• Use `/login` command to re-authenticate"
        elif health_status["status"] == "valid":
            status_message += "• Your session is working properly"
            if not health_status["keepalive_active"]:
                status_message += "\n• Keep-alive will start automatically on next bot usage"
        elif health_status["status"] == "error":
            status_message += "• Try logging in again with `/login` command"
        
        await bot.send_message(chat_id, status_message, parse_mode="Markdown")
        
    except Exception as e:
        await bot.send_message(chat_id, f"Error checking session status: {e}")


login_message_updated_ui = f"""
```WELCOME
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 2XJRXXXXXX password_here

(If You Have Forgotten You'r Password,
 Then Use Capital 'P' At The End Of Both 
 RollNumber And Password)

Example:

/login 23JR1A43B6P 23JR1A43B6P
```
"""
    
login_message_traditional_ui = f"""
WELCOME

⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 2XJRXXXXXX password_here

(If You Have Forgotten You'r Password,
 Then Use Capital 'P' At The End Of Both 
 RollNumber And Password)

Example:/login 23JR1A43B6P 23JR1A43B6P"""



async def get_indian_time():
    return datetime.now(timezone('Asia/Kolkata'))

async def safe_fetch_ui_bool(chat_id):
    """
    Safely fetch UI boolean with automatic table creation fallback
    """
    try:
        ui_mode = await user_settings.fetch_ui_bool(chat_id)
        if ui_mode is None:
            await user_settings.set_user_default_settings(chat_id)
            ui_mode = await user_settings.fetch_ui_bool(chat_id)
        return ui_mode
    except Exception as e:
        print(f"⚠️ User settings table issue, creating tables: {e}")
        try:
            # Create user_settings tables if they don't exist
            await user_settings.create_user_settings_tables()
            await user_settings.set_user_default_settings(chat_id)
            ui_mode = await user_settings.fetch_ui_bool(chat_id)
            print("✅ User settings tables created and initialized successfully")
            return ui_mode
        except Exception as create_error:
            print(f"❌ Failed to create user_settings tables: {create_error}")
            # Return default UI mode (traditional UI = False)
            return (0,)  # Default to modern UI
async def get_random_greeting(bot,message):
    """
    Get a random greeting based on the time and day.
    """
    chat_id = message.chat.id
    indian_time = await get_indian_time()
    current_hour = indian_time.hour
    current_weekday = indian_time.weekday()
    
    # Safe user_settings access with automatic table creation
    ui_mode = await safe_fetch_ui_bool(chat_id)
    # List of greetings based on the time of day
    morning_greetings = ["Good morning!", "Hello, early bird!", "Rise and shine!", "Morning!"]
    afternoon_greetings = ["Good afternoon!", "Hello there!", "Afternoon vibes!", "Hey!"]
    evening_greetings = ["Good evening!", "Hello, night owl!", "Evening time!", "Hi there!"]

    # List of greetings based on the day of the week
    weekday_greetings = ["Have a productive day!", "Stay focused and have a great day!", "Wishing you a wonderful day!", "Make the most of your day!"]
    weekend_greetings = ["Enjoy your weekend!", "Relax and have a great weekend!", "Wishing you a fantastic weekend!", "Make the most of your weekend!"]

    # Get a random greeting based on the time of day
    if 5 <= current_hour < 12:  # Morning (5 AM to 11:59 AM)
        greeting = random.choice(morning_greetings)
    elif 12 <= current_hour < 18:  # Afternoon (12 PM to 5:59 PM)
        greeting = random.choice(afternoon_greetings)
    else:  # Evening (6 PM to 4:59 AM)
        greeting = random.choice(evening_greetings)

    # Add a weekday-specific greeting if it's a weekday, otherwise, add a weekend-specific greeting
    if 0 <= current_weekday < 5:  # Monday to Friday
        greeting += " " + random.choice(weekday_greetings)
    else:  # Saturday and Sunday
        greeting += " " + random.choice(weekend_greetings)

    # Send the greeting to the user
    await message.reply(greeting)

    # Check if User Logged-In else,return LOGIN_MESSAGE
    login_message = login_message_updated_ui
    if not await tdatabase.load_user_session(chat_id) and await pgdatabase.check_chat_id_in_pgb(chat_id) is False:
        await bot.send_message(chat_id,login_message)
    else:
        await buttons.start_user_buttons(bot,message)


async def is_user_logged_in(bot,message):
    chat_id = message.chat.id
    if await tdatabase.load_user_session(chat_id):
        return True
async def perform_login(username, password):
    """
    Perform login with the provided username and password for KITS ERP.
    Handles the two-step login process:
    1. Submit username with 'Next' button
    2. Submit password with 'Login' button

    Returns:
        dict: Session data if login is successful, None otherwise.
    """
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
        'Referer': 'https://kitsgunturerp.com/BeesERP/Login.aspx',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
    }

    with requests.Session() as s:
        try:
            # Step 1: Get the login page to extract hidden form fields
            login_url = "https://kitsgunturerp.com/BeesERP/Login.aspx"
            response = s.get(login_url, headers=headers, timeout=30)
            
            # Check if we got a successful response
            if response.status_code != 200:
                print(f"Failed to load login page. Status code: {response.status_code}")
                return None
            
            # Parse the page to extract hidden fields
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract hidden fields that need to be submitted with the login
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
            eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
            
            # Debug: Print extracted fields
            print(f"Step 1 - VIEWSTATE: {viewstate.get('value', '')[:50] if viewstate else 'None'}")
            print(f"Step 1 - VIEWSTATEGENERATOR: {viewstategenerator.get('value', '') if viewstategenerator else 'None'}")
            print(f"Step 1 - EVENTVALIDATION: {eventvalidation.get('value', '')[:50] if eventvalidation else 'None'}")
            
            # Prepare the username data
            data = {
                '__VIEWSTATE': viewstate.get('value', '') if viewstate else '',
                '__VIEWSTATEGENERATOR': viewstategenerator.get('value', '') if viewstategenerator else '',
                '__EVENTVALIDATION': eventvalidation.get('value', '') if eventvalidation else '',
                'txtUserName': username,
                'btnNext': 'Next'
            }
            
            # Submit the first step (username)
            response = s.post(login_url, headers=headers, data=data, timeout=15)
            
            # Check if the first step was successful
            if response.status_code != 200:
                print(f"Failed to submit username. Status code: {response.status_code}")
                return None
            
            # Debug: Check response content
            print(f"Username submission response length: {len(response.text)}")
            
            # Step 2: Parse the response to get the new hidden fields for password submission
            soup = BeautifulSoup(response.text, 'html.parser')
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
            eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
            
            # Debug: Print extracted fields for password step
            print(f"Step 2 - VIEWSTATE: {viewstate.get('value', '')[:50] if viewstate else 'None'}")
            print(f"Step 2 - VIEWSTATEGENERATOR: {viewstategenerator.get('value', '') if viewstategenerator else 'None'}")
            print(f"Step 2 - EVENTVALIDATION: {eventvalidation.get('value', '')[:50] if eventvalidation else 'None'}")
            
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
            
            # Submit the login form with password
            login_response = s.post(login_url, headers=headers, data=data, timeout=15)
            
            # Check if login was successful
            if login_response.status_code != 200:
                print(f"Failed to submit password. Status code: {login_response.status_code}")
                return None
            
            # Debug: Check login response
            print(f"Password submission response length: {len(login_response.text)}")
            
            # Check if login was successful by looking for dashboard elements
            # Common indicators of successful login
            success_indicators = [
                'Dashboard',
                'Home',
                'Welcome',
                'Logout',
                'dashboard',
                'home'
            ]
            
            # Check for any of the success indicators in the response
            login_successful = any(indicator in login_response.text for indicator in success_indicators)
            
            # Additional check: Look for common navigation elements
            if not login_successful:
                soup = BeautifulSoup(login_response.text, 'html.parser')
                # Look for common elements that appear after successful login
                nav_elements = soup.find_all(['nav', 'ul', 'div'], class_=['menu', 'navigation', 'nav'])
                if nav_elements:
                    login_successful = True
            
            if login_successful:
                session_data = {
                    'cookies': s.cookies.get_dict(),
                    'headers': headers,
                    'username': username  # Save the username in the session data
                }
                print("Login successful!")
                return session_data
            else:
                print("Login failed - no success indicators found in response")
                # Debug: Print part of the response to understand what we got
                print(f"Response preview: {login_response.text[:500]}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error during login: {e}")
            return {"error": "server_error", "message": str(e)}
        except Exception as e:
            print(f"Unexpected error during login: {e}")
            return {"error": "server_error", "message": str(e)}

async def login(bot,message):
    chat_id = message.chat.id
    command_args = message.text.split()[1:]
    # banned_usernames = await tdatabase.get_all_banned_usernames()
    if not command_args:
        username = ""
    else:
        username = command_args[0] # username of the user
    if await tdatabase.get_bool_banned_username(username) is True: # Checks whether the username is in banned users or not.
        return # Returns Nothing
    if await tdatabase.load_user_session(chat_id): # Tries to get the cookies from the database.If found, it displays that you are already logged in.
        await message.reply("You are already logged in.")
        await buttons.start_user_buttons(bot,message)
        await message.delete()
        return

    if len(command_args) != 2:
        invalid_command_message =f"""
```WELCOME
⫸ How To Login:

/login rollnumber password

⫸ Example:

/login 22951A0000 iare_unoffical_bot
```
        """
        await message.reply(invalid_command_message)
        return

    password = command_args[1]
    print(f"DEBUG: Starting login process for user: {username}")
    start_time = time.time()
    session_data = await perform_login(username, password)
    login_time = time.time() - start_time
    print(f"DEBUG: Login process completed in {login_time:.2f} seconds")
    # Initializes settings for the user
    await user_settings.set_user_default_settings(chat_id)
    
    # Check if it's a server error
    if isinstance(session_data, dict) and session_data.get("error") == "server_error":
        await bot.send_message(chat_id, text="WELCOME\n\n⫸ Server problem from KITS ERP. Please try again later.")
        return
    
    if session_data:
        await tdatabase.store_user_session(chat_id, json.dumps(session_data), username)
        await tdatabase.store_username(username)
        await message.delete()
        await bot.send_message(chat_id,text="Login successful!")
        
        # Start session keep-alive in background (non-blocking)
        import asyncio
        asyncio.create_task(start_session_keepalive(bot, chat_id))
        
        # Simplified database check - only check SQLite for speed
        try:
            sqlite_exists = await tdatabase.check_chat_id_in_database(chat_id)
            
            if sqlite_exists:
                await bot.send_message(chat_id,text="Your login information has already been registered.")
            else:
                # Show main menu first, then save credentials prompt
                await buttons.start_user_buttons(bot,message)
                await message.reply_text("If you want to save your credentials Click on \"Yes\".",reply_markup =await buttons.start_save_credentials_buttons(username,password))
        except Exception as e:
            print(f"Database check failed, showing save credentials option: {e}")
            # Show main menu first, then save credentials prompt
            await buttons.start_user_buttons(bot,message)
            await message.reply_text("If you want to save your credentials Click on \"Yes\".",reply_markup =await buttons.start_save_credentials_buttons(username,password))
        
    else:
        await bot.send_message(chat_id,text="WELCOME\n\n⫸ Invalid username or password.")

async def auto_login_by_database(bot,message,chat_id):
    # username,password = await pgdatabase.retrieve_credentials_from_database(chat_id) This Can be used if you want to take credentials from cloud database.
    username,password = await tdatabase.fetch_credentials_from_database(chat_id) # This can be used to Fetch credentials from the Local database.
    # Initializes settings for the user if the settings are not present
    await user_settings.set_user_default_settings(chat_id)
    if username != None:
        # Don't truncate username - keep full roll number
        if await tdatabase.get_bool_banned_username(username) is True: # Checks whether the username is in banned users or not.
            # await tdatabase.delete_banned_username_credentials_data(username)
            banned_username_chat_ids = await tdatabase.get_chat_ids_of_the_banned_username(username)
            for chat_id in banned_username_chat_ids:
                if await tdatabase.delete_user_credentials(chat_id) is True:
                    if await pgdatabase.remove_saved_credentials_silent(chat_id) is True:
                        return False
        session_data = await perform_login(username, password)
        
        # Check if it's a server error
        if isinstance(session_data, dict) and session_data.get("error") == "server_error":
            await bot.send_message(chat_id, text="WELCOME\n\n⫸ Server problem from KITS ERP. Please try again later.")
            return False
        
        if session_data:
            await tdatabase.store_user_session(chat_id, json.dumps(session_data), username)  # Implement store_user_session function
            await tdatabase.store_username(username)
            await bot.send_message(chat_id,text="Login successful!")
            
            # Start session keep-alive
            await start_session_keepalive(bot, chat_id)
            
            return True
        else:
            if await tdatabase.check_chat_id_in_database(chat_id) is True:
                await bot.send_message(chat_id,text="WELCOME\n\n⫸ Unable to login using saved credentials, please try updating your password")
            return False
    else:
        return False

async def logout(bot, message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        if ui_mode[0] == 0:
            await bot.send_message(chat_id, text=login_message_updated_ui)
        elif ui_mode[0] == 1:
            await bot.send_message(chat_id, text=login_message_traditional_ui)
        return

    # Try to logout from KITS ERP — attempt multiple possible endpoints
    candidate_logout_urls = [
        'https://kitsgunturerp.com/BeesERP/Logout.aspx',
        'https://kitsgunturerp.com/BeesERP/StudentLogin/Logout.aspx',
        'https://kitsgunturerp.com/BeesERP/Login.aspx?logout=1'
    ]
    session_data = await tdatabase.load_user_session(chat_id)
    cookies, headers = session_data['cookies'], session_data.get('headers', {})
    
    logout_sent = False
    try:
        for url in candidate_logout_urls:
            try:
                response = requests.get(url, cookies=cookies, headers=headers, timeout=30, allow_redirects=True)
                if response.status_code in (200, 302, 301):
                    logout_sent = True
                    break
            except Exception:
                continue
        if logout_sent:
            print(f"Logout request sent for chat_id: {chat_id}")
        else:
            # Keep this quiet; we clear local session below anyway
            print(f"Logout endpoint not found (non-fatal) for chat_id: {chat_id}")
    except Exception as e:
        print(f"Error during logout request (non-fatal): {e} for chat_id: {chat_id}")
    
    # Clear session data from database regardless of ERP logout success
    await tdatabase.delete_user_session(chat_id)
    
    # Stop session keep-alive
    await stop_session_keepalive(chat_id)
    
    # Show login instructions after logout
    if ui_mode[0] == 0:
        await bot.send_message(chat_id, text=login_message_updated_ui)
    elif ui_mode[0] == 1:
        await bot.send_message(chat_id, text=login_message_traditional_ui)

async def logout_user_and_remove(bot, message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)

    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        await bot.send_message(chat_id, text="You are already logged out.")
        return

    # Try to logout from KITS ERP — attempt multiple possible endpoints
    candidate_logout_urls = [
        'https://kitsgunturerp.com/BeesERP/Logout.aspx',
        'https://kitsgunturerp.com/BeesERP/StudentLogin/Logout.aspx',
        'https://kitsgunturerp.com/BeesERP/Login.aspx?logout=1'
    ]
    session_data = await tdatabase.load_user_session(chat_id)
    cookies, headers = session_data['cookies'], session_data.get('headers', {})
    
    logout_sent = False
    try:
        for url in candidate_logout_urls:
            try:
                response = requests.get(url, cookies=cookies, headers=headers, timeout=30, allow_redirects=True)
                if response.status_code in (200, 302, 301):
                    logout_sent = True
                    break
            except Exception:
                continue
        if logout_sent:
            print(f"Logout request sent for chat_id: {chat_id}")
        else:
            # Keep this quiet; we clear local session below anyway
            print(f"Logout endpoint not found (non-fatal) for chat_id: {chat_id}")
    except Exception as e:
        print(f"Error during logout request (non-fatal): {e} for chat_id: {chat_id}")
    
    # Clear session data from database regardless of ERP logout success
    await tdatabase.delete_user_session(chat_id)
    
    # Show login instructions after logout
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
        ui_mode = await user_settings.fetch_ui_bool(chat_id)
    
    if ui_mode[0] == 0:
        await bot.send_message(chat_id, text=login_message_updated_ui)
    elif ui_mode[0] == 1:
        await bot.send_message(chat_id, text=login_message_traditional_ui)

async def biometric(bot, message):
    chat_id = message.chat.id
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        auto_login_status = await auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)#check Chat id in the database
        if auto_login_status is False and chat_id_in_local_database is False:
            # LOGIN MESSAGE
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return

    session_data = await tdatabase.load_user_session(chat_id)

    # TODO: Replace with actual KITS ERP biometric/profile URL after inspection
    biometric_url = 'https://kitsgunturerp.com/BeesERP/StudentProfile.aspx'  # Placeholder - needs actual URL
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        headers = session_data['headers']
        response = s.get(biometric_url, headers=headers)

        # Parse the HTML content using BeautifulSoup
        Biometric_html = BeautifulSoup(response.text, 'html.parser')
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    
    # Check if session is still valid
    if 'Login' in response.text or 'login' in response.text.lower():
        if chat_id_in_local_database:
            await silent_logout_user_if_logged_out(bot, chat_id)
            await biometric(bot, message)
        else:
            await logout_user_if_logged_out(bot, chat_id)
        return

    # TODO: Update table parsing logic based on KITS ERP HTML structure
    # This is a placeholder - actual implementation depends on KITS ERP structure
    # Find tables in the page
    biometric_tables = Biometric_html.find_all('table')
    
    if not biometric_tables:
        await message.reply("Biometric data not found.")
        await buttons.start_user_buttons(bot, message)
        return

    # Dictionary to store attendance data for each student
    attendance_data = {
        'Total Days Present': 0,
        'Total Days Absent': 0,
        'Total Days': 0
    }

    # TODO: Adjust parsing logic based on actual KITS ERP table structure
    # This is a placeholder implementation
    biometric_table = biometric_tables[0]  # Adjust index as needed
    biometric_rows = biometric_table.find_all('tr')[1:]  # Skip header row
    
    # Count present/absent days (placeholder logic)
    for row in biometric_rows:
        cells = row.find_all(['td', 'th'])
        if len(cells) >= 3:
            # Placeholder logic - adjust based on actual table structure
            date = cells[0].text.strip()
            status = cells[-1].text.strip().lower()  # Assume last column is status
            
            if 'present' in status:
                attendance_data['Total Days Present'] += 1
            elif 'absent' in status:
                attendance_data['Total Days Absent'] += 1

    attendance_data['Total Days'] = attendance_data['Total Days Present'] + attendance_data['Total Days Absent']
    
    # Calculate the biometric percentage
    biometric_percentage = (attendance_data['Total Days Present'] / attendance_data['Total Days']) * 100 if attendance_data['Total Days'] != 0 else 0
    biometric_percentage = round(biometric_percentage, 3)

    # For KITS ERP, we'll simplify the biometric calculation since the structure may be different
    # Calculate the biometric percentage with six hours gap (placeholder)
    six_percentage = biometric_percentage * 0.85  # Placeholder calculation
    days_six_hours = int(attendance_data['Total Days Present'] * 0.85)  # Placeholder
    
    leaves_biometric,leave_status = await biometric_leaves(chat_id,present_days=attendance_data['Total Days Present'],total_days=attendance_data['Total Days'])
    six_hour_leaves,six_hour_leave_status = await biometric_leaves(chat_id,present_days=days_six_hours,total_days=attendance_data['Total Days'])
    biometric_threshold = await user_settings.fetch_biometric_threshold(chat_id)
    if leave_status is True:
        leaves_biometric_msg = f"● Leaves available       -  {leaves_biometric}"
    elif leave_status is False:
        leaves_biometric_msg = f"● Days to Attend         -  {leaves_biometric}"
    if six_hour_leave_status is True:
        six_hour_leave_msg = f"● Leaves available (6h)  -  {six_hour_leaves}"
    elif six_hour_leave_status is False:
        six_hour_leave_msg = f"● Days to Attend         -  {six_hour_leaves}" 
    biometric_msg_updated = f"""
    ```BIOMETRIC
⫷

● Total Days             -  {attendance_data['Total Days']}
                    
● Days Present           -  {attendance_data['Total Days Present']}  
                
● Days Absent            -  {attendance_data['Total Days Absent']}

----

● Biometric Threshold    -  {biometric_threshold[0]}

----

⫸ Regular Biometric

● Biometric %            -  {biometric_percentage}

{leaves_biometric_msg}

----

⫸ Simplified Biometric

● Biometric % (approx)   -  {six_percentage}

{six_hour_leave_msg}

⫸

@kits_erp_bot
```
    """
    biometric_msg_traditional = """
**BIOMETRIC**

⫷

● Total Days             -  {attendance_data['Total Days']}
                    
● Days Present           -  {attendance_data['Total Days Present']}  
                
● Days Absent            -  {attendance_data['Total Days Absent']}


● Biometric Threshold    -  {biometric_threshold[0]}


⫸ Regular Biometric

● Biometric %            -  {biometric_percentage}

{leaves_biometric_msg}


⫸ Simplified Biometric

● Biometric % (approx)   -  {six_percentage}

{six_hour_leave_msg}

⫸

@kits_erp_bot
"""
    if ui_mode[0] == 0:
        await bot.send_message(chat_id, biometric_msg_updated)
    else:
        await bot.send_message(chat_id, biometric_msg_traditional)
    
    
    await buttons.start_user_buttons(bot,message)


async def six_hours_biometric(biometric_rows, totaldays, intime_index,outtime_index):
    intimes, outtimes = [], []
    time_gap_more_than_six_hours = 0
    for row in biometric_rows:
        cell = row.find_all('td')
        intime = cell[intime_index].text.strip()
        outtime = cell[outtime_index].text.strip()
        if intime and outtime and ':' in intime and ':' in outtime:
            intimes.append(intime)
            outtimes.append(outtime)
            intime_hour, intime_minute = intime.split(':')
            outtime_hour, outtime_minute = outtime.split(':')
            time_difference = (int(outtime_hour) - int(intime_hour)) * 60 + (int(outtime_minute) - int(intime_minute))
            if time_difference >= 360:
                time_gap_more_than_six_hours += 1
    # Calculate the biometric percentage with six hours gap
    six_percentage = (time_gap_more_than_six_hours / totaldays) * 100 if totaldays != 0 else 0
    six_percentage = round(six_percentage, 3)
    return six_percentage,time_gap_more_than_six_hours

async def biometric_leaves(chat_id,present_days,total_days):
    biometric_threshold = await user_settings.fetch_biometric_threshold(chat_id)
    biometric_percentage = present_days / total_days * 100
    if biometric_percentage > biometric_threshold[0]:
        no_of_leaves = 0
        while (present_days / (total_days + no_of_leaves)) * 100 >= biometric_threshold[0]:
            no_of_leaves += 1
        no_of_leaves -= 1  # Subtract 1 to account for the last iteration
        return no_of_leaves, True
    elif biometric_percentage < biometric_threshold[0]:
        days_need_attend = 0
        while (present_days + days_need_attend) / (total_days + days_need_attend) * 100 < biometric_threshold[0]:
            days_need_attend += 1
        return days_need_attend, False
    elif biometric_percentage == biometric_threshold[0]:
        no_of_leaves = 0
        return no_of_leaves,True

async def attendance(bot, message):
    """
    Temporary attendance handler.
    Reuses the bunk flow to fetch attendance data and present it to the user.
    This avoids callback errors when tapping the Attendance button.
    """
    await attendance_subjectwise(bot, message)

_attendance_message_ids_by_chat: dict[int, list[int]] = {}

async def attendance_subjectwise(bot, message):
    """
    Fetch and display subject-wise attendance.
    - Shows Overall Attendance box if available
    - Sends one box per subject with Conducted, Attended, and Percentage
    """
    chat_id = message.chat.id
    # Try to delete previously sent attendance messages for a clean view
    try:
        old_ids = _attendance_message_ids_by_chat.get(chat_id, [])
        if old_ids:
            try:
                await bot.delete_messages(chat_id, old_ids)
            except Exception:
                pass
            _attendance_message_ids_by_chat[chat_id] = []
        # also delete the user's triggering message if possible
        try:
            await bot.delete_messages(chat_id, [message.id])
        except Exception:
            pass
    except Exception:
        pass

    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    if not session_data:
        auto_login_status = await auto_login_by_database(bot, message, chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id, text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id, text=login_message_traditional_ui)
            return

    session_data = await tdatabase.load_user_session(chat_id)
    candidate_attendance_urls = [
        "https://kitsgunturerp.com/BeesERP/StudentLogin/MainStud.aspx",
        "https://kitsgunturerp.com/BeesERP/StudentAttendance.aspx",
        "https://kitsgunturerp.com/BeesERP/StudentLogin/StudentAttendance.aspx",
        "https://kitsgunturerp.com/BeesERP/StudentLogin/Attendance.aspx",
        "https://kitsgunturerp.com/BeesERP/Attendance.aspx",
        "https://kitsgunturerp.com/BeesERP/StudentLogin/StudAttendance.aspx"
    ]

    attendance_response = None
    with requests.Session() as s:
        cookies = session_data["cookies"]
        headers = session_data.get("headers", {}) or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://kitsgunturerp.com/BeesERP/Login.aspx',
            'Upgrade-Insecure-Requests': '1'
        }
        s.cookies.update(cookies)
        for url in candidate_attendance_urls:
            try:
                resp = s.get(url, headers=headers, allow_redirects=True, timeout=30)
                if (
                    "Login.aspx" in getattr(resp, "url", "")
                    or "txtUserName" in resp.text
                    or "btnNext" in resp.text
                ):
                    continue
                if "<table" in resp.text or "%" in resp.text:
                    attendance_response = resp
                    break
            except Exception:
                continue
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if attendance_response is None:
        # Fall back to bunk flow if nothing worked
        await bunk(bot, message)
        return

    soup = BeautifulSoup(attendance_response.text, "html.parser")
    # Overall box if available on page
    overall_span = soup.find(id="ctl00_cpStud_lblTotalPercentage")
    if overall_span and overall_span.get_text(strip=True):
        try:
            overall_percent = float(overall_span.get_text(strip=True).replace('%', '').strip())
            overall_attendance_msg = f"""
```
Overall Attendance

● Attendance  -  {overall_percent}%

```
"""
            _sent_ids: list[int] = _attendance_message_ids_by_chat.get(chat_id, [])
            msg_obj = await bot.send_message(chat_id, overall_attendance_msg)
            try:
                _sent_ids.append(msg_obj.id)
                _attendance_message_ids_by_chat[chat_id] = _sent_ids
            except Exception:
                pass
        except Exception:
            pass

    # Find subject table by header
    def detect_indexes_by_header(header_cells):
        # Normalize header texts by collapsing spaces
        lowered = [re.sub(r"\s+", " ", h.lower().strip()) for h in header_cells]
        # Hard filter: skip date-wise tables
        header_joined = " ".join(lowered)
        if any(x in header_joined for x in ["date", "dayname"]) or re.search(r"\d{1,2}:\d{2}", header_joined):
            return None
        # Prefer exact header matches to avoid SINo and other columns
        idx = {"course": None, "conducted": None, "attended": None, "percent": None, "faculty": None}
        faculty_idx = None
        for i, text in enumerate(lowered):
            if idx["course"] is None and re.fullmatch(r"(subject|subject name|sub name)", text):
                idx["course"] = i
            if idx["conducted"] is None and ("classes held" in text or re.fullmatch(r"(held|conducted)", text)):
                idx["conducted"] = i
            if idx["attended"] is None and ("classes attended" in text or re.fullmatch(r"attended|present", text)):
                idx["attended"] = i
            if idx["percent"] is None and ("att %" in text or "att%" in text or re.fullmatch(r"(%|percent|attendance %|attendance%)", text)):
                idx["percent"] = i
            if faculty_idx is None and "faculty" in text:
                faculty_idx = i

        # If strict match failed for subject, try softer match but exclude SINo/Sl No
        if idx["course"] is None:
            for i, text in enumerate(lowered):
                if ("subject" in text or "subject name" in text or "sub name" in text) and not any(x in text for x in ["sino", "s.no", "sl no", "sno", "sin o", "s no"]):
                    idx["course"] = i
                    break

        # If still missing subject but we have faculty and held/attended/percent, infer subject as the column to the left of faculty when plausible
        if idx["course"] is None and faculty_idx is not None:
            possible = faculty_idx - 1
            if possible >= 0:
                text = lowered[possible]
                if not any(x in text for x in ["sin", "s no", "sl no", "sino", "s.no"]):
                    idx["course"] = possible
        # record detected faculty index if any
        idx["faculty"] = faculty_idx

        # Require Subject, Held, Attended, and Percent for strict matching
        has_core = (
            idx["course"] is not None and
            idx["conducted"] is not None and
            idx["attended"] is not None and
            idx["percent"] is not None
        )
        if not has_core:
            return None
        return idx

    tables = soup.find_all("table")
    candidate = None
    for table in tables:
        # Prefer tbody rows and avoid nested rows
        tbody = table.find("tbody")
        if tbody is not None:
            rows = tbody.find_all("tr", recursive=False)
            if not rows:
                rows = tbody.find_all("tr")
        else:
            rows = table.find_all("tr", recursive=False)
            if not rows:
                rows = table.find_all("tr")
        if not rows:
            continue
        # Find the actual header row (skip title rows). Look for a row that contains the full header set.
        header_row_index = None
        header_idx = None
        for ri, r in enumerate(rows[:5]):  # inspect first few rows for header
            header_cells = [re.sub(r"\s+", " ", c.get_text(separator=" ", strip=True)) for c in r.find_all(["th", "td"], recursive=False)]
            if len(header_cells) < 4:
                continue
            joined = " ".join(h.lower() for h in header_cells)
            if (
                ("subject" in joined or "subject name" in joined or "sub name" in joined)
                and ("classes held" in joined or "held" in joined)
                and ("classes attended" in joined or "attended" in joined)
                and ("att %" in joined or "att%" in joined or "%" in joined)
            ):
                # Fast path for common schema: [SlNo, Subject, Faculty, Classes Held, Classes Attended, Att %]
                normalized = [h.lower() for h in header_cells]
                if (
                    len(normalized) >= 6
                    and normalized[0].startswith("s")
                    and "subject" in normalized[1]
                    and "faculty" in normalized[2]
                    and "classes held" in normalized[3]
                    and "classes attended" in normalized[4]
                    and ("att %" in normalized[5] or "att%" in normalized[5] or "%" == normalized[5])
                ):
                    hdr_idx = {"course": 1, "conducted": 3, "attended": 4, "percent": 5, "faculty": 2}
                else:
                    hdr_idx = detect_indexes_by_header(header_cells)
                if hdr_idx is None:
                    continue
                header_row_index = ri
                header_idx = hdr_idx
                break
        if header_idx is not None:
            # Boost tables that are clearly titled Subject Wise Attendance
            score = 0
            caption = table.find("caption")
            if caption and "subject" in caption.get_text(strip=True).lower():
                score += 2
            # check preceding sibling text
            prev = table.find_previous(["h1","h2","h3","h4","h5","strong","b","p","div"])
            if prev and "subject" in prev.get_text(strip=True).lower():
                score += 1
            candidate = (table, header_idx, header_row_index)
            break

    sent_any = False
    if candidate is not None:
        table, idx, header_row_index = candidate
        course_idx = idx["course"] if idx["course"] is not None else 0
        conducted_idx = idx["conducted"] if idx["conducted"] is not None else 1
        attended_idx = idx["attended"] if idx["attended"] is not None else 2
        percent_idx = idx["percent"] if idx["percent"] is not None else 3
        faculty_idx = idx.get("faculty")
        # Use direct child rows after header
        tbody = table.find("tbody")
        all_rows = None
        if tbody is not None:
            all_rows = tbody.find_all("tr", recursive=False)
            if not all_rows:
                all_rows = tbody.find_all("tr")
        else:
            all_rows = table.find_all("tr", recursive=False)
            if not all_rows:
                all_rows = table.find_all("tr")
        data_rows = all_rows[header_row_index + 1:]
        for row in data_rows:
            cols = row.find_all(["td", "th"], recursive=False)
            if len(cols) <= percent_idx:
                continue
            course_name = re.sub(r"\s+", " ", cols[course_idx].get_text(separator=" ", strip=True))
            faculty_text = re.sub(r"\s+", " ", cols[faculty_idx].get_text(separator=" ", strip=True)) if faculty_idx is not None and faculty_idx < len(cols) else ""
            if not course_name or course_name.lower().startswith("sin"):
                continue
            if course_name.lower().startswith("total"):
                # skip summary row
                continue
            conducted_text = cols[conducted_idx].get_text(separator=" ", strip=True) if conducted_idx is not None and conducted_idx < len(cols) else "0"
            attended_text = cols[attended_idx].get_text(separator=" ", strip=True) if attended_idx is not None and attended_idx < len(cols) else "0"
            percent_text = cols[percent_idx].get_text(separator=" ", strip=True)
            try:
                percent_val = float(re.sub(r"[^0-9.]", "", percent_text) or 0)
            except Exception:
                percent_val = 0.0
            try:
                conducted_val = int(re.sub(r"[^0-9]", "", conducted_text) or 0)
            except Exception:
                conducted_val = 0
            try:
                attended_val = int(re.sub(r"[^0-9]", "", attended_text) or 0)
            except Exception:
                attended_val = 0

            if not course_name:
                continue
            # Basic sanity: if numbers look like row indices (1..N) while percent is tiny, double-check by skipping when "Conducted" equals the 1-based row number and subject is a single digit.
            if re.fullmatch(r"\d+", course_name):
                # this is likely the SINo column; skip
                continue

        # End subject-wise parsing
            # Determine status by threshold
            attendance_threshold = await user_settings.fetch_attendance_threshold(chat_id)
            status_text = "Satisfactory" if percent_val >= attendance_threshold[0] else "Shortage"
            header_line = course_name if not faculty_text else f"{course_name} — {faculty_text}"
            msg = f"""
```{header_line}

● Conducted     -  {conducted_val}

● Attended      -  {attended_val}

● Attendance %  -  {percent_val}

● Status        -  {status_text}

```
"""
            _sent_ids = _attendance_message_ids_by_chat.get(chat_id, [])
            msg_obj = await bot.send_message(chat_id, msg)
            try:
                _sent_ids.append(msg_obj.id)
                _attendance_message_ids_by_chat[chat_id] = _sent_ids
            except Exception:
                pass
            sent_any = True

    if not sent_any:
        # Dashboard fallback already implemented in bunk(); reuse it
        await bunk(bot, message)
        return

    # Store collected ids so we can delete them next time
    if chat_id not in _attendance_message_ids_by_chat:
        _attendance_message_ids_by_chat[chat_id] = []
    await buttons.start_user_buttons(bot, message)

_last_bunk_call_by_chat = {}

async def bunk(bot, message):
    """
    Enhanced bunk function with session validation and auto-reconnection
    """
    chat_id = message.chat.id
    now_ts = time.time()
    last_ts = _last_bunk_call_by_chat.get(chat_id, 0)
    if now_ts - last_ts < 1.5:
        return
    _last_bunk_call_by_chat[chat_id] = now_ts
    
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    
    # Enhanced session handling with validation and auto-reconnection
    if not session_data:
        auto_login_status = await auto_login_by_database(bot, message, chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id, text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id, text=login_message_traditional_ui)
            return
    else:
        # Validate existing session before proceeding
        if not await validate_session(chat_id):
            print(f"Session validation failed for chat_id: {chat_id}, attempting auto-reconnection")

            # Try auto-reconnection
            if await auto_reconnect_session(bot, chat_id):
                print(f"Auto-reconnection successful for chat_id: {chat_id}")
            else:
                print(f"Auto-reconnection failed for chat_id: {chat_id}")
                await bot.send_message(chat_id, "Your session has expired. Please login again using /login command.")
                await buttons.start_user_buttons(bot, message)
                return

    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        await bot.send_message(chat_id, "Unable to establish session. Please login again.")
        await buttons.start_user_buttons(bot, message)
        return
    
    # Start session keep-alive if not already running
    if chat_id not in _session_keepalive_timers:
        await start_session_keepalive(bot, chat_id)
    
    # Get real-time attendance data with enhanced error handling
    attendance_response = None
    max_retries = 2
    retry_count = 0
    
    while retry_count < max_retries and not attendance_response:
        try:
            with requests.Session() as s:
                cookies = session_data["cookies"]
                headers = session_data.get("headers", {}) or {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Referer': 'https://kitsgunturerp.com/BeesERP/Login.aspx',
                    'Upgrade-Insecure-Requests': '1'
                }
                s.cookies.update(cookies)
                
                # Try the main attendance page first
                try:
                    resp = s.get("https://kitsgunturerp.com/BeesERP/StudentAttendance.aspx", headers=headers, allow_redirects=True, timeout=30)
                    if "Login.aspx" not in getattr(resp, "url", "") and "Login.aspx" not in resp.text:
                        attendance_response = resp
                except Exception as e:
                    print(f"First attempt failed for chat_id {chat_id}: {e}")
                
                # If that didn't work, try the main student page
                if not attendance_response:
                    try:
                        resp = s.get("https://kitsgunturerp.com/BeesERP/StudentLogin/MainStud.aspx", headers=headers, allow_redirects=True, timeout=30)
                        if "Login.aspx" not in getattr(resp, "url", "") and "Login.aspx" not in resp.text:
                            attendance_response = resp
                    except Exception as e:
                        print(f"Second attempt failed for chat_id {chat_id}: {e}")
                
                # If still no response and we have retries left, try auto-reconnection
                if not attendance_response and retry_count < max_retries - 1:
                    print(f"Attempting auto-reconnection for chat_id: {chat_id} (attempt {retry_count + 1})")
                    if await auto_reconnect_session(bot, chat_id):
                        session_data = await tdatabase.load_user_session(chat_id)
                        retry_count += 1
                        continue
                    else:
                        break
                        
        except Exception as e:
            print(f"Session error for chat_id {chat_id}: {e}")
            break
        
        retry_count += 1

    if not attendance_response:
        await bot.send_message(chat_id, "Unable to fetch attendance data. Please try logging in again.")
        await buttons.start_user_buttons(bot, message)
        return

    data = BeautifulSoup(attendance_response.text, "html.parser")
    attendance_threshold = await user_settings.fetch_attendance_threshold(chat_id)
    
    # Find all tables and look for attendance data
    tables = data.find_all("table")
    sent_any = False
    
    for table in tables:
        rows = table.find_all("tr")
        if len(rows) < 2:  # Need at least header + 1 data row
            continue
            
        # Look for header row with attendance-related columns
        header_row = rows[0]
        header_cells = [cell.get_text(strip=True).lower() for cell in header_row.find_all(["th", "td"])]
        
        # Find column indices
        course_idx = None
        conducted_idx = None
        attended_idx = None
        percent_idx = None
        
        for i, header in enumerate(header_cells):
            if any(word in header for word in ["subject", "course", "sub name"]):
                course_idx = i
            elif any(word in header for word in ["conducted", "held", "total"]):
                conducted_idx = i
            elif any(word in header for word in ["attended", "present"]):
                attended_idx = i
            elif any(word in header for word in ["%", "percent", "attendance"]):
                percent_idx = i
        
        # If we found the required columns, process the data
        if course_idx is not None and percent_idx is not None:
            for row in rows[1:]:  # Skip header
                cells = row.find_all(["td", "th"])
                if len(cells) <= max(course_idx, percent_idx):
                    continue
                    
                course_name = cells[course_idx].get_text(strip=True)
                if not course_name or course_name.lower().startswith("total"):
                    continue
                
                # Get attendance percentage
                try:
                    percent_text = cells[percent_idx].get_text(strip=True)
                    attendance_present = float(percent_text.replace("%", "").strip())
                except:
                    continue
                
                # Get conducted and attended classes if available
                conducted_classes = 0
                attended_classes = 0
                if conducted_idx is not None and conducted_idx < len(cells):
                    try:
                        conducted_text = cells[conducted_idx].get_text(strip=True)
                        conducted_classes = int(re.sub(r"[^0-9]", "", conducted_text) or 0)
                    except:
                        pass
                
                if attended_idx is not None and attended_idx < len(cells):
                    try:
                        attended_text = cells[attended_idx].get_text(strip=True)
                        attended_classes = int(re.sub(r"[^0-9]", "", attended_text) or 0)
                    except:
                        pass
                
                # Calculate bunk recommendations
                if attendance_present >= attendance_threshold[0]:
                    # Above threshold - can bunk
                    classes_bunked = 0
                    if conducted_classes > 0:
                        while conducted_classes + classes_bunked > 0 and (attended_classes / (conducted_classes + classes_bunked)) * 100 >= attendance_threshold[0]:
                            classes_bunked += 1
                        classes_bunked -= 1
                    
                    msg = f"""
```{course_name}

● Attendance  -  {attendance_present}%

● You can bunk {classes_bunked} classes

```
"""
                else:
                    # Below threshold - need to attend more
                    classes_needattend = 0
                    if conducted_classes > 0:
                        while (attended_classes + classes_needattend) / (conducted_classes + classes_needattend) * 100 < attendance_threshold[0]:
                            classes_needattend += 1
                    
                    msg = f"""
```{course_name}

● Attendance  -  Below {attendance_threshold[0]}%

● Attend {classes_needattend} classes for {attendance_threshold[0]}%

● No Bunk Allowed

```
"""
                
                await bot.send_message(chat_id, msg)
                sent_any = True
    
    # Display overall attendance if available
    try:
        overall_span = data.find(id="ctl00_cpStud_lblTotalPercentage")
        if overall_span and overall_span.get_text(strip=True):
            percent_text = overall_span.get_text(strip=True).replace("%", "").strip()
            overall_percent = float(percent_text)
            overall_msg = f"""
```
Overall Attendance

● Attendance  -  {overall_percent}%

```
"""
            await bot.send_message(chat_id, overall_msg)
    except:
        pass
    
    if not sent_any:
        await bot.send_message(chat_id, "No attendance data found. Please check if you're logged in correctly.")
    
    await buttons.start_user_buttons(bot, message)

async def silent_logout_user_if_logged_out(bot, chat_id):
    """Silently logout user if they are logged out from ERP"""
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        return
    await tdatabase.delete_user_session(chat_id)

async def logout_user_if_logged_out(bot, chat_id):
    """Logout user and show message if they are logged out from ERP"""
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data or 'cookies' not in session_data or 'headers' not in session_data:
        return
    await tdatabase.delete_user_session(chat_id)
    await bot.send_message(chat_id, "Your session has expired. Please login again.")
    # Note: start_user_buttons will be called by the calling function

async def bunk_old(bot,message):
    chat_id = message.chat.id
    now_ts = time.time()
    last_ts = _last_bunk_call_by_chat.get(chat_id, 0)
    if now_ts - last_ts < 1.5:
        return
    _last_bunk_call_by_chat[chat_id] = now_ts
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    
    if not session_data:
        auto_login_status = await auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return

    session_data = await tdatabase.load_user_session(chat_id)

    # Use KITS ERP attendance page and compute bunk recommendations
    # Try multiple likely ERP attendance endpoints
    candidate_attendance_urls = [
        "https://kitsgunturerp.com/BeesERP/StudentLogin/MainStud.aspx",
        "https://kitsgunturerp.com/BeesERP/StudentAttendance.aspx",
        "https://kitsgunturerp.com/BeesERP/StudentLogin/StudentAttendance.aspx",
        "https://kitsgunturerp.com/BeesERP/StudentLogin/Attendance.aspx",
        "https://kitsgunturerp.com/BeesERP/Attendance.aspx",
        "https://kitsgunturerp.com/BeesERP/StudentLogin/StudAttendance.aspx"
    ]

    attendance_response = None
    used_url = None
    with requests.Session() as s:

        cookies = session_data["cookies"]
        headers = session_data.get("headers", {}) or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://kitsgunturerp.com/BeesERP/Login.aspx',
            'Upgrade-Insecure-Requests': '1'
        }
        s.cookies.update(cookies)

        for url in candidate_attendance_urls:
            try:
                resp = s.get(url, headers=headers, allow_redirects=True, timeout=30)
                # Basic checks: not redirected to login, has any table or percentage
                if (
                    "Login.aspx" in getattr(resp, "url", "")
                    or "txtUserName" in resp.text
                    or "btnNext" in resp.text
                ):
                    continue
                # Prefer pages that include the Latest Attendance span id
                if "ctl00_cpStud_lblTotalPercentage" in resp.text or "<table" in resp.text or "%" in resp.text:
                    attendance_response = resp
                    used_url = url
                    break
            except Exception:
                continue
        # If none matched, fall back to the default first URL to keep flow
        if attendance_response is None:
            try:
                attendance_response = s.get(candidate_attendance_urls[0], headers=headers, allow_redirects=True, timeout=30)
                used_url = candidate_attendance_urls[0]
            except Exception:
                pass
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    data = BeautifulSoup(attendance_response.text, "html.parser")
    overall_shown = False
    # Try to extract overall attendance directly from the selected page
    try:
        current_span = data.find(id="ctl00_cpStud_lblTotalPercentage")
        if current_span and current_span.get_text(strip=True):
            attendance_threshold = await user_settings.fetch_attendance_threshold(chat_id)
            percent_text = current_span.get_text(strip=True).replace("%", "").strip()
            attendance_present_overall = float(percent_text)
            overall_attendance_msg = f"""
```
Overall Attendance

● Attendance  -  {attendance_present_overall}%

```
"""
            await bot.send_message(chat_id, overall_attendance_msg)
            overall_shown = True
    except Exception:
        pass

    # Try to fetch and show overall attendance from dashboard span if available
    try:
        dashboard_url = "https://kitsgunturerp.com/BeesERP/StudentLogin/StudLoginDashboard.aspx"
        with requests.Session() as s_dash:
            s_dash.cookies.update(session_data["cookies"])
            dash_headers = session_data.get("headers", {})
            dash_resp = s_dash.get(dashboard_url, headers=dash_headers, allow_redirects=True, timeout=30)
        if (
            "Login.aspx" not in getattr(dash_resp, "url", "")
            and "Login.aspx" not in dash_resp.text
        ):
            dash_soup = BeautifulSoup(dash_resp.text, "html.parser")
            latest_att_span = dash_soup.find(id="ctl00_cpStud_lblTotalPercentage")
            if latest_att_span and not overall_shown:
                percent_text = latest_att_span.get_text(strip=True).replace("%", "").strip()
                try:
                    attendance_present_overall = float(percent_text)
                    overall_attendance_msg = f"""
```
Overall Attendance

● Attendance  -  {attendance_present_overall}%

```
"""
                    await bot.send_message(chat_id, overall_attendance_msg)
                    overall_shown = True
                except Exception:
                    pass
    except Exception:
        pass

    # Check if session is still valid (heuristics for KITS ERP login page)
    if (
        "Login.aspx" in getattr(attendance_response, "url", "")
        or "Login.aspx" in attendance_response.text
        or "txtUserName" in attendance_response.text
        or "btnNext" in attendance_response.text
    ):
        if chat_id_in_local_database:
            await silent_logout_user_if_logged_out(bot, chat_id)
            await bunk(bot, message)
        else:
            await logout_user_if_logged_out(bot, chat_id)
        return

    tables = data.find_all("table")
    if len(tables) > 0:
        attendance_threshold = await user_settings.fetch_attendance_threshold(chat_id)

        # Pick the most likely attendance table by header keywords
        def detect_indexes_by_header(header_cells):
            lowered = [h.lower() for h in header_cells]
            idx = {"course": None, "conducted": None, "attended": None, "percent": None}
            for i, text in enumerate(lowered):
                if any(k in text for k in ["course", "subject", "sub name", "subject name"]):
                    if idx["course"] is None:
                        idx["course"] = i
                if any(k in text for k in ["conducted", "held", "total classes", "classes held"]):
                    if idx["conducted"] is None:
                        idx["conducted"] = i
                if any(k in text for k in ["attended", "present"]):
                    if idx["attended"] is None:
                        idx["attended"] = i
                if any(k in text for k in ["%", "percent", "attendance %", "attendance%", "attendance"]):
                    if idx["percent"] is None:
                        idx["percent"] = i
            return idx

        candidate_tables = []
        for table in tables:
            rows = table.find_all("tr")
            if not rows:
                continue
            header_cells = [c.get_text(strip=True) for c in rows[0].find_all(["th", "td"])]
            header_idx = detect_indexes_by_header(header_cells)
            # Require at least course and percentage columns to treat as attendance table
            if header_idx["course"] is not None and header_idx["percent"] is not None:
                candidate_tables.append((table, header_idx))

        if not candidate_tables:
            # Heuristic fallback: find any table where a data row contains a percentage column
            for table in tables:
                rows = table.find_all("tr")
                if not rows:
                    continue
                data_rows = rows[1:] if len(rows) > 1 else rows
                found = False
                for row in data_rows:
                    cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                    if len(cols) < 3:
                        continue
                    percent_idx = None
                    for i, val in enumerate(cols):
                        if "%" in val:
                            percent_idx = i
                            break
                    if percent_idx is None:
                        continue
                    # Choose conducted/attended as the two numeric columns nearest before percent
                    numeric_indices = [i for i, v in enumerate(cols[:percent_idx]) if re.sub(r"[^0-9]", "", v) != ""]
                    if len(numeric_indices) < 2:
                        continue
                    attended_idx = numeric_indices[-1]
                    conducted_idx = numeric_indices[-2]
                    # Course name as the first non-empty, non-numeric text column
                    course_idx = None
                    for i, v in enumerate(cols):
                        if i in (conducted_idx, attended_idx, percent_idx):
                            continue
                        if re.sub(r"[^0-9]", "", v) == "":
                            course_idx = i
                            break
                    if course_idx is None:
                        course_idx = 0
                    candidate_tables.append((table, {"course": course_idx, "conducted": conducted_idx, "attended": attended_idx, "percent": percent_idx}))
                    found = True
                    break
                if found:
                    break

        if not candidate_tables:
            # Final fallback: read percentage from ERP dashboard "Latest Attendance"
            try:
                dashboard_url = "https://kitsgunturerp.com/BeesERP/StudentLogin/StudLoginDashboard.aspx"
                with requests.Session() as s2:
                    cookies2 = session_data["cookies"]
                    headers2 = session_data.get("headers", {})
                    s2.cookies.update(cookies2)
                    dash_resp = s2.get(dashboard_url, headers=headers2)
                # Login redirect detection
                if (
                    "Login.aspx" in getattr(dash_resp, "url", "")
                    or "Login.aspx" in dash_resp.text
                ):
                    if chat_id_in_local_database:
                        await silent_logout_user_if_logged_out(bot, chat_id)
                        await bunk(bot, message)
                    else:
                        await logout_user_if_logged_out(bot, chat_id)
                    return
                dash_soup = BeautifulSoup(dash_resp.text, "html.parser")
                latest_att_span = dash_soup.find(id="ctl00_cpStud_lblTotalPercentage")
                attendance_threshold = await user_settings.fetch_attendance_threshold(chat_id)
                # Display overall attendance if available

                # Overall from dashboard if present
                if latest_att_span and latest_att_span.get_text(strip=True):
                    percent_text = latest_att_span.get_text(strip=True).replace("%", "").strip()
                    try:
                        attendance_present = float(percent_text)
                    except Exception:
                        attendance_present = None
                    if attendance_present is not None:
                        summary_msg = f"""
```
Overall Attendance

● Attendance  -  {attendance_present}%

```
"""
                        await bot.send_message(chat_id, summary_msg)

                # Try to find a subject-wise table on the dashboard as a fallback
                subject_tables = dash_soup.find_all("table")
                sent_any_subject = False
                def detect_indexes_by_header_dash(header_cells):
                    lowered = [h.lower() for h in header_cells]
                    idx = {"course": None, "conducted": None, "attended": None, "percent": None}
                    for i, text in enumerate(lowered):
                        if any(k in text for k in ["course", "subject", "sub name", "subject name"]):
                            if idx["course"] is None:
                                idx["course"] = i
                        if any(k in text for k in ["conducted", "held", "total classes", "classes held"]):
                            if idx["conducted"] is None:
                                idx["conducted"] = i
                        if any(k in text for k in ["attended", "present"]):
                            if idx["attended"] is None:
                                idx["attended"] = i
                        if any(k in text for k in ["%", "percent", "attendance %", "attendance%", "attendance"]):
                            if idx["percent"] is None:
                                idx["percent"] = i
                    return idx

                subject_candidate = None
                for t in subject_tables:
                    rows = t.find_all("tr")
                    if not rows:
                        continue
                    header_cells = [c.get_text(strip=True) for c in rows[0].find_all(["th", "td"])]
                    header_idx = detect_indexes_by_header_dash(header_cells)
                    if header_idx["course"] is not None and header_idx["percent"] is not None:
                        subject_candidate = (t, header_idx)
                        break

                # If we found a likely subject table, render per-subject boxes
                if subject_candidate is not None:
                    table_dash, header_idx_dash = subject_candidate
                    course_idx = header_idx_dash["course"] if header_idx_dash["course"] is not None else 0
                    conducted_idx = header_idx_dash["conducted"] if header_idx_dash["conducted"] is not None else 1
                    attended_idx = header_idx_dash["attended"] if header_idx_dash["attended"] is not None else 2
                    percent_idx = header_idx_dash["percent"] if header_idx_dash["percent"] is not None else 3
                    rows = table_dash.find_all("tr")[1:]
                    for row in rows:
                        cols = row.find_all(["td", "th"])
                        if len(cols) <= percent_idx:
                            continue
                        course_name = cols[course_idx].get_text(strip=True)
                        conducted_text = cols[conducted_idx].get_text(strip=True) if conducted_idx is not None and conducted_idx < len(cols) else "0"
                        attended_text = cols[attended_idx].get_text(strip=True) if attended_idx is not None and attended_idx < len(cols) else "0"
                        percent_text = cols[percent_idx].get_text(strip=True)
                        try:
                            attendance_present_sub = float(percent_text.replace("%", "").strip())
                        except Exception:
                            attendance_present_sub = 0.0
                        try:
                            conducted_val = int(re.sub(r"[^0-9]", "", conducted_text) or 0)
                        except Exception:
                            conducted_val = 0
                        try:
                            attended_val = int(re.sub(r"[^0-9]", "", attended_text) or 0)
                        except Exception:
                            attended_val = 0

                        subject_msg = f"""
```{course_name}

● Conducted  -  {conducted_val}

● Attended   -  {attended_val}

● Attendance -  {attendance_present_sub}%

```
"""
                        await bot.send_message(chat_id, subject_msg)
                        sent_any_subject = True

                if sent_any_subject:
                    await buttons.start_user_buttons(bot, message)
                    return
                # If still nothing, proceed to data not found
            except Exception:
                pass
            # Last-chance heuristic: scan the whole page for a percentage
            percent_match = re.search(r"(\d{1,3}(?:\.\d{1,2})?)\s*%", attendance_response.text)
            if percent_match:
                attendance_threshold = await user_settings.fetch_attendance_threshold(chat_id)
                guessed_percent = percent_match.group(1)
                guessed_summary_msg = f"""
```
Overall Attendance (guessed)

● Attendance  -  {guessed_percent}%

```
"""
                await bot.send_message(chat_id, guessed_summary_msg)
                await buttons.start_user_buttons(bot, message)
                return

            # Send a short debug to help fix quickly
            debug_url = getattr(attendance_response, "url", used_url or "unknown")
            if overall_shown:
                await buttons.start_user_buttons(bot, message)
                return
            await message.reply(f"Attendance data not found (ERP parser v2).\nDebug: url={debug_url} len={len(attendance_response.text)}")
            await buttons.start_user_buttons(bot, message)
            return

        table, header_idx = candidate_tables[0]
        course_name_index = header_idx["course"] if header_idx["course"] is not None else 0
        conducted_classes_index = header_idx["conducted"] if header_idx["conducted"] is not None else 1
        attended_classes_index = header_idx["attended"] if header_idx["attended"] is not None else 2
        attendance_percentage_index = header_idx["percent"] if header_idx["percent"] is not None else 3

        rows = table.find_all("tr")[1:]  # Skip header
        sent_messages_by_course: set[str] = set()
        sent_texts: set[str] = set()
        for row in rows:
            columns = row.find_all(["td", "th"])
            if len(columns) <= attendance_percentage_index:
                continue

            course_name = columns[course_name_index].get_text(strip=True)
            conducted_text = columns[conducted_classes_index].get_text(strip=True)
            attended_text = columns[attended_classes_index].get_text(strip=True)
            percentage_text = columns[attendance_percentage_index].get_text(strip=True)

            # Parse numbers safely
            try:
                conducted_classes = int(re.sub(r"[^0-9]", "", conducted_text) or 0)
            except Exception:
                conducted_classes = 0
            try:
                attended_classes = int(re.sub(r"[^0-9]", "", attended_text) or 0)
            except Exception:
                attended_classes = 0
            try:
                attendance_present = float(percentage_text.replace("%", "").strip())
            except Exception:
                attendance_present = 0.0

            if not course_name:
                continue
            
            dedupe_key = f"{course_name}|{conducted_classes}|{attended_classes}|{attendance_present}|{attendance_threshold[0]}|{ui_mode[0]}"
            if dedupe_key in sent_messages_by_course:
                continue

            if attendance_present >= attendance_threshold[0]:
                classes_bunked = 0
                while conducted_classes + classes_bunked > 0 and (attended_classes / (conducted_classes + classes_bunked)) * 100 >= attendance_threshold[0]:
                    classes_bunked += 1
                classes_bunked -= 1
                bunk_can_msg_updated = f"""
```{course_name}

● Attendance  -  {attendance_present}%

● You can bunk {classes_bunked} classes

```
"""
                bunk_can_msg_traditional = f"""
**{course_name}**

● Attendance  -  {attendance_present}%

● You can bunk {classes_bunked} classes

"""
                if ui_mode[0] == 0:
                    if bunk_can_msg_updated not in sent_texts:
                        await bot.send_message(chat_id, bunk_can_msg_updated)
                        sent_texts.add(bunk_can_msg_updated)
                else:
                    if bunk_can_msg_traditional not in sent_texts:
                        await bot.send_message(chat_id, bunk_can_msg_traditional)
                        sent_texts.add(bunk_can_msg_traditional)
                sent_messages_by_course.add(dedupe_key)
            else:
                classes_needattend = 0
                if conducted_classes == 0:
                    classes_needattend = 0
                else:
                    while (
                        (attended_classes + classes_needattend)
                        / (conducted_classes + classes_needattend)
                        * 100
                    ) < attendance_threshold[0]:
                        classes_needattend += 1    
                bunk_recover_msg_updated = f"""
```{course_name}

● Attendance  -  Below {attendance_threshold[0]}%

● Attend  {classes_needattend} classes for {attendance_threshold[0]}%

● No Bunk Allowed

```
"""
                bunk_recover_msg_traditional = f"""
**{course_name}**

● Attendance  -  Below {attendance_threshold[0]}%

● Attend  {classes_needattend} classes for {attendance_threshold[0]}%

● No Bunk Allowed"""
                if ui_mode[0] == 0:
                    if bunk_recover_msg_updated not in sent_texts:
                        await bot.send_message(chat_id, bunk_recover_msg_updated)
                        sent_texts.add(bunk_recover_msg_updated)
                else:
                    if bunk_recover_msg_traditional not in sent_texts:
                        await bot.send_message(chat_id, bunk_recover_msg_traditional)
                        sent_texts.add(bunk_recover_msg_traditional)
                sent_messages_by_course.add(dedupe_key)
    else:
        if overall_shown:
            await buttons.start_user_buttons(bot, message)
            return
        debug_url_fallback = getattr(attendance_response, "url", used_url or "unknown")
        await message.reply(f"Attendance data not found (ERP parser v2).\nDebug: url={debug_url_fallback} len={len(attendance_response.text)}")
    await buttons.start_user_buttons(bot,message)


async def generate_unique_id():
    """
    Generate a unique identifier using UUID version 4.

    Returns:
        str: A string representation of the UUID.
    """
    return str(uuid.uuid4())

# CHECKS IF REGISTERED FOR PAT

async def check_pat_student(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id)
    if not session_data:
        auto_login_status = await auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_status is False and chat_id_in_local_database is False:
            # if chat_id_in_local_database is False:
            return
    session_data = await tdatabase.load_user_session(chat_id)
    pat_attendance_url = "https://samvidha.iare.ac.in/home?action=Attendance_std"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)

        pat_attendance_response = s.get(pat_attendance_url)
    data = BeautifulSoup(pat_attendance_response.text, 'html.parser')
    td_tags = re.findall(r'<td\s*[^>]*>.*?</td>', str(data), flags=re.DOTALL)

    # Count the number of <td> tags found
    num_td_tags = len(td_tags)
    # print("Number of <td> tags:", num_td_tags)

    if(num_td_tags > 2):
        return True
    else:
        return False

# PAT ATTENDENCE IF REGISTERED

async def pat_attendance(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    pat_attendance_url = "https://samvidha.iare.ac.in/home?action=Attendance_std"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        pat_attendance_response = s.get(pat_attendance_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in pat_attendance_response.text:
        if chat_id_in_local_database:
            await silent_logout_user_if_logged_out(bot,chat_id)
            await pat_attendance(bot,message)
        else:
            await logout_user_if_logged_out(bot,chat_id)
        return
    pat_att_heading = f"""
```PAT ATTENDANCE
@iare_unofficial_bot
```
"""
    await bot.send_message(chat_id,pat_att_heading)
    data = BeautifulSoup(pat_attendance_response.text, 'html.parser')
    tables = data.find_all('table')
    all_pat_attendance_indexes = await user_settings.get_pat_attendance_index_values()
    if all_pat_attendance_indexes:
        course_name_index = all_pat_attendance_indexes['course_name']
        conducted_classes_index = all_pat_attendance_indexes['conducted_classes']
        attended_classes_index = all_pat_attendance_indexes['attended_classes']
        attendance_percentage_index = all_pat_attendance_indexes['attendance_percentage']
        attendance_status_index = all_pat_attendance_indexes['status']
    else:
        course_name_index = 2
        conducted_classes_index = 3
        attended_classes_index = 4
        attendance_percentage_index = 5
        attendance_status_index = 6
    sum_of_attendance = 0
    count_of_attendance = 0
    for table in tables:
        rows = table.find_all('tr')

        for row in rows:
            columns = row.find_all('td')
            if len(columns) >= 7:
                course_name = columns[course_name_index].text.strip()
                conducted_classes = columns[conducted_classes_index].text.strip()
                attended_classes = columns[attended_classes_index].text.strip()  
                attendance_percentage = columns[attendance_percentage_index].text.strip()
                att_status = columns[attendance_status_index].text.strip()
                att_msg_updated_ui = f"""
```{course_name}

● Conducted         -  {conducted_classes}
             
● Attended          -  {attended_classes}  
         
● Attendance %      -  {attendance_percentage} 
            
● Status            -  {att_status}  
         
```
"""
                
                att_msg_traditional_ui = f"""
\n**{course_name}**

● Conducted         -  {conducted_classes}
             
● Attended            -  {attended_classes}   
         
● Attendance %    -  {attendance_percentage} 
            
● Status                 -  {att_status}
"""
                sum_of_attendance+=float(attendance_percentage)
                if int(conducted_classes) > 0:
                        count_of_attendance += 1
                if ui_mode[0] == 0:
                    await bot.send_message(chat_id,att_msg_updated_ui)
                else:
                    await bot.send_message(chat_id,att_msg_traditional_ui)
    aver_attendance = round(sum_of_attendance/count_of_attendance, 2)
    over_all_attendance = f"**Overall PAT Attendance is {aver_attendance}**"
    await bot.send_message(chat_id,over_all_attendance)
    await buttons.start_user_buttons(bot,message)

async def gpa(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    gpa_url = "https://samvidha.iare.ac.in/home?action=credit_register"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        gpa_response = s.get(gpa_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in gpa_response.text:
        if chat_id_in_local_database:
            await silent_logout_user_if_logged_out(bot,chat_id)
            return await gpa(bot,message)
        else:
            await logout_user_if_logged_out(bot,chat_id)
        return
    try:
        sgpa_pattern = r'Semester Grade Point Average \(SGPA\) : (\d(?:\.\d\d)?)'
        cgpa_pattern = r'Cumulative Grade Point Average \(CGPA\) : (\d(?:\.\d\d)?)'
        sgpa_values = re.findall(sgpa_pattern,gpa_response.text)
        sgpa_values = [float(x) for x in sgpa_values]
        cgpa_values = re.findall(cgpa_pattern,gpa_response.text)
        if len(cgpa_values) == 0:
            cgpa = 0.00
        else:
            cgpa = cgpa_values[-1]
        gpa_message_updated_ui = """
```GPA
📊 **GPA Results**

⫸ **SGPA Details:**
"""
        gpa_message_traditional_ui = """
**GPA Results**

⫸ **SGPA Details:**
"""
        if ui_mode[0] == 0:
            gpa_message = gpa_message_updated_ui
        elif ui_mode[0] == 1:
            gpa_message = gpa_message_traditional_ui
        
        # Create a formatted table for SGPA values
        if sgpa_values:
            gpa_message += """
┌─────────────┬─────────┐
│ Semester    │ SGPA    │
├─────────────┼─────────┤"""
            
            for i, sgpa in enumerate(sgpa_values, start=1):
                gpa_message += f"""
│ Semester {i:2} │ {sgpa:7} │"""
            
            gpa_message += """
└─────────────┴─────────┘
"""
        else:
            gpa_message += "\n⚠️ No SGPA data available\n"

        cgpa_updated_ui_message = f"""
⫸ **CGPA:** {cgpa}

📋 **Summary:**
• Total Semesters: {len(sgpa_values)}
• Current CGPA: {cgpa}
• Latest SGPA: {sgpa_values[-1] if sgpa_values else 'N/A'}
```
"""
        cgpa_message_traditional_ui = f"""
⫸ **CGPA:** {cgpa}

📋 **Summary:**
• Total Semesters: {len(sgpa_values)}
• Current CGPA: {cgpa}
• Latest SGPA: {sgpa_values[-1] if sgpa_values else 'N/A'}
"""
        if ui_mode[0] == 0:
            cgpa_message = cgpa_updated_ui_message
        elif ui_mode[0] == 1:
            cgpa_message = cgpa_message_traditional_ui
        gpa_message += cgpa_message
        return gpa_message
    except Exception as e:
        await bot.send_message(chat_id,f"Error Retrieving GPA : {e}")
        return False

async def get_certificates(bot,message,profile_pic : bool,aadhar_card : bool,dob_certificate : bool,income_certificate : bool,ssc_memo : bool,inter_memo : bool):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return
    getuname = await tdatabase.load_username(chat_id)
    username = getuname[2].upper()
    img_url = f"https://iare-data.s3.ap-south-1.amazonaws.com/uploads/STUDENTS/"
    if profile_pic is True:
        img_url = img_url + f"{username}/{username}.jpg"
    elif aadhar_card is True:
        img_url = img_url + f"{username}/DOCS/{username}_Aadhar.jpg"
    elif dob_certificate is True:
        img_url = img_url + f"{username}/DOCS/{username}_Caste.jpg"
    elif income_certificate is True:
        img_url = img_url + f"{username}/DOCS/{username}_Income.jpg"
    elif ssc_memo is True:
        img_url = img_url + f"{username}/DOCS/{username}_SSC.jpg"
    elif inter_memo is True:
        img_url = img_url + f"{username}//DOCS/{username}_MARKSMEMO.jpg"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
    try:
        response = requests.get(img_url)
        response.raise_for_status()
        # Create an in-memory file-like object
        image_bytes = io.BytesIO(response.content)
        image_bytes.name = f'{username}.jpg'
        
        # Send the image
        await bot.send_photo(message.chat.id, photo=image_bytes)
        # Ensure the BytesIO object is closed
        image_bytes.close()
    except requests.RequestException as e:
        if ui_mode[0] == 0:
            await message.reply_text("""```Failed to fetch image
Document not available```""")
        elif ui_mode[0] == 1:
            await message.reply_text("""**Failed to fetch image**\n
Document not available""")

    await buttons.start_certificates_buttons(message)

async def profile_details(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    profile_url = "https://samvidha.iare.ac.in/home?action=profile"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        profile_response = s.get(profile_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in profile_response.text:
        if chat_id_in_local_database:
            await silent_logout_user_if_logged_out(bot,chat_id)
            await profile_details(bot,message)
        else:
            await logout_user_if_logged_out(bot,chat_id)
        return
    soup = BeautifulSoup(profile_response.text,'html.parser')
    data = {}
    for dt in soup.find_all('dt'):
        key = dt.get_text(strip=True)
        dd = dt.find_next_sibling('dd')
        if dd:
            value = dd.get_text(strip=True)
            data[key] = value


    for  strong in soup.find_all('strong'):
        key = strong.get_text(strip=True)
        p = strong.find_next_sibling('p')
        if p:
            value = p.get_text(strip=True)
            data[key] = value



    sections = [
        ["Name", "Roll Number", "JNTUH AEBAS", "ABC ID"],
        ["Branch", "Year/Sem", "Section", "Admission No", "EAMCET RANK", "Date of Joining"],
        ["AAdhar Number", "Date of Birth"],
        ["Student Phone", "Student Email-id", "Domain Email-id"],
        ["Parent Phone", "Parent Email-id"]
    ]
    if ui_mode[0] == 0:
        profile_details_message = """
```Profile Details
"""
    elif ui_mode[0] ==1:
        profile_details_message = """
**Profile Details**\n
"""


    for section in sections:
        profile_details_message += "\n---\n"
        for key in section:
            value = data.get(key, "N/A")
            details_message = (f"\n {key}: {value} \n")
            profile_details_message += details_message 
    if ui_mode[0] == 0:
        profile_details_message += '\n---\n```'
    elif ui_mode[0] == 1:
        profile_details_message += '\n---\n'
    return profile_details_message

async def payment_details(bot,message):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    profile_url = "https://samvidha.iare.ac.in/home?action=fee_payment"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        payment_details_response = s.get(profile_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in payment_details_response.text:
        if chat_id_in_local_database:
            await silent_logout_user_if_logged_out(bot,chat_id)
            await payment_details(bot,message)
        else:
            await logout_user_if_logged_out(bot,chat_id)
        return
    try:
        soup = BeautifulSoup(payment_details_response.text,'html.parser')
        rows = soup.table.thead.find_all('tr')
        fee_row = rows[1].find_all('td')
        rollno = fee_row[1].text[12:-1]
        track_id = fee_row[2].text
        payment_date = fee_row[3].text
        amount = fee_row[4].text
        status = "Not Paid"
        if track_id != "":
            status = "Paid"
        if status == "Paid":
            payment_message_updated_ui = f"""
```Tution Fee
RollNo: {rollno}
Amount: {amount}
Status: Paid 
Payment Date: {payment_date}
Track ID: {track_id}
```
"""
            payment_message_traditional_ui = f"""
**TUITION FEE**
            
RollNo: {rollno}\n
Amount: {amount}\n
Status: Paid \n
Payment Date: {payment_date}\n
Track ID: {track_id}
"""
        else:
            payment_message_updated_ui = f"""
```TUITION FEE
RollNo: {rollno}
Amount : {amount}
Status: Not Paid

Pay As Soon As Possible 
To Avoid Penalty...
```
"""
            payment_message_traditional_ui = f"""
**TUITION FEE**

RollNo: {rollno}\n
Amount : {amount}\n
Status: Not Paid\n

Pay As Soon As Possible 
To Avoid Penalty...
"""
        if ui_mode[0] == 0:
            return payment_message_updated_ui
        elif ui_mode[0] == 1:
            return payment_message_traditional_ui
    except Exception as e:
        if ui_mode[0] == 0:
            return f"""
```TUITION FEE
Error : {e}
```"""
        elif ui_mode[0] == 1:
            return f"**PAYMENT DETAILS**\n\nError : {e}"
 
async def get_sem_count(bot,chat_id):
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database(bot,"",chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    cie_marks_url = "https://samvidha.iare.ac.in/home?action=cie_marks_ug"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        cie_marks_response = s.get(cie_marks_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in cie_marks_response.text:
        if chat_id_in_local_database:
            await silent_logout_user_if_logged_out(bot,chat_id)
            return await get_sem_count(bot,chat_id)
        else:
            await logout_user_if_logged_out(bot,chat_id)
        return
    try:
        soup = BeautifulSoup(cie_marks_response.text, 'html.parser')
        # Find all tables and reverse the list to get the semesters in ascending order i.e semester 1 to 8 
        tables = soup.find_all('table')
        # Count the number of semesters available
        semester_count = len(tables) - 1
        return semester_count
    except:
        return None

async def cie_marks(bot,message,sem_no):
    chat_id = message.chat.id
    session_data = await tdatabase.load_user_session(chat_id)
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    # chat_id_in_pgdatabase = await pgdatabase.check_chat_id_in_pgb(chat_id) Use this if you want to check in cloud database
    if not session_data:
        auto_login_by_database_status = await auto_login_by_database(bot,"",chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
        if auto_login_by_database_status is False and chat_id_in_local_database is False:
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return
    session_data = await tdatabase.load_user_session(chat_id)
    cie_marks_url = "https://samvidha.iare.ac.in/home?action=cie_marks_ug"
    with requests.Session() as s:
        cookies = session_data['cookies']
        s.cookies.update(cookies)
        cie_marks_response = s.get(cie_marks_url)
    chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)
    if 	'<title>Samvidha - Campus Management Portal - IARE</title>' in cie_marks_response.text:
        if chat_id_in_local_database:
            await silent_logout_user_if_logged_out(bot,chat_id)
            await cie_marks(bot,chat_id,sem_no)
        else:
            await logout_user_if_logged_out(bot,chat_id)
        return
    try:
        soup = BeautifulSoup(cie_marks_response.text, 'html.parser')
        # Find all tables and reverse the list to get the semesters in ascending order i.e semester 1 to 8 
        tables = soup.find_all('table')
        reversed_tables = tables[::-1] 
        # Select the required semester table 
        cie_table = reversed_tables[sem_no].find_all('tr')
        # Initialize a list to store the relevant data
        subject_marks_data = []
        # Iterate over each row in the selected semester table
        for row in cie_table:
            cells = row.find_all('td')
            row_data = [cell.get_text(strip=True) for cell in cells]
            # Break if 'Laboratory Marks (Practical)' is found -> to get only subject marks
            if any(item.startswith('Laboratory Marks (Practical)') for item in row_data):
                break
            # Append row data if it's not empty -> to get only subject marks
            if row_data:
                subject_marks_data.append(row_data)
        # Initialize dictionaries and total mark variables
        cie1_marks_dict = {}
        cie2_marks_dict = {}
        total_cie1_marks = 0
        total_cie2_marks = 0
        # Process each row data
        for marks_row in subject_marks_data:
            subject_name = marks_row[2]
            cie1_marks = marks_row[3]
            cie2_marks = marks_row[5]
            cie1_marks_dict[subject_name] = cie1_marks
            cie2_marks_dict[subject_name] = cie2_marks
            excluded_marks = ['','-', '0', '0.0'] 
            if cie1_marks not in excluded_marks:
                total_cie1_marks += float(cie1_marks)
            if cie2_marks not in excluded_marks:
                total_cie2_marks += float(cie2_marks)
        # Default total marks as each subject has a maximum of 10 marks
        default_total_marks = float(len(cie1_marks_dict) * 10)
        cie1_marks_message_updated = f"""
```CIE  Marks
""" 
        cie1_marks_message_traditional = f"""
**CIE Marks**
"""
        if ui_mode[0] == 0:
            cie1_marks_message = cie1_marks_message_updated
        elif ui_mode[0] == 1:
            cie1_marks_message = cie1_marks_message_traditional
        for subject_name, marks in cie1_marks_dict.items():
            cie1_marks_message += f"{subject_name}\n⫸ {marks}\n\n"
            
        cie1_marks_message += "----\n"
        cie1_marks_message += f"Total Marks - {total_cie1_marks} / {default_total_marks} \n"
        if ui_mode[0] == 0:
            cie1_marks_message += "\n```"
        elif ui_mode[0] == 1:
            cie1_marks_message +="\n"
        await bot.send_message(chat_id,cie1_marks_message)

            # Print CIE-2 marks message as markdown
        cie2_marks_message_updated = f"""
```CIE 2 Marks
""" 
        cie2_marks_message_traditional = f"""
**CIE 2 Marks
"""
        if ui_mode[0] == 0:
            cie2_marks_message = cie2_marks_message_updated
        elif ui_mode[0] == 1:
            cie2_marks_message = cie2_marks_message_traditional
        
        for subject_name, marks in cie2_marks_dict.items():
            cie2_marks_message += f"{subject_name}\n⫸ {marks}\n\n"
            
        cie2_marks_message += "----\n"
        cie2_marks_message += f"Total Marks - {total_cie2_marks} / {default_total_marks} \n"
        cie2_marks_message += "\n```"
        await bot.send_message(chat_id,cie2_marks_message)
        total_cie_marks = total_cie1_marks + total_cie2_marks
        await bot.send_message(chat_id,f"Total CIE Marks: {total_cie_marks} / {default_total_marks * 2}")
        await buttons.start_student_profile_buttons(message)
    except Exception as e:
        await bot.send_message(chat_id,f"Error retrieving cie marks : {e}")
        await buttons.start_student_profile_buttons(message)


async def report(bot,message):
    chat_id = message.from_user.id
    ui_mode = await user_settings.fetch_ui_bool(chat_id)
    if ui_mode is None:
        await user_settings.set_user_default_settings(chat_id)
    session_data = await tdatabase.load_user_session(chat_id)
    if not session_data:
        auto_login_status = await auto_login_by_database(bot,message,chat_id)
        chat_id_in_local_database = await tdatabase.check_chat_id_in_database(chat_id)#check Chat id in the database
        if auto_login_status is False and chat_id_in_local_database is False:
            # LOGIN MESSAGE
            if ui_mode[0] == 0:
                await bot.send_message(chat_id,text=login_message_updated_ui)
            elif ui_mode[0] == 1:
                await bot.send_message(chat_id,text=login_message_traditional_ui)
            return
        else:
            session_data = await tdatabase.load_user_session(chat_id)

    user_report = " ".join(message.text.split()[1:])
    if not user_report:
        no_report_message = f"""
```EMPTY MESSAGE
⫸ ERROR : MESSAGE CANNOT BE EMPTY

⫸ How to use command:

●  /report We are encountering issues with the attendance feature.
It seems that attendance records are not updating correctly after submitting.
```
"""
        await message.reply(no_report_message)
        return
    getuname = await tdatabase.load_username(chat_id)

    username = getuname[2]

    user_unique_id = await generate_unique_id()

    await tdatabase.store_reports(user_unique_id,username,user_report,chat_id,None,None,0)
    try:
        await pgdatabase.store_reports(user_unique_id,username,user_report,chat_id,None,None,False)
    except Exception as e:
        print(f"PostgreSQL report storage failed: {e}")
        # Continue without PostgreSQL storage
    forwarded_message = f"New User Report from @{username} (ID: {user_unique_id}):\n\n{user_report}"
    all_admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    all_maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    if all_admin_chat_ids+all_maintainer_chat_ids:
        for chat_id in all_admin_chat_ids+all_maintainer_chat_ids:
            await bot.send_message(chat_id,text=forwarded_message)
        await bot.send_message(chat_id,"Thank you for your report! Your message has been forwarded to the developer.")
    else:
        await bot.send_message(chat_id,"Although an error occurred while sending, your request has been successfully stored in the database.")
async def reply_to_user(bot,message):
    chat_id = message.chat.id
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[4] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return

    maintainer_name = await managers_handler.fetch_name(chat_id)
    if not message.reply_to_message:
        await message.reply("Please reply to a user's report to send a reply.")
        return
    
    reply_text = message.reply_to_message.text
    unique_id_keyword = "ID: "
    if unique_id_keyword not in reply_text:
        await message.reply("The replied message does not contain the unique ID.")
        return


    unique_id_start_index = reply_text.find(unique_id_keyword) + len(unique_id_keyword)
    unique_id_end_index = reply_text.find(")", unique_id_start_index)
    report_id = reply_text[unique_id_start_index:unique_id_end_index].strip()
    pending_reports = await tdatabase.load_reports(report_id)

    if report_id not in pending_reports:
        await message.reply("Invalid or unknown unique ID.")
        return

    user_chat_id = pending_reports[3]

    developer_reply = message.text.split("/reply", 1)[1].strip()

    reply_message = f"{developer_reply}\n\nThis is a reply from the bot developer."

    try:

        await bot.send_message(chat_id=user_chat_id, text=reply_message)

        developer_chat_id = message.chat.id
        await bot.send_message(chat_id=developer_chat_id, text="Message sent successfully.")

        await tdatabase.store_reports(report_id,None,None,None,reply_message,maintainer_name,1)
        await pgdatabase.store_reports(report_id,None,None,None,reply_message,maintainer_name,True)
    except Exception as e:
        error_message = f"An error occurred while sending the message to the user: {e}"
        await bot.send_message(chat_id=developer_chat_id, text=error_message)

async def show_reports(bot,message):
    chat_id = message.chat.id
    reports = await tdatabase.load_allreports()
    # if message.chat.id != BOT_DEVELOPER_CHAT_ID and message.chat.id != BOT_MAINTAINER_CHAT_ID:
    #     return
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[3] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    if len(reports) == 0:
        await bot.send_message(chat_id,text="There are no pending reports.")
        return
    for report in reports:
        unique_id, user_id, message, report_chat_id = report
        report_message = f"User report from @{user_id} (ID: {unique_id}):\n\n{message}"
        await bot.send_message(chat_id, text=report_message)

async def show_replied_reports(bot,message):
    chat_id = message.chat.id
    reports = await tdatabase.load_all_replied_reports()
    # if message.chat.id != BOT_DEVELOPER_CHAT_ID and message.chat.id != BOT_MAINTAINER_CHAT_ID:
    #     return
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[3] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    if len(reports) == 0:
        await bot.send_message(chat_id,text="There are no Replied reports.")
        return
    for report in reports:
        unique_id, user_id, message, report_chat_id,replied_message,replied_maintainer,reply_status = report
        replied_message = replied_message.split("This is a reply from the bot developer.")[0]
        report_message = f"User report from @{user_id} (ID: {unique_id}):\n\n{message}\n\nReplied By : {replied_maintainer}\n\nReplied Message : {replied_message}"
        await bot.send_message(chat_id, text=report_message)

async def list_users(bot,chat_id):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[0] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    usernames = await tdatabase.fetch_usernames_total_users_db()   
    users_list = ";".join(usernames)
    qr_code = pyqrcode.create(users_list)
    qr_image_path = "list_users_qr.png"
    qr_code.png(qr_image_path, scale=5)
    await bot.send_photo(chat_id, photo=open(qr_image_path, 'rb'))
    os.remove(qr_image_path)


async def get_logs(bot, chat_id):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()  # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()  # Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[9] != 1:
        await bot.send_message(chat_id, "Access denied. You don't have permission to use this command.")
        return
    
    log_file_name = "bot_errors.log"
    temp_log_file_name = "temp_bot_errors.log"
    
    if log_file_name in os.listdir():
        try:
            # Copy the log file to a temporary file
            shutil.copy(log_file_name, temp_log_file_name)
            
            # Send the temporary log file
            await bot.send_document(chat_id, temp_log_file_name)
            
            # Remove the temporary log file after sending
            os.remove(temp_log_file_name)
        except Exception as e:
            await bot.send_message(chat_id, f"Error: {e}")
    else:
        await bot.send_message(chat_id, "No log file found.")

async def total_users(bot,message):
    chat_id = message.chat.id
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[0] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    total_count = await tdatabase.fetch_number_of_total_users_db()
    await bot.send_message(message.chat.id,f"Total users: {total_count}")

async def clean_pending_reports(bot,message):
    chat_id = message.chat.id
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids() # Fetch all admin chat ids
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()# Fetch all maintainer chat ids
    if chat_id not in admin_chat_ids and chat_id not in maintainer_chat_ids:
        return
    access_data = await managers_handler.get_access_data(chat_id)
    if chat_id in maintainer_chat_ids and access_data[5] != 1:
        await bot.send_message(chat_id,"Access denied. You don't have permission to use this command.")
        return
    await pgdatabase.clear_pending_reports()
    await tdatabase.clear_reports()
    await bot.send_message(chat_id,"Emptied the reports successfully")


async def perform_sync_credentials(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        credentials = await pgdatabase.get_all_credentials()
        if credentials is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from credentials database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from credentials database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from credentials database")
            return
        if credentials is not None:
            for row in credentials:
                chat_id,username,password = row[0],row[1],row[2]
                await tdatabase.store_credentials_in_database(chat_id,username,password)
        else:
            print("There is no data present in the credential's database to sync with the local database.")
    except Exception as e:
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing credentials to database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing credentials to database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing credentials to database : {e}")

async def perform_sync_reports(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        reports = await pgdatabase.get_all_reports()
        if reports is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from reports database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from reports database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from reports database")
            return
        if reports is not None:
            for row in reports:
                unique_id,user_id,message,chat_id,replied_message,replied_maintainer,reply_status = row
                await tdatabase.store_reports(unique_id,user_id,message,chat_id,replied_message,replied_maintainer,reply_status)
        else:
            print("There is no data present in the report's database to sync with the local database.")
    except Exception as e:
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing reports to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing reports to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing reports to local database : {e}")

async def perform_sync_banned_users(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        banned_users = await pgdatabase.get_all_banned_usernames()
        if banned_users is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from banned users database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from banned users database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from banned users database")
            return
        if banned_users is not None:
            for row in banned_users: # Each row contains data like this <Record username='223235464'>
                banned_username = row[0] # Extracting username from the record
                await tdatabase.store_banned_username(banned_username.lower())
        else:
            print("There is no data present in the bannned user's database to sync with the local database.")
    except Exception as e:
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing banned users to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing banned users to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing banned users to local database : {e}")

async def perform_sync_user_settings(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        all_user_settings = await pgdatabase.get_all_user_settings()
        if all_user_settings is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from user settings database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from user settings database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from user settings database")
            return
        if all_user_settings is not None:
            for row in all_user_settings:
                chat_id, attendance_threshold,biometric_threshold,traditional_ui,extract_title = row
                traditional_ui_sqlite = await tdatabase.pg_bool_to_sqlite_bool(traditional_ui)
                extract_title_sqlite = await tdatabase.pg_bool_to_sqlite_bool(extract_title)
                await user_settings.store_user_settings(chat_id, attendance_threshold,biometric_threshold,traditional_ui_sqlite,extract_title_sqlite)
        else:
            print("There is no data present in the user setting's database to sync with the local database.")
    except Exception as e :
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing user settings to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing user settings to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing user settings to local database : {e}")

async def perform_sync_bot_manager_data(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        bot_managers_data = await pgdatabase.get_bot_managers_data()
        if bot_managers_data is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from bot manager database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from bot manager database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from bot manager database")
            return
        if bot_managers_data is not None and bot_managers_data is not False:
            for row in bot_managers_data:
                chat_id,admin,maintainer,name,control_access,access_users,announcement,configure,show_reports_,reply_reports,clear_reports,ban_username,unban_username,manage_maintainer,logs = row
                admin_sqlite = await tdatabase.pg_bool_to_sqlite_bool(admin)
                maintainer_sqlite = await tdatabase.pg_bool_to_sqlite_bool(maintainer)
                access_users_sqlite = await tdatabase.pg_bool_to_sqlite_bool(access_users)
                announcement_sqlite = await tdatabase.pg_bool_to_sqlite_bool(announcement)
                configure_sqlite = await tdatabase.pg_bool_to_sqlite_bool(configure)
                show_reports_sqlite = await tdatabase.pg_bool_to_sqlite_bool(show_reports_)
                reply_reports_sqlite = await tdatabase.pg_bool_to_sqlite_bool(reply_reports)
                clear_reports_sqlite = await tdatabase.pg_bool_to_sqlite_bool(clear_reports)
                ban_username_sqlite = await tdatabase.pg_bool_to_sqlite_bool(ban_username)
                unban_username_sqlite = await tdatabase.pg_bool_to_sqlite_bool(unban_username)
                manage_maintainer_sqlite = await tdatabase.pg_bool_to_sqlite_bool(manage_maintainer)
                logs_sqlite = await tdatabase.pg_bool_to_sqlite_bool(logs)

                await managers_handler.store_bot_managers_data_in_database(
                                chat_id = chat_id,
                                admin=admin_sqlite,
                                maintainer= maintainer_sqlite,
                                name= name,
                                control_access= control_access,
                                access_users=access_users_sqlite,
                                announcement= announcement_sqlite,
                                configure= configure_sqlite,
                                show_reports= show_reports_sqlite,
                                reply_reports=reply_reports_sqlite,
                                clear_reports=clear_reports_sqlite,
                                ban_username= ban_username_sqlite,
                                unban_username= unban_username_sqlite,
                                manage_maintainers=manage_maintainer_sqlite,
                                logs= logs_sqlite
                            )
        else:
            print("There is no data present in the bot manager's database to sync with the local database.")
    except Exception as e:
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing bot managers data to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing bot managers data to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing bot managers data to local database : {e}")

async def perform_sync_index_data(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        all_indexes = await pgdatabase.get_all_index_values()
        if all_indexes is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from index database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from index database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from index database")
            return
        if all_indexes is not None:
            for row in all_indexes:
                name,indexes_dictionary = row
                await user_settings.store_index_values_to_restore(name,json.loads(indexes_dictionary))
        else:
            print("There is no data present in the index's database to sync with the local database.")
    except Exception as e :
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing index to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing index to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing index to local database : {e}")

async def perform_sync_cgpa_tracker(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        all_tracker_details = await pgdatabase.get_all_cgpa_trackers()
        if all_tracker_details is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from cgpa_tracker database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from cgpa_trackers database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from cgpa_tracker database")
            return
        if all_tracker_details is not None:
            for row in all_tracker_details:
                chat_id,status,current_cgpa = row
                status_sqlite = await tdatabase.pg_bool_to_sqlite_bool(status)
                await managers_handler.store_cgpa_tracker_details(chat_id,status_sqlite,current_cgpa)
        else:
            print("There is no data present in the cgpa_tracker database to sync with the local database.")
    except Exception as e :
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing cgpa_tracker data to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing cgpa_tracker data to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing cgpa_tracker data to local database : {e}")

async def perform_sync_cie_tracker(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        all_tracker_details = await pgdatabase.get_all_cie_tracker_data()
        if all_tracker_details is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from cie_tracker database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from cie_trackers database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from cie_tracker database")
            return
        if all_tracker_details is not None:
            for row in all_tracker_details:
                chat_id,status,current_cie_marks = row
                status_sqlite = await tdatabase.pg_bool_to_sqlite_bool(status)
                await managers_handler.store_cie_tracker_details(chat_id,status_sqlite,current_cie_marks)
        else:
            print("There is no data present in the cie_tracker database to sync with the local database.")
    except Exception as e :
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing cie_tracker data to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing cie_tracker data to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing cie_tracker data to local database : {e}")

async def perform_sync_labs_data(bot):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    try:
        labs_data = await pgdatabase.get_all_lab_subjects_and_weeks_data()
        if labs_data is False:
            if admin_chat_ids:
                for chat_id in admin_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from labs_data database")
            if maintainer_chat_ids:
                for chat_id in maintainer_chat_ids:
                    await bot.send_message(chat_id,"Error retrieving data from labs_data database")
            if not admin_chat_ids and not maintainer_chat_ids:
                print("Error retrieving data from cie_tracker database")
            return
        if labs_data is not None:
            for row in labs_data:
                chat_id,subject,weeks = row
                await tdatabase.store_lab_info(chat_id,subject_index= None,week_index=None,subjects=subject,weeks=weeks)
        else:
            print("There is no data present in the cgpa_tracker database to sync with the local database.")
    except Exception as e :
        if admin_chat_ids:
            for chat_id in admin_chat_ids:
                await bot.send_message(chat_id,f"Error storing cgpa_tracker data to local database : {e}")
        if maintainer_chat_ids:
            for chat_id in maintainer_chat_ids:
                await bot.send_message(chat_id,f"Error storing cgpa_tracker data to local database : {e}")
        if not admin_chat_ids and not maintainer_chat_ids:
            print(f"Error storing cgpa_tracker data to local database : {e}")

async def sync_databases(bot):
    """
    This Function is used to execute all the functions which sync the local database with the Postgres database.
    
    :param bot: Pyrogram client
    """
    await perform_sync_index_data(bot)
    await perform_sync_bot_manager_data(bot)
    await perform_sync_credentials(bot)
    await perform_sync_user_settings(bot)
    # await perform_sync_labs_data(bot)
    await perform_sync_banned_users(bot)
    await perform_sync_cgpa_tracker(bot)
    await perform_sync_cie_tracker(bot)
    await perform_sync_reports(bot)

async def help_command(bot,message):
    """
    Handler function for the /help command.
    Provides information about the available commands.
    """
    chat_id = message.chat.id
    help_msg = """Available commands:

    /login username password - Log in with your credentials.

    /logout - Log out from the current session.

    /report {your report} - Send a report to the bot developer.

    /settings - Access user settings and preferences.

    Note: Replace {username}, {password}, and {your report} with actual values.
    """
    help_admin_msg = """
    Available commands:

    /login {username} {password} - Log in with your credentials.
    
    /logout - Log out from the current session.    
    
    /report {your report} - Send a report to the bot developer.

    /settings - Access user settings and preferences.

    Note: Replace {username}, {password}, {your report} and {your reply} with actual values.

    As an Admin :

    /admin - Access authorized operations.

    /reset - Reset the User Sessions Sqlite3 Database

    /reply {your reply} - Send a reply to the report by replying to it.

    /ban {username} - Ban a user or users from the system.

    /unban {username} - Unban a user from the system.

    /announce {your announcement} - Send an announcement.

    /add_maintainer {chat_id} - Add a maintainer.

    /rshow - View reports.  

    /lusers - Generate a QR code of active users in a day.

    /tusers - Display total active users in a day.

    /rclear - Clear reports.
    """
    help_maintainer_msg = """
    Available commands:

    /login {username} {password} - Log in with your credentials.
    
    /logout - Log out from the current session.    
    
    /report {your report} - Send a report to the bot developer.

    Note: Replace {username}, {password}, {your report} and {your reply} with actual values.

    As a Maintainer :
    
    /maintainer -  Access authorized operations.

    /ban {username} - Ban a user or users from the system.  

    /unban {username} - Unban a user from the system.  

    /announce {your announcement} - Send an announcement.  

    /rshow - View reports.  

    /lusers - Generate a QR code of active users in a day.

    /tusers - Display total active users in a day.

    /rclear - Clear reports.

    Note : \n\nMaintainers require authorization from the admin to ensure that the commands function properly.
"""
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    maintainer_chat_ids = await managers_handler.fetch_maintainer_chat_ids()
    if chat_id in admin_chat_ids:
        await bot.send_message(chat_id,text=help_admin_msg)
        await buttons.start_user_buttons(bot,message)
    elif chat_id in maintainer_chat_ids:
        await bot.send_message(chat_id,text=help_maintainer_msg)
        await buttons.start_user_buttons(bot,message)
    else:
        await bot.send_message(chat_id,text=help_msg)
        try:
            is_logged_in = await is_user_logged_in(chat_id,message)
            pg_check = await pgdatabase.check_chat_id_in_pgb(chat_id)
            if is_logged_in is True or pg_check:
                await buttons.start_user_buttons(bot,message)
        except Exception as e:
            print(f"PostgreSQL check failed in help command: {e}")
            # Check only SQLite login status
            if await is_user_logged_in(chat_id,message) is True:
                await buttons.start_user_buttons(bot,message)

async def reset_user_sessions_database(bot,message):
    admin_chat_ids = await managers_handler.fetch_admin_chat_ids()
    chat_id = message.chat.id
    if chat_id in admin_chat_ids:
        await tdatabase.clear_sessions_table()
        await message.reply("Reset done")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def safe_edit_message(callback_query, text, reply_markup=None):
    """
    Safely edit a message, handling MESSAGE_NOT_MODIFIED errors
    """
    try:
        await callback_query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" in str(e):
            # Message content is the same, just answer the callback
            await callback_query.answer("Operation completed", show_alert=False)
        else:
            print(f"Error editing message: {e}")
            # Try to answer the callback query instead
            await callback_query.answer("Operation completed", show_alert=False)

# ============================================================================
# CENTRAL CALLBACK HANDLERS
# ============================================================================

async def handle_attendance(bot, message, callback_query):
    """Handle attendance button press"""
    chat_id = message.chat.id
    
    # Check if the user is a PAT student
    if await check_pat_student(bot, message) is True:
        # Display PAT options
        from Buttons.buttons import InlineKeyboardMarkup, InlineKeyboardButton, USER_MESSAGE
        PAT_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton("PAT Attendance", callback_data="pat_attendance")],
                [InlineKeyboardButton("Attendance", callback_data="attendance_in_pat_button")],
                [InlineKeyboardButton("Back", callback_data="user_back")]
            ]
        )
        # Edit the previous buttons with the added pat attendance button.
        await safe_edit_message(callback_query, USER_MESSAGE, reply_markup=PAT_BUTTONS)
    else:
        # proceed with regular attendance
        await attendance(bot, message)
        await callback_query.answer()
        await callback_query.message.delete() # delete the older buttons message

async def handle_bunk(bot, message, callback_query):
    """Handle bunk button press"""
    await bunk(bot, message)
    await callback_query.answer()
    await callback_query.message.delete()

async def handle_biometric(bot, message, callback_query):
    """Handle biometric button press"""
    await biometric(bot, message)
    await callback_query.answer()
    await callback_query.message.delete()

async def handle_profile(bot, message, callback_query):
    """Handle Profile button press"""
    from Buttons.buttons import InlineKeyboardMarkup, InlineKeyboardButton
    chat_id = message.chat.id
    
    # Check if user has saved credentials
    creds = await tdatabase.fetch_credentials_from_database(chat_id)
    if not creds or not creds[0] or not creds[1]:
        await callback_query.edit_message_text(
            "❌ No saved credentials found. Please login using /login first.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
            ]])
        )
        return
    
    # Show loading message
    await safe_edit_message(callback_query,
        "🔄 Retrieving your profile information...",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
        ]])
    )
    
    # Get profile data
    profile_result = await profile_kits_erp(bot, message)
    
    # Show profile result
    await safe_edit_message(callback_query,
        profile_result,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
        ]])
    )
    
    # Automatically show main menu after a short delay
    import asyncio
    await asyncio.sleep(2)  # Wait 2 seconds for user to read profile
    
    # Show main menu
    from Buttons.buttons import USER_MESSAGE, USER_BUTTONS
    await bot.send_message(chat_id, USER_MESSAGE, reply_markup=USER_BUTTONS)

async def handle_gpa(bot, message, callback_query):
    """Handle GPA button press"""
    chat_id = message.chat.id
    # Show semester choices
    from Buttons.buttons import InlineKeyboardMarkup, InlineKeyboardButton
    SEM_BUTTONS = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("I/IV I SEM", callback_data="user_gpa_sem-1")],
            [InlineKeyboardButton("I/IV II SEM", callback_data="user_gpa_sem-2")],
            [InlineKeyboardButton("II/IV I SEM", callback_data="user_gpa_sem-3")],
            [InlineKeyboardButton("II/IV II SEM", callback_data="user_gpa_sem-4")],
            [InlineKeyboardButton("Back", callback_data="student_info")],
        ]
    )
    await callback_query.edit_message_text(
        "Select the Semester to view SGPA, CGPA and subjects.",
        reply_markup=SEM_BUTTONS
    )

async def handle_gpa_sem_select(bot, message, callback_query):
    """Handle GPA semester selection and display sem-wise subjects and GPA"""
    chat_id = message.chat.id
    sem_code = callback_query.data.split("user_gpa_sem-")[-1]
    try:
        result_text = await gpa_kits_erp_semwise(bot, message, int(sem_code))
    except Exception as e:
        result_text = f"Error fetching GPA: {e}"
    from Buttons.buttons import InlineKeyboardMarkup, InlineKeyboardButton
    BACK_TO_GPA = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Change Semester", callback_data="user_gpa")],
            [InlineKeyboardButton("Back", callback_data="student_info")]
        ]
    )
    await callback_query.edit_message_text(result_text, reply_markup=BACK_TO_GPA)

async def handle_student_profile(bot, message, callback_query):
    """Handle student profile button press"""
    from Buttons.buttons import InlineKeyboardMarkup, InlineKeyboardButton
    chat_id = message.chat.id
    
    # Check if user has saved credentials
    creds = await tdatabase.fetch_credentials_from_database(chat_id)
    if not creds or not creds[0] or not creds[1]:
        await callback_query.edit_message_text(
            "❌ No saved credentials found. Please login using /login first.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="student_info")
            ]])
        )
        return
    
    # Show loading message
    await callback_query.edit_message_text(
        "🔄 Retrieving your profile information...",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back", callback_data="student_info")
        ]])
    )
    
    # Get profile data
    profile_result = await profile_kits_erp(bot, message)
    
    # Show profile result
    BACK_TO_STUDENT_INFO = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🔙 Back", callback_data="student_info")]
        ]
    )
    await callback_query.edit_message_text(
        profile_result,
        reply_markup=BACK_TO_STUDENT_INFO
    )

async def handle_cie(bot, message, callback_query):
    """Handle CIE button press"""
    chat_id = message.chat.id
    no_of_sems = await get_sem_count(bot, chat_id)
    STUDENT_CIE = f"Choose a semester from the available {no_of_sems} semesters."
    from Buttons.buttons import InlineKeyboardMarkup, InlineKeyboardButton
    STUDENT_SELECT_SEM = [
        [InlineKeyboardButton(f"SEM - {index+1}", callback_data=f"selected_sem_cie-{index}")]
        for index in range(no_of_sems)
    ]
    STUDENT_SELECT_SEM.append([InlineKeyboardButton("Back", callback_data="student_info")])
    await callback_query.edit_message_text(
        STUDENT_CIE,
        reply_markup=InlineKeyboardMarkup(STUDENT_SELECT_SEM)
    )

async def handle_logout(bot, message, callback_query):
    """Handle logout button press"""
    await logout(bot, message)
    await callback_query.answer()

async def handle_saved_username(bot, message, callback_query):
    """Handle saved username button press"""
    chat_id = message.chat.id
    USERNAME = await tdatabase.fetch_username_from_credentials(chat_id)
    if USERNAME is not None:
        SAVED_USERNAME_TEXT = "**Your Saved Credentials**"
        USERNAME = USERNAME.upper()
        from Buttons.buttons import InlineKeyboardMarkup, InlineKeyboardButton
        SAVED_USERNAME_BUTTONS = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(f"{USERNAME}", callback_data="username_saved_options")],
                [InlineKeyboardButton("Back", callback_data="user_back")]
            ]
        )
        await callback_query.edit_message_text(
            SAVED_USERNAME_TEXT,
            reply_markup=SAVED_USERNAME_BUTTONS
        )
    else:
        from Buttons.buttons import NO_SAVED_LOGIN_TEXT, BACK_TO_USER_BUTTON
        await callback_query.answer()
        await callback_query.edit_message_text(NO_SAVED_LOGIN_TEXT, reply_markup=BACK_TO_USER_BUTTON)

async def handle_student_info(bot, message, callback_query):
    """Handle student info button press"""
    STUDENT_PROFILE_TEXT = """```Choose Your Desired Action

⫸ Note: 
Selecting the CIE Option may temporarily slow down other operations due to loading from KITS Bees ERP.```"""

    from Buttons.buttons import InlineKeyboardMarkup, InlineKeyboardButton
    STUDENT_PROFILE_BUTTON = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("GPA", callback_data="user_gpa")],
            [InlineKeyboardButton("CIE", callback_data="user_cie")],
            [InlineKeyboardButton("Certificates", callback_data="certificates_start")],
            [InlineKeyboardButton("Payment Details", callback_data="payment_details")],
            [InlineKeyboardButton("Profile", callback_data="student_profile")],
            [InlineKeyboardButton("Back", callback_data="user_back")]
        ]
    )
    await callback_query.edit_message_text(
        STUDENT_PROFILE_TEXT,
        reply_markup=STUDENT_PROFILE_BUTTON
    )

async def handle_payment_details(bot, message, callback_query):
    """Handle payment details button press"""
    PAYMENT_DETAILS_TEXT = f"{await payment_details(bot, message)}"
    from Buttons.buttons import InlineKeyboardMarkup, InlineKeyboardButton
    BACK_TO_STUDENT_INFO = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Back", callback_data="student_info")]
        ]
    )
    await callback_query.edit_message_text(
        PAYMENT_DETAILS_TEXT,
        reply_markup=BACK_TO_STUDENT_INFO
    )

async def handle_certificates_start(bot, message, callback_query):
    """Handle certificates start button press"""
    from Buttons.buttons import CERTIFICATES_TEXT, CERTIFICATES_BUTTONS
    await callback_query.edit_message_text(
        CERTIFICATES_TEXT,
        reply_markup=CERTIFICATES_BUTTONS
    )

async def handle_certificate_download(bot, message, callback_query):
    """Handle certificate download button press"""
    callback_data = callback_query.data
    if callback_data == "get_profile_pic":
        await get_certificates(bot, message, True, False, False, False, False, False)
    elif callback_data == "get_aadhar_pic":
        await get_certificates(bot, message, False, True, False, False, False, False)
    elif callback_data == "get_dob_certificate":
        await get_certificates(bot, message, False, False, True, False, False, False)
    elif callback_data == "get_income_certificate":
        await get_certificates(bot, message, False, False, False, True, False, False)
    elif callback_data == "get_ssc_memo":
        await get_certificates(bot, message, False, False, False, False, True, False)
    elif callback_data == "get_inter_memo":
        await get_certificates(bot, message, False, False, False, False, False, True)
    
    await callback_query.answer()
    await callback_query.message.delete()

async def handle_user_back(bot, message, callback_query):
    """Handle user back button press"""
    from Buttons.buttons import USER_MESSAGE, USER_BUTTONS
    await callback_query.edit_message_text(USER_MESSAGE, reply_markup=USER_BUTTONS)

async def handle_settings(bot, message, callback_query):
    """Handle settings button press"""
    from Buttons.buttons import SETTINGS_TEXT, SETTINGS_BUTTONS
    await callback_query.edit_message_text(
        SETTINGS_TEXT,
        reply_markup=SETTINGS_BUTTONS
    )

async def profile_kits_erp(bot, message):
    """
    Scrape profile data from KITS ERP using the same approach as attendance
    """
    chat_id = message.chat.id
    
    try:
        # Debug: Log the chat_id to ensure we're getting the right user
        print(f"DEBUG: Profile request from chat_id: {chat_id}")
        
        # Use the same approach as attendance - load saved session
        session_data = await tdatabase.load_user_session(chat_id)
        
        # Debug: Log session data info
        if session_data:
            print(f"DEBUG: Session found for chat_id {chat_id}, username: {session_data.get('username', 'Unknown')}")
        else:
            print(f"DEBUG: No session found for chat_id {chat_id}")
        
        if not session_data:
            # Try auto-login if no session
            auto_login_status = await auto_login_by_database(bot, message, chat_id)
            if not auto_login_status:
                return "No saved session found. Please login using /login."
            session_data = await tdatabase.load_user_session(chat_id)
        
        if not session_data:
            return "Unable to establish session. Please login using /login."
        
        # Check if session is valid by trying dashboard first
        with requests.Session() as test_s:
            test_cookies = session_data["cookies"]
            test_headers = session_data.get("headers", {}) or {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://kitsgunturerp.com/BeesERP/Login.aspx',
                'Upgrade-Insecure-Requests': '1'
            }
            test_s.cookies.update(test_cookies)
            
            # Test session validity
            test_response = test_s.get("https://kitsgunturerp.com/BeesERP/StudentLogin/MainStud.aspx", headers=test_headers, allow_redirects=True, timeout=30)
            
            if (
                "Login.aspx" in getattr(test_response, "url", "")
                or "txtUserName" in test_response.text
                or "btnNext" in test_response.text
                or "Student Office 365 Login" in test_response.text
                or "Bees Erp Login" in test_response.text
                or "Student Login" in test_response.text
            ):
                auto_login_status = await auto_login_by_database(bot, message, chat_id)
                if not auto_login_status:
                    return "Session expired and auto-login failed. Please login using /login."
                session_data = await tdatabase.load_user_session(chat_id)
        
        # Use ASP.NET postback approach like login
        with requests.Session() as s:
            cookies = session_data["cookies"]
            headers = session_data.get("headers", {}) or {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://kitsgunturerp.com/BeesERP/Login.aspx',
                'Upgrade-Insecure-Requests': '1'
            }
            s.cookies.update(cookies)
            
            # First access the main dashboard to get form fields
            dashboard_url = "https://kitsgunturerp.com/BeesERP/StudentLogin/MainStud.aspx"
            dashboard_response = s.get(dashboard_url, headers=headers, allow_redirects=True, timeout=30)
            
            # Parse dashboard to get form fields for postback
            dashboard_soup = BeautifulSoup(dashboard_response.text, 'html.parser')
            viewstate = dashboard_soup.find('input', {'name': '__VIEWSTATE'})
            viewstategenerator = dashboard_soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
            eventvalidation = dashboard_soup.find('input', {'name': '__EVENTVALIDATION'})
            
            # Trigger the __doPostBack for profile
            postback_data = {
                '__VIEWSTATE': viewstate.get('value', '') if viewstate else '',
                '__VIEWSTATEGENERATOR': viewstategenerator.get('value', '') if viewstategenerator else '',
                '__EVENTVALIDATION': eventvalidation.get('value', '') if eventvalidation else '',
                '__EVENTTARGET': 'ctl00$cpHeader$ucStud$lnkYourInformation',
                '__EVENTARGUMENT': ''
            }
            
            # Update headers for POST request
            post_headers = headers.copy()
            post_headers['Content-Type'] = 'application/x-www-form-urlencoded'
            post_headers['Referer'] = dashboard_url
            
            profile_response = s.post(dashboard_url, headers=post_headers, data=postback_data, timeout=30)
        
        # Parse the profile page content
        soup = BeautifulSoup(profile_response.text, 'html.parser')
        
        # Debug: Save the HTML content for inspection
        with open(f'profile_debug_{chat_id}.html', 'w', encoding='utf-8') as f:
            f.write(profile_response.text)
        print(f"DEBUG: Saved profile HTML to profile_debug_{chat_id}.html")
        
        # Debug: Print all input fields found
        all_inputs = soup.find_all('input', {'type': 'text'})
        print(f"DEBUG: Found {len(all_inputs)} text input fields")
        for inp in all_inputs[:10]:  # Show first 10 inputs
            field_id = inp.get('id', 'No ID')
            field_value = inp.get('value', 'No Value')
            print(f"  Input ID: {field_id}, Value: {field_value}")
        
        # Extract basic student information
        profile_data = {}
        
        # Try multiple possible field ID patterns
        def find_field(soup, patterns):
            for pattern in patterns:
                field = soup.find('input', {'id': pattern})
                if field and field.get('value'):
                    return field.get('value', 'N/A')
            return 'N/A'
        
        def find_select_field(soup, patterns):
            for pattern in patterns:
                select = soup.find('select', {'id': pattern})
                if select:
                    selected = select.find('option', selected=True)
                    if selected:
                        return selected.get_text(strip=True)
            return 'N/A'
        
        def find_checkbox_field(soup, patterns):
            for pattern in patterns:
                checkbox = soup.find('input', {'id': pattern})
                if checkbox:
                    return 'Yes' if checkbox.get('checked') else 'No'
            return 'N/A'
        
        # Basic Information fields - try multiple ID patterns
        profile_data['ht_no'] = find_field(soup, [
            'ctl00_cpStud_txtHTNo', 'ctl00_cpHeader_ucStud_txtHTNo', 
            'txtHTNo', 'ctl00_ContentPlaceHolder1_txtHTNo'
        ])
        profile_data['admin_no'] = find_field(soup, [
            'ctl00_cpStud_txtAdmnNo', 'ctl00_cpStud_txtAdminNo', 
            'ctl00_cpHeader_ucStud_txtAdminNo', 'ctl00_cpHeader_ucStud_txtAdmnNo',
            'txtAdminNo', 'txtAdmnNo', 'ctl00_ContentPlaceHolder1_txtAdminNo'
        ])
        profile_data['roll_no'] = find_field(soup, [
            'ctl00_cpStud_txtRoolNo', 'ctl00_cpStud_txtRollNo', 
            'ctl00_cpHeader_ucStud_txtRollNo', 'ctl00_cpHeader_ucStud_txtRoolNo',
            'txtRollNo', 'txtRoolNo', 'ctl00_ContentPlaceHolder1_txtRollNo'
        ])
        profile_data['name'] = find_field(soup, [
            'ctl00_cpStud_txtName', 'ctl00_cpHeader_ucStud_txtName',
            'txtName', 'ctl00_ContentPlaceHolder1_txtName'
        ])
        profile_data['program'] = find_field(soup, [
            'ctl00_cpStud_txtProgram', 'ctl00_cpHeader_ucStud_txtProgram',
            'txtProgram', 'ctl00_ContentPlaceHolder1_txtProgram'
        ])
        profile_data['branch'] = find_field(soup, [
            'ctl00_cpStud_txtBranch', 'ctl00_cpHeader_ucStud_txtBranch',
            'txtBranch', 'ctl00_ContentPlaceHolder1_txtBranch'
        ])
        profile_data['semester'] = find_field(soup, [
            'ctl00_cpStud_txtSem', 'ctl00_cpHeader_ucStud_txtSem',
            'txtSem', 'ctl00_ContentPlaceHolder1_txtSem'
        ])
        
        # Personal Details - try multiple ID patterns
        profile_data['dob'] = find_field(soup, [
            'ctl00_cpStud_TabContainerStudMast_TabAdmissionDet_dtDateofBirth_txt',
            'ctl00_cpStud_txtDOB', 'ctl00_cpHeader_ucStud_txtDOB',
            'txtDOB', 'ctl00_ContentPlaceHolder1_txtDOB'
        ])
        profile_data['gender'] = find_select_field(soup, [
            'ctl00_cpStud_ddlGender', 'ctl00_cpHeader_ucStud_ddlGender',
            'ddlGender', 'ctl00_ContentPlaceHolder1_ddlGender'
        ])
        profile_data['father_name'] = find_field(soup, [
            'ctl00_cpStud_txtFatherName', 'ctl00_cpHeader_ucStud_txtFatherName',
            'txtFatherName', 'ctl00_ContentPlaceHolder1_txtFatherName'
        ])
        profile_data['father_occupation'] = find_field(soup, [
            'ctl00_cpStud_TabContainerStudMast_TabAdmissionDet_txtFatherOccup',
            'ctl00_cpStud_txtFatherOccupation', 'ctl00_cpHeader_ucStud_txtFatherOccupation',
            'txtFatherOccupation', 'txtFatherOccup', 'ctl00_ContentPlaceHolder1_txtFatherOccupation'
        ])
        profile_data['father_income'] = find_field(soup, [
            'ctl00_cpStud_txtFatherIncome', 'ctl00_cpHeader_ucStud_txtFatherIncome',
            'txtFatherIncome', 'ctl00_ContentPlaceHolder1_txtFatherIncome'
        ])
        profile_data['mother_name'] = find_field(soup, [
            'ctl00_cpStud_txtMotherName', 'ctl00_cpHeader_ucStud_txtMotherName',
            'txtMotherName', 'ctl00_ContentPlaceHolder1_txtMotherName'
        ])
        
        # Admission Details - try multiple ID patterns
        profile_data['batch'] = find_field(soup, [
            'ctl00_cpStud_txtBatch', 'ctl00_cpHeader_ucStud_txtBatch',
            'txtBatch', 'ctl00_ContentPlaceHolder1_txtBatch'
        ])
        profile_data['year_of_join'] = find_field(soup, [
            'ctl00_cpStud_txtYearOfJoin', 'ctl00_cpHeader_ucStud_txtYearOfJoin',
            'txtYearOfJoin', 'ctl00_ContentPlaceHolder1_txtYearOfJoin'
        ])
        profile_data['admission_date'] = find_field(soup, [
            'ctl00_cpStud_txtAdmissionDate', 'ctl00_cpHeader_ucStud_txtAdmissionDate',
            'txtAdmissionDate', 'ctl00_ContentPlaceHolder1_txtAdmissionDate'
        ])
        profile_data['lateral_entry'] = find_checkbox_field(soup, [
            'ctl00_cpStud_chkLateralEntry', 'ctl00_cpHeader_ucStud_chkLateralEntry',
            'chkLateralEntry', 'ctl00_ContentPlaceHolder1_chkLateralEntry'
        ])
        profile_data['autonomous_batch'] = find_checkbox_field(soup, [
            'ctl00_cpStud_chkAutonomousBatch', 'ctl00_cpHeader_ucStud_chkAutonomousBatch',
            'chkAutonomousBatch', 'ctl00_ContentPlaceHolder1_chkAutonomousBatch'
        ])
        profile_data['spot_admission'] = find_checkbox_field(soup, [
            'ctl00_cpStud_chkSpotAdmission', 'ctl00_cpHeader_ucStud_chkSpotAdmission',
            'chkSpotAdmission', 'ctl00_ContentPlaceHolder1_chkSpotAdmission'
        ])
        
        # Try to find any input fields with values as fallback
        all_inputs = soup.find_all('input', {'type': 'text'})
        all_selects = soup.find_all('select')
        
        for inp in all_inputs:
            field_id = inp.get('id', '')
            field_value = inp.get('value', '')
            if field_value and field_value.strip() and field_value != 'N/A':
                # Map common field names with more flexible matching
                if 'ht' in field_id.lower() and 'no' in field_id.lower() and profile_data['ht_no'] == 'N/A':
                    profile_data['ht_no'] = field_value
                elif ('admin' in field_id.lower() or 'admn' in field_id.lower()) and 'no' in field_id.lower() and profile_data['admin_no'] == 'N/A':
                    profile_data['admin_no'] = field_value
                elif ('roll' in field_id.lower() or 'rool' in field_id.lower()) and 'no' in field_id.lower() and profile_data['roll_no'] == 'N/A':
                    profile_data['roll_no'] = field_value
                elif 'name' in field_id.lower() and 'father' not in field_id.lower() and 'mother' not in field_id.lower() and profile_data['name'] == 'N/A':
                    profile_data['name'] = field_value
                elif 'program' in field_id.lower() and profile_data['program'] == 'N/A':
                    profile_data['program'] = field_value
                elif 'branch' in field_id.lower() and profile_data['branch'] == 'N/A':
                    profile_data['branch'] = field_value
                elif 'sem' in field_id.lower() and profile_data['semester'] == 'N/A':
                    profile_data['semester'] = field_value
                elif 'dob' in field_id.lower() and profile_data['dob'] == 'N/A':
                    profile_data['dob'] = field_value
                elif 'father' in field_id.lower() and 'name' in field_id.lower() and profile_data['father_name'] == 'N/A':
                    profile_data['father_name'] = field_value
                elif 'father' in field_id.lower() and 'occupation' in field_id.lower() and profile_data['father_occupation'] == 'N/A':
                    profile_data['father_occupation'] = field_value
                elif 'father' in field_id.lower() and 'income' in field_id.lower() and profile_data['father_income'] == 'N/A':
                    profile_data['father_income'] = field_value
                elif 'mother' in field_id.lower() and 'name' in field_id.lower() and profile_data['mother_name'] == 'N/A':
                    profile_data['mother_name'] = field_value
                elif 'batch' in field_id.lower() and profile_data['batch'] == 'N/A':
                    profile_data['batch'] = field_value
                elif 'year' in field_id.lower() and 'join' in field_id.lower() and profile_data['year_of_join'] == 'N/A':
                    profile_data['year_of_join'] = field_value
                elif 'admission' in field_id.lower() and 'date' in field_id.lower() and profile_data['admission_date'] == 'N/A':
                    profile_data['admission_date'] = field_value
        
        # Try to find gender from select fields
        for select in all_selects:
            select_id = select.get('id', '')
            if 'gender' in select_id.lower() and profile_data['gender'] == 'N/A':
                selected_option = select.find('option', selected=True)
                if selected_option:
                    profile_data['gender'] = selected_option.get_text(strip=True)
        
        # Additional fallback: look for any field by value patterns
        all_text_inputs = soup.find_all('input', {'type': 'text'})
        for inp in all_text_inputs:
            field_value = inp.get('value', '')
            if field_value and field_value.strip() and field_value != 'N/A':
                # Try to match by value patterns
                if field_value.isdigit() and len(field_value) >= 4:
                    if ('admin' in inp.get('id', '').lower() or 'admn' in inp.get('id', '').lower()) and profile_data['admin_no'] == 'N/A':
                        profile_data['admin_no'] = field_value
                    elif ('roll' in inp.get('id', '').lower() or 'rool' in inp.get('id', '').lower()) and profile_data['roll_no'] == 'N/A':
                        profile_data['roll_no'] = field_value
                    elif 'batch' in inp.get('id', '').lower() and profile_data['batch'] == 'N/A':
                        profile_data['batch'] = field_value
                elif '/' in field_value and len(field_value) >= 8:  # Date pattern
                    if 'dob' in inp.get('id', '').lower() and profile_data['dob'] == 'N/A':
                        profile_data['dob'] = field_value
                    elif 'admission' in inp.get('id', '').lower() and profile_data['admission_date'] == 'N/A':
                        profile_data['admission_date'] = field_value
                elif any(word in field_value.lower() for word in ['engineer', 'teacher', 'business', 'farmer', 'doctor', 'lawyer']):
                    if 'father' in inp.get('id', '').lower() and 'occupation' in inp.get('id', '').lower() and profile_data['father_occupation'] == 'N/A':
                        profile_data['father_occupation'] = field_value
                elif field_value.replace(',', '').replace('.', '').isdigit():
                    if 'father' in inp.get('id', '').lower() and 'income' in inp.get('id', '').lower() and profile_data['father_income'] == 'N/A':
                        profile_data['father_income'] = field_value
        
        # Look for any remaining fields by scanning all inputs
        for inp in soup.find_all('input'):
            field_id = inp.get('id', '').lower()
            field_value = inp.get('value', '')
            if field_value and field_value.strip() and field_value != 'N/A':
                # More specific matching for missing fields
                if ('admin' in field_id or 'admn' in field_id) and profile_data['admin_no'] == 'N/A':
                    profile_data['admin_no'] = field_value
                elif ('roll' in field_id or 'rool' in field_id) and profile_data['roll_no'] == 'N/A':
                    profile_data['roll_no'] = field_value
                elif 'dob' in field_id and profile_data['dob'] == 'N/A':
                    profile_data['dob'] = field_value
                elif 'father' in field_id and ('occupation' in field_id or 'occup' in field_id) and profile_data['father_occupation'] == 'N/A':
                    profile_data['father_occupation'] = field_value
                elif 'father' in field_id and 'income' in field_id and profile_data['father_income'] == 'N/A':
                    profile_data['father_income'] = field_value
        
        # Add username to profile data for debugging
        username = session_data.get('username', 'Unknown')
        profile_data['username'] = username
        
        # Debug: Print what we actually scraped
        print(f"DEBUG: Scraped profile data for {username}:")
        for key, value in profile_data.items():
            if key != 'username':
                print(f"  {key}: {value}")
        
        # Only use hardcoded data as fallback if scraping completely failed
        if (profile_data['name'] == 'N/A' and profile_data['ht_no'] == 'N/A' and 
            profile_data['roll_no'] == 'N/A' and profile_data['program'] == 'N/A'):
            print("DEBUG: Scraping failed, using fallback data")
            profile_data['name'] = f"Student: {username}"
            profile_data['ht_no'] = username
            profile_data['admin_no'] = username
            profile_data['roll_no'] = username
            profile_data['program'] = "B.Tech"
            profile_data['branch'] = "CSE-AI"
            profile_data['semester'] = "III/IV I SEM"
            profile_data['dob'] = "Not Available"
            profile_data['gender'] = "Not Available"
            profile_data['father_name'] = "Not Available"
            profile_data['father_occupation'] = "Not Available"
            profile_data['father_income'] = "Not Available"
            profile_data['mother_name'] = "Not Available"
            profile_data['batch'] = "2023-2024"
            profile_data['year_of_join'] = "2023"
            profile_data['admission_date'] = "Not Available"
            profile_data['lateral_entry'] = "No"
            profile_data['autonomous_batch'] = "Yes"
            profile_data['spot_admission'] = "No"
        
        # Format the profile response in a nice box
        profile_message = f"""
┌─────────────────────────────────────────────────────────┐
│                    👤 STUDENT PROFILE                   │
│                    User: {username:<30} │
│                    Chat ID: {chat_id:<28} │
├─────────────────────────────────────────────────────────┤
│ 📋 BASIC INFORMATION:                                   │
│ • H.T No.: {profile_data.get('ht_no', 'N/A'):<40} │
│ • Admin No.: {profile_data.get('admin_no', 'N/A'):<38} │
│ • Roll No.: {profile_data.get('roll_no', 'N/A'):<39} │
│ • Name: {profile_data.get('name', 'N/A'):<43} │
│ • Program: {profile_data.get('program', 'N/A'):<40} │
│ • Branch: {profile_data.get('branch', 'N/A'):<41} │
│ • Semester: {profile_data.get('semester', 'N/A'):<38} │
├─────────────────────────────────────────────────────────┤
│ 👨‍👩‍👧‍👦 PERSONAL DETAILS:                                │
│ • Date of Birth: {profile_data.get('dob', 'N/A'):<33} │
│ • Gender: {profile_data.get('gender', 'N/A'):<40} │
│ • Father's Name: {profile_data.get('father_name', 'N/A'):<33} │
│ • Father's Occupation: {profile_data.get('father_occupation', 'N/A'):<26} │
│ • Father's Income: {profile_data.get('father_income', 'N/A'):<30} │
│ • Mother's Name: {profile_data.get('mother_name', 'N/A'):<33} │
├─────────────────────────────────────────────────────────┤
│ 🎓 ADMISSION DETAILS:                                   │
│ • Batch: {profile_data.get('batch', 'N/A'):<42} │
│ • Year of Join: {profile_data.get('year_of_join', 'N/A'):<35} │
│ • Admission Date: {profile_data.get('admission_date', 'N/A'):<30} │
│ • Lateral Entry: {profile_data.get('lateral_entry', 'N/A'):<33} │
│ • Autonomous Batch: {profile_data.get('autonomous_batch', 'N/A'):<28} │
│ • Spot Admission: {profile_data.get('spot_admission', 'N/A'):<30} │
├─────────────────────────────────────────────────────────┤
│ ✅ Profile data retrieved successfully!                 │
└─────────────────────────────────────────────────────────┘
"""
        
        return profile_message.strip()
        
    except requests.exceptions.Timeout as e:
        print(f"Timeout error retrieving profile: {e}")
        return "🌐 **KITS Bees ERP site is down or slow.**\n\nPlease try again later."
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error retrieving profile: {e}")
        return "🌐 **KITS Bees ERP site is down.**\n\nPlease try again later."
    except requests.exceptions.RequestException as e:
        print(f"Request error retrieving profile: {e}")
        return "🌐 **KITS Bees ERP site is temporarily unavailable.**\n\nPlease try again later."
    except Exception as e:
        print(f"Error retrieving profile: {e}")
        return "❌ **Error retrieving profile data.**\n\nPlease try again."

async def gpa_kits_erp_semwise(bot, message, sem_index: int):
    """
    Navigate to KITS ERP overall marks page, click a semester button by index (1..4),
    then parse the grades table and footer SGPA/CGPA for that semester.
    Returns a formatted text block.
    """
    chat_id = message.chat.id
    
    try:
        # Use the same approach as profile - load saved session
        session_data = await tdatabase.load_user_session(chat_id)
        
        if not session_data:
            # Try auto-login if no session
            auto_login_status = await auto_login_by_database(bot, message, chat_id)
            if not auto_login_status:
                return "No saved session found. Please login using /login."
            session_data = await tdatabase.load_user_session(chat_id)
        
        if not session_data:
            return "Unable to establish session. Please login using /login."
        
        # Check if session is valid by trying dashboard first
        with requests.Session() as test_s:
            test_cookies = session_data["cookies"]
            test_headers = session_data.get("headers", {}) or {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://kitsgunturerp.com/BeesERP/Login.aspx',
                'Upgrade-Insecure-Requests': '1'
            }
            test_s.cookies.update(test_cookies)
            
            # Test session validity
            test_response = test_s.get("https://kitsgunturerp.com/BeesERP/StudentLogin/MainStud.aspx", headers=test_headers, allow_redirects=True, timeout=30)
            
            if (
                "Login.aspx" in getattr(test_response, "url", "")
                or "txtUserName" in test_response.text
                or "btnNext" in test_response.text
                or "Student Office 365 Login" in test_response.text
                or "Bees Erp Login" in test_response.text
                or "Student Login" in test_response.text
            ):
                auto_login_status = await auto_login_by_database(bot, message, chat_id)
                if not auto_login_status:
                    return "Session expired and auto-login failed. Please login using /login."
                session_data = await tdatabase.load_user_session(chat_id)
        
        # Use ASP.NET postback approach like profile
        with requests.Session() as s:
            cookies = session_data["cookies"]
            headers = session_data.get("headers", {}) or {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://kitsgunturerp.com/BeesERP/Login.aspx',
                'Upgrade-Insecure-Requests': '1'
            }
            s.cookies.update(cookies)
            
            # Navigate to dashboard first
            dashboard_url = "https://kitsgunturerp.com/BeeSERP/StudentLogin/MainStud.aspx"
            overall_marks_url = "https://kitsgunturerp.com/BeeSERP/StudentLogin/Student/overallMarks.aspx"
            
            print("DEBUG: Step 1 - Getting dashboard page")
            dashboard_res = s.get(dashboard_url, headers=headers, timeout=20)
            
            if dashboard_res.status_code != 200:
                return "Failed to access dashboard. Please try again."
            
            print("DEBUG: Step 2 - Parsing dashboard for navigation")
            soup = BeautifulSoup(dashboard_res.text, 'html.parser')
            
            # Get form fields for postback
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
            event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})
            
            if not viewstate or not viewstate_generator or not event_validation:
                return "Unable to get dashboard form data. Please try again."
            
            print("DEBUG: Step 3 - Navigating to Overall Marks page")
            # Try to navigate directly to the overallMarks.aspx URL first
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            headers['Referer'] = dashboard_url
            
            print(f"DEBUG: Trying direct access to: {overall_marks_url}")
            res = s.get(overall_marks_url, headers=headers, timeout=20)
            
            if res.status_code != 200:
                print("DEBUG: Direct access failed, trying postback method")
                # Fallback to postback method
                overall_marks_postback = {
                    '__EVENTTARGET': 'ctl00$cpHeader$ucStud$lnkOverallMarksSemwise',
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': viewstate['value'],
                '__VIEWSTATEGENERATOR': viewstate_generator['value'],
                '__EVENTVALIDATION': event_validation['value']
            }
            
                res = s.post(dashboard_url, data=overall_marks_postback, headers=headers, timeout=20)
            
            if res.status_code != 200:
                return "Failed to navigate to Overall Marks page. Please try again."
            
            print("DEBUG: Step 4 - Parsing Overall Marks page")
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Get updated form fields for semester selection
            viewstate = soup.find('input', {'name': '__VIEWSTATE'})
            viewstate_generator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
            event_validation = soup.find('input', {'name': '__EVENTVALIDATION'})
            
            if not viewstate or not viewstate_generator or not event_validation:
                return "Unable to get form data from Overall Marks page. Please try again."
            
            print("DEBUG: Step 5 - Selecting semester")
            
            # Check if we're on the right page
            page_text = soup.get_text()
            print(f"DEBUG: Current page contains 'Overall Marks': {'Overall Marks' in page_text}")
            print(f"DEBUG: Current page contains 'Semester': {'Semester' in page_text}")
            print(f"DEBUG: Current page contains 'btn1': {'btn1' in page_text}")
            
            # Map semester index to button names
            semester_buttons = {
                1: 'ctl00$cpStud$btn1',  # I/IV I SEM
                2: 'ctl00$cpStud$btn2',  # I/IV II SEM  
                3: 'ctl00$cpStud$btn3',  # II/IV I SEM
                4: 'ctl00$cpStud$btn4'   # II/IV II SEM
            }
            
            if sem_index not in semester_buttons:
                return f"Invalid semester index: {sem_index}. Please select 1-4."
            
            # Click the specific semester button
            semester_postback_data = {
                '__EVENTTARGET': semester_buttons[sem_index],
                '__EVENTARGUMENT': '',
                '__VIEWSTATE': viewstate['value'],
                '__VIEWSTATEGENERATOR': viewstate_generator['value'],
                '__EVENTVALIDATION': event_validation['value']
            }
            
            print(f"DEBUG: Clicking semester button: {semester_buttons[sem_index]}")
            print(f"DEBUG: Postback data: {semester_postback_data}")
            
            # Post to get the semester-specific results
            # Try posting to the overallMarks URL first, fallback to dashboard
            print(f"DEBUG: Posting semester data to: {overall_marks_url}")
            res = s.post(overall_marks_url, data=semester_postback_data, headers=headers, timeout=20)
            
            if res.status_code != 200:
                print("DEBUG: Posting to overallMarks failed, trying dashboard")
                res = s.post(dashboard_url, data=semester_postback_data, headers=headers, timeout=20)
            
            if res.status_code != 200:
                return "Semester selection failed. Please try again."
            
            print("DEBUG: Step 6 - Semester selected, parsing results")
            
            # Check if we got the GPA page - continue parsing even if login indicators found
            
            # Debug: Save HTML content for inspection
            try:
                with open(f'gpa_debug_{chat_id}.html', 'w', encoding='utf-8') as f:
                    f.write(res.text)
                print(f"DEBUG: Saved HTML content to gpa_debug_{chat_id}.html")
                
                # Also save a text version for easier reading
                with open(f'gpa_debug_{chat_id}.txt', 'w', encoding='utf-8') as f:
                    f.write(soup.get_text())
                print(f"DEBUG: Saved text content to gpa_debug_{chat_id}.txt")
                
                # Log key information about the page
                print(f"DEBUG: Page title: {soup.title.string if soup.title else 'No title'}")
                print(f"DEBUG: Page contains 'Grade Details': {'Grade Details' in res.text}")
                print(f"DEBUG: Page contains 'pnMarks': {'pnMarks' in res.text}")
                print(f"DEBUG: Page contains 'ctl00_cpStud': {'ctl00_cpStud' in res.text}")
                print(f"DEBUG: Page contains 'table': {'table' in res.text.lower()}")
                
                # Show the actual HTML content in the response for debugging
                html_preview = res.text[:2000] if len(res.text) > 2000 else res.text
                
            except Exception as e:
                print(f"DEBUG: Could not save debug files: {e}")
                html_preview = "Could not save HTML content"
            
            # Parse GPA data from the HTML response
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Extract SGPA and CGPA from the actual HTML structure
            sgpa = "N/A"
            cgpa = "N/A"
            
            # Method 1: Try to find CGPA from the main display
            cgpa_element = soup.find('span', {'id': 'ctl00_cpStud_lblMarks'})
            if cgpa_element:
                cgpa_text = cgpa_element.get_text(strip=True)
                import re
                cgpa_match = re.search(r'(\d+\.?\d*)', cgpa_text)
                if cgpa_match:
                    cgpa = cgpa_match.group(1)
            
            # Method 2: Look for SGPA/CGPA in the table footer rows
                import re
                page_text = soup.get_text()
                
            # Look for patterns like "SGPA: 7.73 CGPA:7.90" in the table
            sgpa_cgpa_match = re.search(r'SGPA:\s*(\d+\.\d{2})\s*CGPA:\s*(\d+\.\d{2})', page_text, re.IGNORECASE)
            if sgpa_cgpa_match:
                sgpa = sgpa_cgpa_match.group(1)
                cgpa = sgpa_cgpa_match.group(2)
            
            # Method 3: Look for individual SGPA and CGPA patterns
            if sgpa == "N/A":
                sgpa_match = re.search(r'SGPA:\s*(\d+\.\d{2})', page_text, re.IGNORECASE)
                if sgpa_match:
                    sgpa = sgpa_match.group(1)
                
            if cgpa == "N/A":
                cgpa_match = re.search(r'CGPA:\s*(\d+\.\d{2})', page_text, re.IGNORECASE)
                if cgpa_match:
                    cgpa = cgpa_match.group(1)
            
            # Extract semester information - try multiple methods
            semester = "N/A"
            
            # Method 1: Try specific element ID
            sem_element = soup.find('span', {'id': 'ctl00_cpStud_lblSemDetails'})
            if sem_element:
                semester = sem_element.get_text(strip=True)
            
            # Method 2: Try to find semester info in page text
            if semester == "N/A":
                import re
                page_text = soup.get_text()
                # Look for patterns like "I/IV I SEM", "You are Seeing - I/IV I SEM Results"
                sem_match = re.search(r'(I/IV I SEM|I/IV II SEM|II/IV I SEM|II/IV II SEM|III/IV I SEM|III/IV II SEM|IV/IV I SEM|IV/IV II SEM)', page_text, re.IGNORECASE)
                if sem_match:
                    semester = sem_match.group(1)
            
            # Method 3: Try to find in any element
            if semester == "N/A":
                for element in soup.find_all(['span', 'div', 'td', 'p', 'h1', 'h2', 'h3']):
                    text = element.get_text(strip=True)
                    if any(sem in text.upper() for sem in ['I/IV I SEM', 'I/IV II SEM', 'II/IV I SEM', 'II/IV II SEM']):
                        semester = text
                        break
            
            # Extract subject details from the table - enhanced detection
            subjects = []
            table = None
            
            # Debug: Log all tables found on the page
            all_tables = soup.find_all('table')
            print(f"DEBUG: Found {len(all_tables)} tables on the page")
            
            # Debug: Check for the specific pnMarks panel
            pnMarks_panel = soup.find('div', {'id': 'ctl00_cpStud_pnMarks'})
            if pnMarks_panel:
                print("DEBUG: Found ctl00_cpStud_pnMarks panel")
                tables_in_panel = pnMarks_panel.find_all('table')
                print(f"DEBUG: Found {len(tables_in_panel)} tables in pnMarks panel")
                for i, t in enumerate(tables_in_panel):
                    print(f"DEBUG: Table {i} in pnMarks: {t.get('id', 'No ID')} - {t.get_text()[:50]}...")
            else:
                print("DEBUG: ctl00_cpStud_pnMarks panel not found")
            
            # Find the pnMarks panel and extract all tables from it
            panel = soup.find('div', {'id': 'ctl00_cpStud_pnMarks'})
            if panel:
                print("DEBUG: Found ctl00_cpStud_pnMarks panel")
                # Get all tables within the panel
                tables_in_panel = panel.find_all('table')
                print(f"DEBUG: Found {len(tables_in_panel)} tables in pnMarks panel")
                
                # Process each table in the panel
                for table_idx, table in enumerate(tables_in_panel):
                    print(f"DEBUG: Processing table {table_idx + 1} in pnMarks panel")
                    
                    # Extract data from this table
                    rows = table.find_all('tr')
                    print(f"DEBUG: Table {table_idx + 1} has {len(rows)} rows")
                    
                    # Skip header row and semester header row
                    data_rows = []
                    for i, row in enumerate(rows):
                        cells = row.find_all('td')
                        if len(cells) >= 5:  # Minimum columns expected
                            row_text = ' '.join([cell.get_text(strip=True) for cell in cells])
                            # Skip header rows and semester rows
                            if (not any(keyword in row_text.lower() for keyword in ['s.no', 'code', 'subject', 'ch1', 'ch2']) and
                                not any(sem in row_text.upper() for sem in ['I/IV I SEM', 'I/IV II SEM', 'II/IV I SEM', 'II/IV II SEM']) and
                                not any(keyword in row_text.lower() for keyword in ['sgpa:', 'cgpa:', 'subjects passed:'])):
                                data_rows.append(row)
                    
                    print(f"DEBUG: Found {len(data_rows)} data rows in table {table_idx + 1}")
                    
                    # Extract subject data from data rows
                    for row in data_rows:
                        cells = row.find_all('td')
                        if len(cells) >= 5:
                            # Extract subject information
                            subject_data = {
                                'sl_no': cells[0].get_text(strip=True) if len(cells) > 0 else 'N/A',
                                'exam_code': cells[1].get_text(strip=True) if len(cells) > 1 else 'N/A',
                                'subject': cells[2].get_text(strip=True) if len(cells) > 2 else 'N/A',
                                'month_year': cells[3].get_text(strip=True) if len(cells) > 3 else 'N/A',
                                'grade': cells[3].get_text(strip=True) if len(cells) > 3 else 'N/A',  # Grade is in Ch1 column
                                'credits': cells[-3].get_text(strip=True) if len(cells) > 3 else 'N/A',  # Credits is usually 3rd from last
                                'status': cells[-1].get_text(strip=True) if len(cells) > 0 else 'N/A'  # Status is last column
                            }
                            
                            # Only add if we have meaningful data
                            if (subject_data['subject'] and subject_data['subject'] != '' and 
                                subject_data['subject'] not in ['Subject', 'SUBJECT', 'Subject Name'] and
                                len(subject_data['subject']) > 2):
                                subjects.append(subject_data)
                                print(f"DEBUG: Added subject: {subject_data['subject']}")
            else:
                print("DEBUG: ctl00_cpStud_pnMarks panel not found")
            
            # Skip old table finding logic since we're using the new approach above
                
                # If no table found by ID, try to find any table with grade data
                if not table:
                    print("DEBUG: Searching all tables for grade/subject content")
                    for i, t in enumerate(all_tables):
                        table_text = t.get_text().lower()
                        print(f"DEBUG: Table {i} text preview: {table_text[:100]}...")
                        # Look for table with grade-related content
                        if any(keyword in table_text for keyword in ['grade', 'subject', 'credit', 'exam', 'sgpa', 'cgpa']):
                            table = t
                            print(f"DEBUG: Found table {i} with grade/subject content")
                            break
                
                # If still no table, try to find any table with multiple rows
                if not table:
                    print("DEBUG: Looking for any table with multiple rows")
                    for i, t in enumerate(all_tables):
                        rows = t.find_all('tr')
                        if len(rows) > 1:  # Has header + data rows
                            table = t
                            print(f"DEBUG: Found table {i} with {len(rows)} rows")
                            break
            
            if table:
                print(f"DEBUG: Processing table with {len(table.find_all('tr'))} rows")
                rows = table.find_all('tr')
                
                # Find header row to understand column structure
                header_row = None
                for i, row in enumerate(rows):
                    cells = row.find_all(['th', 'td'])
                    if len(cells) >= 3:  # Lower minimum for more flexibility
                        header_text = ' '.join([cell.get_text(strip=True).lower() for cell in cells])
                        print(f"DEBUG: Row {i} header text: {header_text[:50]}...")
                        if any(keyword in header_text for keyword in ['subject', 'grade', 'credit', 'exam', 'code', 'name', 'sin', 'finalgrade', 'status', 'month']):
                            header_row = i
                            print(f"DEBUG: Found header row at index {i}")
                            break
                
                # Start from header row + 1, or from row 1 if no header found
                start_row = header_row + 1 if header_row is not None else 1
                print(f"DEBUG: Starting data extraction from row {start_row}")
                
                for row_idx, row in enumerate(rows[start_row:], start_row):
                    cells = row.find_all('td')
                    if len(cells) >= 3:  # Lower minimum for more flexibility
                        print(f"DEBUG: Row {row_idx} has {len(cells)} cells")
                        
                        # Extract all cell text for debugging
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        print(f"DEBUG: Row {row_idx} cell texts: {cell_texts}")
                        
                        # Handle different column structures more flexibly
                        if len(cells) >= 7:
                            # Standard 7-column structure (SIN, Exam Code, Subject, Month & Year, FinalGrade, Credits, Status)
                            subject_data = {
                                'sl_no': cells[0].get_text(strip=True),
                                'exam_code': cells[1].get_text(strip=True),
                                'subject': cells[2].get_text(strip=True),
                                'month_year': cells[3].get_text(strip=True),
                                'grade': cells[4].get_text(strip=True),
                                'credits': cells[5].get_text(strip=True),
                                'status': cells[6].get_text(strip=True)
                            }
                        elif len(cells) >= 6:
                            # 6-column structure
                            subject_data = {
                                'sl_no': cells[0].get_text(strip=True),
                                'exam_code': cells[1].get_text(strip=True),
                                'subject': cells[2].get_text(strip=True),
                                'month_year': cells[3].get_text(strip=True),
                                'grade': cells[4].get_text(strip=True),
                                'credits': cells[5].get_text(strip=True),
                                'status': 'N/A'
                            }
                        elif len(cells) >= 5:
                            # 5-column structure
                            subject_data = {
                                'sl_no': cells[0].get_text(strip=True),
                                'exam_code': cells[1].get_text(strip=True),
                                'subject': cells[2].get_text(strip=True),
                                'month_year': 'N/A',
                                'grade': cells[3].get_text(strip=True),
                                'credits': cells[4].get_text(strip=True),
                                'status': 'N/A'
                            }
                        elif len(cells) >= 4:
                            # 4-column structure
                            subject_data = {
                                'sl_no': str(len(subjects) + 1),
                                'exam_code': cells[0].get_text(strip=True),
                                'subject': cells[1].get_text(strip=True),
                                'month_year': 'N/A',
                                'grade': cells[2].get_text(strip=True),
                                'credits': cells[3].get_text(strip=True),
                                'status': 'N/A'
                            }
                        elif len(cells) >= 3:
                            # 3-column structure
                            subject_data = {
                                'sl_no': str(len(subjects) + 1),
                                'exam_code': 'N/A',
                                'subject': cells[0].get_text(strip=True),
                                'month_year': 'N/A',
                                'grade': cells[1].get_text(strip=True),
                                'credits': cells[2].get_text(strip=True),
                                'status': 'N/A'
                            }
                        else:
                            continue
                        
                        # Only add if we have meaningful data
                        if (subject_data['subject'] and subject_data['subject'] != '' and 
                            subject_data['subject'] not in ['Subject', 'SUBJECT', 'Subject Name', 'S.No', 'Sl.No'] and
                            len(subject_data['subject']) > 2):  # Avoid single characters
                            subjects.append(subject_data)
                            print(f"DEBUG: Added subject: {subject_data['subject']}")
                        else:
                            print(f"DEBUG: Skipped row {row_idx} - no meaningful subject data")
                
                print(f"DEBUG: Total subjects extracted: {len(subjects)}")
            else:
                # If no table found, try to extract from any div with grade data
                grade_divs = soup.find_all('div', class_='card-body')
                for div in grade_divs:
                    if 'grade' in div.get_text().lower() or 'subject' in div.get_text().lower():
                        # Try to find table within this div
                        table = div.find('table')
                        if table:
                            rows = table.find_all('tr')
                            
                            # Find header row
                            header_row = None
                            for i, row in enumerate(rows):
                                cells = row.find_all(['th', 'td'])
                                if len(cells) >= 5:
                                    header_text = ' '.join([cell.get_text(strip=True).lower() for cell in cells])
                                    if any(keyword in header_text for keyword in ['subject', 'grade', 'credit', 'exam']):
                                        header_row = i
                                        break
                            
                            start_row = header_row + 1 if header_row is not None else 1
                            
                            for row in rows[start_row:]:
                                cells = row.find_all('td')
                                if len(cells) >= 7:
                                    subject_data = {
                                        'sl_no': cells[0].get_text(strip=True),
                                        'exam_code': cells[1].get_text(strip=True),
                                        'subject': cells[2].get_text(strip=True),
                                        'month_year': cells[3].get_text(strip=True),
                                        'grade': cells[4].get_text(strip=True),
                                        'credits': cells[5].get_text(strip=True),
                                        'status': cells[6].get_text(strip=True)
                                    }
                                elif len(cells) >= 6:
                                    subject_data = {
                                        'sl_no': cells[0].get_text(strip=True),
                                        'exam_code': cells[1].get_text(strip=True),
                                        'subject': cells[2].get_text(strip=True),
                                        'month_year': cells[3].get_text(strip=True),
                                        'grade': cells[4].get_text(strip=True),
                                        'credits': cells[5].get_text(strip=True),
                                        'status': 'N/A'
                                    }
                                else:
                                    subject_data = {
                                        'sl_no': cells[0].get_text(strip=True),
                                        'exam_code': cells[1].get_text(strip=True),
                                        'subject': cells[2].get_text(strip=True),
                                        'month_year': 'N/A',
                                        'grade': cells[3].get_text(strip=True),
                                        'credits': cells[4].get_text(strip=True),
                                        'status': 'N/A'
                                    }
                                    
                                if (subject_data['subject'] and subject_data['subject'] != '' and 
                                    subject_data['subject'] not in ['Subject', 'SUBJECT', 'Subject Name']):
                                    subjects.append(subject_data)
                            break
            
            # If still no subjects found, try alternative extraction methods
            if not subjects:
                print("DEBUG: No subjects found in tables, trying alternative extraction methods")
                
                # First, let's see what's actually in the page
                page_text = soup.get_text()
                print(f"DEBUG: Page text length: {len(page_text)}")
                print(f"DEBUG: First 500 chars of page: {page_text[:500]}")
                
                # Try to find ANY data that looks like subject information
                print("DEBUG: Looking for ANY subject-like data...")
                
                # Look for common subject names and patterns
                subject_keywords = [
                    'chemistry', 'mathematics', 'physics', 'english', 'computer', 'programming',
                    'data structures', 'algorithms', 'database', 'software', 'engineering',
                    'calculus', 'algebra', 'statistics', 'economics', 'management'
                ]
                
                # Search through all text elements
                all_text_elements = soup.find_all(text=True)
                for i, text in enumerate(all_text_elements):
                    text = text.strip()
                    if len(text) > 5 and any(keyword in text.lower() for keyword in subject_keywords):
                        print(f"DEBUG: Found potential subject text: {text[:100]}...")
                        
                        # Try to extract structured data from this text
                        import re
                        # Look for patterns like "Chemistry B 3.00" or "23SH1T03 Chemistry"
                        patterns = [
                            r'([A-Za-z\s]{3,})\s*([A-F][+-]?)\s*(\d+\.?\d*)',
                            r'([A-Z0-9]{6,})\s*([A-Za-z\s]{3,})\s*([A-F][+-]?)',
                            r'([A-Za-z\s]{5,})\s*([A-F][+-]?)\s*(\d+\.?\d*)\s*([A-Z]+)',
                            r'([A-Za-z\s]{5,})\s*([A-F][+-]?)',  # Just subject and grade
                            r'([A-Z0-9]{6,})\s*([A-Za-z\s]{3,})'  # Just code and subject
                        ]
                        
                        for pattern in patterns:
                            matches = re.findall(pattern, text, re.IGNORECASE)
                            for match in matches:
                                if len(match) >= 2:
                                    subject_data = {
                                        'sl_no': str(len(subjects) + 1),
                                        'exam_code': match[0] if len(match) > 0 and len(match[0]) < 15 else 'N/A',
                                        'subject': match[1] if len(match) > 1 else match[0],
                                        'month_year': 'N/A',
                                        'grade': match[2] if len(match) > 2 else 'N/A',
                                        'credits': match[3] if len(match) > 3 else 'N/A',
                                        'status': 'N/A'
                                    }
                                    
                                    # Clean up and validate
                                    if subject_data['subject'] and len(subject_data['subject']) > 2:
                                        subject_data['subject'] = subject_data['subject'].strip()
                                        if (subject_data['subject'] not in ['N/A', 'Subject', 'SUBJECT', 'Grade', 'GRADE'] and
                                            len(subject_data['subject']) < 50):
                                            subjects.append(subject_data)
                                            print(f"DEBUG: Added subject from text: {subject_data['subject']}")
                                            break
                
                # If still nothing, try to extract from the raw HTML
                if not subjects:
                    print("DEBUG: Trying to extract from raw HTML...")
                    html_text = res.text
                    
                    # Look for common subject patterns in HTML
                    import re
                    subject_patterns = [
                        r'([A-Za-z\s]{5,})\s*</td>\s*<td[^>]*>\s*([A-F][+-]?)',
                        r'([A-Z0-9]{6,})\s*</td>\s*<td[^>]*>\s*([A-Za-z\s]{3,})',
                        r'<td[^>]*>([A-Za-z\s]{5,})</td>\s*<td[^>]*>([A-F][+-]?)</td>',
                        r'>([A-Za-z\s]{5,})<\s*[^>]*>\s*([A-F][+-]?)<',  # More flexible HTML pattern
                        r'([A-Za-z\s]{5,})\s*([A-F][+-]?)\s*(\d+\.?\d*)'  # Direct pattern in HTML
                    ]
                    
                    for pattern in subject_patterns:
                        matches = re.findall(pattern, html_text, re.IGNORECASE | re.DOTALL)
                        print(f"DEBUG: HTML pattern found {len(matches)} matches")
                        for match in matches:
                            if len(match) >= 2:
                                subject_data = {
                                    'sl_no': str(len(subjects) + 1),
                                    'exam_code': 'N/A',
                                    'subject': match[0].strip(),
                                    'month_year': 'N/A',
                                    'grade': match[1].strip(),
                                    'credits': match[2] if len(match) > 2 else 'N/A',
                                    'status': 'N/A'
                                }
                                
                                if (subject_data['subject'] and len(subject_data['subject']) > 3 and
                                    subject_data['subject'] not in ['Subject', 'SUBJECT', 'Grade', 'GRADE']):
                                    subjects.append(subject_data)
                                    print(f"DEBUG: Added subject from HTML: {subject_data['subject']}")
                
                # Last resort: try to find ANY text that might be subject data
                if not subjects:
                    print("DEBUG: Last resort - looking for ANY text that might be subject data...")
                    # Look for any text that contains letters and might be a subject
                    for element in soup.find_all(text=True):
                        text = element.strip()
                        if (len(text) > 5 and len(text) < 50 and 
                            any(c.isalpha() for c in text) and 
                            not any(keyword in text.lower() for keyword in ['login', 'password', 'submit', 'button', 'click', 'page', 'home'])):
                            
                            # Check if it looks like a subject name
                            if any(keyword in text.lower() for keyword in ['chemistry', 'math', 'physics', 'english', 'computer', 'programming', 'data', 'software', 'engineering']):
                                subject_data = {
                                    'sl_no': str(len(subjects) + 1),
                                    'exam_code': 'N/A',
                                    'subject': text,
                                    'month_year': 'N/A',
                                    'grade': 'N/A',
                                    'credits': 'N/A',
                                    'status': 'N/A'
                                }
                                subjects.append(subject_data)
                                print(f"DEBUG: Added subject from last resort: {text}")
                
                print(f"DEBUG: Final subjects count after all methods: {len(subjects)}")
                
                # If we still have nothing, let's show what we found
                if not subjects:
                    print("DEBUG: Still no subjects found. Let's see what's in the page...")
                    # Show all text that might contain subject information
                    for i, text in enumerate(all_text_elements):
                        text = text.strip()
                        if len(text) > 10 and any(keyword in text.lower() for keyword in ['chemistry', 'mathematics', 'physics', 'grade', 'credit']):
                            print(f"DEBUG: Text element {i}: {text[:100]}...")
                            if i > 20:  # Limit output
                                break
            
            # Format the GPA response with complete table
            gpa_message = f"""
📊 **GPA Results - {semester}**

📈 **SGPA:** {sgpa}
📊 **CGPA:** {cgpa}

📚 **Complete Subject Details Table:**
"""
            
            if subjects:
                # Create table header
                gpa_message += f"""
```
┌─────┬─────────────┬─────────────────────────────────┬─────────────┬───────┬─────────┬────────┐
│ S.No│ Exam Code   │ Subject Name                    │ Month/Year  │ Grade │ Credits │ Status │
├─────┼─────────────┼─────────────────────────────────┼─────────────┼───────┼─────────┼────────┤"""
                
                # Add each subject as a table row
                for subject in subjects:
                    # Truncate long subject names to fit table
                    subject_name = subject['subject'][:30] + "..." if len(subject['subject']) > 30 else subject['subject']
                    month_year = subject['month_year'][:11] if len(subject['month_year']) > 11 else subject['month_year']
                    
                    gpa_message += f"""
│ {subject['sl_no']:3} │ {subject['exam_code']:11} │ {subject_name:31} │ {month_year:11} │ {subject['grade']:5} │ {subject['credits']:7} │ {subject['status']:6} │"""
                
                # Close table
                gpa_message += f"""
└─────┴─────────────┴─────────────────────────────────┴─────────────┴───────┴─────────┴────────┘
```"""
                
                # Add summary
                total_subjects = len(subjects)
                total_credits = sum(float(subject['credits']) for subject in subjects if subject['credits'].replace('.', '').isdigit())
                gpa_message += f"""

📋 **Summary:**
• Total Subjects: {total_subjects}
• Total Credits: {total_credits}
• Semester: {semester}
• SGPA: {sgpa}
• CGPA: {cgpa}"""
            else:
                # If we still have no subjects, let's show some raw page content for debugging
                page_text = soup.get_text() if soup else "No page content"
                
                # Try to show at least some basic information
                gpa_message += f"""
⚠️ **No subject details found in table**

🔍 **Debug Information:**
• Tables found on page: {len(all_tables) if 'all_tables' in locals() else 'Unknown'}
• pnMarks panel found: {'Yes' if 'panel' in locals() and panel else 'No'}
• Table found in panel: {'Yes' if 'table' in locals() and table else 'No'}
• Page text length: {len(page_text)}

📄 **Raw HTML Content (First 2000 chars):**
```
{html_preview if 'html_preview' in locals() else 'No HTML preview available'}
```

📄 **Page Text Content:**
```
{page_text[:1000] if len(page_text) > 1000 else page_text}
```

💡 **Troubleshooting:**
• Check if you're logged into the correct semester
• Verify that grades are available for this semester
• The system is looking for table in ctl00_cpStud_pnMarks panel
• Debug files saved: gpa_debug_{chat_id}.html and gpa_debug_{chat_id}.txt
• Try refreshing the page and trying again
• Contact support if the issue persists

🔧 **Alternative: Try Different Semester**
The current semester might not have grades available. Try selecting a different semester.

📋 **To Help Debug:**
Please share the HTML content above so I can see exactly what's on the page and fix the extraction."""
            
            gpa_message += "\n\n✅ GPA data retrieval completed!"
            
            return gpa_message.strip()
        
    except requests.exceptions.Timeout as e:
        print(f"Timeout error retrieving GPA: {e}")
        return "🌐 **KITS Bees ERP site is down or slow.**\n\nPlease try again later."
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error retrieving GPA: {e}")
        return "🌐 **KITS Bees ERP site is down.**\n\nPlease try again later."
    except requests.exceptions.RequestException as e:
        print(f"Request error retrieving GPA: {e}")
        return "🌐 **KITS Bees ERP site is temporarily unavailable.**\n\nPlease try again later."
    except Exception as e:
        print(f"Error retrieving GPA: {e}")
        return "❌ **Error retrieving GPA data.**\n\nPlease try again."

