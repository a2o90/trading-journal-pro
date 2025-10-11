import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import calendar as cal

# Password Protection
def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == "Topfloor2025":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "🔒 Password", type="password", on_change=password_entered, key="password"
        )
        st.info("Please enter the password to access the Trading Journal")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error
        st.text_input(
            "🔒 Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

if not check_password():
    st.stop()

# ===== APP STARTS HERE (after password check) =====

# Configuration
trades_FILE = "trades.json"
ACCOUNTS_FILE = "accounts.json"
SETTINGS_FILE = "settings.json"
ACCOUNT_SIZE = 10000  # Default account size for R-multiple calculation

def load_settings():
    """Load app settings"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"currency": "$"}
    return {"currency": "$"}

def save_settings(settings):
    """Save app settings"""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def load_accounts():
    """Load accounts from JSON file"""
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return [{"name": "Main Account", "size": 10000, "id": 0}]
    return [{"name": "Main Account", "size": 10000, "id": 0}]

def save_accounts(accounts):
    """Save accounts to JSON file"""
    with open(ACCOUNTS_FILE, 'w') as f:
        json.dump(accounts, f, indent=2)

def load_trades():
    """Load trades from JSON file"""
    if os.path.exists(trades_FILE):
        try:
            with open(trades_FILE, 'r') as f:
                trades = json.load(f)
                # Add unique IDs if they don't exist
                for i, trade in enumerate(trades):
                    if 'id' not in trade:
                        trade['id'] = i
                    # Add default account_id if not present
                    if 'account_id' not in trade:
                        trade['account_id'] = 0
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
                return trades
        except:
            return []
    return []

def save_trades(trades):
    """Save trades to JSON file"""
    with open(trades_FILE, 'w') as f:
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
    """Calculate trading metrics"""
    if len(df) == 0:
        return {
            'total_profit': 0,
            'win_rate': 0,
            'Expectancy': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'avg_win': 0,
            'avg_loss': 0
        }
    
    total_profit = df['pnl'].sum()
    winning_trades = len(df[df['pnl'] > 0])
    losing_trades = len(df[df['pnl'] < 0])
    total_trades = len(df)
    
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate Expectancy
    avg_win = df[df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
    avg_loss = abs(df[df['pnl'] < 0]['pnl'].mean()) if losing_trades > 0 else 0
    
    if total_trades > 0:
        Expectancy = (win_rate/100 * avg_win) - ((1 - win_rate/100) * avg_loss)
    else:
        Expectancy = 0
    
    return {
        'total_profit': total_profit,
        'win_rate': win_rate,
        'Expectancy': Expectancy,
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'avg_win': avg_win,
        'avg_loss': avg_loss
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
st.set_page_config(page_title="Trading Journal Pro", layout="wide", page_icon="📈")

# Custom CSS for better styling
st.markdown("""
<style>
    .profit-positive {
        color: #00ff00;
        font-weight: bold;
    }
    .profit-negative {
        color: #ff4444;
        font-weight: bold;
    }
    .metric-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Trading Journal Pro")

# Force reload data on each run (prevents deleted trades from coming back)
if 'force_reload' in st.session_state:
    del st.session_state['force_reload']

# Load existing trades, accounts, and settings
trades = load_trades()
accounts = load_accounts()
settings = load_settings()
currency = settings.get('currency', '$')

# Sidebar for settings
with st.sidebar:
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
        account_size = selected_account['size']
        
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
            new_account_size = st.number_input("Account Size ($)", value=10000, min_value=100, step=1000)
            
            if st.form_submit_button("Add Account"):
                if new_account_name:
                    new_id = max([acc['id'] for acc in accounts], default=-1) + 1
                    accounts.append({
                        "name": new_account_name,
                        "size": new_account_size,
                        "id": new_id
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
                new_size = st.number_input(
                    "Account Size",
                    value=acc['size'],
                    min_value=100,
                    step=1000,
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

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Add Trade", "📊 All Trades", "📅 Calendar", "💰 Per Symbol", "🧠 Psychology"])

# TAB 1: Add New Trade
with tab1:
    st.header("Add New Trade")
    with st.form("trade_form"):
        st.subheader("📊 Trade Details")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            trade_date = st.date_input("Date", value=datetime.today())
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
                
                # Get next ID
                next_id = max([t.get('id', 0) for t in trades], default=-1) + 1
                
                trade = {
                    'id': next_id,
                    'account_id': selected_account['id'],
                    'account_name': selected_account['name'],
                    'date': trade_date.strftime('%Y-%m-%d'),
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
    
    # TAB 2: All trades
    with tab2:
        st.header("📊 All trades Overview")
        
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
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            color = "normal" if metrics['total_profit'] >= 0 else "inverse"
            st.metric("💰 Total Profit", f"{currency}{metrics['total_profit']:.2f}", delta=None)
        with col2:
            st.metric("📊 Win Rate", f"{metrics['win_rate']:.1f}%")
        with col3:
            st.metric("🎯 Expectancy", f"${metrics['Expectancy']:.2f}")
        with col4:
            st.metric("📈 Total trades", metrics['total_trades'])
        with col5:
            st.metric("✅ Wins", metrics['winning_trades'])
        with col6:
            st.metric("❌ Losses", metrics['losing_trades'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💚 Avg Win", f"{currency}{metrics['avg_win']:.2f}")
        with col2:
            st.metric("❤️ Avg Loss", f"{currency}{metrics['avg_loss']:.2f}")
        
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
                profit_by_symbol = filtered_df.groupby('symbol')['pnl'].sum().sort_values(ascending=False)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                colors = ['#00ff88' if x > 0 else '#ff4444' for x in profit_by_symbol.values]
                profit_by_symbol.plot(kind='bar', ax=ax, color=colors, edgecolor='white', linewidth=1.5)
                ax.axhline(y=0, color='white', linewidth=1)
                ax.set_xlabel('Symbol', fontsize=12)
                ax.set_ylabel('Total P&L ($)', fontsize=12)
                ax.set_title('Profit/Loss by Symbol', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y', linestyle='--')
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
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
    
    # TAB 3: Calendar View
    with tab3:
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
    
    # TAB 4: Per Symbol Analysis
    with tab4:
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

    # TAB 5: Psychology Analysis
    with tab5:
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

else:
    st.info("🎯 No trades yet. Add your first trade in the 'Add Trade' tab!")
    
# Footer
st.divider()
st.caption("Trading Journal Pro - Track, Analyze, Improve 📈")
