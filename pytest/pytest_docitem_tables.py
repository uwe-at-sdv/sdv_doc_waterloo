#!/usr/bin/env python3
"""Parser and AST tests for Waterloo table blocks."""

from __future__ import annotations

import pytest

from sdv.doc.waterloo.docitem_docstring import make_docitem_tree
from sdv.doc.waterloo.docitem_exceptions import ParseError
from sdv.doc.waterloo.docitem_tables import parse_table_content_blocks
from sdv.doc.waterloo.docitem_tracer import tracer


def test_parse_table_content_blocks_preserves_text_and_empty_cells() -> None:
	blocks = parse_table_content_blocks(tracer(), [
		"Text before the table.",
		"|begin_table|",
		"|columns|",
		"Name |tab| Type |tab| Description",
		"|rows|",
		"alpha |tab| |tab| First value",
		"|end_table|",
		"Text after the table.",
	])

	assert blocks[0] == "Text before the table."
	table = blocks[1]
	assert not isinstance(table, str)
	assert table.groups()[0].title() is None
	assert table.groups()[0].header() == ["Name", "Type", "Description"]
	assert table.groups()[0].rows() == [["alpha", "", "First value"]]
	assert blocks[2] == "Text after the table."


def test_parse_table_content_blocks_supports_multiple_groups_and_multiline_titles() -> None:
	blocks = parse_table_content_blocks(tracer(), [
		"|begin_table|",
		"|title|",
		"Inputs",
		"accepted by the operation",
		"|columns|",
		"Name |tab| Type",
		"|rows|",
		"source |tab| str",
		"|title|",
		"Outputs",
		"|columns|",
		"Name |tab| Type",
		"|rows|",
		"result |tab| bool",
		"|end_table|",
	])

	table = blocks[0]
	assert not isinstance(table, str)
	assert [group.title() for group in table.groups()] == [
		["Inputs", "accepted by the operation"],
		["Outputs"],
	]
	assert table.items() == [
		"Inputs", "accepted by the operation", "Name", "Type", "source", "str",
		"Outputs", "Name", "Type", "result", "bool",
	]


def test_parse_table_content_blocks_preserves_inline_markup_in_title() -> None:
	blocks = parse_table_content_blocks(tracer(), [
		"|begin_table|",
		"|title|",
		"Constants of class |class|`MyClass`",
		"|columns|",
		"Name |tab| Value",
		"|rows|",
		"MAX_ITEMS |tab| 16",
		"|end_table|",
	])

	table = blocks[0]
	assert not isinstance(table, str)
	assert table.groups()[0].title() == ["Constants of class |class|`MyClass`"]


@pytest.mark.parametrize(
	"lines, rule_id, text",
	[
		(["|begin_table|", "|end_table|"], "TBL-003", "at least one group"),
		(["|begin_table|", "|columns|", "A |tab| B", "|end_table|"], "TBL-008", "where |rows| is required"),
		([
			"|begin_table|", "|columns|", "A |tab| B", "|rows|", "one cell", "|end_table|",
		], "TBL-006", "row has 1 cells, expected 2"),
		([
			"|begin_table|", "|columns|", "|begin_table|", "|rows|", "|end_table|",
		], "TBL-008", "expected a header row"),
		([
			"|begin_table|", "|title|", "|begin_table|", "|columns|", "A", "|rows|", "|end_table|",
		], "TBL-008", "expected |columns| after |title|"),
		([
			"|begin_table|", "|title| Inputs", "|columns|", "A", "|rows|", "|end_table|",
		], "TBL-004", "expected |columns|"),
		([
			"|begin_table|", "|columns|", "* Name |tab| Meaning", "|rows|", "item |tab| value", "|end_table|",
		], "TBL-010", "list marker"),
		([
			"|begin_table|", "|columns|", "Name |tab| Meaning", "|rows|", "item |tab| |begin_table|", "|end_table|",
		], "TBL-010", "control token"),
	],
)
def test_parse_table_content_blocks_reports_invalid_structure_with_tbl_rule(
	lines: list[str], rule_id: str, text: str,
) -> None:
	tr = tracer()
	with pytest.raises(ParseError, match=text):
		parse_table_content_blocks(tr, lines)
	assert f"[Rule {rule_id}]" in tr.to_string_errors()


def test_description_exposes_table_through_content_blocks_and_flat_items() -> None:
	doc = """Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| describe the module.
Description:
	Text before the table.
	|begin_table|
	|columns|
	Name |tab| Meaning
	|rows|
	item |tab| A documented item.
	|end_table|
	Text after the table.
"""

	tree = make_docitem_tree(tracer(), doc)
	description = tree.item("Description")
	blocks = description.content_blocks()

	assert len(blocks) == 3
	assert blocks[0] == "Text before the table."
	assert not isinstance(blocks[1], str)
	assert blocks[2] == "Text after the table."
	assert description.items() == [
		"Text before the table.", "Name", "Meaning", "item", "A documented item.", "Text after the table.",
	]


