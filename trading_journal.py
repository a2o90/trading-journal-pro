import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import calendar as cal
import numpy as np
from collections import defaultdict

# Import price action calendar module
try:
    from price_action_calendar import display_weekly_price_action_calendar
    PRICE_ACTION_AVAILABLE = True
except ImportError:
    PRICE_ACTION_AVAILABLE = False

def safe_plot(data, title, xlabel, ylabel, ax=None):
    """Safely plot data with error handling"""
    try:
        if data is None or len(data) == 0:
            return False
        
        # Ensure data is numeric
        if hasattr(data, 'values'):
            data = pd.to_numeric(data.values, errors='coerce')
        else:
            data = pd.to_numeric(data, errors='coerce')
        
        # Remove NaN values
        data = data.dropna()
        
        if len(data) == 0:
            return False
        
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 5))
        
        colors = ['#00ff88' if x > 0 else '#ff4444' for x in data]
        data.plot(kind='bar', ax=ax, color=colors, edgecolor='white', linewidth=1.5)
        ax.axhline(y=0, color='white', linewidth=1)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y', linestyle='--')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return True
    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")
        return False

# Import analytics module
try:
    from analytics import get_complete_analysis, generate_ai_insights
    ANALYTICS_AVAILABLE = True
except Exception as e:
    ANALYTICS_AVAILABLE = False

# Import AI Assistant module
try:
    from ai_assistant import get_daily_summary, analyze_patterns, get_strategy_suggestions, get_weekly_report
    AI_ASSISTANT_AVAILABLE = True
except Exception as e:
    AI_ASSISTANT_AVAILABLE = False

# Import Mobile PWA module
try:
    from mobile_pwa import get_pwa_manifest, get_service_worker, get_pwa_html, get_mobile_css, get_quick_log_form, get_push_notification_schedule
    MOBILE_PWA_AVAILABLE = True
except Exception as e:
    MOBILE_PWA_AVAILABLE = False

# Import Broker Integration module
try:
    from broker_integration import setup_tradingview_webhook, get_webhook_instructions, process_webhook_trade, get_integration_status, test_webhook_connection
    BROKER_INTEGRATION_AVAILABLE = True
except Exception as e:
    BROKER_INTEGRATION_AVAILABLE = False

# Import alerts module
try:
    from alerts import check_all_alerts, get_alert_summary, DEFAULT_THRESHOLDS
    ALERTS_AVAILABLE = True
except Exception as e:
    ALERTS_AVAILABLE = False

# Import risk calculator module
try:
    from risk_calculator import (
        calculate_position_size, calculate_risk_reward, calculate_kelly_criterion,
        get_risk_management_report, calculate_profit_targets
    )
    RISK_CALC_AVAILABLE = True
except Exception as e:
    RISK_CALC_AVAILABLE = False

# Import PDF export module
try:
    from pdf_export import generate_weekly_report, generate_monthly_report, generate_custom_report
    PDF_EXPORT_AVAILABLE = True
except Exception as e:
    PDF_EXPORT_AVAILABLE = False

# Import CSV handler module
try:
    from csv_handler import (
        parse_csv_import, export_trades_to_csv, generate_csv_template,
        get_import_stats, BROKER_FORMATS
    )
    CSV_HANDLER_AVAILABLE = True
except Exception as e:
    CSV_HANDLER_AVAILABLE = False

# Import gamification module
try:
    from gamification import (
        check_achievements, calculate_level, get_weekly_challenges,
        get_current_streaks, get_trading_stats_summary, ACHIEVEMENTS, LEVELS
    )
    GAMIFICATION_AVAILABLE = True
except Exception as e:
    GAMIFICATION_AVAILABLE = False

# Import mentor system module
try:
    from mentor_system import (
        add_trade_comment, get_comments_for_trade, get_all_comments_by_user,
        create_feedback_session, update_feedback_session, get_feedback_for_user,
        generate_suggestions_from_trades, get_mentor_statistics, get_latest_feedback
    )
    MENTOR_SYSTEM_AVAILABLE = True
except Exception as e:
    MENTOR_SYSTEM_AVAILABLE = False

# Import data layer (handles Database or JSON fallback)
try:
    from data_layer import (
        load_users as dl_load_users,
        save_users as dl_save_users,
        register_user as dl_register_user,
        load_trades as dl_load_trades,
        save_trades as dl_save_trades,
        load_accounts as dl_load_accounts,
        save_accounts as dl_save_accounts,
        load_settings as dl_load_settings,
        save_settings as dl_save_settings,
        load_quotes as dl_load_quotes,
        save_quotes as dl_save_quotes,
        add_quote as dl_add_quote,
        use_database,
        get_data_source
    )
    DATA_LAYER_AVAILABLE = True
except Exception as e:
    DATA_LAYER_AVAILABLE = False
    st.error(f"Data layer import failed: {e}")

# Configuration
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
ACCOUNT_SIZE = 10000  # Default account size for R-multiple calculation

# App Version
APP_VERSION = "3.0.0"
LAST_UPDATE = "2025-10-12"

# ===== USER MANAGEMENT FUNCTIONS (must be defined before login_page) =====

def load_users():
    """Load users - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        return dl_load_users()
    # Fallback
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    admin_pass = os.environ.get('ADMIN_PASSWORD', 'ChangeMe123!')
    return [{"id": 0, "username": "admin", "password": admin_pass, "display_name": "Admin", "created_at": datetime.now().strftime('%Y-%m-%d')}]

def save_users(users):
    """Save users - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        dl_save_users(users)
    else:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)

def authenticate_user(username, password):
    """Authenticate user and return user object if valid"""
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user
    return None

