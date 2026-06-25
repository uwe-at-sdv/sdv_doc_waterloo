#!/usr/bin/env python3
"""Pytests for waterlint subcommand extract."""

from __future__ import annotations

from pathlib import Path

from pytest_common import run_waterlint, DIR_EXAMPLES

def test_extract_full_docstring_from_object() -> None:
	"""Extracting a full docstring from an object returns text on stdout."""
	res = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_module_full",
	)
	assert res.returncode == 0, res.stderr
	assert "Preamble:" in res.stdout
	assert "Public_constants:" in res.stdout


def test_extract_subsection_from_object() -> None:
	"""Extracting a concrete subsection from an object returns its text."""
	res = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_module_full",
		"--section",
		"Public_constants",
		"--subsection",
		"MY_CONSTANT",
	)
	assert res.returncode == 0, res.stderr
	assert "|Must| represent a constant value annotated as :wtrl_type:`Final`." in res.stdout


def test_extract_writes_to_output_file(tmp_path: Path) -> None:
	"""--out writes the extracted text to a file instead of stdout."""
	out_file = tmp_path / "extract.txt"
	res = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_module_full",
		"--section",
		"Public_constants",
		"--subsection",
		"MY_CONSTANT",
		"--out",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr
	assert res.stdout == ""
	assert out_file.exists()
	txt = out_file.read_text(encoding="utf-8")
	assert "|Must| represent a constant value annotated as :wtrl_type:`Final`." in txt


def test_extract_is_idempotent_via_input_file(tmp_path: Path) -> None:
	"""A full extracted docstring can be extracted again unchanged from file."""
	out_file = tmp_path / "module_doc.txt"
	res1 = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_module_full",
		"--out",
		str(out_file),
	)
	assert res1.returncode == 0, res1.stderr
	first = out_file.read_text(encoding="utf-8")

	res2 = run_waterlint(
		"extract",
		"--in",
		str(out_file),
	)
	assert res2.returncode == 0, res2.stderr
	assert res2.stdout == first


def test_extract_rejects_subsection_without_section() -> None:
	"""--subsection without --section fails with TOOL-002."""
	res = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_module_full",
		"--subsection",
		"MY_CONSTANT",
	)
	assert res.returncode == 1, res.stderr
	assert "TOOL-002" in res.stderr, res.stderr


def test_extract_rejects_object_without_docstring() -> None:
	"""An object without a docstring fails with TOOL-003."""
	res = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_module_full.MyClass",
	)
	assert res.returncode == 1, res.stderr
	assert "TOOL-003" in res.stderr, res.stderr


def test_extract_reports_missing_section() -> None:
	"""A missing section fails with TOOL-004."""
	res = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_module_full",
		"--section",
		"DoesNotExist",
	)
	assert res.returncode == 1, res.stderr
	assert "TOOL-004" in res.stderr, res.stderr


def test_extract_reports_missing_subsection() -> None:
	"""A missing subsection fails with TOOL-005."""
	res = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_module_full",
		"--section",
		"Public_constants",
		"--subsection",
		"DOES_NOT_EXIST",
	)
	assert res.returncode == 1, res.stderr
	assert "TOOL-005" in res.stderr, res.stderr


def test_extract_reports_parse_error_from_input_file(tmp_path: Path) -> None:
	"""Malformed input text fails with TOOL-006."""
	in_file = tmp_path / "bad_doc.txt"
	in_file.write_text("Contract:\n\tgeneral:\n \t\tMixed indent\n", encoding="utf-8")
	res = run_waterlint(
		"extract",
		"--in",
		str(in_file),
	)
	assert res.returncode == 1, res.stderr
	assert "TOOL-006" in res.stderr, res.stderr


def test_extract_reports_unresolvable_object() -> None:
	"""An unresolvable object fails with TOOL-001."""
	res = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"does_not_exist_module",
	)
	assert res.returncode == 1, res.stderr
	assert "TOOL-001" in res.stderr, res.stderr


def test_extract_syntax_highlighting_is_off_by_default() -> None:
	"""By default extract emits plain text without ANSI escape codes."""
	res = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_module_full",
	)
	assert res.returncode == 0, res.stderr
	assert "\x1b[" not in res.stdout


def test_extract_syntax_highlighting_can_be_forced() -> None:
	"""--syntax-hl with --color emits ANSI escape codes for terminal rendering."""
	res = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_module_full",
		"--syntax-hl",
		"--color",
	)
	assert res.returncode == 0, res.stderr
	assert "\x1b[" in res.stdout
	assert "Preamble:" in res.stdout


def test_extract_rejects_unknown_syntax_style() -> None:
	"""An unknown syntax style fails with TOOL-001."""
	res = run_waterlint(
		"extract",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		"test_docitem_module_full",
		"--syntax-hl",
		"--syntax-hl-style",
		"zephir",
	)
	assert res.returncode == 1, res.stderr
	assert "TOOL-001" in res.stderr, res.stderr
