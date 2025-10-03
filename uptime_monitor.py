#!/usr/bin/env python3
"""
Uptime Monitor for Render.com
This script monitors your bot and keeps it awake on Render's free tier
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
        logging.FileHandler('uptime_monitor.log'),
        logging.StreamHandler()
    ]
)

class UptimeMonitor:
    def __init__(self):
        self.bot_token = os.environ.get('BOT_TOKEN')
        self.monitor_urls = [
            'https://httpbin.org/get',
            'https://api.telegram.org/bot{}/getMe'.format(self.bot_token) if self.bot_token else None,
            'https://jsonplaceholder.typicode.com/posts/1',
            'https://api.github.com/zen'
        ]
        self.interval = 300  # 5 minutes
        self.running = True
        
    def ping_service(self, url):
        """Ping a service to keep Render awake"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                logging.info(f"✅ Ping successful: {url}")
                return True
            else:
                logging.warning(f"⚠️ Ping failed: {url} - Status: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"❌ Ping error: {url} - {e}")
            return False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        logging.info("🚀 Uptime Monitor started")
        logging.info(f"⏰ Monitor interval: {self.interval} seconds")
        logging.info(f"🎯 Monitoring {len(self.monitor_urls)} services")
        
        while self.running:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                logging.info(f"🔄 Uptime check at {current_time}")
                
                successful_pings = 0
                total_pings = 0
                
                for url in self.monitor_urls:
                    if url:  # Skip None URLs
                        total_pings += 1
                        if self.ping_service(url):
                            successful_pings += 1
                
                if successful_pings > 0:
                    logging.info(f"✅ {successful_pings}/{total_pings} pings successful")
                else:
                    logging.warning("⚠️ No successful pings")
                
                # Wait for next check
                time.sleep(self.interval)
                
            except Exception as e:
                logging.error(f"❌ Monitor error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def start(self):
        """Start the uptime monitor"""
        self.monitor_loop()
    
    def stop(self):
        """Stop the uptime monitor"""
        self.running = False
        logging.info("🛑 Uptime Monitor stopped")

if __name__ == "__main__":
    monitor = UptimeMonitor()
    try:
        monitor.start()
    except KeyboardInterrupt:
        logging.info("🛑 Monitor stopped by user")
        monitor.stop()
