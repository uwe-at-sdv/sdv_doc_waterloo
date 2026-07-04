#!/usr/bin/env python3
"""Pytest suite for partial normativity bug warnings."""

from __future__ import annotations

import subprocess

import pytest

from pytest_common import DIR_EXAMPLES, run_waterlint


def _run_waterlint_validate(obj: str) -> subprocess.CompletedProcess[str]:
	"""Run ``waterlint validate`` for the given object and capture output."""
	return run_waterlint(
		"validate",
		"--basedir",
		DIR_EXAMPLES,
		"--obj",
		obj,
	)


def _assert_warning(result: subprocess.CompletedProcess[str], rule: str, text: str) -> None:
	assert result.returncode == 0, f"expected exit code 0 (warning), got {result.returncode}"
	assert rule in result.stderr, f"{rule} not reported: {result.stderr}"
	assert text in result.stderr, f"expected '{text}' in stderr: {result.stderr}"


def _assert_no_warning(result: subprocess.CompletedProcess[str], rule: str) -> None:
	assert result.returncode == 0, f"expected exit code 0, got {result.returncode}: {result.stderr}"
	assert rule not in result.stderr, f"{rule} unexpectedly reported: {result.stderr}"


def test_pnb_004_module_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB")
	_assert_warning(result, "PNB-004", "Untokenized normativity keyword")


def test_pnb_004_class_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.X")
	_assert_warning(result, "PNB-004", "Untokenized normativity keyword")


def test_pnb_004_method_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.X.m")
	_assert_warning(result, "PNB-004", "Untokenized normativity keyword")


def test_pnb_004_function_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.f")
	_assert_warning(result, "PNB-004", "Untokenized normativity keyword")


def test_pnb_002_must_not_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.f_pnb_002_must_not")
	_assert_warning(result, "PNB-002", "|must_not|")


def test_pnb_002_should_not_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.f_pnb_002_should_not")
	_assert_warning(result, "PNB-002", "|should_not|")


def test_pnb_003_may_not_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.f_pnb_003_may_not")
	_assert_warning(result, "PNB-003", "|may| not")


def test_pnb_004_should_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.f_pnb_004_should")
	_assert_warning(result, "PNB-004", "Untokenized normativity keyword")


def test_pnb_004_may_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.f_pnb_004_may")
	_assert_warning(result, "PNB-004", "Untokenized normativity keyword")


def test_pnb_004_hyphenated_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.f_pnb_004_hyphenated")
	_assert_warning(result, "PNB-004", "Untokenized normativity keyword")


@pytest.mark.parametrize(
	"obj",
	[
		"pytest_bad_PNB.f_pnb_004_must_period",
		"pytest_bad_PNB.f_pnb_004_should_comma",
		"pytest_bad_PNB.f_pnb_004_may_colon",
	],
)
def test_pnb_004_warns_before_punctuation(obj: str) -> None:
	result = _run_waterlint_validate(obj)
	_assert_warning(result, "PNB-004", "Untokenized normativity keyword")


def test_pnb_004_ignores_tokenized_text() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.f_no_pnb_004_tokenized")
	_assert_no_warning(result, "PNB-004")


@pytest.mark.parametrize(
	"obj",
	[
		"pytest_bad_PNB.f_no_pnb_004_double_quoted",
		"pytest_bad_PNB.f_no_pnb_004_single_quoted",
		"pytest_bad_PNB.f_no_pnb_004_backtick_quoted",
	],
)
def test_pnb_004_ignores_quoted_text(obj: str) -> None:
	result = _run_waterlint_validate(obj)
	_assert_no_warning(result, "PNB-004")


def test_pnb_004_warns_for_unquoted_text_next_to_quoted_text() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.f_pnb_004_quoted_and_unquoted")
	_assert_warning(result, "PNB-004", "Untokenized normativity keyword")


@pytest.mark.parametrize(
	"obj",
	[
		"pytest_bad_PNB.f_pnb_004_mixed_single_backtick_quote",
		"pytest_bad_PNB.f_pnb_004_mixed_single_double_quote",
		"pytest_bad_PNB.f_pnb_004_mixed_double_backtick_quote",
	],
)
def test_pnb_004_warns_for_mixed_quote_spans(obj: str) -> None:
	result = _run_waterlint_validate(obj)
	_assert_warning(result, "PNB-004", "Untokenized normativity keyword")


def test_pnb_004_warns_in_normative_description() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.f_pnb_004_normative_description")
	_assert_warning(result, "PNB-004", "Untokenized normativity keyword")


def test_pnb_004_ignores_informative_description() -> None:
	result = _run_waterlint_validate("pytest_bad_PNB.f_no_pnb_004_informative_description")
	_assert_no_warning(result, "PNB-004")


@pytest.mark.parametrize(
	"obj",
	[
		"pytest_bad_PNB.f_no_pnb_004_notes",
		"pytest_bad_PNB.f_no_pnb_004_terminology",
		"pytest_bad_PNB.Y",
		"pytest_good_PNB_informative",
	],
)
def test_pnb_004_ignores_informative_sections(obj: str) -> None:
	result = _run_waterlint_validate(obj)
	_assert_no_warning(result, "PNB-004")
