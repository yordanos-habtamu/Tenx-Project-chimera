
import logging
import os
import shutil
from src.api.app import app
from src.api.dashboard import get_system_logs
import asyncio

async def verify_logging():
    print("Verifying File Logging...")
    
    # Clean up previous logs for clean test
    if os.path.exists("logs/chimera.log"):
        os.remove("logs/chimera.log")
        
    # Trigger logging by simulating app startup (which logs info)
    # We can just use the logger directly since it's configured in app.py
    logger = logging.getLogger("src.api.app")
    logger.info("Test Log Entry 1")
    logger.warning("Test Log Entry 2")
    
    # 1. Check File Existence
    if os.path.exists("logs/chimera.log"):
        print("PASS: Log file created")
        with open("logs/chimera.log", "r") as f:
            content = f.read()
            if "Test Log Entry 1" in content:
                print("PASS: Content written to file")
            else:
                print("FAIL: Content missing from file")
    else:
        print("FAIL: Log file not created")
        return

    # 2. Check API Parsing
    print("\nVerifying API Parsing...")
    result = await get_system_logs(limit=10, level="ALL")
    logs = result["logs"]
    
    if len(logs) >= 2:
        print(f"PASS: API returned {len(logs)} logs")
        latest = logs[0]
        # Logs are reversed, so latest should be the last one written
        if "Test Log Entry 2" in latest["message"] and latest["level"] == "WARNING":
             print("PASS: Log parsing correct (Message & Level)")
        else:
             print(f"FAIL: Log parsing mismatch. Got: {latest}")
    else:
        print(f"FAIL: API returned insufficient logs: {len(logs)}")

if __name__ == "__main__":
    asyncio.run(verify_logging())
