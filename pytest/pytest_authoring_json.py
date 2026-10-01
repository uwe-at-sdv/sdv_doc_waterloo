#!/usr/bin/env python3
"""Schema and automatic category-detection tests for Waterloo Authoring JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from pytest_common import DIR_SCHEMA, run_waterlint
from sdv.doc.waterloo.waterlint_authoring import (
	AuthoringDefinitions, load_authoring_document, validate_authoring_document,
)


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "authoring_json"
SCHEMA_PATH = Path(DIR_SCHEMA) / "wtrl-authoring-object-json-0.3.0.schema.json"
SCHEMA_040_PATH = Path(DIR_SCHEMA) / "wtrl-authoring-object-json-0.4.0.schema.json"


def _validate_fixture(name: str):
	"""Run validate-json without --schema to exercise automatic schema selection."""
	return run_waterlint("validate-json", "--in", str(FIXTURE_DIR / name))


def test_authoring_schema_is_a_valid_draft_2020_12_schema() -> None:
	"""Keep schema syntax and self-references valid before testing document fixtures."""
	for path in (SCHEMA_PATH, SCHEMA_040_PATH):
		schema = json.loads(path.read_text(encoding="utf-8"))
		Draft202012Validator.check_schema(schema)


def test_authoring_schema_040_accepts_definitions_inherit_for_non_modules_only() -> None:
	"""Schema 0.4 reserves Definitions._inherit for non-module qualified identifiers."""
	schema = json.loads(SCHEMA_040_PATH.read_text(encoding="utf-8"))
	document = {
		"$schema": "https://sci-d-vis.com/schema/wtrl-authoring-object-json-0.4.0.schema.json",
		"$id": "urn:waterlint:wtrl-authoring-object-json:demo.inherited-definitions",
		"__WTRL_CATEGORY__": "wtrl-authoring-object-json",
		"__WTRL_VERSION__": {"schema": "0.4.0"},
		"qualified_name": "demo.InheritedDefinitions",
		"profile": "class",
		"doc": {
			"Preamble": {"profile": "class", "normative_sections": ["Contract", "Definitions"]},
			"Contract": {
				"general": ["|Must| inherit selected definitions."],
				"constructor": ["|Must| create an instance."],
			},
			"Definitions": {
				"_inherit": ["SharedTerm"],
				"LocalTerm": [{"paragraph": "A local definition."}],
			},
		},
	}
	validator = Draft202012Validator(schema)
	assert list(validator.iter_errors(document)) == []

	document["doc"]["Definitions"]["_inherit"] = [{"paragraph": "Not an identifier list."}]
	assert list(validator.iter_errors(document))

	document["doc"]["Definitions"]["_inherit"] = ["SharedTerm"]
	document["profile"] = "module"
	document["doc"]["Preamble"]["profile"] = "module"
	document["doc"]["Contract"] = {"general": ["|Must| be a module."]}
	assert list(validator.iter_errors(document))


def test_authoring_loader_keeps_inherited_and_local_definitions_separate() -> None:
	"""The typed model must not treat Definitions._inherit as a text-block item."""
	document = {
		"qualified_name": "demo.InheritedDefinitions",
		"profile": "class",
		"doc": {
			"Preamble": {"profile": "class", "normative_sections": ["Contract", "Definitions"]},
			"Contract": {
				"general": ["|Must| inherit selected definitions."],
				"constructor": ["|Must| create an instance."],
			},
			"Definitions": {
				"_inherit": ["SharedTerm"],
				"LocalTerm": [{"paragraph": "A local definition."}],
			},
		},
	}
	loaded = load_authoring_document(document)
	section = loaded.section("Definitions")
	assert section is not None
	assert isinstance(section.value, AuthoringDefinitions)
	assert section.value.inherit == ("SharedTerm",)
	assert tuple(section.value.entries) == ("LocalTerm",)


def test_authoring_semantics_reject_definition_inheritance_for_modules() -> None:
	"""Direct Python callers receive the same module inheritance restriction as JSON input."""
	document = load_authoring_document({
		"qualified_name": "demo.module",
		"profile": "module",
		"doc": {
			"Preamble": {"profile": "module", "normative_sections": ["Contract", "Definitions"]},
			"Contract": {"general": ["|Must| reject inherited definitions."]},
			"Definitions": {"_inherit": ["SharedTerm"]},
		},
	})
	issues = validate_authoring_document(document)
	assert [(issue.code, issue.path) for issue in issues] == [
		("definitions-inherit-module", "doc.Definitions._inherit"),
	]

def test_authoring_schema_accepts_keyed_table_blocks(tmp_path: Path) -> None:
	"""Schema 0.3 accepts tables only through a free-form text-block position."""
	document = {
		"$schema": "https://sci-d-vis.com/schema/wtrl-authoring-object-json-0.3.0.schema.json",
		"$id": "urn:waterlint:wtrl-authoring-object-json:demo.table",
		"__WTRL_CATEGORY__": "wtrl-authoring-object-json",
		"__WTRL_VERSION__": {"schema": "0.3.0"},
		"qualified_name": "demo.table",
		"profile": "module",
		"doc": {
			"Preamble": {"profile": "module", "normative_sections": ["Contract"]},
			"Contract": {"general": ["|Must| provide a table."]},
			"Description": [{"table": {"groups": [{
				"title": ["Result values"],
				"columns": [{"key": "code", "header": "Code"}, {"key": "meaning", "header": "Meaning"}],
				"rows": [{"cells": {"code": "0", "meaning": "success"}}, {"cells": {"code": "1", "meaning": ""}}],
			}]}}],
		},
	}
	path = tmp_path / "table-authoring.json"
	path.write_text(json.dumps(document), encoding="utf-8")
	result = run_waterlint("validate-json", "--in", str(path))
	assert result.returncode == 0, result.stderr

	# Contract remains a list of logical text items, not a free-form block sequence.
	document["doc"]["Contract"]["general"] = document["doc"]["Description"]
	path.write_text(json.dumps(document), encoding="utf-8")
	result = run_waterlint("validate-json", "--in", str(path))
	assert result.returncode == 1, result.stderr
	assert "JSCH-005" in result.stderr, result.stderr


@pytest.mark.parametrize("contract_label", ["invariants", "requires", "ensures"])
def test_authoring_schema_rejects_callable_contract_entries_for_classes(
	tmp_path: Path, contract_label: str,
) -> None:
	"""Class contracts must not use function- or method-only subsections."""
	document = json.loads((FIXTURE_DIR / "valid_class.json").read_text(encoding="utf-8"))
	document["$schema"] = "https://sci-d-vis.com/schema/wtrl-authoring-object-json-0.3.0.schema.json"
	document["__WTRL_VERSION__"] = {"schema": "0.3.0"}
	document["doc"]["Contract"][contract_label] = ["|Must| be rejected by the profile schema."]
	path = tmp_path / f"class-contract-{contract_label}.json"
	path.write_text(json.dumps(document), encoding="utf-8")

	result = run_waterlint("validate-json", "--in", str(path))
	assert result.returncode == 1, result.stderr
	assert "JSCH-005" in result.stderr, result.stderr
	assert "'/doc/Contract'" in result.stderr, result.stderr
	assert contract_label in result.stderr, result.stderr


def test_authoring_schema_requires_constructor_for_classes(tmp_path: Path) -> None:
	"""The class-specific Contract shape requires a constructor subsection."""
	document = json.loads((FIXTURE_DIR / "valid_class.json").read_text(encoding="utf-8"))
	document["$schema"] = "https://sci-d-vis.com/schema/wtrl-authoring-object-json-0.3.0.schema.json"
	document["__WTRL_VERSION__"] = {"schema": "0.3.0"}
	del document["doc"]["Contract"]["constructor"]
	path = tmp_path / "class-contract-missing-constructor.json"
	path.write_text(json.dumps(document), encoding="utf-8")

	result = run_waterlint("validate-json", "--in", str(path))
	assert result.returncode == 1, result.stderr
	assert "JSCH-005" in result.stderr, result.stderr
	assert "constructor" in result.stderr, result.stderr


def test_authoring_schema_rejects_callable_sections_for_classes(tmp_path: Path) -> None:
	"""Class documents must reject sections reserved for callable profiles."""
	document = json.loads((FIXTURE_DIR / "valid_class.json").read_text(encoding="utf-8"))
	document["$schema"] = "https://sci-d-vis.com/schema/wtrl-authoring-object-json-0.3.0.schema.json"
	document["__WTRL_VERSION__"] = {"schema": "0.3.0"}
	document["doc"]["Parameters"] = {
		"value": [{"paragraph": "This callable-only section must be rejected."}],
	}
	path = tmp_path / "class-callable-section.json"
	path.write_text(json.dumps(document), encoding="utf-8")

	result = run_waterlint("validate-json", "--in", str(path))
	assert result.returncode == 1, result.stderr
	assert "JSCH-005" in result.stderr, result.stderr
	assert "'/doc'" in result.stderr, result.stderr
	assert "'Parameters' is not one of" in result.stderr, result.stderr


def test_authoring_schema_localizes_invalid_table_block_once(tmp_path: Path) -> None:
	"""A discriminated table block must expose its local structural error once."""
	document = json.loads((FIXTURE_DIR / "valid_class.json").read_text(encoding="utf-8"))
	document["$schema"] = "https://sci-d-vis.com/schema/wtrl-authoring-object-json-0.3.0.schema.json"
	document["__WTRL_VERSION__"] = {"schema": "0.3.0"}
	document["doc"]["Description"] = [
		{"paragraph": "A valid paragraph before the malformed table."},
		{"table": {"groups": [{"title": ["Broken"], "rows": [{"cells": {"key": "value"}}]}]}},
	]
	path = tmp_path / "invalid-table-block.json"
	path.write_text(json.dumps(document), encoding="utf-8")

	result = run_waterlint("validate-json", "--in", str(path))
	assert result.returncode == 1, result.stderr
	assert result.stderr.count("JSCH-005") == 1, result.stderr
	assert "'/doc/Description/1/table/groups/0'" in result.stderr, result.stderr
	assert "'columns' is a required property" in result.stderr, result.stderr


def test_validate_json_checks_authoring_normative_sections(tmp_path: Path) -> None:
	"""Authoring JSON validation must apply cross-field normative-section rules."""
	document = json.loads((FIXTURE_DIR / "valid_function.json").read_text(encoding="utf-8"))
	document["$schema"] = "https://sci-d-vis.com/schema/wtrl-authoring-object-json-0.3.0.schema.json"
	document["__WTRL_VERSION__"] = {"schema": "0.3.0"}
	document["doc"]["Preamble"]["normative_sections"].remove("Raises")
	path = tmp_path / "missing-normative-raises.json"
	path.write_text(json.dumps(document), encoding="utf-8")

	result = run_waterlint("validate-json", "--in", str(path))
	assert result.returncode == 1, result.stderr
	assert "JIDO-001" in result.stderr, result.stderr
	assert "Normative section 'Raises' must be listed" in result.stderr, result.stderr


def test_validate_json_rejects_whitespace_only_returns(tmp_path: Path) -> None:
	"""Returns must contain text after stripping whitespace."""
	document = json.loads((FIXTURE_DIR / "valid_function.json").read_text(encoding="utf-8"))
	document["$schema"] = "https://sci-d-vis.com/schema/wtrl-authoring-object-json-0.3.0.schema.json"
	document["__WTRL_VERSION__"] = {"schema": "0.3.0"}
	document["doc"]["Returns"] = [{"paragraph": "   "}]
	path = tmp_path / "whitespace-returns.json"
	path.write_text(json.dumps(document), encoding="utf-8")

	result = run_waterlint("validate-json", "--in", str(path))
	assert result.returncode == 0, result.stderr
	assert "JIDO-001" in result.stderr, result.stderr
	assert "Warning" in result.stderr, result.stderr
	assert "Returns should contain non-whitespace content." in result.stderr, result.stderr


@pytest.mark.parametrize(
	"name",
	[
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
	],
)
def test_authoring_json_valid_profiles_are_auto_detected(name: str) -> None:
	"""Every supported profile must validate through __WTRL_CATEGORY__ without --schema."""
	result = _validate_fixture(name)
	assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
	("name", "rule_id"),
	[
		("invalid_unknown_key.json", "JSCH-005"),
		("invalid_profile_mismatch.json", "JSCH-005"),
		("invalid_physical_line.json", "JSCH-005"),
		("invalid_list_item.json", "JSCH-005"),
		("invalid_definitions_inherit.json", "JSCH-005"),
		("invalid_definition_label.json", "JSCH-005"),
		("invalid_unknown_category.json", "JSCH-003"),
	],
)
def test_authoring_json_invalid_fixtures_are_rejected(name: str, rule_id: str) -> None:
	"""Reject malformed authoring documents before rendering can begin."""
	result = _validate_fixture(name)
	assert result.returncode == 1, result.stderr
	assert rule_id in result.stderr, result.stderr
