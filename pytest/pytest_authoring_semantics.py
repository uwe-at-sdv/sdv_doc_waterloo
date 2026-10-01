#!/usr/bin/env python3
"""Source-independent semantic tests for Waterloo Authoring JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sdv.doc.waterloo.docitem_helper import get_allowed_sections_for_profile
from sdv.doc.waterloo.waterlint_authoring import (
	AuthoringDocument,
	AuthoringParagraph,
	AuthoringSection,
	AuthoringTableBlock,
	AuthoringTableColumn,
	AuthoringTableGroup,
	AuthoringTableRow,
	load_authoring_document,
	validate_authoring_document,
)


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


@pytest.mark.parametrize("contract_label", ["invariants", "requires", "ensures"])
def test_authoring_semantics_defensively_rejects_callable_contract_entries_for_classes(
	contract_label: str,
) -> None:
	"""Direct Python callers receive the same profile guard as Schema users."""
	data = json.loads((FIXTURE_DIR / "valid_class.json").read_text(encoding="utf-8"))
	data["doc"]["Contract"][contract_label] = ["|Must| be rejected."]
	issues = validate_authoring_document(load_authoring_document(data))
	assert any(
		issue.code == "contract-subsection-profile"
		and issue.path == f"doc.Contract.{contract_label}"
		for issue in issues
	)


def test_authoring_semantics_defensively_requires_class_constructor() -> None:
	"""Direct Python callers retain the profile-specific constructor requirement."""
	data = json.loads((FIXTURE_DIR / "valid_class.json").read_text(encoding="utf-8"))
	del data["doc"]["Contract"]["constructor"]
	issues = validate_authoring_document(load_authoring_document(data))
	assert any(
		issue.code == "contract-required-subsection"
		and issue.path == "doc.Contract"
		for issue in issues
	)


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


def test_authoring_semantics_checks_keyed_table_rows() -> None:
	"""Table column keys and row cell keys require checks beyond JSON Schema."""
	base = _load("valid_module.json")
	table = AuthoringTableBlock((AuthoringTableGroup(
		title=None,
		columns=(
			AuthoringTableColumn("code", "Code"),
			AuthoringTableColumn("code", "Meaning"),
		),
		rows=(AuthoringTableRow({"code": "0", "unexpected": "failure"}),),
	),))
	document = AuthoringDocument(
		qualified_name=base.qualified_name,
		profile=base.profile,
		signature=base.signature,
		sections={
			**base.sections,
			"Description": AuthoringSection("Description", (AuthoringParagraph("Overview."), table)),
		},
	)
	codes = {issue.code for issue in validate_authoring_document(document)}
	assert codes >= {"table-duplicate-column-key", "table-row-cells"}
