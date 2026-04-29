#!/usr/bin/env python3
"""Common helpers for waterlint pytest suites."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
print(ROOT)

PATH_EXAMPLES =		ROOT / "doc" / "examples"
PATH_EXAMPLES_JSON =	ROOT / "examples-json"

DIR_EXAMPLES =		str(ROOT / "doc" / "examples")
DIR_EXAMPLES_JSON =	str(PATH_EXAMPLES_JSON)

# In our developer workspace we use the latest pre-release.
# In a stable environment we use the official executable.
if Path("./waterlint.py").exists():
	WATERLINT = ROOT / "waterlint.py"
else:
	WATERLINT = "waterlint"

def run_waterlint(*args: str) -> subprocess.CompletedProcess[str]:
	"""Run waterlint with project-local PYTHONPATH and return completed process."""
	env = os.environ.copy()
	env["PYTHONPATH"] = os.pathsep.join([str(ROOT), env.get("PYTHONPATH", "")])

	cmd = [str(WATERLINT), *args]

	return subprocess.run(
		cmd,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
		env=env,
		cwd=ROOT,
	)

