#!/usr/bin/env python3
"""Pytest suite for waterlint coverage examples."""

from __future__ import annotations

import subprocess

from pytest_common import WATERLINT, DIR_EXAMPLES


def _run_waterlint_coverage(obj: str) -> subprocess.CompletedProcess[str]:
	"""Run ``waterlint coverage`` for the given object and capture output."""
	return subprocess.run(
		[
			str(WATERLINT),
			"coverage",
			"--basedir",
			DIR_EXAMPLES,
			"--obj",
			obj,
		],
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
	)


def _assert_error(result: subprocess.CompletedProcess[str], rule: str, text: str) -> None:
	assert result.returncode == 1, f"expected exit code 1, got {result.returncode}"
	assert rule in result.stderr, f"{rule} not reported: {result.stderr}"
	if text != "":
		assert text in result.stderr, f"expected '{text}' in stderr: {result.stderr}"


def _assert_warning(result: subprocess.CompletedProcess[str], rule: str, text: str) -> None:
	assert result.returncode == 0, f"expected exit code 0 (warning), got {result.returncode}"
	assert rule in result.stderr, f"{rule} not reported: {result.stderr}"
	assert text in result.stderr, f"expected '{text}' in stderr: {result.stderr}"


def test_bad_scope_class_vs_base_class() -> None:
	result = _run_waterlint_coverage("pytest_bad_scope_base_class")
	_assert_error(result, "SCP-009", "base class")


def test_good_class_in_class_ok_three_levels() -> None:
	result = _run_waterlint_coverage("pytest_good_class_in_class")
	assert result.returncode == 0, f"expected success, got {result.stderr}"


def test_bad_class_in_class_module_coverage() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_in_class")
	_assert_error(result, "CPCL-007", "listed in Public_classes but has no valid docstring")


def test_bad_class_in_class_x00_coverage() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_in_class.X_00")
	_assert_error(result, "CPCL-007", "listed in Public_classes but has no valid docstring")


def test_bad_class_in_class_x01_coverage_warning() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_in_class.X_01")
	_assert_warning(result, "CPCL-006", "not listed in Public_classes")


def test_bad_class_in_class_x02_coverage_ok() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_in_class.X_02")
	assert result.returncode == 0, f"expected success, got {result.stderr}"


def test_bad_class_in_class_x03_listed_method_invalid() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_in_class.X_03")
	_assert_error(result, "CPMT-007", "listed in Public_methods but has no valid docstring")


def test_bad_class_in_class_x04_not_listed_valid_warn() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_in_class.X_04")
	_assert_warning(result, "CPMT-006", "not listed in Public_methods")


def test_bad_class_in_class_x05_listed_method_missing_doc() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_in_class.X_05")
	_assert_warning(result, "CPMT-007", "no valid docstring")


def test_bad_class_in_module_coverage_errors() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_in_module")
	_assert_error(result, "PRSR-003", "missing colon")
	_assert_error(result, "MPCL-007", "no valid docstring")


def test_bad_class_public_classes_cpcl_x00_coverage_cpcl007() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_public_classes_CPCL.X_00")
	assert result.returncode == 1, f"expected exit code 1, got {result.returncode}"
	assert "CPCL-007" in result.stderr, result.stderr


def test_bad_class_public_classes_cpcl_x04_coverage_cpcl006() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_public_classes_CPCL.X_04")
	_assert_warning(result, "CPCL-006", "not listed in Public_classes")


def test_bad_class_public_methods_cpmt_x00_coverage_cpmt007() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_public_methods_CPMT.X_00")
	assert result.returncode == 1, f"expected exit code 1, got {result.returncode}"
	assert "CPMT-007" in result.stderr, result.stderr


def test_bad_class_public_methods_cpmt_x04_coverage_cpmt006() -> None:
	result = _run_waterlint_coverage("pytest_bad_class_public_methods_CPMT.X_04")
	_assert_warning(result, "CPMT-006", "not listed in Public_methods")


def test_bad_module_public_classes_mpcl_006_coverage_warning() -> None:
	result = _run_waterlint_coverage("pytest_bad_module_public_classes_MPCL_006")
	_assert_warning(result, "MPCL-006", "not listed in Public_classes")


def test_bad_module_public_classes_mpcl_007_coverage_warning() -> None:
	result = _run_waterlint_coverage("pytest_bad_module_public_classes_MPCL_007")
	_assert_warning(result, "MPCL-007", "no valid docstring")


def test_bad_module_public_functions_mpfn_006_coverage_warning() -> None:
	result = _run_waterlint_coverage("pytest_bad_module_public_functions_MPFN_006")
	_assert_warning(result, "MPFN-006", "not listed in Public_functions")


def test_bad_module_public_functions_mpfn_007_coverage_warning() -> None:
	result = _run_waterlint_coverage("pytest_bad_module_public_functions_MPFN_007")
	_assert_warning(result, "MPFN-007", "no valid docstring")


def test_bad_function_in_module_coverage_error() -> None:
	result = _run_waterlint_coverage("pytest_bad_function_in_module")
	_assert_error(result, "PRSR-003", "missing colon")
