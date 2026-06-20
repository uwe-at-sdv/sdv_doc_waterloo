#!/usr/bin/env python3
"""Pytests for the remaining Waterloo MCP discovery and lookup tools."""

from __future__ import annotations

import pytest

from pytest_mcp_common import (
	mcp_call_tool,
	mcp_call_tool_entries,
	mcp_call_tool_error_text,
	mcp_get_prompt,
	mcp_list_prompts,
	mcp_or_skip,
)


@pytest.fixture(scope="module")
def mcp_session() -> str:
	return mcp_or_skip()


def _structured_result(result: dict[str, object]) -> dict[str, object]:
	if result.get("isError") is True:
		raise AssertionError(f"tool call failed: {result}")
	structured = result.get("structuredContent")
	if not isinstance(structured, dict):
		raise AssertionError(f"missing structuredContent: {result}")
	return structured


def test_mcp_describe_tool_mentions_search_related(mcp_session: str) -> None:
	result = mcp_call_tool(mcp_session, "describe_tool", {"toolname": "search_related"})
	structured = _structured_result(result)
	help_text = structured.get("result")
	assert isinstance(help_text, str), structured
	assert "search_related" in help_text, help_text
	assert "Signature:" in help_text, help_text
	assert "Waterloo docstring:" in help_text, help_text
	assert "direction" in help_text, help_text


def test_mcp_describe_tool_mentions_list_objects(mcp_session: str) -> None:
	result = mcp_call_tool(mcp_session, "describe_tool", {"toolname": "list_objects"})
	structured = _structured_result(result)
	help_text = structured.get("result")
	assert isinstance(help_text, str), structured
	assert "list_objects" in help_text, help_text
	assert "root_id" in help_text, help_text
	assert "Waterloo docstring:" in help_text, help_text
	assert "ObjectSummary" in help_text, help_text


def test_mcp_describe_tool_mentions_about(mcp_session: str) -> None:
	result = mcp_call_tool(mcp_session, "describe_tool", {"toolname": "about"})
	structured = _structured_result(result)
	help_text = structured.get("result")
	assert isinstance(help_text, str), structured
	assert "about" in help_text, help_text
	assert "topic" in help_text, help_text
	assert "Waterloo docstring:" in help_text, help_text
	assert "bundled package resources" in help_text, help_text


def test_mcp_about_returns_index_topics(mcp_session: str) -> None:
	result = mcp_call_tool(mcp_session, "about", {})
	structured = _structured_result(result)
	assert structured.get("topic") is None, structured
	assert structured.get("title") == "About", structured
	topics = structured.get("topics")
	assert isinstance(topics, list), structured
	keys = {entry.get("key") for entry in topics if isinstance(entry, dict)}
	assert {"waterlint.command", "waterloo.structure", "waterloo.markup"} <= keys, structured
	assert structured.get("hint") == "Call about('waterloo.introduction') next.", structured


def test_mcp_about_returns_markup_topic(mcp_session: str) -> None:
	result = mcp_call_tool(mcp_session, "about", {"topic": "waterloo.markup"})
	structured = _structured_result(result)
	assert structured.get("topic") == "waterloo.markup", structured
	assert structured.get("title") == "Inline markup", structured
	content = structured.get("content")
	assert isinstance(content, list), structured
	kinds = [entry.get("kind") for entry in content if isinstance(entry, dict)]
	assert "role-examples" in kinds, structured
	assert "normativity-keyword-examples" in kinds, structured
	assert "rules" in kinds, structured


def test_mcp_list_prompts_includes_bundled_prompt_defs(mcp_session: str) -> None:
	prompts = mcp_list_prompts(mcp_session)
	names = {prompt.get("name") for prompt in prompts if isinstance(prompt.get("name"), str)}
	assert {"draft_docstring", "inspect_object", "inspect_root"} <= names, prompts


