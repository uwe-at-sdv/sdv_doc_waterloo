#!/usr/bin/env python3
"""Project-level consistency checks for Waterloo rule IDs.

This test acts as a lightweight guardrail against documentation drift.
Waterloo rule IDs are introduced normatively in the reST docs, primarily
in ``doc/source/format.rst`` and ``doc/source/tools.rst``. The source tree
is expected to use those same rule IDs in tracer messages, validation
errors, and related diagnostics. If source code starts referring to a new
rule ID that is not documented, or if a rule ID is documented more than
once, the project can become hard to reason about for readers and for the
diagnostic tooling.

The check therefore scans Python string literals for rule-like tokens,
collects the documented rule IDs from the normative reST files, and then
asserts that the two views stay aligned. This keeps the taxonomy stable
without requiring every caller to know the full rule inventory by heart.
"""

from __future__ import annotations

import ast
import re
from collections import Counter, defaultdict
from pathlib import Path

from pytest_common import ROOT

RULE_ID_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d{3})\b")
BRACKETED_RULE_RE = re.compile(r"^\s*[*-]\s+\[([A-Z][A-Z0-9]+-\d{3})\]\s+--")
OBSOLETE_RULE_RE = re.compile(r"^\s*[*-]\s+([A-Z][A-Z0-9]+-\d{3})\s+--\s+.*\b(?:Obsolete|obsolete|Superseded|superseded|Implied by|implied by)\b")
# Internal sentinel used by the diagnostics layer; it is not a public rule ID.
IGNORED_CODE_RULE_IDS = {"YYY-999"}

PYTHON_ROOTS = (
	ROOT / "src",
	ROOT / "pytest",
	ROOT / "examples-python",
	ROOT / "examples-diagnostics-python",
	ROOT / "doc" / "examples",
)

RST_RULE_DOCS = (
	ROOT / "doc" / "source" / "format.rst",
	ROOT / "doc" / "source" / "tools.rst",
)


def _iter_python_files() -> list[Path]:
	files: set[Path] = set()
	for root in PYTHON_ROOTS:
		if root.exists():
			files.update(root.rglob("*.py"))
	return sorted(files)


def _collect_rule_ids_from_python(path: Path) -> set[str]:
	tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
	ids: set[str] = set()
	for node in ast.walk(tree):
		if isinstance(node, ast.Constant) and isinstance(node.value, str):
			ids.update(RULE_ID_RE.findall(node.value))
	return ids


def _collect_rule_ids_from_rst(path: Path) -> dict[str, list[str]]:
	locations: dict[str, list[str]] = defaultdict(list)
	for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
		match = BRACKETED_RULE_RE.match(line)
		if match:
			locations[match.group(1)].append(f"{path.name}:{lineno}")
			continue
		match = OBSOLETE_RULE_RE.match(line)
		if match:
			locations[match.group(1)].append(f"{path.name}:{lineno}")
	return locations


def test_rule_ids_used_in_source_are_defined_in_rst() -> None:
	"""Check that all rule IDs mentioned in source strings are defined in the docs."""
	code_rule_ids: set[str] = set()
	for path in _iter_python_files():
		code_rule_ids.update(_collect_rule_ids_from_python(path))
	code_rule_ids.difference_update(IGNORED_CODE_RULE_IDS)

	defs: dict[str, list[str]] = defaultdict(list)
	for path in RST_RULE_DOCS:
		for rid, locs in _collect_rule_ids_from_rst(path).items():
			defs[rid].extend(locs)

	missing = sorted(rid for rid in code_rule_ids if rid not in defs)
	assert not missing, f"Rule IDs used in source but not defined in format/tools docs: {missing}"

	duplicates = {rid: locs for rid, locs in defs.items() if len(locs) != 1}
	assert not duplicates, f"Rule IDs defined more than once in format/tools docs: {duplicates}"
