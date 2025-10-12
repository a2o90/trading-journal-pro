"""
Custom Alerts System for Trading Journal Pro
Monitors trading metrics and triggers warnings
"""

import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

# ===== ALERT THRESHOLDS (can be customized per user) =====

DEFAULT_THRESHOLDS = {
    'max_drawdown_pct': 10.0,  # Alert if drawdown > 10%
    'daily_loss_limit': 500.0,  # Alert if daily loss > $500
    'consecutive_losses': 3,  # Alert after 3 consecutive losses
    'winrate_drop_pct': 10.0,  # Alert if winrate drops > 10% from average
    'daily_trade_limit': 10,  # Alert if more than 10 trades per day
    'risk_per_trade_pct': 2.0,  # Alert if risk per trade > 2%
}

# ===== ALERT CLASSES =====

class Alert:
    """Base alert class"""
    def __init__(self, alert_type, severity, message, data=None):
        self.alert_type = alert_type  # e.g. "DRAWDOWN", "DAILY_LOSS", etc.
        self.severity = severity  # "INFO", "WARNING", "CRITICAL"
        self.message = message
        self.data = data or {}
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def to_dict(self):
        return {
            'type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp
        }

# ===== ALERT DETECTION FUNCTIONS =====

def check_max_drawdown(trades, threshold_pct=10.0, account_size=10000):
    """Check for maximum drawdown alert"""
    if not trades or len(trades) < 5:
        return None
    
    df = pd.DataFrame(trades)
    df = df.sort_values('date')
    df['cumulative_pnl'] = df['pnl'].cumsum()
    
    # Calculate running maximum
    df['running_max'] = df['cumulative_pnl'].cummax()
    
    # Calculate drawdown
    df['drawdown'] = df['cumulative_pnl'] - df['running_max']
    df['drawdown_pct'] = (df['drawdown'] / account_size) * 100
    
    max_dd = df['drawdown'].min()
    max_dd_pct = df['drawdown_pct'].min()
    
    if abs(max_dd_pct) > threshold_pct:
        return Alert(
            alert_type="MAX_DRAWDOWN",
            severity="CRITICAL",
            message=f"⚠️ DRAWDOWN ALERT: Maximum drawdown reached {abs(max_dd_pct):.1f}% (€{abs(max_dd):.2f})",
            data={'drawdown_pct': abs(max_dd_pct), 'drawdown_amount': abs(max_dd), 'threshold': threshold_pct}
        )
    
    return None

def check_daily_loss(trades, threshold=500.0):
    """Check for daily loss limit"""
    if not trades:
        return None
    
    df = pd.DataFrame(trades)
    df['date'] = pd.to_datetime(df['date'])
    
    # Check today's trades
    today = datetime.now().date()
    today_trades = df[df['date'].dt.date == today]
    
    if len(today_trades) > 0:
        today_pnl = today_trades['pnl'].sum()
        
        if today_pnl < -threshold:
            return Alert(
                alert_type="DAILY_LOSS",
                severity="CRITICAL",
                message=f"🛑 DAILY LOSS LIMIT: You've lost €{abs(today_pnl):.2f} today (limit: €{threshold})",
                data={'daily_loss': abs(today_pnl), 'threshold': threshold, 'trades_today': len(today_trades)}
            )
    
    # Also check yesterday if it was bad
    yesterday = today - timedelta(days=1)
    yesterday_trades = df[df['date'].dt.date == yesterday]
    
    if len(yesterday_trades) > 0:
        yesterday_pnl = yesterday_trades['pnl'].sum()
        if yesterday_pnl < -threshold:
            return Alert(
                alert_type="DAILY_LOSS",
                severity="WARNING",
                message=f"⚠️ High loss yesterday: €{abs(yesterday_pnl):.2f}. Consider taking a break today.",
                data={'daily_loss': abs(yesterday_pnl), 'date': str(yesterday)}
            )
    
    return None

def check_consecutive_losses(trades, threshold=3):
    """Check for consecutive losing trades"""
    if not trades or len(trades) < threshold:
        return None
    
    # Sort by date
    sorted_trades = sorted(trades, key=lambda x: (x['date'], x.get('time', '00:00:00')))
    
    consecutive_losses = 0
    max_consecutive = 0
    current_streak = []
    
    for trade in sorted_trades:
        if trade['pnl'] < 0:
            consecutive_losses += 1
            current_streak.append(trade)
            max_consecutive = max(max_consecutive, consecutive_losses)
        else:
            if consecutive_losses >= threshold:
                # Found a streak that meets threshold
                total_loss = sum(t['pnl'] for t in current_streak)
                return Alert(
                    alert_type="CONSECUTIVE_LOSSES",
                    severity="CRITICAL",
                    message=f"🛑 {consecutive_losses} consecutive losses detected! Total loss: €{abs(total_loss):.2f}. STOP and review your strategy!",
                    data={'consecutive_count': consecutive_losses, 'total_loss': abs(total_loss), 'threshold': threshold}
                )
            consecutive_losses = 0
            current_streak = []
    
    # Check if currently in a losing streak
    if consecutive_losses >= threshold:
        total_loss = sum(t['pnl'] for t in current_streak)
        return Alert(
            alert_type="CONSECUTIVE_LOSSES",
            severity="CRITICAL",
            message=f"🛑 ACTIVE LOSING STREAK: {consecutive_losses} consecutive losses! Total: €{abs(total_loss):.2f}. STOP TRADING NOW!",
            data={'consecutive_count': consecutive_losses, 'total_loss': abs(total_loss), 'threshold': threshold, 'active': True}
        )
    
    return None

