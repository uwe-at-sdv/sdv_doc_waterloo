r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Public_functions
	scope:
		extension
Contract:
	general:
		|Must| provide the tool set for the Waterloo MCP-server.
Public_classes:
	SearchObjectsFilter, SearchSectionsFilter, SearchTextFilter
Public_functions:
	list_roots, get_root, get_object, get_section, get_subsection, search_objects, search_sections, search_text
Function_overview:
	list_roots:
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
	search_sections:
		Search for stored section and subsection labels with optional structural filters.
	search_text:
		Search for textual content with optional structural filters and compact excerpts.
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import re
from pathlib import Path
from typing import Iterator, Literal, Mapping, cast

from pydantic import BaseModel, ConfigDict

SearchObjectKind_t = Literal["module", "class", "callable", "type", "constant", "variable"]
SearchTextMatchMode_t = Literal["literal"]
SearchTextTermMode_t = Literal["any", "all"]


class SearchObjectsFilter(BaseModel):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
		scope:
			extension
	Contract:
		general:
			|Must| represent the reusable structural filters for object searches in the Waterloo MCP server.
			|Must| allow the caller to omit any field by leaving it |lit|`None`.
			|Must| keep the documented fields stable for existing clients.
		constructor:
			|Must| accept the following fields:
			- root_id: Optional root identifier filter.
			- kind: Optional object kind filter.
			- scope: Optional exact scope filter.
	Notes:
		Purpose:
			This model is part of the public MCP API and is intentionally small so that it can grow additively.
	"""
	model_config = ConfigDict(extra="forbid")

	root_id: str | None = None
	kind: SearchObjectKind_t | None = None
	scope: str | None = None


class SearchSectionsFilter(BaseModel):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
		scope:
			extension
	Contract:
		general:
			|Must| represent the reusable structural filters for section searches in the Waterloo MCP server.
			|Must| allow the caller to omit any field by leaving it |lit|`None`.
			|Must| keep the documented fields stable for existing clients.
		constructor:
			|Must| accept the following fields:
			- root_id: Optional root identifier filter.
			- qid: Optional object QID filter.
			- kind: Optional object kind filter.
			- scope: Optional exact scope filter.
	Notes:
		Purpose:
			This model is part of the public MCP API and is intentionally small so that it can grow additively.
	"""
	model_config = ConfigDict(extra="forbid")

	root_id: str | None = None
	qid: str | None = None
	kind: SearchObjectKind_t | None = None
	scope: str | None = None