def test_mcp_get_prompt_renders_inspect_root_message(mcp_session: str) -> None:
	result = mcp_get_prompt(mcp_session, "inspect_root", {"root_id": "root:eadb7d51f9fa"})
	assert result.get("description") == "Get a compact structural overview of one Waterloo root before drilling into objects or searches.", result
	messages = result.get("messages")
	assert isinstance(messages, list) and messages, result
	first = messages[0]
	assert isinstance(first, dict), result
	content = first.get("content")
	assert isinstance(content, dict), result
	assert content.get("type") == "text", result
	assert "root:eadb7d51f9fa" in str(content.get("text")), result


def test_mcp_get_signature_returns_wrapper_for_function(mcp_session: str) -> None:
	result = mcp_call_tool(
		mcp_session,
		"get_signature",
		{
			"root_id": "root:eadb7d51f9fa",
			"qid": "sdv.doc.waterloo.mcp.wtrl_server.build_app",
		},
	)
	structured = _structured_result(result)
	assert structured.get("qid") == "sdv.doc.waterloo.mcp.wtrl_server.build_app", structured
	assert structured.get("profile") == "function", structured
	signature = structured.get("signature")
	assert isinstance(signature, dict), structured
	assert signature.get("text") == "build_app(config: 'McpConfig') -> 'FastMCP'", signature
	parameters = signature.get("parameters")
	assert isinstance(parameters, list) and [entry.get("name") for entry in parameters if isinstance(entry, dict)] == ["config"], signature
	assert signature.get("returns") == "FastMCP", signature


def test_mcp_get_root_metadata_returns_header_block(mcp_session: str) -> None:
	result = mcp_call_tool(
		mcp_session,
		"get_root_metadata",
		{
			"root_id": "root:eadb7d51f9fa",
		},
	)
	structured = _structured_result(result)
	assert structured.get("root_id") == "root:eadb7d51f9fa", structured
	assert structured.get("label") == "Waterloo MCP Server and Tool set Reference", structured
	assert isinstance(structured.get("__WTRL_VERSION__"), dict), structured
	assert isinstance(structured.get("__WTRL_META__"), dict), structured
	assert isinstance(structured.get("__WTRL_ROLES__"), dict), structured
	assert isinstance(structured.get("__WTRL_SCOPES__"), dict), structured
	assert "document" not in structured, structured


def test_mcp_list_objects_reports_inventory_rows(mcp_session: str) -> None:
	entries = mcp_call_tool_entries(
		mcp_session,
		"list_objects",
		{
			"root_id": "root:352f5dfbee7c",
		},
	)
	assert entries, entries
	row = next(entry for entry in entries if entry.get("qid") == "tde4.get3DEVersion")
	assert row.get("profile") == "function", row
	assert row.get("kind") == "callable", row
	assert row.get("scope") == "public", row
	assert row.get("status") is None, row
	assert row.get("has_doc") is True, row
	assert row.get("has_examples") is True, row
	assert row.get("has_see_also") is True, row


def test_mcp_get_references_and_search_related_agree_on_tde4_widget_callback_function(
	mcp_session: str,
) -> None:
	references = mcp_call_tool_entries(
		mcp_session,
		"get_references",
		{
			"root_id": "root:352f5dfbee7c",
			"qid": "tde4.setWidgetCallbackFunction",
		},
	)
	reference_qids = {entry.get("source_qid") for entry in references if isinstance(entry.get("source_qid"), str)}
	assert "tde4.addButtonWidget" in reference_qids, references
	assert "tde4.getWidgetCallbackFunction" in reference_qids, references
	assert "tde4.setWidgetShortcut" in reference_qids, references

	related = mcp_call_tool_entries(
		mcp_session,
		"search_related",
		{
			"root_id": "root:352f5dfbee7c",
			"qid": "tde4.setWidgetCallbackFunction",
		},
	)
	related_qids = {entry.get("related_qid") for entry in related if isinstance(entry.get("related_qid"), str)}
	assert "tde4.addButtonWidget" in related_qids, related
	assert "tde4.getWidgetCallbackFunction" in related_qids, related
	assert "tde4.setWidgetShortcut" in related_qids, related
	directions = {entry.get("direction") for entry in related if isinstance(entry.get("direction"), str)}
	assert directions <= {"in", "out", "in_out"}, related


