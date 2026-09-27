"""Table-block parsing and table-capable docitem base classes."""

from __future__ import annotations

from typing import Final, Sequence, cast

from sdv.doc.waterloo.docitem_base import (
	DocstringContentBlock,
	docitem_list_of_content_blocks_base,
	docitem_table,
	docitem_table_group,
)
from sdv.doc.waterloo.docitem_helper import raise_parsing_error
from sdv.doc.waterloo.docitem_tracer import tracer
from sdv.doc.waterloo.docitem_types import DocstringSubtree


BEGIN_TABLE: Final[str] = "|begin_table|"
COLUMNS: Final[str] = "|columns|"
END_TABLE: Final[str] = "|end_table|"
ROWS: Final[str] = "|rows|"
TAB: Final[str] = "|tab|"
TITLE: Final[str] = "|title|"
CONTROL_TOKENS: Final[frozenset[str]] = frozenset({BEGIN_TABLE, COLUMNS, END_TABLE, ROWS, TITLE})
LIST_MARKER_PREFIXES: Final[tuple[str, ...]] = ("* ", "+ ", "- ", "# ")


# See definition of Control line
def _is_control_line(line: str, token: str) -> bool:
	return line.strip() == token

# See TBL-007 and preceeding definitions.
def _validate_cell(tr: tracer, cell: str) -> None:
	"""Reject textflow tokens that would make a table cell structurally ambiguous."""
	if cell == "|":
		raise_parsing_error(tr, "TBL-010", "table cell must not contain the paragraph token '|'")
	if cell.startswith(LIST_MARKER_PREFIXES):
		raise_parsing_error(tr, "TBL-010", f"table cell must not start with list marker {cell[:1]!r}")
	if cell in CONTROL_TOKENS:
		raise_parsing_error(tr, "TBL-010", f"table cell must not contain control token {cell!r}")


def _split_cells(tr: tracer, line: str) -> list[str]:
	"""Split one physical table row while retaining deliberately empty cells."""
	cells = [cell.strip() for cell in line.split(TAB)]
	for cell in cells:
		_validate_cell(tr, cell)
	return cells

# Waterloo's tokenizer already skips blank lines, but we leave check and skip
# here as well since the API-function parse_table_content_blocks() is public
# and may be applied to manually created docstrings.
def _next_nonblank(lines: Sequence[str], pos: int) -> int:
	while pos < len(lines) and not lines[pos].strip():
		pos += 1
	return pos


def _expect_row(tr: tracer, lines: Sequence[str], pos: int, what: str) -> tuple[list[str], int]:
	pos = _next_nonblank(lines, pos)
	if pos >= len(lines):
		raise_parsing_error(tr, "TBL-004", f"expected {what}, found end of table")
	line = lines[pos]
	if _is_control_line(line, BEGIN_TABLE) or _is_control_line(line, COLUMNS) or _is_control_line(line, ROWS) or _is_control_line(line, END_TABLE) or _is_control_line(line, TITLE):
		raise_parsing_error(tr, "TBL-008", f"expected {what}, got control line '{line.strip()}'")
	return _split_cells(tr, line), pos + 1


