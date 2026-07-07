#!/usr/bin/env python3
"""Pytests for MCP bearer-token helpers and localhost-only admin routes."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
from starlette.applications import Starlette

from sdv.doc.waterloo.mcp.wtrl_auth import (
	AuthTokenConflictError,
	FileTokenVerifier,
	create_token,
	list_tokens,
	revoke_token,
	verify_token,
)
from sdv.doc.waterloo.mcp.wtrl_server import (
	AuthConfig,
	LoggingConfig,
	McpConfig,
	SecurityConfig,
	ServerConfig,
	_auth_token_stats,
	_format_os_error,
	_install_admin_routes,
	_build_http_app,
	build_app,
	load_config,
)


def _config(tmp_path: Path, *, auth_enabled: bool = True) -> McpConfig:
	return McpConfig(
		server=ServerConfig(
			transport="streamable-http",
			host="127.0.0.1",
			port=13316,
			streamable_http_path="/mcp",
		),
		security=SecurityConfig(
			allowed_hosts=["127.0.0.1:13316"],
			allowed_origins=[],
		),
		auth=AuthConfig(
			enabled=auth_enabled,
			token_store_path=tmp_path / "tokens.json",
			realm="Waterloo MCP",
		),
		logging=LoggingConfig(level="INFO", config_path=None, access_log=False),
		roots=[],
		source_path=tmp_path / "wtrl_mcp.toml",
	)


def test_create_token_derives_token_id_and_verify_roundtrip(tmp_path: Path) -> None:
	record = create_token(
		tmp_path / "tokens.json",
		token_id="karl_ernst-any-any",
		expires_at=None,
		notes="demo",
	)
	assert record["token_id"] == "karl_ernst-any-any"
	assert record["user"] == "karl_ernst"
	assert record["client"] == "any"
	assert record["location"] == "any"
	assert isinstance(record["token"], str) and record["token"]

	verified = verify_token(tmp_path / "tokens.json", record["token"])
	assert verified is not None
	assert verified["token_id"] == "karl_ernst-any-any"
	assert verified["notes"] == "demo"


def test_create_token_rejects_duplicate_active_token_id(tmp_path: Path) -> None:
	path = tmp_path / "tokens.json"
	create_token(
		path,
		token_id="karl_ernst-vscode-tablet",
		expires_at=None,
		notes=None,
	)
	try:
		create_token(
			path,
			token_id="karl_ernst-vscode-tablet",
			expires_at=None,
			notes=None,
		)
	except AuthTokenConflictError:
		pass
	else:
		raise AssertionError("expected duplicate active token id to be rejected")


def test_revoke_token_marks_record_and_disables_verification(tmp_path: Path) -> None:
	path = tmp_path / "tokens.json"
	record = create_token(
		path,
		token_id="karl_ernst-vscode-tablet",
		expires_at=None,
		notes=None,
	)
	revoked = revoke_token(path, "karl_ernst-vscode-tablet")
	assert isinstance(revoked["revoked_at"], str) and revoked["revoked_at"]
	assert verify_token(path, record["token"]) is None


def test_verify_token_rejects_expired_token(tmp_path: Path) -> None:
	path = tmp_path / "tokens.json"
	record = create_token(
		path,
		token_id="karl_ernst-vscode-tablet",
		expires_at=(datetime.now(timezone.utc) - timedelta(days=1)).replace(microsecond=0).isoformat(),
		notes=None,
	)
	records = list_tokens(path)
	assert len(records) == 1
	assert records[0]["expires_at"] is not None
	assert verify_token(path, record["token"]) is None


def test_file_token_verifier_returns_access_token_for_active_token(tmp_path: Path) -> None:
	path = tmp_path / "tokens.json"
	record = create_token(
		path,
		token_id="karl_ernst-vscode-tablet",
		expires_at=None,
		notes=None,
	)
	verifier = FileTokenVerifier(path)
	access_token = asyncio.run(verifier.verify_token(record["token"]))
	assert access_token is not None
	assert access_token.client_id == "karl_ernst-vscode-tablet"
	assert access_token.scopes == []
	assert access_token.expires_at is None


def test_file_token_verifier_rejects_unknown_token(tmp_path: Path) -> None:
	verifier = FileTokenVerifier(tmp_path / "tokens.json")
	assert asyncio.run(verifier.verify_token("does-not-exist")) is None


def test_load_config_parses_auth_section(tmp_path: Path) -> None:
	(tmp_path / "state").mkdir()
	config_path = tmp_path / "wtrl_mcp.toml"
	config_path.write_text(
		"""
