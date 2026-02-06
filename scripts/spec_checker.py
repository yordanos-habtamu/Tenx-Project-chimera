import os
import re
import sys
from pathlib import Path

def check_file_exists(path):
    if not os.path.exists(path):
        print(f"FAILED: File {path} not found")
        return False
    print(f"PASSED: File {path} exists")
    return True

def check_directory_exists(path):
    if not os.path.isdir(path):
        print(f"FAILED: Directory {path} not found")
        return False
    print(f"PASSED: Directory {path} exists")
    return True

def run_checks():
    print("--- Project Chimera Specification Alignment Check ---")
    
    # Required Project Structure
    required_dirs = ["specs", "src", "tests", "skills", "research", ".github/workflows"]
    required_files = [
        "Dockerfile", 
        "Makefile", 
        "pyproject.toml",
        "specs/_meta.md",
        "specs/technical.md",
        "specs/functional.md",
        "AGENT_RULES.md"
    ]
    
    all_passed = True
    
    print("\nVerifying Project Structure:")
    for d in required_dirs:
        if not check_directory_exists(d): all_passed = False
    for f in required_files:
        if not check_file_exists(f): all_passed = False
        
    # Check if models match tech spec
    print("\nVerifying Database Models Alignment:")
    try:
        from src.database.models import Base
        print("PASSED: Database models are importable")
    except ImportError as e:
        print(f"FAILED: Database models could not be imported: {e}")
        all_passed = False

    # Check for Skills READMEs
    print("\nVerifying Skills Documentation:")
    skills_dir = Path("skills")
    if skills_dir.is_dir():
        for skill_path in skills_dir.iterdir():
            if skill_path.is_dir():
                readme = skill_path / "README.md"
                if readme.exists():
                    print(f"PASSED: Skill '{skill_path.name}' has README.md")
                else:
                    print(f"FAILED: Skill '{skill_path.name}' is missing README.md")
                    all_passed = False
    
    print("\n--- Summary ---")
    if all_passed:
        print("All specification alignment checks PASSED.")
        return 0
    else:
        print("Some specification alignment checks FAILED.")
        return 1

if __name__ == "__main__":
    sys.exit(run_checks())
