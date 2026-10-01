"""Extract canonical Waterloo Authoring JSON from validated docstring ASTs."""

from __future__ import annotations

import inspect
from typing import Any, cast

from sdv.doc.waterloo.docitem_base import (
	docitem_list_of_content_blocks_base,
	docitem_list_of_strings_base,
	docitem_map_base,
	docitem_table,
)
from sdv.doc.waterloo.docitem_docstring import docitem_docstring_base
from sdv.doc.waterloo.docitem_sections import docitem_definitions
from sdv.doc.waterloo.docitem_helper import get_obj_fully_qualified_name
from sdv.doc.waterloo.docitem_types import Profile_t
from sdv.doc.waterloo import waterlint_common as wl_common


_AUTHORING_CATEGORY = "wtrl-authoring-object-json"
_LIST_MARKERS = ("*", "+", "-", "#")


def _table_block(table: docitem_table) -> dict[str, object]:
	groups: list[dict[str, object]] = []
	for group in table.groups():
		columns = [
			{"key": f"column_{index + 1}", "header": header}
			for index, header in enumerate(group.header())
		]
		rows = [
			{"cells": {f"column_{index + 1}": value for index, value in enumerate(row)}}
			for row in group.rows()
		]
		group_json: dict[str, object] = {"columns": columns, "rows": rows}
		title = group.title()
		if title is not None:
			group_json["title"] = list(title)
		groups.append(group_json)
	return {"table": {"groups": groups}}


def _list_block(lines: list[str]) -> dict[str, object]:
	"""Reconstruct one nested Authoring list from Waterloo marker lines."""
	root: list[dict[str, object]] = []
	items_at_depth: list[dict[str, object] | None] = []
	for line in lines:
		marker, text = line[0], line[2:]
		depth = _LIST_MARKERS.index(marker)
		if depth > len(items_at_depth):
			raise RuntimeError(f"List marker '{marker}' skips a nesting level.")
		if depth == 0:
			items = root
		else:
			parent = items_at_depth[depth - 1]
			if parent is None:
				raise RuntimeError(f"List marker '{marker}' has no parent item.")
			child_items = parent.setdefault("items", [])
			assert isinstance(child_items, list)
			items = cast(list[dict[str, object]], child_items)
		item: dict[str, object] = {"text": text}
		items.append(item)
		items_at_depth = items_at_depth[:depth]
		items_at_depth.append(item)
	return {"list": root}


def _freeform_blocks(node: docitem_list_of_content_blocks_base, *, statements: bool) -> list[dict[str, object]]:
	"""Convert text/table blocks; statement contexts retain every logical line."""
	out: list[dict[str, object]] = []
	paragraph_lines: list[str] = []
	list_lines: list[str] = []

	def flush_paragraph() -> None:
		if paragraph_lines:
			out.append({"paragraph": " ".join(paragraph_lines)})
			paragraph_lines.clear()

	def flush_list() -> None:
		if list_lines:
			out.append(_list_block(list_lines))
			list_lines.clear()

	for block in node.content_blocks():
		if isinstance(block, docitem_table):
			flush_paragraph()
			flush_list()
			out.append(_table_block(block))
			continue
		if block == "|":
			flush_paragraph()
			flush_list()
			continue
		if len(block) >= 2 and block[0] in _LIST_MARKERS and block[1] == " " and not statements:
			flush_paragraph()
			list_lines.append(block)
			continue
		flush_list()
		if statements:
			flush_paragraph()
			out.append({"paragraph": block})
		else:
			paragraph_lines.append(block)
	flush_paragraph()
	flush_list()
	return out


def _section_value(label: str, node: object) -> object:
	if label == "Preamble":
		preamble = cast(docitem_map_base, node)
		preamble_json: dict[str, object] = {}
		for key, child in preamble.items().items():
			values = cast(docitem_list_of_strings_base, child).items()
			preamble_json[key] = values[0] if key in {"profile", "status"} else values
		return preamble_json
	if label == "Contract":
		contract = cast(docitem_map_base, node)
		contract_json: dict[str, object] = {}
		for key, child in contract.items().items():
			values = cast(docitem_list_of_strings_base, child).items()
			contract_json[key] = values[0] if key == "base" else values
		return contract_json
	if label == "Definitions":
		definitions = cast(docitem_definitions, node)
		definitions_json: dict[str, object] = {}
		inherited = definitions.inherited()
		if inherited:
			definitions_json["_inherit"] = inherited
		for key, child in definitions.items().items():
			if not isinstance(child, docitem_list_of_content_blocks_base):
				raise RuntimeError(
					f"Authoring JSON cannot represent 'Definitions.{key}' as free-form content."
				)
			definitions_json[key] = _freeform_blocks(child, statements=False)
		return definitions_json
	if isinstance(node, docitem_list_of_content_blocks_base):
		return _freeform_blocks(node, statements=False)
	if isinstance(node, docitem_list_of_strings_base):
		return node.items()
	if isinstance(node, docitem_map_base):
		statements = label in {"Raises", "Factory"}
		map_json: dict[str, object] = {}
		for key, child in node.items().items():
			if not isinstance(child, docitem_list_of_content_blocks_base):
				raise RuntimeError(
				f"Authoring JSON cannot represent '{label}.{key}' as free-form content."
			)
			map_json[key] = _freeform_blocks(child, statements=statements)
		return map_json
	raise RuntimeError(f"Cannot convert AST node '{type(node).__name__}' in section '{label}'.")


def build_authoring_json_from_docstring(obj: object, doc: docitem_docstring_base) -> dict[str, object]:
	"""Build canonical Authoring JSON from one object-validated Waterloo AST."""
	preamble = cast(docitem_map_base, doc.item("Preamble"))
	profile_node = cast(docitem_list_of_strings_base, preamble.item("profile"))
	profile = cast(Profile_t, profile_node.items()[0])
	sections = {label: _section_value(label, node) for label, node in doc.items().items()}
	qualified_name = get_obj_fully_qualified_name(obj)
	out: dict[str, object] = {
		"$schema": f"{wl_common.WTRL_SCHEMA_URI_BASE}/{_AUTHORING_CATEGORY}-{wl_common.WTRL_AUTHORING_OBJECT_JSON_SCHEMA_VERSION}.schema.json",
		"$id": f"urn:waterlint:{_AUTHORING_CATEGORY}:{qualified_name}",
		"__WTRL_CATEGORY__": _AUTHORING_CATEGORY,
		"__WTRL_VERSION__": {"schema": wl_common.WTRL_AUTHORING_OBJECT_JSON_SCHEMA_VERSION},
		"qualified_name": qualified_name,
		"profile": profile,
		"doc": sections,
	}
	if profile in {"function", "method"}:
		out["signature"] = str(inspect.signature(cast(Any, obj)))
	return out
