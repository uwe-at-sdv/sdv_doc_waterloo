#!/usr/bin/env python3
"""Pytests for waterlint subcommand explain-subsection."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pytest_common import DIR_SCHEMA, run_waterlint
from sdv.doc.waterloo.waterlint_explain_common import SECTION_PROPERTIES


PROFILE_ORDER = ("module", "class", "function", "method", "inherited_method")
SCHEMA_PATH = Path(DIR_SCHEMA) / "wtrl-explain-subsection-json-0.1.0.schema.json"


def _subsection_matrix_cases() -> list[pytest.ParameterSet]:
	cases: list[pytest.ParameterSet] = []
	for label, props in SECTION_PROPERTIES.items():
		if "." not in label:
			continue
		profiles = props.get("profile") or []
		for profile in PROFILE_ORDER:
			if profile not in profiles:
				continue
			cases.append(pytest.param(profile, label, id=f"{profile}:{label}"))
	return cases


@pytest.mark.parametrize("profile,label", _subsection_matrix_cases())
def test_explain_subsection_matrix_profile_section(profile: str, label: str, tmp_path: Path) -> None:
	out_file = tmp_path / f"{profile}.{label}.json"
	res = run_waterlint(
		"explain-subsection",
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
	section_label, subsection_label = label.split(".", 1)
	props = SECTION_PROPERTIES[label]

	assert doc["kind"] == "subsection_explanation", doc
	assert doc["profile"] == profile, doc
	assert doc["section_label"] == section_label, doc
	assert doc["subsection_label"] == subsection_label, doc
	assert doc["label"] == label, doc
	assert doc["title"] == label, doc
	assert doc["section_title"] == section_label, doc
	assert doc["body"]["category"] == props["category"], doc
	assert isinstance(doc["body"]["explanation"], list), doc
	assert isinstance(doc["body"]["content"], list), doc
	assert doc["normativity"] == props["normativity"], doc
	assert doc["label_kind"] == props["label_kind"], doc
	assert doc["must_exist"] == props["must_exist"], doc
	assert doc["available_profiles"] == [p for p in PROFILE_ORDER if p in (props["profile"] or [])], doc
	assert doc["try_self"] == f"waterlint explain-subsection --label {label} --profile PROFILE", doc
	assert doc["try_next"] == [f"waterlint explain-section --label {section_label} --profile PROFILE"], doc
	assert isinstance(doc["hint"], list), doc
	assert isinstance(doc["template"], list), doc


def test_explain_subsection_validate_json_rejects_missing_hint(tmp_path: Path) -> None:
	out_file = tmp_path / "missing-hint.json"
	res = run_waterlint(
		"explain-subsection",
		"--label",
		"Contract.requires",
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
