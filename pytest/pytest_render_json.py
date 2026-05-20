#!/usr/bin/env python3
"""Pytests for waterlint subcommand render-json."""

from __future__ import annotations

import json
import re
from pathlib import Path

from pytest_common import ROOT, run_waterlint, DIR_EXAMPLES

def _parse_info_counts(stderr: str) -> tuple[dict[str, tuple[int, int]], dict[str, int]]:
	patts = {
		"modules": r"Num modules skipped \(no docstring / invalid\)\s*:\s*(\d+) / (\d+)",
		"classes": r"Num classes skipped \(no docstring / invalid\)\s*:\s*(\d+) / (\d+)",
		"callables": r"Num callables skipped \(no docstring / invalid\)\s*:\s*(\d+) / (\d+)",
		"unknown": r"Num <unknown> skipped \(no docstring / invalid\)\s*:\s*(\d+) / (\d+)",
	}
	render_patts = {
		"modules": r"Num modules rendered\s*:\s*(\d+)",
		"classes": r"Num classes rendered\s*:\s*(\d+)",
		"callables": r"Num callables rendered\s*:\s*(\d+)",
	}
	skipped: dict[str, tuple[int, int]] = {}
	for key, patt in patts.items():
		m = re.search(patt, stderr)
		if not m:
			raise AssertionError(f"Pattern for {key} not found in stderr: {stderr}")
		skipped[key] = (int(m.group(1)), int(m.group(2)))

	rendered: dict[str, int] = {}
	for key, patt in render_patts.items():
		m = re.search(patt, stderr)
		if not m:
			raise AssertionError(f"Rendered pattern for {key} not found in stderr: {stderr}")
		rendered[key] = int(m.group(1))
	return skipped, rendered


def _run_render_json(obj: str, scope: str = "core", include_imported: bool = True):
	args = [
		"render-json",
		"--scope", scope,
		"--basedir", DIR_EXAMPLES,
		"--obj", obj,
		"--no-allow-local-paths",
	]
	if not include_imported:
		args.append("--no-include-imported")
	return run_waterlint(*args)


def _run_render_json_cli(args: list[str]):
	return run_waterlint("render-json", *args)


def _run_waterlint_validate_json(path: str, schema: str | None = None):
	args: list[str] = ["validate-json", "--in", path]
	if schema:
		args.extend(["--schema", schema])
	return run_waterlint(*args)


def _load_json_doc(path: Path) -> dict[str, object]:
	with path.open("r", encoding="utf-8") as fh:
		return json.load(fh)


def test_render_json_counts_public_A() -> None:
	res = _run_render_json("pytest_good_render_json_A", scope="public", include_imported=True)
	assert res.returncode == 0, res.stderr
	skipped, rendered = _parse_info_counts(res.stderr)
	assert skipped["modules"] == (1, 1)
	assert skipped["classes"] == (1, 3)
	assert skipped["callables"] == (1, 3)
	assert skipped["unknown"] == (0, 0)
	assert rendered["modules"] == 0
	assert rendered["classes"] == 1
	assert rendered["callables"] == 1


def test_render_json_counts_public_B() -> None:
	res = _run_render_json("pytest_good_render_json_B", scope="public", include_imported=True)
	assert res.returncode == 0, res.stderr
	skipped, rendered = _parse_info_counts(res.stderr)
	assert skipped["modules"] == (0, 0)
	assert skipped["classes"] == (1, 2)
	assert skipped["callables"] == (0, 1)
	assert skipped["unknown"] == (0, 0)
	assert rendered["modules"] == 0
	assert rendered["classes"] == 0
	assert rendered["callables"] == 0


def test_render_json_counts_public_C() -> None:
	res = _run_render_json("pytest_good_render_json_C", scope="public", include_imported=True)
	assert res.returncode == 0, res.stderr
	skipped, rendered = _parse_info_counts(res.stderr)
	assert skipped["modules"] == (0, 1)
	assert skipped["classes"] == (0, 1)
	assert skipped["callables"] == (1, 2)
	assert skipped["unknown"] == (0, 0)
	assert rendered["modules"] == 0
	assert rendered["classes"] == 0
	assert rendered["callables"] == 0


def test_render_json_counts_extension_A() -> None:
	res = _run_render_json("pytest_good_render_json_A", scope="extension", include_imported=True)
	assert res.returncode == 0, res.stderr
	skipped, rendered = _parse_info_counts(res.stderr)
	assert skipped["modules"] == (1, 1)
	assert skipped["classes"] == (1, 3)
	assert skipped["callables"] == (1, 3)
	assert skipped["unknown"] == (0, 0)
	assert rendered["modules"] == 1
	assert rendered["classes"] == 2
	assert rendered["callables"] == 2


