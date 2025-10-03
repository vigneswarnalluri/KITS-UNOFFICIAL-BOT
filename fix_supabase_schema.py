#!/usr/bin/env python3
"""
Fix Supabase Schema - Add missing columns to user_settings table
"""

import os
import asyncio
from DATABASE.supabase_database import supabase_db
from load_env import load_environment

async def fix_supabase_schema():
    """Fix the Supabase schema by adding missing columns"""
    
    # Load environment variables
    load_environment()
    
    try:
        # Initialize Supabase connection
        await supabase_db.create_pool()
        print("✅ Connected to Supabase")
        
        # Add missing biometric_threshold column to user_settings table
        print("🔧 Adding biometric_threshold column to user_settings table...")
        
        # SQL to add the missing column
        alter_sql = """
        ALTER TABLE user_settings 
        ADD COLUMN IF NOT EXISTS biometric_threshold INTEGER DEFAULT 75;
        """
        
        # Execute the SQL
        result = await supabase_db.execute_sql(alter_sql)
        print(f"✅ Added biometric_threshold column: {result}")
        
        # Verify the table structure
        print("🔍 Verifying table structure...")
        verify_sql = """
        SELECT column_name, data_type, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'user_settings' 
        ORDER BY ordinal_position;
        """
        
        columns = await supabase_db.execute_sql(verify_sql)
        print("📋 Current user_settings table structure:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (default: {col['column_default']})")
        
        print("✅ Supabase schema fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing Supabase schema: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(fix_supabase_schema())
