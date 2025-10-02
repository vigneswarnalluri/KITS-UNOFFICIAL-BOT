import requests
import json
import os
from typing import Optional, Dict, Any, List

class SupabaseREST:
    """
    Supabase REST API handler for the KITS Bot
    Uses Supabase REST API instead of direct PostgreSQL connection
    """
    
    def __init__(self):
        # Load environment variables
        from load_env import load_environment
        load_environment()
        
        self.url = os.environ.get("SUPABASE_URL")
        self.api_key = os.environ.get("SUPABASE_ANON_KEY")
        self.headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method, endpoint, data=None):
        """Make a request to Supabase REST API"""
        try:
            url = f"{self.url}/rest/v1/{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, timeout=10)
            
            if response.status_code in [200, 201, 204]:
                return response.json() if response.content else True
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    # User Sessions Management
    def store_user_session(self, chat_id: int, session_data: str, username: str):
        """Store user session data"""
        data = {
            "chat_id": chat_id,
            "session_data": session_data,
            "username": username
        }
        return self._make_request("POST", "user_sessions", data)
    
    def load_user_session(self, chat_id: int) -> Optional[str]:
        """Load user session data"""
        response = self._make_request("GET", f"user_sessions?chat_id=eq.{chat_id}")
        if response and len(response) > 0:
            return response[0].get("session_data")
        return None
    
    def delete_user_session(self, chat_id: int):
        """Delete user session"""
        return self._make_request("DELETE", f"user_sessions?chat_id=eq.{chat_id}")
    
    # User Credentials Management
    def store_credentials(self, chat_id: int, username: str, password: str, pat_student: bool = False):
        """Store user credentials (upsert - insert or update)"""
        data = {
            "chat_id": chat_id,
            "username": username,
            "password": password,
            "pat_student": pat_student
        }
        
        # First try to update existing record
        update_result = self._make_request("PATCH", f"user_credentials?chat_id=eq.{chat_id}", data)
        if update_result is not None and update_result is not True:
            return update_result
        
        # If update fails or returns True (no existing record), try to insert new record
        return self._make_request("POST", "user_credentials", data)
    
    def retrieve_credentials(self, chat_id: int) -> Optional[tuple]:
        """Retrieve user credentials"""
        response = self._make_request("GET", f"user_credentials?chat_id=eq.{chat_id}")
        if response and len(response) > 0:
            cred = response[0]
            return (cred.get("username"), cred.get("password"))
        return None
    
    def remove_credentials(self, chat_id: int):
        """Remove user credentials"""
        return self._make_request("DELETE", f"user_credentials?chat_id=eq.{chat_id}")
    
    # User Settings Management
    def store_user_settings(self, chat_id: int, attendance_threshold: int, bio_threshold: int, ui: bool, title: bool):
        """Store user settings"""
        data = {
            "chat_id": chat_id,
            "attendance_threshold": attendance_threshold,
            "bio_threshold": bio_threshold,
            "ui": ui,
            "title": title
        }
        return self._make_request("POST", "user_settings", data)
    
    def fetch_user_settings(self, chat_id: int) -> Optional[tuple]:
        """Fetch user settings"""
        response = self._make_request("GET", f"user_settings?chat_id=eq.{chat_id}")
        if response and len(response) > 0:
            settings = response[0]
            return (
                settings.get("attendance_threshold"),
                settings.get("bio_threshold"),
                settings.get("ui"),
                settings.get("title")
            )
        return None
    
    # Reports Management
    def store_report(self, report_id: str, username: str, report: str, chat_id: int, status: str = "pending"):
        """Store user report"""
        data = {
            "report_id": report_id,
            "username": username,
            "report": report,
            "chat_id": chat_id,
            "status": status
        }
        return self._make_request("POST", "reports", data)
    
    def fetch_reports(self) -> List[Dict[str, Any]]:
        """Fetch all reports"""
        response = self._make_request("GET", "reports")
        return response if response else []
    
    # Test connection
    def test_connection(self):
        """Test Supabase REST API connection"""
        try:
            if not self.url or not self.api_key:
                print(f"ERROR: Missing configuration - URL: {self.url}, Key: {bool(self.api_key)}")
                return False
                
            # Try to get a simple response
            response = requests.get(f"{self.url}/rest/v1/", headers=self.headers, timeout=10)
            if response.status_code == 200:
                print("SUCCESS: Supabase REST API connection working!")
                return True
            else:
                print(f"ERROR: API returned status {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"ERROR: Connection test failed: {e}")
            return False

# Global instance
supabase_rest = SupabaseREST()
