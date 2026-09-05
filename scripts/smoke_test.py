"""Post-deployment smoke test script validating running live environment."""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error

# Ensure UTF-8 output on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")


def check_endpoint(url: str, expected_status: int = 200) -> bool:
    """Send HTTP GET and verify status code."""
    print(f"[*] Probing {url} ...", end=" ")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ITR-TaxPilot-SmokeTester/1.0", "X-Request-ID": "req_smoke_probe"},
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            status = response.getcode()
            if status == expected_status:
                print(f"[+] OK (HTTP {status})")
                return True
            else:
                print(f"[-] FAILED (Expected {expected_status}, got {status})")
                return False
    except urllib.error.HTTPError as e:
        if e.code == expected_status:
            print(f"[+] OK (HTTP {e.code})")
            return True
        print(f"[-] HTTP Error: {e.code} {e.reason}")
        return False
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="ITR-TaxPilot Production Smoke Tester")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of deployed service")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    print("=======================================================")
    print("         ITR-TaxPilot Production Smoke Tester          ")
    print(f" Target: {base_url}")
    print("=======================================================")

    checks = [
        (f"{base_url}/health", 200),
        (f"{base_url}/api/v1/health", 200),
        (f"{base_url}/api/v1/metrics", 200),
        (f"{base_url}/api/v1/admin/ai-providers", 200),
    ]

    all_ok = True
    for url, code in checks:
        if not check_endpoint(url, code):
            all_ok = False

    print("=======================================================")
    if all_ok:
        print("[+] ALL SMOKE TESTS PASSED! System is fully operational.")
        print("=======================================================")
        sys.exit(0)
    else:
        print("[-] SMOKE TESTS DETECTED FAILURES! Review logs.")
        print("=======================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
