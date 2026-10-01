#!/usr/bin/env python3
"""Renderer tests for Waterloo Authoring JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sdv.doc.waterloo.docitem_docstring import make_docitem_tree
from sdv.doc.waterloo.docitem_helper import tracer
from sdv.doc.waterloo.docitem_sections import docitem_definitions
from sdv.doc.waterloo.docitem_validator import get_profile
from sdv.doc.waterloo.waterlint_authoring import load_authoring_document, render_authoring_document


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "authoring_json"


def _load_data(name: str) -> dict[str, object]:
	return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize(
	"name",
	[
		"maximal_module.json",
		"maximal_class.json",
		"maximal_function.json",
		"maximal_method.json",
		"maximal_inherited_method.json",
	],
)
def test_rendered_maximal_authoring_document_builds_docitem_tree(name: str) -> None:
	"""Every maximal Authoring document renders to syntax accepted by Waterloo."""
	document = load_authoring_document(_load_data(name))
	rendered = render_authoring_document(document)
	tree = make_docitem_tree(tracer(), rendered)
	assert get_profile(tree) == document.profile
	assert rendered.startswith("Preamble:\n")
	assert rendered.endswith("\n")


def test_renderer_keeps_inline_role_bodies_intact_when_wrapping() -> None:
	"""A role body containing whitespace must remain one indivisible output token."""
	data = _load_data("valid_function.json")
	contract = data["doc"]["Contract"]
	assert isinstance(contract, dict)
	contract["requires"] = [
		"|Must| keep |ref|`The reference label <wtrl://demo.module.Widget>` intact while rendering a deliberately long rule."
	]
	rendered = render_authoring_document(load_authoring_document(data), width=52)
	assert "|ref|`The reference label <wtrl://demo.module.Widget>`" in rendered
	assert "\\\n" in rendered
	make_docitem_tree(tracer(), rendered)


def test_renderer_keeps_punctuation_attached_to_inline_roles() -> None:
	"""Sentence punctuation after a role must not acquire an artificial space."""
	data = _load_data("valid_function.json")
	contract = data["doc"]["Contract"]
	assert isinstance(contract, dict)
	contract["general"] = ["|Must| return an |class|`AuthoringSemanticIssue`."]
	rendered = render_authoring_document(load_authoring_document(data))
	assert "|class|`AuthoringSemanticIssue`." in rendered
	assert "|class|`AuthoringSemanticIssue` ." not in rendered


def test_renderer_uses_configured_indentation_unit() -> None:
	"""SPC4 indentation applies to every generated physical line."""
	document = load_authoring_document(_load_data("valid_module.json"))
	rendered = render_authoring_document(document, indent_unit="SPC4", indentation=2)
	assert rendered.startswith("        Preamble:\n")
	assert "\t" not in rendered
	assert all(line.startswith("        ") for line in rendered.splitlines())


def test_renderer_uses_waterloo_markers_for_nested_lists() -> None:
	"""Nested Authoring lists are represented through distinct Waterloo markers."""
	document = load_authoring_document(_load_data("maximal_module.json"))
	rendered = render_authoring_document(document)
	assert "\t* A top-level item." in rendered
	assert "\t+ A nested item." in rendered


def test_renderer_keeps_wrapped_raises_paragraph_as_one_logical_line() -> None:
	"""A wrapped Raises paragraph needs one Sphinx statement bullet, not several."""
	data = _load_data("valid_function.json")
	doc = data["doc"]
	assert isinstance(doc, dict)
	doc["Raises"] = {
		"ValueError": [{
			"paragraph": (
				"|Must| raise if a required attribute is missing and therefore the "
				"whole configuration cannot be parsed at all."
			),
		}],
	}

	rendered = render_authoring_document(load_authoring_document(data), width=52)
	assert "\t\t* " not in rendered
	assert "\\\n" in rendered
	tree = make_docitem_tree(tracer(), rendered)
	assert tree.item("Raises").item("ValueError").items() == [
		"|Must| raise if a required attribute is missing and therefore the whole "
		"configuration cannot be parsed at all.",
	]


def test_renderer_keeps_factory_statements_as_itemized_logical_lines() -> None:
	"""Factory paragraphs use the same no-marker statement form as Raises."""
	data = _load_data("maximal_class.json")
	doc = data["doc"]
	assert isinstance(doc, dict)
	doc["Factory"] = {
		"demo.maximum_module.make_widget": [
			{"paragraph": "|Must| create a Widget with a valid default configuration."},
			{"paragraph": "|May| reuse an existing compatible Widget instance."},
		],
	}

	rendered = render_authoring_document(load_authoring_document(data), width=52)
	factory_lines = rendered.split("Public_classes:", 1)[0]
	assert "\t\t* " not in factory_lines
	assert "\t\t|\n" not in factory_lines
	tree = make_docitem_tree(tracer(), rendered)
	assert tree.item("Factory").item("demo.maximum_module.make_widget").items() == [
		"|Must| create a Widget with a valid default configuration.",
		"|May| reuse an existing compatible Widget instance.",
	]


def test_renderer_writes_definition_inheritance_as_identifier_list() -> None:
	"""Definitions._inherit is rendered as the direct module's term identifiers."""
	data = _load_data("valid_class.json")
	doc = data["doc"]
	assert isinstance(doc, dict)
	doc["Definitions"] = {
		"_inherit": ["SharedTerm", "SharedVariation"],
		"LocalTerm": [{"paragraph": "A local definition."}],
	}

	rendered = render_authoring_document(load_authoring_document(data))
	assert "\t_inherit:\n\t\tSharedTerm, SharedVariation\n" in rendered
	tree = make_docitem_tree(tracer(), rendered)
	definitions = tree.item("Definitions")
	assert isinstance(definitions, docitem_definitions)
	assert definitions.inherited() == ["SharedTerm", "SharedVariation"]


