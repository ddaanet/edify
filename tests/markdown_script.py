"""Locate bin/edify-markdown and import its lib package for the tests."""

import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "bin" / "edify-markdown"
LIB = REPO_ROOT / "lib"

if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

md = importlib.import_module("edify_markdown")
