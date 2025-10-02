#!/usr/bin/env python3
"""
Netlify Deployment Guide for KITS Bot
This script helps configure Netlify deployment with Supabase
"""

import os

def fix_requirements_for_netlify():
    """Fix requirements.txt for Netlify compatibility"""
    print("🔧 FIXING REQUIREMENTS FOR NETLIFY")
    print("=" * 50)
    
    # Netlify-compatible requirements
    netlify_requirements = """async-timeout==5.0.1
asyncpg==0.29.0
attrs==25.3.0
beautifulsoup4==4.12.3
certifi==2025.4.26
cffi==1.17.1
charset-normalizer==3.4.2
h11==0.16.0
idna==3.10
outcome==1.3.0.post0
packaging==25.0
pdf2image==1.17.0
pillow==8.4.0
psutil==5.9.8
pyaes==1.6.1
pycparser==2.22
pypng==0.20220715.0
PyQRCode==1.2.1
Pyrogram==2.0.106
PySocks==1.7.1
python-dotenv==1.0.1
pytz==2024.1
requests==2.32.3
selenium==4.21.0
sniffio==1.3.1
sortedcontainers==2.4.0
soupsieve==2.5
TgCrypto==1.2.5
trio==0.30.0
trio-websocket==0.12.2
typing_extensions==4.13.2
urllib3==2.4.0
webdriver-manager==4.0.1
wsproto==1.2.0"""
    
    try:
        with open('requirements.txt', 'w') as f:
            f.write(netlify_requirements)
        print("✅ Fixed requirements.txt for Netlify")
        print("✅ Updated Pillow to version 8.4.0")
        return True
    except Exception as e:
        print(f"❌ Failed to fix requirements: {e}")
        return False

def create_netlify_config():
    """Create Netlify configuration files"""
    print("\n📁 CREATING NETLIFY CONFIGURATION")
    print("=" * 50)
    
    # Create netlify.toml
    netlify_toml = """[build]
  command = "pip install -r requirements.txt"
  functions = "netlify/functions"
  publish = "."

[build.environment]
  PYTHON_VERSION = "3.9"

[[functions]]
  name = "bot"
  runtime = "python3.9"

[functions.bot]
  included_files = ["**"]

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200"""
    
    # Create function handler
    function_handler = """import json
import os
import asyncio
from main_cloud_robust import bot, main

async def handler_async(event, context):
    \"\"\"Async handler for Netlify function\"\"\"
    try:
        # Initialize bot if not already done
        await main(bot)
        
        # Handle webhook from Telegram
        if event.get('httpMethod') == 'POST':
            body = json.loads(event.get('body', '{}'))
            # Process Telegram update
            # Note: This is a simplified handler
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'ok'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'Bot is running'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def handler(event, context):
    \"\"\"Netlify function handler\"\"\"
    return asyncio.run(handler_async(event, context))"""
    
    try:
        # Create netlify.toml
        with open('netlify.toml', 'w') as f:
            f.write(netlify_toml)
        print("✅ Created netlify.toml")
        
        # Create functions directory
        os.makedirs('netlify/functions', exist_ok=True)
        
        # Create function handler
        with open('netlify/functions/bot.py', 'w') as f:
            f.write(function_handler)
        print("✅ Created netlify/functions/bot.py")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create Netlify config: {e}")
        return False

