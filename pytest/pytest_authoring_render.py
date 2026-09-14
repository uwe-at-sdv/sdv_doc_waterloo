#!/usr/bin/env python3
"""Renderer tests for Waterloo Authoring JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sdv.doc.waterloo.docitem_docstring import make_docitem_tree
from sdv.doc.waterloo.docitem_helper import tracer
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


def test_renderer_writes_contract_traits_as_csv() -> None:
	"""Contract.traits is a flat identifier list, not a sequence of text items."""
	data = _load_data("valid_class.json")
	contract = data["doc"]["Contract"]
	assert isinstance(contract, dict)
	contract["traits"] = ["abstract", "final"]
	rendered = render_authoring_document(load_authoring_document(data))
	assert "\ttraits:\n\t\tabstract, final\n" in rendered
	make_docitem_tree(tracer(), rendered)
