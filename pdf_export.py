"""
PDF Export Module for Trading Journal Pro
Generates professional weekly/monthly trading reports with charts
"""

import io
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np

def generate_weekly_report(trades, start_date, end_date, username="Trader"):
    """Generate a weekly trading report PDF"""
    
    # Filter trades for the week
    week_trades = [t for t in trades if start_date <= datetime.strptime(t['date'], '%Y-%m-%d') <= end_date]
    
    if not week_trades:
        return None
    
    # Create PDF in memory
    buffer = io.BytesIO()
    
    with PdfPages(buffer) as pdf:
        # PAGE 1: Overview
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle(f'Weekly Trading Report - {username}', fontsize=16, fontweight='bold')
        
        # Header info
        plt.text(0.5, 0.95, f'{start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}', 
                ha='center', fontsize=12, transform=fig.transFigure)
        
        # Summary statistics
        total_trades = len(week_trades)
        winning_trades = len([t for t in week_trades if t['pnl'] > 0])
        losing_trades = len([t for t in week_trades if t['pnl'] < 0])
        total_pnl = sum(t['pnl'] for t in week_trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = np.mean([t['pnl'] for t in week_trades if t['pnl'] > 0]) if winning_trades > 0 else 0
        avg_loss = np.mean([abs(t['pnl']) for t in week_trades if t['pnl'] < 0]) if losing_trades > 0 else 0
        
        # Summary box
        summary_text = f"""
WEEKLY SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Trades:        {total_trades}
Winning Trades:      {winning_trades}
Losing Trades:       {losing_trades}
Win Rate:           {win_rate:.1f}%

Total P&L:          €{total_pnl:.2f}
Average Win:        €{avg_win:.2f}
Average Loss:       €{avg_loss:.2f}
Win/Loss Ratio:     {(avg_win/avg_loss if avg_loss > 0 else 0):.2f}

Best Trade:         €{max([t['pnl'] for t in week_trades]):.2f}
Worst Trade:        €{min([t['pnl'] for t in week_trades]):.2f}
        """
        
        plt.text(0.1, 0.75, summary_text, fontsize=10, verticalalignment='top',
                family='monospace', transform=fig.transFigure)
        
        # Daily P&L Chart
        ax1 = fig.add_subplot(2, 1, 2)
        daily_pnl = {}
        for trade in week_trades:
            date = trade['date']
            if date not in daily_pnl:
                daily_pnl[date] = 0
            daily_pnl[date] += trade['pnl']
        
        dates = sorted(daily_pnl.keys())
        pnls = [daily_pnl[d] for d in dates]
        colors = ['green' if p > 0 else 'red' for p in pnls]
        
        ax1.bar(dates, pnls, color=colors, alpha=0.7)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.set_title('Daily P&L', fontsize=12, fontweight='bold')
        ax1.set_ylabel('P&L (€)')
        ax1.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 2: Performance Charts
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle('Performance Analysis', fontsize=14, fontweight='bold')
        
        # Cumulative P&L
        ax1 = fig.add_subplot(2, 2, 1)
        sorted_trades = sorted(week_trades, key=lambda x: x['date'])
        cumulative_pnl = np.cumsum([t['pnl'] for t in sorted_trades])
        ax1.plot(range(len(cumulative_pnl)), cumulative_pnl, marker='o', linewidth=2)
        ax1.fill_between(range(len(cumulative_pnl)), cumulative_pnl, alpha=0.3)
        ax1.set_title('Cumulative P&L', fontsize=10, fontweight='bold')
        ax1.set_xlabel('Trade Number')
        ax1.set_ylabel('Cumulative P&L (€)')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='red', linestyle='--', linewidth=1)
        
        # Win/Loss Distribution
        ax2 = fig.add_subplot(2, 2, 2)
        wins_losses = [winning_trades, losing_trades]
        colors_pie = ['#2ecc71', '#e74c3c']
        ax2.pie(wins_losses, labels=['Wins', 'Losses'], autopct='%1.1f%%', 
               colors=colors_pie, startangle=90)
        ax2.set_title('Win/Loss Distribution', fontsize=10, fontweight='bold')
        
        # Trade Size Distribution
        ax3 = fig.add_subplot(2, 2, 3)
        pnls = [t['pnl'] for t in week_trades]
        ax3.hist(pnls, bins=15, color='steelblue', alpha=0.7, edgecolor='black')
        ax3.axvline(x=0, color='red', linestyle='--', linewidth=2)
        ax3.set_title('P&L Distribution', fontsize=10, fontweight='bold')
        ax3.set_xlabel('P&L (€)')
        ax3.set_ylabel('Frequency')
        ax3.grid(True, alpha=0.3)
        
        # Symbol Performance
        ax4 = fig.add_subplot(2, 2, 4)
        symbol_pnl = {}
        for trade in week_trades:
            symbol = trade.get('symbol', 'Unknown')
            if symbol not in symbol_pnl:
                symbol_pnl[symbol] = 0
            symbol_pnl[symbol] += trade['pnl']
        
        symbols = list(symbol_pnl.keys())[:10]  # Top 10
        pnls_by_symbol = [symbol_pnl[s] for s in symbols]
        colors_bar = ['green' if p > 0 else 'red' for p in pnls_by_symbol]
        
        ax4.barh(symbols, pnls_by_symbol, color=colors_bar, alpha=0.7)
        ax4.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        ax4.set_title('Performance by Symbol', fontsize=10, fontweight='bold')
        ax4.set_xlabel('P&L (€)')
        ax4.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 3: Trade Details
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle('Trade Details', fontsize=14, fontweight='bold')
        
        # Create trade table
        trade_data = []
        for i, trade in enumerate(sorted_trades[:20]):  # Max 20 trades
            trade_data.append([
                i+1,
                trade['date'],
                trade.get('symbol', 'N/A'),
                trade.get('direction', 'N/A'),
                f"€{trade['pnl']:.2f}",
                trade.get('setup', 'N/A')[:15]
            ])
        
        ax = fig.add_subplot(1, 1, 1)
        ax.axis('tight')
        ax.axis('off')
        
        table = ax.table(cellText=trade_data, 
                        colLabels=['#', 'Date', 'Symbol', 'Dir', 'P&L', 'Setup'],
                        cellLoc='left',
                        loc='center',
                        colWidths=[0.08, 0.15, 0.15, 0.08, 0.15, 0.25])
        
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)
        
        # Color code P&L cells
        for i in range(len(trade_data)):
            pnl_val = float(trade_data[i][4].replace('€', ''))
            if pnl_val > 0:
                table[(i+1, 4)].set_facecolor('#90EE90')
            else:
                table[(i+1, 4)].set_facecolor('#FFB6C1')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Metadata
        d = pdf.infodict()
        d['Title'] = f'Weekly Trading Report - {start_date.strftime("%Y-%m-%d")}'
        d['Author'] = 'Trading Journal Pro'
        d['Subject'] = 'Weekly Performance Report'
        d['Keywords'] = 'Trading, Report, Performance'
        d['CreationDate'] = datetime.now()
    
    buffer.seek(0)
    return buffer

