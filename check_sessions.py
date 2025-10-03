#!/usr/bin/env python3
"""
Check existing sessions in database
"""
import asyncio
import sys
sys.path.append('.')

from load_env import load_environment
from main_railway_complete_supabase import initialize_complete_supabase, supabase_client

async def check_sessions():
    """Check existing sessions in database"""
    load_environment()
    await initialize_complete_supabase()
    
    result = supabase_client._make_request('GET', 'user_sessions')
    print(f'Total sessions in database: {len(result) if result else 0}')
    
    if result:
        for session in result:
            chat_id = session.get('chat_id')
            username = session.get('username')
            print(f'Chat ID: {chat_id}, Username: {username}')
    else:
        print('No sessions found in database')

if __name__ == "__main__":
    asyncio.run(check_sessions())
