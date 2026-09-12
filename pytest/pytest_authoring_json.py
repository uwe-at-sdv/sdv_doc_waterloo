#!/usr/bin/env python3
"""Schema and automatic category-detection tests for Waterloo Authoring JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from pytest_common import DIR_SCHEMA, run_waterlint


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "authoring_json"
SCHEMA_PATH = Path(DIR_SCHEMA) / "wtrl-authoring-object-json-0.1.0.schema.json"


def _validate_fixture(name: str):
	"""Run validate-json without --schema to exercise automatic schema selection."""
	return run_waterlint("validate-json", "--in", str(FIXTURE_DIR / name))


def test_authoring_schema_is_a_valid_draft_2020_12_schema() -> None:
	"""Keep schema syntax and self-references valid before testing document fixtures."""
	schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
	Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize(
	"name",
	[
		"valid_module.json",
		"valid_class.json",
		"valid_function.json",
		"valid_method.json",
		"valid_inherited_method.json",
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
		("invalid_unknown_category.json", "JSCH-003"),
	],
)
def test_authoring_json_invalid_fixtures_are_rejected(name: str, rule_id: str) -> None:
	"""Reject malformed authoring documents before rendering can begin."""
	result = _validate_fixture(name)
	assert result.returncode == 1, result.stderr
	assert rule_id in result.stderr, result.stderr
