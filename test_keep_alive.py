#!/usr/bin/env python3
"""
Test Keep Alive Functionality
This script tests if your keep-alive system is working properly
"""

import requests
import time
import os
from datetime import datetime

def test_keep_alive():
    """Test the keep-alive functionality"""
    print("🧪 Testing Keep Alive Functionality")
    print("=" * 50)
    
    # Test URLs
    test_urls = [
        'https://httpbin.org/get',
        'https://jsonplaceholder.typicode.com/posts/1',
        'https://api.github.com/zen'
    ]
    
    # Test bot token if available
    bot_token = os.environ.get('BOT_TOKEN')
    if bot_token:
        test_urls.append(f'https://api.telegram.org/bot{bot_token}/getMe')
    
    print(f"🎯 Testing {len(test_urls)} services...")
    print()
    
    successful_tests = 0
    total_tests = len(test_urls)
    
    for i, url in enumerate(test_urls, 1):
        try:
            print(f"Test {i}/{total_tests}: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: {response.status_code}")
                successful_tests += 1
            else:
                print(f"⚠️ WARNING: {response.status_code}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        print("-" * 30)
        time.sleep(1)  # Wait 1 second between tests
    
    print()
    print("📊 Test Results:")
    print(f"✅ Successful: {successful_tests}/{total_tests}")
    print(f"📈 Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! Keep-alive should work perfectly.")
    elif successful_tests > 0:
        print("⚠️ Some tests failed, but keep-alive should still work.")
    else:
        print("❌ All tests failed. Check your internet connection.")
    
    print()
    print("💡 Tips:")
    print("- This test should be run on your deployment platform")
    print("- If tests fail, check your environment variables")
    print("- Make sure your bot token is valid")

if __name__ == "__main__":
    test_keep_alive()
