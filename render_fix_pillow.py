#!/usr/bin/env python3
"""
Fix Pillow Version for Render Deployment
This ensures Render uses the correct Pillow version
"""

def create_render_compatible_requirements():
    """Create Render-compatible requirements with stable versions"""
    print("🔧 CREATING RENDER-COMPATIBLE REQUIREMENTS")
    print("=" * 50)
    
    # Use more stable versions for Render
    render_requirements = """async-timeout==4.0.3
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
pillow==9.5.0
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
    
    try:
        with open('requirements.txt', 'w') as f:
            f.write(render_requirements)
        print("✅ Created Render-compatible requirements.txt")
        print("✅ Updated Pillow to stable version 9.5.0")
        print("✅ All packages use stable, tested versions")
        return True
    except Exception as e:
        print(f"❌ Failed to create requirements: {e}")
        return False

def create_render_deployment_trigger():
    """Create files to force Render to use new requirements"""
    print("\n📁 CREATING RENDER DEPLOYMENT TRIGGER")
    print("=" * 50)
    
    # Create .renderignore to ensure clean deployment
    renderignore = """__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
.env
.venv/
venv/
ENV/
env.bak/
venv.bak/
.git/
.gitignore
README.md
*.log
*.db
*.session
*.session-journal"""
    
    # Create render.yaml for explicit configuration
    render_yaml = """services:
  - type: web
    name: kits-bot
    env: python
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: python main_cloud_robust.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.18
      - key: CONTAINER_DEPLOYMENT
        value: true
      - key: FORCE_SUPABASE_REST
        value: true"""
    
    try:
        with open('.renderignore', 'w') as f:
            f.write(renderignore)
        print("✅ Created .renderignore")
        
        with open('render.yaml', 'w') as f:
            f.write(render_yaml)
        print("✅ Created render.yaml")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create Render config: {e}")
        return False

def show_render_deployment_steps():
    """Show steps to fix Render deployment"""
    print("\n🚀 RENDER DEPLOYMENT FIX STEPS")
    print("=" * 50)
    
    print("📋 IMMEDIATE ACTIONS:")
    print("1. Commit the fixed requirements.txt:")
    print("   git add .")
    print("   git commit -m 'Fix Pillow version for Render deployment'")
    print("   git push origin main")
    
    print("\n2. In Render dashboard:")
    print("   - Go to your service")
    print("   - Click 'Manual Deploy' → 'Clear build cache & deploy'")
    print("   - This forces Render to use the new requirements.txt")
    
    print("\n3. Alternative: Update Build Command in Render:")
    print("   pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt")
    
    print("\n🎯 EXPECTED RESULT:")
    print("✅ Build will succeed with Pillow 9.5.0")
    print("✅ No more '__version__' KeyError")
    print("✅ Bot will start with Supabase connection")
    
    print("\n⚠️ IF STILL FAILING:")
    print("- Try Python 3.9 instead of 3.13 in Render settings")
    print("- Pillow has known issues with Python 3.13")

def main():
    """Main function"""
    print("🔧 RENDER PILLOW VERSION FIX")
    print("=" * 60)
    
    # Create compatible requirements
    req_success = create_render_compatible_requirements()
    
    # Create deployment config
    config_success = create_render_deployment_trigger()
    
    # Show deployment steps
    show_render_deployment_steps()
    
    print("\n" + "=" * 60)
    if req_success and config_success:
        print("🎉 RENDER FIX READY!")
        print("Commit changes and redeploy to fix the Pillow version error.")
    else:
        print("❌ SOME ISSUES DETECTED")
        print("Check the error messages above.")

if __name__ == "__main__":
    main()
