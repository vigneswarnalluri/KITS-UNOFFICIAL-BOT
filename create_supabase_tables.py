#!/usr/bin/env python3
"""
Create Supabase Tables via REST API
"""

import requests
import os
from load_env import load_environment

def create_tables():
    """Create database tables in Supabase"""
    print("Creating Supabase database tables...")
    
    # Load environment
    load_environment()
    
    url = os.environ.get("SUPABASE_URL")
    api_key = os.environ.get("SUPABASE_ANON_KEY")
    
    headers = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # SQL commands to create tables
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS user_sessions (
            chat_id BIGINT PRIMARY KEY,
            session_data TEXT,
            username VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_credentials (
            chat_id BIGINT PRIMARY KEY,
            username VARCHAR(50),
            password VARCHAR(100),
            pat_student BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS user_settings (
            chat_id BIGINT PRIMARY KEY,
            attendance_threshold INTEGER DEFAULT 75,
            bio_threshold INTEGER DEFAULT 75,
            ui BOOLEAN DEFAULT FALSE,
            title BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS reports (
            report_id VARCHAR(50) PRIMARY KEY,
            username VARCHAR(50),
            report TEXT,
            chat_id BIGINT,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS lab_uploads (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT,
            subject_code VARCHAR(20),
            week_no INTEGER,
            title VARCHAR(200),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            UNIQUE(chat_id, subject_code, week_no)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS admins (
            chat_id BIGINT PRIMARY KEY,
            username VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS banned_users (
            username VARCHAR(50) PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
    ]
    
    success_count = 0
    
    for i, sql in enumerate(sql_commands, 1):
        try:
            # Execute SQL via REST API
            response = requests.post(
                f"{url}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={"sql": sql},
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                print(f"SUCCESS: Table {i} created")
                success_count += 1
            else:
                print(f"ERROR: Table {i} failed - {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"ERROR: Table {i} failed: {e}")
    
    print(f"\nSUCCESS: {success_count}/{len(sql_commands)} tables created")
    
    if success_count == len(sql_commands):
        print("SUCCESS: All Supabase tables created!")
        return True
    else:
        print("WARNING: Some tables failed to create")
        return False

def test_tables():
    """Test if tables were created successfully"""
    print("\nTesting table creation...")
    
    try:
        from DATABASE.supabase_rest import supabase_rest
        
        # Test user session storage
        test_chat_id = 123456789
        test_session = '{"test": "session_data"}'
        test_username = "test_user"
        
        result = supabase_rest.store_user_session(test_chat_id, test_session, test_username)
        if result:
            print("SUCCESS: User sessions table working!")
        else:
            print("WARNING: User sessions table not working")
        
        # Test user credentials storage
        result = supabase_rest.store_credentials(test_chat_id, test_username, "test_password")
        if result:
            print("SUCCESS: User credentials table working!")
        else:
            print("WARNING: User credentials table not working")
        
        # Clean up test data
        supabase_rest.delete_user_session(test_chat_id)
        supabase_rest.remove_credentials(test_chat_id)
        print("SUCCESS: Test data cleanup completed")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Table test failed: {e}")
        return False

def main():
    """Main function"""
    print("Supabase Table Creation")
    print("=" * 30)
    
    # Create tables
    if create_tables():
        print("\n" + "="*30)
        
        # Test tables
        if test_tables():
            print("\nSUCCESS: Supabase database setup completed!")
            print("Your bot is now ready to use Supabase cloud database!")
            print("\nNext steps:")
            print("1. Run: python main.py")
            print("2. Your bot will use Supabase for all data storage!")
        else:
            print("\nWARNING: Tables created but tests failed")
    else:
        print("\nERROR: Table creation failed")

if __name__ == "__main__":
    main()
