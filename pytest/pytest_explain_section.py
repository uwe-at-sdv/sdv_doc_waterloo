#!/usr/bin/env python3
"""Pytests for waterlint subcommand explain-section."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pytest_common import DIR_SCHEMA, run_waterlint
from sdv.doc.waterloo.waterlint_explain_common import SECTION_PROPERTIES, SECTION_SUBSECTIONS


PROFILE_ORDER = ("module", "class", "function", "method", "inherited_method")
SCHEMA_PATH = Path(DIR_SCHEMA) / "wtrl-explain-section-json-0.1.0.schema.json"


def _matrix_cases() -> list[pytest.ParameterSet]:
	cases: list[pytest.ParameterSet] = []
	for profile in PROFILE_ORDER:
		for label, profile_map in SECTION_SUBSECTIONS.items():
			if profile not in profile_map:
				continue
			cases.append(pytest.param(profile, label, id=f"{profile}:{label}"))
	return cases


@pytest.mark.parametrize("profile,label", _matrix_cases())
def test_explain_section_matrix_profile_section(profile: str, label: str, tmp_path: Path) -> None:
	out_file = tmp_path / f"{profile}.{label}.json"
	res = run_waterlint(
		"explain-section",
		"--label",
		label,
		"--profile",
		profile,
		"--out-json",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr
	assert out_file.exists(), out_file

	result = run_waterlint("validate-json", "--in", str(out_file), "--schema", str(SCHEMA_PATH))
	assert result.returncode == 0, result.stderr

	doc = json.loads(out_file.read_text(encoding="utf-8"))

	assert doc["kind"] == "section_explanation", doc
	assert doc["profile"] == profile, doc
	assert doc["label"] == label, doc
	assert doc["body_category"] == SECTION_PROPERTIES[label]["category"], doc
	assert doc["normativity"] == SECTION_PROPERTIES[label]["normativity"], doc
	assert doc["label_kind"] == SECTION_PROPERTIES[label]["label_kind"], doc
	assert doc["must_exist"] == SECTION_PROPERTIES[label]["must_exist"], doc

	expected_profiles = [p for p in PROFILE_ORDER if p in SECTION_SUBSECTIONS[label]]
	assert doc["available_profiles"] == expected_profiles, doc
	assert [sub["label"] for sub in doc["subsections"]] == SECTION_SUBSECTIONS[label][profile], doc
	assert doc["try_self"] == f"waterlint explain-section --label {label} --profile PROFILE", doc
	assert isinstance(doc["hint"], list), doc
	assert isinstance(doc["try_next"], list), doc


def test_explain_section_validate_json_rejects_missing_hint(tmp_path: Path) -> None:
	out_file = tmp_path / "missing-hint.json"
	res = run_waterlint(
		"explain-section",
		"--label",
		"Parameters",
		"--profile",
		"function",
		"--out-json",
		str(out_file),
	)
	assert res.returncode == 0, res.stderr

	doc = json.loads(out_file.read_text(encoding="utf-8"))
	assert "hint" in doc, doc
	del doc["hint"]
	out_file.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

	result = run_waterlint("validate-json", "--in", str(out_file), "--schema", str(SCHEMA_PATH))
	assert result.returncode == 1, result.stderr
	assert "hint" in result.stderr or "required property" in result.stderr, result.stderr