def test_render_json_counts_extension_B() -> None:
	res = _run_render_json("pytest_good_render_json_B", scope="extension", include_imported=True)
	assert res.returncode == 0, res.stderr
	skipped, rendered = _parse_info_counts(res.stderr)
	assert skipped["modules"] == (0, 0)
	assert skipped["classes"] == (1, 2)
	assert skipped["callables"] == (0, 1)
	assert skipped["unknown"] == (0, 0)
	assert rendered["modules"] == 1
	assert rendered["classes"] == 1
	assert rendered["callables"] == 1


def test_render_json_counts_extension_C() -> None:
	res = _run_render_json("pytest_good_render_json_C", scope="extension", include_imported=True)
	assert res.returncode == 0, res.stderr
	skipped, rendered = _parse_info_counts(res.stderr)
	assert skipped["modules"] == (0, 1)
	assert skipped["classes"] == (0, 1)
	assert skipped["callables"] == (1, 2)
	assert skipped["unknown"] == (0, 0)
	assert rendered["modules"] == 0
	assert rendered["classes"] == 0
	assert rendered["callables"] == 0


def test_render_json_counts_core_no_imports_A() -> None:
	res = _run_render_json("pytest_good_render_json_A", include_imported=False)
	assert res.returncode == 0, res.stderr
	skipped, rendered = _parse_info_counts(res.stderr)
	assert skipped["modules"] == (1, 0)
	assert skipped["classes"] == (0, 1)
	assert skipped["callables"] == (0, 1)
	assert skipped["unknown"] == (0, 0)
	assert rendered["modules"] == 0
	assert rendered["classes"] == 1
	assert rendered["callables"] == 1


def test_render_json_counts_core_A() -> None:
	res = _run_render_json("pytest_good_render_json_A", include_imported=True)
	assert res.returncode == 0, res.stderr
	skipped, rendered = _parse_info_counts(res.stderr)
	assert skipped["modules"] == (1, 1)
	assert skipped["classes"] == (1, 3)
	assert skipped["callables"] == (1, 3)
	assert skipped["unknown"] == (0, 0)
	assert rendered["modules"] == 1
	assert rendered["classes"] == 3
	assert rendered["callables"] == 3


def test_render_json_counts_core_B() -> None:
	res = _run_render_json("pytest_good_render_json_B", include_imported=False)
	assert res.returncode == 0, res.stderr
	skipped, rendered = _parse_info_counts(res.stderr)
	assert skipped["modules"] == (0, 0)
	assert skipped["classes"] == (1, 2)
	assert skipped["callables"] == (0, 1)
	assert skipped["unknown"] == (0, 0)
	assert rendered["modules"] == 1
	assert rendered["classes"] == 1
	assert rendered["callables"] == 1


def test_render_json_counts_core_C() -> None:
	res = _run_render_json("pytest_good_render_json_C", include_imported=False)
	assert res.returncode == 0, res.stderr
	skipped, rendered = _parse_info_counts(res.stderr)
	assert skipped["modules"] == (0, 1)
	assert skipped["classes"] == (0, 1)
	assert skipped["callables"] == (1, 2)
	assert skipped["unknown"] == (0, 0)
	assert rendered["modules"] == 0
	assert rendered["classes"] == 1
	assert rendered["callables"] == 1


def test_render_json_out_dir_single_obj_generates_good_practice_name(tmp_path: Path) -> None:
	res = _run_render_json_cli(
		[
			"--basedir", DIR_EXAMPLES,
			"--obj", "test_docitem_coroutine",
			"--scope", "core",
			"--flavour", "rfc-2119",
			"--out-dir", str(tmp_path),
			"--no-allow-local-paths",
		]
	)
	assert res.returncode == 0, res.stderr
	out_file = tmp_path / "test_docitem_coroutine.wtrl.core.rfc-2119.json"
	assert out_file.exists(), f"expected file not found: {out_file}"
	with out_file.open("r", encoding="utf-8") as fh:
		doc = json.load(fh)
	assert isinstance(doc, dict)
	assert "__WTRL_OBJECTS__" in doc


def test_render_json_out_dir_multi_obj_requires_out_prefix(tmp_path: Path) -> None:
	res = _run_render_json_cli(
		[
			"--basedir", DIR_EXAMPLES,
			"--obj", "test_docitem_method_property",
			"--obj", "test_docitem_coroutine",
			"--out-dir", str(tmp_path),
			"--no-allow-local-paths",
		]
	)
	assert res.returncode == 1, f"expected exit code 1, got {res.returncode}: {res.stderr}"
	assert "--out-prefix is required" in res.stderr


def test_render_json_out_dir_multi_obj_with_prefix_writes_prefixed_file(tmp_path: Path) -> None:
	res = _run_render_json_cli(
		[
			"--basedir", DIR_EXAMPLES,
			"--obj", "test_docitem_method_property",
			"--obj", "test_docitem_coroutine",
			"--out-dir", str(tmp_path),
			"--out-prefix", "bundle",
			"--scope", "core",
			"--flavour", "rfc-2119",
			"--no-allow-local-paths",
		]
	)
	assert res.returncode == 0, res.stderr
	out_file = tmp_path / "bundle.wtrl.core.rfc-2119.json"
	assert out_file.exists(), f"expected file not found: {out_file}"


