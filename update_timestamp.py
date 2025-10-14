#!/usr/bin/env python3
"""
Auto-update script for Trading Journal Pro
Updates the LAST_UPDATE timestamp automatically before git commits
"""

import re
from datetime import datetime
import pytz

def update_last_updated():
    """Update the LAST_UPDATE timestamp in trading_journal.py"""
    
    # Get current time in NL timezone
    nl_tz = pytz.timezone('Europe/Amsterdam')
    current_time_nl = datetime.now(nl_tz)
    formatted_time = current_time_nl.strftime('%d-%m-%Y %H:%M:%S')
    
    # Read the current file
    with open('trading_journal.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the LAST_UPDATE line
    pattern = r'LAST_UPDATE = "[^"]*"'
    replacement = f'LAST_UPDATE = "{formatted_time}"'
    
    new_content = re.sub(pattern, replacement, content)
    
    # Write back to file
    with open('trading_journal.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Updated LAST_UPDATE to: {formatted_time}")
    return formatted_time

if __name__ == "__main__":
    update_last_updated()
