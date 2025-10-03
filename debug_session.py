#!/usr/bin/env python3
"""
Debug script to test session validation
"""
import asyncio
import sys
import os
sys.path.append('.')

from load_env import load_environment
from main_railway_complete_supabase import load_user_session, validate_session, initialize_complete_supabase

async def debug_session(chat_id):
    """Debug session for a specific chat_id"""
    print(f"🔍 DEBUGGING SESSION for chat_id: {chat_id}")
    
    # Load environment
    load_environment()
    
    # Initialize Supabase
    print("🔧 Initializing Supabase...")
    await initialize_complete_supabase()
    print("✅ Supabase initialized")
    
    # Load session data
    session_data = await load_user_session(chat_id)
    print(f"📊 Session data loaded: {session_data is not None}")
    
    if session_data:
        print(f"📋 Session keys: {list(session_data.keys())}")
        print(f"🍪 Has cookies: {'cookies' in session_data}")
        if 'cookies' in session_data:
            print(f"🍪 Cookie count: {len(session_data['cookies'])}")
            print(f"🍪 Cookie names: {list(session_data['cookies'].keys())}")
        
        # Test session validation
        print("🧪 Testing session validation...")
        is_valid = await validate_session(chat_id)
        print(f"✅ Session validation result: {is_valid}")
    else:
        print("❌ No session data found")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_session.py <chat_id>")
        sys.exit(1)
    
    chat_id = int(sys.argv[1])
    asyncio.run(debug_session(chat_id))
