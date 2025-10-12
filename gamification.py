"""
Gamification Module for Trading Journal Pro
Streaks, achievements, levels, and challenges to motivate traders
"""

from datetime import datetime, timedelta
import json

# Achievement definitions
ACHIEVEMENTS = {
    "first_trade": {
        "name": "🎯 First Trade",
        "description": "Log your first trade",
        "xp": 10,
        "check": lambda trades, user: len(trades) >= 1
    },
    "10_trades": {
        "name": "📈 Consistent Trader",
        "description": "Log 10 trades",
        "xp": 50,
        "check": lambda trades, user: len(trades) >= 10
    },
    "50_trades": {
        "name": "🔥 Active Trader",
        "description": "Log 50 trades",
        "xp": 150,
        "check": lambda trades, user: len(trades) >= 50
    },
    "100_trades": {
        "name": "⭐ Veteran Trader",
        "description": "Log 100 trades",
        "xp": 300,
        "check": lambda trades, user: len(trades) >= 100
    },
    "500_trades": {
        "name": "🏆 Master Trader",
        "description": "Log 500 trades",
        "xp": 1000,
        "check": lambda trades, user: len(trades) >= 500
    },
    "first_win": {
        "name": "✅ First Victory",
        "description": "Win your first trade",
        "xp": 25,
        "check": lambda trades, user: len([t for t in trades if t['pnl'] > 0]) >= 1
    },
    "win_streak_3": {
        "name": "🔥 Hot Hand",
        "description": "Win 3 trades in a row",
        "xp": 75,
        "check": lambda trades, user: get_max_win_streak(trades) >= 3
    },
    "win_streak_5": {
        "name": "🚀 On Fire",
        "description": "Win 5 trades in a row",
        "xp": 150,
        "check": lambda trades, user: get_max_win_streak(trades) >= 5
    },
    "win_streak_10": {
        "name": "💎 Unstoppable",
        "description": "Win 10 trades in a row",
        "xp": 500,
        "check": lambda trades, user: get_max_win_streak(trades) >= 10
    },
    "profitable_week": {
        "name": "📅 Green Week",
        "description": "End the week profitable",
        "xp": 100,
        "check": lambda trades, user: has_profitable_week(trades)
    },
    "profitable_month": {
        "name": "📆 Green Month",
        "description": "End the month profitable",
        "xp": 250,
        "check": lambda trades, user: has_profitable_month(trades)
    },
    "50_percent_winrate": {
        "name": "⚖️ Balanced",
        "description": "Achieve 50% win rate (min 20 trades)",
        "xp": 100,
        "check": lambda trades, user: len(trades) >= 20 and calculate_winrate(trades) >= 50
    },
    "70_percent_winrate": {
        "name": "🎖️ Sharp Shooter",
        "description": "Achieve 70% win rate (min 50 trades)",
        "xp": 300,
        "check": lambda trades, user: len(trades) >= 50 and calculate_winrate(trades) >= 70
    },
    "risk_manager": {
        "name": "🛡️ Risk Manager",
        "description": "Never risk more than 2% (min 30 trades)",
        "xp": 200,
        "check": lambda trades, user: check_risk_management(trades)
    },
    "journal_master": {
        "name": "📖 Journal Master",
        "description": "Add notes to 50 trades",
        "xp": 150,
        "check": lambda trades, user: len([t for t in trades if t.get('notes', '')]) >= 50
    },
    "early_bird": {
        "name": "🌅 Early Bird",
        "description": "Trade before 9 AM 10 times",
        "xp": 75,
        "check": lambda trades, user: count_early_trades(trades) >= 10
    },
    "comeback_king": {
        "name": "👑 Comeback King",
        "description": "Recover from a 3-trade losing streak to profit",
        "xp": 200,
        "check": lambda trades, user: check_comeback(trades)
    },
    "diversifier": {
        "name": "🌍 Diversifier",
        "description": "Trade 10 different symbols",
        "xp": 100,
        "check": lambda trades, user: len(set([t['symbol'] for t in trades])) >= 10
    },
    "perfectionist": {
        "name": "💯 Perfectionist",
        "description": "5 trades with R-multiple > 3",
        "xp": 250,
        "check": lambda trades, user: len([t for t in trades if t.get('r_multiple', 0) > 3]) >= 5
    },
    "consistency": {
        "name": "📊 Consistent Performer",
        "description": "Trade for 30 consecutive days",
        "xp": 500,
        "check": lambda trades, user: check_trading_days_streak(trades) >= 30
    }
}

