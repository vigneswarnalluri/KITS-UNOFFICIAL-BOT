import asyncpg
import os
import json
from typing import Optional, Dict, Any, List

class SupabaseDatabase:
    """
    Supabase database handler for the KITS Bot
    Supabase uses PostgreSQL, so we can use asyncpg with Supabase credentials
    """
    
    def __init__(self):
        self.connection_pool = None
        
    async def get_connection(self):
        """Get a connection from the pool"""
        if not self.connection_pool:
            await self.create_pool()
        return await self.connection_pool.acquire()
    
    async def create_pool(self):
        """Create connection pool for Supabase"""
        try:
            self.connection_pool = await asyncpg.create_pool(
                user=os.environ.get("SUPABASE_USER"),
                password=os.environ.get("SUPABASE_PASSWORD"),
                database=os.environ.get("SUPABASE_DATABASE"),
                host=os.environ.get("SUPABASE_HOST"),
                port=os.environ.get("SUPABASE_PORT"),
                min_size=1,
                max_size=10
            )
            print("Supabase connection pool created successfully")
        except Exception as e:
            print(f"Error creating Supabase connection pool: {e}")
            raise e
    
    async def close_pool(self):
        """Close the connection pool"""
        if self.connection_pool:
            await self.connection_pool.close()
    
    # User Sessions Management
    async def store_user_session(self, chat_id: int, session_data: str, username: str):
        """Store user session data"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO user_sessions (chat_id, session_data, username, created_at, updated_at)
                VALUES ($1, $2, $3, NOW(), NOW())
                ON CONFLICT (chat_id) 
                DO UPDATE SET session_data = $2, username = $3, updated_at = NOW()
            """, chat_id, session_data, username)
    
    async def load_user_session(self, chat_id: int) -> Optional[str]:
        """Load user session data"""
        async with self.get_connection() as conn:
            result = await conn.fetchrow("""
                SELECT session_data FROM user_sessions 
                WHERE chat_id = $1
            """, chat_id)
            return result['session_data'] if result else None
    
    async def delete_user_session(self, chat_id: int):
        """Delete user session"""
        async with self.get_connection() as conn:
            await conn.execute("""
                DELETE FROM user_sessions WHERE chat_id = $1
            """, chat_id)
    
    # User Credentials Management
    async def store_credentials(self, chat_id: int, username: str, password: str, pat_student: bool = False):
        """Store user credentials"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO user_credentials (chat_id, username, password, pat_student, created_at, updated_at)
                VALUES ($1, $2, $3, $4, NOW(), NOW())
                ON CONFLICT (chat_id) 
                DO UPDATE SET username = $2, password = $3, pat_student = $4, updated_at = NOW()
            """, chat_id, username, password, pat_student)
    
    async def retrieve_credentials(self, chat_id: int) -> Optional[tuple]:
        """Retrieve user credentials"""
        async with self.get_connection() as conn:
            result = await conn.fetchrow("""
                SELECT username, password FROM user_credentials 
                WHERE chat_id = $1
            """, chat_id)
            return (result['username'], result['password']) if result else None
    
    async def remove_credentials(self, chat_id: int):
        """Remove user credentials"""
        async with self.get_connection() as conn:
            await conn.execute("""
                DELETE FROM user_credentials WHERE chat_id = $1
            """, chat_id)
    
    # User Settings Management
    async def store_user_settings(self, chat_id: int, attendance_threshold: int, bio_threshold: int, ui: bool, title: bool):
        """Store user settings"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO user_settings (chat_id, attendance_threshold, bio_threshold, ui, title, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                ON CONFLICT (chat_id) 
                DO UPDATE SET attendance_threshold = $2, bio_threshold = $3, ui = $4, title = $5, updated_at = NOW()
            """, chat_id, attendance_threshold, bio_threshold, ui, title)
    
    async def fetch_user_settings(self, chat_id: int) -> Optional[tuple]:
        """Fetch user settings"""
        async with self.get_connection() as conn:
            result = await conn.fetchrow("""
                SELECT attendance_threshold, bio_threshold, ui, title 
                FROM user_settings WHERE chat_id = $1
            """, chat_id)
            return (result['attendance_threshold'], result['bio_threshold'], result['ui'], result['title']) if result else None
    
    # Reports Management
    async def store_report(self, report_id: str, username: str, report: str, chat_id: int, status: str = "pending"):
        """Store user report"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO reports (report_id, username, report, chat_id, status, created_at)
                VALUES ($1, $2, $3, $4, $5, NOW())
            """, report_id, username, report, chat_id, status)
    
    async def fetch_reports(self) -> List[Dict[str, Any]]:
        """Fetch all reports"""
        async with self.get_connection() as conn:
            results = await conn.fetch("""
                SELECT * FROM reports ORDER BY created_at DESC
            """)
            return [dict(row) for row in results]
    
    # Lab Uploads Management
    async def store_lab_upload(self, chat_id: int, subject_code: str, week_no: int, title: str):
        """Store lab upload data"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO lab_uploads (chat_id, subject_code, week_no, title, created_at)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (chat_id, subject_code, week_no) 
                DO UPDATE SET title = $4, updated_at = NOW()
            """, chat_id, subject_code, week_no, title)
    
    async def fetch_lab_uploads(self, chat_id: int) -> List[Dict[str, Any]]:
        """Fetch lab uploads for a user"""
        async with self.get_connection() as conn:
            results = await conn.fetch("""
                SELECT * FROM lab_uploads WHERE chat_id = $1 ORDER BY created_at DESC
            """, chat_id)
            return [dict(row) for row in results]
    
    # Admin Management
    async def add_admin(self, chat_id: int, username: str):
        """Add admin"""
        async with self.get_connection() as conn:
            await conn.execute("""
                INSERT INTO admins (chat_id, username, created_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (chat_id) DO NOTHING
            """, chat_id, username)
    
    async def remove_admin(self, chat_id: int):
        """Remove admin"""
        async with self.get_connection() as conn:
            await conn.execute("""
                DELETE FROM admins WHERE chat_id = $1
            """, chat_id)
    
    async def fetch_admins(self) -> List[int]:
        """Fetch all admin chat IDs"""
        async with self.get_connection() as conn:
            results = await conn.fetch("""
                SELECT chat_id FROM admins
            """)
            return [row['chat_id'] for row in results]
    
    # Database Schema Creation
    async def create_all_tables(self):
        """Create all required tables in Supabase"""
        async with self.get_connection() as conn:
            # User Sessions Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    chat_id BIGINT PRIMARY KEY,
                    session_data TEXT,
                    username VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # User Credentials Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_credentials (
                    chat_id BIGINT PRIMARY KEY,
                    username VARCHAR(50),
                    password VARCHAR(100),
                    pat_student BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # User Settings Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    chat_id BIGINT PRIMARY KEY,
                    attendance_threshold INTEGER DEFAULT 75,
                    bio_threshold INTEGER DEFAULT 75,
                    ui BOOLEAN DEFAULT FALSE,
                    title BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Reports Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    report_id VARCHAR(50) PRIMARY KEY,
                    username VARCHAR(50),
                    report TEXT,
                    chat_id BIGINT,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Lab Uploads Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS lab_uploads (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT,
                    subject_code VARCHAR(20),
                    week_no INTEGER,
                    title VARCHAR(200),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(chat_id, subject_code, week_no)
                )
            """)
            
            # Admins Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    chat_id BIGINT PRIMARY KEY,
                    username VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Banned Users Table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS banned_users (
                    username VARCHAR(50) PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            print("All Supabase tables created successfully")

# Global instance
supabase_db = SupabaseDatabase()
