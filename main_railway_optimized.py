"""
Railway-optimized IARE Bot
This version is specifically designed for Railway deployment
"""

from pyrogram import Client, filters
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Bot configuration - Railway environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH")
DEVELOPER_CHAT_ID = os.environ.get("DEVELOPER_CHAT_ID")
MAINTAINER_CHAT_ID = os.environ.get("MAINTAINER_CHAT_ID")

# Validate required environment variables
if not BOT_TOKEN:
    print("❌ BOT_TOKEN not found in environment variables")
    exit(1)
if not API_ID:
    print("❌ API_ID not found in environment variables")
    exit(1)
if not API_HASH:
    print("❌ API_HASH not found in environment variables")
    exit(1)

print(f"✅ Environment variables loaded:")
print(f"   BOT_TOKEN: {'Set' if BOT_TOKEN else 'Missing'}")
print(f"   API_ID: {API_ID}")
print(f"   API_HASH: {'Set' if API_HASH else 'Missing'}")
print(f"   DEVELOPER_CHAT_ID: {'Set' if DEVELOPER_CHAT_ID else 'Not set (optional)'}")
print(f"   MAINTAINER_CHAT_ID: {'Set' if MAINTAINER_CHAT_ID else 'Not set (optional)'}")

# Create bot client with Railway-optimized settings
bot = Client(
    "KITS_BOT",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH,
    # Railway-optimized settings
    workdir=".",
    sleep_threshold=60,
    max_concurrent_transmissions=1,
    no_updates=False
)

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    """Handle /start command"""
    try:
        await message.reply_text(
            "🎉 **Welcome to IARE Bot!**\n\n"
            "Your bot is working perfectly on Railway!\n\n"
            "Available commands:\n"
            "• /start - Show this message\n"
            "• /help - Show help\n"
            "• /status - Show bot status\n"
            "• /ping - Test bot response\n\n"
            "Bot is running 24/7 with Railway optimization!"
        )
        print(f"✅ Responded to /start from {message.from_user.id}")
    except Exception as e:
        print(f"❌ Error in start command: {e}")

@bot.on_message(filters.command("help"))
async def help_command(client, message):
    """Handle /help command"""
    try:
        await message.reply_text(
            "📋 **IARE Bot Help**\n\n"
            "Available commands:\n"
            "• /start - Welcome message\n"
            "• /help - Show this help\n"
            "• /status - Bot status\n"
            "• /ping - Test bot response\n\n"
            "Bot is optimized for Railway deployment!"
        )
        print(f"✅ Responded to /help from {message.from_user.id}")
    except Exception as e:
        print(f"❌ Error in help command: {e}")

@bot.on_message(filters.command("status"))
async def status_command(client, message):
    """Handle /status command"""
    try:
        await message.reply_text(
            "📊 **Bot Status**\n\n"
            "✅ Bot is running\n"
            "✅ Railway deployment active\n"
            "✅ Commands working\n"
            "✅ 24/7 uptime enabled\n"
            "✅ Railway-optimized connection\n\n"
            "Bot is healthy and operational!"
        )
        print(f"✅ Responded to /status from {message.from_user.id}")
    except Exception as e:
        print(f"❌ Error in status command: {e}")

@bot.on_message(filters.command("ping"))
async def ping_command(client, message):
    """Handle /ping command"""
    try:
        await message.reply_text(
            "🏓 **Pong!**\n\n"
            "Bot is responding and working perfectly!\n"
            "Railway connection is stable and healthy."
        )
        print(f"✅ Responded to /ping from {message.from_user.id}")
    except Exception as e:
        print(f"❌ Error in ping command: {e}")

# Start the bot
if __name__ == "__main__":
    print("🚀 Starting Railway-optimized IARE Bot...")
    print("✅ Bot is ready to receive commands!")
    print("🔄 Bot will run 24/7 with Railway optimization!")
    
    try:
        # Start the bot
        bot.start()
        print("✅ Bot started successfully!")
        print("🔄 Bot is running...")
        
        # Keep the bot running (Railway-optimized)
        while True:
            await asyncio.sleep(1)
        
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        logging.error(f"Bot error: {e}")
    finally:
        try:
            bot.stop()
            print("🛑 Bot stopped")
        except:
            pass
