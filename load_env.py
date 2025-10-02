import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    # Load .env file if it exists
    if os.path.exists('.env'):
        load_dotenv()
        print("Environment variables loaded from .env file")
        return True
    else:
        print("No .env file found")
        return False

if __name__ == "__main__":
    load_environment()