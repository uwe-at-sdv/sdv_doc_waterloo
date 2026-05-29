r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
	scope:
		extension
Contract:
	general:
		|must| provide the tool set for the Waterloo MCP-server.
Public_functions:
	list_docs, get_root, get_object, get_section
Function_overview:
	list_docs:
		List the configured Waterloo roots with stable identifiers.
	get_root:
		Resolve one configured root by its stable identifier and return the loaded JSON document.
	get_object:
		Resolve one object by QID inside one configured root and return the loaded object record.
	get_section:
		Resolve one named section of one object inside one configured root and return the stored section value.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

def _classify_root(path_text: str) -> str:
	path = Path(path_text)
	if path.is_dir():
		return "directory"
	if path.is_file():
		return "file"
	return "missing"


def _canonical_root_path(path_text: str) -> Path:
	return Path(path_text).expanduser().resolve()


def _root_id_for_path(path_text: str) -> str:
	canonical_path = _canonical_root_path(path_text)
	digest = hashlib.blake2s(str(canonical_path).encode("utf-8"), digest_size=6).hexdigest()
	return f"root:{digest}"


def _read_json_document(path_text: str) -> Any:
	path = _canonical_root_path(path_text)
	return json.loads(path.read_text(encoding="utf-8"))


def _get_root_record(root_id: str, roots: list[Mapping[str, Any]]) -> tuple[int, Mapping[str, Any]]:
	return _find_root_by_id(roots, root_id)


def _find_root_by_id(roots: list[Mapping[str, Any]], root_id: str) -> tuple[int, Mapping[str, Any]]:
	for idx, root_data in enumerate(roots):
		path_text = str(root_data.get("path", "")).strip()
		if path_text and _root_id_for_path(path_text) == root_id:
			return idx, root_data
	raise ValueError(f"Unknown root_id: {root_id}")


def list_docs(roots: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| extract attributes from the provided root entries (as given in the configuration), derive a stable root identifier from the canonical absolute path of each root locator, and return a list of dictionaries with specific keys.
			|Must| define the |attr|`root_id` of one root as a short stable hash of that canonical absolute path, independent of labels and configuration order.
	Parameters:
		roots:
			The list of root configurations to process.
	Returns:
		A list of dictionaries, each representing a root document with its attributes.
	Raises:
	"""
	out: list[dict[str, Any]] = []
	for idx, root_data in enumerate(roots):
		root = _canonical_root_path(str(root_data.get("path", "")))
		item = {
			"root_id": _root_id_for_path(str(root)),
			"label": str(root_data.get("label") or root.name or str(root)),
			"kind": str(root_data.get("kind") or _classify_root(str(root))),
			"path": str(root),
			"enabled": bool(root_data.get("enabled", True)),
		}
		out.append(item)
	return out


def get_root(root_id: str, roots: list[Mapping[str, Any]]) -> dict[str, Any]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| resolve a configured root by its canonical root identifier and return the root metadata together with the loaded JSON document.
	Parameters:
		root_id:
			The canonical root identifier derived from the canonical absolute root path.
		roots:
			The list of configured root entries.
	Returns:
		A dictionary describing the root and containing the parsed JSON document.
	Raises:
		ValueError:
			|May| raise if the root identifier is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	"""
	idx, root_data = _get_root_record(root_id, roots)
	root_path = _canonical_root_path(str(root_data.get("path", "")))
	return {
		"root_id": _root_id_for_path(str(root_path)),
		"root_index": idx,
		"label": str(root_data.get("label") or root_path.name or str(root_path)),
		"kind": str(root_data.get("kind") or _classify_root(str(root_path))),
		"path": str(root_path),
		"enabled": bool(root_data.get("enabled", True)),
		"document": _read_json_document(str(root_path)),
	}


def get_object(root_id: str, qid: str, roots: list[Mapping[str, Any]]) -> dict[str, Any]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| resolve one QID inside one configured root and return the stored object record together with the root metadata.
	Parameters:
		root_id:
			The canonical root identifier derived from the canonical absolute root path.
		qid:
			The fully qualified identifier of the requested object inside the loaded Waterloo JSON document.
		roots:
			The list of configured root entries.
	Returns:
		A dictionary describing the root, the requested QID, and the stored object record.
	Raises:
		ValueError:
			|May| raise if the root identifier or QID is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	"""
	idx, root_data = _get_root_record(root_id, roots)
	root_path = _canonical_root_path(str(root_data.get("path", "")))
	document = _read_json_document(str(root_path))
	objects = document.get("__WTRL_OBJECTS__", {})
	if not isinstance(objects, Mapping):
		raise ValueError(f"Unknown qid: {qid}")
	object_record = objects.get(qid)
	if object_record is None:
		raise ValueError(f"Unknown qid: {qid}")
	return {
		"root_id": _root_id_for_path(str(root_path)),
		"root_index": idx,
		"label": str(root_data.get("label") or root_path.name or str(root_path)),
		"kind": str(root_data.get("kind") or _classify_root(str(root_path))),
		"path": str(root_path),
		"enabled": bool(root_data.get("enabled", True)),
		"qid": qid,
		"object": object_record,
	}


def get_section(root_id: str, qid: str, section: str, roots: list[Mapping[str, Any]]) -> dict[str, Any]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| resolve one named section of one QID inside one configured root and return the stored section value together with the relevant metadata.
	Parameters:
		root_id:
			The canonical root identifier derived from the canonical absolute root path.
		qid:
			The fully qualified identifier of the requested object inside the loaded Waterloo JSON document.
		section:
			The name of the requested stored section, for example ``Contract`` or ``Public_functions``.
		roots:
			The list of configured root entries.
	Returns:
		A dictionary describing the root, the requested QID, the requested section, and the stored section value.
	Raises:
		ValueError:
			|May| raise if the root identifier, QID, or section name is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	"""
	idx, root_data = _get_root_record(root_id, roots)
	root_path = _canonical_root_path(str(root_data.get("path", "")))
	document = _read_json_document(str(root_path))
	objects = document.get("__WTRL_OBJECTS__", {})
	if not isinstance(objects, Mapping):
		raise ValueError(f"Unknown qid: {qid}")
	object_record = objects.get(qid)
	if not isinstance(object_record, Mapping):
		raise ValueError(f"Unknown qid: {qid}")
	doc = object_record.get("doc", {})
	if not isinstance(doc, Mapping):
		raise ValueError(f"Unknown section: {section}")
	section_value = doc.get(section)
	if section_value is None:
		raise ValueError(f"Unknown section: {section}")
	return {
		"root_id": _root_id_for_path(str(root_path)),
		"root_index": idx,
		"label": str(root_data.get("label") or root_path.name or str(root_path)),
		"kind": str(root_data.get("kind") or _classify_root(str(root_path))),
		"path": str(root_path),
		"enabled": bool(root_data.get("enabled", True)),
		"qid": qid,
		"section": section,
		"section_value": section_value,
	}
