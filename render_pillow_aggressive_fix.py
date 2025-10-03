#!/usr/bin/env python3
"""
Aggressive Pillow Fix for Render
Remove or replace problematic Pillow dependency
"""

def create_minimal_requirements():
    """Create requirements without problematic packages"""
    print("🔧 CREATING MINIMAL REQUIREMENTS (NO PILLOW)")
    print("=" * 50)
    
    # Remove packages that depend on Pillow or cause build issues
    minimal_requirements = """async-timeout==4.0.3
asyncpg==0.28.0
attrs==23.1.0
beautifulsoup4==4.12.2
certifi==2023.7.22
charset-normalizer==3.2.0
idna==3.4
packaging==23.1
psutil==5.9.5
pyaes==1.6.1
PyQRCode==1.2.1
Pyrogram==2.0.106
PySocks==1.7.1
python-dotenv==1.0.0
pytz==2023.3
requests==2.31.0
sniffio==1.3.0
sortedcontainers==2.4.0
soupsieve==2.5
TgCrypto==1.2.5
typing_extensions==4.7.1
urllib3==2.0.4"""
    
    try:
        with open('requirements_minimal.txt', 'w') as f:
            f.write(minimal_requirements)
        print("✅ Created requirements_minimal.txt (no Pillow/PDF dependencies)")
        return True
    except Exception as e:
        print(f"❌ Failed to create minimal requirements: {e}")
        return False

def create_pillow_wheel_requirements():
    """Create requirements using pre-compiled Pillow wheel"""
    print("\n🔧 CREATING WHEEL-BASED REQUIREMENTS")
    print("=" * 50)
    
    # Use specific wheel versions that don't need compilation
    wheel_requirements = """async-timeout==4.0.3
asyncpg==0.28.0
attrs==23.1.0
beautifulsoup4==4.12.2
certifi==2023.7.22
charset-normalizer==3.2.0
idna==3.4
packaging==23.1
pillow>=8.0.0,<9.0.0 --only-binary=pillow
psutil==5.9.5
pyaes==1.6.1
PyQRCode==1.2.1
Pyrogram==2.0.106
PySocks==1.7.1
python-dotenv==1.0.0
pytz==2023.3
requests==2.31.0
sniffio==1.3.0
sortedcontainers==2.4.0
soupsieve==2.5
TgCrypto==1.2.5
typing_extensions==4.7.1
urllib3==2.0.4"""
    
    try:
        with open('requirements_wheel.txt', 'w') as f:
            f.write(wheel_requirements)
        print("✅ Created requirements_wheel.txt (pre-compiled Pillow)")
        return True
    except Exception as e:
        print(f"❌ Failed to create wheel requirements: {e}")
        return False

def check_bot_pillow_usage():
    """Check if the bot actually uses Pillow"""
    print("\n🔍 CHECKING PILLOW USAGE IN BOT")
    print("=" * 50)
    
    pillow_imports = [
        "from PIL import",
        "import PIL",
        "from pillow import",
        "import pillow"
    ]
    
    files_to_check = [
        "main.py",
        "main_cloud_robust.py",
        "METHODS/operations.py",
        "METHODS/pdf_compressor.py"
    ]
    
    pillow_used = False
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for import_stmt in pillow_imports:
                    if import_stmt in content:
                        print(f"⚠️ Found Pillow usage in {file_path}: {import_stmt}")
                        pillow_used = True
        except FileNotFoundError:
            print(f"📄 File not found: {file_path}")
        except Exception as e:
            print(f"❌ Error checking {file_path}: {e}")
    
    if not pillow_used:
        print("✅ No direct Pillow imports found in main bot files")
        print("✅ Pillow might only be used by pdf2image (optional)")
    
    return pillow_used

