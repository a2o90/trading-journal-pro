"""
Enhanced Risk Calculator for Trading Journal Pro
Position sizing, risk management, and account tracking
"""

def calculate_position_size(account_size, risk_pct, entry_price, stop_loss):
    """
    Calculate position size based on risk parameters
    
    Args:
        account_size: Total account balance
        risk_pct: Risk percentage per trade (e.g. 1.0 for 1%)
        entry_price: Entry price
        stop_loss: Stop loss price
        
    Returns:
        dict with position_size, risk_amount, shares/contracts
    """
    if not all([account_size, risk_pct, entry_price, stop_loss]):
        return None
    
    # Calculate risk amount in currency
    risk_amount = account_size * (risk_pct / 100)
    
    # Calculate price difference (risk per share)
    price_diff = abs(entry_price - stop_loss)
    
    if price_diff == 0:
        return None
    
    # Calculate position size (number of shares/contracts)
    shares = risk_amount / price_diff
    
    # Total position value
    position_value = shares * entry_price
    
    return {
        'shares': round(shares, 2),
        'position_value': round(position_value, 2),
        'risk_amount': round(risk_amount, 2),
        'risk_pct': risk_pct,
        'price_diff': round(price_diff, 2),
        'leverage': round(position_value / account_size, 2) if account_size > 0 else 0
    }

def calculate_risk_reward(entry_price, stop_loss, take_profit):
    """Calculate risk/reward ratio"""
    if not all([entry_price, stop_loss, take_profit]):
        return None
    
    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    
    if risk == 0:
        return None
    
    rr_ratio = reward / risk
    
    return {
        'risk': round(risk, 2),
        'reward': round(reward, 2),
        'ratio': round(rr_ratio, 2),
        'risk_pct': round((risk / entry_price) * 100, 2),
        'reward_pct': round((reward / entry_price) * 100, 2)
    }

def calculate_kelly_criterion(trades):
    """
    Calculate Kelly Criterion for optimal position sizing
    
    Formula: K% = W - [(1 - W) / R]
    Where:
        W = Win rate (decimal)
        R = Average win / Average loss ratio
    """
    if not trades or len(trades) < 20:
        return None
    
    wins = [t['pnl'] for t in trades if t['pnl'] > 0]
    losses = [abs(t['pnl']) for t in trades if t['pnl'] < 0]
    
    if not wins or not losses:
        return None
    
    win_rate = len(wins) / len(trades)
    avg_win = sum(wins) / len(wins)
    avg_loss = sum(losses) / len(losses)
    
    if avg_loss == 0:
        return None
    
    win_loss_ratio = avg_win / avg_loss
    
    # Kelly %
    kelly_pct = win_rate - ((1 - win_rate) / win_loss_ratio)
    
    # Kelly criterion can be negative (don't trade) or very high (reduce it)
    # Recommend half-Kelly for safety
    kelly_pct = max(0, kelly_pct)
    half_kelly = kelly_pct / 2
    
    return {
        'kelly_pct': round(kelly_pct * 100, 2),
        'half_kelly_pct': round(half_kelly * 100, 2),
        'win_rate': round(win_rate * 100, 2),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'win_loss_ratio': round(win_loss_ratio, 2),
        'recommendation': f"Risk {round(half_kelly * 100, 1)}% per trade (Half Kelly)"
    }

def calculate_max_risk_per_day(account_size, daily_risk_pct=5.0):
    """Calculate maximum risk allowed per day"""
    return account_size * (daily_risk_pct / 100)

def calculate_current_risk_exposure(trades_today):
    """Calculate current risk exposure from today's open trades"""
    if not trades_today:
        return 0
    
    # Sum of absolute risk from today's trades
    total_risk = sum(abs(t['pnl']) for t in trades_today)
    return total_risk

def calculate_required_winrate(risk_reward_ratio):
    """
    Calculate minimum winrate needed to breakeven
    
    Formula: Required WR = 1 / (1 + R/R)
    """
    if not risk_reward_ratio or risk_reward_ratio <= 0:
        return None
    
    required_wr = 1 / (1 + risk_reward_ratio)
    
    return {
        'required_winrate_pct': round(required_wr * 100, 2),
        'risk_reward_ratio': risk_reward_ratio,
        'message': f"You need {round(required_wr * 100, 1)}% winrate to breakeven with {risk_reward_ratio}:1 R:R"
    }