[server]
transport = "streamable-http"
host = "127.0.0.1"
port = 13316
streamable_http_path = "/mcp"

[security]
allowed_hosts = ["127.0.0.1:13316"]
allowed_origins = []

[auth]
enabled = true
token_store = "state/tokens.json"
realm = "Test Realm"

[logging]
level = "INFO"

[[roots]]
path = "/tmp/root.json"
label = "Root"
enabled = false
kind = "wtrl-json"
""".strip(),
		encoding="utf-8",
	)
	config = load_config(config_path)
	assert config.auth.enabled is True
	assert config.auth.realm == "Test Realm"
	assert config.auth.token_store_path == (tmp_path / "state" / "tokens.json").resolve()
	assert not (tmp_path / "state" / "tokens.json").exists()


def test_load_config_accepts_existing_valid_auth_token_store(tmp_path: Path) -> None:
	(tmp_path / "state").mkdir()
	(tmp_path / "state" / "tokens.json").write_text(
		"""
		{
		  "tokens": []
		}
		""".strip()
		+ "\n",
		encoding="utf-8",
	)
	config_path = tmp_path / "wtrl_mcp.toml"
	config_path.write_text(
		"""
[server]
transport = "streamable-http"
host = "127.0.0.1"
port = 13316
streamable_http_path = "/mcp"

[security]
allowed_hosts = ["127.0.0.1:13316"]
allowed_origins = []

[auth]
enabled = true
token_store = "state/tokens.json"
realm = "Test Realm"

[logging]
level = "INFO"

[[roots]]
path = "/tmp/root.json"
label = "Root"
enabled = false
kind = "wtrl-json"
""".strip(),
		encoding="utf-8",
	)
	config = load_config(config_path)
	assert config.auth.enabled is True
	assert config.auth.token_store_path == (tmp_path / "state" / "tokens.json").resolve()


def test_load_config_rejects_invalid_existing_auth_token_store(tmp_path: Path) -> None:
	(tmp_path / "state").mkdir()
	(tmp_path / "state" / "tokens.json").write_text("{\"tokens\":[{\"token_id\":\"x\"}]}\n", encoding="utf-8")
	config_path = tmp_path / "wtrl_mcp.toml"
	config_path.write_text(
		"""
[server]
transport = "streamable-http"
host = "127.0.0.1"
port = 13316
streamable_http_path = "/mcp"

[security]
allowed_hosts = ["127.0.0.1:13316"]
allowed_origins = []

[auth]
enabled = true
token_store = "state/tokens.json"
realm = "Test Realm"

[logging]
level = "INFO"

[[roots]]
path = "/tmp/root.json"
label = "Root"
enabled = false
kind = "wtrl-json"
""".strip(),
		encoding="utf-8",
	)
	try:
		load_config(config_path)
	except ValueError as exc:
		message = str(exc)
		assert "Validating auth token store file:" in message
		assert "Auth token store file is invalid" in message
	else:
		raise AssertionError("expected invalid auth token store validation to fail")


def test_format_os_error_includes_errno_and_message() -> None:
	exc = OSError(30, "Read-only file system")
	assert _format_os_error(exc) == "OSError 30: Read-only file system"


def test_load_config_rejects_missing_auth_token_store_directory(tmp_path: Path) -> None:
	config_path = tmp_path / "wtrl_mcp.toml"
	config_path.write_text(
		"""
[server]
transport = "streamable-http"
host = "127.0.0.1"
port = 13316
streamable_http_path = "/mcp"

[security]
allowed_hosts = ["127.0.0.1:13316"]
allowed_origins = []

[auth]
enabled = true
token_store = "missing/state/tokens.json"
realm = "Test Realm"

[logging]
level = "INFO"