# Level thresholds (XP required for each level)
LEVELS = [
    {"level": 1, "xp": 0, "title": "Novice Trader"},
    {"level": 2, "xp": 100, "title": "Apprentice"},
    {"level": 3, "xp": 250, "title": "Intermediate"},
    {"level": 4, "xp": 500, "title": "Advanced"},
    {"level": 5, "xp": 1000, "title": "Expert"},
    {"level": 6, "xp": 2000, "title": "Master"},
    {"level": 7, "xp": 3500, "title": "Grand Master"},
    {"level": 8, "xp": 5000, "title": "Legend"},
    {"level": 9, "xp": 7500, "title": "Pro Trader"},
    {"level": 10, "xp": 10000, "title": "Elite Trader"}
]

# Weekly challenges
WEEKLY_CHALLENGES = [
    {
        "id": "week_10_trades",
        "name": "Volume Challenge",
        "description": "Complete 10 trades this week",
        "xp": 100,
        "check": lambda trades: len(trades) >= 10
    },
    {
        "id": "week_60_winrate",
        "name": "Accuracy Challenge",
        "description": "Achieve 60% win rate this week (min 5 trades)",
        "xp": 150,
        "check": lambda trades: len(trades) >= 5 and calculate_winrate(trades) >= 60
    },
    {
        "id": "week_positive_pnl",
        "name": "Profit Challenge",
        "description": "End the week with positive P&L",
        "xp": 100,
        "check": lambda trades: sum([t['pnl'] for t in trades]) > 0
    },
    {
        "id": "week_journal_all",
        "name": "Journaling Challenge",
        "description": "Add notes to all trades this week",
        "xp": 75,
        "check": lambda trades: all([t.get('notes', '') for t in trades]) if trades else False
    },
    {
        "id": "week_no_revenge",
        "name": "Discipline Challenge",
        "description": "No trades within 1 hour of a loss",
        "xp": 125,
        "check": lambda trades: check_no_revenge_trading(trades)
    }
]

# Helper functions for achievement checks
def get_max_win_streak(trades):
    """Calculate maximum consecutive wins"""
    if not trades:
        return 0
    
    sorted_trades = sorted(trades, key=lambda x: x['date'])
    current_streak = 0
    max_streak = 0
    
    for trade in sorted_trades:
        if trade['pnl'] > 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    return max_streak

def calculate_winrate(trades):
    """Calculate win rate percentage"""
    if not trades:
        return 0
    wins = len([t for t in trades if t['pnl'] > 0])
    return (wins / len(trades)) * 100

def has_profitable_week(trades):
    """Check if last week was profitable"""
    if not trades:
        return False
    
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday() + 7)
    week_end = today - timedelta(days=today.weekday())
    
    week_trades = [t for t in trades if week_start <= datetime.strptime(t['date'], '%Y-%m-%d') <= week_end]
    
    if not week_trades:
        return False
    
    return sum([t['pnl'] for t in week_trades]) > 0

def has_profitable_month(trades):
    """Check if last month was profitable"""
    if not trades:
        return False
    
    today = datetime.now()
    if today.month == 1:
        last_month = 12
        year = today.year - 1
    else:
        last_month = today.month - 1
        year = today.year
    
    month_trades = [t for t in trades if datetime.strptime(t['date'], '%Y-%m-%d').month == last_month and 
                    datetime.strptime(t['date'], '%Y-%m-%d').year == year]
    
    if not month_trades:
        return False
    
    return sum([t['pnl'] for t in month_trades]) > 0

def check_risk_management(trades):
    """Check if risk management is followed"""
    if len(trades) < 30:
        return False
    
    # Simplified check: no single loss > 2% of assumed account
    account_size = 10000
    for trade in trades:
        if trade['pnl'] < 0 and abs(trade['pnl']) > (account_size * 0.02):
            return False
    
    return True

def count_early_trades(trades):
    """Count trades before 9 AM"""
    count = 0
    for trade in trades:
        if 'time' in trade and trade['time']:
            try:
                hour = int(trade['time'].split(':')[0])
                if hour < 9:
                    count += 1
            except:
                pass
    return count

def check_comeback(trades):
    """Check if recovered from 3-trade losing streak"""
    if len(trades) < 4:
        return False
    
    sorted_trades = sorted(trades, key=lambda x: x['date'])
    
    for i in range(len(sorted_trades) - 3):
        # Check for 3 consecutive losses
        if all([sorted_trades[i+j]['pnl'] < 0 for j in range(3)]):
            # Check if next trades recover to profit
            recovery_pnl = sum([sorted_trades[i+j]['pnl'] for j in range(3, min(10, len(sorted_trades)-i))])
            if recovery_pnl > abs(sum([sorted_trades[i+j]['pnl'] for j in range(3)])):
                return True
    
    return False

