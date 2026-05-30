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
		|Must| provide the tool set for the Waterloo MCP-server.
Public_functions:
	list_docs, get_root, get_object, get_section, get_subsection, search_objects
Function_overview:
	list_docs:
		List the configured Waterloo roots with stable identifiers.
	get_root:
		Resolve one configured root by its stable identifier and return the loaded JSON document.
	get_object:
		Resolve one object by QID inside one configured root and return the loaded object record.
	get_section:
		Resolve one named section of one object inside one configured root and return the stored section value.
	get_subsection:
		Resolve one named subsection of one section of one object inside one configured root and return the stored subsection value.
	search_objects:
		Search for object QIDs with optional structural filters and return stable triples.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
from pathlib import Path
from typing import Literal, Mapping, cast

from pydantic import BaseModel, ConfigDict

SearchObjectKind_t = Literal["module", "class", "callable", "type", "constant", "variable"]


class SearchObjectsFilter(BaseModel):
	model_config = ConfigDict(extra="forbid")

	root_id: str | None = None
	kind: SearchObjectKind_t | None = None
	scope: str | None = None

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


def _read_json_document(path_text: str) -> object:
	path = _canonical_root_path(path_text)
	return json.loads(path.read_text(encoding="utf-8"))


def _object_kind_from_toc(document: Mapping[str, object], qid: str) -> str | None:
	toc_kind_map = {
		"module": "__WTRL_TOC_MODULES__",
		"class": "__WTRL_TOC_CLASSES__",
		"callable": "__WTRL_TOC_CALLABLES__",
		"type": "__WTRL_TOC_TYPES__",
		"constant": "__WTRL_TOC_CONSTANTS__",
		"variable": "__WTRL_TOC_VARIABLES__",
	}
	for kind, toc_key in toc_kind_map.items():
		toc = document.get(toc_key, {})
		if isinstance(toc, Mapping) and qid in toc:
			return kind
	return None


def _object_kind_from_profile(object_record: Mapping[str, object]) -> str:
	doc = object_record.get("doc", {})
	if isinstance(doc, Mapping):
		preamble = doc.get("Preamble", {})
		if isinstance(preamble, Mapping):
			profile = str(preamble.get("profile", "")).strip().lower()
			if profile in {"module", "class"}:
				return profile
			if profile in {"function", "method", "inherited_method"}:
				return "callable"
	return "callable"


def _object_kind(document: Mapping[str, object], qid: str, object_record: Mapping[str, object]) -> str:
	return _object_kind_from_toc(document, qid) or _object_kind_from_profile(object_record)


def _object_scopes(object_record: Mapping[str, object]) -> set[str]:
	doc = object_record.get("doc", {})
	if not isinstance(doc, Mapping):
		return set()
	preamble = doc.get("Preamble", {})
	if not isinstance(preamble, Mapping):
		return set()
	scope_data = preamble.get("scope", [])
	if isinstance(scope_data, str):
		return {scope_data}
	if isinstance(scope_data, list):
		return {str(item) for item in scope_data if str(item).strip()}
	return set()


def _root_scope_names(document: Mapping[str, object]) -> set[str]:
	scopes = document.get("__WTRL_SCOPES__", {})
	if not isinstance(scopes, Mapping):
		return set()
	return {str(name) for name in scopes.keys()}


def _matches_expression(qid: str, expression: str) -> bool:
	if any(ch in expression for ch in "*?[]"):
		if fnmatch.fnmatchcase(qid, expression):
			return True
		tail = qid.split(".")[-1]
		if fnmatch.fnmatchcase(tail, expression):
			return True
		return any(fnmatch.fnmatchcase(part, expression) for part in qid.split("."))
	if qid == expression:
		return True
	if qid.endswith(f".{expression}"):
		return True
	return qid.split(".")[-1] == expression


def _load_root_context(root_id: str, roots: list[Mapping[str, object]]) -> tuple[int, Mapping[str, object], Path, dict[str, object]]:
	idx, root_data = _get_root_record(root_id, roots)
	root_path = _canonical_root_path(str(root_data.get("path", "")))
	document = _read_json_document(str(root_path))
	if not isinstance(document, dict):
		raise ValueError(f"Root document must be a JSON object: {root_id}")
	return idx, root_data, root_path, cast(dict[str, object], document)


def _get_root_record(root_id: str, roots: list[Mapping[str, object]]) -> tuple[int, Mapping[str, object]]:
	return _find_root_by_id(roots, root_id)


def _find_root_by_id(roots: list[Mapping[str, object]], root_id: str) -> tuple[int, Mapping[str, object]]:
	for idx, root_data in enumerate(roots):
		path_text = str(root_data.get("path", "")).strip()
		if path_text and _root_id_for_path(path_text) == root_id:
			return idx, root_data
	raise ValueError(f"Unknown root_id: {root_id}")


