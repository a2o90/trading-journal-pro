"""
Data Layer - Smart wrapper that uses Database or falls back to JSON
Handles automatic migration from JSON to PostgreSQL
"""

import streamlit as st
import json
import os
from datetime import datetime

# Try to import database functions
try:
    from database import *
    DATABASE_AVAILABLE = True
except Exception as e:
    DATABASE_AVAILABLE = False
    print(f"Database not available: {e}")

# JSON file paths
TRADES_FILE = "trades.json"
ACCOUNTS_FILE = "accounts.json"
SETTINGS_FILE = "settings.json"
USERS_FILE = "users.json"
NOTES_FILE = "daily_notes.json"
MISTAKES_FILE = "mistakes.json"
AVOIDED_TRADES_FILE = "avoided_trades.json"
PRETRADE_ANALYSIS_FILE = "pretrade_analysis.json"
QUOTES_FILE = "quotes.json"
MINDSET_CHECKINS_FILE = "mindset_checkins.json"

# ===== JSON FALLBACK FUNCTIONS =====

def json_load(filename):
    """Load data from JSON file"""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def sanitize_trade_data(trade):
    """Sanitize trade data to ensure JSON serialization"""
    if not isinstance(trade, dict):
        return trade
    
    sanitized = {}
    for key, value in trade.items():
        if isinstance(value, datetime):
            sanitized[key] = value.isoformat()
        elif isinstance(value, (int, float, str, bool, type(None))):
            sanitized[key] = value
        elif isinstance(value, list):
            sanitized[key] = [sanitize_trade_data(item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, dict):
            sanitized[key] = sanitize_trade_data(value)
        else:
            # Convert any other type to string
            sanitized[key] = str(value)
    
    return sanitized

def json_save(filename, data):
    """Save data to JSON file with proper serialization"""
    def json_serializer(obj):
        """Custom JSON serializer for non-serializable objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, default=json_serializer)

# ===== SMART DATA LAYER FUNCTIONS =====

def use_database():
    """Check if we should use database"""
    return DATABASE_AVAILABLE and 'connections' in st.secrets and 'postgresql' in st.secrets.get('connections', {})

# ===== USER FUNCTIONS =====

def load_users():
    """Load users - Database or JSON"""
    if use_database():
        try:
            return db_load_users()
        except:
            pass
    
    # Fallback to JSON
    users = json_load(USERS_FILE)
    if not users:
        # Create default admin
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'ChangeMe123!')
        return [{"id": 0, "username": "admin", "password": admin_pass, "display_name": "Admin", "created_at": datetime.now().strftime('%Y-%m-%d')}]
    return users

def save_users(users):
    """Save users - Database or JSON"""
    if use_database():
        try:
            # Database saves individually, not bulk
            # This is called from legacy code, so we skip for now
            pass
        except:
            pass
    
    json_save(USERS_FILE, users)

def register_user(username, password, display_name):
    """Register new user"""
    if use_database():
        try:
            users = load_users()
            # Check if exists
            for user in users:
                if user['username'] == username:
                    return False, "Username already exists"
            
            user_id = db_save_user(username, password, display_name)
            if user_id:
                return True, {"id": user_id, "username": username, "password": password, "display_name": display_name, "created_at": datetime.now().strftime('%Y-%m-%d')}
        except Exception as e:
            st.error(f"DB Error: {e}")
    
    # Fallback to JSON
    users = load_users()
    for user in users:
        if user['username'] == username:
            return False, "Username already exists"
    
    new_id = max([u['id'] for u in users], default=-1) + 1
    new_user = {
        'id': new_id,
        'username': username,
        'password': password,
        'display_name': display_name,
        'created_at': datetime.now().strftime('%Y-%m-%d')
    }
    users.append(new_user)
    save_users(users)
    return True, new_user

# ===== TRADE FUNCTIONS =====

def load_trades(user_id=None):
    """Load trades - Database or JSON"""
    if use_database():
        try:
            return db_load_trades(user_id)
        except Exception as e:
            st.error(f"DB Error loading trades: {e}")
    
    # Fallback to JSON
    trades = json_load(TRADES_FILE)
    if user_id is not None:
        return [t for t in trades if t.get('user_id') == user_id]
    return trades

def save_trades(trades):
    """Save trades - Database or JSON"""
    if use_database():
        try:
            db_save_trades(trades)
        except Exception as e:
            st.error(f"DB Error saving trades: {e}")
    
    # Sanitize trades data before saving to JSON
    sanitized_trades = [sanitize_trade_data(trade) for trade in trades]
    json_save(TRADES_FILE, sanitized_trades)

# ===== ACCOUNT FUNCTIONS =====

def load_accounts(user_id=None):
    """Load accounts - Database or JSON"""
    if use_database():
        try:
            return db_load_accounts(user_id)
        except Exception as e:
            st.error(f"DB Error loading accounts: {e}")
    
    # Fallback to JSON
    accounts = json_load(ACCOUNTS_FILE)
    # Add user_id if not present
    for acc in accounts:
        if 'user_id' not in acc:
            acc['user_id'] = 0
    
    if user_id is not None:
        accounts = [a for a in accounts if a.get('user_id') == user_id]
    
    if not accounts and user_id is not None:
        # Create default account
        return [{"id": 0, "name": "Main Account", "size": 10000, "user_id": user_id}]
    
    return accounts if accounts else [{"id": 0, "name": "Main Account", "size": 10000, "user_id": 0}]

def save_accounts(accounts):
    """Save accounts - Database or JSON"""
    if use_database():
        try:
            db_save_accounts(accounts)
        except Exception as e:
            st.error(f"DB Error saving accounts: {e}")
    
    # Sanitize accounts data before saving to JSON
    sanitized_accounts = [sanitize_trade_data(account) for account in accounts]
    json_save(ACCOUNTS_FILE, sanitized_accounts)

# ===== SETTINGS FUNCTIONS =====

def load_settings(user_id=None):
    """Load settings - Database or JSON"""
    if use_database():
        try:
            return db_load_settings(user_id)
        except:
            pass
    
    # Fallback to JSON
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                if 'currency' not in settings:
                    settings['currency'] = "$"
                if 'dark_mode' not in settings:
                    settings['dark_mode'] = False
                return settings
        except:
            return {"currency": "$", "dark_mode": False}
    return {"currency": "$", "dark_mode": False}

def save_settings(settings, user_id=None):
    """Save settings - Database or JSON"""
    if use_database():
        try:
            db_save_settings(settings, user_id)
        except:
            pass
    
    # Sanitize settings data before saving to JSON
    sanitized_settings = sanitize_trade_data(settings)
    json_save(SETTINGS_FILE, sanitized_settings)

# ===== QUOTES FUNCTIONS =====

def load_quotes():
    """Load quotes - Database or JSON"""
    if use_database():
        try:
            return db_load_quotes()
        except:
            pass
    
    # Fallback to JSON
    return json_load(QUOTES_FILE)

def save_quotes(quotes):
    """Save quotes - Database or JSON"""
    if use_database():
        try:
            # Database saves individually
            pass
        except:
            pass
    
    json_save(QUOTES_FILE, quotes)

def add_quote(text, author=""):
    """Add a quote"""
    if use_database():
        try:
            db_save_quote(text, author)
            return {"success": True}
        except:
            pass
    
    # Fallback to JSON
    quotes = load_quotes()
    new_id = max([q['id'] for q in quotes], default=-1) + 1
    quote = {
        'id': new_id,
        'text': text,
        'author': author,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'active': True
    }
    quotes.append(quote)
    save_quotes(quotes)
    return quote

# ===== MIGRATION STATUS =====

def get_data_source():
    """Get current data source"""
    if use_database():
        return "PostgreSQL Database ✅"
    return "JSON Files (Fallback) ⚠️"

def migration_needed():
    """Check if JSON data exists that needs migration"""
    if not use_database():
        return False
    
    # Check if JSON files have data
    for file in [TRADES_FILE, USERS_FILE, ACCOUNTS_FILE]:
        if os.path.exists(file):
            data = json_load(file)
            if len(data) > 0:
                return True
    return False

