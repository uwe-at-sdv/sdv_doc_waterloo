#!/usr/bin/env python3
"""Unit tests for the bundled Waterloo MCP about resources."""

from __future__ import annotations

from sdv.doc.waterloo.mcp.wtrl_server import WTRL_TOOL_DOCS
from sdv.doc.waterloo.mcp.wtrl_tools import about


def test_about_is_registered_in_tool_docs() -> None:
	assert "about" in WTRL_TOOL_DOCS, WTRL_TOOL_DOCS
	assert WTRL_TOOL_DOCS["about"] is about, WTRL_TOOL_DOCS


def test_about_index_returns_topics() -> None:
	index = about()
	assert index["topic"] is None, index
	assert index["title"] == "About", index
	assert index["hint"] == "Call about('waterlint.command') next.", index
	topics = index["topics"]
	assert isinstance(topics, list), index
	keys = [entry["key"] for entry in topics if isinstance(entry, dict) and isinstance(entry.get("key"), str)]
	assert keys == ["waterloo.structure", "waterlint.command", "waterloo.markup"], keys


def test_about_markup_returns_flat_content_blocks() -> None:
	markup = about("waterloo.markup")
	assert markup["topic"] == "waterloo.markup", markup
	assert markup["title"] == "Inline markup", markup
	content = markup["content"]
	assert isinstance(content, list), markup
	kinds = [entry["kind"] for entry in content if isinstance(entry, dict) and isinstance(entry.get("kind"), str)]
	assert kinds == [
		"normativity-keywords",
		"normativity-keyword-examples",
		"value-tokens",
		"value-token-examples",
		"roles",
		"role-examples",
		"rules",
	], kinds