def test_mcp_get_references_unknown_qid_returns_empty_list(mcp_session: str) -> None:
	entries = mcp_call_tool_entries(
		mcp_session,
		"get_references",
		{
			"root_id": "root:eadb7d51f9fa",
			"qid": "does.not.exist",
		},
	)
	assert entries == [], entries


def test_mcp_search_related_unknown_qid_reports_unknown_qid(mcp_session: str) -> None:
	text = mcp_call_tool_error_text(
		mcp_session,
		"search_related",
		{
			"root_id": "root:eadb7d51f9fa",
			"qid": "does.not.exist",
		},
	)
	assert "Unknown qid: does.not.exist" in text, text


def test_mcp_get_examples_and_source_roundtrip_for_tde4_version(mcp_session: str) -> None:
	examples = mcp_call_tool_entries(
		mcp_session,
		"get_examples",
		{
			"root_id": "root:352f5dfbee7c",
			"qid": "tde4.get3DEVersion",
		},
	)
	assert examples, examples
	first = examples[0]
	example_path = first.get("example_path")
	assert isinstance(example_path, str), first
	assert example_path.startswith("/__WTRL_EXAMPLES__/sha256_"), example_path
	assert first.get("lang") == "python", first
	assert isinstance(first.get("size"), int) and first.get("size") > 0, first

	result = mcp_call_tool(
		mcp_session,
		"get_example_source",
		{
			"root_id": "root:352f5dfbee7c",
			"example_path": example_path,
		},
	)
	structured = _structured_result(result)
	source = structured.get("result")
	assert isinstance(source, str), structured
	assert "get3DEVersion" in source, source


def test_mcp_get_signature_module_returns_no_signature_block(mcp_session: str) -> None:
	result = mcp_call_tool(
		mcp_session,
		"get_signature",
		{
			"root_id": "root:eadb7d51f9fa",
			"qid": "sdv.doc.waterloo.mcp.wtrl_tools",
		},
	)
	structured = _structured_result(result)
	assert structured.get("profile") == "module", structured
	assert structured.get("signature") is None, structured


def test_mcp_get_signature_unknown_qid_reports_mcps_002(mcp_session: str) -> None:
	text = mcp_call_tool_error_text(
		mcp_session,
		"get_signature",
		{
			"root_id": "root:eadb7d51f9fa",
			"qid": "does.not.exist",
		},
	)
	assert "Unknown qid: does.not.exist" in text, text


def test_mcp_get_examples_unknown_qid_reports_mcps_002(mcp_session: str) -> None:
	text = mcp_call_tool_error_text(
		mcp_session,
		"get_examples",
		{
			"root_id": "root:eadb7d51f9fa",
			"qid": "does.not.exist",
		},
	)
	assert "Unknown qid: does.not.exist" in text, text


def test_mcp_get_example_source_unknown_example_reports_mcps_006(mcp_session: str) -> None:
	text = mcp_call_tool_error_text(
		mcp_session,
		"get_example_source",
		{
			"root_id": "root:352f5dfbee7c",
			"example_path": "/__WTRL_EXAMPLES__/sha256_does_not_exist",
		},
	)
	assert "MCPS-006 unknown example reference" in text, text


def test_mcp_describe_tool_unknown_tool_reports_mcps_007(mcp_session: str) -> None:
	text = mcp_call_tool_error_text(
		mcp_session,
		"describe_tool",
		{
			"toolname": "does_not_exist",
		},
	)
	assert "MCPS-007 unknown tool" in text, text
