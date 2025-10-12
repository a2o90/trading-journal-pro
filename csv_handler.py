"""
CSV Import/Export Handler for Trading Journal Pro
Supports multiple broker formats and custom mapping
"""

import csv
import io
from datetime import datetime
import pandas as pd

# Broker format templates
BROKER_FORMATS = {
    "MetaTrader 4/5": {
        "columns": ["Ticket", "Open Time", "Type", "Size", "Item", "Price", "S/L", "T/P", "Close Time", "Commission", "Swap", "Profit"],
        "mapping": {
            "date": "Close Time",
            "symbol": "Item",
            "direction": "Type",
            "entry": "Price",
            "pnl": "Profit",
            "volume": "Size"
        },
        "date_format": "%Y.%m.%d %H:%M",
        "direction_map": {"buy": "Long", "sell": "Short", "0": "Long", "1": "Short"}
    },
    "TradingView": {
        "columns": ["Trade Id", "Signal Date/Time", "Symbol", "Type", "Order", "Contracts/Shares/Lots", "Entry Price", "Exit Price", "Profit/Loss", "Cumulative Profit", "Run-up", "Drawdown", "Commission", "Entry Name", "Exit Name"],
        "mapping": {
            "date": "Signal Date/Time",
            "symbol": "Symbol",
            "direction": "Type",
            "entry": "Entry Price",
            "exit": "Exit Price",
            "pnl": "Profit/Loss",
            "volume": "Contracts/Shares/Lots"
        },
        "date_format": "%Y-%m-%d %H:%M:%S",
        "direction_map": {"long": "Long", "short": "Short"}
    },
    "Interactive Brokers": {
        "columns": ["Symbol", "Date/Time", "Quantity", "T. Price", "C. Price", "Proceeds", "Comm/Fee", "Basis", "Realized P/L", "MTM P/L", "Code"],
        "mapping": {
            "date": "Date/Time",
            "symbol": "Symbol",
            "entry": "T. Price",
            "exit": "C. Price",
            "pnl": "Realized P/L",
            "volume": "Quantity"
        },
        "date_format": "%Y%m%d, %H:%M:%S",
        "direction_map": {}  # Inferred from quantity sign
    },
    "Generic": {
        "columns": ["Date", "Symbol", "Direction", "Entry", "Exit", "P&L", "Setup", "Notes"],
        "mapping": {
            "date": "Date",
            "symbol": "Symbol",
            "direction": "Direction",
            "entry": "Entry",
            "exit": "Exit",
            "pnl": "P&L",
            "setup": "Setup",
            "notes": "Notes"
        },
        "date_format": "%Y-%m-%d",
        "direction_map": {}
    },
    "Trading Journal Pro": {
        "columns": ["date", "symbol", "direction", "entry", "exit", "pnl", "setup", "notes", "time", "r_multiple", "emotion", "confidence"],
        "mapping": {
            "date": "date",
            "symbol": "symbol",
            "direction": "direction",
            "entry": "entry",
            "exit": "exit",
            "pnl": "pnl",
            "setup": "setup",
            "notes": "notes",
            "time": "time",
            "r_multiple": "r_multiple",
            "emotion": "emotion",
            "confidence": "confidence"
        },
        "date_format": "%Y-%m-%d",
        "direction_map": {}
    }
}

def get_broker_template(broker_name):
    """Get CSV template for a specific broker"""
    if broker_name in BROKER_FORMATS:
        return BROKER_FORMATS[broker_name]
    return BROKER_FORMATS["Generic"]