def test_renderer_writes_contract_traits_as_csv() -> None:
	"""Contract.traits is a flat identifier list, not a sequence of text items."""
	data = _load_data("valid_class.json")
	contract = data["doc"]["Contract"]
	assert isinstance(contract, dict)
	contract["traits"] = ["abstract", "final"]
	rendered = render_authoring_document(load_authoring_document(data))
	assert "\ttraits:\n\t\tabstract, final\n" in rendered
	make_docitem_tree(tracer(), rendered)


def test_renderer_writes_keyed_table_blocks_in_declared_column_order() -> None:
	"""Authoring tables render as Waterloo table blocks without exposing JSON keys."""
	data = _load_data("valid_module.json")
	data["doc"]["Description"] = [{"table": {"groups": [{
		"title": ["Result values"],
		"columns": [{"key": "code", "header": "Code"}, {"key": "meaning", "header": "Meaning"}],
		"rows": [{"cells": {"meaning": "success", "code": "0"}}],
	}, {
		"title": ["Error values"],
		"columns": [{"key": "code", "header": "Code"}, {"key": "meaning", "header": "Meaning"}],
		"rows": [{"cells": {"meaning": "failure", "code": "1"}}],
	}]}}]
	rendered = render_authoring_document(load_authoring_document(data))
	assert (
		"\t|begin_table|\n"
		"\t|title|\n"
		"\tResult values\n"
		"\t|columns|\n"
		"\tCode |tab| Meaning\n"
		"\t|rows|\n"
		"\t0 |tab| success\n"
		"\t|title|\n"
		"\tError values\n"
		"\t|columns|\n"
		"\tCode |tab| Meaning\n"
		"\t|rows|\n"
		"\t1 |tab| failure\n"
		"\t|end_table|\n"
	) in rendered
	assert "\t|\n\t|title|" not in rendered
	make_docitem_tree(tracer(), rendered)
