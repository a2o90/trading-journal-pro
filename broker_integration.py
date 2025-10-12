#!/usr/bin/env python3
"""
Broker Integration Module
Provides integration with TradingView webhooks and other broker APIs
"""

import json
import requests
import hmac
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify
import threading
import time

class TradingViewWebhookHandler:
    def __init__(self):
        self.webhook_secret = "trading_journal_secret_2024"  # Change this in production
        self.active_webhooks = []
        self.webhook_server = None
        self.server_thread = None
        
    def generate_webhook_url(self, user_id, account_id):
        """Generate unique webhook URL for user"""
        base_url = "https://your-domain.com"  # Replace with actual domain
        webhook_id = f"tj_{user_id}_{account_id}_{int(time.time())}"
        return f"{base_url}/webhook/{webhook_id}"
    
    def create_webhook_config(self, user_id, account_id, symbol_mapping=None):
        """Create webhook configuration for TradingView"""
        webhook_url = self.generate_webhook_url(user_id, account_id)
        
        config = {
            'webhook_id': f"tj_{user_id}_{account_id}",
            'user_id': user_id,
            'account_id': account_id,
            'webhook_url': webhook_url,
            'symbol_mapping': symbol_mapping or {},
            'created_at': datetime.now().isoformat(),
            'active': True,
            'last_used': None,
            'usage_count': 0
        }
        
        self.active_webhooks.append(config)
        return config
    
    def parse_tradingview_alert(self, alert_data):
        """Parse TradingView alert data"""
        try:
            # TradingView sends data in different formats
            if isinstance(alert_data, str):
                alert_data = json.loads(alert_data)
            
            # Extract trade information
            trade_info = {
                'symbol': alert_data.get('symbol', 'UNKNOWN'),
                'action': alert_data.get('action', 'BUY'),  # BUY/SELL
                'price': float(alert_data.get('price', 0)),
                'quantity': float(alert_data.get('quantity', 1)),
                'strategy': alert_data.get('strategy', 'TradingView'),
                'timeframe': alert_data.get('timeframe', '1m'),
                'message': alert_data.get('message', ''),
                'timestamp': alert_data.get('timestamp', datetime.now().isoformat()),
                'source': 'TradingView'
            }
            
            return trade_info
            
        except Exception as e:
            print(f"Error parsing TradingView alert: {e}")
            return None
    
    def validate_webhook_signature(self, payload, signature):
        """Validate webhook signature for security"""
        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            print(f"Error validating signature: {e}")
            return False
    
    def convert_to_trade_format(self, alert_data, user_id, account_id):
        """Convert TradingView alert to internal trade format"""
        try:
            # Parse the alert
            trade_info = self.parse_tradingview_alert(alert_data)
            if not trade_info:
                return None
            
            # Determine side based on action
            side = "Long" if trade_info['action'].upper() in ['BUY', 'LONG'] else "Short"
            
            # Calculate entry and exit prices
            entry_price = trade_info['price']
            exit_price = entry_price  # For now, assume same price (can be modified)
            
            # Create trade object
            trade = {
                'id': int(time.time() * 1000),  # Unique ID based on timestamp
                'user_id': user_id,
                'account_id': account_id,
                'account_name': f'Account {account_id}',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M:%S'),
                'symbol': trade_info['symbol'],
                'side': side,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'quantity': trade_info['quantity'],
                'duration_minutes': 0,
                'pnl': 0.0,  # Will be calculated when trade is closed
                'r_multiple': 0.0,
                'setup': trade_info['strategy'],
                'influence': 'TradingView',
                'trade_type': 'Webhook',
                'market_condition': 'Unknown',
                'mood': 'Automated',
                'focus_level': 5,
                'stress_level': 1,
                'sleep_quality': 5,
                'pre_trade_confidence': 4,
                'notes': f"TradingView Alert: {trade_info['message']} | Timeframe: {trade_info['timeframe']}"
            }
            
            return trade
            
        except Exception as e:
            print(f"Error converting to trade format: {e}")
            return None

