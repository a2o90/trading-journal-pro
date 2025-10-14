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

class PriceActionAnalyzer:
    """Analyzes price action patterns for weekly calendar view"""
    
    def __init__(self):
        self.price_data_cache = {}
        self.cache_duration = 3600  # 1 hour cache
        
    def get_weekly_price_data(self, symbol: str, weeks_back: int = 12) -> Optional[pd.DataFrame]:
        """Fetch weekly price data for a symbol"""
        try:
            if not YFINANCE_AVAILABLE:
                st.warning("⚠️ yfinance not available. Install with: pip install yfinance")
                return None
            
            # Check cache first
            cache_key = f"{symbol}_{weeks_back}"
            if cache_key in self.price_data_cache:
                cached_data, timestamp = self.price_data_cache[cache_key]
                if datetime.now().timestamp() - timestamp < self.cache_duration:
                    return cached_data
            
            # Fetch data from yfinance
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=weeks_back)
            
            # Get weekly data
            data = ticker.history(start=start_date, end=end_date, interval="1wk")
            
            if data.empty:
                st.warning(f"⚠️ No price data found for {symbol}")
                return None
            
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
            
            # Cache the data
            self.price_data_cache[cache_key] = (weekly_data, datetime.now().timestamp())
            
            return weekly_data
            
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
        
        # Symbol selection
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            symbol = st.text_input("Symbol", placeholder="e.g., AAPL, EURUSD=X, BTC-USD", key="price_action_symbol")
        
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
            return
        
        # Display summary
        self._display_price_summary(symbol, data)
        
        # Display calendar
        self._display_weekly_calendar(data)
        
        # Display charts
        self._display_price_charts(data)
        
        # Display pattern analysis
        self._display_pattern_analysis(data)
    
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
                'Shooting Star': '⭐'
            }
            
            calendar_data.append({
                'Week': f"{week_start} to {week_end}",
                'Pattern': color_map.get(row['Pattern'], '⚪'),
                'Open': f"${row['Open']:.2f}",
                'High': f"${row['High']:.2f}",
                'Low': f"${row['Low']:.2f}",
                'Close': f"${row['Close']:.2f}",
                'Change': f"{row['Weekly_Change_Pct']:+.2f}%",
                'Range': f"${row['Weekly_Range']:.2f}"
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
                "Range": st.column_config.TextColumn("Range", width="small")
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
