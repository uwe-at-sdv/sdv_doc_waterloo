#!/usr/bin/env python3
"""End-to-end tests for extract-authoring-json."""

from __future__ import annotations

import json

from pytest_common import DIR_DOC_EXAMPLES, DIR_EXAMPLES, DIR_MODULE, run_waterlint
from sdv.doc.waterloo.docitem_docstring import make_docitem_tree
from sdv.doc.waterloo.docitem_helper import tracer
from sdv.doc.waterloo.docitem_validator import get_profile
from sdv.doc.waterloo.waterlint_authoring import load_authoring_document, render_authoring_document


def test_extract_authoring_json_roundtrips_a_documented_function() -> None:
	"""Extraction emits valid editable JSON for one source-validated callable."""
	result = run_waterlint(
		"extract-authoring-json",
		"--basedir", DIR_MODULE,
		"--obj", "waterlint_authoring.load_authoring_document",
		"--out", "@STDOUT",
	)
	assert result.returncode == 0, result.stderr

	document_json = json.loads(result.stdout)
	assert document_json["profile"] == "function"
	assert document_json["qualified_name"] == "waterlint_authoring.load_authoring_document"
	assert document_json["doc"]["Preamble"]["profile"] == "function"

	document = load_authoring_document(document_json)
	rendered = render_authoring_document(document)
	assert get_profile(make_docitem_tree(tracer(), rendered)) == "function"


def test_extract_authoring_json_preserves_tables_and_lists() -> None:
	"""Extraction retains table groups and ordinary Authoring JSON list blocks."""
	result = run_waterlint(
		"extract-authoring-json",
		"--basedir", DIR_DOC_EXAMPLES,
		"--obj", "test_tables",
	)
	assert result.returncode == 0, result.stderr

	document_json = json.loads(result.stdout)
	doc = document_json["doc"]
	assert isinstance(doc, dict)
	description = doc["Description"]
	assert isinstance(description, list)
	assert any("list" in block for block in description if isinstance(block, dict))
	notes = doc["Notes"]
	assert isinstance(notes, dict)
	assert any("table" in block for block in notes["Application"] if isinstance(block, dict))

	document = load_authoring_document(document_json)
	rendered = render_authoring_document(document)
	assert "|begin_table|" in rendered
	assert "\t* |label|`Description`" in rendered
	assert get_profile(make_docitem_tree(tracer(), rendered)) == "module"


def test_extract_authoring_json_preserves_definition_inheritance() -> None:
	"""Extraction preserves term identifiers inherited from the direct module."""
	result = run_waterlint(
		"extract-authoring-json",
		"--basedir", DIR_EXAMPLES,
		"--obj", "pytest_good_definitions.X",
	)
	assert result.returncode == 0, result.stderr

	document_json = json.loads(result.stdout)
	definitions = document_json["doc"]["Definitions"]
	assert isinstance(definitions, dict)
	assert definitions["_inherit"] == ["Sensitive"]

	rendered = render_authoring_document(load_authoring_document(document_json))
	assert "\t_inherit:\n\t\tSensitive\n" in rendered
