#!/usr/bin/env python3
"""
Bot Diagnostic Script
This script helps identify why your bot isn't working
"""

import os
import sys
import requests
from datetime import datetime

def check_environment():
    """Check if all required environment variables are set"""
    print("🔍 Checking Environment Variables...")
    print("=" * 50)
    
    required_vars = [
        'BOT_TOKEN',
        'API_ID', 
        'API_HASH',
        'DEVELOPER_CHAT_ID',
        'MAINTAINER_CHAT_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'TOKEN' in var or 'ID' in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing variables: {', '.join(missing_vars)}")
        return False
    else:
        print("\n✅ All environment variables are set!")
        return True

def test_bot_token():
    """Test if bot token is valid"""
    print("\n🤖 Testing Bot Token...")
    print("=" * 50)
    
    bot_token = os.environ.get('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN not found")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Bot is valid!")
                print(f"   Name: {bot_info.get('first_name', 'Unknown')}")
                print(f"   Username: @{bot_info.get('username', 'Unknown')}")
                print(f"   ID: {bot_info.get('id', 'Unknown')}")
                return True
            else:
                print(f"❌ Bot API error: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are available"""
    print("\n📦 Testing Dependencies...")
    print("=" * 50)
    
    required_modules = [
        'pyrogram',
        'asyncio',
        'sqlite3',
        'requests',
        'threading'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️ Missing modules: {', '.join(missing_modules)}")
        return False
    else:
        print("\n✅ All dependencies available!")
        return True

def test_database():
    """Test database connectivity"""
    print("\n🗄️ Testing Database...")
    print("=" * 50)
    
    try:
        import sqlite3
        # Test SQLite
        conn = sqlite3.connect(':memory:')
        conn.execute('CREATE TABLE test (id INTEGER)')
        conn.execute('INSERT INTO test VALUES (1)')
        result = conn.execute('SELECT * FROM test').fetchone()
        conn.close()
        
        if result and result[0] == 1:
            print("✅ SQLite database working!")
            return True
        else:
            print("❌ SQLite database test failed")
            return False
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🔧 IARE Bot Diagnostic Tool")
    print("=" * 50)
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print()
    
    # Run all tests
    tests = [
        ("Environment Variables", check_environment),
        ("Bot Token", test_bot_token),
        ("Dependencies", test_dependencies),
        ("Database", test_database)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your bot should be working.")
        print("\n💡 If bot still not working:")
        print("   1. Check Railway logs")
        print("   2. Verify service is running")
        print("   3. Test bot commands on Telegram")
    else:
        print("⚠️ Some tests failed. Fix the issues above.")
        print("\n💡 Common fixes:")
        print("   1. Set missing environment variables")
        print("   2. Check bot token with @BotFather")
        print("   3. Install missing dependencies")
        print("   4. Redeploy service")

if __name__ == "__main__":
    main()
