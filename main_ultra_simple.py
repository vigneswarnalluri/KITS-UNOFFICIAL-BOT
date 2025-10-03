"""
Ultra-simple main.py for Railway deployment
This version uses the most basic Pyrogram setup
"""

from pyrogram import Client, filters
import os
import asyncio

# Bot configuration
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")

# Create bot client
bot = Client(
    "KITS_BOT",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    """Handle /start command"""
    await message.reply_text(
        "🎉 **Welcome to IARE Bot!**\n\n"
        "Bot is working and responding to commands!\n\n"
        "Available commands:\n"
        "• /start - Show this message\n"
        "• /help - Show help\n"
        "• /status - Show bot status"
    )
    print(f"✅ Responded to /start from {message.from_user.id}")

@bot.on_message(filters.command("help"))
async def help_command(client, message):
    """Handle /help command"""
    await message.reply_text(
        "📋 **IARE Bot Help**\n\n"
        "Available commands:\n"
        "• /start - Welcome message\n"
        "• /help - Show this help\n"
        "• /status - Bot status\n\n"
        "Bot is running on Railway!"
    )
    print(f"✅ Responded to /help from {message.from_user.id}")

@bot.on_message(filters.command("status"))
async def status_command(client, message):
    """Handle /status command"""
    await message.reply_text(
        "📊 **Bot Status**\n\n"
        "✅ Bot is running\n"
        "✅ Railway deployment active\n"
        "✅ Commands working\n"
        "✅ 24/7 uptime enabled\n\n"
        "Bot is healthy and operational!"
    )
    print(f"✅ Responded to /status from {message.from_user.id}")

# Start the bot
if __name__ == "__main__":
    print("🚀 Starting IARE Bot on Railway...")
    print("✅ Bot is ready to receive commands!")
    bot.run()
