#!/usr/bin/env python3
"""Schema checks for the new MCP JSON formats."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from pytest_common import DIR_SCHEMA


def _load_schema(name: str) -> dict[str, object]:
	path = Path(DIR_SCHEMA) / name
	doc = json.loads(path.read_text(encoding="utf-8"))
	if not isinstance(doc, dict):
		raise AssertionError(f"schema is not a JSON object: {path}")
	Draft202012Validator.check_schema(doc)
	return doc


def test_mcp_admin_registry_schema_accepts_current_shape() -> None:
	schema = _load_schema("wtrl-mcp-admin-registry-json-0.1.0.schema.json")
	doc = {
		"servers": [
			{
				"label": "local-waterloo",
				"url": "http://127.0.0.1:13316",
				"mcp_endpoint": "/mcp",
				"admin_endpoint": "/admin",
				"description": "Local development server",
			}
		]
	}
	Draft202012Validator(schema).validate(doc)


def test_mcp_admin_registry_schema_rejects_extra_properties() -> None:
	schema = _load_schema("wtrl-mcp-admin-registry-json-0.1.0.schema.json")
	doc = {
		"servers": [
			{
				"label": "local-waterloo",
				"url": "http://127.0.0.1:13316",
				"mcp_endpoint": "/mcp",
				"admin_endpoint": "/admin",
				"description": "Local development server",
				"extra": "not-allowed",
			}
		]
	}
	try:
		Draft202012Validator(schema).validate(doc)
	except ValidationError:
		pass
	else:
		raise AssertionError("expected schema validation to reject extra properties")


def test_mcp_auth_token_store_schema_accepts_current_shape() -> None:
	schema = _load_schema("wtrl-mcp-auth-token-store-json-0.1.0.schema.json")
	doc = {
		"tokens": [
			{
				"token_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
				"token_id": "karl_ernst-vscode-tablet",
				"user": "karl_ernst",
				"client": "vscode",
				"location": "tablet",
				"created_at": "2026-07-07T12:00:00Z",
				"expires_at": None,
				"revoked_at": None,
				"notes": "demo",
			}
		]
	}
	Draft202012Validator(schema).validate(doc)


def test_mcp_auth_token_store_schema_rejects_extra_properties() -> None:
	schema = _load_schema("wtrl-mcp-auth-token-store-json-0.1.0.schema.json")
	doc = {
		"tokens": [
			{
				"token_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
				"token_id": "karl_ernst-vscode-tablet",
				"user": "karl_ernst",
				"client": "vscode",
				"location": "tablet",
				"created_at": "2026-07-07T12:00:00Z",
				"expires_at": None,
				"revoked_at": None,
				"notes": "demo",
				"extra": "not-allowed",
			}
		]
	}
	try:
		Draft202012Validator(schema).validate(doc)
	except ValidationError:
		pass
	else:
		raise AssertionError("expected schema validation to reject extra properties")
