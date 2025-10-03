#!/usr/bin/env python3
"""
Cleanup script to remove temporary files created by the bot
Run this script when the bot is not running to clean up old files
"""

import os
import glob

def cleanup_bot_files():
    """Clean up all temporary files created by the bot"""
    files_to_remove = []
    
    # Remove old session files
    for session_file in glob.glob("KITS_BOT_*.session*"):
        files_to_remove.append(session_file)
    
    # Remove log files
    if os.path.exists("bot_errors.log"):
        files_to_remove.append("bot_errors.log")
    
    # Remove database files (optional - uncomment if you want to reset all data)
    # db_files = ["credentials.db", "labuploads.db", "managers.db", "reports.db", 
    #            "total_users.db", "user_sessions.db", "user_settings.db"]
    # for db_file in db_files:
    #     if os.path.exists(db_file):
    #         files_to_remove.append(db_file)
    
    # Remove __pycache__ directories
    for pycache_dir in glob.glob("**/__pycache__", recursive=True):
        files_to_remove.append(pycache_dir)
    
    # Remove files
    removed_count = 0
    for file_path in files_to_remove:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"✅ Removed file: {file_path}")
                removed_count += 1
            elif os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)
                print(f"✅ Removed directory: {file_path}")
                removed_count += 1
        except Exception as e:
            print(f"❌ Could not remove {file_path}: {e}")
    
    print(f"\n🎉 Cleanup complete! Removed {removed_count} files/directories")
    
    if removed_count == 0:
        print("✨ No files to clean up - your project is already clean!")

if __name__ == "__main__":
    print("🧹 Starting bot cleanup...")
    cleanup_bot_files()
