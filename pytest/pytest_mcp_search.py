#!/usr/bin/env python3
"""Pytests for MCP search tools against the Waterloo MCP docs."""

from __future__ import annotations

import pytest

from pytest_mcp_common import mcp_list_roots, mcp_call_tool_entries, mcp_or_skip, mcp_call_tool


DOCITEM_HELPER_ROOT_SUFFIX = "/package_gh-pages/doc-json/docitem_helper.wtrl.core.rfc-2119.json"


@pytest.fixture(scope="module")
def mcp_session() -> str:
	return mcp_or_skip()


@pytest.fixture(scope="module")
def mcp_docs_root_id(mcp_session: str) -> str:
	roots = mcp_list_roots(mcp_session)
	for root in roots:
		path = root.get("path")
		if isinstance(path, str) and path.endswith(DOCITEM_HELPER_ROOT_SUFFIX):
			root_id = root.get("root_id")
			if isinstance(root_id, str):
				return root_id
	raise AssertionError(f"could not find MCP docs root in roots: {roots}")


def _entry_qids(entries: list[dict[str, object]]) -> set[str]:
	qids: set[str] = set()
	for entry in entries:
		qid = entry.get("qid")
		if isinstance(qid, str):
			qids.add(qid)
	return qids


def test_mcp_search_sections_public_functions_hits_server_and_tools(
	mcp_session: str,
	mcp_docs_root_id: str,
) -> None:
	entries = mcp_call_tool_entries(
		mcp_session,
		"search_sections",
		{
			"expression": "Public_functions",
			"filter": {
				"root_id": mcp_docs_root_id,
			},
		},
	)
	qids = _entry_qids(entries)
	assert "sdv.doc.waterloo.docitem_helper" in qids, entries
	for entry in entries:
		assert entry.get("section") == "Public_functions", entry
		assert entry.get("match_kind") == "section", entry


def test_mcp_search_sections_public_types_is_docitem_helper_only(
	mcp_session: str,
	mcp_docs_root_id: str,
) -> None:
	entries = mcp_call_tool_entries(
		mcp_session,
		"search_sections",
		{
			"expression": "Public_types",
			"filter": {
				"root_id": mcp_docs_root_id,
			},
		},
	)
	qids = _entry_qids(entries)
	assert {"sdv.doc.waterloo.docitem_helper.DocSession", "sdv.doc.waterloo.docitem_helper.tracer"} <= qids, entries
	assert all(qid.startswith("sdv.doc.waterloo.docitem_helper") for qid in qids), entries
	for entry in entries:
		assert entry.get("section") == "Public_types", entry


@pytest.mark.parametrize(
	"terms,expected_qid,expected_section,expected_subsection,expected_excerpt",
	[
		(["fully qualified object name"], "sdv.doc.waterloo.docitem_helper.get_obj_fully_qualified_name", "Contract", "general", "fully qualified object name"),
		(["direct owner module"], "sdv.doc.waterloo.docitem_helper.get_obj_direct_module", "Contract", "general", "direct owner module"),
		(["best-effort and object-local"], "sdv.doc.waterloo.docitem_helper.get_obj_name", "Notes", "Limitations", "best-effort and object-local"),
	],
)
def test_mcp_search_text_finds_mcp_doc_phrases(
	mcp_session: str,
	mcp_docs_root_id: str,
	terms: list[str],
	expected_qid: str,
	expected_section: str,
	expected_subsection: str,
	expected_excerpt: str,
) -> None:
	entries = mcp_call_tool_entries(
		mcp_session,
		"search_text",
		{
			"terms": terms,
			"filter": {
				"root_id": mcp_docs_root_id,
			},
		},
	)
	assert entries, (terms, entries)
	matching = [
		entry
		for entry in entries
		if entry.get("qid") == expected_qid
		and entry.get("section") == expected_section
		and entry.get("subsection") == expected_subsection
	]
	assert matching, entries
	assert any(expected_excerpt in str(entry.get("excerpt", "")) for entry in matching), matching


def test_mcp_get_section_function_overview_lists_docstring_tools(
	mcp_session: str,
	mcp_docs_root_id: str,
) -> None:
	result = mcp_call_tool(
		mcp_session,
		"get_section",
		{
			"root_id": mcp_docs_root_id,
			"qid": "sdv.doc.waterloo.docitem_helper",
			"section": "Public_functions",
		},
	)
	assert result.get("isError") is False, result
	structured = result.get("structuredContent")
	if not isinstance(structured, dict):
		raise AssertionError(f"missing structuredContent: {result}")
	section = structured.get("section_value")
	if not isinstance(section, list):
		raise AssertionError(f"missing section payload: {structured}")
	assert "get_obj_name" in section, section
	assert "get_obj_path" in section, section
	assert "get_obj_fully_qualified_name" in section, section


def test_mcp_get_subsection_public_functions_entry_point(
	mcp_session: str,
	mcp_docs_root_id: str,
) -> None:
	result = mcp_call_tool(
		mcp_session,
		"get_subsection",
		{
			"root_id": mcp_docs_root_id,
			"qid": "sdv.doc.waterloo.docitem_helper.get_obj_name",
			"section": "Notes",
			"subsection": "Limitations",
		},
	)
	assert result.get("isError") is False, result
	structured = result.get("structuredContent")
	if not isinstance(structured, dict):
		raise AssertionError(f"missing structuredContent: {result}")
	subsection = structured.get("subsection_value")
	if not isinstance(subsection, list):
		raise AssertionError(f"missing subsection payload: {structured}")
	assert any("more precise identifier" in str(item) for item in subsection), subsection
