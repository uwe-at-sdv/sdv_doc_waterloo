#!/usr/bin/env python3
"""Live smoke tests for the MCP admin token helpers against a running server."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Iterator

import pytest


AUTH_BASE_URL = os.environ.get("WTRL_MCP_ADMIN_URL", "http://127.0.0.1:7999/admin")
NOAUTH_MCP_URL = os.environ.get("WTRL_MCP_NOAUTH_MCP_URL", "http://127.0.0.1:7998/mcp")
TOKEN_ID = os.environ.get("WTRL_MCP_TEST_TOKEN_ID", "uwe-codex-gilgamesh")


def _admin_request(path: str) -> dict[str, object]:
	req = urllib.request.Request(f"{AUTH_BASE_URL}{path}", method="GET")
	try:
		with urllib.request.urlopen(req, timeout=5) as resp:
			raw = resp.read().decode("utf-8")
	except urllib.error.URLError as exc:
		raise MCPAdminUnavailableError(str(exc)) from exc
	data = json.loads(raw)
	if not isinstance(data, dict):
		raise AssertionError(f"expected JSON object response, got: {type(data).__name__}")
	return data


def _admin_json_request(method: str, path: str, payload: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
	req = urllib.request.Request(
		f"{AUTH_BASE_URL}{path}",
		method=method,
		headers={"Content-Type": "application/json"},
	)
	data = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
	try:
		with urllib.request.urlopen(req, data=data, timeout=5) as resp:
			raw = resp.read().decode("utf-8")
			status = resp.status
	except urllib.error.HTTPError as exc:
		raw = exc.read().decode("utf-8")
		status = exc.code
	except urllib.error.URLError as exc:
		raise MCPAdminUnavailableError(str(exc)) from exc
	if raw:
		obj = json.loads(raw)
		if not isinstance(obj, dict):
			raise AssertionError(f"expected JSON object response, got: {type(obj).__name__}")
	else:
		obj = {}
	return status, obj


def _wait_for_noauth_server() -> None:
	deadline = time.monotonic() + 20
	last_error: Exception | None = None
	while time.monotonic() < deadline:
		try:
			req = urllib.request.Request(NOAUTH_MCP_URL, method="POST")
			req.add_header("Origin", "http://gilgamesh:6274")
			req.add_header("Content-Type", "application/json")
			req.add_header("Accept", "application/json, text/event-stream")
			data = json.dumps(
				{
					"jsonrpc": "2.0",
					"id": 1,
					"method": "initialize",
					"params": {
						"protocolVersion": "2025-11-25",
						"capabilities": {},
						"clientInfo": {"name": "pytest-live", "version": "0.0.0"},
					},
				},
				separators=(",", ":"),
			).encode("utf-8")
			with urllib.request.urlopen(req, data=data, timeout=5) as resp:
				if resp.status != 200:
					raise AssertionError(resp.status)
				if not resp.headers.get("mcp-session-id"):
					raise AssertionError("missing mcp-session-id header")
			return
		except Exception as exc:  # pragma: no cover - retry loop
			last_error = exc
			time.sleep(0.2)
	raise AssertionError(f"noauth MCP server did not become ready: {last_error}")


@pytest.fixture(scope="module", autouse=True)
def _started_servers() -> Iterator[None]:
	if os.environ.get("WTRL_MCP_LAUNCHED") != "1":
		pytest.skip(
			f"start the MCP servers with: bash package_main/pytest/run.sh "
			f"pytest_mcp_auth_live.py -q"
		)
	time.sleep(2)
	_wait_for_noauth_server()
	try:
		_admin_request("/tokens")
	except MCPAdminUnavailableError as exc:
		pytest.skip(
			"start the auth MCP server with: "
			"wtrl_mcp --config package_main/pytest/etc/wtrl_mcp.auth.http.toml "
			f"(or set WTRL_MCP_ADMIN_URL); auth endpoint unavailable: {exc}"
		)
	yield


def _admin_or_fail() -> None:
	try:
		_admin_request("/tokens")
	except MCPAdminUnavailableError:
		raise AssertionError(
			"the auth MCP server should have been started by the module fixture"
		)


def _find_token(tokens: list[dict[str, object]], token_id: str) -> dict[str, object] | None:
	for entry in tokens:
		if entry.get("token_id") == token_id:
			return entry
	return None


def _ensure_absent() -> None:
	while True:
		listed = _admin_request("/tokens")
		tokens = listed.get("tokens")
		if not isinstance(tokens, list):
			raise AssertionError(listed)
		entries = [item for item in tokens if isinstance(item, dict) and item.get("token_id") == TOKEN_ID]
		active_entries = [entry for entry in entries if entry.get("revoked_at") in (None, "")]
		if not active_entries:
			return
		status, _ = _admin_json_request("DELETE", f"/tokens/{TOKEN_ID}")
		assert status == 204, status


def test_live_admin_api_create_and_revoke_token() -> None:
	_admin_or_fail()
	# Bring the store into a known state without failing if the token does not exist yet.
	_ensure_absent()

	status, created = _admin_json_request("POST", "/tokens", {"token_id": TOKEN_ID})
	assert status == 201, created
	assert created.get("token_id") == TOKEN_ID, created
	assert isinstance(created.get("token"), str) and created["token"]

	listed = _admin_request("/tokens")
	tokens = listed.get("tokens")
	assert isinstance(tokens, list), listed
	matching_entries = [entry for entry in tokens if isinstance(entry, dict) and entry.get("token_id") == TOKEN_ID]
	token_entry = next((entry for entry in matching_entries if entry.get("revoked_at") in (None, "")), None)
	assert token_entry is not None, listed
	assert token_entry.get("token_id") == TOKEN_ID, token_entry
	assert token_entry.get("revoked_at") in (None, "")

	status, _ = _admin_json_request("DELETE", f"/tokens/{TOKEN_ID}")
	assert status == 204, status

	listed_after = _admin_request("/tokens")
	tokens_after = listed_after.get("tokens")
	assert isinstance(tokens_after, list), listed_after
	token_entry_after = _find_token([entry for entry in tokens_after if isinstance(entry, dict)], TOKEN_ID)
	assert token_entry_after is not None, listed_after
	assert token_entry_after.get("token_id") == TOKEN_ID, token_entry_after
	assert isinstance(token_entry_after.get("revoked_at"), str) and token_entry_after["revoked_at"]


def test_live_noauth_server_accepts_initialize() -> None:
	req = urllib.request.Request(NOAUTH_MCP_URL, method="POST")
	req.add_header("Origin", "http://gilgamesh:6274")
	req.add_header("Content-Type", "application/json")
	req.add_header("Accept", "application/json, text/event-stream")
	data = json.dumps(
		{
			"jsonrpc": "2.0",
			"id": 1,
			"method": "initialize",
			"params": {
				"protocolVersion": "2025-11-25",
				"capabilities": {},
				"clientInfo": {"name": "pytest-live", "version": "0.0.0"},
			},
		},
		separators=(",", ":"),
	).encode("utf-8")
	with urllib.request.urlopen(req, data=data, timeout=5) as resp:
		assert resp.status == 200
		assert resp.headers.get("mcp-session-id")


class MCPAdminUnavailableError(RuntimeError):
	pass
