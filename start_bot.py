#!/usr/bin/env python3
"""
Enhanced Bot Startup Script with 24/7 Monitoring
This script ensures your bot runs continuously with automatic restarts
"""

import os
import sys
import time
import logging
import subprocess
import signal
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_startup.log'),
        logging.StreamHandler()
    ]
)

class BotManager:
    def __init__(self):
        self.bot_process = None
        self.restart_count = 0
        self.max_restarts = 10
        self.restart_delay = 5
        
    def start_bot(self):
        """Start the bot process"""
        try:
            logging.info("🚀 Starting IARE Bot...")
            self.bot_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logging.info(f"✅ Bot started with PID: {self.bot_process.pid}")
            return True
        except Exception as e:
            logging.error(f"❌ Failed to start bot: {e}")
            return False
    
    def stop_bot(self):
        """Stop the bot process"""
        if self.bot_process:
            try:
                logging.info("🛑 Stopping bot...")
                self.bot_process.terminate()
                self.bot_process.wait(timeout=10)
                logging.info("✅ Bot stopped successfully")
            except subprocess.TimeoutExpired:
                logging.warning("⚠️ Force killing bot...")
                self.bot_process.kill()
            except Exception as e:
                logging.error(f"❌ Error stopping bot: {e}")
    
    def is_bot_running(self):
        """Check if bot is still running"""
        if self.bot_process:
            return self.bot_process.poll() is None
        return False
    
    def restart_bot(self):
        """Restart the bot if it has stopped"""
        if not self.is_bot_running():
            self.restart_count += 1
            logging.warning(f"🔄 Bot stopped, restarting... (Attempt {self.restart_count})")
            
            if self.restart_count <= self.max_restarts:
                time.sleep(self.restart_delay)
                if self.start_bot():
                    logging.info("✅ Bot restarted successfully")
                else:
                    logging.error("❌ Failed to restart bot")
            else:
                logging.error(f"❌ Max restarts ({self.max_restarts}) reached. Stopping.")
                return False
        return True
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logging.info("🛑 Received shutdown signal")
        self.stop_bot()
        sys.exit(0)
    
    def run(self):
        """Main bot management loop"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        logging.info("🎯 IARE Bot Manager started")
        logging.info(f"📊 Max restarts: {self.max_restarts}")
        logging.info(f"⏰ Restart delay: {self.restart_delay} seconds")
        
        # Start bot initially
        if not self.start_bot():
            logging.error("❌ Failed to start bot initially")
            return
        
        # Main monitoring loop
        while True:
            try:
                if not self.is_bot_running():
                    if not self.restart_bot():
                        break
                
                # Check every 30 seconds
                time.sleep(30)
                
                # Log status every 5 minutes
                if int(time.time()) % 300 == 0:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    logging.info(f"📊 Bot status check at {current_time}")
                    logging.info(f"🔄 Restart count: {self.restart_count}")
                
            except KeyboardInterrupt:
                logging.info("🛑 Bot manager stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Bot manager error: {e}")
                time.sleep(60)
        
        # Cleanup
        self.stop_bot()
        logging.info("👋 Bot manager shutdown complete")

if __name__ == "__main__":
    manager = BotManager()
    manager.run()
