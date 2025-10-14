"""
Weekly Price Action Calendar Module
Provides weekly price action analysis and calendar view per symbol
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import json
import os
from typing import Dict, List, Optional, Tuple

# Optional imports for plotting
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Optional imports for price data
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class ManualPriceActionManager:
    """Manages manually added price action data for symbols not available in yfinance"""
    
    def __init__(self):
        self.manual_data_file = "manual_price_action.json"
        
    def load_manual_data(self) -> Dict:
        """Load manually added price action data"""
        if os.path.exists(self.manual_data_file):
            try:
                with open(self.manual_data_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_manual_data(self, data: Dict):
        """Save manually added price action data"""
        try:
            with open(self.manual_data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            st.error(f"Error saving manual data: {e}")
    
    def add_manual_week(self, symbol: str, week_start: str, week_end: str, 
                       open_price: float, high_price: float, low_price: float, 
                       close_price: float, pattern: str, description: str = ""):
        """Add manual price action data for a specific week"""
        manual_data = self.load_manual_data()
        
        if symbol not in manual_data:
            manual_data[symbol] = {}
        
        week_key = f"{week_start}_to_{week_end}"
        
        # Calculate metrics
        weekly_range = high_price - low_price
        weekly_change = close_price - open_price
        weekly_change_pct = (weekly_change / open_price) * 100 if open_price != 0 else 0
        body_size = abs(close_price - open_price)
        upper_wick = high_price - max(open_price, close_price)
        lower_wick = min(open_price, close_price) - low_price
        
        manual_data[symbol][week_key] = {
            'week_start': week_start,
            'week_end': week_end,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'weekly_range': weekly_range,
            'weekly_change': weekly_change,
            'weekly_change_pct': weekly_change_pct,
            'body_size': body_size,
            'upper_wick': upper_wick,
            'lower_wick': lower_wick,
            'pattern': pattern,
            'description': description,
            'added_at': datetime.now().isoformat(),
            'manual': True,
            'type': 'week'
        }
        
        self.save_manual_data(manual_data)
        return True
    
    def add_manual_day(self, symbol: str, date: str, 
                      open_price: float, high_price: float, low_price: float, 
                      close_price: float, pattern: str, description: str = ""):
        """Add manual price action data for a specific day"""
        manual_data = self.load_manual_data()
        
        if symbol not in manual_data:
            manual_data[symbol] = {}
        
        day_key = f"day_{date}"
        
        # Calculate metrics
        daily_range = high_price - low_price
        daily_change = close_price - open_price
        daily_change_pct = (daily_change / open_price) * 100 if open_price != 0 else 0
        body_size = abs(close_price - open_price)
        upper_wick = high_price - max(open_price, close_price)
        lower_wick = min(open_price, close_price) - low_price
        
        manual_data[symbol][day_key] = {
            'date': date,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'daily_range': daily_range,
            'daily_change': daily_change,
            'daily_change_pct': daily_change_pct,
            'body_size': body_size,
            'upper_wick': upper_wick,
            'lower_wick': lower_wick,
            'pattern': pattern,
            'description': description,
            'added_at': datetime.now().isoformat(),
            'manual': True,
            'type': 'day'
        }
        
        self.save_manual_data(manual_data)
        return True
    
    def get_manual_data_for_symbol(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get manual price action data for a symbol as DataFrame"""
        manual_data = self.load_manual_data()
        
        if symbol not in manual_data:
            return None
        
        weeks_data = []
        days_data = []
        
        for key, data in manual_data[symbol].items():
            if data.get('type') == 'week':
                weeks_data.append({
                    'Week_Start': pd.to_datetime(data['week_start']),
                    'Week_End': pd.to_datetime(data['week_end']),
                    'Open': data['open'],
                    'High': data['high'],
                    'Low': data['low'],
                    'Close': data['close'],
                    'Weekly_Range': data['weekly_range'],
                    'Weekly_Change': data['weekly_change'],
                    'Weekly_Change_Pct': data['weekly_change_pct'],
                    'Body_Size': data['body_size'],
                    'Upper_Wick': data['upper_wick'],
                    'Lower_Wick': data['lower_wick'],
                    'Pattern': data['pattern'],
                    'Description': data['description'],
                    'Manual': True,
                    'Type': 'Week'
                })
            elif data.get('type') == 'day':
                days_data.append({
                    'Week_Start': pd.to_datetime(data['date']),
                    'Week_End': pd.to_datetime(data['date']),
                    'Open': data['open'],
                    'High': data['high'],
                    'Low': data['low'],
                    'Close': data['close'],
                    'Weekly_Range': data['daily_range'],
                    'Weekly_Change': data['daily_change'],
                    'Weekly_Change_Pct': data['daily_change_pct'],
                    'Body_Size': data['body_size'],
                    'Upper_Wick': data['upper_wick'],
                    'Lower_Wick': data['lower_wick'],
                    'Pattern': data['pattern'],
                    'Description': data['description'],
                    'Manual': True,
                    'Type': 'Day'
                })
        
        all_data = weeks_data + days_data
        
        if not all_data:
            return None
        
        df = pd.DataFrame(all_data)
        df = df.sort_values('Week_Start')
        df.set_index('Week_Start', inplace=True)
        return df
    
    def delete_manual_entry(self, symbol: str, entry_key: str):
        """Delete a manual price action entry (week or day)"""
        manual_data = self.load_manual_data()
        
        if symbol in manual_data and entry_key in manual_data[symbol]:
            del manual_data[symbol][entry_key]
            
            # Remove symbol if no entries left
            if not manual_data[symbol]:
                del manual_data[symbol]
            
            self.save_manual_data(manual_data)
            return True
        
        return False

