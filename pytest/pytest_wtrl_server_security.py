#!/usr/bin/env python3
"""Pytests for runtime security overrides in the Waterloo MCP server."""

from __future__ import annotations

from pathlib import Path

import pytest

from sdv.doc.waterloo.mcp.wtrl_server import (
	AuthConfig,
	SecurityConfig,
	LoggingConfig,
	McpConfig,
	ServerConfig,
	_print_config_error,
	_runtime_allowed_hosts,
	_with_runtime_security_overrides,
)


def test_runtime_allowed_hosts_defaults_to_config_hosts() -> None:
	assert _runtime_allowed_hosts(["127.0.0.1:13316"], None, 13316, None, 13316) == ["127.0.0.1:13316"]


def test_runtime_allowed_hosts_public_port_rewrites_defaults() -> None:
	assert _runtime_allowed_hosts(["127.0.0.1:13316"], None, 13316, 12345, 13316) == [
		"localhost:12345",
		"127.0.0.1:12345",
	]


def test_runtime_allowed_hosts_public_port_combines_custom_hosts() -> None:
	assert _runtime_allowed_hosts(["127.0.0.1:13316"], ["localhost", "gilgamesh"], 13316, 12345, 13316) == [
		"localhost:12345",
		"gilgamesh:12345",
	]


def test_runtime_allowed_hosts_without_public_port_uses_server_port() -> None:
	assert _runtime_allowed_hosts(["127.0.0.1:13316"], ["gilgamesh"], 13316, None, 13316) == ["gilgamesh:13316"]


def test_runtime_allowed_hosts_server_port_override_updates_config_hosts() -> None:
	assert _runtime_allowed_hosts(["127.0.0.1:13316", "localhost:13316"], None, 13315, None, 13316) == [
		"127.0.0.1:13315",
		"localhost:13315",
	]


def test_runtime_allowed_hosts_rejects_ports_inside_host_names() -> None:
	with pytest.raises(ValueError, match="must not include a port"):
		_runtime_allowed_hosts(["127.0.0.1:13316"], ["localhost:13316"], 13316, 12345, 13316)


def test_with_runtime_security_overrides_keeps_non_security_fields() -> None:
	config = McpConfig(
		server=ServerConfig(
			identity=None,
			transport="streamable-http",
			host="127.0.0.1",
			port=13316,
			streamable_http_path="/mcp",
		),
		security=SecurityConfig(
			allowed_hosts=["127.0.0.1:13316"],
			allowed_origins=["http://gilgamesh:6274"],
		),
		auth=AuthConfig(enabled=False, token_store_path=Path("/tmp/tokens.json"), realm="Waterloo MCP"),
		logging=LoggingConfig(level="INFO", config_path=None, access_log=True),
		roots=[],
		source_path=Path("/tmp/wtrl.toml"),
	)
	overridden = _with_runtime_security_overrides(config, 13315, ["localhost", "gilgamesh"], 13314)
	assert overridden.logging == config.logging
	assert overridden.roots == config.roots
	assert overridden.source_path == config.source_path
	assert overridden.server.transport == config.server.transport
	assert overridden.server.host == config.server.host
	assert overridden.server.port == 13315
	assert overridden.server.streamable_http_path == config.server.streamable_http_path
	assert overridden.security.allowed_hosts == ["localhost:13314", "gilgamesh:13314"]
	assert overridden.security.allowed_origins == config.security.allowed_origins
	assert overridden.auth == config.auth


def test_print_config_error_includes_load_context(capsys) -> None:
	_print_config_error(ValueError("broken config"), Path("/tmp/wtrl.toml"))
	captured = capsys.readouterr()
	assert "Loading configuration file: /tmp/wtrl.toml" in captured.err
	assert "broken config" in captured.err