def list_docs(roots: list[Mapping[str, object]]) -> list[dict[str, object]]:
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
	out: list[dict[str, object]] = []
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


def get_root(root_id: str, roots: list[Mapping[str, object]]) -> dict[str, object]:
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
	idx, root_data, root_path, document = _load_root_context(root_id, roots)
	return {
		"root_id": _root_id_for_path(str(root_path)),
		"root_index": idx,
		"label": str(root_data.get("label") or root_path.name or str(root_path)),
		"kind": str(root_data.get("kind") or _classify_root(str(root_path))),
		"path": str(root_path),
		"enabled": bool(root_data.get("enabled", True)),
		"document": document,
	}


def get_object(root_id: str, qid: str, roots: list[Mapping[str, object]]) -> dict[str, object]:
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
	idx, root_data, root_path, document = _load_root_context(root_id, roots)
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


def get_section(root_id: str, qid: str, section: str, roots: list[Mapping[str, object]]) -> dict[str, object]:
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
	idx, root_data, root_path, document = _load_root_context(root_id, roots)
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


def get_subsection(root_id: str, qid: str, section: str, subsection: str, roots: list[Mapping[str, object]]) -> dict[str, object]:
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
			|Must| resolve one named subsection of one named section of one QID inside one configured root and return the stored subsection value together with the relevant metadata.
	Parameters:
		root_id:
			The canonical root identifier derived from the canonical absolute root path.
		qid:
			The fully qualified identifier of the requested object inside the loaded Waterloo JSON document.
		section:
			The name of the requested stored section.
		subsection:
			The name of the requested subsection inside the selected section.
		roots:
			The list of configured root entries.
	Returns:
		A dictionary describing the root, the requested QID, the requested section, the requested subsection, and the stored subsection value.
	Raises:
		ValueError:
			|May| raise if the root identifier, QID, section name, or subsection name is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	"""
	idx, root_data, root_path, document = _load_root_context(root_id, roots)
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
	if not isinstance(section_value, Mapping):
		raise ValueError(f"Unknown subsection: {subsection}")
	subsection_value = section_value.get(subsection)
	if subsection_value is None:
		raise ValueError(f"Unknown subsection: {subsection}")
	return {
		"root_id": _root_id_for_path(str(root_path)),
		"root_index": idx,
		"label": str(root_data.get("label") or root_path.name or str(root_path)),
		"kind": str(root_data.get("kind") or _classify_root(str(root_path))),
		"path": str(root_path),
		"enabled": bool(root_data.get("enabled", True)),
		"qid": qid,
		"section": section,
		"subsection": subsection,
		"subsection_value": subsection_value,
	}


def search_objects(
	expression: str,
	roots: list[Mapping[str, object]],
	filter: SearchObjectsFilter | None = None,
) -> list[tuple[str, str, str]]:
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
			|Must| search configured Waterloo roots for object QIDs matching the given expression and optional structural filters, and return stable triples of root ID, QID, and kind.
			|Must| treat wildcard expressions as segment-aware matches over the QID, with the last segment being the primary lookup target for simple names.
	Parameters:
		expression:
			The search expression. Wildcards are allowed.
		filter:
			Optional structural filters such as root ID, kind, and scope.
		roots:
			The list of configured root entries.
	Returns:
		A list of triples ``(root_id, qid, kind)`` for matching objects.
	Raises:
	"""
	expression = expression.strip()
	if not expression:
		return []
	root_id_filter = filter.root_id if filter is not None else None
	kind_filter = filter.kind if filter is not None else None
	scope_filter = filter.scope if filter is not None else None
	matches: list[tuple[str, str, str]] = []
	for root_data in roots:
		if not bool(root_data.get("enabled", True)):
			continue
		root_path = _canonical_root_path(str(root_data.get("path", "")))
		current_root_id = _root_id_for_path(str(root_path))
		if root_id_filter is not None and current_root_id != root_id_filter:
			continue
		document = _read_json_document(str(root_path))
		if not isinstance(document, dict):
			continue
		root_scope_names = _root_scope_names(document)
		use_scope_filter = scope_filter is not None and scope_filter in root_scope_names
		objects = document.get("__WTRL_OBJECTS__", {})
		if not isinstance(objects, Mapping):
			continue
		for qid, object_record in objects.items():
			if not isinstance(object_record, Mapping):
				continue
			kind = _object_kind(document, str(qid), object_record)
			if kind_filter is not None and kind != kind_filter:
				continue
			if use_scope_filter and scope_filter is not None and scope_filter not in _object_scopes(object_record):
				continue
			if not _matches_expression(str(qid), expression):
				continue
			matches.append((current_root_id, str(qid), kind))
	return matches
