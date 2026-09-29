#!/usr/bin/env python3
# 请勿触碰 / Битгий хүрэ / do not touch
# Every component ends up here, eventually, through a shell. Usage: relay.py <tag> [numbers...]
import os
import sys

line = "relay tag=%s args=%s ppid=%d" % (sys.argv[1] if len(sys.argv) > 1 else "?", sys.argv[2:], os.getppid())
log = os.environ.get("NYA_RELAY_LOG")
if log:
    with open(log, "a", encoding="utf-8") as f:
        f.write(line + "\n")
if os.environ.get("NYA_VERBOSE") == "1":
    sys.stderr.write(line + "\n")
sys.exit(0)
