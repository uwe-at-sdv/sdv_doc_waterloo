#!/usr/bin/env python3
"""Pytests for waterlint subcommands version, version-json and list-schemas."""

from __future__ import annotations

import json

from pytest_common import run_waterlint


def test_version_prints_plain_version_string() -> None:
	res = run_waterlint("version")
	assert res.returncode == 0, res.stderr
	assert res.stderr == ""
	assert res.stdout.strip()
	assert "." in res.stdout.strip()


def test_version_json_reports_all_schema_categories() -> None:
	res = run_waterlint("version-json")
	assert res.returncode == 0, res.stderr
	doc = json.loads(res.stdout)
	assert isinstance(doc, dict)
	assert set(doc) == {
		"waterlint",
		"wtrl-json",
		"wtrl-tracer-json",
		"wtrl-example-refs-json",
		"wtrl-explain-section-json",
		"wtrl-explain-subsection-json",
		"wtrl-walk-json",
		"wtrl-mcp-about-json",
		"wtrl-mcp-about-topic-json",
		"wtrl_mcp",
		"python-waterloo-lexer",
	}
	assert doc["waterlint"] == {"kind": "executable", "version": doc["waterlint"]["version"]}
	assert doc["wtrl_mcp"] == {"kind": "package", "version": doc["wtrl_mcp"]["version"]}
	assert doc["python-waterloo-lexer"] == {"kind": "package", "version": doc["python-waterloo-lexer"]["version"]}
	for key in (
		"wtrl-json",
		"wtrl-tracer-json",
		"wtrl-example-refs-json",
		"wtrl-explain-section-json",
		"wtrl-explain-subsection-json",
		"wtrl-walk-json",
		"wtrl-mcp-about-json",
		"wtrl-mcp-about-topic-json",
	):
		value = doc[key]
		assert isinstance(value, dict)
		assert value.get("kind") == "schema"
		assert isinstance(value.get("version"), str)


def test_list_schemas_lists_all_schema_categories() -> None:
	res = run_waterlint("list-schemas")
	assert res.returncode == 0, res.stderr
	txt = res.stdout
	assert "wtrl-json-" in txt
	assert "wtrl-tracer-json-" in txt
	assert "wtrl-example-refs-json-" in txt


def test_list_schemas_includes_versions_reported_by_version_json() -> None:
	ver = run_waterlint("version-json")
	assert ver.returncode == 0, ver.stderr
	ver_doc = json.loads(ver.stdout)

	ls = run_waterlint("list-schemas")
	assert ls.returncode == 0, ls.stderr
	txt = ls.stdout

	for category in ("wtrl-json", "wtrl-tracer-json", "wtrl-example-refs-json"):
		version = ver_doc[category]["version"]
		needle = f"{category}-{version}.schema.json"
		assert needle in txt, f"missing schema file {needle!r} in list-schemas output"
