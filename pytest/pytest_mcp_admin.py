#!/usr/bin/env python3
"""Tests for the Waterloo MCP admin helper CLI internals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from contextlib import contextmanager

import sdv.doc.waterloo.mcp.wtrl_mcp_admin as admin_mod

from sdv.doc.waterloo.mcp.wtrl_mcp_admin import (
	ServerEntry,
	_cmd_verify_token,
	_cmd_add_server,
	_cmd_del_server,
	_cmd_list_servers,
	_cmd_list_tokens,
	_build_token_id,
	_format_add_server_message,
	_format_admin_status,
	_format_admin_token_operation_error,
	_format_del_server_message,
	_format_status,
	_format_verify_status,
	_hard_wrap_text,
	_load_registry,
	_normalize_path,
	_parse_json_or_sse,
	_request_json,
	_render_table_report,
	_save_registry,
	_table_report_to_json,
	_write_report,
	TableColumn,
	TableReport,
	_store_server_entry,
)


def test_registry_round_trip_and_upsert(tmp_path: Path) -> None:
	path = tmp_path / "registry.json"
	data = _load_registry(path)
	entry = ServerEntry(
		label="local-waterloo",
		url="http://127.0.0.1:13316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="Local development server",
	)
	_save_registry(path, _store_server_entry(data, entry))
	loaded = _load_registry(path)
	servers = loaded["servers"]
	assert isinstance(servers, list)
	assert len(servers) == 1
	assert servers[0]["label"] == "local-waterloo"
	assert servers[0]["url"] == "http://127.0.0.1:13316"

	updated = ServerEntry(
		label="local-waterloo",
		url="http://127.0.0.1:13317",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="Updated",
	)
	_save_registry(path, _store_server_entry(loaded, updated))
	loaded_again = _load_registry(path)
	servers_again = loaded_again["servers"]
	assert len(servers_again) == 1
	assert servers_again[0]["url"] == "http://127.0.0.1:13317"
	assert servers_again[0]["description"] == "Updated"


def test_registry_load_accepts_current_schema_shape(tmp_path: Path) -> None:
	path = tmp_path / "registry.json"
	path.write_text(
		"""
		{
		  "servers": [
		    {
		      "label": "local-waterloo",
		      "url": "http://127.0.0.1:13316",
		      "mcp_endpoint": "/mcp",
		      "admin_endpoint": "/admin",
		      "description": "Local development server"
		    }
		  ]
		}
		""".strip()
		+ "\n",
		encoding="utf-8",
	)
	data = _load_registry(path)
	servers = data["servers"]
	assert isinstance(servers, list)
	assert len(servers) == 1
	assert servers[0]["label"] == "local-waterloo"


def test_registry_load_rejects_invalid_json_with_context(tmp_path: Path) -> None:
	path = tmp_path / "registry.json"
	path.write_text("{not-json}\n", encoding="utf-8")
	try:
		_load_registry(path)
	except ValueError as exc:
		message = str(exc)
		assert "Validating admin registry file:" in message
		assert "Registry file is not valid JSON" in message
	else:
		raise AssertionError("expected invalid registry JSON to fail")


def test_registry_load_rejects_extra_properties(tmp_path: Path) -> None:
	path = tmp_path / "registry.json"
	path.write_text(
		"""
		{
		  "servers": [
		    {
		      "label": "local-waterloo",
		      "url": "http://127.0.0.1:13316",
		      "mcp_endpoint": "/mcp",
		      "admin_endpoint": "/admin",
		      "description": "Local development server",
		      "extra": "not-allowed"
		    }
		  ]
		}
		""".strip()
		+ "\n",
		encoding="utf-8",
	)
	try:
		_load_registry(path)
	except ValueError as exc:
		message = str(exc)
		assert "Validating admin registry file:" in message
		assert "Registry file is invalid" in message
	else:
		raise AssertionError("expected registry schema validation to fail")


def test_build_token_id_from_parts() -> None:
	args = argparse.Namespace(token_id=None, user="alice", client="vscode", location="tablet")
	assert _build_token_id(args) == "alice-vscode-tablet"

	args = argparse.Namespace(token_id="karl_ernst-any-any", user=None, client=None, location=None)
	assert _build_token_id(args) == "karl_ernst-any-any"


def test_normalize_path() -> None:
	assert _normalize_path("admin", "/admin") == "/admin"
	assert _normalize_path("/admin/", "/admin") == "/admin"


def test_parse_json_or_sse_reports_body_preview() -> None:
	try:
		_parse_json_or_sse("plain text error", url="http://example.invalid/admin/tokens", status=500, content_type="text/plain")
	except RuntimeError as exc:
		message = str(exc)
		assert "status 500" in message
		assert "content-type text/plain" in message
		assert "plain text error" in message
	else:
		raise AssertionError("RuntimeError not raised")


def test_format_status_is_readable() -> None:
	assert _format_status(200) == "ok"
	assert _format_status(401) == "auth-required (401)"
	assert _format_status(403) == "forbidden (403)"
	assert _format_status(404) == "http 404"


def test_format_verify_status_is_more_specific() -> None:
	assert _format_verify_status(200) == "ok"
	assert _format_verify_status(401) == "invalid token (401)"
	assert _format_verify_status(403) == "forbidden (403)"
	assert _format_verify_status(404) == "http 404"


def test_format_admin_status_is_readable() -> None:
	assert _format_admin_status({"auth_enabled": False}) == "auth-disabled"
	assert _format_admin_status({"auth_enabled": True, "valid_tokens": 1, "revoked_tokens": 2}) == "auth-enabled"


def test_format_admin_token_operation_error_is_specific() -> None:
	entry = ServerEntry(
		label="auth-server",
		url="http://127.0.0.1:23316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="",
	)
	assert _format_admin_token_operation_error(entry, "token listing", 404, "/admin/tokens") == (
		"server 'auth-server' does not expose token administration at '/admin/tokens' (404)"
	)
	assert _format_admin_token_operation_error(entry, "token generation", 401, "/admin/tokens").startswith(
		"server 'auth-server' rejected token generation"
	)


def test_ping_admin_uses_ssh_tunnel_for_non_loopback_host(monkeypatch) -> None:
	entry = ServerEntry(
		label="remote-waterloo",
		url="http://gilgamesh:23316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="",
	)
	calls: dict[str, object] = {}

	class _FakeProc:
		def __init__(self) -> None:
			self._alive = True
			self.stderr = SimpleNamespace(read=lambda: "")

		def poll(self) -> int | None:
			return None if self._alive else 0

		def terminate(self) -> None:
			self._alive = False

		def wait(self, timeout: float | None = None) -> int:
			self._alive = False
			return 0

		def kill(self) -> None:
			self._alive = False

	def _fake_popen(cmd: list[str], stdout: object = None, stderr: object = None, text: bool = False) -> _FakeProc:
		calls["ssh_cmd"] = cmd
		return _FakeProc()

	def _fake_request_json(method: str, url: str, payload: dict[str, object] | None = None, extra_headers: dict[str, str] | None = None) -> tuple[int, dict[str, object]]:
		calls["method"] = method
		calls["url"] = url
		return 200, {"auth_enabled": False}

	monkeypatch.setattr(admin_mod.shutil, "which", lambda name: "/usr/bin/ssh")
	monkeypatch.setattr(admin_mod.subprocess, "Popen", _fake_popen)
	monkeypatch.setattr(admin_mod, "_free_local_port", lambda: 45678)
	monkeypatch.setattr(admin_mod, "_wait_for_tcp_port", lambda host, port, timeout: None)
	monkeypatch.setattr(admin_mod, "_request_json", _fake_request_json)

	mode, status = admin_mod._ping_admin(entry)
	assert mode == "ssh"
	assert status == "auth-disabled"
	assert calls["method"] == "GET"
	assert calls["url"] == "http://127.0.0.1:45678/admin"
	assert calls["ssh_cmd"] == [
		"ssh",
		"-o",
		"BatchMode=yes",
		"-o",
		"ExitOnForwardFailure=yes",
		"-N",
		"-L",
		"127.0.0.1:45678:127.0.0.1:23316",
		"gilgamesh",
	]


def test_format_add_and_del_server_messages_are_specific() -> None:
	entry = ServerEntry(
		label="local-waterloo",
		url="http://127.0.0.1:13316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="Local development server",
	)
	assert _format_add_server_message(entry) == "registered server 'local-waterloo' at 127.0.0.1:13316"
	assert _format_del_server_message("local-waterloo") == "removed server 'local-waterloo'"


def test_format_table_has_header_separator() -> None:
	report = TableReport(
		kind="demo",
		columns=(TableColumn("col1", "Col1"), TableColumn("col2", "Col2")),
		rows=[{"col1": "alpha", "col2": "beta"}],
	)
	out = _render_table_report(report)
	lines = out.splitlines()
	assert len(lines) >= 4
	assert lines[1] != lines[2]
	assert "alpha" in out
	assert "beta" in out


def test_format_table_keeps_status_columns_left_aligned() -> None:
	report = TableReport(
		kind="ping",
		columns=(
			TableColumn("label", "Label"),
			TableColumn("host", "Host"),
			TableColumn("admin_access", "Admin access"),
			TableColumn("admin_status", "Admin status"),
			TableColumn("client_status", "Client status"),
		),
		rows=[{"label": "server", "host": "localhost", "admin_access": "direct", "admin_status": "auth-required (401)", "client_status": "ok"}],
	)
	out = _render_table_report(report)
	assert "auth-required (401)" in out
	assert "| ok" in out or "|ok" in out


def test_table_report_to_json_has_stable_shape() -> None:
	report = TableReport(
		kind="servers",
		columns=(TableColumn("label", "Label"), TableColumn("host_port", "Host:Port")),
		rows=[{"label": "local-waterloo", "host_port": "127.0.0.1:13316"}],
	)
	doc = _table_report_to_json(report)
	assert doc["kind"] == "servers"
	assert doc["columns"] == [{"key": "label", "label": "Label"}, {"key": "host_port", "label": "Host:Port"}]
	assert doc["rows"] == [{"label": "local-waterloo", "host_port": "127.0.0.1:13316"}]


def test_write_report_can_emit_json_to_stdout(capsys) -> None:
	report = TableReport(
		kind="demo",
		columns=(TableColumn("label", "Label"),),
		rows=[{"label": "alpha"}],
	)
	_write_report(report, out=None, out_json="-")
	captured = capsys.readouterr()
	doc = json.loads(captured.out)
	assert doc["kind"] == "demo"
	assert doc["rows"] == [{"label": "alpha"}]


def test_write_report_rejects_dual_outputs() -> None:
	report = TableReport(kind="demo", columns=(TableColumn("label", "Label"),), rows=[{"label": "alpha"}])
	try:
		_write_report(report, out="-", out_json="-")
	except ValueError as exc:
		assert "only one of --out or --out-json" in str(exc)
	else:
		raise AssertionError("ValueError not raised")


def test_list_servers_json_mode_keeps_empty_report(monkeypatch, capsys) -> None:
	monkeypatch.setattr(admin_mod, "_load_registry", lambda path: {"servers": []})
	args = argparse.Namespace(registry=None, out=None, out_json="-")
	assert _cmd_list_servers(args) == 0
	doc = json.loads(capsys.readouterr().out)
	assert doc["kind"] == "servers"
	assert doc["rows"] == []


def test_add_server_reports_registration_message(monkeypatch, capsys) -> None:
	saved: dict[str, object] = {}

	def _fake_load_registry(path: Path) -> dict[str, object]:
		return {"servers": []}

	def _fake_save_registry(path: Path, data: dict[str, object]) -> None:
		saved["path"] = path
		saved["data"] = data

	monkeypatch.setattr(admin_mod, "_load_registry", _fake_load_registry)
	monkeypatch.setattr(admin_mod, "_save_registry", _fake_save_registry)
	args = argparse.Namespace(
		registry=None,
		url="http://127.0.0.1:23316",
		host=None,
		port=None,
		label="local-waterloo",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="Local development server",
	)
	assert _cmd_add_server(args) == 0
	assert capsys.readouterr().out.strip() == "registered server 'local-waterloo' at 127.0.0.1:23316"
	assert isinstance(saved.get("data"), dict)


def test_del_server_reports_removal_message(monkeypatch, capsys) -> None:
	monkeypatch.setattr(admin_mod, "_load_registry", lambda path: {"servers": [{"label": "local-waterloo"}]})
	monkeypatch.setattr(admin_mod, "_save_registry", lambda path, data: None)
	args = argparse.Namespace(registry=None, label="local-waterloo")
	assert _cmd_del_server(args) == 0
	assert capsys.readouterr().out.strip() == "removed server 'local-waterloo'"


def test_hard_wrap_text_wraps_at_fixed_width() -> None:
	text = "x" * 32 + "y"
	wrapped = _hard_wrap_text(text)
	assert wrapped == ("x" * 32) + "\n" + "y"


def test_request_json_uses_extra_headers(monkeypatch) -> None:
	captured: dict[str, str | None] = {}

	class _FakeResponse:
		status = 200
		headers = SimpleNamespace(get_content_type=lambda: "application/json")

		def read(self) -> bytes:
			return b'{"ok":true}'

		def __enter__(self) -> "_FakeResponse":
			return self

		def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
			return False

	def _fake_urlopen(req: object, timeout: float = 0.0) -> _FakeResponse:
		captured["authorization"] = req.get_header("Authorization")
		captured["origin"] = req.get_header("Origin")
		captured["accept"] = req.get_header("Accept")
		return _FakeResponse()

	monkeypatch.setattr(admin_mod, "urlopen", _fake_urlopen)
	status, data = _request_json(
		"POST",
		"http://example.invalid/mcp",
		{"jsonrpc": "2.0"},
		{"Authorization": "Bearer abc123"},
	)
	assert status == 200
	assert data == {"ok": True}
	assert captured["authorization"] == "Bearer abc123"
	assert captured["origin"] == admin_mod.DEFAULT_ORIGIN
	assert "application/json" in str(captured["accept"])


def test_verify_token_command_uses_bearer_token(monkeypatch) -> None:
	entry = ServerEntry(
		label="auth-server",
		url="http://127.0.0.1:23316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="",
	)
	calls: dict[str, object] = {}

	def _fake_read_server_entry(data: dict[str, object], label: str) -> ServerEntry:
		assert label == "auth-server"
		return entry

	def _fake_request_json(method: str, url: str, payload: dict[str, object] | None = None, extra_headers: dict[str, str] | None = None) -> tuple[int, dict[str, object]]:
		calls["method"] = method
		calls["url"] = url
		calls["payload"] = payload
		calls["extra_headers"] = extra_headers
		return 200, {"result": "ok"}

	monkeypatch.setattr(admin_mod, "_read_server_entry", _fake_read_server_entry)
	monkeypatch.setattr(admin_mod, "_request_json", _fake_request_json)
	args = argparse.Namespace(server="auth-server", token="BearerToken", registry=None)
	assert _cmd_verify_token(args) == 0
	assert calls["method"] == "POST"
	assert calls["url"] == "http://127.0.0.1:23316/mcp"
	assert isinstance(calls["payload"], dict)
	assert calls["extra_headers"] == {"Authorization": "Bearer BearerToken", "Host": "127.0.0.1:23316"}


def test_verify_token_command_uses_ssh_tunnel_for_non_loopback_host(monkeypatch, capsys) -> None:
	entry = ServerEntry(
		label="remote-waterloo",
		url="http://gilgamesh:23316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="",
	)
	calls: dict[str, object] = {}

	@contextmanager
	def _fake_admin_access(entry: ServerEntry):
		yield admin_mod.AdminAccess(mode="ssh", base_url="http://127.0.0.1:45678")

	def _fake_read_server_entry(data: dict[str, object], label: str) -> ServerEntry:
		assert label == "remote-waterloo"
		return entry

	def _fake_request_json(method: str, url: str, payload: dict[str, object] | None = None, extra_headers: dict[str, str] | None = None) -> tuple[int, dict[str, object]]:
		calls["method"] = method
		calls["url"] = url
		calls["payload"] = payload
		calls["extra_headers"] = extra_headers
		return 200, {"result": "ok"}

	monkeypatch.setattr(admin_mod, "_read_server_entry", _fake_read_server_entry)
	monkeypatch.setattr(admin_mod, "_admin_access", _fake_admin_access)
	monkeypatch.setattr(admin_mod, "_request_json", _fake_request_json)
	args = argparse.Namespace(server="remote-waterloo", token="BearerToken", registry=None)
	assert _cmd_verify_token(args) == 0
	assert calls["method"] == "POST"
	assert calls["url"] == "http://127.0.0.1:45678/mcp"
	assert isinstance(calls["payload"], dict)
	assert calls["extra_headers"] == {"Authorization": "Bearer BearerToken", "Host": "gilgamesh:23316"}
	assert capsys.readouterr().out.strip() == "ok"


def test_verify_token_command_reports_invalid_token_on_401(monkeypatch, capsys) -> None:
	entry = ServerEntry(
		label="auth-server",
		url="http://127.0.0.1:23316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="",
	)

	def _fake_read_server_entry(data: dict[str, object], label: str) -> ServerEntry:
		assert label == "auth-server"
		return entry

	def _fake_request_json(method: str, url: str, payload: dict[str, object] | None = None, extra_headers: dict[str, str] | None = None) -> tuple[int, dict[str, object]]:
		return 401, {"error": "unauthorized"}

	monkeypatch.setattr(admin_mod, "_read_server_entry", _fake_read_server_entry)
	monkeypatch.setattr(admin_mod, "_request_json", _fake_request_json)
	args = argparse.Namespace(server="auth-server", token="BearerToken", registry=None)
	assert _cmd_verify_token(args) == 1
	assert capsys.readouterr().out.strip() == "invalid token (401)"


def test_verify_token_command_reports_unknown_server_cleanly() -> None:
	args = argparse.Namespace(server="missing-server", token="abc", registry=None)
	try:
		_cmd_verify_token(args)
	except ValueError as exc:
		assert str(exc) == "unknown server label: missing-server"
	else:
		raise AssertionError("ValueError not raised")


def test_list_tokens_reports_malformed_token_list(monkeypatch) -> None:
	entry = ServerEntry(
		label="auth-server",
		url="http://127.0.0.1:23316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="",
	)

	def _fake_read_server_entry(data: dict[str, object], label: str) -> ServerEntry:
		assert label == "auth-server"
		return entry

	def _fake_request_json(method: str, url: str, payload: dict[str, object] | None = None, extra_headers: dict[str, str] | None = None) -> tuple[int, dict[str, object]]:
		return 200, {"tokens": "not-a-list"}

	monkeypatch.setattr(admin_mod, "_read_server_entry", _fake_read_server_entry)
	monkeypatch.setattr(admin_mod, "_request_json", _fake_request_json)
	args = argparse.Namespace(server="auth-server", registry=None, out=None, out_json=None)
	try:
		_cmd_list_tokens(args)
	except RuntimeError as exc:
		assert str(exc) == "server 'auth-server' returned a malformed token list"
	else:
		raise AssertionError("RuntimeError not raised")
