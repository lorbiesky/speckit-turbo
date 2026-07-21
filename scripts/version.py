#!/usr/bin/env python3
"""Print the Spec Kit Turbo version from a repository or installed project."""
from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
path = root / "manifest.json"
if not path.exists():
    path = root / ".specify" / "turbo" / "manifest.json"
try:
    print(json.loads(path.read_text(encoding="utf-8"))["turboVersion"])
except (OSError, KeyError, json.JSONDecodeError) as exc:
    print(f"Unable to read Spec Kit Turbo manifest: {exc}", file=sys.stderr)
    raise SystemExit(2)