class BrokerIntegrationManager:
    def __init__(self):
        self.tradingview_handler = TradingViewWebhookHandler()
        self.integration_settings = {}
        
    def setup_tradingview_integration(self, user_id, account_id, settings=None):
        """Setup TradingView integration for user"""
        default_settings = {
            'enabled': True,
            'auto_create_trades': True,
            'symbol_mapping': {
                'EURUSD': 'EURUSD',
                'GBPUSD': 'GBPUSD',
                'USDJPY': 'USDJPY',
                'AUDUSD': 'AUDUSD',
                'USDCAD': 'USDCAD',
                'NZDUSD': 'NZDUSD',
                'EURJPY': 'EURJPY',
                'GBPJPY': 'GBPJPY'
            },
            'default_quantity': 1.0,
            'risk_per_trade': 0.01,  # 1% risk per trade
            'notification_enabled': True
        }
        
        if settings:
            default_settings.update(settings)
        
        # Create webhook configuration
        webhook_config = self.tradingview_handler.create_webhook_config(
            user_id, account_id, default_settings['symbol_mapping']
        )
        
        # Store integration settings
        integration_key = f"tradingview_{user_id}_{account_id}"
        self.integration_settings[integration_key] = {
            'webhook_config': webhook_config,
            'settings': default_settings,
            'created_at': datetime.now().isoformat(),
            'last_activity': None,
            'total_trades': 0
        }
        
        return webhook_config
    
    def get_webhook_instructions(self, webhook_config):
        """Generate TradingView webhook setup instructions"""
        instructions = {
            'webhook_url': webhook_config['webhook_url'],
            'setup_steps': [
                "1. Open TradingView and go to your chart",
                "2. Click on 'Alerts' button",
                "3. Create a new alert",
                "4. Set your conditions (price, indicators, etc.)",
                "5. In 'Notifications', select 'Webhook URL'",
                f"6. Paste this URL: {webhook_config['webhook_url']}",
                "7. In 'Message', use this format:",
                "   {\"symbol\": \"{{ticker}}\", \"action\": \"{{strategy.order.action}}\", \"price\": {{close}}, \"quantity\": 1, \"strategy\": \"{{strategy.order.comment}}\", \"message\": \"{{strategy.order.alert_message}}\"}"
            ],
            'example_message': {
                "symbol": "EURUSD",
                "action": "BUY",
                "price": 1.0850,
                "quantity": 1,
                "strategy": "My Strategy",
                "message": "Long signal triggered",
                "timeframe": "5m"
            },
            'supported_actions': ['BUY', 'SELL', 'LONG', 'SHORT'],
            'supported_symbols': list(webhook_config['symbol_mapping'].keys())
        }
        
        return instructions
    
    def process_webhook_trade(self, webhook_data, user_id, account_id):
        """Process incoming webhook trade"""
        try:
            # Convert to internal trade format
            trade = self.tradingview_handler.convert_to_trade_format(
                webhook_data, user_id, account_id
            )
            
            if not trade:
                return {'success': False, 'error': 'Failed to parse trade data'}
            
            # Update integration stats
            integration_key = f"tradingview_{user_id}_{account_id}"
            if integration_key in self.integration_settings:
                self.integration_settings[integration_key]['last_activity'] = datetime.now().isoformat()
                self.integration_settings[integration_key]['total_trades'] += 1
            
            return {
                'success': True,
                'trade': trade,
                'message': f"Trade created: {trade['symbol']} {trade['side']} at {trade['entry_price']}"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_integration_status(self, user_id, account_id):
        """Get integration status for user"""
        integration_key = f"tradingview_{user_id}_{account_id}"
        
        if integration_key not in self.integration_settings:
            return {
                'enabled': False,
                'message': 'TradingView integration not set up'
            }
        
        config = self.integration_settings[integration_key]
        webhook_config = config['webhook_config']
        
        return {
            'enabled': config['settings']['enabled'],
            'webhook_url': webhook_config['webhook_url'],
            'total_trades': config['total_trades'],
            'last_activity': config['last_activity'],
            'created_at': config['created_at'],
            'settings': config['settings']
        }
    
    def test_webhook_connection(self, webhook_url):
        """Test webhook connection"""
        try:
            test_data = {
                'symbol': 'EURUSD',
                'action': 'BUY',
                'price': 1.0850,
                'quantity': 1,
                'strategy': 'Test',
                'message': 'Webhook test',
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                webhook_url,
                json=test_data,
                timeout=10
            )
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response': response.text
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
broker_integration = BrokerIntegrationManager()

# Convenience functions
def setup_tradingview_webhook(user_id, account_id, settings=None):
    """Setup TradingView webhook integration"""
    return broker_integration.setup_tradingview_integration(user_id, account_id, settings)

def get_webhook_instructions(webhook_config):
    """Get webhook setup instructions"""
    return broker_integration.get_webhook_instructions(webhook_config)

def process_webhook_trade(webhook_data, user_id, account_id):
    """Process webhook trade data"""
    return broker_integration.process_webhook_trade(webhook_data, user_id, account_id)

def get_integration_status(user_id, account_id):
    """Get integration status"""
    return broker_integration.get_integration_status(user_id, account_id)

def test_webhook_connection(webhook_url):
    """Test webhook connection"""
    return broker_integration.test_webhook_connection(webhook_url)