class SearchTextFilter(BaseModel):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
		scope:
			extension
	Contract:
		general:
			|Must| represent the reusable structural and matching filters for text searches in the Waterloo MCP server.
			|Must| allow the caller to omit any field by leaving it |lit|`None`.
			|Must| keep the documented fields stable for existing clients.
		constructor:
			|Must| accept the following fields:
			- root_id: Optional root identifier filter.
			- qid: Optional object QID filter.
			- kind: Optional object kind filter.
			- scope: Optional exact scope filter.
			- ignore_case: Optional case-insensitive matching toggle.
			- strip_roles: Optional markup and role stripping toggle.
			- match_mode: Optional literal matching mode.
			- term_mode: Optional any/all term combination mode.
	Notes:
		Purpose:
			This model is part of the public MCP API and is intentionally small so that it can grow additively.
	"""
	model_config = ConfigDict(extra="forbid")

	root_id: str | None = None
	qid: str | None = None
	kind: SearchObjectKind_t | None = None
	scope: str | None = None
	ignore_case: bool = True
	strip_roles: bool = True
	match_mode: SearchTextMatchMode_t = "literal"
	term_mode: SearchTextTermMode_t = "any"


# The Pydantic base classes are only needed for class construction above.
# Remove the imported helper names from the module namespace so the doc
# renderer does not traverse the external Pydantic implementation as if it
# were part of the Waterloo API surface.
del BaseModel, ConfigDict

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


def _root_summary(idx: int, root_data: Mapping[str, object], root_path: Path) -> dict[str, object]:
	return {
		"root_id": _root_id_for_path(str(root_path)),
		"root_index": idx,
		"label": str(root_data.get("label") or root_path.name or str(root_path)),
		"kind": str(root_data.get("kind") or _classify_root(str(root_path))),
		"path": str(root_path),
		"enabled": bool(root_data.get("enabled", True)),
	}


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


def _strip_roles_from_text(text: str) -> str:
	text = re.sub(r"\|([^|]+)\|", r"\1", text)
	text = re.sub(r"`([^`]*)`", r"\1", text)
	return text


def _normalize_search_text(text: str, ignore_case: bool, strip_roles: bool) -> str:
	if strip_roles:
		text = _strip_roles_from_text(text)
	text = " ".join(text.split())
	if ignore_case:
		text = text.casefold()
	return text


def _iter_text_leaves(value: object, path: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], str]]:
	if isinstance(value, str):
		yield path, value
		return
	if isinstance(value, list):
		text_parts: list[str] = []
		for item in value:
			if isinstance(item, str):
				text_parts.append(item)
			elif isinstance(item, Mapping):
				yield from _iter_text_leaves(item, path)
			else:
				text_parts.append(str(item))
		if text_parts:
			yield path, " ".join(text_parts)
		return
	if isinstance(value, Mapping):
		for key, child in value.items():
			yield from _iter_text_leaves(child, path + (str(key),))


def _search_excerpt_source(text: str, strip_roles: bool) -> str:
	return _strip_roles_from_text(text) if strip_roles else text


def _find_term_hits(source: str, terms: list[str], ignore_case: bool) -> list[tuple[int, int]]:
	haystack = source.casefold() if ignore_case else source
	hits: list[tuple[int, int]] = []
	for term in terms:
		needle = _strip_roles_from_text(term).strip()
		if not needle:
			continue
		needle_cmp = needle.casefold() if ignore_case else needle
		pos = haystack.find(needle_cmp)
		if pos >= 0:
			hits.append((pos, len(needle_cmp)))
	return hits


def _trim_excerpt(excerpt: str, max_chars: int = 240) -> str:
	excerpt = " ".join(excerpt.split())
	if len(excerpt) <= max_chars:
		return excerpt
	cut = max_chars - 1
	return f"{excerpt[:cut].rstrip()}…"


def _make_excerpt(text: str, terms: list[str], ignore_case: bool, strip_roles: bool, term_mode: str) -> str:
	source = _search_excerpt_source(text, strip_roles=strip_roles)
	if not source:
		return ""
	hits = _find_term_hits(source, terms, ignore_case=ignore_case)
	if not hits:
		return _trim_excerpt(source[:240])
	start_pos = min(pos for pos, _ in hits)
	end_pos = max(pos + length for pos, length in hits)
	if term_mode == "any":
		end_pos = max(end_pos, start_pos + 60)
	line_start = source.rfind("\n", 0, start_pos)
	line_start = 0 if line_start < 0 else line_start + 1
	line_end = source.find("\n", end_pos)
	line_end = len(source) if line_end < 0 else line_end
	excerpt = source[line_start:line_end].strip()
	truncated_before = line_start > 0
	truncated_after = line_end < len(source)
	if len(" ".join(excerpt.split())) < 30 or len(excerpt) > 280:
		window_start = max(0, start_pos - 80)
		window_end = min(len(source), max(end_pos + 80, start_pos + 180))
		excerpt = source[window_start:window_end].strip()
		truncated_before = window_start > 0
		truncated_after = window_end < len(source)
		excerpt = _trim_excerpt(excerpt)
	else:
		excerpt = _trim_excerpt(excerpt)
	if truncated_before:
		excerpt = f"... {excerpt}"
	if truncated_after:
		excerpt = f"{excerpt} ..."
	return excerpt


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


def list_roots(roots: list[Mapping[str, object]]) -> list[dict[str, object]]:
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
		out.append(_root_summary(idx, root_data, root))
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
	return {**_root_summary(idx, root_data, root_path), "document": document}


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
	return {**_root_summary(idx, root_data, root_path), "qid": qid, "object": object_record}


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
	return {**_root_summary(idx, root_data, root_path), "qid": qid, "section": section, "section_value": section_value}


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
		**_root_summary(idx, root_data, root_path),
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
	for idx, root_data in enumerate(roots):
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


def search_sections(
	expression: str,
	roots: list[Mapping[str, object]],
	filter: SearchSectionsFilter | None = None,
) -> list[dict[str, object]]:
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
			|Must| search configured Waterloo roots for stored section and subsection labels matching the given expression and optional structural filters, and return compact result records.
			|Must| treat wildcard expressions as segment-aware matches over section and subsection labels.
	Parameters:
		expression:
			The search expression. Wildcards are allowed.
		filter:
			Optional structural filters such as root ID, QID, kind, and scope.
		roots:
			The list of configured root entries.
	Returns:
		A list of dictionaries describing matching section or subsection labels together with their object and root location.
	Raises:
	"""
	expression = expression.strip()
	if not expression:
		return []
	root_id_filter = filter.root_id if filter is not None else None
	qid_filter = filter.qid if filter is not None else None
	kind_filter = filter.kind if filter is not None else None
	scope_filter = filter.scope if filter is not None else None
	matches: list[dict[str, object]] = []
	for idx, root_data in enumerate(roots):
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
			if qid_filter is not None and not _matches_expression(str(qid), qid_filter):
				continue
			if use_scope_filter and scope_filter is not None and scope_filter not in _object_scopes(object_record):
				continue
			doc = object_record.get("doc", {})
			if not isinstance(doc, Mapping):
				continue
			root_summary = _root_summary(idx, root_data, root_path)
			for section_name, section_value in doc.items():
				if _matches_expression(str(section_name), expression):
					matches.append(
						{
							**root_summary,
							"qid": str(qid),
							"object_kind": kind,
							"section": str(section_name),
							"subsection": None,
							"match_kind": "section",
						}
					)
				if isinstance(section_value, Mapping):
					for subsection_name, subsection_value in section_value.items():
						if _matches_expression(str(subsection_name), expression):
							matches.append(
								{
									**root_summary,
									"qid": str(qid),
									"object_kind": kind,
									"section": str(section_name),
									"subsection": str(subsection_name),
									"match_kind": "subsection",
								}
							)
	return matches


