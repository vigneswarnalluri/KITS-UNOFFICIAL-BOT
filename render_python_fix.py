#!/usr/bin/env python3
"""
Fix Python Version for Render Deployment
Force Python 3.9 to avoid Pillow compatibility issues
"""

def create_python_version_files():
    """Create files to force Python 3.9 on Render"""
    print("🐍 FORCING PYTHON 3.9 FOR RENDER")
    print("=" * 50)
    
    # Create runtime.txt (Render standard)
    with open('runtime.txt', 'w') as f:
        f.write('python-3.9.18\n')
    print("✅ Created runtime.txt with Python 3.9.18")
    
    # Create .python-version (alternative method)
    with open('.python-version', 'w') as f:
        f.write('3.9.18\n')
    print("✅ Created .python-version with 3.9.18")
    
    # Update render.yaml with explicit Python version
    render_yaml = """services:
  - type: web
    name: kits-bot
    env: python
    runtime: python39
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: python main_cloud_robust.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
      - key: CONTAINER_DEPLOYMENT
        value: true
      - key: FORCE_SUPABASE_REST
        value: true"""
    
    with open('render.yaml', 'w') as f:
        f.write(render_yaml)
    print("✅ Updated render.yaml with Python 3.9 runtime")
    
    return True

def create_pillow_compatible_requirements():
    """Create requirements with Pillow version that works with Python 3.9"""
    print("\n📦 CREATING PYTHON 3.9 COMPATIBLE REQUIREMENTS")
    print("=" * 50)
    
    # Use Pillow version specifically tested with Python 3.9
    requirements = """async-timeout==4.0.3
asyncpg==0.28.0
attrs==23.1.0
beautifulsoup4==4.12.2
certifi==2023.7.22
cffi==1.15.1
charset-normalizer==3.2.0
h11==0.14.0
idna==3.4
outcome==1.2.0
packaging==23.1
pdf2image==1.16.3
pillow==8.4.0
psutil==5.9.5
pyaes==1.6.1
pycparser==2.21
pypng==0.20220715.0
PyQRCode==1.2.1
Pyrogram==2.0.106
PySocks==1.7.1
python-dotenv==1.0.0
pytz==2023.3
requests==2.31.0
selenium==4.11.2
sniffio==1.3.0
sortedcontainers==2.4.0
soupsieve==2.5
TgCrypto==1.2.5
trio==0.22.2
trio-websocket==0.10.3
typing_extensions==4.7.1
urllib3==2.0.4
webdriver-manager==4.0.0
wsproto==1.2.0"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("✅ Updated requirements.txt with Pillow 8.4.0 (Python 3.9 compatible)")
    
    return True

def show_render_fix_steps():
    """Show steps to fix Render deployment"""
    print("\n🚀 RENDER PYTHON VERSION FIX")
    print("=" * 50)
    
    print("📋 IMMEDIATE ACTIONS:")
    print("1. Commit the Python version fix:")
    print("   git add .")
    print("   git commit -m 'Force Python 3.9 for Render compatibility'")
    print("   git push origin main")
    
    print("\n2. In Render Dashboard:")
    print("   - Go to Settings → Environment")
    print("   - Add environment variable:")
    print("     PYTHON_VERSION = 3.9.18")
    print("   - Click 'Manual Deploy' → 'Clear build cache & deploy'")
    
    print("\n3. Alternative: Update Build Command:")
    print("   pip install --upgrade pip setuptools wheel && pip install -r requirements.txt")
    
    print("\n🎯 EXPECTED RESULT:")
    print("✅ Python 3.9.18 will be used instead of 3.13.4")
    print("✅ Pillow 8.4.0 will install successfully")
    print("✅ No more '__version__' KeyError")
    print("✅ Bot will start with Supabase connection")
    
    print("\n📊 WHY THIS WORKS:")
    print("• Python 3.13 has breaking changes for Pillow")
    print("• Python 3.9 is stable and well-tested")
    print("• Pillow 8.4.0 is proven to work with Python 3.9")
    print("• Your bot code is compatible with Python 3.9")

def main():
    """Main function"""
    print("🔧 RENDER PYTHON VERSION FIX")
    print("=" * 60)
    
    # Create Python version files
    python_success = create_python_version_files()
    
    # Create compatible requirements
    req_success = create_pillow_compatible_requirements()
    
    # Show fix steps
    show_render_fix_steps()
    
    print("\n" + "=" * 60)
    if python_success and req_success:
        print("🎉 PYTHON 3.9 FIX READY!")
        print("Commit changes and redeploy to fix the Python 3.13 compatibility issue.")
    else:
        print("❌ SOME ISSUES DETECTED")

if __name__ == "__main__":
    main()