def generate_monthly_report(trades, month, year, username="Trader"):
    """Generate a monthly trading report PDF"""
    
    # Filter trades for the month
    month_trades = []
    for t in trades:
        trade_date = datetime.strptime(t['date'], '%Y-%m-%d')
        if trade_date.month == month and trade_date.year == year:
            month_trades.append(t)
    
    if not month_trades:
        return None
    
    # Create PDF in memory
    buffer = io.BytesIO()
    
    with PdfPages(buffer) as pdf:
        # PAGE 1: Monthly Overview
        fig = plt.figure(figsize=(8.5, 11))
        month_name = datetime(year, month, 1).strftime('%B %Y')
        fig.suptitle(f'Monthly Trading Report - {month_name}', fontsize=16, fontweight='bold')
        
        # Summary statistics
        total_trades = len(month_trades)
        winning_trades = len([t for t in month_trades if t['pnl'] > 0])
        losing_trades = len([t for t in month_trades if t['pnl'] < 0])
        total_pnl = sum(t['pnl'] for t in month_trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = np.mean([t['pnl'] for t in month_trades if t['pnl'] > 0]) if winning_trades > 0 else 0
        avg_loss = np.mean([abs(t['pnl']) for t in month_trades if t['pnl'] < 0]) if losing_trades > 0 else 0
        
        max_win = max([t['pnl'] for t in month_trades])
        max_loss = min([t['pnl'] for t in month_trades])
        
        # Calculate weekly breakdown
        weeks = {}
        for trade in month_trades:
            trade_date = datetime.strptime(trade['date'], '%Y-%m-%d')
            week = trade_date.isocalendar()[1]
            if week not in weeks:
                weeks[week] = {'trades': 0, 'pnl': 0}
            weeks[week]['trades'] += 1
            weeks[week]['pnl'] += trade['pnl']
        
        # Summary text
        summary_text = f"""
MONTHLY SUMMARY - {month_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Trades:           {total_trades}
Winning Trades:         {winning_trades}
Losing Trades:          {losing_trades}
Breakeven Trades:       {total_trades - winning_trades - losing_trades}

Win Rate:              {win_rate:.1f}%
Total P&L:             €{total_pnl:.2f}

Average Win:           €{avg_win:.2f}
Average Loss:          €{avg_loss:.2f}
Win/Loss Ratio:        {(avg_win/avg_loss if avg_loss > 0 else 0):.2f}

Best Trade:            €{max_win:.2f}
Worst Trade:           €{max_loss:.2f}

Trading Days:          {len(set([t['date'] for t in month_trades]))}
Avg Trades/Day:        {total_trades/max(len(set([t['date'] for t in month_trades])), 1):.1f}
        """
        
        plt.text(0.1, 0.85, summary_text, fontsize=9, verticalalignment='top',
                family='monospace', transform=fig.transFigure)
        
        # Weekly breakdown chart
        ax1 = fig.add_subplot(2, 1, 2)
        week_nums = sorted(weeks.keys())
        week_pnls = [weeks[w]['pnl'] for w in week_nums]
        colors = ['green' if p > 0 else 'red' for p in week_pnls]
        
        ax1.bar([f'W{w}' for w in week_nums], week_pnls, color=colors, alpha=0.7)
        ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax1.set_title('Weekly P&L Breakdown', fontsize=12, fontweight='bold')
        ax1.set_ylabel('P&L (€)')
        ax1.grid(True, alpha=0.3)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # PAGE 2: Performance Analysis
        fig = plt.figure(figsize=(8.5, 11))
        fig.suptitle('Monthly Performance Analysis', fontsize=14, fontweight='bold')
        
        # Cumulative P&L with drawdown
        ax1 = fig.add_subplot(2, 2, 1)
        sorted_trades = sorted(month_trades, key=lambda x: x['date'])
        cumulative_pnl = np.cumsum([t['pnl'] for t in sorted_trades])
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdown = cumulative_pnl - running_max
        
        ax1.plot(range(len(cumulative_pnl)), cumulative_pnl, marker='o', linewidth=2, label='Equity')
        ax1.fill_between(range(len(drawdown)), drawdown, alpha=0.3, color='red', label='Drawdown')
        ax1.set_title('Equity Curve & Drawdown', fontsize=10, fontweight='bold')
        ax1.set_xlabel('Trade Number')
        ax1.set_ylabel('P&L (€)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # R-Multiple distribution
        ax2 = fig.add_subplot(2, 2, 2)
        r_multiples = [t.get('r_multiple', 0) for t in month_trades if 'r_multiple' in t]
        if r_multiples:
            ax2.hist(r_multiples, bins=15, color='steelblue', alpha=0.7, edgecolor='black')
            ax2.axvline(x=0, color='red', linestyle='--', linewidth=2)
            ax2.set_title('R-Multiple Distribution', fontsize=10, fontweight='bold')
            ax2.set_xlabel('R-Multiple')
            ax2.set_ylabel('Frequency')
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, 'No R-Multiple data', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('R-Multiple Distribution', fontsize=10, fontweight='bold')
        
        # Setup performance
        ax3 = fig.add_subplot(2, 2, 3)
        setup_pnl = {}
        for trade in month_trades:
            setup = trade.get('setup', 'Unknown')
            if setup not in setup_pnl:
                setup_pnl[setup] = 0
            setup_pnl[setup] += trade['pnl']
        
        setups = list(setup_pnl.keys())[:8]  # Top 8
        pnls_by_setup = [setup_pnl[s] for s in setups]
        colors_bar = ['green' if p > 0 else 'red' for p in pnls_by_setup]
        
        ax3.barh(setups, pnls_by_setup, color=colors_bar, alpha=0.7)
        ax3.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        ax3.set_title('Performance by Setup', fontsize=10, fontweight='bold')
        ax3.set_xlabel('P&L (€)')
        ax3.grid(True, alpha=0.3, axis='x')
        
        # Time of day performance
        ax4 = fig.add_subplot(2, 2, 4)
        hour_pnl = {}
        for trade in month_trades:
            if 'time' in trade and trade['time']:
                try:
                    hour = int(trade['time'].split(':')[0])
                    if hour not in hour_pnl:
                        hour_pnl[hour] = []
                    hour_pnl[hour].append(trade['pnl'])
                except:
                    pass
        
        if hour_pnl:
            hours = sorted(hour_pnl.keys())
            avg_pnl_by_hour = [np.mean(hour_pnl[h]) for h in hours]
            colors_time = ['green' if p > 0 else 'red' for p in avg_pnl_by_hour]
            
            ax4.bar(hours, avg_pnl_by_hour, color=colors_time, alpha=0.7)
            ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
            ax4.set_title('Avg P&L by Hour', fontsize=10, fontweight='bold')
            ax4.set_xlabel('Hour of Day')
            ax4.set_ylabel('Avg P&L (€)')
            ax4.grid(True, alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'No time data', ha='center', va='center', transform=ax4.transAxes)
            ax4.set_title('Avg P&L by Hour', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Metadata
        d = pdf.infodict()
        d['Title'] = f'Monthly Trading Report - {month_name}'
        d['Author'] = 'Trading Journal Pro'
        d['Subject'] = 'Monthly Performance Report'
        d['Keywords'] = 'Trading, Report, Performance, Monthly'
        d['CreationDate'] = datetime.now()
    
    buffer.seek(0)
    return buffer

def generate_custom_report(trades, start_date, end_date, username="Trader", title="Custom Report"):
    """Generate a custom date range trading report"""
    # Similar to weekly report but with custom date range
    return generate_weekly_report(trades, start_date, end_date, username)

