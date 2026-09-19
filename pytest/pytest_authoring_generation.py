#!/usr/bin/env python3
"""Golden and roundtrip tests for Authoring JSON generator commands."""

from __future__ import annotations

import json
from pathlib import Path

from pytest_common import DIR_MODULE, run_waterlint
from sdv.doc.waterloo.docitem_docstring import make_docitem_tree
from sdv.doc.waterloo.docitem_helper import tracer
from sdv.doc.waterloo.docitem_validator import get_profile
from sdv.doc.waterloo.waterlint_authoring import load_authoring_document, render_authoring_document, validate_authoring_document


def _generate(command: str, qualified_name: str):
	return run_waterlint(
		command,
		"--basedir", DIR_MODULE,
		"--obj", qualified_name,
	)


def test_gen_minimal_authoring_json_function_golden_output() -> None:
	"""Minimal generation must emit one deterministic, directly editable JSON object."""
	result = _generate("gen-minimal-authoring-json", "docitem_helper.get_obj_name")
	assert result.returncode == 0, result.stderr
	expected = {
		"$schema": "https://sci-d-vis.com/schema/wtrl-authoring-object-json-0.1.0.schema.json",
		"$id": "urn:waterlint:wtrl-authoring-object-json:docitem_helper.get_obj_name",
		"__WTRL_CATEGORY__": "wtrl-authoring-object-json",
		"__WTRL_VERSION__": {"schema": "0.1.0"},
		"qualified_name": "docitem_helper.get_obj_name",
		"profile": "function",
		"doc": {
			"Preamble": {
				"profile": "function",
				"normative_sections": ["Contract", "Parameters", "Returns", "Raises"],
			},
			"Contract": {"general": ["|Must| describe the externally visible behavior."]},
			"Parameters": {"obj": [{"paragraph": "TODO: describe |var|`obj`."}]},
			"Returns": [{"paragraph": "TODO: describe the return value."}],
			"Raises": {},
		},
		"signature": "(obj: 'object') -> 'str'",
	}
	assert result.stdout == json.dumps(expected, indent=4, ensure_ascii=False) + "\n"


def test_gen_full_authoring_json_class_golden_output() -> None:
	"""Full generation adds every safely representable class-level structure."""
	result = _generate("gen-full-authoring-json", "docitem_tracer.tracer")
	assert result.returncode == 0, result.stderr
	expected = {
		"$schema": "https://sci-d-vis.com/schema/wtrl-authoring-object-json-0.1.0.schema.json",
		"$id": "urn:waterlint:wtrl-authoring-object-json:docitem_tracer.tracer",
		"__WTRL_CATEGORY__": "wtrl-authoring-object-json",
		"__WTRL_VERSION__": {"schema": "0.1.0"},
		"qualified_name": "docitem_tracer.tracer",
		"profile": "class",
		"doc": {
			"Preamble": {
				"profile": "class",
				"normative_sections": [
					"Contract", "Definitions", "Factory", "Public_types",
					"Public_variables", "Public_constants",
				],
			},
			"Contract": {
				"general": ["|Must| describe the externally visible behavior."],
				"constructor": ["|Must| describe construction requirements and guarantees."],
			},
			"Definitions": {},
			"Terminology": {},
			"Description": [{"paragraph": "TODO: provide an informative description."}],
			"Factory": {},
			"Class_overview": {},
			"Method_overview": {},
			"Public_types": {},
			"Public_variables": {},
			"Public_constants": {},
			"Notes": {},
		},
	}
	assert result.stdout == json.dumps(expected, indent=4, ensure_ascii=False) + "\n"


def test_generated_authoring_json_validates_and_roundtrips_to_waterloo(tmp_path: Path) -> None:
	"""Generated JSON must validate and render to a docstring accepted by the parser."""
	generated = _generate("gen-minimal-authoring-json", "docitem_helper.get_obj_name")
	assert generated.returncode == 0, generated.stderr
	path = tmp_path / "generated-authoring.json"
	path.write_text(generated.stdout, encoding="utf-8")

	validated = run_waterlint("validate-json", "--in", str(path))
	assert validated.returncode == 0, validated.stderr
	document = load_authoring_document(json.loads(generated.stdout))
	assert validate_authoring_document(document) == []
	rendered = render_authoring_document(document)
	assert get_profile(make_docitem_tree(tracer(), rendered)) == "function"