def generate_csv_template(broker_name="Trading Journal Pro"):
    """Generate a downloadable CSV template"""
    template = get_broker_template(broker_name)
    
    # Create CSV with headers
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(template["columns"])
    
    # Add example row
    example_row = []
    for col in template["columns"]:
        if "date" in col.lower() or "time" in col.lower():
            example_row.append(datetime.now().strftime(template["date_format"]))
        elif "symbol" in col.lower() or "item" in col.lower():
            example_row.append("EUR/USD")
        elif "type" in col.lower() or "direction" in col.lower():
            example_row.append("Long")
        elif "profit" in col.lower() or "p&l" in col.lower() or "p/l" in col.lower():
            example_row.append("100.00")
        elif "price" in col.lower() or "entry" in col.lower():
            example_row.append("1.1000")
        elif "exit" in col.lower() or "close" in col.lower():
            example_row.append("1.1050")
        elif "size" in col.lower() or "quantity" in col.lower() or "volume" in col.lower() or "contracts" in col.lower():
            example_row.append("1.0")
        elif "setup" in col.lower():
            example_row.append("Breakout")
        elif "notes" in col.lower():
            example_row.append("Good trade")
        else:
            example_row.append("0")
    
    writer.writerow(example_row)
    
    output.seek(0)
    return output.getvalue()

