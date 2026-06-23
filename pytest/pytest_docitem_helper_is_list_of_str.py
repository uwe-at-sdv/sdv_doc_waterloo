#!/usr/bin/env python3
"""Pytests for the is_list_of_str TypeGuard demo example."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from pytest_common import ROOT


EXAMPLE = Path(__file__).resolve().parent / "docitem_helper_is_list_of_str_demo.py"


def test_is_list_of_str_example_runs() -> None:
	"""The example script should run without runtime errors."""
	result = subprocess.run(
		[sys.executable, str(EXAMPLE)],
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
		cwd=ROOT.parent,
	)
	assert result.returncode == 0, result.stderr


def test_is_list_of_str_example_shows_typeguard_narrowing() -> None:
	"""mypy should reveal list[str] in the TypeGuard branch."""
	result = subprocess.run(
		[sys.executable, "-m", "mypy", str(EXAMPLE)],
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
		cwd=ROOT.parent,
	)
	assert result.returncode == 0, result.stderr
	assert 'Revealed type is "list[str]"' in result.stdout, result.stdout
