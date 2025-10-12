#!/usr/bin/env python3
"""
AI Trading Assistant Module
Provides intelligent insights, daily summaries, and strategy optimization
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import json

class TradingAIAssistant:
    def __init__(self):
        self.insights_cache = {}
        
    def generate_daily_summary(self, trades, date=None):
        """Generate AI-powered daily trading summary"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Filter trades for the specific date
        daily_trades = [t for t in trades if t.get('date') == date]
        
        if not daily_trades:
            return {
                'date': date,
                'summary': "No trades executed today.",
                'insights': [],
                'recommendations': [],
                'stats': {}
            }
        
        # Calculate basic stats
        total_pnl = sum(t.get('pnl', 0) for t in daily_trades)
        win_count = len([t for t in daily_trades if t.get('pnl', 0) > 0])
        loss_count = len([t for t in daily_trades if t.get('pnl', 0) < 0])
        win_rate = (win_count / len(daily_trades) * 100) if daily_trades else 0
        
        # Generate insights
        insights = self._generate_daily_insights(daily_trades)
        
        # Generate recommendations
        recommendations = self._generate_daily_recommendations(daily_trades, total_pnl, win_rate)
        
        # Create summary
        summary = self._create_daily_summary_text(daily_trades, total_pnl, win_rate, win_count, loss_count)
        
        return {
            'date': date,
            'summary': summary,
            'insights': insights,
            'recommendations': recommendations,
            'stats': {
                'total_trades': len(daily_trades),
                'total_pnl': total_pnl,
                'win_rate': win_rate,
                'win_count': win_count,
                'loss_count': loss_count,
                'best_trade': max(daily_trades, key=lambda x: x.get('pnl', 0))['pnl'] if daily_trades else 0,
                'worst_trade': min(daily_trades, key=lambda x: x.get('pnl', 0))['pnl'] if daily_trades else 0
            }
        }
    
    def _generate_daily_insights(self, trades):
        """Generate AI insights for daily trades"""
        insights = []
        
        if not trades:
            return insights
        
        # Symbol analysis
        symbols = [t.get('symbol', 'Unknown') for t in trades]
        symbol_counts = defaultdict(int)
        for symbol in symbols:
            symbol_counts[symbol] += 1
        
        most_traded = max(symbol_counts.items(), key=lambda x: x[1]) if symbol_counts else None
        if most_traded and most_traded[1] > 1:
            insights.append(f"🎯 **Focus Symbol**: You traded {most_traded[0]} {most_traded[1]} times today - showing strong conviction.")
        
        # Psychology analysis
        moods = [t.get('mood', 'Unknown') for t in trades if t.get('mood')]
        if moods:
            mood_counts = defaultdict(int)
            for mood in moods:
                mood_counts[mood] += 1
            dominant_mood = max(mood_counts.items(), key=lambda x: x[1])
            insights.append(f"🧠 **Mental State**: Your dominant mood was '{dominant_mood[0]}' - {dominant_mood[1]} trades.")
        
        # Time analysis
        times = [t.get('time', '') for t in trades if t.get('time')]
        if times:
            morning_trades = len([t for t in times if t and int(t.split(':')[0]) < 12])
            afternoon_trades = len(times) - morning_trades
            if morning_trades > afternoon_trades:
                insights.append("🌅 **Trading Pattern**: You're more active in the morning - consider if this aligns with market volatility.")
            elif afternoon_trades > morning_trades:
                insights.append("🌆 **Trading Pattern**: You prefer afternoon trading - good for catching end-of-day moves.")
        
        # Performance analysis
        pnl_values = [t.get('pnl', 0) for t in trades]
        if pnl_values:
            avg_pnl = sum(pnl_values) / len(pnl_values)
            if avg_pnl > 0:
                insights.append(f"📈 **Positive Momentum**: Average P&L per trade was €{avg_pnl:.2f} - maintaining profitability.")
            else:
                insights.append(f"📉 **Caution**: Average P&L per trade was €{avg_pnl:.2f} - consider reviewing strategy.")
        
        return insights
    
    def _generate_daily_recommendations(self, trades, total_pnl, win_rate):
        """Generate AI recommendations based on daily performance"""
        recommendations = []
        
        if not trades:
            recommendations.append("💡 **Action**: Consider adding some trades to build momentum and test your strategy.")
            return recommendations
        
        # Risk management recommendations
        if len(trades) > 5:
            recommendations.append("⚠️ **Risk Management**: You made many trades today - ensure you're not overtrading.")
        
        if total_pnl < 0:
            recommendations.append("🛑 **Stop Loss**: Consider implementing stricter stop losses to limit daily losses.")
        
        # Psychology recommendations
        moods = [t.get('mood', '') for t in trades if t.get('mood')]
        if 'Frustrated' in moods or 'Anxious' in moods:
            recommendations.append("🧘 **Mental Health**: Take a break if feeling frustrated - emotional trading leads to losses.")
        
        # Strategy recommendations
        if win_rate < 30:
            recommendations.append("📚 **Education**: Low win rate suggests strategy review needed - consider paper trading.")
        elif win_rate > 70:
            recommendations.append("🚀 **Scale Up**: High win rate - consider increasing position sizes gradually.")
        
        # Time-based recommendations
        times = [t.get('time', '') for t in trades if t.get('time')]
        if times:
            late_trades = len([t for t in times if t and int(t.split(':')[0]) > 20])
            if late_trades > 0:
                recommendations.append("🌙 **Sleep**: Late night trading can affect decision-making - prioritize rest.")
        
        return recommendations
    
    def _create_daily_summary_text(self, trades, total_pnl, win_rate, win_count, loss_count):
        """Create human-readable daily summary"""
        if not trades:
            return "No trading activity today."
        
        summary_parts = []
        
        # Opening
        if total_pnl > 0:
            summary_parts.append(f"🎉 **Great day!** You made €{total_pnl:.2f} profit across {len(trades)} trades.")
        elif total_pnl < 0:
            summary_parts.append(f"📉 **Challenging day** with €{abs(total_pnl):.2f} loss across {len(trades)} trades.")
        else:
            summary_parts.append(f"⚖️ **Break-even day** with {len(trades)} trades.")
        
        # Performance details
        summary_parts.append(f"**Performance**: {win_count} wins, {loss_count} losses ({win_rate:.1f}% win rate)")
        
        # Best/worst trade
        if trades:
            best_trade = max(trades, key=lambda x: x.get('pnl', 0))
            worst_trade = min(trades, key=lambda x: x.get('pnl', 0))
            
            if best_trade['pnl'] > 0:
                summary_parts.append(f"**Best trade**: {best_trade.get('symbol', 'Unknown')} (+€{best_trade['pnl']:.2f})")
            if worst_trade['pnl'] < 0:
                summary_parts.append(f"**Worst trade**: {worst_trade.get('symbol', 'Unknown')} (€{worst_trade['pnl']:.2f})")
        
        return " ".join(summary_parts)
    
    def analyze_trading_patterns(self, trades, days=30):
        """Analyze trading patterns over specified period"""
        if not trades:
            return {}
        
        # Filter trades for the period
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        recent_trades = [t for t in trades if t.get('date', '') >= cutoff_date]
        
        if not recent_trades:
            return {'error': 'No trades in the specified period'}
        
        patterns = {}
        
        # Day of week analysis
        dow_performance = defaultdict(list)
        for trade in recent_trades:
            try:
                date_obj = datetime.strptime(trade['date'], '%Y-%m-%d')
                dow = date_obj.strftime('%A')
                dow_performance[dow].append(trade.get('pnl', 0))
            except:
                continue
        
        patterns['day_of_week'] = {}
        for day, pnls in dow_performance.items():
            patterns['day_of_week'][day] = {
                'total_pnl': sum(pnls),
                'avg_pnl': sum(pnls) / len(pnls),
                'trade_count': len(pnls),
                'win_rate': len([p for p in pnls if p > 0]) / len(pnls) * 100
            }
        
        # Symbol performance
        symbol_performance = defaultdict(list)
        for trade in recent_trades:
            symbol = trade.get('symbol', 'Unknown')
            symbol_performance[symbol].append(trade.get('pnl', 0))
        
        patterns['symbols'] = {}
        for symbol, pnls in symbol_performance.items():
            patterns['symbols'][symbol] = {
                'total_pnl': sum(pnls),
                'avg_pnl': sum(pnls) / len(pnls),
                'trade_count': len(pnls),
                'win_rate': len([p for p in pnls if p > 0]) / len(pnls) * 100
            }
        
        # Psychology patterns
        mood_performance = defaultdict(list)
        for trade in recent_trades:
            mood = trade.get('mood', 'Unknown')
            if mood != 'Unknown':
                mood_performance[mood].append(trade.get('pnl', 0))
        
        patterns['psychology'] = {}
        for mood, pnls in mood_performance.items():
            patterns['psychology'][mood] = {
                'total_pnl': sum(pnls),
                'avg_pnl': sum(pnls) / len(pnls),
                'trade_count': len(pnls),
                'win_rate': len([p for p in pnls if p > 0]) / len(pnls) * 100
            }
        
        return patterns
    
    def generate_strategy_suggestions(self, trades, days=30):
        """Generate AI-powered strategy optimization suggestions"""
        patterns = self.analyze_trading_patterns(trades, days)
        
        if 'error' in patterns:
            return [{'type': 'error', 'message': patterns['error']}]
        
        suggestions = []
        
        # Day of week suggestions
        if 'day_of_week' in patterns:
            best_day = max(patterns['day_of_week'].items(), key=lambda x: x[1]['total_pnl'])
            worst_day = min(patterns['day_of_week'].items(), key=lambda x: x[1]['total_pnl'])
            
            if best_day[1]['total_pnl'] > 0:
                suggestions.append({
                    'type': 'optimization',
                    'title': f"Focus on {best_day[0]}",
                    'message': f"Your best performing day is {best_day[0]} with €{best_day[1]['total_pnl']:.2f} profit. Consider allocating more capital on this day.",
                    'priority': 'medium'
                })
            
            if worst_day[1]['total_pnl'] < 0:
                suggestions.append({
                    'type': 'warning',
                    'title': f"Avoid {worst_day[0]}",
                    'message': f"You consistently lose money on {worst_day[0]} (€{worst_day[1]['total_pnl']:.2f}). Consider taking this day off.",
                    'priority': 'high'
                })
        
        # Symbol suggestions
        if 'symbols' in patterns:
            best_symbol = max(patterns['symbols'].items(), key=lambda x: x[1]['total_pnl'])
            worst_symbol = min(patterns['symbols'].items(), key=lambda x: x[1]['total_pnl'])
            
            if best_symbol[1]['total_pnl'] > 0 and best_symbol[1]['trade_count'] >= 3:
                suggestions.append({
                    'type': 'optimization',
                    'title': f"Scale up {best_symbol[0]}",
                    'message': f"{best_symbol[0]} is your most profitable symbol (€{best_symbol[1]['total_pnl']:.2f}). Consider increasing position sizes.",
                    'priority': 'medium'
                })
            
            if worst_symbol[1]['total_pnl'] < 0 and worst_symbol[1]['trade_count'] >= 3:
                suggestions.append({
                    'type': 'warning',
                    'title': f"Review {worst_symbol[0]} strategy",
                    'message': f"{worst_symbol[0]} is consistently unprofitable (€{worst_symbol[1]['total_pnl']:.2f}). Consider avoiding or revising your approach.",
                    'priority': 'high'
                })
        
        # Psychology suggestions
        if 'psychology' in patterns:
            best_mood = max(patterns['psychology'].items(), key=lambda x: x[1]['total_pnl'])
            worst_mood = min(patterns['psychology'].items(), key=lambda x: x[1]['total_pnl'])
            
            if best_mood[1]['total_pnl'] > 0:
                suggestions.append({
                    'type': 'psychology',
                    'title': f"Leverage {best_mood[0]} state",
                    'message': f"You perform best when feeling '{best_mood[0]}' (€{best_mood[1]['total_pnl']:.2f}). Try to cultivate this mindset.",
                    'priority': 'low'
                })
            
            if worst_mood[1]['total_pnl'] < 0:
                suggestions.append({
                    'type': 'psychology',
                    'title': f"Avoid trading when {worst_mood[0]}",
                    'message': f"You lose money when feeling '{worst_mood[0]}' (€{worst_mood[1]['total_pnl']:.2f}). Take breaks during these times.",
                    'priority': 'high'
                })
        
        return suggestions
    
    def get_weekly_report(self, trades):
        """Generate comprehensive weekly AI report"""
        # Get trades from last 7 days
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        weekly_trades = [t for t in trades if t.get('date', '') >= week_ago]
        
        if not weekly_trades:
            return {
                'summary': 'No trades this week.',
                'insights': [],
                'recommendations': [],
                'stats': {}
            }
        
        # Calculate weekly stats
        total_pnl = sum(t.get('pnl', 0) for t in weekly_trades)
        win_count = len([t for t in weekly_trades if t.get('pnl', 0) > 0])
        total_trades = len(weekly_trades)
        win_rate = (win_count / total_trades * 100) if total_trades else 0
        
        # Generate insights and recommendations
        insights = self._generate_weekly_insights(weekly_trades)
        recommendations = self.generate_strategy_suggestions(trades, days=7)
        
        return {
            'summary': f"Weekly Performance: €{total_pnl:.2f} across {total_trades} trades ({win_rate:.1f}% win rate)",
            'insights': insights,
            'recommendations': recommendations,
            'stats': {
                'total_pnl': total_pnl,
                'total_trades': total_trades,
                'win_rate': win_rate,
                'win_count': win_count,
                'loss_count': total_trades - win_count
            }
        }
    
    def _generate_weekly_insights(self, trades):
        """Generate weekly insights"""
        insights = []
        
        if not trades:
            return insights
        
        # Consistency analysis
        daily_pnl = defaultdict(float)
        for trade in trades:
            daily_pnl[trade.get('date', '')] += trade.get('pnl', 0)
        
        profitable_days = len([pnl for pnl in daily_pnl.values() if pnl > 0])
        total_days = len(daily_pnl)
        
        if profitable_days / total_days > 0.6:
            insights.append("🎯 **Consistency**: You're profitable on most trading days - excellent discipline!")
        elif profitable_days / total_days < 0.3:
            insights.append("⚠️ **Consistency**: You're struggling with consistency - consider reviewing your strategy.")
        
        # Volume analysis
        if len(trades) > 20:
            insights.append("📊 **High Volume**: You're very active this week - ensure quality over quantity.")
        elif len(trades) < 5:
            insights.append("🐌 **Low Volume**: Few trades this week - consider if you're missing opportunities.")
        
        return insights

# Global instance
ai_assistant = TradingAIAssistant()

# Convenience functions
def get_daily_summary(trades, date=None):
    """Get AI-generated daily summary"""
    return ai_assistant.generate_daily_summary(trades, date)

def analyze_patterns(trades, days=30):
    """Analyze trading patterns"""
    return ai_assistant.analyze_trading_patterns(trades, days)

def get_strategy_suggestions(trades, days=30):
    """Get AI strategy suggestions"""
    return ai_assistant.generate_strategy_suggestions(trades, days)

def get_weekly_report(trades):
    """Get weekly AI report"""
    return ai_assistant.get_weekly_report(trades)
