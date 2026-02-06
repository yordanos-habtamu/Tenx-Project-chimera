import os
import sys

from src.api.app import app


def verify_frontend():
    print("Verifying Frontend Configuration...")

    # 1. Check directory existence
    if not os.path.exists("src/static"):
        print("FAIL: src/static directory missing")
        sys.exit(1)

    required_files = ["index.html", "css/style.css", "js/app.js", "js/api.js"]
    for f in required_files:
        if not os.path.exists(f"src/static/{f}"):
            print(f"FAIL: Missing file src/static/{f}")
            sys.exit(1)

    print("PASS: Static files present")

    # 2. Check FastAPI Mount
    routes = [route.path for route in app.routes]
    print(f"Routes found: {routes}")

    dashboard_route = next(
        (r for r in app.routes if getattr(r, "path", "") == "/dashboard"), None
    )

    if dashboard_route:
        print("PASS: /dashboard route mounted")
    else:
        print("FAIL: /dashboard route NOT found")
        sys.exit(1)

    print("Frontend Verification Successful!")


if __name__ == "__main__":
    verify_frontend()