def test_terminology_entry_exposes_table_through_content_blocks() -> None:
	doc = """Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| describe the module.
Terminology:
	Input value:
		|begin_table|
		|columns|
		Name |tab| Meaning
		|rows|
		port |tab| UDP port number.
		|end_table|
"""

	tree = make_docitem_tree(tracer(), doc)
	entry = tree.item("Terminology").item("Input value")
	blocks = entry.content_blocks()

	assert len(blocks) == 1
	assert not isinstance(blocks[0], str)
	assert entry.items() == ["Name", "Meaning", "port", "UDP port number."]


def test_parameters_and_raises_entries_expose_tables_through_content_blocks() -> None:
	"""Structured parameter and exception details preserve their table nodes."""
	doc = """Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Raises, Returns
Contract:
	general:
		|Must| demonstrate structured callable details.
Parameters:
	config:
		|begin_table|
		|columns|
		Key |tab| Meaning
		|rows|
		mode |tab| The requested operating mode.
		|end_table|
Raises:
	ValueError:
		|begin_table|
		|columns|
		Code |tab| Meaning
		|rows|
		1 |tab| The configuration is invalid.
		|end_table|
Returns:
	|None|
"""

	tree = make_docitem_tree(tracer(), doc)
	parameter_blocks = tree.item("Parameters").item("config").content_blocks()
	raises_blocks = tree.item("Raises").item("ValueError").content_blocks()

	assert len(parameter_blocks) == 1
	assert not isinstance(parameter_blocks[0], str)
	assert len(raises_blocks) == 1
	assert not isinstance(raises_blocks[0], str)


def test_factory_entry_exposes_table_through_content_blocks() -> None:
	"""Structured factory configuration details preserve their table nodes."""
	doc = """Preamble:
	profile:
		class
	normative_sections:
		Contract, Factory
Contract:
	general:
		|Must| demonstrate structured factory details.
	constructor:
Factory:
	make_from_config:
		|begin_table|
		|columns|
		Key |tab| Meaning
		|rows|
		path |tab| The source configuration path.
		|end_table|
"""

	tree = make_docitem_tree(tracer(), doc)
	blocks = tree.item("Factory").item("make_from_config").content_blocks()

	assert len(blocks) == 1
	assert not isinstance(blocks[0], str)


def test_overview_entries_expose_tables_through_content_blocks() -> None:
	"""Class, function, and method overview entries preserve their table nodes."""
	module_doc = """Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Public_functions
Contract:
	general:
		|Must| demonstrate structured overview details.
Public_classes:
	Model
Class_overview:
	Model:
		|begin_table|
		|columns|
		Name |tab| Meaning
		|rows|
		fast |tab| The compact model.
		|end_table|
Public_functions:
	build
Function_overview:
	build:
		|begin_table|
		|columns|
		Name |tab| Meaning
		|rows|
		fast |tab| The compact build.
		|end_table|
"""
	class_doc = """Preamble:
	profile:
		class
	normative_sections:
		Contract, Public_methods
Contract:
	general:
		|Must| demonstrate structured overview details.
	constructor:
Public_methods:
	execute
Method_overview:
	execute:
		|begin_table|
		|columns|
		Name |tab| Meaning
		|rows|
		fast |tab| The compact execution mode.
		|end_table|
"""

	module_tree = make_docitem_tree(tracer(), module_doc)
	class_tree = make_docitem_tree(tracer(), class_doc)
	for tree, section, label in [
		(module_tree, "Class_overview", "Model"),
		(module_tree, "Function_overview", "build"),
		(class_tree, "Method_overview", "execute"),
	]:
		blocks = tree.item(section).item(label).content_blocks()
		assert len(blocks) == 1
		assert not isinstance(blocks[0], str)


def test_public_type_and_assignable_entries_expose_tables_through_content_blocks() -> None:
	"""Public type, variable, and constant entries preserve their table nodes."""
	doc = """Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_types, Public_variables, Public_constants
Contract:
	general:
		|Must| demonstrate structured public API details.
Public_types:
	Mode_t:
		|begin_table|
		|columns|
		Value |tab| Meaning
		|rows|
		fast |tab| Optimized processing.
		|end_table|
Public_variables:
	mode:
		|begin_table|
		|columns|
		Value |tab| Meaning
		|rows|
		fast |tab| The active mode.
		|end_table|
Public_constants:
	DEFAULT_MODE:
		|begin_table|
		|columns|
		Value |tab| Meaning
		|rows|
		fast |tab| The default mode.
		|end_table|
"""

	tree = make_docitem_tree(tracer(), doc)
	for section, label in [
		("Public_types", "Mode_t"),
		("Public_variables", "mode"),
		("Public_constants", "DEFAULT_MODE"),
	]:
		blocks = tree.item(section).item(label).content_blocks()
		assert len(blocks) == 1
		assert not isinstance(blocks[0], str)
