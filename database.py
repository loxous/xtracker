import json
import os
from datetime import datetime
from config import DATA_DIR, USERS_DB_FILE

class Database:
    def __init__(self):
        self.ensure_data_dir()
        self.ensure_db_file()
    
    def ensure_data_dir(self):
        """Create data directory if not exists"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
    
    def ensure_db_file(self):
        """Create database file if not exists"""
        if not os.path.exists(USERS_DB_FILE):
            with open(USERS_DB_FILE, 'w') as f:
                json.dump({}, f)
    
    def load_data(self):
        """Load all data from JSON file"""
        try:
            with open(USERS_DB_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}
    
    def save_data(self, data):
        """Save data to JSON file"""
        try:
            with open(USERS_DB_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def get_user(self, username):
        """Get user data by username"""
        data = self.load_data()
        return data.get(username.lower())
    
    def save_user(self, username, user_info, following_count):
        """Save or update user data"""
        data = self.load_data()
        username_lower = username.lower()
        
        now = datetime.now().isoformat()
        
        if username_lower not in data:
            # First time tracking
            data[username_lower] = {
                'username': username,
                'user_info': user_info,
                'following_count': following_count,
                'last_following_count': following_count,
                'first_tracked': now,
                'last_checked': now,
                'check_count': 1
            }
        else:
            # Update existing user
            data[username_lower]['user_info'] = user_info
            data[username_lower]['last_following_count'] = data[username_lower]['following_count']
            data[username_lower]['following_count'] = following_count
            data[username_lower]['last_checked'] = now
            data[username_lower]['check_count'] = data[username_lower].get('check_count', 0) + 1
        
        self.save_data(data)
        return data[username_lower]
    
    def remove_user(self, username):
        """Remove user from tracking"""
        data = self.load_data()
        username_lower = username.lower()
        
        if username_lower in data:
            del data[username_lower]
            self.save_data(data)
            return True
        return False
    
    def get_all_users(self):
        """Get all tracked users"""
        data = self.load_data()
        return list(data.values())
    
    def get_following_difference(self, username):
        """Get difference in following count"""
        user = self.get_user(username)
        if not user:
            return 0
        
        current = user.get('following_count', 0)
        last = user.get('last_following_count', 0)
        
        return current - last