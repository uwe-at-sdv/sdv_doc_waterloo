#!/usr/bin/env python3
"""Pytests for the Waterloo VS Code extension backend protocol."""

from __future__ import annotations

import inspect
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import sdv.doc.waterloo.docitem_helper as docitem_helper


PATH_IDE_PLUGINS = Path(__file__).resolve().parents[1]
PATH_BACKEND = PATH_IDE_PLUGINS / "vscode" / "extension_waterloo_commands.py"
PATH_PACKAGE_JSON = PATH_IDE_PLUGINS / "vscode" / "package.json"
PATH_EXTENSION_JS = PATH_IDE_PLUGINS / "vscode" / "extension.js"
PATH_DOCITEM_HELPER = Path(docitem_helper.__file__).resolve()


def _run_backend(payload: dict[str, Any]) -> dict[str, Any]:
	result = subprocess.run(
		[sys.executable, str(PATH_BACKEND)],
		input=json.dumps(payload, separators=(",", ":")) + "\n",
		text=True,
		capture_output=True,
		check=False,
		timeout=30,
	)
	assert result.returncode == 0, result.stderr or result.stdout
	lines = [line for line in result.stdout.splitlines() if line.strip()]
	assert lines, "backend produced no JSON response"
	response = json.loads(lines[-1])
	assert isinstance(response, dict)
	return response


def _assert_successful_backend_validation(response: dict[str, Any], *, command: str, kind: str, qid: str) -> None:
	assert response["ok"] is True
	assert response["command"] == command
	assert response["data"]["kind"] == kind
	assert response["data"]["qualified_identifier"] == qid
	assert response["diagnostics_summary"]["warning"] == 0
	assert response["diagnostics_summary"]["error"] == 0


def _docitem_helper_module_payload(command: str) -> dict[str, Any]:
	return {
		"version": 1,
		"command": command,
		"kind": "module",
		"source_fragment": "",
		"source_file": str(PATH_DOCITEM_HELPER),
		"line": 0,
		"ignore": ["PNB-004", "VLII-001"],
		"include_diagnostics": True,
	}


def _docitem_helper_tracer_class_payload(command: str) -> dict[str, Any]:
	return {
		"version": 1,
		"command": command,
		"kind": "class",
		"source_fragment": "class tracer: pass\n",
		"source_file": str(PATH_DOCITEM_HELPER),
		# VS Code sends zero-based editor line numbers.
		"line": inspect.getsourcelines(docitem_helper.tracer)[1] - 1,
		"ignore": ["PNB-004", "VLII-001"],
		"include_diagnostics": True,
	}


def test_backend_validates_docitem_helper_docstring() -> None:
	response = _run_backend(_docitem_helper_module_payload("validate_docstring"))
	_assert_successful_backend_validation(response, command="validate_docstring", kind="module", qid="docitem_helper")


def test_backend_validates_docitem_helper_coverage() -> None:
	response = _run_backend(_docitem_helper_module_payload("validate_coverage_of_docstring"))
	_assert_successful_backend_validation(response, command="validate_coverage_of_docstring", kind="module", qid="docitem_helper")


def test_backend_validates_docitem_helper_tracer_coverage() -> None:
	response = _run_backend(_docitem_helper_tracer_class_payload("validate_coverage_of_docstring"))
	_assert_successful_backend_validation(response, command="validate_coverage_of_docstring", kind="class", qid="docitem_helper.tracer")


def test_package_json_commands_are_registered_in_extension_js() -> None:
	package = json.loads(PATH_PACKAGE_JSON.read_text(encoding="utf-8"))
	contributed = {
		entry["command"]
		for entry in package.get("contributes", {}).get("commands", [])
		if isinstance(entry, dict) and isinstance(entry.get("command"), str)
	}
	extension_js = PATH_EXTENSION_JS.read_text(encoding="utf-8")
	registered = set(re.findall(r"registerCommand\(['\"]([^'\"]+)['\"]", extension_js))
	assert contributed <= registered


def test_package_json_menu_commands_are_contributed() -> None:
	package = json.loads(PATH_PACKAGE_JSON.read_text(encoding="utf-8"))
	contributed = {
		entry["command"]
		for entry in package.get("contributes", {}).get("commands", [])
		if isinstance(entry, dict) and isinstance(entry.get("command"), str)
	}
	menu_items = package.get("contributes", {}).get("menus", {}).get("waterloo.context", [])
	menu_commands = {
		entry["command"]
		for entry in menu_items
		if isinstance(entry, dict) and isinstance(entry.get("command"), str)
	}
	assert menu_commands <= contributed
