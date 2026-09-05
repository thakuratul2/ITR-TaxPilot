"""Automated test runner and verification script for CI/CD pipelines."""

import os
import subprocess
import sys
import time

# Ensure UTF-8 stdout on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")


def run_command(cmd: list[str], description: str) -> bool:
    """Run a shell command and print real-time status."""
    print(f"\n=======================================================")
    print(f"[*] RUNNING: {description}")
    print(f"COMMAND: {' '.join(cmd)}")
    print(f"=======================================================")
    start_time = time.time()
    result = subprocess.run(cmd)
    elapsed = time.time() - start_time

    if result.returncode == 0:
        print(f"[+] PASSED in {elapsed:.2f}s: {description}")
        return True
    else:
        print(f"[-] FAILED with code {result.returncode} in {elapsed:.2f}s: {description}")
        return False


def main():
    """Execute complete test runner pipeline."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    print("=======================================================")
    print("      ITR-TaxPilot CI/CD Test & Quality Runner         ")
    print("=======================================================")

    all_passed = True

    # 1. Pytest Test Suite
    pytest_cmd = [sys.executable, "-m", "pytest", "-v"]
    if not run_command(pytest_cmd, "Backend Test Suite (Pytest)"):
        all_passed = False

    # Summary
    print("\n=======================================================")
    if all_passed:
        print("[+] ALL TESTS & QUALITY CHECKS PASSED SUCCESSFULLY!")
        print("=======================================================")
        sys.exit(0)
    else:
        print("[-] SOME TEST SUITES OR CHECKS FAILED.")
        print("=======================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
