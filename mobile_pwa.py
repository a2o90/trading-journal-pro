#!/usr/bin/env python3
"""
Mobile PWA Module
Provides Progressive Web App functionality, push notifications, and mobile optimization
"""

import json
import os
from datetime import datetime, timedelta
import base64

class MobilePWAManager:
    def __init__(self):
        self.service_worker_code = self._generate_service_worker()
        self.manifest_code = self._generate_manifest()
        self.push_notifications_enabled = False
        
    def _generate_service_worker(self):
        """Generate Service Worker code for PWA functionality"""
        return """
// Trading Journal Pro - Service Worker
const CACHE_NAME = 'trading-journal-v1';
const urlsToCache = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js'
];

// Install event
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            }
        )
    );
});

// Push notification event
self.addEventListener('push', function(event) {
    const options = {
        body: event.data ? event.data.text() : 'Trading reminder!',
        icon: '/icon-192x192.png',
        badge: '/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Open Trading Journal',
                icon: '/icon-192x192.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/icon-192x192.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Trading Journal Pro', options)
    );
});

// Notification click event
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});
"""
    
    def _generate_manifest(self):
        """Generate Web App Manifest for PWA"""
        return {
            "name": "Trading Journal Pro",
            "short_name": "TradingJournal",
            "description": "Professional trading journal with AI insights",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#1f77b4",
            "orientation": "portrait-primary",
            "icons": [
                {
                    "src": "/icon-72x72.png",
                    "sizes": "72x72",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/icon-96x96.png",
                    "sizes": "96x96",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/icon-128x128.png",
                    "sizes": "128x128",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/icon-144x144.png",
                    "sizes": "144x144",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/icon-152x152.png",
                    "sizes": "152x152",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/icon-384x384.png",
                    "sizes": "384x384",
                    "type": "image/png",
                    "purpose": "any maskable"
                },
                {
                    "src": "/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable"
                }
            ],
            "categories": ["finance", "productivity", "business"],
            "screenshots": [
                {
                    "src": "/screenshot-mobile.png",
                    "sizes": "390x844",
                    "type": "image/png",
                    "form_factor": "narrow"
                }
            ]
        }
    
    def generate_pwa_html(self):
        """Generate HTML for PWA setup"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Journal Pro - PWA</title>
    
    <!-- PWA Meta Tags -->
    <meta name="application-name" content="Trading Journal Pro">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="Trading Journal Pro">
    <meta name="description" content="Professional trading journal with AI insights">
    <meta name="format-detection" content="telephone=no">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="msapplication-config" content="/browserconfig.xml">
    <meta name="msapplication-TileColor" content="#1f77b4">
    <meta name="msapplication-tap-highlight" content="no">
    <meta name="theme-color" content="#1f77b4">
    
    <!-- Apple Touch Icons -->
    <link rel="apple-touch-icon" href="/icon-152x152.png">
    <link rel="apple-touch-icon" sizes="152x152" href="/icon-152x152.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/icon-180x180.png">
    <link rel="apple-touch-icon" sizes="167x167" href="/icon-167x167.png">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
    <link rel="shortcut icon" href="/favicon.ico">
    
    <!-- Web App Manifest -->
    <link rel="manifest" href="/manifest.json">
    
    <!-- Splash Screens -->
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    
    <style>
        /* PWA-specific styles */
        body {{
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .pwa-container {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 400px;
            width: 90%;
        }}
        
        .pwa-icon {{
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #1f77b4, #ff7f0e);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            color: white;
        }}
        
        .pwa-title {{
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .pwa-subtitle {{
            color: #666;
            margin-bottom: 30px;
            line-height: 1.5;
        }}
        
        .pwa-features {{
            text-align: left;
            margin: 30px 0;
        }}
        
        .pwa-feature {{
            display: flex;
            align-items: center;
            margin: 15px 0;
            color: #555;
        }}
        
        .pwa-feature-icon {{
            margin-right: 15px;
            font-size: 20px;
        }}
        
        .install-button {{
            background: linear-gradient(135deg, #1f77b4, #ff7f0e);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin: 10px;
            transition: transform 0.2s;
        }}
        
        .install-button:hover {{
            transform: translateY(-2px);
        }}
        
        .install-button:disabled {{
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }}
        
        .status {{
            margin-top: 20px;
            padding: 15px;
            border-radius: 10px;
            font-weight: bold;
        }}
        
        .status.success {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .status.error {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        .status.info {{
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }}
    </style>
</head>
<body>
    <div class="pwa-container">
        <div class="pwa-icon">📈</div>
        <h1 class="pwa-title">Trading Journal Pro</h1>
        <p class="pwa-subtitle">Professional trading journal with AI insights</p>
        
        <div class="pwa-features">
            <div class="pwa-feature">
                <span class="pwa-feature-icon">📱</span>
                <span>Install as mobile app</span>
            </div>
            <div class="pwa-feature">
                <span class="pwa-feature-icon">🔔</span>
                <span>Push notifications</span>
            </div>
            <div class="pwa-feature">
                <span class="pwa-feature-icon">⚡</span>
                <span>Offline functionality</span>
            </div>
            <div class="pwa-feature">
                <span class="pwa-feature-icon">🤖</span>
                <span>AI-powered insights</span>
            </div>
        </div>
        
        <button id="install-button" class="install-button">
            📱 Install App
        </button>
        
        <button id="notify-button" class="install-button">
            🔔 Enable Notifications
        </button>
        
        <div id="status" class="status" style="display: none;"></div>
    </div>
    
    <script>
        let deferredPrompt;
        let isInstalled = false;
        
        // Check if app is already installed
        if (window.matchMedia('(display-mode: standalone)').matches) {{
            isInstalled = true;
            document.getElementById('install-button').textContent = '✅ App Installed';
            document.getElementById('install-button').disabled = true;
        }}
        
        // Listen for beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (e) => {{
            e.preventDefault();
            deferredPrompt = e;
            
            if (!isInstalled) {{
                document.getElementById('install-button').style.display = 'inline-block';
            }}
        }});
        
        // Install button click
        document.getElementById('install-button').addEventListener('click', async () => {{
            if (deferredPrompt) {{
                deferredPrompt.prompt();
                const {{ outcome }} = await deferredPrompt.userChoice;
                
                if (outcome === 'accepted') {{
                    showStatus('App installed successfully!', 'success');
                    document.getElementById('install-button').textContent = '✅ App Installed';
                    document.getElementById('install-button').disabled = true;
                }} else {{
                    showStatus('App installation cancelled.', 'info');
                }}
                
                deferredPrompt = null;
            }} else {{
                showStatus('App installation not available on this device.', 'error');
            }}
        }});
        
        // Notification button click
        document.getElementById('notify-button').addEventListener('click', async () => {{
            if ('Notification' in window) {{
                const permission = await Notification.requestPermission();
                
                if (permission === 'granted') {{
                    showStatus('Notifications enabled! You will receive trading reminders.', 'success');
                    document.getElementById('notify-button').textContent = '✅ Notifications Enabled';
                    document.getElementById('notify-button').disabled = true;
                    
                    // Register service worker for push notifications
                    if ('serviceWorker' in navigator) {{
                        navigator.serviceWorker.register('/sw.js')
                            .then(registration => {{
                                console.log('Service Worker registered:', registration);
                            }})
                            .catch(error => {{
                                console.log('Service Worker registration failed:', error);
                            }});
                    }}
                }} else {{
                    showStatus('Notifications blocked. Please enable them in browser settings.', 'error');
                }}
            }} else {{
                showStatus('Notifications not supported on this device.', 'error');
            }}
        }});
        
        function showStatus(message, type) {{
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `status ${{type}}`;
            status.style.display = 'block';
            
            setTimeout(() => {{
                status.style.display = 'none';
            }}, 5000);
        }}
        
        // Check if notifications are already enabled
        if ('Notification' in window && Notification.permission === 'granted') {{
            document.getElementById('notify-button').textContent = '✅ Notifications Enabled';
            document.getElementById('notify-button').disabled = true;
        }}
    </script>
</body>
</html>
"""
    
    def generate_quick_log_form(self, user_id):
        """Generate quick logging form for mobile"""
        return {
            'symbol': '',
            'side': 'Long',
            'entry_price': 0.0,
            'exit_price': 0.0,
            'quantity': 1.0,
            'notes': '',
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
    
    def create_mobile_optimized_trade_form(self):
        """Create mobile-optimized trade entry form"""
        return """
        <div class="mobile-trade-form">
            <h3>⚡ Quick Trade Entry</h3>
            <form id="quick-trade-form">
                <div class="form-group">
                    <label>Symbol</label>
                    <input type="text" id="symbol" placeholder="e.g., EURUSD" required>
                </div>
                
                <div class="form-group">
                    <label>Side</label>
                    <select id="side">
                        <option value="Long">📈 Long</option>
                        <option value="Short">📉 Short</option>
                    </select>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label>Entry Price</label>
                        <input type="number" id="entry_price" step="0.00001" required>
                    </div>
                    <div class="form-group">
                        <label>Exit Price</label>
                        <input type="number" id="exit_price" step="0.00001" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Quantity</label>
                    <input type="number" id="quantity" value="1" step="0.01" required>
                </div>
                
                <div class="form-group">
                    <label>Notes (Optional)</label>
                    <textarea id="notes" placeholder="Quick notes..."></textarea>
                </div>
                
                <button type="submit" class="submit-button">
                    ✅ Save Trade
                </button>
            </form>
        </div>
        """
    
    def generate_push_notification_schedule(self, user_preferences):
        """Generate push notification schedule based on user preferences"""
        notifications = []
        
        # Market open reminders
        if user_preferences.get('market_open_reminder', False):
            notifications.append({
                'time': '09:00',
                'title': 'Market Open',
                'body': 'Markets are opening! Time to check your trading plan.',
                'type': 'market_open'
            })
        
        # Market close reminders
        if user_preferences.get('market_close_reminder', False):
            notifications.append({
                'time': '17:00',
                'title': 'Market Close',
                'body': 'Markets are closing. Time to review your trades.',
                'type': 'market_close'
            })
        
        # Journal reminder
        if user_preferences.get('journal_reminder', False):
            notifications.append({
                'time': '20:00',
                'title': 'Journal Time',
                'body': 'Don\'t forget to log your trades and review your performance.',
                'type': 'journal'
            })
        
        # Weekly review
        if user_preferences.get('weekly_review', False):
            notifications.append({
                'time': '18:00',
                'day': 'friday',
                'title': 'Weekly Review',
                'body': 'Time for your weekly trading review and analysis.',
                'type': 'weekly_review'
            })
        
        return notifications
    
    def create_mobile_css(self):
        """Generate mobile-optimized CSS"""
        return """
        /* Mobile PWA Styles */
        @media (max-width: 768px) {
            .mobile-trade-form {
                padding: 20px;
                background: white;
                border-radius: 15px;
                margin: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            
            .mobile-trade-form h3 {
                text-align: center;
                color: #333;
                margin-bottom: 25px;
                font-size: 24px;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #555;
            }
            
            .form-group input,
            .form-group select,
            .form-group textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            
            .form-group input:focus,
            .form-group select:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #1f77b4;
            }
            
            .form-row {
                display: flex;
                gap: 15px;
            }
            
            .form-row .form-group {
                flex: 1;
            }
            
            .submit-button {
                width: 100%;
                background: linear-gradient(135deg, #1f77b4, #ff7f0e);
                color: white;
                border: none;
                padding: 15px;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                transition: transform 0.2s;
            }
            
            .submit-button:hover {
                transform: translateY(-2px);
            }
            
            .submit-button:active {
                transform: translateY(0);
            }
            
            /* Mobile navigation */
            .mobile-nav {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: white;
                border-top: 1px solid #e1e5e9;
                display: flex;
                justify-content: space-around;
                padding: 10px 0;
                z-index: 1000;
            }
            
            .mobile-nav-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-decoration: none;
                color: #666;
                font-size: 12px;
                transition: color 0.3s;
            }
            
            .mobile-nav-item.active {
                color: #1f77b4;
            }
            
            .mobile-nav-item i {
                font-size: 20px;
                margin-bottom: 4px;
            }
            
            /* Mobile cards */
            .mobile-card {
                background: white;
                border-radius: 15px;
                padding: 20px;
                margin: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .mobile-card h4 {
                margin: 0 0 15px 0;
                color: #333;
                font-size: 18px;
            }
            
            /* Mobile metrics */
            .mobile-metrics {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin: 20px;
            }
            
            .mobile-metric {
                background: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .mobile-metric-value {
                font-size: 24px;
                font-weight: bold;
                color: #1f77b4;
                margin-bottom: 5px;
            }
            
            .mobile-metric-label {
                font-size: 14px;
                color: #666;
            }
            
            /* Mobile buttons */
            .mobile-button {
                width: 100%;
                padding: 15px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                margin: 10px 0;
                transition: all 0.3s;
            }
            
            .mobile-button.primary {
                background: linear-gradient(135deg, #1f77b4, #ff7f0e);
                color: white;
            }
            
            .mobile-button.secondary {
                background: #f8f9fa;
                color: #333;
                border: 2px solid #e1e5e9;
            }
            
            .mobile-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
        }
        
        /* PWA-specific styles */
        @media (display-mode: standalone) {
            body {
                padding-bottom: 0;
            }
            
            .mobile-nav {
                display: none;
            }
        }
        """

# Global instance
mobile_pwa = MobilePWAManager()

# Convenience functions
def get_pwa_manifest():
    """Get PWA manifest"""
    return mobile_pwa._generate_manifest()

def get_service_worker():
    """Get service worker code"""
    return mobile_pwa.service_worker_code

def get_pwa_html():
    """Get PWA setup HTML"""
    return mobile_pwa.generate_pwa_html()

def get_mobile_css():
    """Get mobile CSS"""
    return mobile_pwa.create_mobile_css()

def get_quick_log_form(user_id):
    """Get quick log form for mobile"""
    return mobile_pwa.generate_quick_log_form(user_id)

def get_push_notification_schedule(user_preferences):
    """Get push notification schedule"""
    return mobile_pwa.generate_push_notification_schedule(user_preferences)
