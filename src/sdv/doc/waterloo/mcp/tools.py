"""Waterloo MCP tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


def _classify_root(path_text: str) -> str:
	path = Path(path_text)
	if path.is_dir():
		return "directory"
	if path.is_file():
		return "file"
	return "missing"


def list_docs(roots: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
	"""Return a compact summary of configured Waterloo data roots."""
	out: list[dict[str, Any]] = []
	for idx, root_data in enumerate(roots):
		root = Path(str(root_data.get("path", ""))).expanduser()
		item = {
			"root_id": f"root-{idx}",
			"label": str(root_data.get("label") or root.name or str(root)),
			"kind": str(root_data.get("kind") or _classify_root(str(root))),
			"path": str(root.resolve()) if root.exists() else str(root),
			"enabled": bool(root_data.get("enabled", True)),
		}
		out.append(item)
	return out
