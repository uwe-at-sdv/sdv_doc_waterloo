#!/usr/bin/env python3
"""Pytests for waterlint subcommand add-example-json."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from pytest_common import ROOT, run_waterlint, PATH_EXAMPLES, PATH_EXAMPLES_JSON


def _build_example_refs_doc(refs: dict[str, list[str]]) -> dict[str, object]:
	"""Build a valid example-refs JSON envelope for add-example-json tests."""
	return {
		"$schema": "https://sci-d-vis.com/schema/wtrl-example-refs-json-0.1.0.schema.json",
		"$id": "urn:pytest:wtrl-example-refs-json:0.1.0",
		"__WTRL_VERSION__": {
			"waterloo": "test",
			"schema": "0.1.0",
		},
		"__WTRL_EXAMPLE_REFS__": refs,
	}


def _run_waterlint_add_example_json(
	in_json: str,
	mapping_json: str,
	out_json: str,
	*,
	basedir: str | None = None,
	allow_local_paths: bool = False,
) -> subprocess.CompletedProcess[str]:
	args: list[str] = [
		"add-example-json",
		"--in", in_json,
		"--examples", mapping_json,
		"--out", out_json,
	]
	if basedir:
		args.extend(["--basedir", basedir])
	if allow_local_paths:
		args.append("--allow-local-paths")
	else:
		args.append("--no-allow-local-paths")
	return run_waterlint(*args)


def test_add_example_json_success_hash_key_and_no_path_default(tmp_path: Path) -> None:
	in_json = PATH_EXAMPLES_JSON / "mymod.wtrl.core.rfc-2119.json"
	mapping = tmp_path / "map.json"
	out_json = tmp_path / "out.json"
	mapping.write_text(
		json.dumps(_build_example_refs_doc({"mymod.X": ["example_mymod_X.py"]}), ensure_ascii=False),
		encoding="utf-8",
	)
	res = _run_waterlint_add_example_json(
		str(in_json),
		str(mapping),
		str(out_json),
		basedir=str(PATH_EXAMPLES_JSON),
		allow_local_paths=False,
	)
	assert res.returncode == 0, res.stderr
	doc = json.loads(out_json.read_text(encoding="utf-8"))
	ex = doc["__WTRL_EXAMPLES__"]
	assert len(ex) >= 1
	sha_keys = [k for k in ex.keys() if k.startswith("sha256_")]
	assert sha_keys, f"expected at least one sha256_* key, got {list(ex.keys())}"
	ex_key = sha_keys[0]
	assert "path" not in ex[ex_key]
	assert f"/__WTRL_EXAMPLES__/{ex_key}" in doc["__WTRL_OBJECTS__"]["mymod.X"]["examples"]


def test_add_example_json_fails_for_unknown_object(tmp_path: Path) -> None:
	in_json = PATH_EXAMPLES_JSON / "mymod.wtrl.core.rfc-2119.json"
	mapping = tmp_path / "map_bad.json"
	out_json = tmp_path / "out_bad.json"
	mapping.write_text(
		json.dumps(_build_example_refs_doc({"mymod.UnknownObject": ["example_mymod_X.py"]}), ensure_ascii=False),
		encoding="utf-8",
	)
	res = _run_waterlint_add_example_json(
		str(in_json),
		str(mapping),
		str(out_json),
		basedir=str(PATH_EXAMPLES_JSON),
		allow_local_paths=False,
	)
	assert res.returncode == 1, f"expected exit code 1, got {res.returncode}"
	assert "AXMPL-002" in res.stderr, res.stderr