def check_winrate_drop(trades, drop_threshold=10.0):
    """Check for significant winrate drop"""
    if not trades or len(trades) < 20:
        return None
    
    df = pd.DataFrame(trades)
    df = df.sort_values('date')
    
    # Calculate overall winrate
    overall_winrate = (df['pnl'] > 0).sum() / len(df) * 100
    
    # Calculate recent winrate (last 10 trades)
    recent_trades = df.tail(10)
    recent_winrate = (recent_trades['pnl'] > 0).sum() / len(recent_trades) * 100
    
    winrate_diff = overall_winrate - recent_winrate
    
    if winrate_diff > drop_threshold:
        return Alert(
            alert_type="WINRATE_DROP",
            severity="WARNING",
            message=f"📉 WINRATE DROP: Recent winrate {recent_winrate:.1f}% vs overall {overall_winrate:.1f}% (-{winrate_diff:.1f}%)",
            data={'overall_winrate': overall_winrate, 'recent_winrate': recent_winrate, 'drop': winrate_diff}
        )
    
    return None

def check_overtrading(trades, daily_limit=10):
    """Check for overtrading (too many trades in one day)"""
    if not trades:
        return None
    
    df = pd.DataFrame(trades)
    df['date'] = pd.to_datetime(df['date'])
    
    # Check today
    today = datetime.now().date()
    today_trades = df[df['date'].dt.date == today]
    
    if len(today_trades) >= daily_limit:
        today_pnl = today_trades['pnl'].sum()
        return Alert(
            alert_type="OVERTRADING",
            severity="WARNING",
            message=f"⚠️ OVERTRADING: {len(today_trades)} trades today (limit: {daily_limit}). P&L: €{today_pnl:.2f}",
            data={'trades_today': len(today_trades), 'limit': daily_limit, 'pnl': today_pnl}
        )
    
    return None

def check_high_risk(trades, risk_threshold=2.0, account_size=10000):
    """Check if recent trades have high risk per trade"""
    if not trades or len(trades) < 5:
        return None
    
    df = pd.DataFrame(trades)
    df = df.sort_values('date')
    
    # Calculate risk as % of account for last 5 trades
    recent = df.tail(5)
    recent['risk_pct'] = (recent['pnl'].abs() / account_size) * 100
    
    high_risk_trades = recent[recent['risk_pct'] > risk_threshold]
    
    if len(high_risk_trades) > 2:  # More than 2 out of 5
        avg_risk = recent['risk_pct'].mean()
        return Alert(
            alert_type="HIGH_RISK",
            severity="WARNING",
            message=f"⚠️ HIGH RISK: {len(high_risk_trades)} recent trades exceed {risk_threshold}% risk. Avg risk: {avg_risk:.2f}%",
            data={'high_risk_count': len(high_risk_trades), 'avg_risk': avg_risk, 'threshold': risk_threshold}
        )
    
    return None

def check_revenge_trading_pattern(trades):
    """Detect potential revenge trading (quick trades after loss)"""
    if not trades or len(trades) < 10:
        return None
    
    df = pd.DataFrame(trades)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Look for pattern: Loss followed by multiple quick trades same day
    revenge_days = 0
    
    for date in df['date'].dt.date.unique():
        day_trades = df[df['date'].dt.date == date].sort_values('date')
        
        if len(day_trades) >= 4:  # At least 4 trades in one day
            # Check if first trade was a loss
            if day_trades.iloc[0]['pnl'] < 0:
                # Check if subsequent trades were attempts to recover
                subsequent_losses = (day_trades.iloc[1:]['pnl'] < 0).sum()
                if subsequent_losses >= 2:
                    revenge_days += 1
    
    if revenge_days > 0:
        return Alert(
            alert_type="REVENGE_TRADING",
            severity="WARNING",
            message=f"⚠️ REVENGE TRADING PATTERN: Detected {revenge_days} day(s) with possible revenge trading (loss → multiple quick trades)",
            data={'days_detected': revenge_days}
        )
    
    return None

# ===== MAIN ALERT CHECKER =====

def check_all_alerts(trades, thresholds=None, account_size=10000):
    """Run all alert checks and return list of active alerts"""
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS.copy()
    
    alerts = []
    
    # Run all checks
    checks = [
        check_max_drawdown(trades, thresholds['max_drawdown_pct'], account_size),
        check_daily_loss(trades, thresholds['daily_loss_limit']),
        check_consecutive_losses(trades, thresholds['consecutive_losses']),
        check_winrate_drop(trades, thresholds['winrate_drop_pct']),
        check_overtrading(trades, thresholds['daily_trade_limit']),
        check_high_risk(trades, thresholds['risk_per_trade_pct'], account_size),
        check_revenge_trading_pattern(trades)
    ]
    
    # Filter out None results
    alerts = [alert for alert in checks if alert is not None]
    
    return alerts

def get_alert_summary(alerts):
    """Get summary of alerts by severity"""
    if not alerts:
        return "✅ No active alerts. Trading within safe parameters."
    
    critical = [a for a in alerts if a.severity == "CRITICAL"]
    warnings = [a for a in alerts if a.severity == "WARNING"]
    
    summary = f"🚨 {len(critical)} CRITICAL | ⚠️ {len(warnings)} WARNING"
    return summary

