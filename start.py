#!/usr/bin/env python3
"""
Startup script for Render deployment
This script ensures the bot starts correctly on Render
"""

import os
import sys
import subprocess

def main():
    """Start the bot with proper error handling"""
    print("🚀 Starting IARE Bot on Render...")
    
    # Check if main.py exists
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found!")
        print("📁 Current directory contents:")
        for file in os.listdir('.'):
            print(f"  - {file}")
        sys.exit(1)
    
    # Start the bot
    try:
        print("✅ main.py found, starting bot...")
        subprocess.run([sys.executable, 'main.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Bot failed to start: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
