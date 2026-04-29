#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from pytest_common import WATERLINT, ROOT, DIR_EXAMPLES, PATH_VSCODE

import pytest

BACKEND = PATH_VSCODE / "extension_waterloo_commands.py"

def _build_env() -> dict[str, str]:
	env = os.environ.copy()
	parts = [str(ROOT / "package_main" / "src"), str(ROOT)]
	if env.get("PYTHONPATH"):
		parts.append(env["PYTHONPATH"])
	env["PYTHONPATH"] = os.pathsep.join(parts)
	return env


def _run_backend(command: str, kind: str, source_fragment: str) -> tuple[dict[str, object], str]:
	payload = {
		"version": 1,
		"command": command,
		"kind": kind,
		"source_fragment": source_fragment,
	}
	res = subprocess.run(
		[sys.executable, str(BACKEND)],
		input=json.dumps(payload),
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
		cwd=ROOT,
		env=_build_env(),
	)
	assert res.stdout.strip(), f"backend returned empty stdout (stderr={res.stderr!r})"
	data = json.loads(res.stdout)
	assert data.get("ok") is True, f"backend not ok: {data}\nstderr={res.stderr}"
	node = data.get("data")
	assert isinstance(node, dict), f"missing data node: {data}"
	tmp_file = node.get("tmp_file")
	assert isinstance(tmp_file, str) and tmp_file, f"missing tmp_file: {data}"
	p = Path(tmp_file)
	assert p.exists(), f"tmp_file does not exist: {tmp_file}"
	return data, p.read_text(encoding="utf-8")


def _run_backend_json(payload: dict[str, object]) -> dict[str, object]:
	res = subprocess.run(
		[sys.executable, str(BACKEND)],
		input=json.dumps(payload),
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
		cwd=ROOT,
		env=_build_env(),
	)
	assert res.stdout.strip(), f"backend returned empty stdout (stderr={res.stderr!r})"
	return json.loads(res.stdout)


def _error_rule_ids(data: dict[str, object]) -> list[str]:
	diag = data.get("diagnostics", {})
	if not isinstance(diag, dict):
		return []
	errs = diag.get("__WTRL_ERROR__", [])
	if not isinstance(errs, list):
		return []
	out: list[str] = []
	for entry in errs:
		if isinstance(entry, dict):
			rid = entry.get("rule-id")
			if isinstance(rid, str):
				out.append(rid)
	return out


def _strip_triple_quotes(text: str) -> str:
	lines = text.splitlines()
	if lines and lines[0].strip() == 'r"""':
		lines = lines[1:]
	if lines and lines[-1].strip() == '"""':
		lines = lines[:-1]
	return "\n".join(lines).rstrip() + "\n"


def _extract_parameter_labels(docstring_body: str) -> list[str]:
	lines = docstring_body.splitlines()
	in_parameters = False
	out: list[str] = []
	for line in lines:
		if line.strip() == "Parameters:":
			in_parameters = True
			continue
		if not in_parameters:
			continue
		if line and not line.startswith("\t") and line.endswith(":"):
			break
		if line.startswith("\t") and not line.startswith("\t\t") and line.endswith(":"):
			label = line.strip()[:-1]
			if label:
				out.append(label)
	return out


def _validate_structural_only(tmp_path: Path, generated_docstring_literal: str) -> None:
	doc_for_validate = _strip_triple_quotes(generated_docstring_literal)
	in_file = tmp_path / "generated_docstring.txt"
	in_file.write_text(doc_for_validate, encoding="utf-8")
	res = subprocess.run(
		[str(WATERLINT), "validate", "--in", str(in_file)],
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
		cwd=ROOT,
		env=_build_env(),
	)
	assert res.returncode == 0, (
		f"waterlint validate --in failed\nstdout:\n{res.stdout}\nstderr:\n{res.stderr}\n"
		f"doc:\n{doc_for_validate}"
	)


@pytest.mark.parametrize(
	"command,kind,source_fragment,expected_params,expected_return_snippet",
	[
		("generate_minimal_docstring_to_tmp", "module", "", [], None),
		("generate_minimal_docstring_to_tmp", "class", "class X:\n    pass\n", [], None),
		("generate_minimal_docstring_to_tmp", "function", "def f(a: int, *, b: str) -> None: pass\n", ["a", "b"], None),
		("generate_minimal_docstring_to_tmp", "method", "def m(self, x: int) -> None: pass\n", ["x"], None),
		("generate_full_docstring_to_tmp", "module", "", [], None),
		("generate_full_docstring_to_tmp", "class", "class X:\n    pass\n", [], None),
		("generate_full_docstring_to_tmp", "function", "def f(a: int, *, b: str) -> None: pass\n", ["a", "b"], "|Must| return |None|."),
		("generate_full_docstring_to_tmp", "method", "def m(self, x: int) -> Self: pass\n", ["x"], "|Must| return |Self| for fluent-style chaining."),
		("generate_minimal_docstring_to_tmp", "method", "@classmethod\ndef cm(cls, x: int) -> None: pass\n", ["x"], None),
		("generate_minimal_docstring_to_tmp", "method", "@staticmethod\ndef sm(x: int) -> None: pass\n", ["x"], None),
		("generate_full_docstring_to_tmp", "method", "@classmethod\ndef cm(cls, x: int) -> None: pass\n", ["x"], "|Must| return |None|."),
		("generate_full_docstring_to_tmp", "method", "@staticmethod\ndef sm(x: int) -> bool: pass\n", ["x"], "|Must| return |True| if ... and |False| otherwise."),
	],
)
def test_vscode_backend_docstring_generation(
	tmp_path: Path,
	command: str,
	kind: str,
	source_fragment: str,
	expected_params: list[str],
	expected_return_snippet: str | None,
) -> None:
	_, generated = _run_backend(command, kind, source_fragment)
	_validate_structural_only(tmp_path, generated)
	if expected_params:
		params = _extract_parameter_labels(_strip_triple_quotes(generated))
		assert params == expected_params, f"unexpected parameters: {params}\ndoc:\n{generated}"
	if expected_return_snippet is not None:
		assert expected_return_snippet in generated, f"missing return snippet in:\n{generated}"


