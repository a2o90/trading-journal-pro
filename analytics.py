"""
Advanced Analytics Module for Trading Journal Pro
Provides deep insights, correlations, and AI-assisted pattern detection
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

# ===== PSYCHOLOGY CORRELATION ANALYSIS =====

def analyze_psychology_performance(trades):
    """Analyze correlation between psychological factors and trade performance"""
    if not trades or len(trades) < 10:
        return None
    
    df = pd.DataFrame(trades)
    
    # Filter out trades without psychology data
    df = df[df['mood'].notna() & df['focus_level'].notna()]
    
    if len(df) < 10:
        return None
    
    insights = {
        'mood_analysis': {},
        'focus_analysis': {},
        'stress_analysis': {},
        'sleep_analysis': {},
        'confidence_analysis': {}
    }
    
    # Mood correlation
    if 'mood' in df.columns:
        mood_groups = df.groupby('mood').agg({
            'pnl': ['mean', 'sum', 'count'],
        }).round(2)
        
        best_mood = mood_groups['pnl']['mean'].idxmax()
        worst_mood = mood_groups['pnl']['mean'].idxmin()
        
        insights['mood_analysis'] = {
            'best_mood': best_mood,
            'best_mood_avg_pnl': float(mood_groups.loc[best_mood, ('pnl', 'mean')]),
            'worst_mood': worst_mood,
            'worst_mood_avg_pnl': float(mood_groups.loc[worst_mood, ('pnl', 'mean')]),
            'mood_groups': mood_groups.to_dict()
        }
    
    # Focus level correlation
    if 'focus_level' in df.columns:
        focus_corr = df[['focus_level', 'pnl']].corr().iloc[0, 1]
        high_focus = df[df['focus_level'] >= 4]['pnl'].mean()
        low_focus = df[df['focus_level'] <= 2]['pnl'].mean()
        
        insights['focus_analysis'] = {
            'correlation': round(float(focus_corr), 3),
            'high_focus_avg': round(float(high_focus), 2),
            'low_focus_avg': round(float(low_focus), 2),
            'difference': round(float(high_focus - low_focus), 2)
        }
    
    # Stress level correlation
    if 'stress_level' in df.columns:
        stress_corr = df[['stress_level', 'pnl']].corr().iloc[0, 1]
        high_stress = df[df['stress_level'] >= 4]['pnl'].mean()
        low_stress = df[df['stress_level'] <= 2]['pnl'].mean()
        
        insights['stress_analysis'] = {
            'correlation': round(float(stress_corr), 3),
            'high_stress_avg': round(float(high_stress), 2),
            'low_stress_avg': round(float(low_stress), 2),
            'difference': round(float(low_stress - high_stress), 2)
        }
    
    # Sleep quality correlation
    if 'sleep_quality' in df.columns:
        sleep_corr = df[['sleep_quality', 'pnl']].corr().iloc[0, 1]
        good_sleep = df[df['sleep_quality'] >= 4]['pnl'].mean()
        poor_sleep = df[df['sleep_quality'] <= 2]['pnl'].mean()
        
        insights['sleep_analysis'] = {
            'correlation': round(float(sleep_corr), 3),
            'good_sleep_avg': round(float(good_sleep), 2),
            'poor_sleep_avg': round(float(poor_sleep), 2),
            'difference': round(float(good_sleep - poor_sleep), 2)
        }
    
    # Confidence correlation
    if 'pre_trade_confidence' in df.columns:
        conf_corr = df[['pre_trade_confidence', 'pnl']].corr().iloc[0, 1]
        high_conf = df[df['pre_trade_confidence'] >= 4]['pnl'].mean()
        low_conf = df[df['pre_trade_confidence'] <= 2]['pnl'].mean()
        
        insights['confidence_analysis'] = {
            'correlation': round(float(conf_corr), 3),
            'high_confidence_avg': round(float(high_conf), 2),
            'low_confidence_avg': round(float(low_conf), 2),
            'difference': round(float(high_conf - low_conf), 2)
        }
    
    return insights

# ===== TIME-BASED ANALYSIS =====

def analyze_time_patterns(trades):
    """Analyze performance by time of day and day of week"""
    if not trades or len(trades) < 10:
        return None
    
    df = pd.DataFrame(trades)
    df['date'] = pd.to_datetime(df['date'])
    df['day_of_week'] = df['date'].dt.day_name()
    
    # Parse time if available
    if 'time' in df.columns and df['time'].notna().any():
        df['hour'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce').dt.hour
    
    insights = {
        'day_analysis': {},
        'hour_analysis': {},
        'best_times': [],
        'worst_times': []
    }
    
    # Day of week analysis
    day_stats = df.groupby('day_of_week').agg({
        'pnl': ['mean', 'sum', 'count'],
    }).round(2)
    
    # Order days properly
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_stats = day_stats.reindex([d for d in day_order if d in day_stats.index])
    
    if len(day_stats) > 0:
        best_day = day_stats['pnl']['mean'].idxmax()
        worst_day = day_stats['pnl']['mean'].idxmin()
        
        insights['day_analysis'] = {
            'best_day': best_day,
            'best_day_avg': float(day_stats.loc[best_day, ('pnl', 'mean')]),
            'worst_day': worst_day,
            'worst_day_avg': float(day_stats.loc[worst_day, ('pnl', 'mean')]),
            'daily_stats': day_stats.to_dict()
        }
    
    # Hour analysis (if time data available)
    if 'hour' in df.columns and df['hour'].notna().any():
        hour_stats = df.groupby('hour').agg({
            'pnl': ['mean', 'sum', 'count'],
        }).round(2)
        
        if len(hour_stats) > 0:
            best_hours = hour_stats.nlargest(3, ('pnl', 'mean'))
            worst_hours = hour_stats.nsmallest(3, ('pnl', 'mean'))
            
            insights['hour_analysis'] = {
                'best_hours': best_hours.index.tolist(),
                'worst_hours': worst_hours.index.tolist(),
                'hourly_stats': hour_stats.to_dict()
            }
    
    return insights

# ===== SETUP & SYMBOL ANALYSIS =====

def analyze_setups_symbols(trades):
    """Analyze performance by setup and symbol"""
    if not trades or len(trades) < 5:
        return None
    
    df = pd.DataFrame(trades)
    
    insights = {
        'setup_analysis': {},
        'symbol_analysis': {},
        'market_condition_analysis': {}
    }
    
    # Setup analysis
    if 'setup' in df.columns and df['setup'].notna().any():
        setup_stats = df.groupby('setup').agg({
            'pnl': ['mean', 'sum', 'count', lambda x: (x > 0).sum()],
        }).round(2)
        setup_stats.columns = ['avg_pnl', 'total_pnl', 'count', 'wins']
        setup_stats['winrate'] = (setup_stats['wins'] / setup_stats['count'] * 100).round(1)
        
        best_setup = setup_stats['avg_pnl'].idxmax()
        worst_setup = setup_stats['avg_pnl'].idxmin()
        
        insights['setup_analysis'] = {
            'best_setup': best_setup,
            'best_setup_avg': float(setup_stats.loc[best_setup, 'avg_pnl']),
            'best_setup_winrate': float(setup_stats.loc[best_setup, 'winrate']),
            'worst_setup': worst_setup,
            'worst_setup_avg': float(setup_stats.loc[worst_setup, 'avg_pnl']),
            'setup_stats': setup_stats.to_dict()
        }
    
    # Symbol analysis
    if 'symbol' in df.columns:
        symbol_stats = df.groupby('symbol').agg({
            'pnl': ['mean', 'sum', 'count', lambda x: (x > 0).sum()],
        }).round(2)
        symbol_stats.columns = ['avg_pnl', 'total_pnl', 'count', 'wins']
        symbol_stats['winrate'] = (symbol_stats['wins'] / symbol_stats['count'] * 100).round(1)
        
        # Only show symbols with 3+ trades
        symbol_stats = symbol_stats[symbol_stats['count'] >= 3]
        
        if len(symbol_stats) > 0:
            best_symbol = symbol_stats['avg_pnl'].idxmax()
            worst_symbol = symbol_stats['avg_pnl'].idxmin()
            
            insights['symbol_analysis'] = {
                'best_symbol': best_symbol,
                'best_symbol_avg': float(symbol_stats.loc[best_symbol, 'avg_pnl']),
                'best_symbol_winrate': float(symbol_stats.loc[best_symbol, 'winrate']),
                'worst_symbol': worst_symbol,
                'worst_symbol_avg': float(symbol_stats.loc[worst_symbol, 'avg_pnl']),
                'symbol_stats': symbol_stats.to_dict()
            }
    
    # Market condition analysis
    if 'market_condition' in df.columns and df['market_condition'].notna().any():
        market_stats = df.groupby('market_condition').agg({
            'pnl': ['mean', 'sum', 'count', lambda x: (x > 0).sum()],
        }).round(2)
        market_stats.columns = ['avg_pnl', 'total_pnl', 'count', 'wins']
        market_stats['winrate'] = (market_stats['wins'] / market_stats['count'] * 100).round(1)
        
        insights['market_condition_analysis'] = {
            'market_stats': market_stats.to_dict()
        }
    
    return insights

# ===== AI INSIGHTS GENERATOR =====

def generate_ai_insights(trades):
    """Generate AI-powered insights and recommendations"""
    if not trades or len(trades) < 10:
        return ["Voeg meer trades toe (minimaal 10) voor AI insights."]
    
    insights = []
    df = pd.DataFrame(trades)
    
    # Psychology insights
    psych = analyze_psychology_performance(trades)
    if psych:
        # Mood insights
        if psych['mood_analysis']:
            best_mood = psych['mood_analysis']['best_mood']
            worst_mood = psych['mood_analysis']['worst_mood']
            diff = psych['mood_analysis']['best_mood_avg_pnl'] - psych['mood_analysis']['worst_mood_avg_pnl']
            insights.append(f"🧠 Je tradet het beste als je '{best_mood}' bent (€{diff:.2f} beter dan '{worst_mood}').")
        
        # Focus insights
        if psych['focus_analysis'] and psych['focus_analysis']['correlation'] > 0.2:
            diff = psych['focus_analysis']['difference']
            insights.append(f"🎯 Hogere focus = betere resultaten! (€{diff:.2f} verschil tussen hoge/lage focus).")
        
        # Stress insights
        if psych['stress_analysis'] and psych['stress_analysis']['correlation'] < -0.2:
            diff = psych['stress_analysis']['difference']
            insights.append(f"⚠️ Stress vermindert je performance met €{abs(diff):.2f} gemiddeld. Trade rustiger!")
        
        # Sleep insights
        if psych['sleep_analysis'] and psych['sleep_analysis']['correlation'] > 0.15:
            diff = psych['sleep_analysis']['difference']
            insights.append(f"😴 Goede slaap = betere trades! €{diff:.2f} verschil tussen goed/slecht geslapen.")
    
    # Time-based insights
    time_insights = analyze_time_patterns(trades)
    if time_insights and time_insights['day_analysis']:
        best_day = time_insights['day_analysis']['best_day']
        worst_day = time_insights['day_analysis']['worst_day']
        insights.append(f"📅 Je beste dag: {best_day}. Je slechtste dag: {worst_day}. Plan je trades strategisch!")
    
    # Setup insights
    setup_insights = analyze_setups_symbols(trades)
    if setup_insights and setup_insights['setup_analysis']:
        best = setup_insights['setup_analysis']['best_setup']
        winrate = setup_insights['setup_analysis']['best_setup_winrate']
        insights.append(f"📈 Je beste setup: '{best}' met {winrate}% winrate. Focus hierop!")
    
    # Symbol insights
    if setup_insights and setup_insights['symbol_analysis']:
        worst_sym = setup_insights['symbol_analysis']['worst_symbol']
        worst_wr = setup_insights['symbol_analysis']['worst_symbol_winrate']
        if worst_wr < 40:
            insights.append(f"⚠️ {worst_sym} heeft slechts {worst_wr}% winrate. Overweeg dit symbool te mijden.")
    
    # Consecutive loss detection
    consecutive_losses = 0
    max_consecutive = 0
    for trade in sorted(trades, key=lambda x: x['date']):
        if trade['pnl'] < 0:
            consecutive_losses += 1
            max_consecutive = max(max_consecutive, consecutive_losses)
        else:
            consecutive_losses = 0
    
    if max_consecutive >= 3:
        insights.append(f"🛑 Je hebt {max_consecutive} opeenvolgende verliezen gehad. Implementeer een 'circuit breaker' regel!")
    
    # Risk management check
    df['risk_pct'] = (df['pnl'].abs() / 10000 * 100)  # Assuming 10k account
    avg_risk = df['risk_pct'].mean()
    if avg_risk > 2:
        insights.append(f"⚠️ Je gemiddelde risico per trade is {avg_risk:.1f}%. Overweeg dit te verlagen naar <2%.")
    
    # Overtrading check
    recent_30d = df[df['date'] >= (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')]
    if len(recent_30d) > 60:
        insights.append(f"⚠️ Je hebt {len(recent_30d)} trades in 30 dagen (>2/dag). Mogelijk overtrading?")
    
    if not insights:
        insights.append("✅ Goede balans gevonden! Blijf consistent en volg je strategie.")
    
    return insights

# ===== GENERATE INSIGHTS SUMMARY =====

def get_complete_analysis(trades):
    """Get complete analysis package"""
    return {
        'psychology': analyze_psychology_performance(trades),
        'time_patterns': analyze_time_patterns(trades),
        'setups_symbols': analyze_setups_symbols(trades),
        'ai_insights': generate_ai_insights(trades)
    }