def calculate_profit_targets(entry_price, risk_amount, r_multiples=[1, 2, 3, 5]):
    """
    Calculate profit targets based on R-multiples
    
    R-multiple: How many times your risk you're targeting
    """
    if not entry_price or not risk_amount:
        return None
    
    targets = []
    for r in r_multiples:
        profit = risk_amount * r
        targets.append({
            'r_multiple': r,
            'profit_amount': round(profit, 2),
            'target_price_long': round(entry_price + profit, 2),
            'target_price_short': round(entry_price - profit, 2)
        })
    
    return targets

def calculate_expectancy(trades):
    """
    Calculate trading expectancy
    
    Expectancy = (Win% × Avg Win) - (Loss% × Avg Loss)
    """
    if not trades or len(trades) < 10:
        return None
    
    wins = [t['pnl'] for t in trades if t['pnl'] > 0]
    losses = [abs(t['pnl']) for t in trades if t['pnl'] < 0]
    
    if not wins or not losses:
        return None
    
    win_pct = len(wins) / len(trades)
    loss_pct = len(losses) / len(trades)
    avg_win = sum(wins) / len(wins)
    avg_loss = sum(losses) / len(losses)
    
    expectancy = (win_pct * avg_win) - (loss_pct * avg_loss)
    
    return {
        'expectancy': round(expectancy, 2),
        'win_pct': round(win_pct * 100, 2),
        'loss_pct': round(loss_pct * 100, 2),
        'avg_win': round(avg_win, 2),
        'avg_loss': round(avg_loss, 2),
        'trades_analyzed': len(trades),
        'message': f"Expected value per trade: €{round(expectancy, 2)}"
    }

def calculate_risk_of_ruin(account_size, risk_per_trade, win_rate, num_trades=100):
    """
    Calculate probability of losing X% of account (Risk of Ruin)
    
    Simplified formula for educational purposes
    """
    if not all([account_size, risk_per_trade, win_rate]):
        return None
    
    # Convert to decimals
    risk_pct = risk_per_trade / 100
    wr = win_rate / 100
    
    # Number of losing trades to ruin (lose 50% of account)
    trades_to_ruin = 50 / risk_per_trade  # 50% drawdown threshold
    
    # Probability of consecutive losses
    loss_rate = 1 - wr
    ruin_probability = loss_rate ** trades_to_ruin
    
    return {
        'ruin_probability_pct': round(ruin_probability * 100, 4),
        'trades_to_50pct_loss': round(trades_to_ruin, 0),
        'risk_per_trade': risk_per_trade,
        'win_rate': win_rate,
        'warning': 'Keep risk per trade below 2% to minimize ruin probability'
    }

def get_risk_management_report(trades, account_size, current_balance=None):
    """Generate comprehensive risk management report"""
    if not trades:
        return None
    
    if current_balance is None:
        current_balance = account_size + sum(t['pnl'] for t in trades)
    
    # Calculate various metrics
    kelly = calculate_kelly_criterion(trades)
    expectancy = calculate_expectancy(trades)
    
    # Current stats
    total_pnl = sum(t['pnl'] for t in trades)
    win_rate = len([t for t in trades if t['pnl'] > 0]) / len(trades) * 100
    
    # Risk of ruin (assuming 1% risk)
    ruin = calculate_risk_of_ruin(current_balance, 1.0, win_rate)
    
    report = {
        'account_size': account_size,
        'current_balance': round(current_balance, 2),
        'total_pnl': round(total_pnl, 2),
        'roi_pct': round((total_pnl / account_size) * 100, 2),
        'total_trades': len(trades),
        'win_rate': round(win_rate, 2),
        'kelly_criterion': kelly,
        'expectancy': expectancy,
        'risk_of_ruin': ruin,
        'recommendations': []
    }
    
    # Generate recommendations
    if kelly and kelly['half_kelly_pct'] > 0:
        report['recommendations'].append(f"✅ Optimal risk per trade: {kelly['half_kelly_pct']}% (Half-Kelly)")
    
    if expectancy and expectancy['expectancy'] > 0:
        report['recommendations'].append(f"✅ Positive expectancy: €{expectancy['expectancy']} per trade")
    else:
        report['recommendations'].append("⚠️ Negative or zero expectancy - review your strategy!")
    
    if win_rate < 40:
        report['recommendations'].append("⚠️ Low winrate (<40%) - ensure your R:R ratio is high (>2:1)")
    
    if ruin and ruin['ruin_probability_pct'] > 1:
        report['recommendations'].append(f"⚠️ Risk of ruin: {ruin['ruin_probability_pct']}% - lower your risk per trade!")
    
    return report

