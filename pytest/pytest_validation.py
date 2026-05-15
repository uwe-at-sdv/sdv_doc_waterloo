#!/usr/bin/env python3
"""Pytest suite for waterlint example objects without docstrings."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from pytest_common import ROOT, WATERLINT, DIR_EXAMPLES

# We can run this reliably only after preparing the package,
# using the module in sdv/doc/waterloo, because docitem contains
# machine-verifyable references to sdv.doc.waterloo.docitem....parse
def test_selftest_runs() -> None:
	"""Run the built-in coverage self-test."""
	cwd = os.getcwd()

# Not good. Use installed module.
#	os.chdir('package/src')

	result = subprocess.run(
		[sys.executable, "-m", "sdv.doc.waterloo.docitem"],
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
	)
	os.chdir(cwd)
	assert result.returncode == 0, f"self-test failed: {result.stderr}"

def _run_waterlint_validate(obj: str) -> subprocess.CompletedProcess[str]:
	"""Run ``waterlint validate`` for the given object and capture output."""
	return subprocess.run(
		[
			*WATERLINT,
			"validate",
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

def _run_waterlint_validate_with_basedir(obj: str, basedir: str = DIR_EXAMPLES) -> subprocess.CompletedProcess[str]:
	"""Run ``waterlint validate`` with explicit ``--basedir`` and capture output."""
	return subprocess.run(
		[
			*WATERLINT,
			"validate",
			"--basedir",
			basedir,
			"--obj",
			obj,
		],
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
		text=True,
		check=False,
		cwd=ROOT,
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


def test_bad_class_overview_missing_public_section() -> None:
	result = _run_waterlint_validate("pytest_bad_class_overview_in_module")
	_assert_error(result, "MCLO-003", "Public_classes")


def test_bad_function_overview_missing_public_section() -> None:
	result = _run_waterlint_validate("pytest_bad_function_overview_in_module")
	_assert_error(result, "MFNO-003", "Public_functions")


def test_bad_method_overview_missing_public_section() -> None:
	result = _run_waterlint_validate("pytest_bad_overview_in_class.BadMethodOverview")
	_assert_error(result, "CMTO-003", "Public_methods")


def test_bad_class_overview_missing_public_section_in_class() -> None:
	result = _run_waterlint_validate("pytest_bad_overview_in_class.BadClassOverview")
	_assert_error(result, "CCLO-003", "Public_classes")


def test_good_overview_module_and_class() -> None:
	result = _run_waterlint_validate("pytest_good_overview")
	assert result.returncode == 0, result.stderr
	result = _run_waterlint_validate("pytest_good_overview.GoodClass")
	assert result.returncode == 0, result.stderr


def test_bad_class_overview_cclo_cmto_x_cmto_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CMTO_002")
	_assert_error(result, "CMTO-002", "")


def test_bad_class_overview_cclo_cmto_x_cmto_003() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CMTO_003")
	_assert_error(result, "CMTO-003", "")


def test_bad_class_overview_cclo_cmto_x_cmto_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CMTO_005")
	_assert_error(result, "CMTO-005", "")


def test_bad_class_overview_cclo_cmto_x_cmto_006() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CMTO_006")
	_assert_error(result, "CMTO-006", "")


def test_bad_class_overview_cclo_cmto_x_cmto_007() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CMTO_007")
	_assert_error(result, "CMTO-007", "")


def test_bad_class_overview_cclo_cmto_x_cmto_008() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CMTO_008")
	_assert_error(result, "CMTO-008", "")


def test_bad_class_overview_cclo_cmto_x_cmto_009() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CMTO_009")
	_assert_error(result, "CMTO-009", "")


def test_bad_class_overview_cclo_cmto_x_cmto_011() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CMTO_011")
	_assert_error(result, "CMTO-011", "")


def test_bad_class_overview_cclo_cmto_x_cclo_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CCLO_002")
	_assert_error(result, "CCLO-002", "")


def test_bad_class_overview_cclo_cmto_x_cclo_003() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CCLO_003")
	_assert_error(result, "CCLO-003", "")


def test_bad_class_overview_cclo_cmto_x_cclo_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CCLO_005")
	_assert_error(result, "CCLO-005", "")


def test_bad_class_overview_cclo_cmto_x_cclo_006() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CCLO_006")
	_assert_error(result, "CCLO-006", "")


def test_bad_class_overview_cclo_cmto_x_cclo_007() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CCLO_007")
	_assert_error(result, "CCLO-007", "")


def test_bad_class_overview_cclo_cmto_x_cclo_008() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CCLO_008")
	_assert_error(result, "CCLO-008", "")


def test_bad_class_overview_cclo_cmto_x_cclo_009() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CCLO_009")
	_assert_error(result, "CCLO-009", "")


def test_bad_class_overview_cclo_cmto_x_cclo_011() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_overview_CCLO_CMTO.X_CCLO_011")
	_assert_error(result, "CCLO-011", "")


def test_bad_see_also_unresolvable_informative() -> None:
	result = _run_waterlint_validate("pytest_bad_see_also_in_class.X_00")
	_assert_warning(result, "SEE-003", "cannot be resolved")


def test_bad_see_also_no_docstring_informative() -> None:
	result = _run_waterlint_validate("pytest_bad_see_also_in_class.X_01")
	_assert_warning(result, "SEE-006", "has no docstring")


def test_bad_see_also_invalid_docstring_informative() -> None:
	result = _run_waterlint_validate("pytest_bad_see_also_in_class.X_02")
	_assert_warning(result, "SEE-007", "no valid docstring")


def test_bad_see_also_unresolvable_normative() -> None:
	result = _run_waterlint_validate("pytest_bad_see_also_in_class.X_03")
	_assert_error(result, "SEE-004", "cannot be resolved")


def test_bad_see_also_no_docstring_normative() -> None:
	result = _run_waterlint_validate("pytest_bad_see_also_in_class.X_04")
	_assert_error(result, "SEE-008", "no valid docstring")


def test_bad_see_also_invalid_docstring_normative() -> None:
	result = _run_waterlint_validate("pytest_bad_see_also_in_class.X_05")
	_assert_error(result, "SEE-008", "no valid docstring")

def test_bad_scope_see_also_module() -> None:
	result = _run_waterlint_validate("pytest_bad_scope_see_also")
	_assert_error(result, "SCP-006", "which is less public")

def test_bad_scope_see_also_spam() -> None:
	result = _run_waterlint_validate("pytest_bad_scope_see_also.spam")
	assert result.returncode == 0, result.stderr

def test_bad_scope_see_also_eggs() -> None:
	result = _run_waterlint_validate("pytest_bad_scope_see_also.eggs")
	_assert_error(result, "SCP-006", "which is less public")

#def test_bad_scope_see_also_normative_function() -> None:
#	result = _run_waterlint_validate("pytest_bad_scope_see_also.helper")
#	_assert_error(result, "SCP-006", "scope {<Scope.PUBLIC: 0>} which is more public")


def test_bad_status_multiple_entries() -> None:
	result = _run_waterlint_validate("pytest_bad_status.X_00.f_status_multiple")
	_assert_error(result, "STA-002", "exactly one item")


def test_bad_status_not_identifier() -> None:
	result = _run_waterlint_validate("pytest_bad_status.X_01.f_status_not_identifier")
	_assert_error(result, "LQID-002", "identifier")


def test_bad_status_unknown_tag() -> None:
	result = _run_waterlint_validate("pytest_bad_status.X_02.f_status_unknown_tag")
	_assert_error(result, "STA-004", "not allowed")


def test_bad_status_module_status_not_allowed() -> None:
	result = _run_waterlint_validate("pytest_bad_status")
	_assert_error(result, "PRE-016", "status")


def test_bad_status_class_status_not_allowed() -> None:
	result = _run_waterlint_validate("pytest_bad_status.X_03")
	_assert_error(result, "PRE-016", "status")

# ----- Scope monotonicity --------------------------------------------------#

def test_bad_scope_class_vs_module() -> None:
	result = _run_waterlint_validate("pytest_bad_scope")
	_assert_error(result, "SCP-005", "Scope of class")

def test_bad_scope_method_vs_class() -> None:
	result = _run_waterlint_validate("pytest_bad_scope.X_extension")
	_assert_error(result, "SCP-005", "Scope of method")

def test_bad_scope_derived_class() -> None:
	result = _run_waterlint_validate("pytest_bad_scope.Y_public")
	_assert_error(result, "SCP-009", "Scope of base class")

def test_bad_scope_inherited_method_vs_base() -> None:
	result = _run_waterlint_validate("pytest_bad_scope.Y_public.f")
	_assert_error(result, "SCP-008", "base method")


def test_bad_scope_module_vs_class() -> None:
	# module scope core, class scope extension -> violation
	result = _run_waterlint_validate("pytest_bad_scope")
	_assert_error(result, "SCP-005", "class 'X_extension'")


def test_bad_scope_class_vs_base_class_B() -> None:
	result = _run_waterlint_validate("pytest_bad_scope_base_class.B")
	_assert_error(result, "SCP-009", "base class")
def test_bad_scope_class_vs_base_class_C() -> None:
	result = _run_waterlint_validate("pytest_bad_scope_base_class.C")
	assert result.returncode == 0, f"expected success, got {result.stderr}"


def test_module_without_docstring() -> None:
	result = _run_waterlint_validate("pytest_no_docstring")
	_assert_error(result, "DOC-001", "module has no docstring")


def test_class_without_docstring() -> None:
	result = _run_waterlint_validate("pytest_no_docstring.X")
	_assert_error(result, "DOC-001", "class has no docstring")


def test_method_without_docstring() -> None:
	result = _run_waterlint_validate("pytest_no_docstring.X.m")
	_assert_error(result, "DOC-001", "function has no docstring")


def test_function_without_docstring() -> None:
	result = _run_waterlint_validate("pytest_no_docstring.f")
	_assert_error(result, "DOC-001", "function has no docstring")


def test_module_with_empty_docstring() -> None:
	result = _run_waterlint_validate("pytest_empty_docstring")
	_assert_error(result, "DOC-007", "Empty docstring")


def test_class_with_empty_docstring() -> None:
	result = _run_waterlint_validate("pytest_empty_docstring.X")
	_assert_error(result, "DOC-007", "Empty docstring")


def test_method_with_empty_docstring() -> None:
	result = _run_waterlint_validate("pytest_empty_docstring.X.m")
	_assert_error(result, "DOC-007", "Empty docstring")


def test_function_with_empty_docstring() -> None:
	result = _run_waterlint_validate("pytest_empty_docstring.f")
	_assert_error(result, "DOC-007", "Empty docstring")


def test_bad_preamble_missing_profile() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_00")
	_assert_error(result, "PRE-003", "profile")


def test_bad_section_label() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_00_0")
	_assert_error(result, "PRSR-005", "expected identifier")


def test_bad_preamble_empty_profile() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_01")
	_assert_error(result, "PRE-004", "exactly one item")


def test_bad_preamble_expect_identifier() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_01_0")
	_assert_error(result, "PRE-003", "not found")


def test_bad_preamble_invalid_profile_value() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_02")
	_assert_error(result, "PRE-005", "nonsense")


def test_bad_preamble_profile_not_identifier() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_03")
	_assert_error(result, "PRE-014", "identifier")


def test_bad_preamble_missing_normative_sections() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_04")
	_assert_error(result, "PRE-006", "normative_sections")


def test_bad_preamble_missing_contract_in_normative() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_05")
	_assert_error(result, "CON-002", "Contract")


def test_bad_preamble_nonexistent_normative_section() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_06")
	_assert_error(result, "PRE-012", "Nonsense")


def test_bad_preamble_duplicate_normative_entry() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_07")
	_assert_error(result, "LQID-004", "duplicate")


def test_bad_preamble_normative_terminology() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_08")
	_assert_error(result, "TERM-002", "marked as normative")


def test_bad_preamble_normativity_keyword_not_listed() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_09")
	_assert_error(result, "PRE-013", "not listed")


def test_bad_preamble_definitions_not_normative() -> None:
	result = _run_waterlint_validate("pytest_bad_preamble.A_10")
	_assert_error(result, "DEF-002", "not normative")


def test_bad_profile_module() -> None:
	result = _run_waterlint_validate("pytest_bad_profile")
	_assert_error(result, "PRE-017", "profile")


def test_bad_profile_class() -> None:
	result = _run_waterlint_validate("pytest_bad_profile.X")
	_assert_error(result, "PRE-018", "profile")


def test_bad_profile_method() -> None:
	result = _run_waterlint_validate("pytest_bad_profile.X.spam")
	_assert_error(result, "PRE-019", "profile")


def test_bad_profile_function() -> None:
	result = _run_waterlint_validate("pytest_bad_profile.eggs")
	_assert_error(result, "PRE-019", "profile")

def test_good_callable_profile_class_factory_from_int() -> None:
	result = _run_waterlint_validate_with_basedir("test_docitem_class_factory.X.from_int")
	assert result.returncode == 0, result.stderr


def test_bad_callable_profile_make_x() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_callable_profile.make_X")
	_assert_error(result, "PRE-019", "profile")

def test_bad_public_types_module_entry_not_identifier() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_public_types")
	_assert_error(result, "MPTYP-004", "identifier")


def test_bad_public_types_class_entry_not_identifier() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_public_types.X")
	_assert_error(result, "CPTYP-004", "identifier")


def test_definitions_missing_colon() -> None:
	result = _run_waterlint_validate("pytest_bad_def_term_desc.B_00")
	_assert_error(result, "PRSR-003", "missing colon")


def test_definitions_bad_identifier() -> None:
	result = _run_waterlint_validate("pytest_bad_def_term_desc.B_01")
	_assert_error(result, "DEF-004", "identifier")


def test_definitions_empty_content_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_def_term_desc.B_02")
	_assert_warning(result, "DEF-009", "should not be empty")


def test_terminology_empty_content_warning() -> None:
	result = _run_waterlint_validate("pytest_bad_def_term_desc.B_03")
	_assert_warning(result, "TERM-008", "Term content should not be empty")


def test_definitions_misc_multiline_required() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_misc.X_01")
	_assert_error(result, "DEF-006", "")


def test_terminology_misc_multiline_required() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_misc.X_02")
	_assert_error(result, "TERM-007", "")


def test_definitions_misc_csv_duplicate_term_in_header() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_misc.X_04_PRSR_002")
	_assert_error(result, "PRSR-002", "appears more than once")


def test_definitions_misc_inherit_variation_not_allowed() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_misc.X_05_DEF_018")
	_assert_error(result, "DEF-018", "not found in direct module terms")


def test_definitions_misc_inherit_duplicate_entry() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_misc.X_06_LQID_004")
	_assert_error(result, "LQID-004", "duplicate")


def test_good_definitions_def_022() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_good_definitions_DEF_022.X_DEF_022")
	assert result.returncode == 0, result.stderr


def test_bad_notes_normative_not_allowed() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_notes.X_01")
	_assert_error(result, "NOTE-002", "marked as normative")


def test_bad_notes_normativity_keyword_not_allowed() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_notes.X_02")
	_assert_error(result, "NOTE-003", "must not contain normativity keywords")


def test_bad_notes_nested_subsection_not_allowed() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_notes.X_03")
	_assert_error(result, "NOTE-007", "expected list of strings")


def test_bad_notes_empty_label() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_notes.X_04")
	_assert_error(result, "NOTE-006", "must not be empty")


def test_bad_notes_empty_content_warning() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_notes.X_05")
	_assert_warning(result, "NOTE-009", "should not be empty")


def test_bad_definitions_inherited_class_term_not_in_module() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_inherited.X_term_not_in_module")
	_assert_error(result, "DEF-018", "not found in direct module")


def test_bad_definitions_inherited_class_duplicate_term() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_inherited.X_duplicate_term")
	_assert_error(result, "LQID-004", "duplicate")


def test_bad_definitions_inherited_class_duplicate_inherited_subsection() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_inherited.X_duplicate_inherited")
	_assert_error(result, "PRSR-008", "Duplicate subsection")


def test_bad_definitions_inherited_class_term_not_identifier() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_inherited.X_term_not_an_identifier")
	_assert_error(result, "LQID-002", "expected identifier")


def test_bad_definitions_inherited_class_term_redefined() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_inherited.X_term_redefined")
	_assert_error(result, "DEF-017", "redefined")


def test_bad_definitions_inherited_not_allowed_in_module() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_inherited_not_allowed_in_module")
	_assert_error(result, "DEF-011", "_inherited")


def test_bad_definitions_inherited_module_without_docstring_module() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_inherited_module_without_docstring")
	_assert_error(result, "DOC-001", "module has no docstring")


def test_bad_definitions_inherited_module_without_docstring_class_x() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_definitions_inherited_module_without_docstring.X")
	_assert_error(result, "DEF-014", "Direct module")


def test_bad_factory_not_normative() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_factory_not_normative.X")
	_assert_error(result, "PRE-013", "Factory")


def test_bad_factory_label_not_qualified_identifier() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_factory_label_not_qualified_identifier.X")
	_assert_error(result, "FAC-005", "qualified identifier")


def test_bad_factory_not_free_form_text() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_factory_not_free_form_text.X")
	_assert_error(result, "FAC-007", "list of strings")


def test_bad_factory_function_does_not_resolve() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_factory_function_does_not_resolve.X")
	_assert_error(result, "FAC-006", "does not resolve")


def test_bad_factory_duplicate_entry() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_factory_duplicate_entry.X")
	_assert_error(result, "FAC-008", "Duplicate entry")


def test_description_no_subsection_allowed() -> None:
	result = _run_waterlint_validate("pytest_bad_def_term_desc.B_04")
	_assert_error(result, "DESC-004", "list of strings")


def test_inherited_missing_base_section() -> None:
	result = _run_waterlint_validate("pytest_bad_inheritance.Y_00.spam")
	_assert_error(result, "CON-039", "base")


def test_inherited_missing_base_entry() -> None:
	result = _run_waterlint_validate("pytest_bad_inheritance.Y_01.spam")
	_assert_error(result, "CON-040", "exactly one")


def test_inherited_base_not_qid() -> None:
	result = _run_waterlint_validate("pytest_bad_inheritance.Y_02.spam")
	_assert_error(result, "LQID-002", "identifier")


def test_inherited_base_not_resolvable() -> None:
	result = _run_waterlint_validate("pytest_bad_inheritance.Y_03.spam")
	_assert_error(result, "CON-042", "cannot be resolved")


def test_inherited_base_not_baseclass() -> None:
	result = _run_waterlint_validate("pytest_bad_inheritance.Y_04.spam")
	_assert_error(result, "CON-043", "base class")


def test_inherited_base_missing_docstring() -> None:
	result = _run_waterlint_validate("pytest_bad_inheritance.Y_05.spam")
	_assert_error(result, "CON-045", "docstring")


def test_inherited_base_invalid_docstring() -> None:
	result = _run_waterlint_validate("pytest_bad_inheritance.Y_06.spam")
	_assert_error(result, "CON-045", "ParseError")


def test_bad_function_contract_requires_subsection_not_allowed() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_contract.f_01")
	_assert_error(result, "CON-048", "expected str")


def test_bad_function_contract_ensures_subsection_not_allowed() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_contract.f_02")
	_assert_error(result, "CON-050", "expected str")


def test_bad_function_contract_invariants_subsection_not_allowed() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_contract.f_03")
	_assert_error(result, "CON-026", "expected str")


def test_bad_function_parameters_par_001() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_parameters_PAR.f_PAR_001")
	_assert_error(result, "PAR-001", "Section 'Parameters' does not exist")


def test_bad_function_parameters_par_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_parameters_PAR.f_PAR_002")
	_assert_error(result, "PAR-002", "not listed as normative")


def test_bad_function_parameters_par_003_positive() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_parameters_PAR.f_PAR_003")
	assert result.returncode == 0, result.stderr


def test_bad_function_parameters_par_004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_parameters_PAR.f_PAR_004")
	_assert_error(result, "PAR-004", "in signature but not documented")


def test_bad_function_parameters_par_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_parameters_PAR.f_PAR_005")
	_assert_error(result, "PAR-005", "documented but not in signature")


def test_bad_function_parameters_par_006() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_parameters_PAR.f_PAR_006")
	_assert_error(result, "PAR-006", "expected identifier")


def test_bad_function_parameters_par_007() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_parameters_PAR.f_PAR_007")
	_assert_error(result, "PAR-007", "expected list of strings")


def test_bad_function_returns_ret_001() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_returns_RET.f_RET_001")
	_assert_error(result, "RET-001", "Section 'Returns' does not exist")


def test_bad_function_returns_ret_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_returns_RET.f_RET_002")
	_assert_error(result, "RET-002", "not listed as normative")


def test_bad_function_returns_ret_004_warning() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_returns_RET.f_RET_004")
	_assert_warning(result, "RET-004", "truthy/falsy")


def test_bad_function_returns_ret_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_returns_RET.f_RET_005")
	_assert_error(result, "RET-005", "expected list of strings")


def test_bad_function_returns_ret_006_warning() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_returns_RET.f_RET_006")
	_assert_warning(result, "RET-006", "tokenized form as |None|")


def test_bad_function_returns_ret_007_warning() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_returns_RET.f_RET_007")
	_assert_warning(result, "RET-007", "tokenized form as |Self|")


def test_bad_function_returns_ret_positive() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_returns_RET.f")
	assert result.returncode == 0, result.stderr


def test_bad_function_raises_rai_001() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_raises_RAI.f_RAI_001")
	_assert_error(result, "RAI-001", "Section 'Raises' does not exist")


def test_bad_function_raises_rai_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_raises_RAI.f_RAI_002")
	_assert_error(result, "RAI-002", "not listed as normative")


def test_bad_function_raises_rai_004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_raises_RAI.f_RAI_004")
	_assert_error(result, "RAI-004", "does not refer to an existing class")


def test_bad_function_raises_rai_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_raises_RAI.f_RAI_005")
	_assert_error(result, "RAI-005", "expected list of strings")


def test_bad_function_raises_rai_007() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_raises_RAI.f_RAI_007")
	_assert_error(result, "RAI-007", "not a subclass of BaseException")


def test_bad_function_raises_rai_008() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_function_raises_RAI.f_RAI_008")
	_assert_error(result, "RAI-008", "expected qualified identifier")


def test_inherited_ok_three_levels() -> None:
	result = _run_waterlint_validate("pytest_good_inheritance.Z.spam")
	assert result.returncode == 0, f"expected success, got {result.stderr}"

def test_inherited_ok_derived_from_mro() -> None:
	result = _run_waterlint_validate_with_basedir("test_docitem_derived_from_mro.Y", basedir="doc/examples")
	assert result.returncode == 0, f"expected success, got {result.stderr}"

def test_inherited_bad_derived_from_mro_non_direct() -> None:
	result = _run_waterlint_validate_with_basedir("test_docitem_derived_from_mro.Z", basedir="doc/examples")
	_assert_error(result, "DER-003", "not a direct base")

def test_bad_class_in_class_x01_validate_ok() -> None:
	result = _run_waterlint_validate("pytest_bad_class_in_class.X_01")
	assert result.returncode == 0, f"expected success, got {result.stderr}"


def test_bad_class_in_class_x01_inner_validate_ok() -> None:
	result = _run_waterlint_validate("pytest_bad_class_in_class.X_01.Y_not_listed")
	assert result.returncode == 0, f"expected success, got {result.stderr}"


def test_bad_class_in_class_x02_validate_ok() -> None:
	result = _run_waterlint_validate("pytest_bad_class_in_class.X_02")
	assert result.returncode == 0, f"expected success, got {result.stderr}"


def test_bad_class_in_class_x02_bad_doc_invalid() -> None:
	result = _run_waterlint_validate("pytest_bad_class_in_class.X_02.Y_not_listed_bad_doc")
	assert result.returncode == 1, "expected error for invalid docstring"


def test_bad_class_in_class_x02_no_doc_invalid() -> None:
	result = _run_waterlint_validate("pytest_bad_class_in_class.X_02.Y_not_listed_no_doc")
	_assert_error(result, "DOC-001", "has no docstring")


# ----- bad class in module scenarios --------------------------------------- #

def test_bad_class_in_module_validate_ok() -> None:
	result = _run_waterlint_validate("pytest_bad_class_in_module")
	assert result.returncode == 0, f"expected success, got {result.stderr}"


def test_bad_class_public_classes_cpcl_x00_validate_ok() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_classes_CPCL.X_00")
	assert result.returncode == 0, result.stderr


def test_bad_class_public_classes_cpcl_x01_validate_cpcl002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_classes_CPCL.X_01")
	_assert_error(result, "CPCL-002", "not listed as normative")


def test_bad_class_public_classes_cpcl_x02_validate_cpcl004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_classes_CPCL.X_02")
	_assert_error(result, "CPCL-004", "does not exist on class")


def test_bad_class_public_classes_cpcl_x03_validate_cpcl005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_classes_CPCL.X_03")
	_assert_error(result, "CPCL-005", "not a class")


def test_bad_class_public_methods_cpmt_x00_validate_ok() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_methods_CPMT.X_00")
	assert result.returncode == 0, result.stderr


def test_bad_class_public_methods_cpmt_x01_validate_cpmt002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_methods_CPMT.X_01")
	_assert_error(result, "CPMT-002", "not listed as normative")


def test_bad_class_public_methods_cpmt_x02_validate_cpmt004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_methods_CPMT.X_02")
	_assert_error(result, "CPMT-004", "does not exist on class")


def test_bad_class_public_methods_cpmt_x03_validate_cpmt005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_methods_CPMT.X_03")
	_assert_error(result, "CPMT-005", "not a method")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cptyp_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPTYP_002")
	_assert_error(result, "CPTYP-002", "not listed as normative")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cptyp_004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPTYP_004")
	_assert_error(result, "CPTYP-004", "identifier")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cptyp_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPTYP_005")
	_assert_error(result, "CPTYP-005", "does not exist on class")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cptyp_006() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPTYP_006")
	_assert_error(result, "CPTYP-006", "expected list of strings")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cptyp_008() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPTYP_008")
	_assert_error(result, "CPTYP-008", "TypeAlias/NewType")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cpvar_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPVAR_002")
	_assert_error(result, "CPVAR-002", "not listed as normative")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cpvar_004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPVAR_004")
	_assert_error(result, "CPVAR-004", "identifier")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cpvar_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPVAR_005")
	_assert_error(result, "CPVAR-005", "does not exist on class")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cpvar_006() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPVAR_006")
	_assert_error(result, "CPVAR-006", "expected list of strings")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cpvar_008() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPVAR_008")
	_assert_error(result, "CPVAR-008", "must refer to a named value")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cpcon_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPCON_002")
	_assert_error(result, "CPCON-002", "not listed as normative")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cpcon_004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPCON_004")
	_assert_error(result, "CPCON-004", "identifier")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cpcon_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPCON_005")
	_assert_error(result, "CPCON-005", "does not exist on class")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cpcon_006() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPCON_006")
	_assert_error(result, "CPCON-006", "not Final")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cpcon_007() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPCON_007")
	_assert_error(result, "CPCON-007", "expected list of strings")


def test_bad_class_public_cptyp_cpvar_cpcon_x_cpcon_009() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_class_public_CPTYP_CPVAR_CPCON.X_CPCON_009")
	_assert_error(result, "CPCON-009", "must refer to a named value")


def test_bad_module_public_classes_mpcl_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_classes_MPCL_002")
	_assert_error(result, "MPCL-002", "not listed as normative")


def test_bad_module_public_classes_mpcl_004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_classes_MPCL_004")
	_assert_error(result, "MPCL-004", "does not exist")


def test_bad_module_public_classes_mpcl_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_classes_MPCL_005")
	_assert_error(result, "MPCL-005", "not a class")


def test_bad_module_public_functions_mpfn_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_functions_MPFN_002")
	_assert_error(result, "MPFN-002", "not listed as normative")


def test_bad_module_public_functions_mpfn_004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_functions_MPFN_004")
	_assert_error(result, "MPFN-004", "does not exist")


def test_bad_module_public_functions_mpfn_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_functions_MPFN_005")
	_assert_error(result, "MPFN-005", "not a function")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mptyp_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPTYP_002")
	_assert_error(result, "MPTYP-002", "not listed as normative")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mptyp_004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPTYP_004")
	_assert_error(result, "MPTYP-004", "identifier")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mptyp_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPTYP_005")
	_assert_error(result, "MPTYP-005", "does not exist on module")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mptyp_006() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPTYP_006")
	_assert_error(result, "MPTYP-006", "expected list of strings")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mptyp_008() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPTYP_008")
	_assert_error(result, "MPTYP-008", "TypeAlias/NewType")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mpvar_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPVAR_002")
	_assert_error(result, "MPVAR-002", "not listed as normative")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mpvar_004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPVAR_004")
	_assert_error(result, "MPVAR-004", "identifier")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mpvar_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPVAR_005")
	_assert_error(result, "MPVAR-005", "does not exist on module")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mpvar_006() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPVAR_006")
	_assert_error(result, "MPVAR-006", "expected list of strings")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mpvar_008() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPVAR_008")
	_assert_error(result, "MPVAR-008", "must refer to a named value")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mpcon_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPCON_002")
	_assert_error(result, "MPCON-002", "not listed as normative")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mpcon_004() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPCON_004")
	_assert_error(result, "MPCON-004", "identifier")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mpcon_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPCON_005")
	_assert_error(result, "MPCON-005", "does not exist on module")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mpcon_006() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPCON_006")
	_assert_error(result, "MPCON-006", "not Final")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mpcon_007() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPCON_007")
	_assert_error(result, "MPCON-007", "expected list of strings")


def test_bad_module_public_mptyp_mpvar_mpcon_m_mpcon_009() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_public_MPTYP_MPVAR_MPCON.M_MPCON_009")
	_assert_error(result, "MPCON-009", "must refer to a named value")


def test_bad_module_overview_mclo_mfno_m_mclo_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MCLO_002")
	_assert_error(result, "MCLO-002", "")


def test_bad_module_overview_mclo_mfno_m_mclo_003() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MCLO_003")
	_assert_error(result, "MCLO-003", "")


def test_bad_module_overview_mclo_mfno_m_mclo_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MCLO_005")
	_assert_error(result, "MCLO-005", "")


def test_bad_module_overview_mclo_mfno_m_mclo_006() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MCLO_006")
	_assert_error(result, "MCLO-006", "")


def test_bad_module_overview_mclo_mfno_m_mclo_007() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MCLO_007")
	_assert_error(result, "MCLO-007", "")


def test_bad_module_overview_mclo_mfno_m_mclo_008() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MCLO_008")
	_assert_error(result, "MCLO-008", "")


def test_bad_module_overview_mclo_mfno_m_mclo_009() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MCLO_009")
	_assert_error(result, "MCLO-009", "")


def test_bad_module_overview_mclo_mfno_m_mclo_011() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MCLO_011")
	_assert_error(result, "MCLO-011", "")


def test_bad_module_overview_mclo_mfno_m_mfno_002() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MFNO_002")
	_assert_error(result, "MFNO-002", "")


def test_bad_module_overview_mclo_mfno_m_mfno_003() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MFNO_003")
	_assert_error(result, "MFNO-003", "")


def test_bad_module_overview_mclo_mfno_m_mfno_005() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MFNO_005")
	_assert_error(result, "MFNO-005", "")


def test_bad_module_overview_mclo_mfno_m_mfno_006() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MFNO_006")
	_assert_error(result, "MFNO-006", "")


def test_bad_module_overview_mclo_mfno_m_mfno_007() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MFNO_007")
	_assert_error(result, "MFNO-007", "")


def test_bad_module_overview_mclo_mfno_m_mfno_008() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MFNO_008")
	_assert_error(result, "MFNO-008", "")


def test_bad_module_overview_mclo_mfno_m_mfno_009() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MFNO_009")
	_assert_error(result, "MFNO-009", "")


def test_bad_module_overview_mclo_mfno_m_mfno_011() -> None:
	result = _run_waterlint_validate_with_basedir("pytest_bad_module_overview_MCLO_MFNO.M_MFNO_011")
	_assert_error(result, "MFNO-011", "")


def test_bad_function_in_module_validate_ok() -> None:
	result = _run_waterlint_validate("pytest_bad_function_in_module")
	assert result.returncode == 0, f"expected success, got {result.stderr}"
