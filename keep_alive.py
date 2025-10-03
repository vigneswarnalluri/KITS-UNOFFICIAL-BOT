#!/usr/bin/env python3
"""
Keep Alive Script for 24/7 Bot Operation
This script ensures your bot stays online even on free hosting platforms
"""

import time
import requests
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keep_alive.log'),
        logging.StreamHandler()
    ]
)

class KeepAlive:
    def __init__(self):
        self.bot_token = os.environ.get('BOT_TOKEN')
        self.uptime_url = os.environ.get('UPTIME_URL', 'https://httpbin.org/get')
        self.interval = int(os.environ.get('KEEP_ALIVE_INTERVAL', '300'))  # 5 minutes default
        
    def ping_bot(self):
        """Ping the bot to keep it alive"""
        try:
            if self.bot_token:
                url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logging.info("✅ Bot ping successful")
                    return True
                else:
                    logging.warning(f"⚠️ Bot ping failed: {response.status_code}")
                    return False
            else:
                logging.warning("⚠️ No BOT_TOKEN found")
                return False
        except Exception as e:
            logging.error(f"❌ Bot ping error: {e}")
            return False
    
    def ping_uptime(self):
        """Ping uptime service to prevent sleep"""
        try:
            response = requests.get(self.uptime_url, timeout=10)
            if response.status_code == 200:
                logging.info("✅ Uptime ping successful")
                return True
            else:
                logging.warning(f"⚠️ Uptime ping failed: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"❌ Uptime ping error: {e}")
            return False
    
    def run(self):
        """Main keep alive loop"""
        logging.info("🚀 Keep Alive service started")
        logging.info(f"⏰ Ping interval: {self.interval} seconds")
        
        while True:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logging.info(f"🔄 Keep alive check at {current_time}")
                
                # Ping bot
                bot_status = self.ping_bot()
                
                # Ping uptime service
                uptime_status = self.ping_uptime()
                
                if bot_status and uptime_status:
                    logging.info("✅ All systems operational")
                else:
                    logging.warning("⚠️ Some services may be down")
                
                # Wait for next ping
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                logging.info("🛑 Keep alive service stopped by user")
                break
            except Exception as e:
                logging.error(f"❌ Keep alive error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    keep_alive = KeepAlive()
    keep_alive.run()