def register_user(username, password, display_name):
    """Register a new user - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        return dl_register_user(username, password, display_name)
    
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

def change_password(user_id, new_password):
    """Change password for a user"""
    users = load_users()
    
    for user in users:
        if user['id'] == user_id:
            user['password'] = new_password
            save_users(users)
            return True, "Password updated successfully"
    
    return False, "User not found"

# ===== LOGIN PAGE =====

def login_page():
    """Display login page and handle authentication"""
    
    st.title("📈 Trading Journal Pro")
    
    # ===== IMPORTANT DATABASE MIGRATION NOTICE =====
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(0, 255, 136, 0.15) 0%, rgba(0, 136, 255, 0.15) 100%);
                padding: 20px; border-radius: 12px; border-left: 5px solid #00ff88;
                margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0, 255, 136, 0.2);'>
        <h3 style='color: #00ff88; margin-top: 0;'>🚀 BELANGRIJKE UPDATE!</h3>
        <p style='font-size: 16px; margin: 10px 0; line-height: 1.6;'>
            <strong>Vanaf vandaag (12 oktober 2024)</strong> draait Trading Journal Pro op een 
            <strong style='color: #00ff88;'>PostgreSQL database</strong>!
        </p>
        <p style='font-size: 15px; margin: 15px 0 10px 0;'><strong>Dit betekent:</strong></p>
        <ul style='margin: 5px 0 15px 20px; font-size: 14px; line-height: 1.8;'>
            <li>✅ <strong>Geen data loss meer</strong> bij updates of redeploys</li>
            <li>✅ <strong>Veilige opslag</strong> van al je trades en gegevens</li>
            <li>✅ <strong>Betere performance</strong> en schaalbaarheid</li>
            <li>✅ <strong>Professionele data bescherming</strong></li>
        </ul>
        <div style='background-color: rgba(255, 136, 0, 0.2); padding: 12px; border-radius: 8px; 
                    border-left: 3px solid #ff8800; margin-top: 15px;'>
            <p style='margin: 0; font-size: 14px;'>
                ⚠️ <strong>Actie vereist:</strong> Bestaande gebruikers moeten <strong>opnieuw registreren</strong>. 
                Je oude data is gearchiveerd, maar de nieuwe database start met een schone lei voor maximale stabiliteit.
            </p>
        </div>
        <p style='margin: 15px 0 0 0; font-size: 13px; opacity: 0.8; text-align: center;'>
            💾 <em>Alle nieuwe data wordt vanaf nu permanent opgeslagen in de database</em>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display version info on login page
    from datetime import datetime
    import pytz
    
    # Get current time in NL timezone
    nl_tz = pytz.timezone('Europe/Amsterdam')
    current_time_nl = datetime.now(nl_tz).strftime('%H:%M:%S')
    current_date_nl = datetime.now(nl_tz).strftime('%d-%m-%Y')
    
    st.markdown(f"""
    <div style='background-color: rgba(38, 39, 48, 0.5); padding: 15px; border-radius: 10px; 
                border: 1px solid rgba(250, 250, 250, 0.1); text-align: center; margin-bottom: 20px;'>
        <p style='margin: 0; font-size: 14px;'>
            <strong>Version {APP_VERSION}</strong> | Last Updated: {LAST_UPDATE}
        </p>
        <p style='margin: 5px 0 0 0; font-size: 12px; opacity: 0.7;'>
            🕐 NL Time: {current_date_nl} {current_time_nl}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Highlights
    st.markdown("### ✨ Latest Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style='background-color: rgba(38, 39, 48, 0.5); padding: 15px; border-radius: 10px; 
                    border: 1px solid rgba(0, 255, 136, 0.3); height: 180px;'>
            <h4 style='color: #00ff88; margin-top: 0;'>🎬 Trade Replay</h4>
            <p style='font-size: 14px; line-height: 1.6;'>
                Replay your trading journey chronologically. Visualize entry/exit points 
                and see how your strategy evolved over time.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: rgba(38, 39, 48, 0.5); padding: 15px; border-radius: 10px; 
                    border: 1px solid rgba(0, 136, 255, 0.3); height: 180px;'>
            <h4 style='color: #0088ff; margin-top: 0;'>👨‍🏫 Mentor Mode</h4>
            <p style='font-size: 14px; line-height: 1.6;'>
                Share your journal with coaches using a unique code. Mentors get 
                read-only access to review your trades and provide feedback.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background-color: rgba(38, 39, 48, 0.5); padding: 15px; border-radius: 10px; 
                    border: 1px solid rgba(255, 136, 0, 0.3); height: 180px;'>
            <h4 style='color: #ff8800; margin-top: 0;'>📊 Advanced Analytics</h4>
            <p style='font-size: 14px; line-height: 1.6;'>
                Max Drawdown, Sharpe Ratio, Profit Factor, Day of Week analysis, 
                Psychology insights, and more professional metrics.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    # Additional features in compact format
    with st.expander("🚀 More Features", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Core Features:**
            - 📝 Multi-user system with private journals
            - 💼 Multiple trading accounts
            - 📅 Calendar view with daily P&L
            - 🧠 Psychology & mood tracking
            - 📔 Daily journal notes
            - 💱 Multi-currency support ($/€)
            """)
        
        with col2:
            st.markdown("""
            **Analytics & Charts:**
            - 📈 Equity curve & drawdown chart
            - 📊 Monthly performance breakdown
            - 💰 Profit by symbol analysis
            - 📅 Best day of week insights
            - 🎯 R-multiple tracking
            - 📥 CSV export with filters
            """)
    
    st.markdown("---")
    
    # Privacy Disclaimer
    st.markdown("""
    <style>
        .privacy-disclaimer {
            background: linear-gradient(135deg, rgba(255, 136, 0, 0.15) 0%, rgba(255, 68, 68, 0.15) 100%);
            border: 2px solid rgba(255, 136, 0, 0.5);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .privacy-disclaimer h4 {
            color: #ff8800;
            margin-top: 0;
            font-size: 18px;
        }
        .privacy-disclaimer p {
            margin: 10px 0;
            line-height: 1.6;
            font-size: 14px;
        }
        .privacy-disclaimer ul {
            margin: 10px 0;
            padding-left: 25px;
        }
        .privacy-disclaimer li {
            margin: 5px 0;
            line-height: 1.5;
        }
    </style>
    <div class="privacy-disclaimer">
        <h4>⚠️ Privacy & Data Disclaimer</h4>
        <p><strong>Important:</strong> By using this Trading Journal, you acknowledge that:</p>
        <ul>
            <li>🔍 The <strong>admin</strong> has access to all user data, including your trades and statistics</li>
            <li>👨‍🏫 You can share your journal with coaches via <strong>Mentor Mode</strong> (read-only access)</li>
            <li>🔒 Your data is stored locally in JSON files on the server</li>
            <li>📊 No data is shared with third parties - only the admin has access</li>
        </ul>
        <p style='margin-top: 15px; font-size: 13px; opacity: 0.9;'>
            By logging in or registering, you agree to these terms.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs for login, register, and mentor access
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Register", "👨‍🏫 Mentor Access"])
    
    with tab1:
        st.subheader("Login to Your Journal")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
        
        # Handle login outside form to prevent message conflicts
        if submit:
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state['user'] = user
                    st.session_state['logged_in'] = True
                    st.rerun()  # Immediate rerun
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.error("❌ Please fill in all fields")
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            new_username = st.text_input("Choose Username", key="reg_user")
            new_display_name = st.text_input("Display Name", key="reg_display")
            new_password = st.text_input("Choose Password", type="password", key="reg_pass")
            new_password_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_conf")
            register = st.form_submit_button("Register", use_container_width=True)
        
        # Handle registration outside form to prevent message conflicts
        if register:
            if new_username and new_display_name and new_password and new_password_confirm:
                if new_password != new_password_confirm:
                    st.error("❌ Passwords don't match")
                elif len(new_password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    success, result = register_user(new_username, new_password, new_display_name)
                    if success:
                        st.success(f"✅ Account created! You can now login with username: {new_username}")
                    else:
                        st.error(f"❌ {result}")
            else:
                st.error("❌ Please fill in all fields")
    
    with tab3:
        st.subheader("🎓 Mentor/Coach Access")
        st.info("💡 Enter a student's share code to view their journal (read-only)")
        
        with st.form("mentor_access_form"):
            share_code = st.text_input("Enter Share Code", placeholder="e.g. TJ-1-A2O9")
            mentor_name = st.text_input("Your Name (Optional)", placeholder="e.g. Coach John")
            access_submit = st.form_submit_button("📊 Access Journal", use_container_width=True)
        
        # Handle form submission OUTSIDE the form to prevent message conflicts
        if access_submit:
            if share_code:
                # Decode share code: TJ-{user_id}-{username_prefix}
                try:
                    parts = share_code.strip().upper().split('-')
                    if len(parts) == 3 and parts[0] == 'TJ':
                        student_id = int(parts[1])
                        
                        # Find user by ID
                        all_users = load_users()
                        student_user = None
                        for u in all_users:
                            if u['id'] == student_id:
                                student_user = u
                                break
                        
                        if student_user:
                            # Create mentor session
                            st.session_state['user'] = student_user
                            st.session_state['logged_in'] = True
                            st.session_state['mentor_mode'] = True
                            st.session_state['mentor_name'] = mentor_name if mentor_name else "Mentor"
                            st.rerun()  # Immediate rerun, no success message needed here
                        else:
                            st.error("❌ Invalid share code - Student not found")
                    else:
                        st.error("❌ Invalid share code format. Use format: TJ-X-XXXX")
                except ValueError:
                    st.error("❌ Invalid share code - User ID must be a number")
                except Exception as e:
                    st.error("❌ Invalid share code format. Please check and try again.")
            else:
                st.error("❌ Please enter a share code")
        
        st.divider()
        
        with st.expander("ℹ️ How does Mentor Access work?", expanded=False):
            st.markdown("""
            **For Mentors/Coaches:**
            1. Ask your student for their **Share Code**
            2. Enter the code above
            3. You'll get **read-only** access to their journal
            4. You can view all trades, stats, and analytics
            5. You **cannot** edit or delete their data
            
            **For Students:**
            - Enable sharing in **👨‍🏫 Mentor Mode** tab
            - Share your code with your mentor/coach
            - Your data stays safe - mentors can only view, not edit
            """)

# ===== CHECK LOGIN STATUS =====

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    login_page()
    st.stop()

# Get current user
current_user = st.session_state['user']

# ===== APP STARTS HERE (after login) =====

def load_settings():
    """Load app settings - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        return dl_load_settings()
    
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

def save_settings(settings):
    """Save app settings - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        dl_save_settings(settings)
    else:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)

# ===== MISTAKES MANAGEMENT =====

def load_mistakes(user_id=None):
    """Load mistakes from JSON file"""
    if os.path.exists(MISTAKES_FILE):
        try:
            with open(MISTAKES_FILE, 'r') as f:
                mistakes = json.load(f)
                if user_id is not None:
                    return [m for m in mistakes if m.get('user_id') == user_id]
                return mistakes
        except:
            return []
    return []

def save_mistakes(mistakes):
    """Save mistakes to JSON file"""
    with open(MISTAKES_FILE, 'w') as f:
        json.dump(mistakes, f, indent=2)

def add_mistake(user_id, mistake_type, description, trade_id=None):
    """Add a new mistake"""
    mistakes = load_mistakes()
    new_id = max([m['id'] for m in mistakes], default=-1) + 1
    mistake = {
        'id': new_id,
        'user_id': user_id,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'mistake_type': mistake_type,
        'description': description,
        'trade_id': trade_id
    }
    mistakes.append(mistake)
    save_mistakes(mistakes)
    return mistake

# ===== AVOIDED TRADES =====

def load_avoided_trades(user_id=None):
    """Load avoided trades from JSON file"""
    if os.path.exists(AVOIDED_TRADES_FILE):
        try:
            with open(AVOIDED_TRADES_FILE, 'r') as f:
                avoided = json.load(f)
                if user_id is not None:
                    return [a for a in avoided if a.get('user_id') == user_id]
                return avoided
        except:
            return []
    return []

def save_avoided_trades(avoided):
    """Save avoided trades to JSON file"""
    with open(AVOIDED_TRADES_FILE, 'w') as f:
        json.dump(avoided, f, indent=2)

def add_avoided_trade(user_id, symbol, reason, potential_loss=0, notes=""):
    """Add a new avoided trade"""
    avoided = load_avoided_trades()
    new_id = max([a['id'] for a in avoided], default=-1) + 1
    trade = {
        'id': new_id,
        'user_id': user_id,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'symbol': symbol,
        'reason': reason,
        'potential_loss': potential_loss,
        'notes': notes
    }
    avoided.append(trade)
    save_avoided_trades(avoided)
    return trade

# ===== PRE-TRADE ANALYSIS =====

def load_pretrade_analysis(user_id=None):
    """Load pre-trade analysis from JSON file"""
    if os.path.exists(PRETRADE_ANALYSIS_FILE):
        try:
            with open(PRETRADE_ANALYSIS_FILE, 'r') as f:
                analysis = json.load(f)
                if user_id is not None:
                    return [a for a in analysis if a.get('user_id') == user_id]
                return analysis
        except:
            return []
    return []

def save_pretrade_analysis(analysis):
    """Save pre-trade analysis to JSON file"""
    with open(PRETRADE_ANALYSIS_FILE, 'w') as f:
        json.dump(analysis, f, indent=2)

def add_pretrade_analysis(user_id, symbol, direction, entry_plan, stop_loss, take_profit, risk_reward, confidence, checklist):
    """Add a new pre-trade analysis"""
    analysis = load_pretrade_analysis()
    new_id = max([a['id'] for a in analysis], default=-1) + 1
    pretrade = {
        'id': new_id,
        'user_id': user_id,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'symbol': symbol,
        'direction': direction,
        'entry_plan': entry_plan,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'risk_reward': risk_reward,
        'confidence': confidence,
        'checklist': checklist,
        'executed': False,
        'trade_id': None
    }
    analysis.append(pretrade)
    save_pretrade_analysis(analysis)
    return pretrade

# ===== QUOTES SYSTEM =====

def load_quotes():
    """Load quotes - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        return dl_load_quotes()
    
    # Fallback to JSON
    if os.path.exists(QUOTES_FILE):
        try:
            with open(QUOTES_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_quotes(quotes):
    """Save quotes - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        dl_save_quotes(quotes)
    else:
        with open(QUOTES_FILE, 'w') as f:
            json.dump(quotes, f, indent=2)

def add_quote(text, author=""):
    """Add a new quote - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        return dl_add_quote(text, author)
    
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

# ===== MINDSET CHECK-INS =====

def load_mindset_checkins(user_id=None):
    """Load mindset check-ins from JSON file"""
    if os.path.exists(MINDSET_CHECKINS_FILE):
        try:
            with open(MINDSET_CHECKINS_FILE, 'r') as f:
                checkins = json.load(f)
                if user_id is not None:
                    return [c for c in checkins if c.get('user_id') == user_id]
                return checkins
        except:
            return []
    return []

def save_mindset_checkins(checkins):
    """Save mindset check-ins to JSON file"""
    with open(MINDSET_CHECKINS_FILE, 'w') as f:
        json.dump(checkins, f, indent=2)

def add_mindset_checkin(user_id, focus_level, locked_in, emotional_state, notes=""):
    """Add a new mindset check-in"""
    checkins = load_mindset_checkins()
    new_id = max([c['id'] for c in checkins], default=-1) + 1
    checkin = {
        'id': new_id,
        'user_id': user_id,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S'),
        'focus_level': focus_level,
        'locked_in': locked_in,
        'emotional_state': emotional_state,
        'notes': notes
    }
    checkins.append(checkin)
    save_mindset_checkins(checkins)
    return checkin

def load_accounts(user_id=None):
    """Load accounts - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        return dl_load_accounts(user_id)
    
    # Fallback to JSON
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r') as f:
                accounts = json.load(f)
                # Add user_id if not present (legacy data)
                for acc in accounts:
                    if 'user_id' not in acc:
                        acc['user_id'] = 0
                
                # Filter by user_id if specified
                if user_id is not None:
                    accounts = [a for a in accounts if a.get('user_id') == user_id]
                
                return accounts if accounts else [{"name": "Main Account", "size": 10000, "id": 0, "user_id": user_id}]
        except:
            return [{"name": "Main Account", "size": 10000, "id": 0, "user_id": user_id if user_id else 0}]
    return [{"name": "Main Account", "size": 10000, "id": 0, "user_id": user_id if user_id else 0}]

def save_accounts(accounts):
    """Save accounts - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        dl_save_accounts(accounts)
    else:
        with open(ACCOUNTS_FILE, 'w') as f:
            json.dump(accounts, f, indent=2)

def load_trades(user_id=None):
    """Load trades - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        return dl_load_trades(user_id)
    
    # Fallback to JSON
    if os.path.exists(TRADES_FILE):
        try:
            with open(TRADES_FILE, 'r') as f:
                trades = json.load(f)
                # Add unique IDs if they don't exist
                for i, trade in enumerate(trades):
                    if 'id' not in trade:
                        trade['id'] = i
                    # Add default account_id if not present
                    if 'account_id' not in trade:
                        trade['account_id'] = 0
                    # Add user_id if not present (legacy data)
                    if 'user_id' not in trade:
                        trade['user_id'] = 0
                    # Add default psychological fields if not present
                    if 'trade_type' not in trade:
                        trade['trade_type'] = 'Daytrade'
                    if 'market_condition' not in trade:
                        trade['market_condition'] = 'Trending'
                    if 'mood' not in trade:
                        trade['mood'] = 'Calm'
                    if 'focus_level' not in trade:
                        trade['focus_level'] = 3
                    if 'stress_level' not in trade:
                        trade['stress_level'] = 3
                    if 'sleep_quality' not in trade:
                        trade['sleep_quality'] = 3
                    if 'pre_trade_confidence' not in trade:
                        trade['pre_trade_confidence'] = 3
                    if 'duration_minutes' not in trade:
                        trade['duration_minutes'] = 0
                    if 'influence' not in trade:
                        trade['influence'] = ''
                
                # Filter by user_id if specified
                if user_id is not None:
                    trades = [t for t in trades if t.get('user_id') == user_id]
                
                return trades
        except:
            return []
    return []

def save_trades(trades):
    """Save trades - Uses Database or JSON fallback"""
    if DATA_LAYER_AVAILABLE:
        dl_save_trades(trades)
    else:
        with open(TRADES_FILE, 'w') as f:
            json.dump(trades, f, indent=2)

def delete_trade(trade_id):
    """Delete a specific trade by ID"""
    trades = load_trades()
    trades = [t for t in trades if t.get('id') != trade_id]
    # Reassign IDs sequentially
    for i, trade in enumerate(trades):
        trade['id'] = i
    save_trades(trades)
    return True

def load_daily_notes(user_id=None):
    """Load daily notes from JSON file"""
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, 'r') as f:
                notes = json.load(f)
                # Filter by user_id if specified
                if user_id is not None:
                    notes = [n for n in notes if n.get('user_id') == user_id]
                return notes
        except:
            return []
    return []

def save_daily_notes(notes):
    """Save daily notes to JSON file"""
    with open(NOTES_FILE, 'w') as f:
        json.dump(notes, f, indent=2)

def add_daily_note(user_id, date, note_text, mood, energy_level):
    """Add or update a daily note"""
    all_notes = load_daily_notes()
    
    # Check if note for this date and user already exists
    existing_note = None
    for i, note in enumerate(all_notes):
        if note['date'] == date and note.get('user_id') == user_id:
            existing_note = i
            break
    
    note_entry = {
        'user_id': user_id,
        'date': date,
        'note': note_text,
        'mood': mood,
        'energy_level': energy_level,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if existing_note is not None:
        all_notes[existing_note] = note_entry
    else:
        all_notes.append(note_entry)
    
    save_daily_notes(all_notes)
    return True

def delete_daily_note(user_id, date):
    """Delete a daily note"""
    all_notes = load_daily_notes()
    all_notes = [n for n in all_notes if not (n['date'] == date and n.get('user_id') == user_id)]
    save_daily_notes(all_notes)
    return True

def calculate_pnl(entry, exit, quantity, side):
    """Calculate profit/loss for a trade"""
    if side == "Long":
        pnl = (exit - entry) * quantity
    else:  # Short
        pnl = (entry - exit) * quantity
    return pnl

def calculate_r_multiple(pnl, account_size):
    """Calculate R-multiple (assuming 1R = 1% of account)"""
    one_r = account_size * 0.01
    return pnl / one_r if one_r > 0 else 0

def calculate_metrics(df):
    """Calculate trading metrics including advanced metrics"""
    if len(df) == 0:
        return {
            'total_profit': 0,
            'win_rate': 0,
            'Expectancy': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'max_drawdown_pct': 0
        }
    
    # Ensure pnl column exists and is numeric
    if 'pnl' not in df.columns:
        return {
            'total_profit': 0,
            'win_rate': 0,
            'Expectancy': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'max_drawdown_pct': 0
        }
    
    # Convert pnl to numeric and remove any non-numeric values
    df_clean = df.copy()
    df_clean['pnl'] = pd.to_numeric(df_clean['pnl'], errors='coerce')
    df_clean = df_clean.dropna(subset=['pnl'])
    
    if len(df_clean) == 0:
        return {
            'total_profit': 0,
            'win_rate': 0,
            'Expectancy': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'profit_factor': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'max_drawdown_pct': 0
        }
    
    total_profit = df_clean['pnl'].sum()
    winning_trades = len(df_clean[df_clean['pnl'] > 0])
    losing_trades = len(df_clean[df_clean['pnl'] < 0])
    total_trades = len(df_clean)
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate Expectancy
    avg_win = df_clean[df_clean['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
    avg_loss = abs(df_clean[df_clean['pnl'] < 0]['pnl'].mean()) if losing_trades > 0 else 0
    
    if total_trades > 0:
        Expectancy = (win_rate/100 * avg_win) - ((1 - win_rate/100) * avg_loss)
    else:
        Expectancy = 0
    
    # Calculate Profit Factor
    gross_profit = df_clean[df_clean['pnl'] > 0]['pnl'].sum() if winning_trades > 0 else 0
    gross_loss = abs(df_clean[df_clean['pnl'] < 0]['pnl'].sum()) if losing_trades > 0 else 0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
    
    # Calculate Sharpe Ratio (assuming daily returns) - with safe std calculation
    if len(df_clean) > 1:
        returns = df_clean['pnl']
        try:
            returns_mean = returns.mean()
            returns_std = returns.std()
            if pd.notna(returns_std) and returns_std > 0:
                sharpe_ratio = (returns_mean / returns_std) * (252 ** 0.5)
            else:
                sharpe_ratio = 0
        except Exception:
            sharpe_ratio = 0
    else:
        sharpe_ratio = 0
    
    # Calculate Max Drawdown - using clean data
    try:
        df_sorted = df_clean.sort_values('date')
        cumulative = df_sorted['pnl'].cumsum()
        running_max = cumulative.cummax()
        drawdown = cumulative - running_max
        max_drawdown = abs(drawdown.min()) if len(drawdown) > 0 else 0
        
        # Max Drawdown Percentage
        peak = running_max.max()
        max_drawdown_pct = (max_drawdown / peak * 100) if peak > 0 else 0
    except Exception:
        max_drawdown = 0
        max_drawdown_pct = 0
    
    return {
        'total_profit': total_profit,
        'win_rate': win_rate,
        'Expectancy': Expectancy,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'profit_factor': profit_factor,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'max_drawdown_pct': max_drawdown_pct
    }

def get_daily_stats(df):
    """Calculate daily statistics"""
    if len(df) == 0:
        return pd.DataFrame()
    
    daily = df.groupby(df['date'].dt.date).agg({
        'pnl': ['sum', 'count']
    }).reset_index()
    daily.columns = ['date', 'pnl', 'trades']
    daily['date'] = pd.to_datetime(daily['date'])
    return daily

def create_calendar_view(df, year, month):
    """Create a calendar heatmap view"""
    if len(df) == 0:
        return None
    
    # Filter for specific month
    month_data = df[(df['date'].dt.year == year) & (df['date'].dt.month == month)]
    
    if len(month_data) == 0:
        return None
    
    # Get daily stats
    daily_stats = month_data.groupby(month_data['date'].dt.date).agg({
        'pnl': 'sum',
        'symbol': 'count'
    }).reset_index()
    daily_stats.columns = ['date', 'pnl', 'num_trades']
    # Don't convert to datetime, keep as date for comparison
    
    return daily_stats

# Streamlit App
st.set_page_config(
    page_title="Trading Journal Pro", 
    layout="wide", 
    page_icon="📈",
    initial_sidebar_state="expanded"  # Sidebar always starts expanded with collapse button visible
)

# Load settings for dark mode
settings = load_settings()
dark_mode = settings.get('dark_mode', False)

# Custom CSS for better styling with dark/light mode support
if dark_mode:
    bg_color = "#0E1117"
    secondary_bg = "#262730"
    text_color = "#FAFAFA"
    card_bg = "#262730"
    border_color = "#38383d"
    input_bg = "#262730"
    hover_color = "#38383d"
else:
    bg_color = "#FFFFFF"
    secondary_bg = "#F0F2F6"
    text_color = "#31333F"
    card_bg = "#FFFFFF"
    border_color = "#D3D3D3"
    input_bg = "#FFFFFF"
    hover_color = "#E8E8E8"

st.markdown(f"""
<style>
    /* Main background */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {secondary_bg};
    }}
    
    /* Sidebar collapse button - make it visible */
    [data-testid="collapsedControl"] {{
        color: {text_color} !important;
        background-color: {card_bg} !important;
        border: 2px solid {border_color} !important;
    }}
    
    [data-testid="collapsedControl"]:hover {{
        background-color: {hover_color} !important;
        border-color: {text_color} !important;
    }}
    
    /* All text */
    .stMarkdown, p, span, label, .stTextInput label, .stTextArea label, 
    .stSelectbox label, .stDateInput label, .stNumberInput label {{
        color: {text_color} !important;
    }}
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stDateInput > div > div > div {{
        background-color: {input_bg} !important;
        color: {text_color} !important;
        border-color: {border_color} !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: {card_bg};
        color: {text_color};
        border: 1px solid {border_color};
    }}
    
    .stButton > button:hover {{
        background-color: {hover_color};
        border-color: {text_color};
    }}
    
    /* Metrics */
    [data-testid="stMetricValue"] {{
        color: {text_color} !important;
    }}
    
    /* Dataframes */
    .stDataFrame {{
        background-color: {card_bg};
    }}
    
    /* Expanders */
    .streamlit-expanderHeader {{
        background-color: {card_bg};
        color: {text_color};
        border: 1px solid {border_color};
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
        background-color: {secondary_bg};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: {card_bg};
        color: {text_color};
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {hover_color};
    }}
    
    /* Custom classes */
    .profit-positive {{
        color: #00ff00;
        font-weight: bold;
    }}
    
    .profit-negative {{
        color: #ff4444;
        font-weight: bold;
    }}
    
    .metric-card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid {border_color};
    }}
    
    .version-badge {{
        background-color: {card_bg};
        padding: 8px 12px;
        border-radius: 5px;
        border: 1px solid {border_color};
        font-size: 12px;
        text-align: center;
        color: {text_color};
    }}
    
    /* Form containers */
    .stForm {{
        background-color: {card_bg};
        border: 1px solid {border_color};
        padding: 20px;
        border-radius: 10px;
    }}
    
    /* Info/Warning/Success boxes */
    .stAlert {{
        background-color: {card_bg};
        border: 1px solid {border_color};
    }}
</style>
""", unsafe_allow_html=True)

header_col1, header_col2, header_col3 = st.columns([2, 1, 1])

with header_col1:
    st.title("📈 Trading Journal Pro")
    st.markdown(f"""
    <div class="version-badge">
        <strong>Version {APP_VERSION}</strong> | Last Updated: {LAST_UPDATE}
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    st.write("")
    st.write("")
    theme_col1, theme_col2 = st.columns(2)
    
    with theme_col1:
        if st.button("🌙 Dark", use_container_width=True, type="primary" if dark_mode else "secondary", key="header_dark"):
            settings['dark_mode'] = True
            save_settings(settings)
            st.rerun()
    
    with theme_col2:
        if st.button("☀️ Light", use_container_width=True, type="primary" if not dark_mode else "secondary", key="header_light"):
            settings['dark_mode'] = False
            save_settings(settings)
            st.rerun()

with header_col3:
    st.write("")
    st.write("")
    st.markdown("""
    <style>
        .sidebar-hint {
            background-color: rgba(255, 136, 0, 0.2);
            border: 2px solid #ff8800;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
            margin-top: 5px;
        }
    </style>
    <div class="sidebar-hint">
        👈 Click the arrow on the left edge<br>to open/close sidebar
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ===== DATABASE MIGRATION NOTICE =====
# Check database status
try:
    db_status = get_data_source() if DATA_LAYER_AVAILABLE else "JSON Files ⚠️"
    using_db = use_database() if DATA_LAYER_AVAILABLE else False
except:
    db_status = "Checking..."
    using_db = False

if using_db:
    st.success(f"""
    ✅ **DATABASE MIGRATIE SUCCESVOL!**
    
    Je Trading Journal gebruikt nu **PostgreSQL** voor data opslag!
    
    **Voordelen:**
    - ✅ **Geen data loss meer** bij updates
    - ✅ **Veilige opslag** (niet in publieke repository)  
    - ✅ **Betere performance & schaalbaarheid**
    - 📊 Data source: **{db_status}**
    """)
else:
    st.warning("""
    ⚠️ **DATABASE MIGRATIE BEZIG**
    
    Je Trading Journal wordt gemigreerd naar een **PostgreSQL database** voor permanente data opslag!
    
    **Wat betekent dit:**
    - ✅ **Geen data loss meer** bij updates
    - ✅ **Veilige opslag** (niet in publieke repository)
    - ✅ **Betere performance**
    - 📊 Je huidige data wordt automatisch gemigreerd
    
    **LET OP:** Tijdens de migratie kunnen sommige functies tijdelijk niet werken. We zijn zo terug! 🚀
    """)
    
    st.info("💾 **Status:** Database setup in uitvoering... Export je data als backup via '📊 All Trades' → '📥 Export'")

st.write("")

# ===== QUOTES SLIDER WITH MANUAL ROTATION =====
quotes = load_quotes()
active_quotes = [q for q in quotes if q.get('active', True)]
if active_quotes:
    import random
    
    # Initialize quote index if not present
    if 'current_quote_idx' not in st.session_state:
        st.session_state['current_quote_idx'] = random.randint(0, len(active_quotes) - 1)
    
    # Get current quote
    quote_idx = st.session_state['current_quote_idx'] % len(active_quotes)
    current_quote = active_quotes[quote_idx]
    
    # Create columns for quote and navigation
    quote_col, btn_col = st.columns([5, 1])
    
    with quote_col:
        # Display sliding quote banner
        st.markdown(f"""
        <style>
            @keyframes slideIn {{
                from {{ transform: translateX(-100%); opacity: 0; }}
                to {{ transform: translateX(0); opacity: 1; }}
            }}
            .quote-banner {{
                background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 136, 255, 0.1) 100%);
                border-left: 4px solid #00ff88;
                padding: 15px 20px;
                border-radius: 8px;
                margin: 10px 0 20px 0;
                animation: slideIn 0.8s ease-out;
                box-shadow: 0 2px 8px rgba(0, 255, 136, 0.2);
            }}
            .quote-text {{
                font-size: 16px;
                font-style: italic;
                margin: 0;
                color: #e0e0e0;
            }}
            .quote-author {{
                font-size: 14px;
                text-align: right;
                margin-top: 8px;
                color: #00ff88;
                font-weight: 600;
            }}
        </style>
        <div class="quote-banner">
            <p class="quote-text">"{current_quote['text']}"</p>
            <p class="quote-author">— {current_quote.get('author', 'Trading Wisdom')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with btn_col:
        # Show next quote button if there are multiple quotes
        if len(active_quotes) > 1:
            st.write("")
            st.write("")
            if st.button("🔄", key="rotate_quote", help="Next quote"):
                st.session_state['current_quote_idx'] = (st.session_state['current_quote_idx'] + 1) % len(active_quotes)
                st.rerun()
    
    # Display quote counter
    if len(active_quotes) > 1:
        st.caption(f"💬 Quote {quote_idx + 1} of {len(active_quotes)} • Click 🔄 for next")

# ===== 15-MINUTE MINDSET CHECK-IN SYSTEM =====
# Initialize check-in state
if 'last_checkin_time' not in st.session_state:
    st.session_state['last_checkin_time'] = datetime.now()
    st.session_state['show_checkin_alert'] = False

# Check if 15 minutes have passed
time_since_checkin = datetime.now() - st.session_state['last_checkin_time']
if time_since_checkin.total_seconds() >= 900:  # 900 seconds = 15 minutes
    st.session_state['show_checkin_alert'] = True

# Display mindset check-in alert
if st.session_state.get('show_checkin_alert', False):
    st.markdown("""
    <style>
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
        }}
        .checkin-alert {{
            background: linear-gradient(135deg, rgba(255, 136, 0, 0.2) 0%, rgba(255, 68, 68, 0.2) 100%);
            border: 2px solid #ff8800;
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
            animation: pulse 2s infinite;
            box-shadow: 0 4px 12px rgba(255, 136, 0, 0.3);
        }}
        .checkin-title {{
            font-size: 20px;
            font-weight: bold;
            color: #ff8800;
            margin-bottom: 10px;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="checkin-alert">', unsafe_allow_html=True)
        st.markdown('<div class="checkin-title">⏰ Mindset Check-In Time!</div>', unsafe_allow_html=True)
        st.write("Het is tijd om je mindset te checken. Ben je nog steeds gefocust en locked in?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Check-in Nu", use_container_width=True, type="primary"):
                st.session_state['open_checkin_form'] = True
                st.session_state['show_checkin_alert'] = False
                st.rerun()
        
        with col2:
            if st.button("⏰ Herinner me over 5 min", use_container_width=True):
                st.session_state['last_checkin_time'] = datetime.now() - timedelta(minutes=10)  # Will trigger again in 5 min
                st.session_state['show_checkin_alert'] = False
                st.rerun()
        
        with col3:
            if st.button("❌ Sluiten", use_container_width=True):
                st.session_state['last_checkin_time'] = datetime.now()
                st.session_state['show_checkin_alert'] = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Mindset check-in form (if triggered)
if st.session_state.get('open_checkin_form', False):
    with st.form("mindset_checkin_form"):
        st.subheader("🧠 Mindset Check-In")
        
        focus_level = st.slider("Focus Level (1-10)", 1, 10, 5)
        locked_in = st.radio("Ben je nog steeds locked in?", ["Ja, volledig gefocust", "Beetje afgeleid", "Nee, niet meer gefocust"])
        emotional_state = st.selectbox("Huidige emotionele staat", 
                                       ["Calm & Focused", "Excited", "Anxious", "Frustrated", "Tired", "Bored", "Stressed"])
        notes = st.text_area("Notities (optioneel)", placeholder="Hoe voel je je? Wat speelt er?")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_checkin = st.form_submit_button("✅ Check-in Opslaan", use_container_width=True, type="primary")
        with col2:
            cancel_checkin = st.form_submit_button("❌ Annuleren", use_container_width=True)
        
        if submit_checkin:
            add_mindset_checkin(
                user_id=current_user['id'],
                focus_level=focus_level,
                locked_in=locked_in,
                emotional_state=emotional_state,
                notes=notes
            )
            st.session_state['last_checkin_time'] = datetime.now()
            st.session_state['open_checkin_form'] = False
            st.success("✅ Mindset check-in opgeslagen!")
            st.rerun()
        
        if cancel_checkin:
            st.session_state['open_checkin_form'] = False
            st.session_state['last_checkin_time'] = datetime.now()
            st.rerun()

# Force reload data on each run (prevents deleted trades from coming back)
if 'force_reload' in st.session_state:
    del st.session_state['force_reload']

# Load existing trades, accounts, and settings for current user
trades = load_trades(current_user['id'])
accounts = load_accounts(current_user['id'])
settings = load_settings()
currency = settings.get('currency', '$')

# ===== RISK ALERTS SYSTEM =====
if ALERTS_AVAILABLE and len(trades) >= 5:
    # Check for active alerts
    active_alerts = check_all_alerts(trades, DEFAULT_THRESHOLDS, account_size=10000)
    
    if active_alerts:
        # Separate by severity
        critical_alerts = [a for a in active_alerts if a.severity == "CRITICAL"]
        warning_alerts = [a for a in active_alerts if a.severity == "WARNING"]
        
        # Display critical alerts
        if critical_alerts:
            for alert in critical_alerts:
                st.error(alert.message)
        
        # Display warnings in expandable section
        if warning_alerts:
            with st.expander(f"⚠️ {len(warning_alerts)} Warning(s) - Click to view", expanded=False):
                for alert in warning_alerts:
                    st.warning(alert.message)
        
        st.divider()

# Check if in mentor mode
is_mentor_mode = st.session_state.get('mentor_mode', False)
mentor_name = st.session_state.get('mentor_name', 'Mentor')

# Mentor mode banner (always visible, even if sidebar collapsed)
if is_mentor_mode:
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.warning(f"👨‍🏫 **Mentor Mode Active** | Viewing: **{current_user['display_name']}**'s Journal ({mentor_name}) | 🔒 Read-Only")
    
    with col2:
        if st.button("🚪 Exit Mentor Mode", type="primary", use_container_width=True):
            st.session_state['logged_in'] = False
            del st.session_state['user']
            if 'mentor_mode' in st.session_state:
                del st.session_state['mentor_mode']
            if 'mentor_name' in st.session_state:
                del st.session_state['mentor_name']
            st.rerun()
    
    st.divider()

# Sidebar for settings
with st.sidebar:
    # Mentor mode indicator
    if is_mentor_mode:
        st.warning(f"👨‍🏫 **Mentor View** ({mentor_name})")
        st.info(f"📊 Viewing: **{current_user['display_name']}**'s Journal")
        
        if st.button("🚪 Exit Mentor Mode", use_container_width=True):
            st.session_state['logged_in'] = False
            del st.session_state['user']
            if 'mentor_mode' in st.session_state:
                del st.session_state['mentor_mode']
            if 'mentor_name' in st.session_state:
                del st.session_state['mentor_name']
            st.rerun()
        
        st.caption("🔒 **Read-Only Mode** - You cannot edit or delete data")
    else:
        # User info and logout
        st.success(f"👤 Logged in as: **{current_user['display_name']}**")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state['logged_in'] = False
            del st.session_state['user']
            st.rerun()
    
    st.divider()
    
    # Theme Toggle
    st.subheader("⚙️ Appearance")
    theme_col1, theme_col2 = st.columns(2)
    
    with theme_col1:
        if st.button("🌙 Dark", use_container_width=True, type="primary" if dark_mode else "secondary"):
            settings['dark_mode'] = True
            save_settings(settings)
            st.rerun()
    
    with theme_col2:
        if st.button("☀️ Light", use_container_width=True, type="primary" if not dark_mode else "secondary"):
            settings['dark_mode'] = False
            save_settings(settings)
            st.rerun()
    
    st.divider()
    
    # ==== NAVIGATION MENU ====
    st.header("📍 Navigation")
    
    # Create navigation options
    nav_options = [
        "📝 Add Trade",
        "📊 All Trades", 
        "📅 Calendar",
        "💰 Per Symbol",
        "📈 Weekly Price Action",
        "🧠 Psychology",
        "🔬 Advanced Analytics",
        "🤖 AI Assistant",
        "📱 Mobile PWA",
        "🔗 Broker Integration",
        "🎯 Risk Calculator",
        "📔 Daily Journal",
        "🎬 Trade Replay",
        "📄 Export PDF",
        "📥 Import/Export",
        "🏆 Achievements",
        "👨‍🏫 Mentor Mode",
        "❌ Mistakes",
        "🛡️ Avoided Trades",
        "📋 Pre-Trade Plan",
        "💬 Admin Quotes"
    ]
    
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = "📝 Add Trade"
    
    # Navigation menu
    selected_page = st.radio(
        "Select Page:",
        nav_options,
        index=nav_options.index(st.session_state['current_page']),
        key="nav_radio",
        label_visibility="collapsed"
    )
    
    # Update current page
    st.session_state['current_page'] = selected_page
    
    st.divider()
    
    # Admin Panel (only visible to admin user)
    if current_user['username'] == 'admin':
        with st.expander("👑 Admin Panel", expanded=False):
            st.subheader("📋 Registered Users & Activity")
            
            # Refresh button to reload latest data
            if st.button("🔄 Refresh Stats", use_container_width=True):
                st.rerun()
            
            # Force load all data freshly (bypass any caching)
            all_users = load_users()
            
            # Load ALL trades from file directly (no user_id filter)
            if os.path.exists(TRADES_FILE):
                with open(TRADES_FILE, 'r') as f:
                    all_trades_data = json.load(f)
            else:
                all_trades_data = []
            
            # Debug info
            st.info(f"📊 **Debug Info:** Loaded {len(all_trades_data)} total trades from file | {len(all_users)} registered users")
            
            # Create a DataFrame for better display with activity stats
            users_display = []
            for user in all_users:
                # Get trades for this user (ensure type matching - convert both to int)
                user_id = int(user['id'])
                user_trades = [t for t in all_trades_data if int(t.get('user_id', 0)) == user_id]
                
                # Calculate stats
                num_trades = len(user_trades)
                
                if num_trades > 0:
                    # Count unique trading days
                    trade_dates = [pd.to_datetime(t['date']).date() for t in user_trades]
                    unique_days = len(set(trade_dates))
                    
                    # Get last activity
                    latest_trade = max([pd.to_datetime(t['date']) for t in user_trades])
                    last_activity = latest_trade.strftime('%Y-%m-%d')
                else:
                    unique_days = 0
                    last_activity = 'No activity'
                
                users_display.append({
                    'ID': user['id'],
                    'Username': user['username'],
                    'Display Name': user['display_name'],
                    'Registered': user.get('created_at', 'N/A'),
                    'Total Trades': num_trades,
                    'Trading Days': unique_days,
                    'Last Activity': last_activity
                })
            
            users_df = pd.DataFrame(users_display)
            
            # Sort by number of trades (most active first)
            users_df = users_df.sort_values('Total Trades', ascending=False)
            
            st.dataframe(users_df, use_container_width=True, hide_index=True)
            
            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Users", len(all_users))
            with col2:
                active_users = len([u for u in users_display if u['Total Trades'] > 0])
                st.metric("Active Users", active_users)
            with col3:
                total_trades = sum([u['Total Trades'] for u in users_display])
                st.metric("Total Trades", total_trades)
            
            st.divider()
            
            # Detailed user breakdown (for debugging)
            with st.expander("🔍 Debug: View Trades by User", expanded=False):
                debug_user = st.selectbox(
                    "Select user to inspect",
                    all_users,
                    format_func=lambda u: f"{u['username']} (ID: {u['id']}) - {u['display_name']}",
                    key="debug_user_select"
                )
                
                if debug_user:
                    debug_user_id = int(debug_user['id'])
                    debug_user_trades = [t for t in all_trades_data if int(t.get('user_id', 0)) == debug_user_id]
                    
                    st.info(f"**User ID:** {debug_user_id} | **Trades found:** {len(debug_user_trades)}")
                    
                    if debug_user_trades:
                        # Show first 5 trades with their user_id
                        st.markdown("**Sample Trades (first 5):**")
                        for i, t in enumerate(debug_user_trades[:5]):
                            st.text(f"{i+1}. Date: {t.get('date', 'N/A')} | Symbol: {t.get('symbol', 'N/A')} | user_id in trade: {t.get('user_id', 'MISSING')} | P&L: {currency}{t.get('pnl', 0):.2f}")
                    else:
                        st.warning("No trades found for this user. This could mean:\n- User hasn't added any trades yet\n- Trades are assigned to wrong user_id\n- Data synchronization issue")
            
            st.divider()
            
            # Reset user password section
            st.subheader("🔑 Reset User Password")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                user_to_reset = st.selectbox(
                    "Select User",
                    all_users,
                    format_func=lambda u: f"{u['username']} ({u['display_name']})",
                    key="admin_reset_user"
                )
            
            with col2:
                st.write("")
                st.write("")
            
            new_pass_admin = st.text_input("New Password", type="password", key="admin_new_pass")
            
            if st.button("🔄 Reset Password", type="primary", use_container_width=True):
                if new_pass_admin and len(new_pass_admin) >= 6:
                    success, message = change_password(user_to_reset['id'], new_pass_admin)
                    if success:
                        st.success(f"✅ Password reset for {user_to_reset['username']}")
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.error("❌ Password must be at least 6 characters")
        
        st.divider()
    
    # Change Password section (for all users)
    with st.expander("🔐 Change My Password", expanded=False):
        st.subheader("Change Your Password")
        
        with st.form("change_password_form"):
            old_password = st.text_input("Current Password", type="password", key="old_pass")
            new_password = st.text_input("New Password", type="password", key="new_pass")
            confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_pass")
            
            submit_pass = st.form_submit_button("🔄 Change Password", use_container_width=True)
            
            if submit_pass:
                if old_password and new_password and confirm_password:
                    # Verify old password
                    if old_password != current_user['password']:
                        st.error("❌ Current password is incorrect")
                    elif new_password != confirm_password:
                        st.error("❌ New passwords don't match")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters")
                    else:
                        success, message = change_password(current_user['id'], new_password)
                        if success:
                            st.success("✅ Password changed successfully! Please login again.")
                            # Update session
                            current_user['password'] = new_password
                            st.session_state['user'] = current_user
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.error("❌ Please fill in all fields")
    
    st.divider()
    
    st.header("💼 Account Management")
    
    # Currency selector
    st.subheader("💱 Currency")
    currency_option = st.selectbox(
        "Select Currency",
        ["$", "€"],
        index=0 if currency == "$" else 1,
        key="currency_selector"
    )
    
    if currency_option != currency:
        settings['currency'] = currency_option
        save_settings(settings)
        currency = currency_option
        st.rerun()
    
    st.divider()
    
    # Account selector
    if len(accounts) > 0:
        account_names = [f"{acc['name']} ({currency}{acc['size']:,.0f})" for acc in accounts]
        selected_account_idx = st.selectbox(
            "Select Account",
            range(len(accounts)),
            format_func=lambda x: account_names[x],
            key="selected_account"
        )
        selected_account = accounts[selected_account_idx]
        account_size = float(selected_account['size'])
        
        st.success(f"✅ Active: **{selected_account['name']}**")
        st.metric("Account Size", f"{currency}{account_size:,.0f}")
    else:
        selected_account = {"name": "Main Account", "size": 10000, "id": 0}
        account_size = 10000
    
    st.divider()
    
    # Add new account
    with st.expander("➕ Nieuw Add Account"):
        with st.form("add_account_form"):
            new_account_name = st.text_input("Account Name", placeholder="e.g. Futures Account")
            new_account_size = st.number_input("Account Size ($)", value=10000.0, min_value=100.0, step=1000.0)
            
            if st.form_submit_button("Add Account"):
                if new_account_name:
                    # Get highest ID across ALL accounts (not just user's)
                    all_accounts = load_accounts()
                    new_id = max([acc['id'] for acc in all_accounts], default=-1) + 1
                    accounts.append({
                        "name": new_account_name,
                        "size": new_account_size,
                        "id": new_id,
                        "user_id": current_user['id']
                    })
                    save_accounts(accounts)
                    st.success(f"Account '{new_account_name}' toegevoegd!")
                    st.rerun()
                else:
                    st.error("Enter a name for the account")
    
    # Edit/Rename accounts
    with st.expander("✏️ Edit Accounts"):
        for acc in accounts:
            st.subheader(f"Account: {acc['name']}")
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                new_name = st.text_input(
                    "Nieuwe Naam",
                    value=acc['name'],
                    key=f"rename_{acc['id']}",
                    placeholder="e.g. Futures Account"
                )
            
            with col2:
                # Ensure account size is a proper float
                try:
                    size_value = float(acc['size'])
                except (ValueError, TypeError):
                    size_value = 10000.0
                
                new_size = st.number_input(
                    "Account Size",
                    value=size_value,
                    min_value=100.0,
                    step=1000.0,
                    key=f"resize_{acc['id']}"
                )
            
            with col3:
                st.write("")
                st.write("")
                if st.button("💾 Save", key=f"save_{acc['id']}"):
                    # Update account
                    for a in accounts:
                        if a['id'] == acc['id']:
                            a['name'] = new_name
                            a['size'] = new_size
                            # Update all trades with this account
                            all_trades = load_trades()
                            for t in all_trades:
                                if t.get('account_id') == acc['id']:
                                    t['account_name'] = new_name
                            save_trades(all_trades)
                            break
                    save_accounts(accounts)
                    st.success(f"✅ Account updated!")
                    st.rerun()
            
            st.divider()
    
    # Manage existing accounts
    if len(accounts) > 1:
        with st.expander("⚙️ Delete Accounts"):
            for acc in accounts:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"{acc['name']} - {currency}{acc['size']:,.0f}")
                with col2:
                    if st.button("🗑️", key=f"del_acc_{acc['id']}", help="Delete account"):
                        # Check if account has trades
                        account_trades = [t for t in trades if t.get('account_id') == acc['id']]
                        if len(account_trades) > 0:
                            st.error(f"Kan niet Deleteen: {len(account_trades)} trades linked")
                        else:
                            accounts = [a for a in accounts if a['id'] != acc['id']]
                            save_accounts(accounts)
                            st.rerun()
    
    st.divider()
    
    # Clean slate option
    with st.expander("⚠️ Danger Zone"):
        st.warning("**Warning:** These actions are permanent!")
        
        if st.button("🗑️ Delete ALL trades from this account", type="secondary"):
            if 'confirm_delete_all' not in st.session_state:
                st.session_state['confirm_delete_all'] = True
                st.error("⚠️ Click again to confirm")
            elif st.session_state['confirm_delete_all']:
                # Delete all trades for this account
                all_trades = load_trades()
                all_trades = [t for t in all_trades if t.get('account_id') != selected_account['id']]
                # Reassign IDs
                for i, trade in enumerate(all_trades):
                    trade['id'] = i
                save_trades(all_trades)
                del st.session_state['confirm_delete_all']
                st.session_state['force_reload'] = True
                st.success("✅ All trades deleted!")
                st.rerun()
        
        if st.button("💥 RESET ALL (all trades + accounts)", type="secondary"):
            if 'confirm_reset_all' not in st.session_state:
                st.session_state['confirm_reset_all'] = True
                st.error("⚠️⚠️⚠️ Click again to wipe EVERYTHING!")
            elif st.session_state['confirm_reset_all']:
                # Reset everything
                save_trades([])
                save_accounts([{"name": "Main Account", "size": 10000, "id": 0}])
                del st.session_state['confirm_reset_all']
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.success("✅ Everything reset to default!")
                st.rerun()
    
    st.divider()
    
    # Export section in sidebar
    st.header("📥 Export")
    if len(trades) > 0:
        account_trades = [t for t in trades if t.get('account_id') == selected_account['id']]
        if len(account_trades) > 0:
            # Prepare export dataframe for current account
            export_df = pd.DataFrame(account_trades)
            if 'date' in export_df.columns:
                export_df['date'] = pd.to_datetime(export_df['date']).dt.strftime('%Y-%m-%d')
            
            # Select and reorder columns for export
            export_columns = [
                'date', 'symbol', 'side', 'entry_price', 'exit_price', 'quantity',
                'duration_minutes', 'setup', 'influence', 'trade_type', 'market_condition', 
                'mood', 'focus_level', 'stress_level', 'sleep_quality', 'pre_trade_confidence', 
                'notes', 'pnl', 'r_multiple'
            ]
            
            # Only include columns that exist
            export_columns = [col for col in export_columns if col in export_df.columns]
            export_df = export_df[export_columns]
            
            # Rename columns for better readability
            column_names = {
                'date': 'Date',
                'symbol': 'Symbol',
                'side': 'Side',
                'entry_price': 'Entry Price',
                'exit_price': 'Exit Price',
                'quantity': 'Quantity',
                'duration_minutes': 'Duration (Minutes)',
                'setup': 'Setup/Strategy',
                'influence': 'Influence/Reason',
                'trade_type': 'Trade Type',
                'market_condition': 'Market Condition',
                'mood': 'Mood',
                'focus_level': 'Focus Level',
                'stress_level': 'Stress Level',
                'sleep_quality': 'Sleep Quality',
                'pre_trade_confidence': 'Pre-Trade Confidence',
                'notes': 'Notes/Lessons',
                'pnl': 'PnL',
                'r_multiple': 'R-Multiple'
            }
            export_df = export_df.rename(columns=column_names)
            
            # Convert to CSV
            csv = export_df.to_csv(index=False)
            
            # Create filename with account name and date
            safe_account_name = selected_account['name'].replace(' ', '_')
            filename = f"{safe_account_name}_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            st.download_button(
                label=f"📥 Export {selected_account['name']}",
                data=csv,
                file_name=filename,
                mime="text/csv",
                help="Download all trades from this account as CSV",
                use_container_width=True
            )
            st.caption(f"{len(account_trades)} trades")
    
    st.divider()
    st.header("📊 Filters")

# PAGE 1: Add New Trade
if selected_page == "📝 Add Trade":
    st.header("Add New Trade")
    
    if is_mentor_mode:
        st.warning("🔒 **Read-Only Mode**")
        st.info("You are viewing this journal as a mentor. You cannot add new trades.")
        st.markdown("### 📊 Student's Recent Activity")
        
        if len(trades) > 0:
            # Get recent 10 trades
            recent_trades_data = sorted(trades, key=lambda x: x.get('date', ''), reverse=True)[:10]
            
            for trade in recent_trades_data:
                # Create detailed expander for each trade
                pnl_emoji = "🟢" if trade['pnl'] > 0 else "🔴"
                trade_title = f"{pnl_emoji} {trade['date']} - {trade['symbol']} {trade['side']} - {currency}{trade['pnl']:.2f} ({trade.get('r_multiple', 0):.2f}R)"
                
                with st.expander(trade_title, expanded=False):
                    # Trade details in columns
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("**📊 Trade Info:**")
                        st.text(f"Entry: {currency}{trade['entry_price']:.2f}")
                        st.text(f"Exit: {currency}{trade['exit_price']:.2f}")
                        st.text(f"Quantity: {trade['quantity']}")
                        st.text(f"Duration: {trade.get('duration_minutes', 0)} min")
                        st.text(f"Setup: {trade.get('setup', 'N/A')}")
                    
                    with col2:
                        st.markdown("**🧠 Psychology:**")
                        st.text(f"Mood: {trade.get('mood', 'N/A')}")
                        st.text(f"Confidence: {trade.get('pre_trade_confidence', 'N/A')}/5")
                        st.text(f"Focus: {trade.get('focus_level', 'N/A')}/5")
                        st.text(f"Stress: {trade.get('stress_level', 'N/A')}/5")
                        st.text(f"Sleep: {trade.get('sleep_quality', 'N/A')}/5")
                    
                    with col3:
                        st.markdown("**📌 Context:**")
                        st.text(f"Type: {trade.get('trade_type', 'N/A')}")
                        st.text(f"Market: {trade.get('market_condition', 'N/A')}")
                        if trade.get('influence'):
                            st.text(f"Influence: {trade.get('influence', 'N/A')}")
                        st.text(f"Account: {trade.get('account_name', 'N/A')}")
                    
                    # Notes section
                    if trade.get('notes'):
                        st.divider()
                        st.markdown(f"**💭 Notes/Lessons:**")
                        st.write(trade['notes'])
        else:
            st.info("No trades yet")
    else:
        with st.form("trade_form"):
            st.subheader("📊 Trade Details")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                trade_date = st.date_input("Date", value=datetime.today())
                trade_time = st.time_input("Time", value=datetime.now().time(), step=60, help="Tijd van entry (op de minuut)")
                symbol = st.text_input("Symbol/Pair", placeholder="e.g. MNQ, AAPL")
                side = st.selectbox("Side", ["Long", "Short"])
                trade_type = st.selectbox("Trade Type", ["Daytrade", "Swing", "Scalping", "Position"])
            
            with col2:
                entry_price = st.number_input("Entry Price", min_value=0.0, step=0.01, format="%.2f")
                exit_price = st.number_input("Exit Price", min_value=0.0, step=0.01, format="%.2f")
                quantity = st.number_input("Quantity", min_value=0.01, step=0.01, value=1.0, format="%.2f")
                duration_minutes = st.number_input("Trade Duration (minutes)", min_value=0, step=1, value=0, help="How long were you in this trade?")
                market_condition = st.selectbox("Market Condition", ["Trending", "Range", "Volatile", "News-driven"])
            
            with col3:
                setup = st.text_input("Setup", placeholder="e.g. Breakout, Bounce")
                influence = st.text_input("Influence/Reason", placeholder="Why did you take this trade?", 
                                         help="e.g. FOMO, Signal, Analysis, News")
                notes = st.text_area("Notes/Lessons", placeholder="What did you learn from this trade?", height=80)
            
            st.divider()
            st.subheader("🧠 Psychology & Performance")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                mood = st.selectbox("Mood", ["Calm", "Anxious", "Confident", "Excited", "Frustrated"])
                pre_trade_confidence = st.slider("Pre-Trade Confidence", 1, 5, 3)
            
            with col2:
                focus_level = st.slider("Focus Level", 1, 5, 3)
                stress_level = st.slider("Stress Level", 1, 5, 3)
            
            with col3:
                sleep_quality = st.slider("Sleep Quality", 1, 5, 3)
            
            with col4:
                st.caption("1 = Very low")
                st.caption("5 = Very high")
            
            submitted = st.form_submit_button("✅ Add Trade", use_container_width=True)
            
            if submitted:
                if symbol and entry_price > 0 and exit_price > 0:
                    pnl = calculate_pnl(entry_price, exit_price, quantity, side)
                    r_multiple = calculate_r_multiple(pnl, account_size)
                    
                    # Get next ID (across all trades, not just user's)
                    all_trades = load_trades()
                    next_id = max([t.get('id', 0) for t in all_trades], default=-1) + 1
                    
                    trade = {
                        'id': next_id,
                        'user_id': current_user['id'],
                        'account_id': selected_account['id'],
                        'account_name': selected_account['name'],
                        'date': trade_date.strftime('%Y-%m-%d'),
                        'time': trade_time.strftime('%H:%M:%S'),
                        'symbol': symbol.upper(),
                        'side': side,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'quantity': quantity,
                        'duration_minutes': duration_minutes,
                        'pnl': round(pnl, 2),
                        'r_multiple': round(r_multiple, 2),
                        'setup': setup,
                        'influence': influence,
                        'trade_type': trade_type,
                        'market_condition': market_condition,
                        'mood': mood,
                        'focus_level': focus_level,
                        'stress_level': stress_level,
                        'sleep_quality': sleep_quality,
                        'pre_trade_confidence': pre_trade_confidence,
                        'notes': notes
                    }
                    
                    trades.append(trade)
                    save_trades(trades)
                    st.success(f"✅ Trade added to {selected_account['name']}! PnL: {currency}{pnl:.2f}")
                    st.rerun()
                else:
                    st.error("⚠️ Fill in all required fields (Symbol, Entry Price, Exit Price)")

# PAGE: Mistakes Tracking
if selected_page == "❌ Mistakes":
    st.header("❌ Mistakes Tracker")
    st.markdown("Track en analyseer je trading mistakes om te leren en verbeteren.")
    
    if is_mentor_mode:
        st.warning("🔒 **Read-Only Mode** - Viewing student's mistakes")
    
    # Load mistakes for current user
    user_mistakes = load_mistakes(current_user['id'])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Recent Mistakes")
        
        if user_mistakes:
            # Sort by date and time (newest first)
            sorted_mistakes = sorted(user_mistakes, key=lambda x: (x['date'], x.get('time', '00:00:00')), reverse=True)
            
            for mistake in sorted_mistakes[:20]:  # Show last 20
                mistake_emoji = "🔴" if mistake.get('mistake_type') in ['Revenge Trading', 'FOMO', 'Overtrading'] else "⚠️"
                
                with st.expander(f"{mistake_emoji} {mistake['date']} {mistake.get('time', '')} - {mistake.get('mistake_type', 'Mistake')}"):
                    st.write(f"**Type:** {mistake.get('mistake_type', 'N/A')}")
                    st.write(f"**Beschrijving:** {mistake.get('description', 'N/A')}")
                    if mistake.get('trade_id'):
                        st.write(f"**Gekoppeld aan trade ID:** {mistake.get('trade_id')}")
                    
                    if not is_mentor_mode:
                        if st.button(f"🗑️ Verwijder", key=f"del_mistake_{mistake['id']}"):
                            all_mistakes = load_mistakes()
                            all_mistakes = [m for m in all_mistakes if m['id'] != mistake['id']]
                            save_mistakes(all_mistakes)
                            st.success("Mistake verwijderd!")
                            st.rerun()
        else:
            st.info("Nog geen mistakes geregistreerd. Blijf leren en verbeteren!")
    
    with col2:
        st.subheader("📊 Weekly Mistakes")
        
        if user_mistakes:
            # Get mistakes from last 7 days
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            weekly_mistakes = [
                m for m in user_mistakes 
                if datetime.strptime(m['date'], '%Y-%m-%d').date() >= week_ago
            ]
            
            st.metric("Deze Week", len(weekly_mistakes))
            
            # Count by type
            if weekly_mistakes:
                mistake_types = {}
                for m in weekly_mistakes:
                    mtype = m.get('mistake_type', 'Other')
                    mistake_types[mtype] = mistake_types.get(mtype, 0) + 1
                
                st.write("**Breakdown:**")
                for mtype, count in sorted(mistake_types.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"- {mtype}: {count}x")
        else:
            st.metric("Deze Week", 0)
        
        st.divider()
        
        # Monthly stats
        st.subheader("📅 Maandelijkse Trend")
        if user_mistakes:
            month_ago = today - timedelta(days=30)
            monthly_mistakes = [
                m for m in user_mistakes 
                if datetime.strptime(m['date'], '%Y-%m-%d').date() >= month_ago
            ]
            st.metric("Laatste 30 Dagen", len(monthly_mistakes))
        else:
            st.metric("Laatste 30 Dagen", 0)
    
    if not is_mentor_mode:
        st.divider()
        st.subheader("➕ Voeg Mistake Toe")
        
        with st.form("add_mistake_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                mistake_type = st.selectbox("Mistake Type", [
                    "Revenge Trading", "FOMO", "Overtrading", "No Stop Loss",
                    "Broke Rules", "Poor Entry", "Early Exit", "Late Exit",
                    "Emotional Trading", "Lack of Patience", "Other"
                ])
            
            with col2:
                # Option to link to a trade
                trade_options = ["Geen trade"] + [f"Trade {t['id']} - {t['symbol']} ({t['date']})" for t in trades]
                linked_trade = st.selectbox("Koppel aan trade (optioneel)", trade_options)
            
            description = st.text_area("Beschrijving", placeholder="Wat ging er mis? Wat kun je hiervan leren?")
            
            submit_mistake = st.form_submit_button("✅ Voeg Mistake Toe", use_container_width=True)
            
            if submit_mistake:
                if description:
                    trade_id = None
                    if linked_trade != "Geen trade":
                        # Extract trade ID from selection
                        trade_id = int(linked_trade.split()[1])
                    
                    add_mistake(
                        user_id=current_user['id'],
                        mistake_type=mistake_type,
                        description=description,
                        trade_id=trade_id
                    )
                    st.success("✅ Mistake toegevoegd!")
                    st.rerun()
                else:
                    st.error("Vul een beschrijving in")

# PAGE: Avoided Trades
if selected_page == "🛡️ Avoided Trades":
    st.header("🛡️ Avoided Trades Journal")
    st.markdown("Documenteer trades die je NIET hebt genomen - soms is niet traden de beste trade!")
    
    if is_mentor_mode:
        st.warning("🔒 **Read-Only Mode** - Viewing student's avoided trades")
    
    # Load avoided trades
    user_avoided = load_avoided_trades(current_user['id'])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Avoided Trades Log")
        
        if user_avoided:
            sorted_avoided = sorted(user_avoided, key=lambda x: (x['date'], x.get('time', '00:00:00')), reverse=True)
            
            for avoided in sorted_avoided:
                with st.expander(f"🛡️ {avoided['date']} {avoided.get('time', '')} - {avoided.get('symbol', 'N/A')}"):
                    st.write(f"**Symbol:** {avoided.get('symbol', 'N/A')}")
                    st.write(f"**Reden:** {avoided.get('reason', 'N/A')}")
                    st.write(f"**Potentiële Loss:** {currency}{avoided.get('potential_loss', 0):.2f}")
                    if avoided.get('notes'):
                        st.write(f"**Notities:** {avoided.get('notes')}")
                    
                    if not is_mentor_mode:
                        if st.button(f"🗑️ Verwijder", key=f"del_avoided_{avoided['id']}"):
                            all_avoided = load_avoided_trades()
                            all_avoided = [a for a in all_avoided if a['id'] != avoided['id']]
                            save_avoided_trades(all_avoided)
                            st.success("Avoided trade verwijderd!")
                            st.rerun()
        else:
            st.info("Nog geen avoided trades gedocumenteerd.")
    
    with col2:
        st.subheader("📊 Statistics")
        
        if user_avoided:
            # Weekly stats
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            weekly_avoided = [
                a for a in user_avoided 
                if datetime.strptime(a['date'], '%Y-%m-%d').date() >= week_ago
            ]
            
            st.metric("Deze Week", len(weekly_avoided))
            
            # Total potential loss saved
            total_saved = sum([a.get('potential_loss', 0) for a in user_avoided])
            st.metric("Totaal Bespaarde Loss", f"{currency}{total_saved:.2f}")
            
            # Top reasons
            if user_avoided:
                reasons = {}
                for a in user_avoided:
                    reason = a.get('reason', 'Other')
                    reasons[reason] = reasons.get(reason, 0) + 1
                
                st.write("**Top Redenen:**")
                for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
                    st.write(f"- {reason}: {count}x")
        else:
            st.metric("Deze Week", 0)
            st.metric("Totaal Bespaarde Loss", f"{currency}0.00")
    
    if not is_mentor_mode:
        st.divider()
        st.subheader("➕ Documenteer Avoided Trade")
        
        with st.form("add_avoided_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                symbol = st.text_input("Symbol", placeholder="e.g. MNQ, AAPL")
                reason = st.selectbox("Reden om niet te traden", [
                    "Setup was niet perfect", "Emotioneel niet ready", "Markt condities niet goed",
                    "Risk te hoog", "Tegen trading plan", "FOMO herkenning",
                    "News event", "Low confidence", "Already max positions", "Other"
                ])
            
            with col2:
                potential_loss = st.number_input("Potentiële Loss (indien getradet)", min_value=0.0, step=10.0, 
                                                help="Schatting van hoeveel je had kunnen verliezen")
                
            notes = st.text_area("Notities", placeholder="Waarom heb je deze trade vermeden? Wat was het signaal?")
            
            submit_avoided = st.form_submit_button("✅ Voeg Avoided Trade Toe", use_container_width=True)
            
            if submit_avoided:
                if symbol:
                    add_avoided_trade(
                        user_id=current_user['id'],
                        symbol=symbol.upper(),
                        reason=reason,
                        potential_loss=potential_loss,
                        notes=notes
                    )
                    st.success("✅ Avoided trade gedocumenteerd!")
                    st.rerun()
                else:
                    st.error("Vul minimaal een symbol in")

# PAGE: Pre-Trade Analysis
if selected_page == "📋 Pre-Trade Plan":
    st.header("📋 Pre-Trade Planning")
    st.markdown("Plan je trades vooraf - voorbereiding is de sleutel tot succes!")
    
    if is_mentor_mode:
        st.warning("🔒 **Read-Only Mode** - Viewing student's pre-trade plans")
    
    # Load pre-trade analysis
    user_pretrade = load_pretrade_analysis(current_user['id'])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 Pre-Trade Plans")
        
        if user_pretrade:
            sorted_pretrade = sorted(user_pretrade, key=lambda x: (x['date'], x.get('time', '00:00:00')), reverse=True)
            
            for plan in sorted_pretrade[:15]:
                status_emoji = "✅" if plan.get('executed') else "⏳"
                
                with st.expander(f"{status_emoji} {plan['date']} {plan.get('time', '')} - {plan.get('symbol', 'N/A')} {plan.get('direction', '')}"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write(f"**Symbol:** {plan.get('symbol', 'N/A')}")
                        st.write(f"**Direction:** {plan.get('direction', 'N/A')}")
                        st.write(f"**Entry Plan:** {plan.get('entry_plan', 'N/A')}")
                        st.write(f"**Stop Loss:** {plan.get('stop_loss', 'N/A')}")
                        st.write(f"**Take Profit:** {plan.get('take_profit', 'N/A')}")
                    
                    with col_b:
                        st.write(f"**Risk/Reward:** {plan.get('risk_reward', 'N/A')}")
                        st.write(f"**Confidence:** {plan.get('confidence', 0)}/10")
                        st.write(f"**Status:** {'Uitgevoerd' if plan.get('executed') else 'Nog niet uitgevoerd'}")
                        if plan.get('trade_id'):
                            st.write(f"**Trade ID:** {plan.get('trade_id')}")
                    
                    if plan.get('checklist'):
                        st.divider()
                        st.write(f"**Checklist:** {plan.get('checklist')}")
                    
                    if not is_mentor_mode:
                        col_x, col_y = st.columns(2)
                        with col_x:
                            if not plan.get('executed') and st.button(f"✅ Mark Executed", key=f"exec_{plan['id']}"):
                                all_pretrade = load_pretrade_analysis()
                                for p in all_pretrade:
                                    if p['id'] == plan['id']:
                                        p['executed'] = True
                                save_pretrade_analysis(all_pretrade)
                                st.success("Gemarkeerd als uitgevoerd!")
                                st.rerun()
                        
                        with col_y:
                            if st.button(f"🗑️ Verwijder", key=f"del_pretrade_{plan['id']}"):
                                all_pretrade = load_pretrade_analysis()
                                all_pretrade = [p for p in all_pretrade if p['id'] != plan['id']]
                                save_pretrade_analysis(all_pretrade)
                                st.success("Plan verwijderd!")
                                st.rerun()
        else:
            st.info("Nog geen pre-trade plans gemaakt.")
    
    with col2:
        st.subheader("📊 Statistics")
        
        if user_pretrade:
            executed_count = len([p for p in user_pretrade if p.get('executed')])
            pending_count = len([p for p in user_pretrade if not p.get('executed')])
            
            st.metric("Totaal Plans", len(user_pretrade))
            st.metric("Uitgevoerd", executed_count)
            st.metric("Pending", pending_count)
            
            if len(user_pretrade) > 0:
                execution_rate = (executed_count / len(user_pretrade)) * 100
                st.metric("Execution Rate", f"{execution_rate:.1f}%")
        else:
            st.metric("Totaal Plans", 0)
    
    if not is_mentor_mode:
        st.divider()
        st.subheader("➕ Nieuw Pre-Trade Plan")
        
        with st.form("add_pretrade_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                symbol = st.text_input("Symbol", placeholder="e.g. MNQ, AAPL")
                direction = st.selectbox("Direction", ["Long", "Short"])
                entry_plan = st.text_input("Entry Plan", placeholder="e.g. Break above 20000")
            
            with col2:
                stop_loss = st.text_input("Stop Loss", placeholder="e.g. 19950")
                take_profit = st.text_input("Take Profit", placeholder="e.g. 20100")
                risk_reward = st.text_input("Risk/Reward", placeholder="e.g. 1:2")
            
            with col3:
                confidence = st.slider("Confidence Level", 1, 10, 5)
            
            checklist = st.text_area("Pre-Trade Checklist", 
                                    placeholder="✓ Setup confirmed\n✓ Risk defined\n✓ Emotionally ready\n✓ Market conditions good",
                                    height=100)
            
            submit_pretrade = st.form_submit_button("✅ Save Pre-Trade Plan", use_container_width=True)
            
            if submit_pretrade:
                if symbol and entry_plan:
                    add_pretrade_analysis(
                        user_id=current_user['id'],
                        symbol=symbol.upper(),
                        direction=direction,
                        entry_plan=entry_plan,
                        stop_loss=stop_loss,
                        take_profit=take_profit,
                        risk_reward=risk_reward,
                        confidence=confidence,
                        checklist=checklist
                    )
                    st.success("✅ Pre-trade plan opgeslagen!")
                    st.rerun()
                else:
                    st.error("Vul minimaal symbol en entry plan in")

# PAGE: Admin Quotes Management
if selected_page == "💬 Admin Quotes":
    st.header("💬 Quotes Management")
    
    # Check if user is admin (by username or ID)
    is_admin = current_user['username'] == 'admin' or current_user.get('id') == 0
    
    if is_admin:
        st.markdown("Beheer inspirerende quotes die voor alle gebruikers zichtbaar zijn.")
        
        # Load quotes
        all_quotes = load_quotes()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📝 Alle Quotes")
            
            if all_quotes:
                for quote in all_quotes:
                    status = "🟢 Active" if quote.get('active', True) else "🔴 Inactive"
                    
                    with st.expander(f"{status} - {quote['text'][:50]}..."):
                        st.write(f"**Quote:** {quote['text']}")
                        st.write(f"**Author:** {quote.get('author', 'Unknown')}")
                        st.write(f"**Created:** {quote.get('created_at', 'N/A')}")
                        
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            if quote.get('active', True):
                                if st.button(f"❌ Deactivate", key=f"deact_{quote['id']}"):
                                    for q in all_quotes:
                                        if q['id'] == quote['id']:
                                            q['active'] = False
                                    save_quotes(all_quotes)
                                    st.success("Quote gedeactiveerd!")
                                    st.rerun()
                            else:
                                if st.button(f"✅ Activate", key=f"act_{quote['id']}"):
                                    for q in all_quotes:
                                        if q['id'] == quote['id']:
                                            q['active'] = True
                                    save_quotes(all_quotes)
                                    st.success("Quote geactiveerd!")
                                    st.rerun()
                        
                        with col_b:
                            if st.button(f"🗑️ Delete", key=f"del_quote_{quote['id']}"):
                                all_quotes = [q for q in all_quotes if q['id'] != quote['id']]
                                save_quotes(all_quotes)
                                st.success("Quote verwijderd!")
                                st.rerun()
            else:
                st.info("Nog geen quotes toegevoegd.")
        
        with col2:
            st.subheader("📊 Statistics")
            st.metric("Totaal Quotes", len(all_quotes))
            active_quotes = len([q for q in all_quotes if q.get('active', True)])
            st.metric("Active Quotes", active_quotes)
        
        st.divider()
        st.subheader("➕ Nieuwe Quote Toevoegen")
        
        with st.form("add_quote_form"):
            quote_text = st.text_area("Quote Text", placeholder="Enter an inspiring trading quote...", height=100)
            author = st.text_input("Author", placeholder="e.g. Jesse Livermore, Mark Douglas")
            
            submit_quote = st.form_submit_button("✅ Add Quote", use_container_width=True)
            
            if submit_quote:
                if quote_text:
                    add_quote(text=quote_text, author=author)
                    st.success("✅ Quote toegevoegd!")
                    st.rerun()
                else:
                    st.error("Vul een quote in")
    else:
        st.info("🔒 Deze sectie is alleen toegankelijk voor admins")
        
        st.divider()
        st.subheader("💡 Current Quotes")
        st.markdown("Dit zijn de quotes die je kunt zien in de header:")
        
        all_quotes = load_quotes()
        active_quotes = [q for q in all_quotes if q.get('active', True)]
        
        if active_quotes:
            for quote in active_quotes:
                st.markdown(f"""
                <div style='background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; margin: 10px 0;
                            border-left: 3px solid #00ff88;'>
                    <p style='font-style: italic; margin: 0;'>"{quote['text']}"</p>
                    <p style='text-align: right; margin-top: 5px; color: #00ff88;'>— {quote.get('author', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nog geen actieve quotes.")

# Display trades if any exist
if trades:
    # Filter trades by selected account
    account_trades = [t for t in trades if t.get('account_id') == selected_account['id']]
    
    if not account_trades:
        st.info(f"No trades found for account: {selected_account['name']}")
        st.stop()
    
    df = pd.DataFrame(account_trades)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date', ascending=False)
    
    # Calculate cumulative profit for Equity Curve
    df_sorted = df.sort_values('date')
    df_sorted['cumulative_pnl'] = df_sorted['pnl'].cumsum()
    
    # Get unique symbols for filtering
    all_symbols = sorted(df['symbol'].unique().tolist())
    
    # PAGE: All trades
    if selected_page == "📊 All Trades":
        st.header("📊 All Trades Overview")
        
        # Export options
        with st.expander("📥 Export Opties", expanded=False):
            export_col1, export_col2 = st.columns(2)
            
            with export_col1:
                st.subheader("📋 Export trades")
                
                # Standard export
                if len(df) > 0:
                    # Prepare export dataframe
                    export_df = df.copy()
                    export_df['date'] = export_df['date'].dt.strftime('%Y-%m-%d')
                    
                    # Select and reorder columns for export
                    export_columns = [
                        'date', 'symbol', 'side', 'entry_price', 'exit_price', 'quantity',
                        'duration_minutes', 'setup', 'influence', 'trade_type', 'market_condition', 
                        'mood', 'focus_level', 'stress_level', 'sleep_quality', 'pre_trade_confidence', 
                        'notes', 'pnl', 'r_multiple', 'account_name'
                    ]
                    
                    # Only include columns that exist
                    export_columns = [col for col in export_columns if col in export_df.columns]
                    export_df_full = export_df[export_columns].copy()
                    
                    # Rename columns for better readability
                    column_names = {
                        'date': 'Date',
                        'symbol': 'Symbol',
                        'side': 'Side',
                        'entry_price': 'Entry Price',
                        'exit_price': 'Exit Price',
                        'quantity': 'Quantity',
                        'duration_minutes': 'Duration (Minutes)',
                        'setup': 'Setup/Strategy',
                        'influence': 'Influence/Reason',
                        'trade_type': 'Trade Type',
                        'market_condition': 'Market Condition',
                        'mood': 'Mood',
                        'focus_level': 'Focus Level',
                        'stress_level': 'Stress Level',
                        'sleep_quality': 'Sleep Quality',
                        'pre_trade_confidence': 'Pre-Trade Confidence',
                        'notes': 'Notes/Lessons',
                        'pnl': 'PnL',
                        'r_multiple': 'R-Multiple',
                        'account_name': 'Account'
                    }
                    export_df_full = export_df_full.rename(columns=column_names)
                    
                    # Convert to CSV
                    csv_all = export_df_full.to_csv(index=False)
                    filename_all = f"all_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    
                    st.download_button(
                        label="📥 Export All trades",
                        data=csv_all,
                        file_name=filename_all,
                        mime="text/csv",
                        help="Download all trades as CSV",
                        use_container_width=True
                    )
                    
                    st.divider()
                    
                    # Filtered export by Setup/Mood
                    st.subheader("🔍 Export Filtered")
                    
                    filter_col1, filter_col2 = st.columns(2)
                    
                    with filter_col1:
                        # Get unique setups and moods
                        unique_setups = df['setup'].unique().tolist() if 'setup' in df.columns else []
                        if unique_setups:
                            selected_setups = st.multiselect(
                                "Filter by Setup",
                                unique_setups,
                                default=unique_setups,
                                key="export_setup_filter"
                            )
                    
                    with filter_col2:
                        unique_moods = df['mood'].unique().tolist() if 'mood' in df.columns else []
                        if unique_moods:
                            selected_moods = st.multiselect(
                                "Filter by Mood",
                                unique_moods,
                                default=unique_moods,
                                key="export_mood_filter"
                            )
                    
                    # Apply filters
                    filtered_export_df = export_df.copy()
                    if 'setup' in filtered_export_df.columns and unique_setups:
                        filtered_export_df = filtered_export_df[filtered_export_df['setup'].isin(selected_setups)]
                    if 'mood' in filtered_export_df.columns and unique_moods:
                        filtered_export_df = filtered_export_df[filtered_export_df['mood'].isin(selected_moods)]
                    
                    if len(filtered_export_df) > 0:
                        filtered_export_df = filtered_export_df[export_columns].copy()
                        filtered_export_df = filtered_export_df.rename(columns=column_names)
                        csv_filtered = filtered_export_df.to_csv(index=False)
                        
                        filter_label = []
                        if unique_setups and len(selected_setups) < len(unique_setups):
                            filter_label.append(f"{len(selected_setups)} setups")
                        if unique_moods and len(selected_moods) < len(unique_moods):
                            filter_label.append(f"{len(selected_moods)} moods")
                        
                        button_label = f"📥 Export Filtered ({len(filtered_export_df)} trades)"
                        filename_filtered = f"filtered_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        
                        st.download_button(
                            label=button_label,
                            data=csv_filtered,
                            file_name=filename_filtered,
                            mime="text/csv",
                            help="Download gefilterde trades",
                            use_container_width=True
                        )
                    else:
                        st.info("No trades with these filters")
            
            with export_col2:
                st.subheader("📊 Export Monthelijkse Stats")
                
                if len(df) > 0:
                    # Create monthly summary
                    df_monthly = df.copy()
                    df_monthly['year_month'] = df_monthly['date'].dt.to_period('M')
                    
                    monthly_summary = df_monthly.groupby('year_month').agg({
                        'pnl': ['sum', 'mean', 'count'],
                        'r_multiple': 'mean'
                    }).round(2)
                    
                    # Calculate Win Rate per month
                    win_rates = []
                    winning_trades = []
                    losing_trades = []
                    
                    for period in monthly_summary.index:
                        month_trades = df_monthly[df_monthly['year_month'] == period]
                        wins = len(month_trades[month_trades['pnl'] > 0])
                        losses = len(month_trades[month_trades['pnl'] < 0])
                        total = len(month_trades)
                        win_rate = (wins / total * 100) if total > 0 else 0
                        win_rates.append(win_rate)
                        winning_trades.append(wins)
                        losing_trades.append(losses)
                    
                    # Flatten multi-level columns
                    monthly_summary.columns = ['Total_PnL', 'Avg_PnL_Per_Trade', 'Total_trades', 'Avg_R_Multiple']
                    monthly_summary['Win_Rate_%'] = win_rates
                    monthly_summary['Winning_trades'] = winning_trades
                    monthly_summary['Losing_trades'] = losing_trades
                    
                    # Reset index to make year_month a column
                    monthly_summary = monthly_summary.reset_index()
                    monthly_summary['Year_Month'] = monthly_summary['year_month'].astype(str)
                    monthly_summary = monthly_summary.drop('year_month', axis=1)
                    
                    # Reorder columns
                    monthly_summary = monthly_summary[[
                        'Year_Month', 'Total_trades', 'Winning_trades', 'Losing_trades',
                        'Win_Rate_%', 'Total_PnL', 'Avg_PnL_Per_Trade', 'Avg_R_Multiple'
                    ]]
                    
                    # Display preview
                    st.dataframe(monthly_summary, use_container_width=True, hide_index=True)
                    
                    # Convert to CSV
                    csv_monthly = monthly_summary.to_csv(index=False)
                    filename_monthly = f"monthly_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    
                    st.download_button(
                        label="📥 Export Monthly Summary",
                        data=csv_monthly,
                        file_name=filename_monthly,
                        mime="text/csv",
                        help="Download Monthelijkse statistieken for journaling",
                        use_container_width=True
                    )
                    
                    st.caption(f"📅 {len(monthly_summary)} Monthen data")
        
        st.divider()
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_symbol = st.multiselect("Filter Symbol", all_symbols, default=all_symbols)
        with col2:
            filter_side = st.multiselect("Filter Side", ["Long", "Short"], default=["Long", "Short"])
        with col3:
            date_range = st.date_input("Date Range", value=(df['date'].min(), df['date'].max()), key="date_range")
        
        # Apply filters
        # Handle date_range (can be single date or tuple)
        if isinstance(date_range, tuple) and len(date_range) == 2:
            date_filter = (df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))
        elif isinstance(date_range, tuple) and len(date_range) == 1:
            date_filter = df['date'] >= pd.to_datetime(date_range[0])
        else:
            date_filter = df['date'] >= pd.to_datetime(date_range)
        
        filtered_df = df[
            (df['symbol'].isin(filter_symbol)) &
            (df['side'].isin(filter_side)) &
            date_filter
        ].copy()
        
        # Display metrics
        metrics = calculate_metrics(filtered_df)
        
        st.subheader("📊 Performance Metrics")
        
        # Create organized metrics in 4 columns x 3 rows
        # Row 1: Main Performance
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            profit_delta = "🟢" if metrics['total_profit'] >= 0 else "🔴"
            st.metric("💰 Total Profit", f"{currency}{metrics['total_profit']:.2f}")
        with col2:
            st.metric("📈 Total Trades", metrics['total_trades'])
        with col3:
            st.metric("📊 Win Rate", f"{metrics['win_rate']:.1f}%")
        with col4:
            st.metric("🎯 Expectancy", f"{currency}{metrics['Expectancy']:.2f}")
        
        # Row 2: Win/Loss Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("✅ Winning Trades", metrics['winning_trades'])
        with col2:
            st.metric("❌ Losing Trades", metrics['losing_trades'])
        with col3:
            st.metric("💚 Avg Win", f"{currency}{metrics['avg_win']:.2f}")
        with col4:
            st.metric("❤️ Avg Loss", f"{currency}{metrics['avg_loss']:.2f}")
        
        # Row 3: Advanced Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Profit Factor", f"{metrics['profit_factor']:.2f}")
        with col2:
            st.metric("⚡ Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
        with col3:
            st.metric("📉 Max Drawdown", f"{currency}{metrics['max_drawdown']:.2f}")
        with col4:
            st.metric("📉 Max DD %", f"{metrics['max_drawdown_pct']:.1f}%")
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Equity Curve")
            if len(filtered_df) > 0:
                fig, ax = plt.subplots(figsize=(10, 5))
                df_chart = filtered_df.sort_values('date').copy()
                df_chart['cumulative_pnl'] = df_chart['pnl'].cumsum()
                ax.plot(df_chart['date'], df_chart['cumulative_pnl'], marker='o', linewidth=2, 
                       markersize=6, color='#00ff88', markerfacecolor='#00ff88')
                ax.axhline(y=0, color='red', linestyle='--', alpha=0.5, linewidth=1)
                ax.fill_between(df_chart['date'], df_chart['cumulative_pnl'], 0, alpha=0.2, color='#00ff88')
                ax.set_xlabel('Date', fontsize=12)
                ax.set_ylabel('Cumulatieve P&L ($)', fontsize=12)
                ax.set_title('Equity Curve', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3, linestyle='--')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No data to display")
        
        with col2:
            st.subheader("💼 Profit by Symbol")
            if len(filtered_df) > 0:
                try:
                    # Ensure pnl column exists and is numeric
                    if 'pnl' not in filtered_df.columns:
                        st.warning("P&L data not available")
                    else:
                        # Convert pnl to numeric, handling any non-numeric values
                        filtered_df['pnl'] = pd.to_numeric(filtered_df['pnl'], errors='coerce')
                        
                        # Remove any rows with NaN pnl values
                        valid_df = filtered_df.dropna(subset=['pnl'])
                        
                        if len(valid_df) > 0:
                            profit_by_symbol = valid_df.groupby('symbol')['pnl'].sum().sort_values(ascending=False)
                            
                            if len(profit_by_symbol) > 0:
                                fig, ax = plt.subplots(figsize=(10, 5))
                                if safe_plot(profit_by_symbol, 'Profit/Loss by Symbol', 'Symbol', 'Total P&L ($)', ax):
                                    st.pyplot(fig)
                                else:
                                    st.info("No valid symbol data to display")
                            else:
                                st.info("No valid symbol data to display")
                        else:
                            st.info("No valid P&L data to display")
                except Exception as e:
                    st.error(f"Error creating chart: {str(e)}")
                    st.info("Displaying data table instead:")
                    st.dataframe(filtered_df[['symbol', 'pnl', 'date']].head(10))
            else:
                st.info("No data to display")
        
        st.divider()
        
        # New charts row: Drawdown and Monthly Performance
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📉 Drawdown Chart")
            if len(filtered_df) > 0:
                fig, ax = plt.subplots(figsize=(10, 5))
                df_chart = filtered_df.sort_values('date').copy()
                df_chart['cumulative_pnl'] = df_chart['pnl'].cumsum()
                df_chart['running_max'] = df_chart['cumulative_pnl'].cummax()
                df_chart['drawdown'] = df_chart['cumulative_pnl'] - df_chart['running_max']
                
                ax.fill_between(df_chart['date'], df_chart['drawdown'], 0, 
                               color='#ff4444', alpha=0.3, label='Drawdown')
                ax.plot(df_chart['date'], df_chart['drawdown'], 
                       color='#ff4444', linewidth=2)
                ax.axhline(y=0, color='white', linestyle='--', alpha=0.5, linewidth=1)
                ax.set_xlabel('Date', fontsize=12)
                ax.set_ylabel('Drawdown ($)', fontsize=12)
                ax.set_title('Underwater Equity Curve', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3, linestyle='--')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No data to display")
        
        with col2:
            st.subheader("📊 Monthly Performance")
            if len(filtered_df) > 0:
                df_monthly = filtered_df.copy()
                df_monthly['year_month'] = df_monthly['date'].dt.to_period('M').astype(str)
                monthly_pnl = df_monthly.groupby('year_month')['pnl'].sum().sort_index()
                
                fig, ax = plt.subplots(figsize=(10, 5))
                colors = ['#00ff88' if x > 0 else '#ff4444' for x in monthly_pnl.values]
                monthly_pnl.plot(kind='bar', ax=ax, color=colors, edgecolor='white', linewidth=1.5)
                ax.axhline(y=0, color='white', linewidth=1)
                ax.set_xlabel('Month', fontsize=12)
                ax.set_ylabel('P&L ($)', fontsize=12)
                ax.set_title('Monthly Performance', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y', linestyle='--')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No data to display")
        
        st.divider()
        
        # Day of Week Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Best Day of Week")
            if len(filtered_df) > 0:
                df_dow = filtered_df.copy()
                df_dow['day_of_week'] = df_dow['date'].dt.day_name()
                
                # Order days correctly
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                dow_stats = df_dow.groupby('day_of_week').agg({
                    'pnl': ['sum', 'mean', 'count']
                }).round(2)
                dow_stats.columns = ['Total P&L', 'Avg P&L', 'Trades']
                
                # Reindex to correct order
                dow_stats = dow_stats.reindex([d for d in day_order if d in dow_stats.index])
                
                fig, ax = plt.subplots(figsize=(10, 5))
                colors = ['#00ff88' if x > 0 else '#ff4444' for x in dow_stats['Total P&L']]
                dow_stats['Total P&L'].plot(kind='bar', ax=ax, color=colors, 
                                           edgecolor='white', linewidth=1.5)
                ax.axhline(y=0, color='white', linewidth=1)
                ax.set_xlabel('Day of Week', fontsize=12)
                ax.set_ylabel('Total P&L ($)', fontsize=12)
                ax.set_title('Performance by Day of Week', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y', linestyle='--')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                
                # Show best day
                best_day = dow_stats['Total P&L'].idxmax()
                best_day_pnl = dow_stats.loc[best_day, 'Total P&L']
                st.success(f"🏆 Best Day: **{best_day}** ({currency}{best_day_pnl:.2f})")
            else:
                st.info("No data to display")
        
        with col2:
            st.subheader("📊 Day of Week Stats")
            if len(filtered_df) > 0:
                st.dataframe(dow_stats, use_container_width=True)
                
                st.caption("💡 **Insights:**")
                # Find worst day
                worst_day = dow_stats['Total P&L'].idxmin()
                worst_day_pnl = dow_stats.loc[worst_day, 'Total P&L']
                
                st.info(f"📉 Worst Day: **{worst_day}** ({currency}{worst_day_pnl:.2f})")
                
                # Most active day
                most_active = dow_stats['Trades'].idxmax()
                most_active_count = dow_stats.loc[most_active, 'Trades']
                st.info(f"📈 Most Active: **{most_active}** ({int(most_active_count)} trades)")
            else:
                st.info("No data to display")
        
        st.divider()
        st.subheader("📋 Trade Details")
        
        if len(filtered_df) == 0:
            st.info("No trades gevonden met de huidige filters")
        
        # Display trades with delete button
        for idx, row in filtered_df.iterrows():
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1.5, 1.5, 1, 1.5, 1.5, 1, 2, 1.5, 2.5, 1])
            
            with col1:
                st.text(row['date'].strftime('%Y-%m-%d'))
            with col2:
                st.text(f"**{row['symbol']}**")
            with col3:
                st.text(row['side'])
            with col4:
                st.text(f"${row['entry_price']:.2f}")
            with col5:
                st.text(f"${row['exit_price']:.2f}")
            with col6:
                st.text(str(row['quantity']))
            with col7:
                pnl_color = "🟢" if row['pnl'] > 0 else "🔴"
                st.markdown(f"{pnl_color} **${row['pnl']:.2f}**")
            with col8:
                st.text(f"{row['r_multiple']:.2f}R")
            with col9:
                st.text(row['setup'][:20] + "..." if len(row['setup']) > 20 else row['setup'])
            with col10:
                if st.button("🗑️", key=f"del_{row['id']}", help="Delete this trade"):
                    if delete_trade(row['id']):
                        # Force fresh data load
                        st.session_state['force_reload'] = True
                        st.success(f"Trade {row['id']} Deleted!")
                        st.rerun()
    
    # PAGE: Calendar View
    if selected_page == "📅 Calendar":
        st.header("📅 Calendar Overview")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Date selector
            available_dates = df['date'].dt.to_period('M').unique()
            current_month = datetime.now()
            
            selected_year = st.selectbox("Year", sorted(df['date'].dt.year.unique(), reverse=True))
            selected_month = st.selectbox("Month", range(1, 13), 
                                         format_func=lambda x: cal.month_name[x],
                                         index=current_month.month - 1)
            
            st.divider()
            
            # Symbol filter for calendar
            st.subheader("Filter by Symbol")
            calendar_symbols = st.multiselect(
                "Select Symbols",
                all_symbols,
                default=all_symbols,
                key="calendar_symbols"
            )
        
        with col2:
            # Filter dataframe by selected symbols
            calendar_df = df[df['symbol'].isin(calendar_symbols)] if calendar_symbols else df
            
            # Create calendar
            daily_stats = create_calendar_view(calendar_df, selected_year, selected_month)
            
            if daily_stats is not None and len(daily_stats) > 0:
                # Get calendar matrix
                month_cal = cal.monthcalendar(selected_year, selected_month)
                
                st.subheader(f"{cal.month_name[selected_month]} {selected_year}")
                
                # Create calendar grid
                days = ['Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za', 'Zo']
                cols = st.columns(7)
                for i, day in enumerate(days):
                    cols[i].markdown(f"**{day}**")
                
                for week in month_cal:
                    cols = st.columns(7)
                    for i, day in enumerate(week):
                        if day == 0:
                            cols[i].text("")
                        else:
                            day_date = datetime(selected_year, selected_month, day).date()
                            day_data = daily_stats[daily_stats['date'] == day_date]
                            
                            if len(day_data) > 0:
                                pnl = day_data.iloc[0]['pnl']
                                num_trades = int(day_data.iloc[0]['num_trades'])
                                
                                if pnl > 0:
                                    cols[i].markdown(f"""
                                    <div style='background-color: #00ff0030; padding: 10px; border-radius: 5px; border: 2px solid #00ff00;'>
                                        <div style='font-weight: bold; font-size: 20px;'>{day}</div>
                                        <div style='color: #00ff00; font-size: 16px; font-weight: bold;'>{currency}{pnl:.0f}</div>
                                        <div style='font-size: 11px;'>{num_trades} trades</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    cols[i].markdown(f"""
                                    <div style='background-color: #ff000030; padding: 10px; border-radius: 5px; border: 2px solid #ff4444;'>
                                        <div style='font-weight: bold; font-size: 20px;'>{day}</div>
                                        <div style='color: #ff4444; font-size: 16px; font-weight: bold;'>{currency}{pnl:.0f}</div>
                                        <div style='font-size: 11px;'>{num_trades} trades</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                cols[i].markdown(f"""
                                <div style='background-color: #1e1e1e; padding: 10px; border-radius: 5px;'>
                                    <div style='font-size: 18px; color: #666;'>{day}</div>
                                </div>
                                """, unsafe_allow_html=True)
                
                st.divider()
                
                # Daily summary
                st.subheader("📊 Daily Summary")
                if calendar_symbols:
                    st.caption(f"Filtered by: {', '.join(calendar_symbols)}")
                daily_summary = daily_stats.copy()
                daily_summary['date'] = pd.to_datetime(daily_summary['date']).dt.strftime('%Y-%m-%d (%A)')
                daily_summary['pnl'] = daily_summary['pnl'].apply(lambda x: f"{currency}{x:.2f}")
                daily_summary.columns = ['Date', 'P&L', 'Number of trades']
                st.dataframe(daily_summary, use_container_width=True, hide_index=True)
            else:
                st.info("No trades in this month" + (f" for {', '.join(calendar_symbols)}" if calendar_symbols else ""))
    
    # PAGE: Per Symbol Analysis
    if selected_page == "💰 Per Symbol":
        st.header("💰 Analysis Per Symbol")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # Symbol selector
            selected_symbol = st.selectbox("Select Symbol", all_symbols)
        with col2:
            st.write("")
            st.write("")
            if st.button("🗑️ Delete all trades for this symbol", type="secondary"):
                if 'confirm_delete_symbol' not in st.session_state:
                    st.session_state['confirm_delete_symbol'] = selected_symbol
                    st.warning(f"⚠️ Click again to delete ALL {selected_symbol} trades")
                elif st.session_state['confirm_delete_symbol'] == selected_symbol:
                    # Delete all trades for this symbol
                    all_trades = load_trades()
                    all_trades = [t for t in all_trades if t.get('symbol') != selected_symbol]
                    # Reassign IDs
                    for i, trade in enumerate(all_trades):
                        trade['id'] = i
                    save_trades(all_trades)
                    del st.session_state['confirm_delete_symbol']
                    st.session_state['force_reload'] = True
                    st.success(f"✅ All {selected_symbol} trades deleted!")
                    st.rerun()
                else:
                    st.session_state['confirm_delete_symbol'] = selected_symbol
                    st.warning(f"⚠️ Click again to delete ALL {selected_symbol} trades")
        
        symbol_df = df[df['symbol'] == selected_symbol].copy()
        
        if len(symbol_df) > 0:
            metrics = calculate_metrics(symbol_df)
            
            # Metrics for this symbol
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Total Profit", f"${metrics['total_profit']:.2f}")
            with col2:
                st.metric("📊 Win Rate", f"{metrics['win_rate']:.1f}%")
            with col3:
                st.metric("📈 Total trades", metrics['total_trades'])
            with col4:
                st.metric("🎯 Expectancy", f"${metrics['Expectancy']:.2f}")
            
            st.divider()
            
            # Equity Curve for this symbol
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"📈 Equity Curve - {selected_symbol}")
                fig, ax = plt.subplots(figsize=(10, 5))
                symbol_sorted = symbol_df.sort_values('date')
                symbol_sorted['cumulative_pnl'] = symbol_sorted['pnl'].cumsum()
                ax.plot(symbol_sorted['date'], symbol_sorted['cumulative_pnl'], 
                       marker='o', linewidth=2, markersize=6, color='#00ff88')
                ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
                ax.fill_between(symbol_sorted['date'], symbol_sorted['cumulative_pnl'], 0, 
                               alpha=0.2, color='#00ff88')
                ax.set_xlabel('Date')
                ax.set_ylabel('Cumulatieve P&L ($)')
                ax.set_title(f'Equity Curve - {selected_symbol}')
                ax.grid(True, alpha=0.3)
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            
            with col2:
                st.subheader(f"📊 Win/Loss Distribution - {selected_symbol}")
                fig, ax = plt.subplots(figsize=(10, 5))
                win_loss = [metrics['winning_trades'], metrics['losing_trades']]
                colors_pie = ['#00ff88', '#ff4444']
                ax.pie(win_loss, labels=['Wins', 'Losses'], colors=colors_pie, 
                      autopct='%1.1f%%', startangle=90)
                ax.set_title(f'Win/Loss Ratio - {selected_symbol}')
                st.pyplot(fig)
            
            st.divider()
            
            # Trade history for this symbol
            st.subheader(f"📋 Trade History - {selected_symbol}")
            symbol_display = symbol_df.copy()
            symbol_display = symbol_display.sort_values('date', ascending=False)
            
            for idx, row in symbol_display.iterrows():
                col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1.5, 1, 1.5, 1.5, 1, 2, 1.5, 2.5, 1])
                
                with col1:
                    st.text(row['date'].strftime('%Y-%m-%d'))
                with col2:
                    st.text(row['side'])
                with col3:
                    st.text(f"${row['entry_price']:.2f}")
                with col4:
                    st.text(f"${row['exit_price']:.2f}")
                with col5:
                    st.text(str(row['quantity']))
                with col6:
                    pnl_color = "🟢" if row['pnl'] > 0 else "🔴"
                    st.markdown(f"{pnl_color} **${row['pnl']:.2f}**")
                with col7:
                    st.text(f"{row['r_multiple']:.2f}R")
                with col8:
                    st.text(row['setup'])
                with col9:
                    if st.button("🗑️", key=f"del_sym_{row['id']}", help="Delete"):
                        if delete_trade(row['id']):
                            # Force fresh data load
                            st.session_state['force_reload'] = True
                            st.success(f"Trade {row['id']} Deleted!")
                            st.rerun()
        else:
            st.info(f"No trades found for {selected_symbol}")

    # PAGE: Weekly Price Action Calendar
    if selected_page == "📈 Weekly Price Action":
        if PRICE_ACTION_AVAILABLE:
            display_weekly_price_action_calendar()
        else:
            st.header("📈 Weekly Price Action Calendar")
            st.error("❌ Price Action Calendar module not available")
            st.info("💡 This feature requires additional dependencies. Please install them:")
            st.code("pip install yfinance plotly", language="bash")
            st.info("🔄 After installation, restart the application to use this feature.")

    # PAGE: Psychology Analysis
    if selected_page == "🧠 Psychology":
        st.header("🧠 Psychological Analysis")
        
        st.info("💡 Discover how your mental state affects your trading performance")
        
        # Check if psychological data exists
        if 'mood' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Performance by Mood")
                mood_stats = df.groupby('mood').agg({
                    'pnl': ['sum', 'mean', 'count']
                }).round(2)
                mood_stats.columns = ['Total P&L', 'Avg P&L', 'Number of trades']
                mood_stats = mood_stats.sort_values('Total P&L', ascending=False)
                
                # Create bar chart for mood
                fig, ax = plt.subplots(figsize=(10, 5))
                colors = ['#00ff88' if x > 0 else '#ff4444' for x in mood_stats['Total P&L']]
                mood_stats['Total P&L'].plot(kind='bar', ax=ax, color=colors, edgecolor='white', linewidth=1.5)
                ax.axhline(y=0, color='white', linewidth=1)
                ax.set_xlabel('Mood', fontsize=12)
                ax.set_ylabel('Total P&L ($)', fontsize=12)
                ax.set_title('Profitability per Mood', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                
                st.dataframe(mood_stats, use_container_width=True)
            
            with col2:
                st.subheader("📌 Performance by Influence")
                
                # Check if influence column exists and has data
                if 'influence' in df.columns and df['influence'].notna().any():
                    influence_stats = df[df['influence'] != ''].groupby('influence').agg({
                        'pnl': ['sum', 'mean', 'count']
                    }).round(2)
                    
                    if len(influence_stats) > 0:
                        influence_stats.columns = ['Total P&L', 'Avg P&L', 'Number of trades']
                        influence_stats = influence_stats.sort_values('Total P&L', ascending=False)
                        
                        # Create bar chart for influence
                        fig, ax = plt.subplots(figsize=(10, 5))
                        colors = ['#00ff88' if x > 0 else '#ff4444' for x in influence_stats['Total P&L']]
                        influence_stats['Total P&L'].plot(kind='bar', ax=ax, color=colors, 
                                                          edgecolor='white', linewidth=1.5)
                        ax.axhline(y=0, color='white', linewidth=1)
                        ax.set_xlabel('Influence/Reason', fontsize=12)
                        ax.set_ylabel('Total P&L ($)', fontsize=12)
                        ax.set_title('Profitability per Influence', fontsize=14, fontweight='bold')
                        ax.grid(True, alpha=0.3, axis='y')
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        st.pyplot(fig)
                        
                        st.dataframe(influence_stats, use_container_width=True)
                        
                        # Show best influence with date
                        best_influence = influence_stats.index[0]
                        best_influence_trades = df[df['influence'] == best_influence].sort_values('pnl', ascending=False)
                        if len(best_influence_trades) > 0:
                            best_inf_date = best_influence_trades.iloc[0]['date'].strftime('%Y-%m-%d')
                            best_inf_pnl = best_influence_trades.iloc[0]['pnl']
                            st.info(f"💡 Best '{best_influence}' trade: 📅 {best_inf_date} ({currency}{best_inf_pnl:.2f})")
                    else:
                        st.info("Add 'Influence' to your trades")
                else:
                    st.info("Add 'Influence' to your trades to see which reasons work best!")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🎯 Performance by Trade Type")
                type_stats = df.groupby('trade_type').agg({
                    'pnl': ['sum', 'mean', 'count']
                }).round(2)
                type_stats.columns = ['Total P&L', 'Avg P&L', 'Number of trades']
                type_stats = type_stats.sort_values('Total P&L', ascending=False)
                
                # Create bar chart for trade type
                fig, ax = plt.subplots(figsize=(10, 5))
                colors = ['#00ff88' if x > 0 else '#ff4444' for x in type_stats['Total P&L']]
                type_stats['Total P&L'].plot(kind='bar', ax=ax, color=colors, edgecolor='white', linewidth=1.5)
                ax.axhline(y=0, color='white', linewidth=1)
                ax.set_xlabel('Trade Type', fontsize=12)
                ax.set_ylabel('Total P&L ($)', fontsize=12)
                ax.set_title('Profitability per Trade Type', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                
                st.dataframe(type_stats, use_container_width=True)
            
            with col2:
                st.subheader("🌍 Performance by Market Condition")
                market_stats = df.groupby('market_condition').agg({
                    'pnl': ['sum', 'mean', 'count']
                }).round(2)
                market_stats.columns = ['Total P&L', 'Avg P&L', 'Number of trades']
                market_stats = market_stats.sort_values('Total P&L', ascending=False)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                colors = ['#00ff88' if x > 0 else '#ff4444' for x in market_stats['Total P&L']]
                market_stats['Total P&L'].plot(kind='bar', ax=ax, color=colors, edgecolor='white', linewidth=1.5)
                ax.axhline(y=0, color='white', linewidth=1)
                ax.set_xlabel('Market Condition', fontsize=12)
                ax.set_ylabel('Total P&L ($)', fontsize=12)
                ax.set_title('Profitability per Market Condition', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
                
                st.dataframe(market_stats, use_container_width=True)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("💪 Correlation: Mental State vs P&L")
                
                # Calculate correlations
                mental_factors = ['focus_level', 'stress_level', 'sleep_quality', 'pre_trade_confidence', 'duration_minutes']
                correlations = {}
                
                for factor in mental_factors:
                    if factor in df.columns:
                        corr = df[factor].corr(df['pnl'])
                        correlations[factor] = corr
                
                corr_df = pd.DataFrame(list(correlations.items()), columns=['Factor', 'Correlatie met P&L'])
                corr_df['Correlatie met P&L'] = corr_df['Correlatie met P&L'].round(3)
                corr_df = corr_df.sort_values('Correlatie met P&L', ascending=False)
                
                # Rename factors for display
                factor_names = {
                    'focus_level': 'Focus Level',
                    'stress_level': 'Stress Level',
                    'sleep_quality': 'Sleep Quality',
                    'pre_trade_confidence': 'Pre-Trade Confidence',
                    'duration_minutes': 'Trade Duration (Minutes)'
                }
                corr_df['Factor'] = corr_df['Factor'].map(factor_names)
                
                # Create bar chart
                fig, ax = plt.subplots(figsize=(10, 5))
                colors = ['#00ff88' if x > 0 else '#ff4444' for x in corr_df['Correlatie met P&L']]
                ax.barh(corr_df['Factor'], corr_df['Correlatie met P&L'], color=colors, edgecolor='white', linewidth=1.5)
                ax.axvline(x=0, color='white', linewidth=1)
                ax.set_xlabel('Correlatie Coefficient', fontsize=12)
                ax.set_title('Mental State Correlatie met P&L', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='x')
                plt.tight_layout()
                st.pyplot(fig)
                
                st.info("📈 Positive correlation = Higher value → Better results\n\n📉 Negative correlation = Higher value → Worse results")
                st.dataframe(corr_df, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("🔗 Mood → Setup → Influence Correlation")
                
                # Create cross-tabulation showing relationship
                if 'mood' in df.columns and 'influence' in df.columns:
                    st.caption("Which combination works best?")
                    
                    # Mood vs PnL
                    mood_influence = df.groupby(['mood', 'influence']).agg({
                        'pnl': ['sum', 'count']
                    }).round(2)
                    
                    if len(mood_influence) > 0:
                        mood_influence.columns = ['Total P&L', 'trades']
                        mood_influence = mood_influence[mood_influence['trades'] >= 1]  # At least 1 trade
                        mood_influence = mood_influence.sort_values('Total P&L', ascending=False).head(10)
                        
                        # Reset index to show mood and influence as columns
                        mood_influence = mood_influence.reset_index()
                        
                        st.dataframe(mood_influence, use_container_width=True, hide_index=True)
                        
                        # Best combination with date
                        if len(mood_influence) > 0:
                            best_combo = mood_influence.iloc[0]
                            # Find best trade with this combo
                            combo_trades = df[
                                (df['mood'] == best_combo['mood']) & 
                                (df['influence'] == best_combo['influence'])
                            ].sort_values('pnl', ascending=False)
                            
                            if len(combo_trades) > 0:
                                best_combo_date = combo_trades.iloc[0]['date'].strftime('%Y-%m-%d')
                                best_combo_pnl = combo_trades.iloc[0]['pnl']
                                st.success(f"🏆 **Best Combo:**\n\n{best_combo['mood']} + {best_combo['influence']}\n\n💰 {currency}{best_combo['Total P&L']:.2f} ({int(best_combo['trades'])} trades)\n\n📅 Best trade: {best_combo_date}\n💵 {currency}{best_combo_pnl:.2f}")
                    else:
                        st.info("Add trades to see correlations")
                else:
                    st.info("Add Mood and Influence data")
            
            st.divider()
            
            # Performance metrics by mental state ranges
            st.subheader("🎯 Performance by Confidence Level")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                high_conf = df[df['pre_trade_confidence'] >= 4]
                if len(high_conf) > 0:
                    avg_pnl = high_conf['pnl'].mean()
                    win_rate = (len(high_conf[high_conf['pnl'] > 0]) / len(high_conf) * 100)
                    best_high_conf = high_conf.sort_values('pnl', ascending=False).iloc[0]
                    st.metric("High Confidence (4-5)", f"{currency}{avg_pnl:.2f}", f"{win_rate:.1f}% WR")
                    st.caption(f"📅 Best: {best_high_conf['date'].strftime('%Y-%m-%d')} ({currency}{best_high_conf['pnl']:.2f})")
                else:
                    st.metric("High Confidence (4-5)", "N/A")
            
            with col2:
                med_conf = df[(df['pre_trade_confidence'] >= 2) & (df['pre_trade_confidence'] <= 3)]
                if len(med_conf) > 0:
                    avg_pnl = med_conf['pnl'].mean()
                    win_rate = (len(med_conf[med_conf['pnl'] > 0]) / len(med_conf) * 100)
                    best_med_conf = med_conf.sort_values('pnl', ascending=False).iloc[0]
                    st.metric("Normal Confidence (2-3)", f"{currency}{avg_pnl:.2f}", f"{win_rate:.1f}% WR")
                    st.caption(f"📅 Best: {best_med_conf['date'].strftime('%Y-%m-%d')} ({currency}{best_med_conf['pnl']:.2f})")
                else:
                    st.metric("Normal Confidence (2-3)", "N/A")
            
            with col3:
                low_conf = df[df['pre_trade_confidence'] <= 1]
                if len(low_conf) > 0:
                    avg_pnl = low_conf['pnl'].mean()
                    win_rate = (len(low_conf[low_conf['pnl'] > 0]) / len(low_conf) * 100)
                    best_low_conf = low_conf.sort_values('pnl', ascending=False).iloc[0]
                    st.metric("Low Confidence (1)", f"{currency}{avg_pnl:.2f}", f"{win_rate:.1f}% WR")
                    st.caption(f"📅 Best: {best_low_conf['date'].strftime('%Y-%m-%d')} ({currency}{best_low_conf['pnl']:.2f})")
                else:
                    st.metric("Low Confidence (1)", "N/A")
            
            st.divider()
            
            # Trade Duration Analysis
            if 'duration_minutes' in df.columns:
                st.subheader("⏱️ Trade Duration Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Average duration for winners vs losers
                    winners = df[df['pnl'] > 0]
                    losers = df[df['pnl'] < 0]
                    
                    avg_win_duration = winners['duration_minutes'].mean() if len(winners) > 0 else 0
                    avg_loss_duration = losers['duration_minutes'].mean() if len(losers) > 0 else 0
                    
                    # Best winning trade by duration
                    if len(winners) > 0:
                        best_winner = winners.sort_values('pnl', ascending=False).iloc[0]
                        best_win_date = best_winner['date'].strftime('%Y-%m-%d')
                        best_win_duration = best_winner['duration_minutes']
                        best_win_pnl = best_winner['pnl']
                    
                    duration_col1, duration_col2 = st.columns(2)
                    with duration_col1:
                        st.metric("Avg Duration Wins", f"{avg_win_duration:.0f} min")
                        if len(winners) > 0:
                            st.caption(f"📅 Best: {best_win_date} ({best_win_duration:.0f}min, {currency}{best_win_pnl:.2f})")
                    with duration_col2:
                        st.metric("Avg Duration Losses", f"{avg_loss_duration:.0f} min")
                    
                    # Chart: Duration distribution
                    fig, ax = plt.subplots(figsize=(10, 5))
                    
                    if len(winners) > 0:
                        ax.hist(winners['duration_minutes'], bins=20, alpha=0.5, color='#00ff88', 
                               label='Wins', edgecolor='white')
                    if len(losers) > 0:
                        ax.hist(losers['duration_minutes'], bins=20, alpha=0.5, color='#ff4444', 
                               label='Losses', edgecolor='white')
                    
                    ax.set_xlabel('Duration (Minutes)', fontsize=12)
                    ax.set_ylabel('Number of trades', fontsize=12)
                    ax.set_title('Trade Duration Distributie', fontsize=14, fontweight='bold')
                    ax.legend()
                    ax.grid(True, alpha=0.3, axis='y')
                    plt.tight_layout()
                    st.pyplot(fig)
                
                with col2:
                    # Performance by duration buckets
                    st.caption("Performance per tijdsduur")
                    
                    # Create duration buckets
                    df_duration = df[df['duration_minutes'] > 0].copy()
                    
                    if len(df_duration) > 0:
                        # Define buckets
                        bins = [0, 5, 15, 30, 60, 120, float('inf')]
                        labels = ['0-5 min', '5-15 min', '15-30 min', '30-60 min', '1-2 uur', '2+ uur']
                        
                        df_duration['duration_bucket'] = pd.cut(df_duration['duration_minutes'], 
                                                                bins=bins, labels=labels, right=False)
                        
                        duration_stats = df_duration.groupby('duration_bucket').agg({
                            'pnl': ['sum', 'mean', 'count']
                        }).round(2)
                        
                        duration_stats.columns = ['Total P&L', 'Avg P&L', 'Count']
                        
                        st.dataframe(duration_stats, use_container_width=True)
                        
                        # Bar chart
                        fig, ax = plt.subplots(figsize=(10, 5))
                        colors = ['#00ff88' if x > 0 else '#ff4444' for x in duration_stats['Total P&L']]
                        duration_stats['Total P&L'].plot(kind='bar', ax=ax, color=colors, 
                                                         edgecolor='white', linewidth=1.5)
                        ax.axhline(y=0, color='white', linewidth=1)
                        ax.set_xlabel('Duration', fontsize=12)
                        ax.set_ylabel('Total P&L ($)', fontsize=12)
                        ax.set_title('Performance per Trade Duration', fontsize=14, fontweight='bold')
                        ax.grid(True, alpha=0.3, axis='y')
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        st.pyplot(fig)
                    else:
                        st.info("Add duration to your trades for this analysis")
            
            st.divider()
            
            # Best performing conditions
            st.subheader("⭐ Optimal Trading Conditions")
            
            # Find best mood with dates
            best_mood = mood_stats['Total P&L'].idxmax()
            best_mood_pnl = mood_stats.loc[best_mood, 'Total P&L']
            best_mood_trades = df[df['mood'] == best_mood].sort_values('pnl', ascending=False)
            best_mood_date = best_mood_trades.iloc[0]['date'].strftime('%Y-%m-%d') if len(best_mood_trades) > 0 else 'N/A'
            best_mood_best_pnl = best_mood_trades.iloc[0]['pnl'] if len(best_mood_trades) > 0 else 0
            
            # Find best trade type with dates
            best_type = type_stats['Total P&L'].idxmax()
            best_type_pnl = type_stats.loc[best_type, 'Total P&L']
            best_type_trades = df[df['trade_type'] == best_type].sort_values('pnl', ascending=False)
            best_type_date = best_type_trades.iloc[0]['date'].strftime('%Y-%m-%d') if len(best_type_trades) > 0 else 'N/A'
            best_type_best_pnl = best_type_trades.iloc[0]['pnl'] if len(best_type_trades) > 0 else 0
            
            # Find best market condition with dates
            best_market = market_stats['Total P&L'].idxmax()
            best_market_pnl = market_stats.loc[best_market, 'Total P&L']
            best_market_trades = df[df['market_condition'] == best_market].sort_values('pnl', ascending=False)
            best_market_date = best_market_trades.iloc[0]['date'].strftime('%Y-%m-%d') if len(best_market_trades) > 0 else 'N/A'
            best_market_best_pnl = best_market_trades.iloc[0]['pnl'] if len(best_market_trades) > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success(f"**Best Mood:** {best_mood}\n\n💰 {currency}{best_mood_pnl:.2f} total\n\n📅 Best trade: {best_mood_date}\n💵 {currency}{best_mood_best_pnl:.2f}")
            with col2:
                st.success(f"**Best Trade Type:** {best_type}\n\n💰 {currency}{best_type_pnl:.2f} total\n\n📅 Best trade: {best_type_date}\n💵 {currency}{best_type_best_pnl:.2f}")
            with col3:
                st.success(f"**Best Market:** {best_market}\n\n💰 {currency}{best_market_pnl:.2f} total\n\n📅 Best trade: {best_market_date}\n💵 {currency}{best_market_best_pnl:.2f}")
            
        else:
            st.warning("⚠️ No psychological data available. Add trades with the new fields!")
    
    # PAGE: Advanced Analytics
    if selected_page == "🔬 Advanced Analytics":
        st.header("🔬 Advanced Analytics & AI Insights")
        
        if not ANALYTICS_AVAILABLE:
            st.error("❌ Analytics module not available")
        elif len(trades) < 10:
            st.warning("📊 Add at least 10 trades to unlock Advanced Analytics insights")
        else:
            st.success(f"✅ Analyzing {len(trades)} trades with AI-powered insights...")
            
            # Get complete analysis
            analysis = get_complete_analysis(trades)
            
            # === AI INSIGHTS ===
            st.subheader("🤖 AI-Powered Insights")
            insights = analysis['ai_insights']
            
            for i, insight in enumerate(insights, 1):
                if insight.startswith("🧠"):
                    st.info(insight)
                elif insight.startswith("⚠️") or insight.startswith("🛑"):
                    st.warning(insight)
                elif insight.startswith("✅"):
                    st.success(insight)
                else:
                    st.write(f"{i}. {insight}")
            
            st.divider()
            
            # === PSYCHOLOGY CORRELATIONS ===
            if analysis['psychology']:
                st.subheader("🧠 Psychology Performance Analysis")
                psych = analysis['psychology']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Mood Analysis
                    if psych['mood_analysis']:
                        st.metric("Best Mood", psych['mood_analysis']['best_mood'], 
                                 f"€{psych['mood_analysis']['best_mood_avg_pnl']:.2f} avg")
                        st.metric("Worst Mood", psych['mood_analysis']['worst_mood'],
                                 f"€{psych['mood_analysis']['worst_mood_avg_pnl']:.2f} avg")
                    
                    # Focus Analysis
                    if psych['focus_analysis']:
                        st.metric("Focus Impact", 
                                 f"€{psych['focus_analysis']['difference']:.2f}",
                                 f"Correlation: {psych['focus_analysis']['correlation']:.2f}")
                
                with col2:
                    # Stress Analysis
                    if psych['stress_analysis']:
                        st.metric("Stress Impact (Lower is Better)", 
                                 f"€{psych['stress_analysis']['difference']:.2f}",
                                 f"Correlation: {psych['stress_analysis']['correlation']:.2f}")
                    
                    # Sleep Analysis
                    if psych['sleep_analysis']:
                        st.metric("Sleep Impact", 
                                 f"€{psych['sleep_analysis']['difference']:.2f}",
                                 f"Correlation: {psych['sleep_analysis']['correlation']:.2f}")
                
                st.divider()
            
            # === TIME PATTERNS ===
            if analysis['time_patterns']:
                st.subheader("⏰ Time-Based Performance Patterns")
                time_pat = analysis['time_patterns']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if time_pat['day_analysis']:
                        st.write("**📅 Best/Worst Trading Days:**")
                        st.metric("Best Day", time_pat['day_analysis']['best_day'],
                                 f"€{time_pat['day_analysis']['best_day_avg']:.2f} avg")
                        st.metric("Worst Day", time_pat['day_analysis']['worst_day'],
                                 f"€{time_pat['day_analysis']['worst_day_avg']:.2f} avg")
                
                with col2:
                    if time_pat['hour_analysis'] and time_pat['hour_analysis']['best_hours']:
                        st.write("**🕐 Best Trading Hours:**")
                        best_hours = time_pat['hour_analysis']['best_hours'][:3]
                        st.write(f"✅ {', '.join([f'{h}:00' for h in best_hours])}")
                        
                        st.write("**⚠️ Worst Trading Hours:**")
                        worst_hours = time_pat['hour_analysis']['worst_hours'][:3]
                        st.write(f"❌ {', '.join([f'{h}:00' for h in worst_hours])}")
                
                st.divider()
            
            # === SETUP & SYMBOL ANALYSIS ===
            if analysis['setups_symbols']:
                st.subheader("📊 Setup & Symbol Performance")
                setup_sym = analysis['setups_symbols']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if setup_sym['setup_analysis']:
                        st.write("**🎯 Best Setup:**")
                        st.metric(setup_sym['setup_analysis']['best_setup'],
                                 f"€{setup_sym['setup_analysis']['best_setup_avg']:.2f} avg",
                                 f"{setup_sym['setup_analysis']['best_setup_winrate']:.1f}% WR")
                        
                        st.write("**❌ Worst Setup:**")
                        st.metric(setup_sym['setup_analysis']['worst_setup'],
                                 f"€{setup_sym['setup_analysis']['worst_setup_avg']:.2f} avg")
                
                with col2:
                    if setup_sym['symbol_analysis']:
                        st.write("**💰 Best Symbol:**")
                        st.metric(setup_sym['symbol_analysis']['best_symbol'],
                                 f"€{setup_sym['symbol_analysis']['best_symbol_avg']:.2f} avg",
                                 f"{setup_sym['symbol_analysis']['best_symbol_winrate']:.1f}% WR")
                        
                        st.write("**⚠️ Worst Symbol:**")
                        st.metric(setup_sym['symbol_analysis']['worst_symbol'],
                                 f"€{setup_sym['symbol_analysis']['worst_symbol_avg']:.2f} avg",
                                 f"{setup_sym['symbol_analysis']['worst_symbol_winrate']:.1f}% WR")
            
            st.divider()
            
            # === DETAILED STATS TABLES ===
            with st.expander("📋 Detailed Statistics Tables", expanded=False):
                tab1, tab2, tab3 = st.tabs(["Psychology", "Time Patterns", "Setups & Symbols"])
                
                with tab1:
                    if analysis['psychology']:
                        st.write("**Mood Statistics:**")
                        if analysis['psychology']['mood_analysis']:
                            st.json(analysis['psychology']['mood_analysis'])
                
                with tab2:
                    if analysis['time_patterns']:
                        st.write("**Day Statistics:**")
                        if analysis['time_patterns']['day_analysis']:
                            st.json(analysis['time_patterns']['day_analysis'])
                
                with tab3:
                    if analysis['setups_symbols']:
                        st.write("**Setup Statistics:**")
                        if analysis['setups_symbols']['setup_analysis']:
                            st.json(analysis['setups_symbols']['setup_analysis'])
    
    # PAGE: AI Assistant
    if selected_page == "🤖 AI Assistant":
        st.header("🤖 AI Trading Assistant")
        st.info("💡 Get intelligent insights, daily summaries, and strategy optimization suggestions")
        
        if not AI_ASSISTANT_AVAILABLE:
            st.error("❌ AI Assistant module not available")
        elif len(trades) < 5:
            st.warning("📊 Add at least 5 trades to unlock AI Assistant features")
        else:
            st.success(f"✅ AI Assistant ready! Analyzing {len(trades)} trades...")
            
            # Create tabs for different AI features
            tab1, tab2, tab3, tab4 = st.tabs(["📅 Daily Summary", "🔍 Pattern Analysis", "💡 Strategy Suggestions", "📊 Weekly Report"])
            
            with tab1:
                st.subheader("📅 Daily Trading Summary")
                st.write("Get AI-powered insights about your daily trading performance")
                
                # Date selector for daily summary
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    selected_date = st.date_input(
                        "Select Date",
                        value=datetime.now().date(),
                        max_value=datetime.now().date(),
                        help="Choose a date to analyze"
                    )
                
                with col2:
                    if st.button("🔄 Generate Summary", type="primary", use_container_width=True):
                        st.session_state['generate_daily_summary'] = True
                
                if st.session_state.get('generate_daily_summary', False):
                    with st.spinner("🤖 AI is analyzing your trades..."):
                        try:
                            daily_summary = get_daily_summary(trades, selected_date.strftime('%Y-%m-%d'))
                            
                            # Display summary
                            st.markdown(f"### 📊 {daily_summary['date']} Summary")
                            st.markdown(daily_summary['summary'])
                            
                            # Display stats
                            if daily_summary['stats']:
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total Trades", daily_summary['stats']['total_trades'])
                                with col2:
                                    st.metric("Total P&L", f"€{daily_summary['stats']['total_pnl']:.2f}")
                                with col3:
                                    st.metric("Win Rate", f"{daily_summary['stats']['win_rate']:.1f}%")
                                with col4:
                                    st.metric("Best Trade", f"€{daily_summary['stats']['best_trade']:.2f}")
                            
                            # Display insights
                            if daily_summary['insights']:
                                st.subheader("🧠 AI Insights")
                                for insight in daily_summary['insights']:
                                    st.info(insight)
                            
                            # Display recommendations
                            if daily_summary['recommendations']:
                                st.subheader("💡 AI Recommendations")
                                for rec in daily_summary['recommendations']:
                                    st.warning(rec)
                            
                        except Exception as e:
                            st.error(f"Error generating summary: {str(e)}")
                        finally:
                            st.session_state['generate_daily_summary'] = False
            
            with tab2:
                st.subheader("🔍 Trading Pattern Analysis")
                st.write("Discover patterns in your trading behavior and performance")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    analysis_days = st.slider(
                        "Analysis Period (days)",
                        min_value=7,
                        max_value=90,
                        value=30,
                        help="How many days back to analyze"
                    )
                
                with col2:
                    if st.button("🔍 Analyze Patterns", type="primary", use_container_width=True):
                        st.session_state['analyze_patterns'] = True
                
                if st.session_state.get('analyze_patterns', False):
                    with st.spinner("🔍 AI is analyzing patterns..."):
                        try:
                            patterns = analyze_patterns(trades, analysis_days)
                            
                            if 'error' in patterns:
                                st.error(patterns['error'])
                            else:
                                # Day of week analysis
                                if 'day_of_week' in patterns:
                                    st.subheader("📅 Performance by Day of Week")
                                    
                                    dow_data = []
                                    for day, stats in patterns['day_of_week'].items():
                                        dow_data.append({
                                            'Day': day,
                                            'Total P&L': stats['total_pnl'],
                                            'Avg P&L': stats['avg_pnl'],
                                            'Trades': stats['trade_count'],
                                            'Win Rate': f"{stats['win_rate']:.1f}%"
                                        })
                                    
                                    if dow_data:
                                        dow_df = pd.DataFrame(dow_data)
                                        st.dataframe(dow_df, use_container_width=True)
                                        
                                        # Best and worst days
                                        best_day = max(patterns['day_of_week'].items(), key=lambda x: x[1]['total_pnl'])
                                        worst_day = min(patterns['day_of_week'].items(), key=lambda x: x[1]['total_pnl'])
                                        
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.success(f"🏆 **Best Day**: {best_day[0]} (€{best_day[1]['total_pnl']:.2f})")
                                        with col2:
                                            st.error(f"⚠️ **Worst Day**: {worst_day[0]} (€{worst_day[1]['total_pnl']:.2f})")
                                
                                # Symbol analysis
                                if 'symbols' in patterns:
                                    st.subheader("💰 Performance by Symbol")
                                    
                                    symbol_data = []
                                    for symbol, stats in patterns['symbols'].items():
                                        symbol_data.append({
                                            'Symbol': symbol,
                                            'Total P&L': stats['total_pnl'],
                                            'Avg P&L': stats['avg_pnl'],
                                            'Trades': stats['trade_count'],
                                            'Win Rate': f"{stats['win_rate']:.1f}%"
                                        })
                                    
                                    if symbol_data:
                                        symbol_df = pd.DataFrame(symbol_data)
                                        symbol_df = symbol_df.sort_values('Total P&L', ascending=False)
                                        st.dataframe(symbol_df, use_container_width=True)
                                
                                # Psychology analysis
                                if 'psychology' in patterns:
                                    st.subheader("🧠 Performance by Mood")
                                    
                                    mood_data = []
                                    for mood, stats in patterns['psychology'].items():
                                        mood_data.append({
                                            'Mood': mood,
                                            'Total P&L': stats['total_pnl'],
                                            'Avg P&L': stats['avg_pnl'],
                                            'Trades': stats['trade_count'],
                                            'Win Rate': f"{stats['win_rate']:.1f}%"
                                        })
                                    
                                    if mood_data:
                                        mood_df = pd.DataFrame(mood_data)
                                        mood_df = mood_df.sort_values('Total P&L', ascending=False)
                                        st.dataframe(mood_df, use_container_width=True)
                        
                        except Exception as e:
                            st.error(f"Error analyzing patterns: {str(e)}")
                        finally:
                            st.session_state['analyze_patterns'] = False
            
            with tab3:
                st.subheader("💡 Strategy Optimization Suggestions")
                st.write("Get AI-powered recommendations to improve your trading strategy")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    suggestion_days = st.slider(
                        "Analysis Period for Suggestions",
                        min_value=7,
                        max_value=90,
                        value=30,
                        help="How many days back to analyze for suggestions"
                    )
                
                with col2:
                    if st.button("💡 Get Suggestions", type="primary", use_container_width=True):
                        st.session_state['get_suggestions'] = True
                
                if st.session_state.get('get_suggestions', False):
                    with st.spinner("💡 AI is generating suggestions..."):
                        try:
                            suggestions = get_strategy_suggestions(trades, suggestion_days)
                            
                            if suggestions:
                                # Group suggestions by priority
                                high_priority = [s for s in suggestions if s.get('priority') == 'high']
                                medium_priority = [s for s in suggestions if s.get('priority') == 'medium']
                                low_priority = [s for s in suggestions if s.get('priority') == 'low']
                                
                                if high_priority:
                                    st.subheader("🔴 High Priority")
                                    for sug in high_priority:
                                        if sug['type'] == 'warning':
                                            st.error(f"**{sug['title']}**")
                                        else:
                                            st.warning(f"**{sug['title']}**")
                                        st.write(sug['message'])
                                        st.divider()
                                
                                if medium_priority:
                                    st.subheader("🟡 Medium Priority")
                                    for sug in medium_priority:
                                        st.info(f"**{sug['title']}**")
                                        st.write(sug['message'])
                                        st.divider()
                                
                                if low_priority:
                                    st.subheader("🟢 Low Priority")
                                    for sug in low_priority:
                                        st.success(f"**{sug['title']}**")
                                        st.write(sug['message'])
                                        st.divider()
                            else:
                                st.info("No specific suggestions at this time. Keep trading consistently!")
                        
                        except Exception as e:
                            st.error(f"Error generating suggestions: {str(e)}")
                        finally:
                            st.session_state['get_suggestions'] = False
            
            with tab4:
                st.subheader("📊 Weekly AI Report")
                st.write("Comprehensive weekly analysis and insights")
                
                if st.button("📊 Generate Weekly Report", type="primary", use_container_width=True):
                    st.session_state['generate_weekly_report'] = True
                
                if st.session_state.get('generate_weekly_report', False):
                    with st.spinner("📊 AI is generating weekly report..."):
                        try:
                            weekly_report = get_weekly_report(trades)
                            
                            # Display summary
                            st.markdown(f"### 📈 Weekly Summary")
                            st.markdown(weekly_report['summary'])
                            
                            # Display stats
                            if weekly_report['stats']:
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Total P&L", f"€{weekly_report['stats']['total_pnl']:.2f}")
                                with col2:
                                    st.metric("Total Trades", weekly_report['stats']['total_trades'])
                                with col3:
                                    st.metric("Win Rate", f"{weekly_report['stats']['win_rate']:.1f}%")
                                with col4:
                                    st.metric("Win Count", weekly_report['stats']['win_count'])
                            
                            # Display insights
                            if weekly_report['insights']:
                                st.subheader("🧠 Weekly Insights")
                                for insight in weekly_report['insights']:
                                    st.info(insight)
                            
                            # Display recommendations
                            if weekly_report['recommendations']:
                                st.subheader("💡 Weekly Recommendations")
                                for rec in weekly_report['recommendations']:
                                    if rec.get('priority') == 'high':
                                        st.error(f"**{rec['title']}**: {rec['message']}")
                                    elif rec.get('priority') == 'medium':
                                        st.warning(f"**{rec['title']}**: {rec['message']}")
                                    else:
                                        st.info(f"**{rec['title']}**: {rec['message']}")
                        
                        except Exception as e:
                            st.error(f"Error generating weekly report: {str(e)}")
                        finally:
                            st.session_state['generate_weekly_report'] = False
    
    # PAGE: Mobile PWA
    if selected_page == "📱 Mobile PWA":
        st.header("📱 Mobile PWA & Quick Logging")
        st.info("💡 Install as mobile app, enable notifications, and use quick logging features")
        
        if not MOBILE_PWA_AVAILABLE:
            st.error("❌ Mobile PWA module not available")
        else:
            st.success("✅ Mobile PWA features ready!")
            
            # Create tabs for different PWA features
            tab1, tab2, tab3, tab4 = st.tabs(["📱 Install App", "⚡ Quick Logging", "🔔 Notifications", "📊 Mobile Stats"])
            
            with tab1:
                st.subheader("📱 Install as Mobile App")
                st.write("Transform your Trading Journal into a native mobile app experience")
                
                # PWA Installation Info
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    **🚀 PWA Benefits:**
                    - 📱 Install on home screen
                    - ⚡ Offline functionality
                    - 🔔 Push notifications
                    - 📲 Native app feel
                    - 🎯 Quick access
                    """)
                
                with col2:
                    st.markdown("""
                    **📋 Installation Steps:**
                    1. Click "Install App" button
                    2. Follow browser prompts
                    3. App appears on home screen
                    4. Launch like native app
                    """)
                
                # PWA Status Check
                st.subheader("📊 PWA Status")
                
                # Check if running as PWA
                is_pwa = st.checkbox("Running as PWA", value=False, disabled=True)
                if is_pwa:
                    st.success("✅ Running as Progressive Web App!")
                else:
                    st.info("💡 Install the app to run as PWA")
                
                # Service Worker Status
                sw_status = st.checkbox("Service Worker Active", value=False, disabled=True)
                if sw_status:
                    st.success("✅ Service Worker is active - offline functionality enabled!")
                else:
                    st.info("💡 Service Worker will activate after installation")
                
                # Installation Instructions
                st.subheader("📱 Installation Instructions")
                
                with st.expander("🖥️ Desktop Installation", expanded=True):
                    st.markdown("""
                    **Chrome/Edge:**
                    1. Look for install icon in address bar
                    2. Click "Install Trading Journal Pro"
                    3. Confirm installation
                    
                    **Firefox:**
                    1. Click menu (3 lines)
                    2. Select "Install"
                    3. Confirm installation
                    """)
                
                with st.expander("📱 Mobile Installation"):
                    st.markdown("""
                    **Android Chrome:**
                    1. Tap menu (3 dots)
                    2. Select "Add to Home screen"
                    3. Tap "Add"
                    
                    **iOS Safari:**
                    1. Tap Share button
                    2. Select "Add to Home Screen"
                    3. Tap "Add"
                    """)
                
                # PWA Manifest Download
                st.subheader("📄 PWA Files")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    manifest = get_pwa_manifest()
                    st.download_button(
                        label="📄 Download Manifest",
                        data=json.dumps(manifest, indent=2),
                        file_name="manifest.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col2:
                    service_worker = get_service_worker()
                    st.download_button(
                        label="⚙️ Download Service Worker",
                        data=service_worker,
                        file_name="sw.js",
                        mime="application/javascript",
                        use_container_width=True
                    )
                
                with col3:
                    pwa_html = get_pwa_html()
                    st.download_button(
                        label="🌐 Download PWA HTML",
                        data=pwa_html,
                        file_name="pwa.html",
                        mime="text/html",
                        use_container_width=True
                    )
            
            with tab2:
                st.subheader("⚡ Quick Trade Logging")
                st.write("Fast and easy trade entry optimized for mobile devices")
                
                # Quick Log Form
                with st.form("quick_log_form"):
                    st.markdown("### 🚀 Quick Trade Entry")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        quick_symbol = st.text_input(
                            "Symbol",
                            placeholder="EURUSD",
                            help="Trading symbol"
                        )
                        
                        quick_side = st.selectbox(
                            "Side",
                            ["Long", "Short"],
                            help="Trade direction"
                        )
                    
                    with col2:
                        quick_entry = st.number_input(
                            "Entry Price",
                            min_value=0.0,
                            step=0.00001,
                            format="%.5f",
                            help="Entry price"
                        )
                        
                        quick_exit = st.number_input(
                            "Exit Price", 
                            min_value=0.0,
                            step=0.00001,
                            format="%.5f",
                            help="Exit price"
                        )
                    
                    quick_quantity = st.number_input(
                        "Quantity",
                        min_value=0.01,
                        value=1.0,
                        step=0.01,
                        help="Position size"
                    )
                    
                    quick_notes = st.text_area(
                        "Quick Notes",
                        placeholder="Optional notes...",
                        height=100,
                        help="Quick notes about the trade"
                    )
                    
                    submitted = st.form_submit_button("⚡ Quick Save", type="primary", use_container_width=True)
                    
                    if submitted:
                        if quick_symbol and quick_entry > 0 and quick_exit > 0:
                            # Calculate P&L
                            if quick_side == "Long":
                                pnl = (quick_exit - quick_entry) * quick_quantity
                            else:
                                pnl = (quick_entry - quick_exit) * quick_quantity
                            
                            # Create trade object
                            quick_trade = {
                                'id': max([t.get('id', 0) for t in trades], default=0) + 1,
                                'user_id': current_user['id'],
                                'account_id': selected_account.get('id', 1),
                                'account_name': selected_account.get('name', 'Main Account'),
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'time': datetime.now().strftime('%H:%M:%S'),
                                'symbol': quick_symbol.upper(),
                                'side': quick_side,
                                'entry_price': quick_entry,
                                'exit_price': quick_exit,
                                'quantity': quick_quantity,
                                'duration_minutes': 0,
                                'pnl': round(pnl, 2),
                                'r_multiple': round(pnl / (selected_account.get('size', 10000) * 0.01), 2),
                                'setup': 'Quick Log',
                                'influence': 'Mobile',
                                'trade_type': 'Quick',
                                'market_condition': 'Unknown',
                                'mood': 'Quick',
                                'focus_level': 3,
                                'stress_level': 3,
                                'sleep_quality': 3,
                                'pre_trade_confidence': 3,
                                'notes': quick_notes
                            }
                            
                            # Save trade
                            trades.append(quick_trade)
                            save_trades(trades)
                            
                            st.success(f"⚡ Trade saved! P&L: €{pnl:.2f}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Please fill in all required fields")
                
                # Quick Stats
                st.subheader("📊 Quick Stats")
                
                if trades:
                    recent_trades = [t for t in trades if t.get('setup') == 'Quick Log']
                    
                    if recent_trades:
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Quick Trades", len(recent_trades))
                        
                        with col2:
                            quick_pnl = sum(t.get('pnl', 0) for t in recent_trades)
                            st.metric("Quick P&L", f"€{quick_pnl:.2f}")
                        
                        with col3:
                            quick_wins = len([t for t in recent_trades if t.get('pnl', 0) > 0])
                            quick_wr = (quick_wins / len(recent_trades) * 100) if recent_trades else 0
                            st.metric("Quick Win Rate", f"{quick_wr:.1f}%")
                        
                        with col4:
                            avg_quick = sum(t.get('pnl', 0) for t in recent_trades) / len(recent_trades)
                            st.metric("Avg Quick P&L", f"€{avg_quick:.2f}")
                    else:
                        st.info("No quick trades yet. Start logging!")
                else:
                    st.info("No trades yet. Start logging!")
            
            with tab3:
                st.subheader("🔔 Push Notifications")
                st.write("Enable notifications for trading reminders and alerts")
                
                # Notification Settings
                st.markdown("### ⚙️ Notification Settings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    market_open_reminder = st.checkbox(
                        "Market Open Reminder",
                        value=True,
                        help="Get notified when markets open"
                    )
                    
                    market_close_reminder = st.checkbox(
                        "Market Close Reminder", 
                        value=True,
                        help="Get notified when markets close"
                    )
                
                with col2:
                    journal_reminder = st.checkbox(
                        "Journal Reminder",
                        value=True,
                        help="Daily reminder to log trades"
                    )
                    
                    weekly_review = st.checkbox(
                        "Weekly Review",
                        value=True,
                        help="Weekly performance review reminder"
                    )
                
                # Notification Schedule Preview
                st.subheader("📅 Notification Schedule")
                
                user_prefs = {
                    'market_open_reminder': market_open_reminder,
                    'market_close_reminder': market_close_reminder,
                    'journal_reminder': journal_reminder,
                    'weekly_review': weekly_review
                }
                
                notifications = get_push_notification_schedule(user_prefs)
                
                if notifications:
                    for notif in notifications:
                        col1, col2, col3 = st.columns([2, 2, 1])
                        
                        with col1:
                            st.write(f"**{notif['title']}**")
                        
                        with col2:
                            time_str = notif.get('time', '')
                            day_str = notif.get('day', 'Daily')
                            st.write(f"{day_str} at {time_str}")
                        
                        with col3:
                            st.write(notif['body'])
                        
                        st.divider()
                else:
                    st.info("No notifications configured")
                
                # Notification Test
                st.subheader("🧪 Test Notifications")
                
                if st.button("🔔 Test Notification", type="primary"):
                    st.success("✅ Test notification sent! (Note: Actual notifications require PWA installation)")
                
                # Notification Status
                st.subheader("📊 Notification Status")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Notifications Enabled", "Yes" if any(user_prefs.values()) else "No")
                
                with col2:
                    st.metric("Scheduled Notifications", len(notifications))
            
            with tab4:
                st.subheader("📊 Mobile-Optimized Stats")
                st.write("Key metrics optimized for mobile viewing")
                
                if trades:
                    # Mobile-friendly metrics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 📈 Today's Performance")
                        
                        today = datetime.now().strftime('%Y-%m-%d')
                        today_trades = [t for t in trades if t.get('date') == today]
                        
                        if today_trades:
                            today_pnl = sum(t.get('pnl', 0) for t in today_trades)
                            today_wins = len([t for t in today_trades if t.get('pnl', 0) > 0])
                            today_wr = (today_wins / len(today_trades) * 100) if today_trades else 0
                            
                            st.metric("Today's P&L", f"€{today_pnl:.2f}")
                            st.metric("Today's Trades", len(today_trades))
                            st.metric("Today's Win Rate", f"{today_wr:.1f}%")
                        else:
                            st.info("No trades today")
                    
                    with col2:
                        st.markdown("### 📊 This Week")
                        
                        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                        week_trades = [t for t in trades if t.get('date', '') >= week_ago]
                        
                        if week_trades:
                            week_pnl = sum(t.get('pnl', 0) for t in week_trades)
                            week_wins = len([t for t in week_trades if t.get('pnl', 0) > 0])
                            week_wr = (week_wins / len(week_trades) * 100) if week_trades else 0
                            
                            st.metric("Week's P&L", f"€{week_pnl:.2f}")
                            st.metric("Week's Trades", len(week_trades))
                            st.metric("Week's Win Rate", f"{week_wr:.1f}%")
                        else:
                            st.info("No trades this week")
                    
                    # Mobile-friendly charts
                    st.markdown("### 📈 Mobile Charts")
                    
                    # Simple P&L chart
                    if len(trades) > 1:
                        df = pd.DataFrame(trades)
                        df['date'] = pd.to_datetime(df['date'])
                        df = df.sort_values('date')
                        df['cumulative_pnl'] = df['pnl'].cumsum()
                        
                        st.line_chart(
                            df.set_index('date')['cumulative_pnl'],
                            height=300
                        )
                    
                    # Top performing symbols
                    if trades:
                        symbol_pnl = {}
                        for trade in trades:
                            symbol = trade.get('symbol', 'Unknown')
                            if symbol not in symbol_pnl:
                                symbol_pnl[symbol] = 0
                            symbol_pnl[symbol] += trade.get('pnl', 0)
                        
                        if symbol_pnl:
                            top_symbols = sorted(symbol_pnl.items(), key=lambda x: x[1], reverse=True)[:5]
                            
                            st.markdown("### 🏆 Top Symbols")
                            for symbol, pnl in top_symbols:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.write(symbol)
                                with col2:
                                    color = "green" if pnl > 0 else "red"
                                    st.write(f":{color}[€{pnl:.2f}]")
                else:
                    st.info("Add some trades to see mobile stats!")
    
    # PAGE: Broker Integration
    if selected_page == "🔗 Broker Integration":
        st.header("🔗 Broker Integration & TradingView Webhooks")
        st.info("💡 Connect your TradingView alerts to automatically log trades")
        
        if not BROKER_INTEGRATION_AVAILABLE:
            st.error("❌ Broker Integration module not available")
        else:
            st.success("✅ Broker Integration ready!")
            
            # Create tabs for different integration features
            tab1, tab2, tab3, tab4 = st.tabs(["📊 TradingView Setup", "🔗 Webhook Management", "📈 Test Integration", "📋 Integration Status"])
            
            with tab1:
                st.subheader("📊 TradingView Webhook Setup")
                st.write("Connect your TradingView alerts to automatically create trades in your journal")
                
                # Setup TradingView Integration
                st.markdown("### 🚀 Setup TradingView Integration")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    **📈 TradingView Benefits:**
                    - ⚡ Automatic trade logging
                    - 🎯 Real-time alerts
                    - 📊 Strategy integration
                    - 🔄 No manual entry needed
                    - 📱 Works with any device
                    """)
                
                with col2:
                    st.markdown("""
                    **🔧 How It Works:**
                    1. Create webhook URL
                    2. Setup TradingView alert
                    3. Configure message format
                    4. Trades auto-logged
                    5. Review in journal
                    """)
                
                # Integration Settings
                st.subheader("⚙️ Integration Settings")
                
                with st.form("tradingview_setup"):
                    st.markdown("### 🔧 Configure Integration")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        auto_create_trades = st.checkbox(
                            "Auto-create trades",
                            value=True,
                            help="Automatically create trades from webhooks"
                        )
                        
                        default_quantity = st.number_input(
                            "Default quantity",
                            min_value=0.01,
                            value=1.0,
                            step=0.01,
                            help="Default position size for trades"
                        )
                    
                    with col2:
                        risk_per_trade = st.number_input(
                            "Risk per trade (%)",
                            min_value=0.1,
                            max_value=10.0,
                            value=1.0,
                            step=0.1,
                            help="Risk percentage per trade"
                        )
                        
                        notification_enabled = st.checkbox(
                            "Enable notifications",
                            value=True,
                            help="Get notified when trades are created"
                        )
                    
                    # Symbol mapping
                    st.markdown("### 🎯 Symbol Mapping")
                    st.write("Map TradingView symbols to your preferred format")
                    
                    symbol_mapping = {}
                    symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'NZDUSD', 'EURJPY', 'GBPJPY']
                    
                    for symbol in symbols:
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write(symbol)
                        with col2:
                            mapped_symbol = st.text_input(
                                f"Map {symbol}",
                                value=symbol,
                                key=f"symbol_{symbol}",
                                help=f"TradingView symbol for {symbol}"
                            )
                            symbol_mapping[symbol] = mapped_symbol
                    
                    submitted = st.form_submit_button("🔗 Setup TradingView Integration", type="primary", use_container_width=True)
                    
                    if submitted:
                        settings = {
                            'auto_create_trades': auto_create_trades,
                            'default_quantity': default_quantity,
                            'risk_per_trade': risk_per_trade / 100,
                            'notification_enabled': notification_enabled,
                            'symbol_mapping': symbol_mapping
                        }
                        
                        # Setup integration
                        webhook_config = setup_tradingview_webhook(
                            current_user['id'], 
                            selected_account.get('id', 1), 
                            settings
                        )
                        
                        st.success("✅ TradingView integration setup complete!")
                        st.session_state['webhook_config'] = webhook_config
                        st.rerun()
            
            with tab2:
                st.subheader("🔗 Webhook Management")
                st.write("Manage your TradingView webhook URLs and configurations")
                
                # Check if webhook is configured
                if 'webhook_config' in st.session_state:
                    webhook_config = st.session_state['webhook_config']
                    
                    # Display webhook info
                    st.markdown("### 📋 Current Webhook Configuration")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Webhook ID", webhook_config['webhook_id'])
                        st.metric("Status", "🟢 Active" if webhook_config['active'] else "🔴 Inactive")
                    
                    with col2:
                        st.metric("Usage Count", webhook_config['usage_count'])
                        st.metric("Created", webhook_config['created_at'][:10])
                    
                    # Webhook URL
                    st.markdown("### 🔗 Webhook URL")
                    st.code(webhook_config['webhook_url'], language="text")
                    
                    # Copy button
                    if st.button("📋 Copy Webhook URL", use_container_width=True):
                        st.success("✅ Webhook URL copied to clipboard!")
                    
                    # Get instructions
                    st.subheader("📖 Setup Instructions")
                    
                    instructions = get_webhook_instructions(webhook_config)
                    
                    st.markdown("### 📊 TradingView Alert Setup")
                    
                    for step in instructions['setup_steps']:
                        st.write(step)
                    
                    st.markdown("### 📝 Message Format")
                    st.code(json.dumps(instructions['example_message'], indent=2), language="json")
                    
                    st.markdown("### ✅ Supported Actions")
                    st.write(", ".join(instructions['supported_actions']))
                    
                    st.markdown("### 🎯 Supported Symbols")
                    st.write(", ".join(instructions['supported_symbols']))
                    
                else:
                    st.warning("⚠️ No webhook configured. Please setup TradingView integration first.")
                    
                    if st.button("🔧 Setup Integration", type="primary"):
                        st.session_state['current_page'] = "🔗 Broker Integration"
                        st.rerun()
            
            with tab3:
                st.subheader("📈 Test Integration")
                st.write("Test your webhook connection and message format")
                
                if 'webhook_config' in st.session_state:
                    webhook_config = st.session_state['webhook_config']
                    
                    # Test webhook connection
                    st.markdown("### 🧪 Test Webhook Connection")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("🔗 Test Connection", type="primary", use_container_width=True):
                            with st.spinner("Testing webhook connection..."):
                                result = test_webhook_connection(webhook_config['webhook_url'])
                                
                                if result['success']:
                                    st.success("✅ Webhook connection successful!")
                                    st.json(result)
                                else:
                                    st.error(f"❌ Connection failed: {result.get('error', 'Unknown error')}")
                    
                    with col2:
                        st.metric("Webhook URL", webhook_config['webhook_url'][:50] + "...")
                    
                    # Test message format
                    st.markdown("### 📝 Test Message Format")
                    
                    with st.form("test_message"):
                        st.markdown("### 🎯 Create Test Trade")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            test_symbol = st.selectbox(
                                "Symbol",
                                ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD'],
                                help="Test symbol"
                            )
                            
                            test_action = st.selectbox(
                                "Action",
                                ['BUY', 'SELL', 'LONG', 'SHORT'],
                                help="Test action"
                            )
                        
                        with col2:
                            test_price = st.number_input(
                                "Price",
                                min_value=0.0,
                                value=1.0850,
                                step=0.0001,
                                format="%.4f",
                                help="Test price"
                            )
                            
                            test_quantity = st.number_input(
                                "Quantity",
                                min_value=0.01,
                                value=1.0,
                                step=0.01,
                                help="Test quantity"
                            )
                        
                        test_message = st.text_area(
                            "Test Message",
                            value="Test trade from TradingView webhook",
                            help="Test message"
                        )
                        
                        submitted = st.form_submit_button("📤 Send Test Message", type="primary", use_container_width=True)
                        
                        if submitted:
                            # Create test data
                            test_data = {
                                'symbol': test_symbol,
                                'action': test_action,
                                'price': test_price,
                                'quantity': test_quantity,
                                'strategy': 'Test Strategy',
                                'message': test_message,
                                'timeframe': '5m',
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            # Process test trade
                            result = process_webhook_trade(
                                test_data, 
                                current_user['id'], 
                                selected_account.get('id', 1)
                            )
                            
                            if result['success']:
                                st.success(f"✅ Test trade created: {result['message']}")
                                
                                # Add to trades
                                trades.append(result['trade'])
                                save_trades(trades)
                                
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ Test failed: {result['error']}")
                    
                    # Webhook logs
                    st.markdown("### 📊 Webhook Activity")
                    
                    # Show recent webhook activity
                    recent_trades = [t for t in trades if t.get('influence') == 'TradingView']
                    
                    if recent_trades:
                        st.write(f"**Recent TradingView trades: {len(recent_trades)}**")
                        
                        for trade in recent_trades[-5:]:  # Show last 5
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                st.write(f"{trade['symbol']} {trade['side']} @ {trade['entry_price']}")
                            
                            with col2:
                                st.write(trade['date'])
                            
                            with col3:
                                st.write(trade['time'])
                    else:
                        st.info("No TradingView trades yet. Send a test message to see activity.")
                
                else:
                    st.warning("⚠️ No webhook configured. Please setup TradingView integration first.")
            
            with tab4:
                st.subheader("📋 Integration Status")
                st.write("Monitor your broker integration status and activity")
                
                # Get integration status
                integration_status = get_integration_status(
                    current_user['id'], 
                    selected_account.get('id', 1)
                )
                
                if integration_status['enabled']:
                    st.success("✅ TradingView integration is active")
                    
                    # Status metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Status", "🟢 Active")
                    
                    with col2:
                        st.metric("Total Trades", integration_status['total_trades'])
                    
                    with col3:
                        last_activity = integration_status['last_activity']
                        if last_activity:
                            st.metric("Last Activity", last_activity[:10])
                        else:
                            st.metric("Last Activity", "Never")
                    
                    with col4:
                        created_at = integration_status['created_at']
                        st.metric("Created", created_at[:10])
                    
                    # Settings overview
                    st.markdown("### ⚙️ Current Settings")
                    
                    settings = integration_status['settings']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Auto-create trades:** {'✅' if settings['auto_create_trades'] else '❌'}")
                        st.write(f"**Default quantity:** {settings['default_quantity']}")
                    
                    with col2:
                        st.write(f"**Risk per trade:** {settings['risk_per_trade']*100:.1f}%")
                        st.write(f"**Notifications:** {'✅' if settings['notification_enabled'] else '❌'}")
                    
                    # Symbol mapping
                    st.markdown("### 🎯 Symbol Mapping")
                    
                    symbol_mapping = settings['symbol_mapping']
                    if symbol_mapping:
                        mapping_df = pd.DataFrame([
                            {'TradingView': k, 'Journal': v} 
                            for k, v in symbol_mapping.items()
                        ])
                        st.dataframe(mapping_df, use_container_width=True)
                    
                    # Webhook URL
                    st.markdown("### 🔗 Webhook URL")
                    st.code(integration_status['webhook_url'], language="text")
                    
                    # Activity chart
                    if integration_status['total_trades'] > 0:
                        st.markdown("### 📈 Integration Activity")
                        
                        # Show trades created via webhook
                        webhook_trades = [t for t in trades if t.get('influence') == 'TradingView']
                        
                        if webhook_trades:
                            # Create activity chart
                            df = pd.DataFrame(webhook_trades)
                            df['date'] = pd.to_datetime(df['date'])
                            daily_counts = df.groupby('date').size().reset_index(name='trades')
                            
                            st.line_chart(
                                daily_counts.set_index('date')['trades'],
                                height=300
                            )
                    
                else:
                    st.warning("⚠️ TradingView integration not set up")
                    
                    st.markdown("### 🚀 Get Started")
                    st.write("1. Go to 'TradingView Setup' tab")
                    st.write("2. Configure your integration settings")
                    st.write("3. Copy the webhook URL")
                    st.write("4. Setup TradingView alerts")
                    st.write("5. Start receiving automatic trades!")
                    
                    if st.button("🔧 Setup Integration", type="primary"):
                        st.session_state['current_page'] = "🔗 Broker Integration"
                        st.rerun()
    
    # PAGE: Risk Calculator
    if selected_page == "🎯 Risk Calculator":
        st.header("🎯 Risk Calculator & Position Sizing")
        
        if not RISK_CALC_AVAILABLE:
            st.error("❌ Risk Calculator module not available")
        else:
            st.info("💡 Calculate optimal position sizes and manage your trading risk")
            
            tab1, tab2, tab3 = st.tabs(["📐 Position Size Calculator", "📊 Risk Management Report", "🎓 Education"])
            
            with tab1:
                st.subheader("📐 Position Size Calculator")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    calc_account_size = st.number_input("Account Size (€)", min_value=100.0, value=10000.0, step=100.0, key="calc_account")
                    calc_risk_pct = st.slider("Risk per Trade (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key="calc_risk")
                    calc_entry = st.number_input("Entry Price (€)", min_value=0.01, value=100.0, step=0.01, key="calc_entry")
                
                with col2:
                    calc_stop = st.number_input("Stop Loss (€)", min_value=0.01, value=95.0, step=0.01, key="calc_stop")
                    calc_take_profit = st.number_input("Take Profit (€)", min_value=0.01, value=110.0, step=0.01, key="calc_tp")
                
                if st.button("🧮 Calculate Position Size", type="primary", use_container_width=True):
                    position = calculate_position_size(calc_account_size, calc_risk_pct, calc_entry, calc_stop)
                    rr = calculate_risk_reward(calc_entry, calc_stop, calc_take_profit)
                    
                    if position:
                        st.success("✅ Position Size Calculated!")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Shares/Contracts", f"{position['shares']:.2f}")
                        with col2:
                            st.metric("Position Value", f"€{position['position_value']:.2f}")
                        with col3:
                            st.metric("Risk Amount", f"€{position['risk_amount']:.2f}")
                        with col4:
                            st.metric("Leverage", f"{position['leverage']:.2f}x")
                        
                        st.divider()
                        
                        if rr:
                            col1, col2 = st.columns(2)
                            with col1:
                                st.subheader("📊 Risk/Reward Analysis")
                                st.metric("R:R Ratio", f"{rr['ratio']:.2f}:1")
                                st.metric("Risk (€)", f"{rr['risk']:.2f}")
                                st.metric("Reward (€)", f"{rr['reward']:.2f}")
                            
                            with col2:
                                st.subheader("💡 Recommendations")
                                if rr['ratio'] >= 2:
                                    st.success(f"✅ Excellent R:R ratio ({rr['ratio']:.1f}:1)")
                                elif rr['ratio'] >= 1:
                                    st.info(f"⚠️ Acceptable R:R ({rr['ratio']:.1f}:1) - Consider increasing target")
                                else:
                                    st.error(f"❌ Poor R:R ({rr['ratio']:.1f}:1) - Not recommended!")
                                
                                # Calculate required winrate
                                from risk_calculator import calculate_required_winrate
                                req_wr = calculate_required_winrate(rr['ratio'])
                                if req_wr:
                                    st.write(f"**Required Winrate:** {req_wr['required_winrate_pct']:.1f}%")
                        
                        # Profit targets
                        st.subheader("🎯 Profit Targets (R-Multiples)")
                        targets = calculate_profit_targets(calc_entry, position['risk_amount'])
                        if targets:
                            target_df = pd.DataFrame(targets)
                            st.dataframe(target_df, use_container_width=True, hide_index=True)
                    
                    else:
                        st.error("❌ Invalid inputs - check your values")
            
            with tab2:
                st.subheader("📊 Risk Management Report")
                
                if len(trades) < 10:
                    st.warning("📊 Add at least 10 trades to generate Risk Management Report")
                else:
                    # Calculate current balance
                    account_size = 10000.0  # Default
                    current_balance = account_size + sum(t['pnl'] for t in trades)
                    
                    report = get_risk_management_report(trades, account_size, current_balance)
                    
                    if report:
                        # Account Overview
                        st.subheader("💰 Account Overview")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Starting Balance", f"€{report['account_size']:.2f}")
                        with col2:
                            st.metric("Current Balance", f"€{report['current_balance']:.2f}")
                        with col3:
                            st.metric("Total P&L", f"€{report['total_pnl']:.2f}", 
                                     delta=f"{report['roi_pct']:.1f}%")
                        with col4:
                            st.metric("Total Trades", report['total_trades'])
                        
                        st.divider()
                        
                        # Kelly Criterion
                        if report['kelly_criterion']:
                            st.subheader("📈 Kelly Criterion (Optimal Position Sizing)")
                            kelly = report['kelly_criterion']
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Full Kelly", f"{kelly['kelly_pct']:.2f}%")
                                st.metric("Half Kelly (Recommended)", f"{kelly['half_kelly_pct']:.2f}%")
                                st.info(kelly['recommendation'])
                            
                            with col2:
                                st.metric("Win Rate", f"{kelly['win_rate']:.1f}%")
                                st.metric("Avg Win/Loss Ratio", f"{kelly['win_loss_ratio']:.2f}")
                                st.metric("Avg Win", f"€{kelly['avg_win']:.2f}")
                        
                        st.divider()
                        
                        # Expectancy
                        if report['expectancy']:
                            st.subheader("🎯 Trading Expectancy")
                            exp = report['expectancy']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Expectancy", f"€{exp['expectancy']:.2f}")
                            with col2:
                                st.metric("Win Rate", f"{exp['win_pct']:.1f}%")
                            with col3:
                                st.metric("Trades Analyzed", exp['trades_analyzed'])
                            
                            if exp['expectancy'] > 0:
                                st.success(f"✅ {exp['message']}")
                            else:
                                st.error("❌ Negative expectancy - review your strategy!")
                        
                        st.divider()
                        
                        # Risk of Ruin
                        if report['risk_of_ruin']:
                            st.subheader("⚠️ Risk of Ruin Analysis")
                            ruin = report['risk_of_ruin']
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Risk of 50% Drawdown", f"{ruin['ruin_probability_pct']:.4f}%")
                                st.metric("Trades to 50% Loss", ruin['trades_to_50pct_loss'])
                            
                            with col2:
                                if ruin['ruin_probability_pct'] < 0.1:
                                    st.success("✅ Very low risk of ruin")
                                elif ruin['ruin_probability_pct'] < 1:
                                    st.info("⚠️ Acceptable risk level")
                                else:
                                    st.error("❌ High risk of ruin - reduce position size!")
                                st.caption(ruin['warning'])
                        
                        st.divider()
                        
                        # Recommendations
                        st.subheader("💡 Recommendations")
                        for rec in report['recommendations']:
                            if "✅" in rec:
                                st.success(rec)
                            else:
                                st.warning(rec)
            
            with tab3:
                st.subheader("🎓 Risk Management Education")
                
                with st.expander("📐 What is Position Sizing?"):
                    st.markdown("""
                    **Position sizing** determines how many shares/contracts to buy based on:
                    - Your account size
                    - Risk percentage per trade
                    - Distance to stop loss
                    
                    **Example:**
                    - Account: €10,000
                    - Risk: 1% = €100
                    - Entry: €100, Stop: €95 (€5 risk per share)
                    - Position: €100 / €5 = 20 shares
                    """)
                
                with st.expander("📊 What is Risk/Reward Ratio?"):
                    st.markdown("""
                    **Risk/Reward (R:R)** measures potential profit vs. potential loss.
                    
                    **Formula:** R:R = (Take Profit - Entry) / (Entry - Stop Loss)
                    
                    **Guidelines:**
                    - **3:1** or higher = Excellent
                    - **2:1** = Good
                    - **1:1** = Breakeven (need 50% winrate)
                    - **<1:1** = Poor (avoid!)
                    """)
                
                with st.expander("🎯 What is Kelly Criterion?"):
                    st.markdown("""
                    **Kelly Criterion** calculates optimal bet size based on your edge.
                    
                    **Formula:** K% = W - [(1-W) / R]
                    - W = Win rate
                    - R = Average Win / Average Loss
                    
                    **Why Half-Kelly?**
                    - Full Kelly can be aggressive
                    - Half-Kelly reduces volatility
                    - Still captures most growth potential
                    """)
                
                with st.expander("💡 What is Expectancy?"):
                    st.markdown("""
                    **Expectancy** is your average profit/loss per trade.
                    
                    **Formula:** E = (W% × Avg Win) - (L% × Avg Loss)
                    
                    **Example:**
                    - 40% winrate, €200 avg win
                    - 60% loss rate, €100 avg loss
                    - E = (0.4 × 200) - (0.6 × 100) = €20
                    
                    **Positive expectancy = Profitable system**
                    """)
                
                with st.expander("⚠️ What is Risk of Ruin?"):
                    st.markdown("""
                    **Risk of Ruin** is probability of losing a large % of your account.
                    
                    **How to minimize:**
                    - Keep risk per trade low (<2%)
                    - Maintain high winrate or R:R
                    - Never risk more than 5% per day
                    - Use stop losses consistently
                    
                    **Golden Rule:** 
                    Survive first, profit second!
                    """)
    
    # PAGE: Daily Journal
    if selected_page == "📔 Daily Journal":
        st.header("📔 Daily Journal")
        st.info("💡 Write daily notes about your trading mindset, market observations, and lessons learned")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("✍️ Add Daily Note")
            
            with st.form("daily_note_form"):
                note_date = st.date_input("Date", value=datetime.today(), key="note_date")
                note_mood = st.selectbox("Overall Mood", ["Calm", "Anxious", "Confident", "Excited", "Frustrated", "Neutral"], key="note_mood")
                note_energy = st.slider("Energy Level", 1, 5, 3, key="note_energy")
                note_text = st.text_area("Daily Notes", placeholder="What did you observe today? How did you feel? What did you learn?", height=200, key="note_text")
                
                submit_note = st.form_submit_button("💾 Save Daily Note", use_container_width=True)
                
                if submit_note:
                    if note_text:
                        success = add_daily_note(
                            current_user['id'],
                            note_date.strftime('%Y-%m-%d'),
                            note_text,
                            note_mood,
                            note_energy
                        )
                        if success:
                            st.success("✅ Daily note saved!")
                            st.rerun()
                    else:
                        st.error("⚠️ Please write something in your note")
        
        with col2:
            st.subheader("📊 Journal Stats")
            user_notes = load_daily_notes(current_user['id'])
            
            if len(user_notes) > 0:
                st.metric("Total Entries", len(user_notes))
                
                # Count by mood
                moods = [n['mood'] for n in user_notes]
                mood_counts = pd.Series(moods).value_counts()
                st.caption("**Mood Distribution:**")
                for mood, count in mood_counts.items():
                    st.text(f"{mood}: {count}")
            else:
                st.info("No entries yet")
        
        st.divider()
        
        st.subheader("📖 Your Daily Notes")
        
        # Load and display notes
        user_notes = load_daily_notes(current_user['id'])
        
        if len(user_notes) > 0:
            # Sort by date (newest first)
            notes_df = pd.DataFrame(user_notes)
            notes_df['date'] = pd.to_datetime(notes_df['date'])
            notes_df = notes_df.sort_values('date', ascending=False)
            
            # Display notes
            for idx, note in notes_df.iterrows():
                with st.expander(f"📅 {note['date'].strftime('%Y-%m-%d')} - {note['mood']} (Energy: {note['energy_level']}/5)", expanded=False):
                    st.markdown(f"**Note:**")
                    st.write(note['note'])
                    st.caption(f"Created: {note.get('created_at', 'N/A')}")
                    
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_note_{note['date'].strftime('%Y%m%d')}"):
                            delete_daily_note(current_user['id'], note['date'].strftime('%Y-%m-%d'))
                            st.success("Note deleted!")
                            st.rerun()
        else:
            st.info("📝 No daily notes yet. Start journaling to track your trading journey!")
    
    # PAGE: Trade Replay
    if selected_page == "🎬 Trade Replay":
        st.header("🎬 Trade Replay")
        st.info("💡 Replay your trading journey chronologically and see how your strategy evolved")
        
        if len(df) > 0:
            # Replay controls
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                replay_speed = st.slider("Replay Speed (trades per view)", 1, 50, 10, key="replay_speed")
            
            with col2:
                replay_symbol_filter = st.multiselect(
                    "Filter Symbols",
                    all_symbols,
                    default=all_symbols,
                    key="replay_symbols"
                )
            
            with col3:
                st.write("")
                st.write("")
                auto_play = st.checkbox("Auto-play", key="auto_play")
            
            # Filter trades for replay
            replay_df = df[df['symbol'].isin(replay_symbol_filter)].copy()
            replay_df = replay_df.sort_values('date')
            
            if len(replay_df) > 0:
                # Trade counter slider
                max_trades = len(replay_df)
                trades_shown = st.slider(
                    "Progress",
                    0,
                    max_trades,
                    max_trades,
                    key="replay_progress",
                    help=f"Slide to replay your trading journey (Total: {max_trades} trades)"
                )
                
                # Get trades up to selected point
                replay_subset = replay_df.iloc[:trades_shown]
                
                st.divider()
                
                # Show progress metrics
                if trades_shown > 0:
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    replay_metrics = calculate_metrics(replay_subset)
                    
                    with col1:
                        st.metric("Trades Shown", trades_shown)
                    with col2:
                        st.metric("Total P&L", f"{currency}{replay_metrics['total_profit']:.2f}")
                    with col3:
                        st.metric("Win Rate", f"{replay_metrics['win_rate']:.1f}%")
                    with col4:
                        st.metric("Wins", replay_metrics['winning_trades'])
                    with col5:
                        st.metric("Losses", replay_metrics['losing_trades'])
                    
                    st.divider()
                    
                    # Replay charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📈 Equity Curve Evolution")
                        fig, ax = plt.subplots(figsize=(10, 5))
                        replay_chart = replay_subset.copy()
                        replay_chart['cumulative_pnl'] = replay_chart['pnl'].cumsum()
                        
                        ax.plot(replay_chart['date'], replay_chart['cumulative_pnl'], 
                               marker='o', linewidth=2, markersize=4, color='#00ff88')
                        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
                        ax.fill_between(replay_chart['date'], replay_chart['cumulative_pnl'], 0, 
                                       alpha=0.2, color='#00ff88')
                        ax.set_xlabel('Date')
                        ax.set_ylabel(f'Cumulative P&L ({currency})')
                        ax.set_title(f'Your Journey: First {trades_shown} Trades')
                        ax.grid(True, alpha=0.3)
                        plt.xticks(rotation=45)
                        plt.tight_layout()
                        st.pyplot(fig)
                    
                    with col2:
                        st.subheader("📊 Performance Breakdown")
                        # Show win/loss distribution
                        wins = replay_metrics['winning_trades']
                        losses = replay_metrics['losing_trades']
                        
                        if wins + losses > 0:
                            fig, ax = plt.subplots(figsize=(10, 5))
                            ax.pie([wins, losses], labels=['Wins', 'Losses'], 
                                  colors=['#00ff88', '#ff4444'],
                                  autopct='%1.1f%%', startangle=90)
                            ax.set_title(f'Win/Loss Ratio at Trade {trades_shown}')
                            st.pyplot(fig)
                    
                    st.divider()
                    
                    # Trade Timeline Chart - Visual of Entry/Exit points
                    st.subheader("📍 Trade Entry/Exit Timeline")
                    
                    fig, ax = plt.subplots(figsize=(14, 6))
                    
                    # Plot each trade with entry and exit points
                    for idx, row in replay_subset.iterrows():
                        trade_date = row['date']
                        entry_price = row['entry_price']
                        exit_price = row['exit_price']
                        is_win = row['pnl'] > 0
                        
                        # Color based on win/loss
                        color = '#00ff88' if is_win else '#ff4444'
                        marker_entry = '^' if row['side'] == 'Long' else 'v'
                        marker_exit = 'v' if row['side'] == 'Long' else '^'
                        
                        # Plot entry point
                        ax.scatter(trade_date, entry_price, color=color, marker=marker_entry, 
                                 s=150, alpha=0.7, edgecolors='white', linewidth=2, zorder=3)
                        
                        # Plot exit point
                        ax.scatter(trade_date, exit_price, color=color, marker=marker_exit, 
                                 s=150, alpha=0.7, edgecolors='white', linewidth=2, zorder=3)
                        
                        # Draw line connecting entry to exit
                        ax.plot([trade_date, trade_date], [entry_price, exit_price], 
                               color=color, linewidth=2, alpha=0.5, zorder=2)
                        
                        # Add symbol label
                        mid_price = (entry_price + exit_price) / 2
                        ax.text(trade_date, mid_price, row['symbol'], 
                               fontsize=8, ha='right', va='center', 
                               bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.3))
                    
                    ax.set_xlabel('Date', fontsize=12)
                    ax.set_ylabel('Price', fontsize=12)
                    ax.set_title('Entry/Exit Points Timeline\n(▲ = Entry Long/Exit Short | ▼ = Exit Long/Entry Short)', 
                                fontsize=14, fontweight='bold')
                    ax.grid(True, alpha=0.3, linestyle='--')
                    
                    # Legend
                    from matplotlib.patches import Patch
                    legend_elements = [
                        Patch(facecolor='#00ff88', label='Winning Trade'),
                        Patch(facecolor='#ff4444', label='Losing Trade')
                    ]
                    ax.legend(handles=legend_elements, loc='upper left')
                    
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    st.caption("""
                    **How to read:**
                    - **Green** = Winning trades | **Red** = Losing trades
                    - **▲** = Entry (Long) or Exit (Short)
                    - **▼** = Exit (Long) or Entry (Short)
                    - **Line** connects entry to exit for each trade
                    """)
                    
                    st.divider()
                    
                    # Recent trades in replay
                    st.subheader(f"📋 Last {min(10, trades_shown)} Trades")
                    recent_replay = replay_subset.tail(10).sort_values('date', ascending=False)
                    
                    for idx, row in recent_replay.iterrows():
                        col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1, 1.5, 1.5, 2])
                        
                        with col1:
                            st.text(row['date'].strftime('%Y-%m-%d'))
                        with col2:
                            st.text(f"**{row['symbol']}**")
                        with col3:
                            st.text(row['side'])
                        with col4:
                            st.text(f"{currency}{row['entry_price']:.2f}")
                        with col5:
                            pnl_color = "🟢" if row['pnl'] > 0 else "🔴"
                            st.markdown(f"{pnl_color} **{currency}{row['pnl']:.2f}**")
                        with col6:
                            st.text(row['setup'])
                else:
                    st.info("👈 Use the slider to replay your trades")
            else:
                st.info("No trades match your filter selection")
        else:
            st.info("🎬 Add some trades to use Trade Replay!")
    
    # PAGE: Export PDF
    if selected_page == "📄 Export PDF":
        st.header("📄 Export PDF Reports")
        st.warning("⚠️ PDF Export feature is temporarily disabled for maintenance. Will be available soon!")
        st.info("In the meantime, you can export trades as CSV from the Import/Export page")
        
        if False and not PDF_EXPORT_AVAILABLE:
            st.error("❌ PDF Export module not available. Install required packages: matplotlib")
        elif len(trades) < 5:
            st.warning("📊 Add at least 5 trades to generate meaningful reports")
        else:
            tab1, tab2, tab3 = st.tabs(["📅 Weekly Report", "📆 Monthly Report", "🎯 Custom Range"])
            
            with tab1:
                st.subheader("📅 Weekly Report")
                st.write("Generate a comprehensive weekly trading report with:")
                st.markdown("""
                - 📊 Summary statistics (Total P&L, Win Rate, Avg Win/Loss)
                - 📈 Daily P&L breakdown chart
                - 📉 Cumulative equity curve
                - 🎯 Performance by symbol
                - 📋 Detailed trade list
                """)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Week selector
                    today = datetime.now()
                    week_options = []
                    for i in range(12):  # Last 12 weeks
                        week_start = today - timedelta(weeks=i, days=today.weekday())
                        week_end = week_start + timedelta(days=6)
                        week_options.append((week_start, week_end, f"Week {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"))
                    
                    selected_week_idx = st.selectbox(
                        "Select Week",
                        range(len(week_options)),
                        format_func=lambda x: week_options[x][2],
                        key="week_selector"
                    )
                    
                    week_start, week_end, _ = week_options[selected_week_idx]
                
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("📄 Generate Weekly PDF", type="primary", use_container_width=True):
                        with st.spinner("Generating PDF report..."):
                            try:
                                pdf_buffer = generate_weekly_report(
                                    trades, 
                                    week_start, 
                                    week_end, 
                                    current_user.get('display_name', 'Trader')
                                )
                                
                                if pdf_buffer:
                                    st.success("✅ PDF Report Generated!")
                                    st.download_button(
                                        label="⬇️ Download Weekly Report",
                                        data=pdf_buffer,
                                        file_name=f"weekly_report_{week_start.strftime('%Y%m%d')}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                else:
                                    st.warning("⚠️ No trades found for this week")
                            except Exception as e:
                                st.error(f"❌ Error generating PDF: {str(e)}")
            
            with tab2:
                st.subheader("📆 Monthly Report")
                st.write("Generate a detailed monthly trading report including:")
                st.markdown("""
                - 📊 Monthly summary with key metrics
                - 📈 Weekly P&L breakdown
                - 📉 Equity curve with drawdown visualization
                - 🎯 Performance by setup and symbol
                - ⏰ Time-of-day analysis
                - 📊 R-Multiple distribution
                """)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Month selector
                    current_date = datetime.now()
                    months = []
                    for i in range(12):  # Last 12 months
                        date = current_date - timedelta(days=i*30)
                        months.append((date.year, date.month, date.strftime('%B %Y')))
                    
                    selected_month_idx = st.selectbox(
                        "Select Month",
                        range(len(months)),
                        format_func=lambda x: months[x][2],
                        key="month_selector"
                    )
                    
                    year, month, _ = months[selected_month_idx]
                
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("📄 Generate Monthly PDF", type="primary", use_container_width=True):
                        with st.spinner("Generating PDF report..."):
                            try:
                                pdf_buffer = generate_monthly_report(
                                    trades,
                                    month,
                                    year,
                                    current_user.get('display_name', 'Trader')
                                )
                                
                                if pdf_buffer:
                                    st.success("✅ PDF Report Generated!")
                                    st.download_button(
                                        label="⬇️ Download Monthly Report",
                                        data=pdf_buffer,
                                        file_name=f"monthly_report_{year}{month:02d}.pdf",
                                        mime="application/pdf",
                                        use_container_width=True
                                    )
                                else:
                                    st.warning("⚠️ No trades found for this month")
                            except Exception as e:
                                st.error(f"❌ Error generating PDF: {str(e)}")
            
            with tab3:
                st.subheader("🎯 Custom Date Range Report")
                st.write("Generate a report for any custom date range")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    custom_start = st.date_input(
                        "Start Date",
                        value=datetime.now() - timedelta(days=30),
                        key="custom_start"
                    )
                
                with col2:
                    custom_end = st.date_input(
                        "End Date",
                        value=datetime.now(),
                        key="custom_end"
                    )
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    report_title = st.text_input("Report Title", value="Custom Trading Report", key="report_title")
                
                with col2:
                    st.write("")
                    st.write("")
                    if st.button("📄 Generate Custom PDF", type="primary", use_container_width=True):
                        if custom_start > custom_end:
                            st.error("❌ Start date must be before end date")
                        else:
                            with st.spinner("Generating PDF report..."):
                                try:
                                    pdf_buffer = generate_custom_report(
                                        trades,
                                        datetime.combine(custom_start, datetime.min.time()),
                                        datetime.combine(custom_end, datetime.max.time()),
                                        current_user.get('display_name', 'Trader'),
                                        report_title
                                    )
                                    
                                    if pdf_buffer:
                                        st.success("✅ PDF Report Generated!")
                                        st.download_button(
                                            label="⬇️ Download Custom Report",
                                            data=pdf_buffer,
                                            file_name=f"custom_report_{custom_start.strftime('%Y%m%d')}_{custom_end.strftime('%Y%m%d')}.pdf",
                                            mime="application/pdf",
                                            use_container_width=True
                                        )
                                    else:
                                        st.warning("⚠️ No trades found for this date range")
                                except Exception as e:
                                    st.error(f"❌ Error generating PDF: {str(e)}")
                
                # Preview stats for selected range
                if custom_start and custom_end:
                    range_trades = [t for t in trades if custom_start <= datetime.strptime(t['date'], '%Y-%m-%d').date() <= custom_end]
                    
                    if range_trades:
                        st.divider()
                        st.subheader("📊 Preview Stats")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Total Trades", len(range_trades))
                        with col2:
                            total_pnl = sum(t['pnl'] for t in range_trades)
                            st.metric("Total P&L", f"€{total_pnl:.2f}")
                        with col3:
                            wins = len([t for t in range_trades if t['pnl'] > 0])
                            wr = (wins / len(range_trades) * 100) if range_trades else 0
                            st.metric("Win Rate", f"{wr:.1f}%")
                        with col4:
                            trading_days = len(set([t['date'] for t in range_trades]))
                            st.metric("Trading Days", trading_days)
    
    # PAGE: Import/Export CSV
    if selected_page == "📥 Import/Export":
        st.header("📥 Import/Export Trades")
        st.warning("⚠️ Import/Export feature is temporarily disabled for maintenance. Will be available soon!")
        st.info("This feature will support MT4/5, TradingView, Interactive Brokers and more")
        st.info("📊 For now, you can manually add trades using the 'Add Trade' page")
        
        # Feature temporarily disabled due to indentation issues - will be fixed soon
        pass
    
    # NOTE: PDF Export and CSV Import/Export features are temporarily disabled for maintenance
    # They will be re-enabled in the next update after fixing indentation issues
    
    # PAGE: Achievements & Gamification
    if selected_page == "🏆 Achievements":
        st.header("🏆 Achievements & Progress")
        st.warning("⚠️ Gamification feature is temporarily disabled for maintenance. Will be available soon!")
        st.info("💡 This feature will track your trading journey through achievements, levels, and challenges")
        st.info("Features include: streaks, milestones, trading levels, weekly challenges, and more!")
        pass
    
    # Gamification code temporarily removed - will be fixed and re-added in next update
    
    # PAGE: Mentor Mode v2
    if selected_page == "👨‍🏫 Mentor Mode":
        st.header("👨‍🏫 Mentor Mode v2")
        st.warning("⚠️ Mentor Mode feature is temporarily disabled for maintenance. Will be available soon!")
        st.info("💡 This feature will provide feedback, track improvement, and generate personalized suggestions")
        st.info("Features include: trade comments, feedback sessions, AI suggestions, and mentor statistics")
        pass
    
    # Mentor Mode code temporarily removed - will be fixed and re-added in next update

# NO TRADES FALLBACK  
else:
    st.info("🎯 No trades yet. Add your first trade in the 'Add Trade' tab!")

# Footer
st.divider()
st.caption("Trading Journal Pro - Track, Analyze, Improve 📈")
