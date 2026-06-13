#!/usr/bin/env python3
"""Pytests for the Waterloo MCP HTTP transport."""

from __future__ import annotations

import pytest

from pytest_mcp_common import (
	load_template_object,
	mcp_call_tool,
	mcp_or_skip,
	mcp_tools_list,
)


def _tool_names(result: dict[str, object]) -> set[str]:
	tools = result.get("tools")
	if not isinstance(tools, list):
		raise AssertionError(f"tools/list response missing tools array: {result}")
	names: set[str] = set()
	for tool in tools:
		if isinstance(tool, dict):
			name = tool.get("name")
			if isinstance(name, str):
				names.add(name)
	return names


def _extract_json_snippet(result: dict[str, object]) -> dict[str, object]:
	structured = result.get("structuredContent")
	if not isinstance(structured, dict):
		raise AssertionError(f"tools/call response missing structuredContent: {result}")
	snippet = structured.get("json_snippet")
	if not isinstance(snippet, dict):
		raise AssertionError(f"gen_docstring response missing json_snippet: {structured}")
	return snippet


def _extract_generated_docgen(result: dict[str, object]) -> dict[str, object]:
	snippet = _extract_json_snippet(result)
	objects = snippet.get("__WTRL_OBJECTS__")
	if not isinstance(objects, dict):
		raise AssertionError(f"gen_docstring response missing __WTRL_OBJECTS__: {snippet}")
	entry = objects.get("generated_docstring_template")
	if not isinstance(entry, dict):
		raise AssertionError(f"gen_docstring response missing generated_docstring_template: {objects}")
	return entry


@pytest.fixture(scope="module")
def mcp_session() -> str:
	return mcp_or_skip()


def test_mcp_http_tools_list_includes_docstring_tools(mcp_session: str) -> None:
	result = mcp_tools_list(mcp_session)
	names = _tool_names(result)
	assert "about" in names, names
	assert "list_roots" in names, names
	assert "gen_docstring" in names, names
	assert "search_text" in names, names


def test_mcp_http_gen_docstring_doc_only_matches_templates_json_function(mcp_session: str) -> None:
	result = mcp_call_tool(
		mcp_session,
		"gen_docstring",
		{
			"profile": "function",
			"signature": "def f(a: int) -> int",
			"mode": "full",
			"indent_mode": "tab",
			"json_mode": "doc_only",
		},
	)
	assert result.get("isError") is False, result
	entry = _extract_json_snippet(result)
	expected = load_template_object("full_docstring_templates.f.json")["doc"]
	assert entry == expected, entry


def test_mcp_http_gen_docstring_full_matches_templates_json_function(mcp_session: str) -> None:
	result = mcp_call_tool(
		mcp_session,
		"gen_docstring",
		{
			"profile": "function",
			"signature": "def f(a: int) -> int",
			"mode": "full",
			"indent_mode": "tab",
			"json_mode": "full",
		},
	)
	assert result.get("isError") is False, result
	entry = _extract_generated_docgen(result)
	expected = load_template_object("full_docstring_templates.f.json")
	assert entry == expected, entry


@pytest.mark.parametrize(
	"profile,signature,mode,indent_mode,json_mode,expected_doc_name",
	[
		("class", "class X", "minimal", "tab", "doc_only", "minimal_docstring_templates.X.json"),
		("class", "class X", "full", "spc4", "full", "full_docstring_templates.X.json"),
		("method", "def m(self, a: int) -> int", "minimal", "spc4", "doc_only", "minimal_docstring_templates.X.m.json"),
		("method", "def m(self, a: int) -> int", "full", "tab", "full", "full_docstring_templates.X.m.json"),
	],
)
def test_mcp_http_gen_docstring_matrix_matches_templates_json(
	mcp_session: str,
	profile: str,
	signature: str,
	mode: str,
	indent_mode: str,
	json_mode: str,
	expected_doc_name: str,
) -> None:
	result = mcp_call_tool(
		mcp_session,
		"gen_docstring",
		{
			"profile": profile,
			"signature": signature,
			"mode": mode,
			"indent_mode": indent_mode,
			"json_mode": json_mode,
		},
	)
	assert result.get("isError") is False, result
	structured = result.get("structuredContent")
	if not isinstance(structured, dict):
		raise AssertionError(f"missing structuredContent: {result}")
	docstring = structured.get("docstring")
	if not isinstance(docstring, str):
		raise AssertionError(f"missing docstring: {structured}")
	if indent_mode == "spc4":
		assert "\t" not in docstring, docstring
		assert "    " in docstring, docstring
	else:
		assert "\t" in docstring or "Preamble:" in docstring, docstring
	snippet = _extract_json_snippet(result)
	if json_mode == "doc_only":
		expected = load_template_object(expected_doc_name)["doc"]
		assert snippet == expected, snippet
	else:
		entry = _extract_generated_docgen(result)
		expected = load_template_object(expected_doc_name)
		if profile == "class":
			assert entry == expected, entry
		else:
			assert entry["doc"] == expected["doc"], entry
			signature = entry.get("signature")
			if not isinstance(signature, dict):
				raise AssertionError(f"missing signature block: {entry}")
			assert signature.get("text") == "m(self, a: int) -> int", signature
			parameters = signature.get("parameters")
			assert isinstance(parameters, list) and [p.get("name") for p in parameters if isinstance(p, dict)] == ["a"], signature
			assert signature.get("returns") == "int", signature
