#!/usr/bin/env python3
"""Checks whether the server is running by asking it if it is a teapot. Exit 0 means teapot."""
import sys
import urllib.error
import urllib.request

try:
    urllib.request.urlopen("http://127.0.0.1:8418/api/why", timeout=2)
except urllib.error.HTTPError as e:
    sys.exit(0 if e.code == 418 else 1)
except OSError:
    sys.exit(2)
sys.exit(1)