def _parse_table(tr: tracer, lines: Sequence[str], start: int) -> tuple[docitem_table, int]:
	"""Parse a table beginning immediately after its ``|begin_table|`` line."""
	groups: list[docitem_table_group] = []
	column_count: int | None = None
	pos = start

	while True:
		pos = _next_nonblank(lines, pos)
		if pos >= len(lines):
			raise_parsing_error(tr, "TBL-002", f"missing closing {END_TABLE}")
		if _is_control_line(lines[pos], END_TABLE):
			if not groups:
				raise_parsing_error(tr, "TBL-003", f"a table must contain at least one group (premature occurrence of {END_TABLE})")
			table = docitem_table()
			table.set_groups(groups)
			return table, pos + 1

		title: list[str] | None = None
		if _is_control_line(lines[pos], TITLE):
			title = []
			pos += 1
			while True:
				pos = _next_nonblank(lines, pos)
				if pos >= len(lines):
					raise_parsing_error(tr, "TBL-004", f"missing {COLUMNS} after {TITLE}")
				if _is_control_line(lines[pos], COLUMNS):
					break
				if _is_control_line(lines[pos], BEGIN_TABLE) or _is_control_line(lines[pos], END_TABLE) or _is_control_line(lines[pos], ROWS) or _is_control_line(lines[pos], TITLE):
					raise_parsing_error(tr, "TBL-008", f"expected {COLUMNS} after {TITLE}, got '{lines[pos].strip()}'")
				title.append(lines[pos])
				pos += 1

		if not _is_control_line(lines[pos], COLUMNS):
			if _is_control_line(lines[pos], BEGIN_TABLE) or _is_control_line(lines[pos], END_TABLE) or _is_control_line(lines[pos], ROWS) or _is_control_line(lines[pos], TITLE):
				raise_parsing_error(tr, "TBL-008", f"unexpected control line '{lines[pos].strip()}' where {COLUMNS} is required")
			raise_parsing_error(tr, "TBL-004", f"expected {COLUMNS}, got '{lines[pos].strip()}'")
		header, pos = _expect_row(tr, lines, pos + 1, "a header row after |columns|")
		if column_count is None:
			column_count = len(header)
		elif len(header) != column_count:
			raise_parsing_error(
				tr,
				"TBL-006",
				f"header has {len(header)} cells, expected {column_count} cells established by the first group"
			)

		pos = _next_nonblank(lines, pos)
		if pos >= len(lines):
			raise_parsing_error(tr, "TBL-004", f"expected {ROWS} after the header row, got end of table")
		if not _is_control_line(lines[pos], ROWS):
			if _is_control_line(lines[pos], BEGIN_TABLE) or _is_control_line(lines[pos], COLUMNS) or _is_control_line(lines[pos], END_TABLE) or _is_control_line(lines[pos], TITLE):
				raise_parsing_error(tr, "TBL-008", f"unexpected control line '{lines[pos].strip()}' where {ROWS} is required")
			raise_parsing_error(tr, "TBL-004", f"expected {ROWS} after the header row, got {lines[pos].strip()!r}")
		pos += 1

		rows: list[list[str]] = []
		while True:
			pos = _next_nonblank(lines, pos)
			if pos >= len(lines) or _is_control_line(lines[pos], END_TABLE) or _is_control_line(lines[pos], TITLE):
				break
			if _is_control_line(lines[pos], BEGIN_TABLE) or _is_control_line(lines[pos], COLUMNS) or _is_control_line(lines[pos], ROWS):
				raise_parsing_error(tr, "TBL-008", f"unexpected control line '{lines[pos].strip()}' in table rows")
			row = _split_cells(tr, lines[pos])
			if len(row) != column_count:
				raise_parsing_error(tr, "TBL-006", f"row has {len(row)} cells, expected {column_count}")
			rows.append(row)
			pos += 1

		group = docitem_table_group()
		group.set_title(title)
		group.set_header(header)
		group.set_rows(rows)
		groups.append(group)


def parse_table_content_blocks(tr: tracer, lines: DocstringSubtree) -> list[DocstringContentBlock]:
	"""Convert a free-text subtree into text blocks and validated table nodes."""
	if not isinstance(lines, list) or not all(isinstance(line, str) for line in lines):
		raise_parsing_error(tr, tr.get_rule_on_fail(), "expected list of strings")
	raw_lines = cast(list[str], lines)

	blocks: list[DocstringContentBlock] = []
	pos = 0
	while pos < len(raw_lines):
		line = raw_lines[pos]
		if _is_control_line(line, BEGIN_TABLE):
			table, pos = _parse_table(tr, raw_lines, pos + 1)
			blocks.append(table)
			continue
		if _is_control_line(line, END_TABLE):
			raise_parsing_error(tr, "TBL-002", f"unexpected {END_TABLE}")
		blocks.append(line)
		pos += 1
	return blocks


class docitem_table_content_entry_base(docitem_list_of_content_blocks_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from
Contract:
	general:
		|Must| parse free-form entries that permit Waterloo table blocks.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_of_content_blocks_base
"""
	def parse(self, tr: tracer, lines: DocstringSubtree) -> None:
		self.set_content_blocks(parse_table_content_blocks(tr, lines))
