#!/usr/bin/env python3
"""Source-independent semantic tests for Waterloo Authoring JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sdv.doc.waterloo.docitem_helper import get_allowed_sections_for_profile
from sdv.doc.waterloo.waterlint_authoring import load_authoring_document, validate_authoring_document


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "authoring_json"


def _load(name: str):
	return load_authoring_document(json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8")))


def _codes(name: str) -> set[str]:
	return {issue.code for issue in validate_authoring_document(_load(name))}


def test_authoring_semantics_accept_existing_schema_examples() -> None:
	"""The schema fixtures remain semantically valid Authoring JSON documents."""
	for name in (
		"valid_module.json",
		"valid_class.json",
		"valid_function.json",
		"valid_method.json",
		"valid_inherited_method.json",
		"maximal_module.json",
		"maximal_class.json",
		"maximal_function.json",
		"maximal_method.json",
		"maximal_inherited_method.json",
	):
		assert not validate_authoring_document(_load(name)), name


@pytest.mark.parametrize(
	("name", "profile"),
	[
		("maximal_module.json", "module"),
		("maximal_class.json", "class"),
		("maximal_function.json", "function"),
		("maximal_method.json", "method"),
		("maximal_inherited_method.json", "inherited_method"),
	],
)
def test_authoring_maximal_fixture_contains_every_allowed_section(name: str, profile: str) -> None:
	"""Maximal fixtures cover the complete top-level section set of their profile."""
	document = _load(name)
	assert document.profile == profile
	assert set(document.sections) == {"Preamble", *get_allowed_sections_for_profile(profile)}


def test_authoring_semantics_rejects_section_not_allowed_for_profile() -> None:
	"""A schema-valid section may still be prohibited for the selected profile."""
	document = _load("valid_function.json")
	data = json.loads((FIXTURE_DIR / "valid_function.json").read_text(encoding="utf-8"))
	data["doc"]["Derived_from"] = ["demo.module.Base"]
	issues = validate_authoring_document(load_authoring_document(data))
	assert any(issue.code == "profile-section" and issue.path == "doc.Derived_from" for issue in issues)
	assert document.profile == "function"


def test_authoring_semantics_requires_existing_normative_sections() -> None:
	"""Preamble.normative_sections must not refer to a missing section."""
	data = json.loads((FIXTURE_DIR / "valid_module.json").read_text(encoding="utf-8"))
	data["doc"]["Preamble"]["normative_sections"].append("Definitions")
	assert "normative-missing-section" in {issue.code for issue in validate_authoring_document(load_authoring_document(data))}


def test_authoring_semantics_requires_fixed_normative_sections_to_be_listed() -> None:
	"""Existing normative sections are governed by BinNorm even without Python context."""
	data = json.loads((FIXTURE_DIR / "valid_module.json").read_text(encoding="utf-8"))
	data["doc"]["Definitions"] = {
		"Widget": [{"paragraph": "A demonstration type."}],
	}
	assert "normative-required-section" in {issue.code for issue in validate_authoring_document(load_authoring_document(data))}


def test_authoring_semantics_rejects_informative_section_as_normative() -> None:
	"""Notes is informative regardless of the selected profile."""
	data = json.loads((FIXTURE_DIR / "valid_module.json").read_text(encoding="utf-8"))
	data["doc"]["Notes"] = {"Usage": [{"paragraph": "Informative."}]}
	data["doc"]["Preamble"]["normative_sections"].append("Notes")
	assert "normative-informative-section" in {issue.code for issue in validate_authoring_document(load_authoring_document(data))}


def test_authoring_semantics_rejects_duplicate_normative_section() -> None:
	"""The Preamble normative section list is a set semantically."""
	data = json.loads((FIXTURE_DIR / "valid_module.json").read_text(encoding="utf-8"))
	data["doc"]["Preamble"]["normative_sections"].append("Contract")
	assert "normative-duplicate" in {issue.code for issue in validate_authoring_document(load_authoring_document(data))}


def test_authoring_semantics_requires_normative_description_to_be_declared() -> None:
	"""Description may be normative, but only when Preamble declares that mode."""
	data = json.loads((FIXTURE_DIR / "valid_module.json").read_text(encoding="utf-8"))
	data["doc"]["Description"] = [{"paragraph": "|Must| describe the public API."}]
	assert "normative-keyword-missing-section" in {
		issue.code for issue in validate_authoring_document(load_authoring_document(data))
	}


def test_authoring_semantics_checks_redundant_preamble_profile() -> None:
	"""The redundant local profile remains meaningful outside Schema validation."""
	data = json.loads((FIXTURE_DIR / "valid_module.json").read_text(encoding="utf-8"))
	data["doc"]["Preamble"]["profile"] = "class"
	assert "preamble-profile-mismatch" in {
		issue.code for issue in validate_authoring_document(load_authoring_document(data))
	}
