#!/usr/bin/env python3
"""Common helpers for waterlint pytest suites."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PATH_MAIN =		ROOT
PATH_EXAMPLES =		PATH_MAIN / "examples-python"
PATH_EXAMPLES_JSON =	PATH_MAIN / "examples-json"
PATH_MODULE =		PATH_MAIN / "src" / "sdv" / "doc" / "waterloo"

DIR_EXAMPLES =		str(PATH_EXAMPLES)
DIR_EXAMPLES_JSON =	str(PATH_EXAMPLES_JSON)

DIR_DOC =		str(ROOT / "doc")
DIR_MODULE = 		str(PATH_MODULE)
DIR_SCHEMA =		str(PATH_MODULE / "schema")

PATH_IDE_PLUGINS =	ROOT / ".." / "package_ide-plugins"
PATH_PYGMENTS =		PATH_IDE_PLUGINS / "pygments"
PATH_VSCODE =		PATH_IDE_PLUGINS / "vscode"

# In our developer workspace we use the latest pre-release.
# In a stable environment we use the official executable.
#if Path("./waterlint.py").exists():
#	WATERLINT = ROOT / "waterlint.py"
#else:
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

