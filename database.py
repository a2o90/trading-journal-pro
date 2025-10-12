"""
Database connection and helper functions for Trading Journal
Uses PostgreSQL via Neon.tech
"""

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor, Json
import json
from datetime import datetime

# ===== CONNECTION =====

def get_connection():
    """Get fresh database connection"""
    try:
        conn = psycopg2.connect(st.secrets["connections"]["postgresql"]["url"])
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

def execute_query(query, params=None, fetch=False, fetchone=False):
    """Execute a database query with proper connection handling"""
    conn = None
    cur = None
    
    try:
        # Get fresh connection for each query
        conn = get_connection()
        if not conn:
            return None
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params)
        
        if fetch:
            result = cur.fetchall()
        elif fetchone:
            result = cur.fetchone()
        else:
            result = None
        
        conn.commit()
        return result
        
    except Exception as e:
        if conn:
            conn.rollback()
        st.error(f"❌ Database error: {e}")
        return None
    
    finally:
        # Always close cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

# ===== INITIALIZATION =====

def init_database():
    """Initialize database tables"""
    
    # Users table
    execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            display_name VARCHAR(255) NOT NULL,
            created_at DATE NOT NULL
        )
    """)
    
    # Accounts table
    execute_query("""
        CREATE TABLE IF NOT EXISTS accounts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            size DECIMAL(15, 2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Trades table
    execute_query("""
        CREATE TABLE IF NOT EXISTS trades (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
            account_name VARCHAR(255),
            date DATE NOT NULL,
            time TIME,
            symbol VARCHAR(50) NOT NULL,
            side VARCHAR(10) NOT NULL,
            entry_price DECIMAL(15, 2) NOT NULL,
            exit_price DECIMAL(15, 2) NOT NULL,
            quantity DECIMAL(15, 4) NOT NULL,
            duration_minutes INTEGER,
            pnl DECIMAL(15, 2) NOT NULL,
            r_multiple DECIMAL(10, 2),
            setup VARCHAR(255),
            influence VARCHAR(255),
            trade_type VARCHAR(50),
            market_condition VARCHAR(50),
            mood VARCHAR(50),
            focus_level INTEGER,
            stress_level INTEGER,
            sleep_quality INTEGER,
            pre_trade_confidence INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Mistakes table
    execute_query("""
        CREATE TABLE IF NOT EXISTS mistakes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            time TIME,
            mistake_type VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            trade_id INTEGER REFERENCES trades(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Avoided trades table
    execute_query("""
        CREATE TABLE IF NOT EXISTS avoided_trades (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            time TIME,
            symbol VARCHAR(50) NOT NULL,
            reason VARCHAR(255) NOT NULL,
            potential_loss DECIMAL(15, 2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Pre-trade analysis table
    execute_query("""
        CREATE TABLE IF NOT EXISTS pretrade_analysis (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            time TIME,
            symbol VARCHAR(50) NOT NULL,
            direction VARCHAR(10) NOT NULL,
            entry_plan VARCHAR(500),
            stop_loss VARCHAR(100),
            take_profit VARCHAR(100),
            risk_reward VARCHAR(50),
            confidence INTEGER,
            checklist TEXT,
            executed BOOLEAN DEFAULT FALSE,
            trade_id INTEGER REFERENCES trades(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Mindset check-ins table
    execute_query("""
        CREATE TABLE IF NOT EXISTS mindset_checkins (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            time TIME,
            focus_level INTEGER NOT NULL,
            locked_in VARCHAR(100) NOT NULL,
            emotional_state VARCHAR(100) NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Daily notes table
    execute_query("""
        CREATE TABLE IF NOT EXISTS daily_notes (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, date)
        )
    """)
    
    # Quotes table (admin only)
    execute_query("""
        CREATE TABLE IF NOT EXISTS quotes (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            author VARCHAR(255),
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Settings table (per user or global)
    execute_query("""
        CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            currency VARCHAR(5) DEFAULT '$',
            dark_mode BOOLEAN DEFAULT TRUE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id)
        )
    """)
    
    # Create default admin user if not exists
    import os
    admin_password = os.environ.get('ADMIN_PASSWORD', 'ChangeMe123!')
    
    # Check if admin exists
    admin_exists = execute_query("""
        SELECT id FROM users WHERE username = 'admin'
    """, fetchone=True)
    
    if not admin_exists:
        # Create admin user
        admin_result = execute_query("""
            INSERT INTO users (username, password, display_name, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, ('admin', admin_password, 'Admin', datetime.now().strftime('%Y-%m-%d')), fetchone=True)
        
        if admin_result:
            admin_id = admin_result['id']
            # Create default Main Account for admin
            execute_query("""
                INSERT INTO accounts (user_id, name, size)
                VALUES (%s, %s, %s)
            """, (admin_id, 'Main Account', 10000))
            
            # Add some default quotes
            default_quotes = [
                ("The market is a device for transferring money from the impatient to the patient.", "Warren Buffett"),
                ("Risk comes from not knowing what you're doing.", "Warren Buffett"),
                ("In trading, discipline and patience are more important than intelligence.", "Trading Wisdom"),
                ("The goal is not to be right, but to make money.", "Trading Psychology"),
                ("Your biggest enemy in trading is yourself.", "Trading Wisdom")
            ]
            
            for quote_text, quote_author in default_quotes:
                execute_query("""
                    INSERT INTO quotes (text, author, active)
                    VALUES (%s, %s, %s)
                """, (quote_text, quote_author, True))

# ===== USER FUNCTIONS =====

def db_load_users():
    """Load all users from database"""
    result = execute_query("SELECT * FROM users ORDER BY id", fetch=True)
    return [dict(row) for row in result] if result else []

def db_save_user(username, password, display_name):
    """Save a new user to database"""
    result = execute_query("""
        INSERT INTO users (username, password, display_name, created_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (username, password, display_name, datetime.now().strftime('%Y-%m-%d')), fetchone=True)
    return result['id'] if result else None

def db_update_password(user_id, new_password):
    """Update user password"""
    execute_query("""
        UPDATE users SET password = %s WHERE id = %s
    """, (new_password, user_id))

# ===== ACCOUNT FUNCTIONS =====

def db_load_accounts(user_id=None):
    """Load accounts from database"""
    if user_id is not None:
        result = execute_query("""
            SELECT * FROM accounts WHERE user_id = %s ORDER BY id
        """, (user_id,), fetch=True)
    else:
        result = execute_query("SELECT * FROM accounts ORDER BY id", fetch=True)
    
    return [dict(row) for row in result] if result else []

def db_save_accounts(accounts):
    """Save/update accounts (bulk operation)"""
    for acc in accounts:
        if 'id' in acc and acc['id'] is not None:
            # Update existing
            execute_query("""
                UPDATE accounts SET name = %s, size = %s
                WHERE id = %s
            """, (acc['name'], acc['size'], acc['id']))
        else:
            # Insert new
            execute_query("""
                INSERT INTO accounts (user_id, name, size)
                VALUES (%s, %s, %s)
            """, (acc['user_id'], acc['name'], acc['size']))

def db_delete_account(account_id):
    """Delete an account"""
    execute_query("DELETE FROM accounts WHERE id = %s", (account_id,))

# ===== TRADE FUNCTIONS =====

def db_load_trades(user_id=None):
    """Load trades from database"""
    if user_id is not None:
        result = execute_query("""
            SELECT * FROM trades WHERE user_id = %s ORDER BY date DESC, time DESC
        """, (user_id,), fetch=True)
    else:
        result = execute_query("SELECT * FROM trades ORDER BY date DESC, time DESC", fetch=True)
    
    if not result:
        return []
    
    # Convert to dict and format dates/times
    trades = []
    for row in result:
        trade = dict(row)
        if trade.get('date'):
            trade['date'] = trade['date'].strftime('%Y-%m-%d')
        if trade.get('time'):
            trade['time'] = trade['time'].strftime('%H:%M:%S')
        trades.append(trade)
    
    return trades

def db_save_trades(trades):
    """Save/update trades (bulk operation)"""
    for trade in trades:
        if 'id' in trade and trade['id'] is not None:
            # Update existing (simplified - add all fields as needed)
            execute_query("""
                UPDATE trades SET
                    symbol = %s, pnl = %s, notes = %s
                WHERE id = %s
            """, (trade.get('symbol'), trade.get('pnl'), trade.get('notes'), trade['id']))
        else:
            # Insert new
            execute_query("""
                INSERT INTO trades (
                    user_id, account_id, account_name, date, time, symbol, side,
                    entry_price, exit_price, quantity, duration_minutes, pnl, r_multiple,
                    setup, influence, trade_type, market_condition, mood,
                    focus_level, stress_level, sleep_quality, pre_trade_confidence, notes
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                trade.get('user_id'), trade.get('account_id'), trade.get('account_name'),
                trade.get('date'), trade.get('time'), trade.get('symbol'), trade.get('side'),
                trade.get('entry_price'), trade.get('exit_price'), trade.get('quantity'),
                trade.get('duration_minutes'), trade.get('pnl'), trade.get('r_multiple'),
                trade.get('setup'), trade.get('influence'), trade.get('trade_type'),
                trade.get('market_condition'), trade.get('mood'), trade.get('focus_level'),
                trade.get('stress_level'), trade.get('sleep_quality'),
                trade.get('pre_trade_confidence'), trade.get('notes')
            ))

def db_delete_trade(trade_id):
    """Delete a trade"""
    execute_query("DELETE FROM trades WHERE id = %s", (trade_id,))

# ===== QUOTES FUNCTIONS =====

def db_load_quotes():
    """Load quotes from database"""
    result = execute_query("SELECT * FROM quotes ORDER BY id", fetch=True)
    return [dict(row) for row in result] if result else []

def db_save_quote(text, author="", active=True):
    """Save a new quote"""
    execute_query("""
        INSERT INTO quotes (text, author, active)
        VALUES (%s, %s, %s)
    """, (text, author, active))

def db_update_quote(quote_id, active):
    """Update quote active status"""
    execute_query("""
        UPDATE quotes SET active = %s WHERE id = %s
    """, (active, quote_id))

def db_delete_quote(quote_id):
    """Delete a quote"""
    execute_query("DELETE FROM quotes WHERE id = %s", (quote_id,))

# ===== SETTINGS FUNCTIONS =====

def db_load_settings(user_id=None):
    """Load settings"""
    if user_id:
        result = execute_query("""
            SELECT * FROM settings WHERE user_id = %s
        """, (user_id,), fetchone=True)
    else:
        result = execute_query("""
            SELECT * FROM settings WHERE user_id IS NULL
        """, fetchone=True)
    
    if result:
        return dict(result)
    else:
        # Return defaults
        return {"currency": "$", "dark_mode": True}

def db_save_settings(settings, user_id=None):
    """Save settings"""
    execute_query("""
        INSERT INTO settings (user_id, currency, dark_mode)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            currency = EXCLUDED.currency,
            dark_mode = EXCLUDED.dark_mode,
            updated_at = CURRENT_TIMESTAMP
    """, (user_id, settings.get('currency', '$'), settings.get('dark_mode', True)))

# Initialize database on module import
try:
    init_database()
except Exception as e:
    pass  # Will be handled by streamlit app