class PriceActionAnalyzer:
    """Analyzes price action patterns for weekly calendar view"""
    
    def __init__(self):
        self.price_data_cache = {}
        self.cache_duration = 3600  # 1 hour cache
        self.manual_manager = ManualPriceActionManager()
        
    def get_weekly_price_data(self, symbol: str, weeks_back: int = 12) -> Optional[pd.DataFrame]:
        """Fetch weekly price data for a symbol (combines yfinance and manual data)"""
        try:
            # First try to get manual data
            manual_data = self.manual_manager.get_manual_data_for_symbol(symbol)
            
            # Try to get yfinance data
            yfinance_data = None
            if YFINANCE_AVAILABLE:
                try:
                    # Check cache first
                    cache_key = f"{symbol}_{weeks_back}"
                    if cache_key in self.price_data_cache:
                        cached_data, timestamp = self.price_data_cache[cache_key]
                        if datetime.now().timestamp() - timestamp < self.cache_duration:
                            yfinance_data = cached_data
                    
                    if yfinance_data is None:
                        # Fetch data from yfinance
                        ticker = yf.Ticker(symbol)
                        end_date = datetime.now()
                        start_date = end_date - timedelta(weeks=weeks_back)
                        
                        # Get weekly data
                        data = ticker.history(start=start_date, end=end_date, interval="1wk")
                        
                        if not data.empty:
                            # Process the data
                            weekly_data = data.copy()
                            weekly_data['Week_Start'] = weekly_data.index
                            weekly_data['Week_End'] = weekly_data.index + timedelta(days=6)
                            weekly_data['Symbol'] = symbol
                            
                            # Calculate price action metrics
                            weekly_data['Weekly_Range'] = weekly_data['High'] - weekly_data['Low']
                            weekly_data['Weekly_Change'] = weekly_data['Close'] - weekly_data['Open']
                            weekly_data['Weekly_Change_Pct'] = (weekly_data['Weekly_Change'] / weekly_data['Open']) * 100
                            weekly_data['Body_Size'] = abs(weekly_data['Close'] - weekly_data['Open'])
                            weekly_data['Upper_Wick'] = weekly_data['High'] - weekly_data[['Open', 'Close']].max(axis=1)
                            weekly_data['Lower_Wick'] = weekly_data[['Open', 'Close']].min(axis=1) - weekly_data['Low']
                            
                            # Determine candle pattern
                            weekly_data['Pattern'] = self._classify_candle_pattern(weekly_data)
                            weekly_data['Manual'] = False
                            weekly_data['Description'] = ""
                            
                            yfinance_data = weekly_data
                            
                            # Cache the data
                            self.price_data_cache[cache_key] = (yfinance_data, datetime.now().timestamp())
                            
                except Exception as e:
                    st.warning(f"⚠️ Could not fetch yfinance data for {symbol}: {str(e)}")
            
            # Combine manual and yfinance data
            if manual_data is not None and yfinance_data is not None:
                # Combine both datasets
                combined_data = pd.concat([yfinance_data, manual_data])
                combined_data = combined_data.sort_index()
                combined_data = combined_data.drop_duplicates()
                return combined_data
            elif manual_data is not None:
                return manual_data
            elif yfinance_data is not None:
                return yfinance_data
            else:
                st.warning(f"⚠️ No price data found for {symbol}")
                st.info("💡 Try adding manual data or check the symbol format")
                return None
            
        except Exception as e:
            st.error(f"❌ Error fetching price data for {symbol}: {str(e)}")
            return None
    
    def _classify_candle_pattern(self, data: pd.DataFrame) -> List[str]:
        """Classify weekly candle patterns"""
        patterns = []
        
        for _, row in data.iterrows():
            open_price = row['Open']
            close_price = row['Close']
            high_price = row['High']
            low_price = row['Low']
            
            body_size = abs(close_price - open_price)
            total_range = high_price - low_price
            
            if total_range == 0:
                patterns.append("Doji")
                continue
            
            body_ratio = body_size / total_range
            upper_wick_ratio = row['Upper_Wick'] / total_range
            lower_wick_ratio = row['Lower_Wick'] / total_range
            
            # Classify pattern
            if body_ratio < 0.1:
                patterns.append("Doji")
            elif body_ratio > 0.7:
                if close_price > open_price:
                    patterns.append("Strong Bullish")
                else:
                    patterns.append("Strong Bearish")
            elif upper_wick_ratio > 0.6:
                patterns.append("Shooting Star")
            elif lower_wick_ratio > 0.6:
                patterns.append("Hammer")
            elif close_price > open_price:
                patterns.append("Bullish")
            else:
                patterns.append("Bearish")
        
        return patterns
    
    def get_price_action_summary(self, symbol: str, weeks_back: int = 12) -> Dict:
        """Get price action summary for a symbol"""
        data = self.get_weekly_price_data(symbol, weeks_back)
        
        if data is None or data.empty:
            return {}
        
        summary = {
            'symbol': symbol,
            'total_weeks': len(data),
            'avg_weekly_range': data['Weekly_Range'].mean(),
            'avg_weekly_change_pct': data['Weekly_Change_Pct'].mean(),
            'volatility': data['Weekly_Change_Pct'].std(),
            'bullish_weeks': len(data[data['Weekly_Change'] > 0]),
            'bearish_weeks': len(data[data['Weekly_Change'] < 0]),
            'doji_weeks': len(data[data['Pattern'] == 'Doji']),
            'strong_moves': len(data[data['Pattern'].isin(['Strong Bullish', 'Strong Bearish'])]),
            'current_price': data['Close'].iloc[-1],
            'price_change_12w': ((data['Close'].iloc[-1] - data['Close'].iloc[0]) / data['Close'].iloc[0]) * 100,
            'patterns': data['Pattern'].value_counts().to_dict()
        }
        
        return summary

