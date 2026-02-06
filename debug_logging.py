import os
import subprocess
import time


def debug_logging():
    print("Debugging File Logging...")

    if os.path.exists("logs/chimera.log"):
        os.remove("logs/chimera.log")

    print(f"CWD: {os.getcwd()}")

    # Run slightly longer to ensure startup
    cmd = ["uv", "run", "python3", "-m", "src.main"]
    print(f"Running: {' '.join(cmd)}")

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    time.sleep(10)
    process.terminate()

    stdout, stderr = process.communicate()

    print("--- STDOUT ---")
    print(stdout[:500])
    print("\n--- STDERR ---")
    print(stderr[:500])

    if os.path.exists("logs/chimera.log"):
        print("\nPASS: Log file exists.")
        print(f"Size: {os.path.getsize('logs/chimera.log')} bytes")
    else:
        print("\nFAIL: Log file does NOT exist.")
        # Check permissions?
        print(f"Logs dir exists? {os.path.exists('logs')}")


if __name__ == "__main__":
    debug_logging()
