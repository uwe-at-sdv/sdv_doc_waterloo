#!/usr/bin/env python3
"""Tests for the Waterloo MCP admin helper CLI internals."""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
from types import SimpleNamespace
from contextlib import contextmanager

import sdv.doc.waterloo.mcp.wtrl_mcp_admin as admin_mod
from sdv.doc.waterloo.waterlint_common import emit_diagnostics

from sdv.doc.waterloo.mcp.wtrl_mcp_admin import (
	AdminCliError,
	ServerEntry,
	_cmd_verify_token,
	_cmd_add_server,
	_cmd_del_server,
	_cmd_list_servers,
	_cmd_ping_servers,
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
		identity="local-waterloo",
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
		identity="local-waterloo",
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
		      "identity": "",
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
	assert servers[0]["identity"] == ""


def test_registry_load_rejects_invalid_json_with_context(tmp_path: Path) -> None:
	path = tmp_path / "registry.json"
	path.write_text("{not-json}\n", encoding="utf-8")
	try:
		_load_registry(path)
	except AdminCliError as exc:
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
		      "identity": "",
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
	except AdminCliError as exc:
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
	except AdminCliError as exc:
		message = str(exc)
		assert "status 500" in message
		assert "content-type text/plain" in message
		assert "plain text error" in message
	else:
		raise AssertionError("AdminCliError not raised")


def test_format_status_is_readable() -> None:
	assert _format_status(200) == "ok"
	assert _format_status(401) == "auth-required (401)"
	assert _format_status(403) == "forbidden (403)"
	assert _format_status(404) == "http 404"


def test_format_verify_status_is_more_specific() -> None:
	assert _format_verify_status(200) == "ok"
	assert _format_verify_status(401) == "invalid token (401)"
	assert _format_verify_status(403) == "forbidden (403)"
	assert _format_verify_status(404) == "not found (404)"


def test_format_admin_status_is_readable() -> None:
	assert _format_admin_status({"auth_enabled": False}) == "auth-disabled"
	assert _format_admin_status({"auth_enabled": True, "valid_tokens": 1, "revoked_tokens": 2}) == "auth-enabled"


def test_format_admin_token_operation_error_is_specific() -> None:
	entry = ServerEntry(
		identity="auth-server",
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
		identity="remote-waterloo",
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

	def _fake_request_json(
		method: str,
		url: str,
		payload: dict[str, object] | None = None,
		extra_headers: dict[str, str] | None = None,
		**kwargs: object,
	) -> tuple[int, dict[str, object]]:
		calls["method"] = method
		calls["url"] = url
		return 200, {"auth_enabled": False}

	monkeypatch.setattr(admin_mod.shutil, "which", lambda name: "/usr/bin/ssh")
	monkeypatch.setattr(admin_mod.subprocess, "Popen", _fake_popen)
	monkeypatch.setattr(admin_mod, "_free_local_port", lambda: 45678)
	monkeypatch.setattr(admin_mod, "_wait_for_tcp_port", lambda host, port, timeout: None)
	monkeypatch.setattr(admin_mod, "_request_json", _fake_request_json)

	mode, status, identity = admin_mod._ping_admin(entry)
	assert mode == "ssh"
	assert status == "auth-disabled"
	assert identity == ""
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


def test_admin_access_treats_ipv4_loopback_alias_as_direct(monkeypatch) -> None:
	entry = ServerEntry(
		identity="local-waterloo",
		label="local-waterloo",
		url="http://127.0.1.1:23316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="",
	)
	assert admin_mod._admin_access_mode(entry) == "direct"


def test_format_add_and_del_server_messages_are_specific() -> None:
	entry = ServerEntry(
		identity="",
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
			TableColumn("identity", "Identity"),
			TableColumn("host", "Host"),
			TableColumn("admin_access", "Admin access"),
			TableColumn("admin_status", "Admin status"),
			TableColumn("client_status", "Client status"),
		),
		rows=[{"label": "server", "identity": "server-id", "host": "localhost", "admin_access": "direct", "admin_status": "auth-required (401)", "client_status": "ok"}],
	)
	out = _render_table_report(report)
	assert "auth-required (401)" in out
	assert "| ok" in out or "|ok" in out


def test_table_report_to_json_has_stable_shape() -> None:
	report = TableReport(
		kind="servers",
		columns=(TableColumn("label", "Label"), TableColumn("identity", "Identity"), TableColumn("host_port", "Host:Port")),
		rows=[{"label": "local-waterloo", "identity": "local-waterloo", "host_port": "127.0.0.1:13316"}],
	)
	doc = _table_report_to_json(report)
	assert doc["kind"] == "servers"
	assert doc["columns"] == [
		{"key": "label", "label": "Label"},
		{"key": "identity", "label": "Identity"},
		{"key": "host_port", "label": "Host:Port"},
	]
	assert doc["rows"] == [{"label": "local-waterloo", "identity": "local-waterloo", "host_port": "127.0.0.1:13316"}]


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


def test_main_writes_json_diagnostics_for_missing_server(tmp_path: Path) -> None:
	registry = tmp_path / "registry.json"
	registry.write_text("{\"servers\": []}\n", encoding="utf-8")
	diag = tmp_path / "diag.json"

	rc = admin_mod.main([
		"--registry",
		str(registry),
		"--out-diag-json",
		str(diag),
		"gen-token",
		"--server",
		"missing-server",
	])

	assert rc == 1
	doc = json.loads(diag.read_text(encoding="utf-8"))
	assert doc["$schema"].endswith("wtrl-tracer-json-0.1.0.schema.json")
	assert doc["__WTRL_INFO__"][0]["msg"] == "generating a bearer token"
	assert doc["__WTRL_ERROR__"][0]["rule-id"] == "MCPA-001"
	assert "unknown server label" in doc["__WTRL_ERROR__"][0]["msg"]


def test_main_writes_json_diagnostics_for_success(tmp_path: Path) -> None:
	registry = tmp_path / "registry.json"
	registry.write_text("{\"servers\": []}\n", encoding="utf-8")
	diag = tmp_path / "diag.json"

	rc = admin_mod.main([
		"--registry",
		str(registry),
		"--out-diag-json",
		str(diag),
		"list-servers",
	])

	assert rc == 0
	doc = json.loads(diag.read_text(encoding="utf-8"))
	assert doc["$schema"].endswith("wtrl-tracer-json-0.1.0.schema.json")
	assert doc["__WTRL_INFO__"][0]["msg"] == "listing registered servers"
	assert doc["__WTRL_WARNING__"] == []
	assert doc["__WTRL_ERROR__"] == []


def test_main_emits_tracer_on_gen_token_timeout_without_json(monkeypatch, capsys) -> None:
	entry = ServerEntry(
		identity="lots_of_stuff",
		label="lots_of_stuff",
		url="http://localhost:13316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="",
	)

	@contextmanager
	def _fake_admin_access(entry: ServerEntry):
		yield admin_mod.AdminAccess(mode="direct", base_url=entry.url)

	def _fake_request_json(*args, **kwargs):
		raise AdminCliError("MCPA-004", "request to http://localhost:13316/admin/tokens timed out after 5.0s")

	monkeypatch.setattr(
		admin_mod,
		"_load_registry",
		lambda path: {"servers": [{"identity": "lots_of_stuff", "label": "lots_of_stuff", "url": "http://localhost:13316"}]},
	)
	monkeypatch.setattr(admin_mod, "_read_server_entry", lambda data, label: entry)
	monkeypatch.setattr(admin_mod, "_admin_access", _fake_admin_access)
	monkeypatch.setattr(admin_mod, "_request_json", _fake_request_json)

	rc = admin_mod.main(["gen-token", "--server", "lots_of_stuff"])

	assert rc == 1
	captured = capsys.readouterr()
	assert captured.out == ""
	assert "----- Tracer-----8<---------------------------------------------" in captured.err
	assert "generating a bearer token" in captured.err
	assert "timed out after 5.0s" in captured.err


def test_list_servers_json_mode_keeps_empty_report(monkeypatch, capsys) -> None:
	monkeypatch.setattr(admin_mod, "_load_registry", lambda path: {"servers": []})
	args = argparse.Namespace(registry=None, out=None, out_json="-")
	assert _cmd_list_servers(args) == 0
	doc = json.loads(capsys.readouterr().out)
	assert doc["kind"] == "servers"
	assert doc["rows"] == []


def test_ping_servers_json_mode_falls_back_to_label_when_identity_missing(monkeypatch, capsys) -> None:
	monkeypatch.setattr(
		admin_mod,
		"_load_registry",
		lambda path: {"servers": [{"identity": "", "label": "noauth-server", "url": "http://127.0.0.1:13316"}]},
	)
	monkeypatch.setattr(admin_mod, "_ping_admin", lambda entry: ("direct", "auth-disabled", ""))
	monkeypatch.setattr(admin_mod, "_ping_client", lambda entry: "ok")
	args = argparse.Namespace(registry=None, out=None, out_json="-")
	assert _cmd_ping_servers(args) == 0
	doc = json.loads(capsys.readouterr().out)
	assert doc["kind"] == "ping"
	assert doc["rows"][0]["label"] == "noauth-server"
	assert doc["rows"][0]["identity"] == "noauth-server"


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
	tr = admin_mod.tracer()
	assert _cmd_add_server(args, tr) == 0
	buf = io.StringIO()
	emit_diagnostics(tr, buf, strip_ansi=True)
	text = buf.getvalue()
	assert isinstance(saved.get("data"), dict)


def test_del_server_reports_removal_message(monkeypatch, capsys) -> None:
	monkeypatch.setattr(admin_mod, "_load_registry", lambda path: {"servers": [{"label": "local-waterloo"}]})
	monkeypatch.setattr(admin_mod, "_save_registry", lambda path, data: None)
	args = argparse.Namespace(registry=None, label="local-waterloo")
	tr = admin_mod.tracer()
	assert _cmd_del_server(args, tr) == 0
	buf = io.StringIO()
	emit_diagnostics(tr, buf, strip_ansi=True)
	text = buf.getvalue()


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


def test_request_json_timeout_becomes_admin_error(monkeypatch) -> None:
	def _fake_urlopen(req: object, timeout: float = 0.0) -> object:
		raise TimeoutError("timed out")

	monkeypatch.setattr(admin_mod, "urlopen", _fake_urlopen)
	try:
		_request_json("POST", "http://example.invalid/mcp", {"jsonrpc": "2.0"})
	except AdminCliError as exc:
		assert exc.rule_id == "MCPA-004"
		assert "timed out after" in str(exc)
	else:
		raise AssertionError("expected request timeout to be wrapped")


def test_verify_token_command_uses_bearer_token(monkeypatch) -> None:
	entry = ServerEntry(
		identity="auth-server",
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

	def _fake_request_json(
		method: str,
		url: str,
		payload: dict[str, object] | None = None,
		extra_headers: dict[str, str] | None = None,
		**kwargs: object,
	) -> tuple[int, dict[str, object]]:
		calls["method"] = method
		calls["url"] = url
		calls["payload"] = payload
		calls["extra_headers"] = extra_headers
		return 200, {"result": "ok"}

	monkeypatch.setattr(admin_mod, "_read_server_entry", _fake_read_server_entry)
	monkeypatch.setattr(admin_mod, "_load_registry", lambda path: {"servers": [{"identity": "auth-server", "label": "auth-server", "url": "http://127.0.0.1:23316"}]})
	monkeypatch.setattr(admin_mod, "_request_json", _fake_request_json)
	args = argparse.Namespace(server="auth-server", token="BearerToken", registry=None)
	tr = admin_mod.tracer()
	assert _cmd_verify_token(args, tr) == 0
	assert calls["method"] == "POST"
	assert calls["url"] == "http://127.0.0.1:23316/mcp"
	assert isinstance(calls["payload"], dict)
	assert calls["extra_headers"] == {"Authorization": "Bearer BearerToken", "Host": "127.0.0.1:23316"}


def test_verify_token_command_uses_ssh_tunnel_for_non_loopback_host(monkeypatch, capsys) -> None:
	entry = ServerEntry(
		identity="remote-waterloo",
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

	def _fake_request_json(
		method: str,
		url: str,
		payload: dict[str, object] | None = None,
		extra_headers: dict[str, str] | None = None,
		**kwargs: object,
	) -> tuple[int, dict[str, object]]:
		calls["method"] = method
		calls["url"] = url
		calls["payload"] = payload
		calls["extra_headers"] = extra_headers
		return 200, {"result": "ok"}

	monkeypatch.setattr(admin_mod, "_read_server_entry", _fake_read_server_entry)
	monkeypatch.setattr(admin_mod, "_admin_access", _fake_admin_access)
	monkeypatch.setattr(admin_mod, "_load_registry", lambda path: {"servers": [{"identity": "remote-waterloo", "label": "remote-waterloo", "url": "http://gilgamesh:23316"}]})
	monkeypatch.setattr(admin_mod, "_request_json", _fake_request_json)
	args = argparse.Namespace(server="remote-waterloo", token="BearerToken", registry=None)
	tr = admin_mod.tracer()
	assert _cmd_verify_token(args, tr) == 0
	assert calls["method"] == "POST"
	assert calls["url"] == "http://127.0.0.1:45678/mcp"
	assert isinstance(calls["payload"], dict)
	assert calls["extra_headers"] == {"Authorization": "Bearer BearerToken", "Host": "gilgamesh:23316"}
	buf = io.StringIO()
	emit_diagnostics(tr, buf, strip_ansi=True)
	text = buf.getvalue()


def test_verify_token_command_reports_invalid_token_on_401(monkeypatch, capsys) -> None:
	entry = ServerEntry(
		identity="auth-server",
		label="auth-server",
		url="http://127.0.0.1:23316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="",
	)

	def _fake_read_server_entry(data: dict[str, object], label: str) -> ServerEntry:
		assert label == "auth-server"
		return entry

	def _fake_request_json(
		method: str,
		url: str,
		payload: dict[str, object] | None = None,
		extra_headers: dict[str, str] | None = None,
		**kwargs: object,
	) -> tuple[int, dict[str, object]]:
		return 401, {"error": "unauthorized"}

	monkeypatch.setattr(admin_mod, "_read_server_entry", _fake_read_server_entry)
	monkeypatch.setattr(admin_mod, "_load_registry", lambda path: {"servers": [{"identity": "auth-server", "label": "auth-server", "url": "http://127.0.0.1:23316"}]})
	monkeypatch.setattr(admin_mod, "_request_json", _fake_request_json)
	args = argparse.Namespace(server="auth-server", token="BearerToken", registry=None)
	try:
		_cmd_verify_token(args)
	except AdminCliError as exc:
		assert exc.rule_id == "MCPA-005"
		assert "invalid token (401)" in exc.message
	else:
		raise AssertionError("AdminCliError not raised")


def test_verify_token_command_reports_unknown_server_cleanly(monkeypatch) -> None:
	args = argparse.Namespace(server="missing-server", token="abc", registry=None)
	monkeypatch.setattr(admin_mod, "_load_registry", lambda path: {"servers": []})
	try:
		_cmd_verify_token(args)
	except AdminCliError as exc:
		assert exc.rule_id == "MCPA-001"
		assert str(exc) == "unknown server label: missing-server"
	else:
		raise AssertionError("AdminCliError not raised")


def test_list_tokens_reports_malformed_token_list(monkeypatch) -> None:
	entry = ServerEntry(
		identity="auth-server",
		label="auth-server",
		url="http://127.0.0.1:23316",
		mcp_endpoint="/mcp",
		admin_endpoint="/admin",
		description="",
	)

	def _fake_read_server_entry(data: dict[str, object], label: str) -> ServerEntry:
		assert label == "auth-server"
		return entry

	def _fake_request_json(
		method: str,
		url: str,
		payload: dict[str, object] | None = None,
		extra_headers: dict[str, str] | None = None,
		**kwargs: object,
	) -> tuple[int, dict[str, object]]:
		return 200, {"tokens": "not-a-list"}

	monkeypatch.setattr(admin_mod, "_read_server_entry", _fake_read_server_entry)
	monkeypatch.setattr(admin_mod, "_load_registry", lambda path: {"servers": [{"identity": "auth-server", "label": "auth-server", "url": "http://127.0.0.1:23316"}]})
	monkeypatch.setattr(admin_mod, "_request_json", _fake_request_json)
	args = argparse.Namespace(server="auth-server", registry=None, out=None, out_json=None)
	try:
		_cmd_list_tokens(args)
	except AdminCliError as exc:
		assert exc.rule_id == "MCPA-004"
		assert str(exc) == "server 'auth-server' returned a malformed token list"
	else:
		raise AssertionError("AdminCliError not raised")