def parse_csv_import(file_content, broker_format="Trading Journal Pro", user_id=0):
    """
    Parse imported CSV and convert to trades format
    
    Returns: (success_count, error_count, trades_list, errors_list)
    """
    template = get_broker_template(broker_format)
    mapping = template["mapping"]
    date_format = template["date_format"]
    direction_map = template["direction_map"]
    
    trades = []
    errors = []
    
    try:
        # Try to read CSV
        try:
            df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
        except:
            df = pd.read_csv(io.StringIO(file_content))
        
        # Validate columns
        missing_cols = []
        for required_col in mapping.values():
            if required_col and required_col not in df.columns:
                missing_cols.append(required_col)
        
        if missing_cols:
            return 0, len(df), [], [f"Missing required columns: {', '.join(missing_cols)}"]
        
        # Process each row
        for idx, row in df.iterrows():
            try:
                # Extract date
                date_col = mapping.get("date", "Date")
                if date_col and date_col in row:
                    try:
                        # Parse date
                        trade_date = datetime.strptime(str(row[date_col]).strip(), date_format)
                        date_str = trade_date.strftime("%Y-%m-%d")
                        time_str = trade_date.strftime("%H:%M")
                    except:
                        # Fallback: try generic date parsing
                        try:
                            trade_date = pd.to_datetime(row[date_col])
                            date_str = trade_date.strftime("%Y-%m-%d")
                            time_str = trade_date.strftime("%H:%M")
                        except:
                            date_str = datetime.now().strftime("%Y-%m-%d")
                            time_str = datetime.now().strftime("%H:%M")
                else:
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    time_str = datetime.now().strftime("%H:%M")
                
                # Extract symbol
                symbol_col = mapping.get("symbol", "Symbol")
                symbol = str(row[symbol_col]).strip() if symbol_col and symbol_col in row else "Unknown"
                
                # Extract direction
                direction_col = mapping.get("direction", "Direction")
                if direction_col and direction_col in row:
                    raw_direction = str(row[direction_col]).strip().lower()
                    direction = direction_map.get(raw_direction, raw_direction.capitalize())
                else:
                    # Infer from quantity (IB style)
                    volume_col = mapping.get("volume", "Quantity")
                    if volume_col and volume_col in row:
                        try:
                            qty = float(row[volume_col])
                            direction = "Long" if qty > 0 else "Short"
                        except:
                            direction = "Long"
                    else:
                        direction = "Long"
                
                # Extract prices
                entry_col = mapping.get("entry", "Entry")
                entry = float(row[entry_col]) if entry_col and entry_col in row and row[entry_col] else 0.0
                
                exit_col = mapping.get("exit", "Exit")
                exit_price = float(row[exit_col]) if exit_col and exit_col in row and row[exit_col] else entry
                
                # Extract P&L
                pnl_col = mapping.get("pnl", "P&L")
                if pnl_col and pnl_col in row and row[pnl_col]:
                    pnl = float(row[pnl_col])
                else:
                    # Calculate from entry/exit
                    volume_col = mapping.get("volume", "Size")
                    volume = float(row[volume_col]) if volume_col and volume_col in row and row[volume_col] else 1.0
                    
                    if direction.lower() == "long":
                        pnl = (exit_price - entry) * abs(volume)
                    else:
                        pnl = (entry - exit_price) * abs(volume)
                
                # Extract optional fields
                setup_col = mapping.get("setup", "Setup")
                setup = str(row[setup_col]) if setup_col and setup_col in row and row[setup_col] else "Imported"
                
                notes_col = mapping.get("notes", "Notes")
                notes = str(row[notes_col]) if notes_col and notes_col in row and row[notes_col] else ""
                
                r_multiple_col = mapping.get("r_multiple", "R")
                r_multiple = float(row[r_multiple_col]) if r_multiple_col and r_multiple_col in row and row[r_multiple_col] else None
                
                emotion_col = mapping.get("emotion", "Emotion")
                emotion = str(row[emotion_col]) if emotion_col and emotion_col in row and row[emotion_col] else ""
                
                confidence_col = mapping.get("confidence", "Confidence")
                confidence = int(row[confidence_col]) if confidence_col and confidence_col in row and row[confidence_col] else 5
                
                # Create trade object
                trade = {
                    "id": len(trades) + 1,
                    "user_id": user_id,
                    "date": date_str,
                    "time": time_str,
                    "symbol": symbol,
                    "direction": direction,
                    "entry": entry,
                    "exit": exit_price,
                    "pnl": pnl,
                    "setup": setup,
                    "notes": notes,
                    "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if r_multiple is not None:
                    trade["r_multiple"] = r_multiple
                if emotion:
                    trade["emotion"] = emotion
                if confidence:
                    trade["confidence"] = confidence
                
                trades.append(trade)
                
            except Exception as e:
                errors.append(f"Row {idx+2}: {str(e)}")
        
        return len(trades), len(errors), trades, errors
        
    except Exception as e:
        return 0, 1, [], [f"Failed to parse CSV: {str(e)}"]

def export_trades_to_csv(trades, format_type="Trading Journal Pro"):
    """Export trades to CSV in specified format"""
    template = get_broker_template(format_type)
    
    output = io.StringIO()
    
    if format_type == "Trading Journal Pro":
        # Full export with all fields
        fieldnames = ["date", "time", "symbol", "direction", "entry", "exit", "pnl", 
                     "setup", "notes", "r_multiple", "emotion", "confidence"]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for trade in trades:
            writer.writerow({
                "date": trade.get('date', ''),
                "time": trade.get('time', ''),
                "symbol": trade.get('symbol', ''),
                "direction": trade.get('direction', ''),
                "entry": trade.get('entry', 0),
                "exit": trade.get('exit', 0),
                "pnl": trade.get('pnl', 0),
                "setup": trade.get('setup', ''),
                "notes": trade.get('notes', ''),
                "r_multiple": trade.get('r_multiple', ''),
                "emotion": trade.get('emotion', ''),
                "confidence": trade.get('confidence', 5)
            })
    
    elif format_type == "Generic":
        # Simple format
        fieldnames = ["Date", "Symbol", "Direction", "Entry", "Exit", "P&L", "Setup", "Notes"]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for trade in trades:
            writer.writerow({
                "Date": trade.get('date', ''),
                "Symbol": trade.get('symbol', ''),
                "Direction": trade.get('direction', ''),
                "Entry": trade.get('entry', 0),
                "Exit": trade.get('exit', 0),
                "P&L": trade.get('pnl', 0),
                "Setup": trade.get('setup', ''),
                "Notes": trade.get('notes', '')
            })
    
    else:
        # Default to Trading Journal Pro format
        return export_trades_to_csv(trades, "Trading Journal Pro")
    
    output.seek(0)
    return output.getvalue()

def get_import_stats(trades):
    """Get statistics from imported trades"""
    if not trades:
        return None
    
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t['pnl'] > 0])
    losing_trades = len([t for t in trades if t['pnl'] < 0])
    total_pnl = sum(t['pnl'] for t in trades)
    
    unique_symbols = len(set([t['symbol'] for t in trades]))
    date_range = f"{min([t['date'] for t in trades])} to {max([t['date'] for t in trades])}"
    
    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "total_pnl": total_pnl,
        "win_rate": (winning_trades / total_trades * 100) if total_trades > 0 else 0,
        "unique_symbols": unique_symbols,
        "date_range": date_range
    }

