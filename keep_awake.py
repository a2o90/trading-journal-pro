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
    """Prevent Windows from going to sleep using PowerShell"""
    try:
        # PowerShell command to prevent sleep
        ps_command = """
        Add-Type -TypeDefinition @"
        using System;
        using System.Runtime.InteropServices;
        public class PowerManagement {
            [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
            public static extern uint SetThreadExecutionState(uint esFlags);
        }
"@
        [PowerManagement]::SetThreadExecutionState(0x80000000 -bor 0x00000001)
        """
        
        # Run PowerShell command
        subprocess.run([
            "powershell", "-Command", ps_command
        ], check=True, capture_output=True)
        
        print("✅ System sleep prevention activated")
        return True
        
    except Exception as e:
        print(f"❌ Failed to prevent sleep: {e}")
        return False

def keep_alive():
    """Keep the system alive by simulating activity"""
    while True:
        try:
            # Simulate mouse movement (minimal)
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
    
    # Prevent sleep
    if not prevent_sleep_windows():
        print("⚠️ Could not prevent sleep, using fallback method")
    
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
        print("✅ System sleep prevention disabled")
        sys.exit(0)

if __name__ == "__main__":
    main()
