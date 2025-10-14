#!/usr/bin/env python3
"""
Keep System Awake Script
Prevents the system from going to sleep while Trading Journal is running
"""

import time
import threading
import subprocess
import sys
import os
from datetime import datetime

def prevent_sleep_windows():
    """Prevent Windows from going to sleep using ctypes"""
    try:
        import ctypes
        from ctypes import wintypes
        
        # Define constants
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ES_DISPLAY_REQUIRED = 0x00000002
        
        # Set thread execution state
        result = ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )
        
        if result:
            print("✅ System sleep prevention activated (ctypes method)")
            return True
        else:
            print("❌ Failed to set thread execution state")
            return False
            
    except Exception as e:
        print(f"❌ Failed to prevent sleep with ctypes: {e}")
        return False

def prevent_sleep_powershell():
    """Prevent Windows from going to sleep using PowerShell"""
    try:
        # Simplified PowerShell command
        ps_command = 'powercfg /change standby-timeout-ac 0'
        result = subprocess.run(ps_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ System sleep prevention activated (powercfg method)")
            return True
        else:
            print(f"❌ PowerShell command failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to prevent sleep with PowerShell: {e}")
        return False

def restore_sleep_settings():
    """Restore normal sleep settings"""
    try:
        # Restore normal sleep timeout (30 minutes)
        ps_command = 'powercfg /change standby-timeout-ac 30'
        subprocess.run(ps_command, shell=True, capture_output=True)
        print("✅ Sleep settings restored to normal")
    except Exception as e:
        print(f"❌ Failed to restore sleep settings: {e}")

def keep_alive():
    """Keep the system alive by simulating activity"""
    while True:
        try:
            # Simulate minimal mouse movement
            import ctypes
            ctypes.windll.user32.SetCursorPos(0, 0)
            ctypes.windll.user32.SetCursorPos(1, 1)
            
            # Print status every 5 minutes
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"🔄 Keep-alive active at {current_time}")
            
            time.sleep(300)  # 5 minutes
            
        except Exception as e:
            print(f"❌ Keep-alive error: {e}")
            time.sleep(60)  # Retry in 1 minute

def main():
    """Main function to prevent sleep"""
    print("🚀 Starting Trading Journal Keep-Alive System")
    print("=" * 50)
    
    # Try multiple methods to prevent sleep
    sleep_prevented = False
    
    # Method 1: ctypes (most reliable)
    if prevent_sleep_windows():
        sleep_prevented = True
    
    # Method 2: PowerShell powercfg (backup)
    if not sleep_prevented and prevent_sleep_powershell():
        sleep_prevented = True
    
    if not sleep_prevented:
        print("⚠️ Could not prevent sleep, using fallback method only")
    
    # Start keep-alive thread
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    
    print("✅ Keep-alive system started")
    print("💡 System will stay awake while this script is running")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping keep-alive system...")
        restore_sleep_settings()
        print("✅ System sleep prevention disabled")
        sys.exit(0)

if __name__ == "__main__":
    main()