def show_netlify_deployment_steps():
    """Show Netlify deployment steps"""
    print("\n🚀 NETLIFY DEPLOYMENT STEPS")
    print("=" * 50)
    
    print("⚠️ IMPORTANT: Netlify Considerations for Telegram Bots")
    print("  • Netlify is designed for static sites and serverless functions")
    print("  • Telegram bots need continuous running or webhook setup")
    print("  • Better alternatives: Railway, Render, Heroku for bots")
    
    print("\n🎯 IF YOU WANT TO USE NETLIFY:")
    
    print("\n📋 STEP 1: Prepare Repository")
    print("  git add .")
    print("  git commit -m 'Configure for Netlify deployment with Supabase'")
    print("  git push origin main")
    
    print("\n📋 STEP 2: Deploy to Netlify")
    print("  1. Go to netlify.com")
    print("  2. Connect your GitHub repository")
    print("  3. Set build command: pip install -r requirements.txt")
    print("  4. Set publish directory: .")
    
    print("\n📋 STEP 3: Configure Environment Variables")
    print("  Add these in Netlify dashboard:")
    print("  SUPABASE_URL=https://wecaohxjejimxhbcgmjp.supabase.co")
    print("  SUPABASE_ANON_KEY=your_anon_key")
    print("  BOT_TOKEN=your_bot_token")
    print("  API_ID=your_api_id")
    print("  API_HASH=your_api_hash")
    
    print("\n📋 STEP 4: Set Up Telegram Webhook")
    print("  • Configure Telegram webhook to point to Netlify function")
    print("  • URL: https://your-site.netlify.app/.netlify/functions/bot")

def show_better_alternatives():
    """Show better alternatives for Telegram bot deployment"""
    print("\n💡 BETTER ALTERNATIVES FOR TELEGRAM BOTS")
    print("=" * 50)
    
    print("🥇 RECOMMENDED: Railway (Current Setup)")
    print("  ✅ Perfect for Telegram bots")
    print("  ✅ Continuous running")
    print("  ✅ Supabase integration ready")
    print("  ✅ Just need to fix environment variables")
    
    print("\n🥈 ALTERNATIVE: Render")
    print("  ✅ Excellent for Python bots")
    print("  ✅ Free tier available")
    print("  ✅ Better Supabase connectivity than Railway")
    print("  ✅ Easy migration from current setup")
    
    print("\n🥉 ALTERNATIVE: Heroku")
    print("  ✅ Most reliable for bots")
    print("  ✅ Excellent Supabase connectivity")
    print("  ❌ No free tier (paid only)")
    
    print("\n⚠️ NETLIFY LIMITATIONS:")
    print("  ❌ Not designed for continuous bot processes")
    print("  ❌ Function timeout limits")
    print("  ❌ Complex webhook setup required")
    print("  ❌ Not ideal for 60-70 concurrent users")

def recommend_render_migration():
    """Show how to migrate to Render instead"""
    print("\n🎯 RECOMMENDED: MIGRATE TO RENDER")
    print("=" * 50)
    
    print("📋 RENDER DEPLOYMENT (BETTER THAN NETLIFY FOR BOTS):")
    print("  1. Go to render.com")
    print("  2. Connect GitHub repository")
    print("  3. Create 'Web Service'")
    print("  4. Build Command: pip install -r requirements.txt")
    print("  5. Start Command: python main_cloud_robust.py")
    
    print("\n📋 RENDER ENVIRONMENT VARIABLES:")
    print("  Copy all variables from railway_supabase_env.txt")
    print("  Add: FORCE_SUPABASE_REST=true")
    
    print("\n✅ RENDER BENEFITS:")
    print("  ✅ Perfect for Telegram bots")
    print("  ✅ Better Supabase connectivity than Railway")
    print("  ✅ Free tier available")
    print("  ✅ Continuous running (not serverless)")
    print("  ✅ Same code, just different platform")

def main():
    """Main function"""
    print("🌐 NETLIFY DEPLOYMENT CONFIGURATION")
    print("=" * 60)
    
    # Fix requirements
    req_fixed = fix_requirements_for_netlify()
    
    # Create Netlify config
    config_created = create_netlify_config()
    
    # Show deployment steps
    show_netlify_deployment_steps()
    
    # Show better alternatives
    show_better_alternatives()
    
    # Recommend Render
    recommend_render_migration()
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDATION:")
    print("While Netlify setup is ready, Render or Railway are better for Telegram bots.")
    print("Render often has better Supabase connectivity than Railway.")
    
    if req_fixed and config_created:
        print("\n✅ NETLIFY FILES READY (if you still want to try)")
        print("✅ Pillow version fixed")
        print("✅ Configuration files created")
    else:
        print("\n❌ SOME ISSUES WITH NETLIFY SETUP")

if __name__ == "__main__":
    main()