class WeeklyPriceActionCalendar:
    """Main calendar interface for weekly price action analysis"""
    
    def __init__(self):
        self.analyzer = PriceActionAnalyzer()
        self.calendar_data_file = "weekly_price_action.json"
        self.manual_manager = ManualPriceActionManager()
        
    def load_calendar_data(self) -> Dict:
        """Load saved calendar data"""
        if os.path.exists(self.calendar_data_file):
            try:
                with open(self.calendar_data_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_calendar_data(self, data: Dict):
        """Save calendar data"""
        try:
            with open(self.calendar_data_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            st.error(f"Error saving calendar data: {e}")
    
    def display_calendar_interface(self):
        """Display the main calendar interface"""
        st.header("📅 Weekly Price Action Calendar")
        
        # Create tabs for different functions
        tab1, tab2, tab3 = st.tabs(["📊 View Price Action", "➕ Add Manual Data", "🗑️ Manage Manual Data"])
        
        with tab1:
            self._display_view_interface()
        
        with tab2:
            self._display_add_manual_interface()
        
        with tab3:
            self._display_manage_manual_interface()
    
    def _display_view_interface(self):
        """Display the main viewing interface"""
        # Symbol selection
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            symbol = st.text_input("Symbol", placeholder="e.g., AAPL, EURUSD=X, BTC-USD, MNQ", key="price_action_symbol")
        
        with col2:
            weeks_back = st.selectbox("Weeks Back", [8, 12, 16, 24, 52], index=1)
        
        with col3:
            if st.button("🔄 Refresh Data", type="primary"):
                if symbol:
                    st.session_state['refresh_price_data'] = True
        
        if not symbol:
            st.info("👆 Enter a symbol to view weekly price action calendar")
            return
        
        # Fetch and display data
        with st.spinner(f"Fetching weekly price action data for {symbol}..."):
            data = self.analyzer.get_weekly_price_data(symbol, weeks_back)
        
        if data is None or data.empty:
            st.error(f"❌ Could not fetch data for {symbol}. Please check the symbol format.")
            st.info("💡 Try formats like: AAPL, EURUSD=X, BTC-USD, ^GSPC")
            st.info("💡 Or add manual data using the 'Add Manual Data' tab")
            return
        
        # Display summary
        self._display_price_summary(symbol, data)
        
        # Display calendar
        self._display_weekly_calendar(data)
        
        # Display charts
        self._display_price_charts(data)
        
        # Display pattern analysis
        self._display_pattern_analysis(data)
    
    def _display_add_manual_interface(self):
        """Display interface for adding manual price action data"""
        st.subheader("➕ Add Manual Price Action Data")
        st.info("💡 Use this to add price action data for symbols not available in yfinance (like MNQ)")
        
        # Choose between week or day
        data_type = st.radio("Data Type", ["Week", "Day"], horizontal=True, key="manual_data_type")
        
        with st.form("add_manual_data"):
            col1, col2 = st.columns(2)
            
            with col1:
                symbol = st.text_input("Symbol", placeholder="e.g., MNQ, ES, YM", key="manual_symbol")
                
                if data_type == "Week":
                    week_start = st.date_input("Week Start Date", key="manual_week_start")
                    week_end = st.date_input("Week End Date", key="manual_week_end")
                else:  # Day
                    date = st.date_input("Date", key="manual_date")
            
            with col2:
                open_price = st.number_input("Open Price", min_value=0.0, step=0.01, format="%.2f", key="manual_open")
                high_price = st.number_input("High Price", min_value=0.0, step=0.01, format="%.2f", key="manual_high")
                low_price = st.number_input("Low Price", min_value=0.0, step=0.01, format="%.2f", key="manual_low")
                close_price = st.number_input("Close Price", min_value=0.0, step=0.01, format="%.2f", key="manual_close")
            
            pattern = st.selectbox("Pattern", [
                "Strong Bullish", "Bullish", "Doji", "Bearish", "Strong Bearish", 
                "Hammer", "Shooting Star", "Spinning Top", "Marubozu", "Other"
            ], key="manual_pattern")
            
            description = st.text_area("Description/Analysis", 
                                     placeholder="Describe the price action, key levels, market sentiment, etc.", 
                                     key="manual_description")
            
            if st.form_submit_button(f"➕ Add Manual {data_type}", type="primary"):
                if symbol and open_price and high_price and low_price and close_price:
                    if data_type == "Week":
                        success = self.manual_manager.add_manual_week(
                            symbol, 
                            week_start.strftime('%Y-%m-%d'), 
                            week_end.strftime('%Y-%m-%d'),
                            open_price, high_price, low_price, close_price,
                            pattern, description
                        )
                    else:  # Day
                        success = self.manual_manager.add_manual_day(
                            symbol, 
                            date.strftime('%Y-%m-%d'),
                            open_price, high_price, low_price, close_price,
                            pattern, description
                        )
                    
                    if success:
                        st.success(f"✅ Added manual {data_type.lower()} data for {symbol}")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add manual data")
                else:
                    st.error("❌ Please fill in all required fields")
    
    def _display_manage_manual_interface(self):
        """Display interface for managing manual price action data"""
        st.subheader("🗑️ Manage Manual Price Action Data")
        
        manual_data = self.manual_manager.load_manual_data()
        
        if not manual_data:
            st.info("📝 No manual price action data found")
            return
        
        for symbol, entries in manual_data.items():
            # Count weeks and days
            weeks_count = sum(1 for entry in entries.values() if entry.get('type') == 'week')
            days_count = sum(1 for entry in entries.values() if entry.get('type') == 'day')
            
            with st.expander(f"📊 {symbol} ({weeks_count} weeks, {days_count} days)", expanded=False):
                for entry_key, entry_data in entries.items():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        if entry_data.get('type') == 'week':
                            st.write(f"**Week:** {entry_data['week_start']} to {entry_data['week_end']}")
                            st.write(f"**Range:** {entry_data['weekly_range']:.2f}")
                            st.write(f"**Change:** {entry_data['weekly_change_pct']:+.2f}%")
                        else:  # day
                            st.write(f"**Day:** {entry_data['date']}")
                            st.write(f"**Range:** {entry_data['daily_range']:.2f}")
                            st.write(f"**Change:** {entry_data['daily_change_pct']:+.2f}%")
                        
                        st.write(f"**OHLC:** {entry_data['open']:.2f} / {entry_data['high']:.2f} / {entry_data['low']:.2f} / {entry_data['close']:.2f}")
                        st.write(f"**Pattern:** {entry_data['pattern']}")
                        if entry_data['description']:
                            st.write(f"**Description:** {entry_data['description']}")
                    
                    with col2:
                        st.write(f"**Type:** {entry_data.get('type', 'Unknown').title()}")
                        st.write(f"**Added:** {entry_data['added_at'][:10]}")
                    
                    with col3:
                        if st.button("🗑️ Delete", key=f"del_{symbol}_{entry_key}"):
                            if self.manual_manager.delete_manual_entry(symbol, entry_key):
                                st.success("✅ Entry deleted")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete entry")
    
    def _display_price_summary(self, symbol: str, data: pd.DataFrame):
        """Display price action summary"""
        st.subheader(f"📊 {symbol} Weekly Summary")
        
        summary = self.analyzer.get_price_action_summary(symbol, len(data))
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Price",
                f"${data['Close'].iloc[-1]:.2f}",
                f"{summary['price_change_12w']:+.2f}%"
            )
        
        with col2:
            st.metric(
                "Avg Weekly Range",
                f"${summary['avg_weekly_range']:.2f}",
                f"±{summary['volatility']:.2f}%"
            )
        
        with col3:
            st.metric(
                "Bullish Weeks",
                f"{summary['bullish_weeks']}/{summary['total_weeks']}",
                f"{summary['bullish_weeks']/summary['total_weeks']*100:.1f}%"
            )
        
        with col4:
            st.metric(
                "Strong Moves",
                summary['strong_moves'],
                f"{summary['doji_weeks']} Doji"
            )
    
    def _display_weekly_calendar(self, data: pd.DataFrame):
        """Display weekly calendar grid"""
        st.subheader("📅 Weekly Calendar View")
        
        # Create calendar grid
        calendar_data = []
        
        for _, row in data.iterrows():
            week_start = row['Week_Start'].strftime('%Y-%m-%d')
            week_end = row['Week_End'].strftime('%Y-%m-%d')
            
            # Determine color based on pattern
            color_map = {
                'Strong Bullish': '🟢',
                'Strong Bearish': '🔴',
                'Bullish': '🟡',
                'Bearish': '🟠',
                'Doji': '⚪',
                'Hammer': '🔨',
                'Shooting Star': '⭐',
                'Spinning Top': '🌀',
                'Marubozu': '⬛',
                'Other': '❓'
            }
            
            # Add manual indicator and type indicator
            manual_indicator = "📝" if row.get('Manual', False) else ""
            type_indicator = "📅" if row.get('Type') == 'Day' else ""
            pattern_display = f"{manual_indicator}{type_indicator}{color_map.get(row['Pattern'], '⚪')}"
            
            # Format date range based on type
            if row.get('Type') == 'Day':
                date_display = f"{week_start} (Day)"
            else:
                date_display = f"{week_start} to {week_end}"
            
            calendar_data.append({
                'Week': date_display,
                'Pattern': pattern_display,
                'Open': f"${row['Open']:.2f}",
                'High': f"${row['High']:.2f}",
                'Low': f"${row['Low']:.2f}",
                'Close': f"${row['Close']:.2f}",
                'Change': f"{row['Weekly_Change_Pct']:+.2f}%",
                'Range': f"${row['Weekly_Range']:.2f}",
                'Description': row.get('Description', '')[:50] + '...' if len(row.get('Description', '')) > 50 else row.get('Description', '')
            })
        
        calendar_df = pd.DataFrame(calendar_data)
        calendar_df = calendar_df.sort_values('Week', ascending=False)
        
        st.dataframe(
            calendar_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Week": st.column_config.TextColumn("Week", width="medium"),
                "Pattern": st.column_config.TextColumn("Pattern", width="small"),
                "Open": st.column_config.TextColumn("Open", width="small"),
                "High": st.column_config.TextColumn("High", width="small"),
                "Low": st.column_config.TextColumn("Low", width="small"),
                "Close": st.column_config.TextColumn("Close", width="small"),
                "Change": st.column_config.TextColumn("Change %", width="small"),
                "Range": st.column_config.TextColumn("Range", width="small"),
                "Description": st.column_config.TextColumn("Description", width="large")
            }
        )
    
    def _display_price_charts(self, data: pd.DataFrame):
        """Display price action charts"""
        st.subheader("📈 Price Action Charts")
        
        if not PLOTLY_AVAILABLE:
            st.warning("⚠️ Plotly not available. Install with: pip install plotly")
            st.info("📊 Charts will be displayed when plotly is installed")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Weekly candlestick chart
            fig = go.Figure(data=go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Weekly Candles"
            ))
            
            fig.update_layout(
                title="Weekly Candlestick Chart",
                xaxis_title="Date",
                yaxis_title="Price",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Weekly change percentage
            fig = px.bar(
                x=data.index,
                y=data['Weekly_Change_Pct'],
                title="Weekly Change Percentage",
                color=data['Weekly_Change_Pct'],
                color_continuous_scale=['red', 'white', 'green']
            )
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Change %",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _display_pattern_analysis(self, data: pd.DataFrame):
        """Display pattern analysis"""
        st.subheader("🔍 Pattern Analysis")
        
        if not PLOTLY_AVAILABLE:
            st.warning("⚠️ Plotly not available. Install with: pip install plotly")
            st.info("📊 Charts will be displayed when plotly is installed")
            
            # Show pattern data in table format instead
            pattern_counts = data['Pattern'].value_counts()
            st.write("**Pattern Distribution:**")
            st.dataframe(pattern_counts.to_frame('Count'), use_container_width=True)
            
            # Weekly range statistics
            st.write("**Weekly Range Statistics:**")
            range_stats = data['Weekly_Range'].describe()
            st.dataframe(range_stats.to_frame('Value'), use_container_width=True)
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pattern distribution
            pattern_counts = data['Pattern'].value_counts()
            
            fig = px.pie(
                values=pattern_counts.values,
                names=pattern_counts.index,
                title="Pattern Distribution"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Weekly range analysis
            fig = px.box(
                y=data['Weekly_Range'],
                title="Weekly Range Distribution",
                labels={'y': 'Weekly Range ($)'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Pattern insights
        st.subheader("💡 Pattern Insights")
        
        insights = []
        
        # Most common pattern
        most_common = data['Pattern'].mode()[0]
        insights.append(f"**Most common pattern:** {most_common} ({data['Pattern'].value_counts()[most_common]} weeks)")
        
        # Volatility analysis
        avg_range = data['Weekly_Range'].mean()
        high_vol_weeks = len(data[data['Weekly_Range'] > avg_range * 1.5])
        insights.append(f"**High volatility weeks:** {high_vol_weeks} out of {len(data)} weeks")
        
        # Trend analysis
        bullish_weeks = len(data[data['Weekly_Change'] > 0])
        bearish_weeks = len(data[data['Weekly_Change'] < 0])
        insights.append(f"**Trend bias:** {bullish_weeks} bullish vs {bearish_weeks} bearish weeks")
        
        for insight in insights:
            st.markdown(f"• {insight}")

# Global instance
price_action_calendar = WeeklyPriceActionCalendar()

# Convenience functions
def display_weekly_price_action_calendar():
    """Display the weekly price action calendar interface"""
    price_action_calendar.display_calendar_interface()

def get_price_action_summary(symbol: str, weeks_back: int = 12) -> Dict:
    """Get price action summary for a symbol"""
    analyzer = PriceActionAnalyzer()
    return analyzer.get_price_action_summary(symbol, weeks_back)

def get_weekly_price_data(symbol: str, weeks_back: int = 12) -> Optional[pd.DataFrame]:
    """Get weekly price data for a symbol"""
    analyzer = PriceActionAnalyzer()
    return analyzer.get_weekly_price_data(symbol, weeks_back)
