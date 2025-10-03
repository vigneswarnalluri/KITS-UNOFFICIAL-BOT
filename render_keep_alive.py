#!/usr/bin/env python3
"""
Render.com Keep Alive Script
This script prevents your bot from sleeping on Render's free tier
by making periodic requests to keep it active.
"""

import os
import time
import requests
import threading
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('render_keep_alive.log'),
        logging.StreamHandler()
    ]
)

class RenderKeepAlive:
    def __init__(self):
        self.bot_token = os.environ.get('BOT_TOKEN')
        self.render_url = os.environ.get('RENDER_URL', 'https://httpbin.org/get')
        self.interval = int(os.environ.get('KEEP_ALIVE_INTERVAL', '300'))  # 5 minutes default
        self.running = True
        
    def ping_render(self):
        """Ping external service to keep Render awake"""
        try:
            response = requests.get(self.render_url, timeout=10)
            if response.status_code == 200:
                logging.info("✅ Render keep-alive ping successful")
                return True
            else:
                logging.warning(f"⚠️ Render ping failed: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"❌ Render ping error: {e}")
            return False
    
    def ping_bot(self):
        """Ping the bot to keep it active"""
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
    
    def keep_alive_loop(self):
        """Main keep alive loop"""
        logging.info("🚀 Render Keep Alive service started")
        logging.info(f"⏰ Ping interval: {self.interval} seconds")
        logging.info(f"🌐 Render URL: {self.render_url}")
        
        while self.running:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logging.info(f"🔄 Keep alive check at {current_time}")
                
                # Ping external service to keep Render awake
                render_status = self.ping_render()
                
                # Ping bot to keep it active
                bot_status = self.ping_bot()
                
                if render_status and bot_status:
                    logging.info("✅ All keep-alive pings successful")
                else:
                    logging.warning("⚠️ Some keep-alive pings failed")
                
                # Wait for next ping
                time.sleep(self.interval)
                
            except Exception as e:
                logging.error(f"❌ Keep alive error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def start(self):
        """Start the keep alive service"""
        self.keep_alive_loop()
    
    def stop(self):
        """Stop the keep alive service"""
        self.running = False
        logging.info("🛑 Render Keep Alive service stopped")

if __name__ == "__main__":
    keep_alive = RenderKeepAlive()
    try:
        keep_alive.start()
    except KeyboardInterrupt:
        logging.info("🛑 Keep alive service stopped by user")
        keep_alive.stop()
