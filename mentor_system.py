"""
Mentor System for Trading Journal Pro
Trade comments, feedback tracking, and improvement suggestions
"""

from datetime import datetime
import json
import os

MENTOR_FEEDBACK_FILE = "mentor_feedback.json"
TRADE_COMMENTS_FILE = "trade_comments.json"

def load_trade_comments():
    """Load all trade comments"""
    if os.path.exists(TRADE_COMMENTS_FILE):
        try:
            with open(TRADE_COMMENTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_trade_comments(comments):
    """Save trade comments"""
    with open(TRADE_COMMENTS_FILE, 'w') as f:
        json.dump(comments, f, indent=2)

def add_trade_comment(trade_id, commenter_name, comment_text, comment_type="general", rating=None):
    """
    Add a comment to a trade
    
    comment_type: general, praise, improvement, warning, question
    rating: 1-5 stars (optional)
    """
    comments = load_trade_comments()
    
    new_comment = {
        "id": len(comments) + 1,
        "trade_id": trade_id,
        "commenter_name": commenter_name,
        "comment_text": comment_text,
        "comment_type": comment_type,
        "rating": rating,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "edited": False
    }
    
    comments.append(new_comment)
    save_trade_comments(comments)
    
    return new_comment

def get_comments_for_trade(trade_id):
    """Get all comments for a specific trade"""
    comments = load_trade_comments()
    return [c for c in comments if c['trade_id'] == trade_id]

def get_all_comments_by_user(user_id, trades):
    """Get all comments for a user's trades"""
    comments = load_trade_comments()
    user_trade_ids = [t['id'] for t in trades]
    return [c for c in comments if c['trade_id'] in user_trade_ids]

def delete_comment(comment_id):
    """Delete a comment"""
    comments = load_trade_comments()
    comments = [c for c in comments if c['id'] != comment_id]
    save_trade_comments(comments)

def edit_comment(comment_id, new_text):
    """Edit a comment"""
    comments = load_trade_comments()
    for comment in comments:
        if comment['id'] == comment_id:
            comment['comment_text'] = new_text
            comment['edited'] = True
            comment['last_edited'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_trade_comments(comments)

# Mentor Feedback System
def load_mentor_feedback():
    """Load mentor feedback records"""
    if os.path.exists(MENTOR_FEEDBACK_FILE):
        try:
            with open(MENTOR_FEEDBACK_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_mentor_feedback(feedback_list):
    """Save mentor feedback"""
    with open(MENTOR_FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_list, f, indent=2)

def create_feedback_session(user_id, mentor_name, session_type="weekly"):
    """Create a new feedback session"""
    feedback_list = load_mentor_feedback()
    
    new_session = {
        "id": len(feedback_list) + 1,
        "user_id": user_id,
        "mentor_name": mentor_name,
        "session_type": session_type,  # weekly, monthly, ad-hoc
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "status": "in_progress",
        "strengths": [],
        "improvements": [],
        "action_items": [],
        "overall_rating": None,
        "notes": ""
    }
    
    feedback_list.append(new_session)
    save_mentor_feedback(feedback_list)
    
    return new_session

def update_feedback_session(session_id, strengths=None, improvements=None, action_items=None, 
                            overall_rating=None, notes=None, status=None):
    """Update a feedback session"""
    feedback_list = load_mentor_feedback()
    
    for session in feedback_list:
        if session['id'] == session_id:
            if strengths is not None:
                session['strengths'] = strengths
            if improvements is not None:
                session['improvements'] = improvements
            if action_items is not None:
                session['action_items'] = action_items
            if overall_rating is not None:
                session['overall_rating'] = overall_rating
            if notes is not None:
                session['notes'] = notes
            if status is not None:
                session['status'] = status
            session['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    save_mentor_feedback(feedback_list)

def get_feedback_for_user(user_id):
    """Get all feedback sessions for a user"""
    feedback_list = load_mentor_feedback()
    return [f for f in feedback_list if f['user_id'] == user_id]

def get_latest_feedback(user_id):
    """Get the most recent feedback session"""
    feedback_list = get_feedback_for_user(user_id)
    if feedback_list:
        return sorted(feedback_list, key=lambda x: x['created_at'], reverse=True)[0]
    return None

# Suggestion System
def generate_suggestions_from_trades(trades):
    """Generate automated suggestions based on trade analysis"""
    suggestions = []
    
    if not trades or len(trades) < 5:
        return [{
            "type": "info",
            "title": "Keep Trading",
            "message": "Log more trades to receive personalized suggestions",
            "priority": "low"
        }]
    
    # Calculate metrics
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] < 0]
    win_rate = (len(wins) / len(trades)) * 100 if trades else 0
    
    # Win rate suggestions
    if win_rate < 40:
        suggestions.append({
            "type": "warning",
            "title": "Low Win Rate Alert",
            "message": f"Your win rate is {win_rate:.1f}%. Consider reviewing your entry criteria and focusing on high-probability setups.",
            "priority": "high",
            "action": "Review your top 5 losing trades and identify common patterns"
        })
    elif win_rate > 70:
        suggestions.append({
            "type": "success",
            "title": "Excellent Win Rate",
            "message": f"Win rate of {win_rate:.1f}% is outstanding! Consider increasing position sizes gradually.",
            "priority": "medium",
            "action": "Document your winning strategy to ensure consistency"
        })
    
    # Average P&L suggestions
    if wins and losses:
        avg_win = sum([t['pnl'] for t in wins]) / len(wins)
        avg_loss = abs(sum([t['pnl'] for t in losses]) / len(losses))
        
        if avg_loss > avg_win:
            suggestions.append({
                "type": "warning",
                "title": "Risk/Reward Imbalance",
                "message": f"Average loss (€{avg_loss:.2f}) exceeds average win (€{avg_win:.2f}). Focus on better take-profit targets.",
                "priority": "high",
                "action": "Aim for 2:1 risk-reward ratio on all new trades"
            })
    
    # Trading frequency
    if len(trades) > 50:
        # Check for overtrading
        dates = [t['date'] for t in trades]
        unique_days = len(set(dates))
        trades_per_day = len(trades) / unique_days if unique_days > 0 else 0
        
        if trades_per_day > 10:
            suggestions.append({
                "type": "warning",
                "title": "Possible Overtrading",
                "message": f"You're averaging {trades_per_day:.1f} trades per day. Consider focusing on quality over quantity.",
                "priority": "medium",
                "action": "Limit yourself to 5 high-quality setups per day"
            })
    
    # Consistency
    recent_trades = sorted(trades, key=lambda x: x['date'], reverse=True)[:10]
    if len(recent_trades) >= 10:
        recent_pnl = sum([t['pnl'] for t in recent_trades])
        if recent_pnl < 0:
            suggestions.append({
                "type": "warning",
                "title": "Recent Downtrend",
                "message": "Your last 10 trades are net negative. Consider taking a break and reviewing your strategy.",
                "priority": "high",
                "action": "Paper trade for 1 week before resuming live trading"
            })
    
    # Setup diversity
    setups = [t.get('setup', 'Unknown') for t in trades]
    unique_setups = len(set(setups))
    
    if unique_setups < 3:
        suggestions.append({
            "type": "info",
            "title": "Limited Strategy Diversity",
            "message": f"You're using {unique_setups} setup(s). Consider learning 1-2 additional strategies for more opportunities.",
            "priority": "low",
            "action": "Study and backtest a new trading setup this month"
        })
    
    # Psychology check
    trades_with_emotions = [t for t in trades if t.get('emotion')]
    if len(trades_with_emotions) > 10:
        negative_emotions = ['stressed', 'anxious', 'frustrated', 'revenge', 'fomo']
        emotional_trades = [t for t in trades_with_emotions 
                          if any(neg in str(t.get('emotion', '')).lower() for neg in negative_emotions)]
        
        if len(emotional_trades) > len(trades_with_emotions) * 0.3:
            suggestions.append({
                "type": "warning",
                "title": "Emotional Trading Detected",
                "message": f"{len(emotional_trades)} trades were logged with negative emotions. Focus on psychological discipline.",
                "priority": "high",
                "action": "Implement a 30-minute cool-down period after losses"
            })
    
    # Time-based patterns
    if len(trades) >= 20:
        # Check for time-of-day patterns
        hour_pnl = {}
        for trade in trades:
            if 'time' in trade and trade['time']:
                try:
                    hour = int(trade['time'].split(':')[0])
                    if hour not in hour_pnl:
                        hour_pnl[hour] = []
                    hour_pnl[hour].append(trade['pnl'])
                except:
                    pass
        
        if hour_pnl:
            worst_hour = min(hour_pnl.items(), key=lambda x: sum(x[1]))
            if sum(worst_hour[1]) < 0:
                suggestions.append({
                    "type": "info",
                    "title": "Time-Based Pattern",
                    "message": f"You perform worst at {worst_hour[0]}:00. Consider avoiding trades during this time.",
                    "priority": "medium",
                    "action": f"Review why trades at {worst_hour[0]}:00 underperform"
                })
    
    # If no issues found
    if not suggestions:
        suggestions.append({
            "type": "success",
            "title": "Great Job!",
            "message": "Your trading performance looks solid. Keep following your plan and stay disciplined.",
            "priority": "low",
            "action": "Continue with your current strategy"
        })
    
    return suggestions

def get_mentor_statistics(user_id, trades):
    """Get statistics for mentor dashboard"""
    comments = get_all_comments_by_user(user_id, trades)
    feedback_sessions = get_feedback_for_user(user_id)
    
    # Comment stats
    comment_types = {}
    for comment in comments:
        c_type = comment.get('comment_type', 'general')
        comment_types[c_type] = comment_types.get(c_type, 0) + 1
    
    # Rating stats
    ratings = [c.get('rating') for c in comments if c.get('rating')]
    avg_rating = sum(ratings) / len(ratings) if ratings else None
    
    # Feedback stats
    completed_sessions = len([f for f in feedback_sessions if f['status'] == 'completed'])
    in_progress_sessions = len([f for f in feedback_sessions if f['status'] == 'in_progress'])
    
    return {
        "total_comments": len(comments),
        "comment_types": comment_types,
        "average_rating": avg_rating,
        "total_feedback_sessions": len(feedback_sessions),
        "completed_sessions": completed_sessions,
        "in_progress_sessions": in_progress_sessions,
        "latest_feedback": get_latest_feedback(user_id)
    }