def search_text(
	terms: list[str],
	roots: list[Mapping[str, object]],
	filter: SearchTextFilter | None = None,
) -> list[dict[str, object]]:
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
			|Must| search configured Waterloo roots for textual content matching the given search terms and optional structural filters, and return compact result records with excerpts.
			|Must| treat the search terms as a list so that clients can fan out over multiple terms without inventing a mini query language.
			|Must| keep the first implementation exact and literal while still honoring the explicit term-mode and matching-mode fields in the filter object.
	Parameters:
		terms:
			The search terms. Each term is treated literally in the first implementation.
		filter:
			Optional structural and matching filters such as root ID, QID, kind, scope, case folding, role stripping, and term mode.
		roots:
			The list of configured root entries.
	Returns:
		A list of dictionaries describing matching text locations together with their object and root location, plus a compact excerpt.
	Raises:
	"""
	terms = [str(term).strip() for term in terms if str(term).strip()]
	if not terms:
		return []
	root_id_filter = filter.root_id if filter is not None else None
	qid_filter = filter.qid if filter is not None else None
	kind_filter = filter.kind if filter is not None else None
	scope_filter = filter.scope if filter is not None else None
	ignore_case = filter.ignore_case if filter is not None else True
	strip_roles = filter.strip_roles if filter is not None else True
	term_mode = filter.term_mode if filter is not None else "any"
	normalized_terms = [
		_normalize_search_text(term, ignore_case=ignore_case, strip_roles=strip_roles)
		for term in terms
	]
	matches: list[dict[str, object]] = []
	seen: set[tuple[object, ...]] = set()
	for idx, root_data in enumerate(roots):
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
			qid_text = str(qid)
			kind = _object_kind(document, qid_text, object_record)
			if kind_filter is not None and kind != kind_filter:
				continue
			if qid_filter is not None and not _matches_expression(qid_text, qid_filter):
				continue
			if use_scope_filter and scope_filter is not None and scope_filter not in _object_scopes(object_record):
				continue
			doc = object_record.get("doc", {})
			if not isinstance(doc, Mapping):
				continue
			root_summary = _root_summary(idx, root_data, root_path)
			for section_path, leaf_text in _iter_text_leaves(doc):
				if not leaf_text:
					continue
				normalized_leaf = _normalize_search_text(leaf_text, ignore_case=ignore_case, strip_roles=strip_roles)
				if not normalized_leaf:
					continue
				if term_mode == "all":
					if not all(term in normalized_leaf for term in normalized_terms):
						continue
				else:
					if not any(term in normalized_leaf for term in normalized_terms):
						continue
				section = section_path[0] if section_path else ""
				subsection = "/".join(section_path[1:]) if len(section_path) > 1 else None
				matches.append(
					{
						**root_summary,
						"qid": qid_text,
						"object_kind": kind,
						"section": section,
						"subsection": subsection,
						"excerpt": _make_excerpt(leaf_text, terms, ignore_case=ignore_case, strip_roles=strip_roles, term_mode=term_mode),
					}
				)
	deduped: list[dict[str, object]] = []
	for match in matches:
		key = (
			match.get("root_id"),
			match.get("qid"),
			match.get("object_kind"),
			match.get("section"),
			match.get("subsection"),
			match.get("excerpt"),
		)
		if key in seen:
			continue
		seen.add(key)
		deduped.append(match)
	return deduped
