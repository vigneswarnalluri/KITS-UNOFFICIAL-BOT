"""
Simplified main.py for Railway deployment
This version is optimized for stability and minimal resource usage
"""

from pyrogram import Client, filters, errors
import asyncio
import os
import logging
import time
from load_env import load_environment

# Load environment variables
load_environment()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_errors.log"),
        logging.StreamHandler()
    ]
)

# Bot configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

# Create bot client
session_name = "KITS_BOT"
bot = Client(
    session_name,
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    """Handle /start command"""
    try:
        await message.reply_text(
            "🎉 **Welcome to IARE Bot!**\n\n"
            "This is a simplified version running on Railway.\n"
            "Bot is working and responding to commands!\n\n"
            "Available commands:\n"
            "• /start - Show this message\n"
            "• /help - Show help\n"
            "• /status - Show bot status"
        )
        print(f"✅ Responded to /start from {message.from_user.id}")
    except Exception as e:
        print(f"❌ Error in start command: {e}")
        logging.error(f"Error in start command: {e}")

@bot.on_message(filters.command("help"))
async def help_command(client, message):
    """Handle /help command"""
    try:
        await message.reply_text(
            "📋 **IARE Bot Help**\n\n"
            "Available commands:\n"
            "• /start - Welcome message\n"
            "• /help - Show this help\n"
            "• /status - Bot status\n\n"
            "Bot is running on Railway cloud platform!"
        )
        print(f"✅ Responded to /help from {message.from_user.id}")
    except Exception as e:
        print(f"❌ Error in help command: {e}")
        logging.error(f"Error in help command: {e}")

@bot.on_message(filters.command("status"))
async def status_command(client, message):
    """Handle /status command"""
    try:
        await message.reply_text(
            "📊 **Bot Status**\n\n"
            "✅ Bot is running\n"
            "✅ Railway deployment active\n"
            "✅ Commands working\n"
            "✅ 24/7 uptime enabled\n\n"
            "Bot is healthy and operational!"
        )
        print(f"✅ Responded to /status from {message.from_user.id}")
    except Exception as e:
        print(f"❌ Error in status command: {e}")
        logging.error(f"Error in status command: {e}")

async def main():
    """Main bot function"""
    try:
        print("🚀 Starting IARE Bot on Railway...")
        print("📋 Bot configuration:")
        print(f"   Session: {session_name}")
        print(f"   Bot Token: {'Set' if BOT_TOKEN else 'Missing'}")
        print(f"   API ID: {'Set' if API_ID else 'Missing'}")
        print(f"   API Hash: {'Set' if API_HASH else 'Missing'}")
        
        # Start the bot
        await bot.start()
        print("✅ Bot started successfully!")
        print("🔄 Bot is now running 24/7!")
        
        # Keep the bot running
        print("🔄 Bot is running...")
        print("✅ Bot is ready to receive commands!")
        
        # Keep the bot running with proper event handling
        try:
            while True:
                await asyncio.sleep(0.1)  # Short sleep to allow event processing
        except KeyboardInterrupt:
            print("🛑 Bot stopped by user")
        except Exception as e:
            print(f"❌ Bot runtime error: {e}")
            logging.error(f"Bot runtime error: {e}")
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.error(f"Fatal error: {e}")
    finally:
        try:
            await bot.stop()
            print("🛑 Bot stopped")
        except:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        logging.error(f"Startup error: {e}")
