
import subprocess
import time
import os
import requests
import sys

def verify_logging_subprocess():
    print("Verifying File Logging (Subprocess Method)...")
    
    # Clean prev logs
    if os.path.exists("logs/chimera.log"):
        os.remove("logs/chimera.log")
        
    # Start the App in a subprocess to ensure clean logging config
    # We use a short timeout and just check if log file appears
    print("Starting app...")
    process = subprocess.Popen(
        ["uv", "run", "python3", "src/main.py", "--test-import-only"], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    # Wait for a few seconds for initialization logs to flush
    time.sleep(8)
    
    # Check File
    if os.path.exists("logs/chimera.log"):
        print("PASS: Log file created")
        with open("logs/chimera.log", "r") as f:
            content = f.read()
            if "Initializing database" in content or "Starting Project Chimera API" in content:
                 print("PASS: App logs written to file")
                 print(f"Log Preview: {content[:200]}...")
            else:
                 print("FAIL: Log file empty or missing expected content")
    else:
        print("FAIL: Log file not created")
        
    process.terminate()

if __name__ == "__main__":
    verify_logging_subprocess()