[[roots]]
path = "/tmp/root.json"
label = "Root"
enabled = false
kind = "wtrl-json"
""".strip(),
		encoding="utf-8",
	)
	try:
		load_config(config_path)
	except ValueError as exc:
		assert "Auth token store directory does not exist" in str(exc)
	else:
		raise AssertionError("expected auth token store directory validation to fail")


def test_build_app_enables_token_verifier_when_auth_is_enabled(tmp_path: Path) -> None:
	config = _config(tmp_path, auth_enabled=True)
	app = build_app(config)
	assert app._token_verifier is not None
	assert app.settings.auth is not None


def test_build_app_keeps_token_verifier_disabled_when_auth_is_disabled(tmp_path: Path) -> None:
	config = _config(tmp_path, auth_enabled=False)
	app = build_app(config)
	assert app._token_verifier is None
	assert app.settings.auth is None


def test_build_app_exposes_admin_status_when_auth_is_disabled(tmp_path: Path) -> None:
	config = _config(tmp_path, auth_enabled=False)
	app = _build_http_app(config, build_app(config))

	async def _run() -> None:
		transport = httpx.ASGITransport(app=app, client=("127.0.0.1", 50123))
		async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
			status_response = await client.get("/admin")
			assert status_response.status_code == 200, status_response.text
			status = status_response.json()
			assert status["auth_enabled"] is False
			response = await client.get("/admin/tokens")
			assert response.status_code == 404, response.text

	asyncio.run(_run())


def test_admin_routes_create_list_and_revoke_tokens(tmp_path: Path) -> None:
	config = _config(tmp_path, auth_enabled=True)
	app = Starlette()
	_install_admin_routes(app, config.auth)
	async def _run() -> None:
		transport = httpx.ASGITransport(app=app, client=("127.0.0.1", 50123))
		async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
			status_response = await client.get("/admin")
			assert status_response.status_code == 200, status_response.text
			status = status_response.json()
			assert status["auth_enabled"] is True
			assert status["valid_tokens"] == 0
			assert status["revoked_tokens"] == 0

			create_response = await client.post(
				"/admin/tokens",
				json={"token_id":"karl_ernst-vscode-tablet"},
			)
			assert create_response.status_code == 201, create_response.text
			created = create_response.json()
			assert created["token_id"] == "karl_ernst-vscode-tablet"
			assert isinstance(created["token"], str) and created["token"]

			list_response = await client.get("/admin/tokens")
			assert list_response.status_code == 200, list_response.text
			listed = list_response.json()
			assert [entry["token_id"] for entry in listed["tokens"]] == ["karl_ernst-vscode-tablet"]
			assert "token" not in listed["tokens"][0]

			revoke_response = await client.delete("/admin/tokens/karl_ernst-vscode-tablet")
			assert revoke_response.status_code == 204, revoke_response.text

			listed_after = (await client.get("/admin/tokens")).json()
			assert isinstance(listed_after["tokens"][0]["revoked_at"], str)

	asyncio.run(_run())


def test_streamable_http_requires_bearer_token_when_auth_is_enabled(tmp_path: Path) -> None:
	config = _config(tmp_path, auth_enabled=True)
	app = build_app(config).streamable_http_app()

	async def _run() -> None:
		transport = httpx.ASGITransport(app=app, client=("127.0.0.1", 50123))
		async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
			response = await client.post(
				"/mcp",
				headers={
					"Content-Type": "application/json",
					"Accept": "application/json, text/event-stream",
				},
				json={
					"jsonrpc": "2.0",
					"id": 1,
					"method": "initialize",
					"params": {
						"protocolVersion": "2025-11-25",
						"capabilities": {},
						"clientInfo": {"name": "pytest-mcp-auth", "version": "0.0.0"},
					},
				},
			)
			assert response.status_code == 401, response.text

	asyncio.run(_run())


def test_admin_routes_reject_non_loopback_clients(tmp_path: Path) -> None:
	config = _config(tmp_path, auth_enabled=True)
	app = Starlette()
	_install_admin_routes(app, config.auth)
	async def _run() -> None:
		transport = httpx.ASGITransport(app=app, client=("gilgamesh", 50123))
		async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
			response = await client.get("/admin/tokens")
			assert response.status_code == 403, response.text

	asyncio.run(_run())


def test_admin_routes_absent_when_auth_disabled(tmp_path: Path) -> None:
	config = _config(tmp_path, auth_enabled=False)
	app = Starlette()
	_install_admin_routes(app, config.auth)
	async def _run() -> None:
		transport = httpx.ASGITransport(app=app, client=("127.0.0.1", 50123))
		async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
			status_response = await client.get("/admin")
			assert status_response.status_code == 200, status_response.text
			status = status_response.json()
			assert status["auth_enabled"] is False
			response = await client.get("/admin/tokens")
			assert response.status_code == 404, response.text

	asyncio.run(_run())


def test_auth_token_stats_counts_valid_and_revoked_tokens(tmp_path: Path) -> None:
	path = tmp_path / "tokens.json"
	create_token(path, token_id="karl_ernst-vscode-tablet", expires_at=None, notes=None)
	create_token(path, token_id="alice-vscode-laptop", expires_at=None, notes=None)
	revoke_token(path, "karl_ernst-vscode-tablet")
	valid, revoked = _auth_token_stats(path)
	assert valid == 1
	assert revoked == 1