def test_vscode_backend_invalid_source_fragment_reports_xtnsn_007() -> None:
	payload = {
		"version": 1,
		"command": "generate_minimal_docstring_to_tmp",
		"kind": "method",
		"source_fragment": "def spam(a: int,b: float,*,c: str,/,d: bool) -> None: pass\n",
	}
	res = subprocess.run(
		[sys.executable, str(BACKEND)],
		input=json.dumps(payload),
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
		cwd=ROOT,
		env=_build_env(),
	)
	assert res.stdout.strip(), f"backend returned empty stdout (stderr={res.stderr!r})"
	data = json.loads(res.stdout)
	assert data.get("ok") is False, data
	diag = data.get("diagnostics", {})
	errs = diag.get("__WTRL_ERROR__", []) if isinstance(diag, dict) else []
	assert any(isinstance(e, dict) and e.get("rule-id") == "XTNSN-007" for e in errs), data


def test_vscode_backend_validate_reports_xtnsn_010_missing_source_file() -> None:
	data = _run_backend_json(
		{
			"version": 1,
			"command": "validate_docstring",
			"kind": "module",
			"source_fragment": "",
			"source_file": "",
			"line": 0,
			"include_diagnostics": True,
		}
	)
	assert data.get("ok") is False, data
	assert "XTNSN-010" in _error_rule_ids(data), data


def test_vscode_backend_validate_reports_xtnsn_011_bad_line_type() -> None:
	data = _run_backend_json(
		{
			"version": 1,
			"command": "validate_docstring",
			"kind": "module",
			"source_fragment": "",
			"source_file": DIR_EXAMPLES + "/test_docitem_module_minimal.py",
			"line": "not-an-int",
			"include_diagnostics": True,
		}
	)
	assert data.get("ok") is False, data
	assert "XTNSN-011" in _error_rule_ids(data), data


def test_vscode_backend_validate_reports_xtnsn_008_parse_module_file_error(tmp_path: Path) -> None:
	bad_module = tmp_path / "bad_module_syntax.py"
	bad_module.write_text("def broken(:\n    pass\n", encoding="utf-8")
	data = _run_backend_json(
		{
			"version": 1,
			"command": "validate_docstring",
			"kind": "function",
			"source_fragment": "def spam() -> None: pass\n",
			"source_file": str(bad_module),
			"line": 0,
			"include_diagnostics": True,
		}
	)
	assert data.get("ok") is False, data
	assert "XTNSN-008" in _error_rule_ids(data), data


def test_vscode_backend_validate_reports_xtnsn_009_cannot_resolve_nested_runtime_object(tmp_path: Path) -> None:
	mod = tmp_path / "nested_validate_case.py"
	mod.write_text(
		"def outer() -> object:\n"
		"\t\"\"\"Outer helper.\"\"\"\n"
		"\tdef inner() -> None:\n"
		"\t\t\"\"\"Inner helper.\"\"\"\n"
		"\t\tpass\n"
		"\treturn inner\n",
		encoding="utf-8",
	)
	data = _run_backend_json(
		{
			"version": 1,
			"command": "validate_docstring",
			"kind": "function",
			"source_fragment": "def inner() -> None: pass\n",
			"source_file": str(mod),
			"line": 2,
			"include_diagnostics": True,
		}
	)
	assert data.get("ok") is False, data
	assert "XTNSN-009" in _error_rule_ids(data), data


def test_vscode_backend_validate_reports_xtnsn_012_cannot_qualify_object() -> None:
	data = _run_backend_json(
		{
			"version": 1,
			"command": "validate_docstring",
			"kind": "function",
			"source_fragment": "def spam() -> None: pass\n",
			"source_file": DIR_EXAMPLES + "/test_docitem_function_minimal.py",
			"line": 9999,
			"include_diagnostics": True,
		}
	)
	assert data.get("ok") is False, data
	assert "XTNSN-012" in _error_rule_ids(data), data


def test_vscode_backend_validate_reports_real_waterloo_validation_error() -> None:
	data = _run_backend_json(
		{
			"version": 1,
			"command": "validate_docstring",
			"kind": "class",
			"source_fragment": "class A_00: pass\n",
			"source_file": DIR_EXAMPLES + "/pytest_bad_preamble.py",
			"line": 3,
			"include_diagnostics": True,
		}
	)
	assert data.get("ok") is False, data
	rules = _error_rule_ids(data)
	assert rules, data
	assert any(not rid.startswith("XTNSN-") for rid in rules), data
