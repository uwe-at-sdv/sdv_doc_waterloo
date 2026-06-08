#!/usr/bin/env python3
"""Pytests for MCP search tools against the Waterloo MCP docs."""

from __future__ import annotations

import pytest

from pytest_mcp_common import mcp_list_roots, mcp_call_tool_entries, mcp_or_skip, mcp_call_tool


@pytest.fixture(scope="module")
def mcp_session() -> str:
	return mcp_or_skip()


@pytest.fixture(scope="module")
def mcp_docs_root_id(mcp_session: str) -> str:
	roots = mcp_list_roots(mcp_session)
	for root in roots:
		path = root.get("path")
		if isinstance(path, str) and path.endswith("/mcp_roots/wtrl_mcp.wtrl.core.rfc-2119.json"):
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
	assert "sdv.doc.waterloo.mcp.wtrl_server" in qids, entries
	assert "sdv.doc.waterloo.mcp.wtrl_tools" in qids, entries
	for entry in entries:
		assert entry.get("section") == "Public_functions", entry
		assert entry.get("match_kind") == "section", entry


def test_mcp_search_sections_public_types_is_tools_only(
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
	assert qids == {"sdv.doc.waterloo.mcp.wtrl_tools"}, entries
	for entry in entries:
		assert entry.get("section") == "Public_types", entry


@pytest.mark.parametrize(
	"terms,expected_qid,expected_section,expected_subsection,expected_excerpt",
	[
		(["entry point"], "sdv.doc.waterloo.mcp.wtrl_server", "Contract", "general", "entry point"),
		(["tool set"], "sdv.doc.waterloo.mcp.wtrl_tools", "Contract", "general", "tool set"),
		(["compact excerpts"], "sdv.doc.waterloo.mcp.wtrl_tools", "Function_overview", "search_text", "compact excerpts"),
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
			"qid": "sdv.doc.waterloo.mcp.wtrl_tools",
			"section": "Function_overview",
		},
	)
	assert result.get("isError") is False, result
	structured = result.get("structuredContent")
	if not isinstance(structured, dict):
		raise AssertionError(f"missing structuredContent: {result}")
	section = structured.get("section_value")
	if not isinstance(section, dict):
		raise AssertionError(f"missing section payload: {structured}")
	assert "gen_docstring" in section, section
	assert "search_text" in section, section
	assert "get_section" in section, section


def test_mcp_get_subsection_public_functions_entry_point(
	mcp_session: str,
	mcp_docs_root_id: str,
) -> None:
	result = mcp_call_tool(
		mcp_session,
		"get_subsection",
		{
			"root_id": mcp_docs_root_id,
			"qid": "sdv.doc.waterloo.mcp.wtrl_server",
			"section": "Contract",
			"subsection": "general",
		},
	)
	assert result.get("isError") is False, result
	structured = result.get("structuredContent")
	if not isinstance(structured, dict):
		raise AssertionError(f"missing structuredContent: {result}")
	subsection = structured.get("subsection_value")
	if not isinstance(subsection, list):
		raise AssertionError(f"missing subsection payload: {structured}")
	assert any("entry point for the Waterloo MCP server" in str(item) for item in subsection), subsection
