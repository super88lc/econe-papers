#!/usr/bin/env python3
import subprocess
import sys

# Run the daily_update_v2.py and capture errors
result = subprocess.run(
    [sys.executable, "daily_update_v2.py"],
    capture_output=True,
    text=True,
    cwd="/Users/apple/.openclaw/workspace/econe-papers/backend"
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
