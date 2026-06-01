#!/usr/bin/env python3
"""Common helpers for MCP HTTP integration tests."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import cast

import pytest

from pytest_common import PATH_MAIN

MCP_URL = os.environ.get("WTRL_MCP_URL", "http://127.0.0.1:13316/mcp")
MCP_ORIGIN = os.environ.get("WTRL_MCP_ORIGIN", "http://gilgamesh:6274")
MCP_PROTOCOL_VERSION = os.environ.get("WTRL_MCP_PROTOCOL_VERSION", "2025-11-25")
MCP_START_COMMAND = "wtrl_mcp --config etc/wtrl_mcp.http.toml"

PATH_TEMPLATES_JSON_OUT = PATH_MAIN / "templates-json" / "out"


def _encode_payload(payload: dict[str, object]) -> bytes:
	return json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _parse_sse_json(text: str) -> dict[str, object]:
	text = text.strip()
	if not text:
		return {}
	if text.startswith("{"):
		data = json.loads(text)
		if not isinstance(data, dict):
			raise AssertionError(f"expected a JSON object response, got: {type(data).__name__}")
		return cast(dict[str, object], data)
	data_lines: list[str] = []
	for line in text.splitlines():
		if line.startswith("data:"):
			data_lines.append(line.split(":", 1)[1].lstrip())
	if not data_lines:
		raise AssertionError(f"could not find an SSE data payload in response:\n{text}")
	data = json.loads("\n".join(data_lines))
	if not isinstance(data, dict):
		raise AssertionError(f"expected a JSON object response, got: {type(data).__name__}")
	return cast(dict[str, object], data)


def mcp_request(payload: dict[str, object], *, session_id: str | None = None) -> tuple[dict[str, object], dict[str, str]]:
	headers = {
		"Origin": MCP_ORIGIN,
		"Content-Type": "application/json",
		"Accept": "application/json, text/event-stream",
	}
	if session_id is not None:
		headers["Mcp-Session-Id"] = session_id
	req = urllib.request.Request(MCP_URL, data=_encode_payload(payload), headers=headers, method="POST")
	try:
		with urllib.request.urlopen(req, timeout=10) as resp:
			raw = resp.read().decode("utf-8")
			resp_headers = {str(key).lower(): str(value) for key, value in resp.headers.items()}
	except urllib.error.URLError as exc:
		raise MCPUnavailableError(str(exc)) from exc
	return _parse_sse_json(raw), resp_headers


def mcp_initialize() -> tuple[str, dict[str, object]]:
	payload, headers = mcp_request(
		{
			"jsonrpc": "2.0",
			"id": 1,
			"method": "initialize",
			"params": {
				"protocolVersion": MCP_PROTOCOL_VERSION,
				"capabilities": {},
				"clientInfo": {
					"name": "pytest-mcp-http",
					"version": "0.0.0",
				},
			},
		}
	)
	session_id = headers.get("mcp-session-id")
	if not session_id:
		raise AssertionError(f"missing mcp-session-id header in initialize response: {headers}")
	result = payload.get("result")
	if not isinstance(result, dict):
		raise AssertionError(f"initialize response has no result object: {payload}")
	return session_id, result


def mcp_initialize_session() -> str:
	session_id, _ = mcp_initialize()
	mcp_request(
		{
			"jsonrpc": "2.0",
			"method": "notifications/initialized",
			"params": {},
		},
		session_id=session_id,
	)
	return session_id


def mcp_tools_list(session_id: str) -> dict[str, object]:
	payload, _ = mcp_request(
		{
			"jsonrpc": "2.0",
			"id": 2,
			"method": "tools/list",
			"params": {},
		},
		session_id=session_id,
	)
	result = payload.get("result")
	if not isinstance(result, dict):
		raise AssertionError(f"tools/list response has no result object: {payload}")
	return result


def mcp_call_tool_entries(session_id: str, name: str, arguments: dict[str, object]) -> list[dict[str, object]]:
	result = mcp_call_tool(session_id, name, arguments)
	if result.get("isError") is True:
		raise AssertionError(f"tool call failed: {result}")
	structured = result.get("structuredContent")
	if not isinstance(structured, dict):
		raise AssertionError(f"tools/call response missing structuredContent: {result}")
	entries = structured.get("result")
	if not isinstance(entries, list):
		raise AssertionError(f"tools/call structured result is not a list: {structured}")
	out: list[dict[str, object]] = []
	for entry in entries:
		if not isinstance(entry, dict):
			raise AssertionError(f"tools/call result entry is not an object: {entry!r}")
		out.append(cast(dict[str, object], entry))
	return out


def mcp_call_tool(session_id: str, name: str, arguments: dict[str, object]) -> dict[str, object]:
	payload, _ = mcp_request(
		{
			"jsonrpc": "2.0",
			"id": 3,
			"method": "tools/call",
			"params": {
				"name": name,
				"arguments": arguments,
			},
		},
		session_id=session_id,
	)
	result = payload.get("result")
	if not isinstance(result, dict):
		raise AssertionError(f"tools/call response has no result object: {payload}")
	return result


def mcp_list_roots(session_id: str) -> list[dict[str, object]]:
	return mcp_call_tool_entries(session_id, "list_roots", {})


def mcp_or_skip() -> str:
	try:
		return mcp_initialize_session()
	except MCPUnavailableError:
		pytest.skip(f"start the MCP server with: {MCP_START_COMMAND}")


def load_template_json(name: str) -> dict[str, object]:
	path = PATH_TEMPLATES_JSON_OUT / name
	with path.open("r", encoding="utf-8") as fh:
		doc = json.load(fh)
	if not isinstance(doc, dict):
		raise AssertionError(f"template JSON is not an object: {path}")
	return cast(dict[str, object], doc)


def load_template_object(name: str) -> dict[str, object]:
	doc = load_template_json(name)
	objects = doc.get("__WTRL_OBJECTS__")
	if not isinstance(objects, dict):
		raise AssertionError(f"missing __WTRL_OBJECTS__ in {name}")
	if len(objects) != 1:
		raise AssertionError(f"expected exactly one object in {name}, got {list(objects)}")
	obj = next(iter(objects.values()))
	if not isinstance(obj, dict):
		raise AssertionError(f"template object is not an object in {name}")
	return cast(dict[str, object], obj)


class MCPUnavailableError(RuntimeError):
	pass