def check_trading_days_streak(trades):
    """Check for consecutive trading days"""
    if not trades:
        return 0
    
    dates = sorted(set([t['date'] for t in trades]))
    
    max_streak = 1
    current_streak = 1
    
    for i in range(1, len(dates)):
        prev_date = datetime.strptime(dates[i-1], '%Y-%m-%d')
        curr_date = datetime.strptime(dates[i], '%Y-%m-%d')
        
        # Check if dates are consecutive (excluding weekends)
        delta = (curr_date - prev_date).days
        if delta == 1 or (delta <= 3 and prev_date.weekday() >= 4):  # Weekend gap allowed
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
    
    return max_streak

def check_no_revenge_trading(trades):
    """Check if no trades within 1 hour of a loss"""
    if len(trades) < 2:
        return True
    
    sorted_trades = sorted(trades, key=lambda x: f"{x['date']} {x.get('time', '12:00')}")
    
    for i in range(len(sorted_trades) - 1):
        if sorted_trades[i]['pnl'] < 0:
            try:
                loss_time = datetime.strptime(f"{sorted_trades[i]['date']} {sorted_trades[i].get('time', '12:00')}", '%Y-%m-%d %H:%M')
                next_time = datetime.strptime(f"{sorted_trades[i+1]['date']} {sorted_trades[i+1].get('time', '12:00')}", '%Y-%m-%d %H:%M')
                
                if (next_time - loss_time).total_seconds() < 3600:  # Less than 1 hour
                    return False
            except:
                pass
    
    return True

def check_achievements(trades, user_achievements=None):
    """Check which achievements have been unlocked"""
    if user_achievements is None:
        user_achievements = []
    
    unlocked = []
    new_unlocks = []
    
    for ach_id, achievement in ACHIEVEMENTS.items():
        if ach_id in user_achievements:
            unlocked.append(ach_id)
        else:
            # Check if achievement is now completed
            try:
                if achievement["check"](trades, None):
                    new_unlocks.append({
                        "id": ach_id,
                        **achievement
                    })
            except:
                pass
    
    return unlocked, new_unlocks

def calculate_level(total_xp):
    """Calculate current level from total XP"""
    current_level = LEVELS[0]
    
    for level in LEVELS:
        if total_xp >= level["xp"]:
            current_level = level
        else:
            break
    
    # Find next level
    next_level_idx = current_level["level"]
    if next_level_idx < len(LEVELS):
        next_level = LEVELS[next_level_idx]
        xp_to_next = next_level["xp"] - total_xp
    else:
        next_level = None
        xp_to_next = 0
    
    return {
        "current_level": current_level["level"],
        "title": current_level["title"],
        "total_xp": total_xp,
        "current_level_xp": current_level["xp"],
        "next_level": next_level,
        "xp_to_next_level": xp_to_next
    }

def get_weekly_challenges(trades_this_week):
    """Get weekly challenges and their completion status"""
    challenges = []
    
    for challenge in WEEKLY_CHALLENGES:
        try:
            completed = challenge["check"](trades_this_week)
        except:
            completed = False
        
        challenges.append({
            "id": challenge["id"],
            "name": challenge["name"],
            "description": challenge["description"],
            "xp": challenge["xp"],
            "completed": completed
        })
    
    return challenges

def get_current_streaks(trades):
    """Get current win/loss streaks"""
    if not trades:
        return {"win_streak": 0, "loss_streak": 0, "total_trades": 0}
    
    sorted_trades = sorted(trades, key=lambda x: x['date'], reverse=True)
    
    # Current streak (from most recent)
    current_streak = 0
    streak_type = None
    
    for trade in sorted_trades:
        if trade['pnl'] > 0:
            if streak_type is None:
                streak_type = "win"
            if streak_type == "win":
                current_streak += 1
            else:
                break
        elif trade['pnl'] < 0:
            if streak_type is None:
                streak_type = "loss"
            if streak_type == "loss":
                current_streak += 1
            else:
                break
        else:
            break
    
    win_streak = current_streak if streak_type == "win" else 0
    loss_streak = current_streak if streak_type == "loss" else 0
    
    # Max streaks
    max_win_streak = get_max_win_streak(trades)
    
    return {
        "current_win_streak": win_streak,
        "current_loss_streak": loss_streak,
        "max_win_streak": max_win_streak,
        "total_trades": len(trades)
    }

def get_trading_stats_summary(trades):
    """Get summary stats for gamification display"""
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "best_trade": 0,
            "worst_trade": 0,
            "unique_symbols": 0
        }
    
    wins = len([t for t in trades if t['pnl'] > 0])
    total_pnl = sum([t['pnl'] for t in trades])
    
    return {
        "total_trades": len(trades),
        "win_rate": (wins / len(trades) * 100) if trades else 0,
        "total_pnl": total_pnl,
        "best_trade": max([t['pnl'] for t in trades]),
        "worst_trade": min([t['pnl'] for t in trades]),
        "unique_symbols": len(set([t['symbol'] for t in trades]))
    }

