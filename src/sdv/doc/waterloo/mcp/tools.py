"""Waterloo MCP tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _classify_root(path_text: str) -> str:
	path = Path(path_text)
	if path.is_dir():
		return "directory"
	if path.is_file():
		return "file"
	return "missing"


def list_docs(roots: list[str]) -> list[dict[str, Any]]:
	"""Return a compact summary of configured Waterloo data roots."""
	out: list[dict[str, Any]] = []
	for idx, root_text in enumerate(roots):
		root = Path(root_text).expanduser()
		item = {
			"root_id": f"root-{idx}",
			"label": root.name or str(root),
			"kind": _classify_root(str(root)),
			"path": str(root.resolve()) if root.exists() else str(root),
		}
		out.append(item)
	return out