def test_render_json_out_prefix_without_out_dir_fails() -> None:
	res = _run_render_json_cli(
		[
			"--basedir", DIR_EXAMPLES,
			"--obj", "test_docitem_coroutine",
			"--out-prefix", "oops",
			"--no-allow-local-paths",
		]
	)
	assert res.returncode == 1, f"expected exit code 1, got {res.returncode}: {res.stderr}"
	assert "--out-prefix requires --out-dir" in res.stderr


def test_render_json_from_walk_input(tmp_path: Path) -> None:
	walk_json = tmp_path / "walk.json"
	out_json = tmp_path / "render.json"
	res_walk = run_waterlint(
		"walk",
		"--basedir", DIR_EXAMPLES,
		"--obj", "test_docitem_coroutine",
		"--no-include-imported",
		"--out-json", str(walk_json),
	)
	assert res_walk.returncode == 0, res_walk.stderr
	assert walk_json.exists()

	res_render = run_waterlint(
		"render-json",
		"--in", str(walk_json),
		"--scope", "core",
		"--flavour", "rfc-2119",
		"--no-allow-local-paths",
		"--out", str(out_json),
	)
	assert res_render.returncode == 0, res_render.stderr
	assert out_json.exists()
	val = _run_waterlint_validate_json(str(out_json))
	assert val.returncode == 0, val.stderr


def _render_json_scope_triangle(tmp_path: Path, scope: str) -> None:
	direct_json = tmp_path / f"direct_{scope}.json"
	walk_json = tmp_path / f"walk_{scope}.json"
	replay_json = tmp_path / f"replay_{scope}.json"

	res_direct = run_waterlint(
		"render-json",
		"--basedir", DIR_EXAMPLES,
		"--obj", "test_scope_mix",
		"--scope", scope,
		"--no-allow-local-paths",
		"--out", str(direct_json),
	)
	assert res_direct.returncode == 0, res_direct.stderr
	assert direct_json.exists()

	res_walk = run_waterlint(
		"walk",
		"--basedir", DIR_EXAMPLES,
		"--obj", "test_scope_mix",
		"--out-json", str(walk_json),
	)
	assert res_walk.returncode == 0, res_walk.stderr
	assert walk_json.exists()

	res_replay = run_waterlint(
		"render-json",
		"--in", str(walk_json),
		"--scope", scope,
		"--no-allow-local-paths",
		"--out", str(replay_json),
	)
	assert res_replay.returncode == 0, res_replay.stderr
	assert replay_json.exists()

	res_validate = _run_waterlint_validate_json(str(replay_json))
	assert res_validate.returncode == 0, res_validate.stderr

	direct_doc = _load_json_doc(direct_json)
	replay_doc = _load_json_doc(replay_json)
	assert set(direct_doc["__WTRL_OBJECTS__"]) == set(replay_doc["__WTRL_OBJECTS__"])


def test_render_json_scope_triangle_public(tmp_path: Path) -> None:
	_render_json_scope_triangle(tmp_path, "public")


def test_render_json_scope_triangle_extension(tmp_path: Path) -> None:
	_render_json_scope_triangle(tmp_path, "extension")


def test_render_json_scope_triangle_core(tmp_path: Path) -> None:
	_render_json_scope_triangle(tmp_path, "core")


def _render_and_validate_example_json(tmp_path: Path, obj: str) -> None:
	"""Replicate make_doc.sh example pipeline: render-json -> validate-json."""
	res_render = _run_render_json_cli(
		[
			"--basedir", DIR_EXAMPLES,
			"--no-allow-local-paths",
			"--scope", "core",
			"--flavour", "rfc-2119",
			"--obj", obj,
			"--out-dir", str(tmp_path),
		]
	)
	assert res_render.returncode == 0, res_render.stderr

	out_file = tmp_path / f"{obj}.wtrl.core.rfc-2119.json"
	assert out_file.exists(), f"expected file not found: {out_file}"

	res_validate = _run_waterlint_validate_json(str(out_file))
	assert res_validate.returncode == 0, res_validate.stderr


def test_make_doc_examples_render_and_validate_method_decorator(tmp_path: Path) -> None:
	_render_and_validate_example_json(tmp_path, "test_docitem_method_decorator")


def test_make_doc_examples_render_and_validate_method_property(tmp_path: Path) -> None:
	_render_and_validate_example_json(tmp_path, "test_docitem_method_property")


def test_make_doc_examples_render_and_validate_definitions_inherited(tmp_path: Path) -> None:
	_render_and_validate_example_json(tmp_path, "test_docitem_definitions_inherited")
