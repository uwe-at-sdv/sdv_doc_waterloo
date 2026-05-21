#!/usr/bin/env python3
"""Pytests for waterlint subcommand carve."""

from __future__ import annotations

import json
from pathlib import Path

from pytest_common import DIR_EXAMPLES, run_waterlint


def _load_json_doc(path: Path) -> dict[str, object]:
	with path.open("r", encoding="utf-8") as fh:
		return json.load(fh)


def _count_entries(entries: list[dict[str, object]]) -> dict[str, dict[str, int] | int]:
	count_by_kind: dict[str, int] = {}
	count_by_scope: dict[str, int] = {}
	count_by_reason: dict[str, int] = {}
	included = 0
	for entry in entries:
		kind = str(entry.get("kind", "unknown"))
		scope = str(entry.get("scope", "unknown"))
		reason = str(entry.get("reason", "unknown"))
		count_by_kind[kind] = count_by_kind.get(kind, 0) + 1
		count_by_scope[scope] = count_by_scope.get(scope, 0) + 1
		count_by_reason[reason] = count_by_reason.get(reason, 0) + 1
		if bool(entry.get("included", False)):
			included += 1
	return {
		"total": len(entries),
		"included": included,
		"excluded": len(entries) - included,
		"by_kind": count_by_kind,
		"by_scope": count_by_scope,
		"by_reason": count_by_reason,
	}


def _make_walk_json(tmp_path: Path) -> Path:
	walk_json = tmp_path / "walk.json"
	res = run_waterlint(
		"walk",
		"--basedir", DIR_EXAMPLES,
		"--obj", "test_scope_mix",
		"--out-json", str(walk_json),
	)
	assert res.returncode == 0, res.stderr
	assert walk_json.exists()
	return walk_json


def test_carve_simplify_and_recompute(tmp_path: Path) -> None:
	walk_json = _make_walk_json(tmp_path)
	out_json = tmp_path / "carved.json"
	res = run_waterlint(
		"carve",
		"--in", str(walk_json),
		"--simplify",
		"--recompute",
		"--out", str(out_json),
	)
	assert res.returncode == 0, res.stderr
	assert out_json.exists()

	val = run_waterlint("validate-json", "--in", str(out_json))
	assert val.returncode == 0, val.stderr

	doc = _load_json_doc(out_json)
	entries = list(doc["__WTRL_OBJECTS__"])
	assert entries
	assert all(bool(entry.get("included", False)) for entry in entries)
	summary = doc["__WTRL_SUMMARY__"]
	assert isinstance(summary, dict)
	assert summary["excluded"] == 0
	assert summary["total"] == len(entries)
	assert summary["included"] == len(entries)
	assert doc["__WTRL_META__"]["generator"] == "waterlint.carve"


def test_carve_recompute_fixes_tampered_summary(tmp_path: Path) -> None:
	walk_json = _make_walk_json(tmp_path)
	tampered_json = tmp_path / "tampered.json"
	doc = _load_json_doc(walk_json)
	doc["__WTRL_SUMMARY__"] = {
		"total": 0,
		"included": 0,
		"excluded": 0,
		"by_kind": {},
		"by_scope": {},
		"by_reason": {},
	}
	with tampered_json.open("w", encoding="utf-8") as fh:
		json.dump(doc, fh, indent=4)
		fh.write("\n")

	out_json = tmp_path / "recomputed.json"
	res = run_waterlint(
		"carve",
		"--in", str(tampered_json),
		"--recompute",
		"--out", str(out_json),
	)
	assert res.returncode == 0, res.stderr
	doc_out = _load_json_doc(out_json)
	entries = list(doc_out["__WTRL_OBJECTS__"])
	expected = _count_entries(entries)
	summary = doc_out["__WTRL_SUMMARY__"]
	assert summary == expected


def test_carve_invalid_input_writes_diag_json(tmp_path: Path) -> None:
	bad_json = tmp_path / "bad.json"
	with bad_json.open("w", encoding="utf-8") as fh:
		json.dump(
			{
				"$schema": "https://sci-d-vis.com/schema/wtrl-walk-json-0.0.1.schema.json",
				"$id": "urn:waterlint:bad",
				"__WTRL_VERSION__": {"waterloo": "0.0.0", "schema": "0.0.1"},
				"__WTRL_META__": {"generated_at": "2026-05-21T00:00:00+02:00", "generator": "test"},
			},
			fh,
			indent=4,
		)
		fh.write("\n")
	diag_json = tmp_path / "diag.json"
	res = run_waterlint(
		"carve",
		"--in", str(bad_json),
		"--out-diag-json", str(diag_json),
	)
	assert res.returncode != 0
	assert diag_json.exists()
	doc = _load_json_doc(diag_json)
	assert "__WTRL_ERROR__" in doc
	assert doc["__WTRL_ERROR__"]