def create_render_build_script():
    """Create custom build script for Render"""
    print("\n📜 CREATING CUSTOM BUILD SCRIPT")
    print("=" * 50)
    
    build_script = """#!/bin/bash
# Custom Render build script to handle Pillow issues

echo "🔧 Starting custom build process..."

# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel

# Try to install requirements with different strategies
echo "📦 Attempting minimal installation..."

# Install core packages first
pip install async-timeout==4.0.3
pip install asyncpg==0.28.0
pip install attrs==23.1.0
pip install beautifulsoup4==4.12.2
pip install certifi==2023.7.22
pip install charset-normalizer==3.2.0
pip install idna==3.4
pip install packaging==23.1
pip install psutil==5.9.5
pip install pyaes==1.6.1
pip install PyQRCode==1.2.1
pip install Pyrogram==2.0.106
pip install PySocks==1.7.1
pip install python-dotenv==1.0.0
pip install pytz==2023.3
pip install requests==2.31.0
pip install sniffio==1.3.0
pip install sortedcontainers==2.4.0
pip install soupsieve==2.5
pip install TgCrypto==1.2.5
pip install typing_extensions==4.7.1
pip install urllib3==2.0.4

# Try to install Pillow with different methods
echo "🖼️ Attempting Pillow installation..."
pip install --only-binary=pillow pillow || echo "⚠️ Pillow installation failed, continuing without it"

echo "✅ Build process completed"
"""
    
    try:
        with open('build.sh', 'w') as f:
            f.write(build_script)
        print("✅ Created build.sh (custom build script)")
        
        # Make it executable
        import os
        os.chmod('build.sh', 0o755)
        print("✅ Made build.sh executable")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create build script: {e}")
        return False

def show_render_solutions():
    """Show multiple solutions for Render deployment"""
    print("\n🚀 RENDER DEPLOYMENT SOLUTIONS")
    print("=" * 50)
    
    print("🎯 SOLUTION 1: Use Minimal Requirements (RECOMMENDED)")
    print("1. Copy requirements_minimal.txt to requirements.txt:")
    print("   cp requirements_minimal.txt requirements.txt")
    print("2. Commit and push:")
    print("   git add . && git commit -m 'Use minimal requirements without Pillow' && git push")
    print("3. Redeploy in Render")
    
    print("\n🎯 SOLUTION 2: Use Custom Build Script")
    print("1. Update Render build command to: ./build.sh")
    print("2. Commit and push the build.sh file")
    print("3. Redeploy in Render")
    
    print("\n🎯 SOLUTION 3: Use Different Build Command")
    print("Update Render build command to:")
    print("pip install --upgrade pip && pip install --only-binary=:all: -r requirements.txt || pip install --no-deps -r requirements.txt")
    
    print("\n🎯 SOLUTION 4: Switch to Railway (ALTERNATIVE)")
    print("Railway might handle Pillow dependencies better")
    print("Just update Railway environment variables with FORCE_SUPABASE_REST=true")
    
    print("\n✅ EXPECTED RESULTS:")
    print("• Build will succeed without Pillow compilation issues")
    print("• Bot will start successfully")
    print("• Supabase connection will work")
    print("• PDF features might be limited (if Pillow was needed)")

def main():
    """Main function"""
    print("🔧 AGGRESSIVE PILLOW FIX FOR RENDER")
    print("=" * 60)
    
    # Check if bot actually uses Pillow
    pillow_used = check_bot_pillow_usage()
    
    # Create minimal requirements
    minimal_success = create_minimal_requirements()
    
    # Create wheel requirements
    wheel_success = create_pillow_wheel_requirements()
    
    # Create build script
    script_success = create_render_build_script()
    
    # Show solutions
    show_render_solutions()
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDATION:")
    if not pillow_used:
        print("Since Pillow isn't directly used, try SOLUTION 1 (minimal requirements)")
    else:
        print("Since Pillow is used, try SOLUTION 2 (custom build script)")
    
    print("\n📊 FILES CREATED:")
    if minimal_success:
        print("✅ requirements_minimal.txt")
    if wheel_success:
        print("✅ requirements_wheel.txt")
    if script_success:
        print("✅ build.sh")

if __name__ == "__main__":
    main()

