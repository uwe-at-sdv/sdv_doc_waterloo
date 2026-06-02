r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Public_functions, Public_types
	scope:
		extension
Contract:
	general:
		|Must| provide the tool set for the Waterloo MCP-server.
Public_classes:
	ReferenceRecord, SearchObjectsFilter, SearchSectionsFilter, SearchTextFilter
Public_functions:
	list_roots, get_root, get_object, get_section, get_subsection,
	get_references, search_objects, search_sections, search_text, gen_docstring
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
	get_references:
		Return the structured incoming See_also references for one object using a reverse lookup map.
	search_objects:
		Search for object QIDs with optional structural filters and return stable triples.
	search_sections:
		Search for stored section and subsection labels with optional structural filters.
	search_text:
		Search for textual content with optional structural filters and compact excerpts.
	gen_docstring:
		Generate a Waterloo docstring template for a given profile and return a
		docstring text together with a JSON placeholder snippet.
Public_types:
	SearchObjectKind_t:
		The kind of object to search for, such as module, class, callable, type, constant, or variable.
	SearchTextMatchMode_t:
		The mode of matching text search terms. Currently only literal matching is supported.
	SearchTextTermMode_t:
		The mode of combining multiple search terms in text search. Can be |value|`any` or |value|`all`.
	DocstringProfile_t:
		The profile to target when generating a docstring template, one of |value|`module`, |value|`class`, |value|`function`, or |value|`method`.
	DocstringMode_t:
		The mode of the docstring template, either |value|`minimal` or |value|`full`.
	DocstringIndentMode_t:
		The indentation mode for generated docstrings, either |value|`tab` or |value|`spc4`.
	DocstringJsonMode_t:
		The JSON output mode for generated docstrings, either |value|`full` or |value|`doc_only`.
"""

from __future__ import annotations

import fnmatch
import ast
import hashlib
import json
import re
from pathlib import Path
# Note that we don't need to import Any here.
from typing import Dict, Iterator, List, Literal, Mapping, cast, TypeAlias, Union

from pydantic import BaseModel, ConfigDict
from sdv.doc.waterloo import docitem_genutil as genutil

#===== Type Checking ==========================================#
# Gemini says nope, but I don't see the problem here, as long as
# mypy is happy and the actual runtime values are correct.
# The whole point of defining WtrlJsonNode_t is to have a
# well-defined type for the JSON data we load, even if we can't
# enforce it at runtime without extra validation. So let's keep
# it as is and let the callers handle the type appropriately.
# We got rid of a lot of plain objects in the API and replaced
# them with well-defined Pydantic models, so the places where we
# still have to use a generic JSON node type should be limited and manageable.
WtrlJsonNode_t: TypeAlias = Dict[str, "WtrlJsonNode_t"] | List["WtrlJsonNode_t"] | str | int | float | bool | None

SearchObjectKind_t = Literal["module", "class", "callable", "type", "constant", "variable"]
SearchTextMatchMode_t = Literal["literal"]
SearchTextTermMode_t = Literal["any", "all"]
DocstringProfile_t = Literal["module", "class", "function", "method"]
DocstringMode_t = Literal["minimal", "full"]
DocstringIndentMode_t = Literal["tab", "spc4"]
DocstringJsonMode_t = Literal["full", "doc_only"]
#=============================================================#

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


class ReferenceRecord(BaseModel):
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
			|Must| represent one incoming structured See_also reference in the Waterloo MCP server.
			|Must| keep the record compact and stable so that lookup results can be reused directly by MCP clients.
		constructor:
			|Must| accept the following fields:
			- source_root_id: stable root identifier of the object that holds the See_also link.
			- source_qid: fully qualified identifier of the source object.
			- source_profile: Waterloo docstring profile of the source object.
			- is_normative: whether the See_also link was recorded in a normative section.
	Notes:
		Purpose:
			This record is the canonical Waterloo representation for reverse See_also lookups.
	"""
	model_config = ConfigDict(extra="forbid")

	source_root_id: str
	source_qid: str
	source_profile: DocstringProfile_t
	is_normative: bool


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

# Of course we could just cast the loaded JSON to the expected type,
# but that would be unsafe and defeat the purpose of having a
# well-defined JSON node type in the first place. So we keep
# the return type of this function as the generic WtrlJsonNode_t
# and let the callers handle it appropriately.
def _read_json_document(path_text: str) -> WtrlJsonNode_t:
	path = _canonical_root_path(path_text)
	return cast(WtrlJsonNode_t, json.loads(path.read_text(encoding="utf-8")))

def _root_summary(idx: int, root_data: Mapping[str, object], root_path: Path) -> dict[str, WtrlJsonNode_t]:
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


def _load_root_context(root_id: str, roots: list[Mapping[str, object]]) -> tuple[int, Mapping[str, object], Path, dict[str, WtrlJsonNode_t]]:
	idx, root_data = _get_root_record(root_id, roots)
	root_path = _canonical_root_path(str(root_data.get("path", "")))
	document = _read_json_document(str(root_path))
	if not isinstance(document, dict):
		raise ValueError(f"Root document must be a JSON object: {root_id}")
	return idx, root_data, root_path, document


def _get_root_record(root_id: str, roots: list[Mapping[str, object]]) -> tuple[int, Mapping[str, object]]:
	return _find_root_by_id(roots, root_id)


def _find_root_by_id(roots: list[Mapping[str, object]], root_id: str) -> tuple[int, Mapping[str, object]]:
	for idx, root_data in enumerate(roots):
		path_text = str(root_data.get("path", "")).strip()
		if path_text and _root_id_for_path(path_text) == root_id:
			return idx, root_data
	raise ValueError(f"Unknown root_id: {root_id}")


def list_roots(roots: list[Mapping[str, object]]) -> list[dict[str, WtrlJsonNode_t]]:
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
	out: list[dict[str, WtrlJsonNode_t]] = []
	for idx, root_data in enumerate(roots):
		root = _canonical_root_path(str(root_data.get("path", "")))
		out.append(_root_summary(idx, root_data, root))
	return out


def get_root(root_id: str, roots: list[Mapping[str, object]]) -> dict[str, WtrlJsonNode_t]:
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


def get_object(root_id: str, qid: str, roots: list[Mapping[str, object]]) -> dict[str, WtrlJsonNode_t]:
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


def get_section(root_id: str, qid: str, section: str, roots: list[Mapping[str, object]]) -> dict[str, WtrlJsonNode_t]:
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


def get_subsection(root_id: str, qid: str, section: str, subsection: str, roots: list[Mapping[str, object]]) -> dict[str, WtrlJsonNode_t]:
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


def get_references(
	reference_index: Mapping[tuple[str, str], list[ReferenceRecord]],
	root_id: str,
	qid: str,
	normative_only: bool = False,
) -> list[ReferenceRecord]:
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
			|Must| return the structured incoming See_also references for one object from the provided reverse lookup map.
			|Must| treat the lookup as a simple read-only reverse-map access and filter the result when normative_only is requested.
	Parameters:
		reference_index:
			The reverse lookup map built by the server at startup.
		root_id:
			The canonical root identifier of the object whose incoming references should be returned.
		qid:
			The fully qualified identifier of the object whose incoming references should be returned.
		normative_only:
			Whether to keep only references recorded from a normative See_also section.
	Returns:
		A list of incoming structured See_also reference records.
	Raises:
	"""
	records = reference_index.get((root_id, qid), [])
	records = [
		record if isinstance(record, ReferenceRecord) else ReferenceRecord.model_validate(record)
		for record in records
	]
	if normative_only:
		records = [record for record in records if record.is_normative]
	return records


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
) -> list[dict[str, WtrlJsonNode_t]]:
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
	matches: list[dict[str, WtrlJsonNode_t]] = []
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
) -> list[dict[str, WtrlJsonNode_t]]:
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
	matches: list[dict[str, WtrlJsonNode_t]] = []
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
	deduped: list[dict[str, WtrlJsonNode_t]] = []
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


def _unparse_expr(node: ast.AST | None) -> str | None:
	if node is None:
		return None
	try:
		text = ast.unparse(node)
	except Exception:
		return None
	text = text.strip()
	return text or None


def _signature_parameters_from_function_node(
	node: ast.FunctionDef | ast.AsyncFunctionDef,
	*,
	drop_first_receiver: bool = False,
) -> list[dict[str, WtrlJsonNode_t]]:
	all_pos = list(node.args.posonlyargs) + list(node.args.args)
	default_start = len(all_pos) - len(node.args.defaults)
	parameters: list[dict[str, WtrlJsonNode_t]] = []

	for index, arg in enumerate(node.args.posonlyargs):
		default_idx = index - default_start
		parameters.append(
			{
				"name": arg.arg,
				"kind": "POSITIONAL_ONLY",
				"annotation": _unparse_expr(arg.annotation),
				"default": _unparse_expr(node.args.defaults[default_idx]) if default_idx >= 0 else None,
			}
		)
	for index, arg in enumerate(node.args.args, start=len(node.args.posonlyargs)):
		default_idx = index - default_start
		parameters.append(
			{
				"name": arg.arg,
				"kind": "POSITIONAL_OR_KEYWORD",
				"annotation": _unparse_expr(arg.annotation),
				"default": _unparse_expr(node.args.defaults[default_idx]) if default_idx >= 0 else None,
			}
		)
	if node.args.vararg is not None:
		parameters.append(
			{
				"name": node.args.vararg.arg,
				"kind": "VAR_POSITIONAL",
				"annotation": _unparse_expr(node.args.vararg.annotation),
				"default": None,
			}
		)
	for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults, strict=False):
		parameters.append(
			{
				"name": arg.arg,
				"kind": "KEYWORD_ONLY",
				"annotation": _unparse_expr(arg.annotation),
				"default": _unparse_expr(default),
			}
		)
	if node.args.kwarg is not None:
		parameters.append(
			{
				"name": node.args.kwarg.arg,
				"kind": "VAR_KEYWORD",
				"annotation": _unparse_expr(node.args.kwarg.annotation),
				"default": None,
			}
		)
	if drop_first_receiver and parameters and parameters[0]["name"] in {"self", "cls", "mcls"}:
		parameters = parameters[1:]
	return parameters


def _signature_parameter_names_from_node(
	node: ast.FunctionDef | ast.AsyncFunctionDef,
	*,
	drop_first_receiver: bool = False,
) -> list[str]:
	return [
		str(item["name"])
		for item in _signature_parameters_from_function_node(node, drop_first_receiver=drop_first_receiver)
	]


def _signature_json_from_node(
	profile: DocstringProfile_t,
	signature: str | None,
	node: ast.AST | None,
) -> dict[str, WtrlJsonNode_t] | None:
	if profile == "module":
		return None
	if isinstance(node, ast.ClassDef):
		return {
			"text": "object.__init__(self, /, *args, **kwargs)",
			"parameters": [
				{
					"name": "args",
					"kind": "VAR_POSITIONAL",
					"annotation": None,
					"default": None,
				},
				{
					"name": "kwargs",
					"kind": "VAR_KEYWORD",
					"annotation": None,
					"default": None,
				},
			],
			"returns": None,
		}
	if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
		kind = "method" if profile == "method" else "function"
		return {
			"text": _signature_text_from_node(profile, signature, node) or kind,
			"parameters": cast(WtrlJsonNode_t, _signature_parameters_from_function_node(node, drop_first_receiver=(profile == "method"))),
			"returns": _unparse_expr(node.returns),
		}
	return None


def _signature_text_from_node(profile: DocstringProfile_t, signature: str | None, node: ast.AST | None) -> str | None:
	if isinstance(node, ast.ClassDef):
		try:
			rendered = ast.unparse(node)
		except Exception:
			rendered = signature.strip() if signature else node.name
		rendered = re.sub(r":\s*pass\s*\Z", "", rendered.strip())
		rendered = rendered.removeprefix("class ").strip()
		return rendered or node.name
	if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
		try:
			rendered = ast.unparse(node)
		except Exception:
			rendered = signature.strip() if signature else node.name
		rendered = rendered.strip()
		rendered = rendered.removeprefix("async def ").removeprefix("def ").strip()
		rendered = re.sub(r":\s*pass\s*\Z", "", rendered).strip()
		return rendered or node.name
	return signature.strip() if signature else None


def _doc_snippet_for(profile: DocstringProfile_t, node: ast.AST | None, mode: DocstringMode_t) -> dict[str, WtrlJsonNode_t]:
	if profile == "module":
		if mode == "minimal":
			return {
				"Preamble": {
					"profile": "module",
					"normative_sections": ["Contract"],
				},
				"Contract": {
					"general": [],
				},
			}
		return {
			"Preamble": {
				"profile": "module",
				"normative_sections": [
					"Definitions",
					"Contract",
					"Public_classes",
					"Public_functions",
					"Public_types",
					"Public_variables",
					"Public_constants",
					"See_also",
				],
				"scope": ["public"],
			},
			"Definitions": {
				"ExampleTerm": {
					"variations": [],
					"text": ["..."],
				},
			},
			"Terminology": {
				"Example term": ["..."],
			},
			"Contract": {
				"general": ["MUST define the externally visible behavior of this module."],
			},
			"Description": [],
			"Notes": {
				"General note": ["..."],
			},
			"Public_classes": [],
			"Class_overview": {},
			"Public_functions": [],
			"Function_overview": {},
			"Public_types": {},
			"Public_variables": {},
			"Public_constants": {},
			"See_also": [],
		}
	if profile == "class":
		if mode == "minimal":
			return {
				"Preamble": {
					"profile": "class",
					"normative_sections": ["Contract"],
				},
				"Contract": {
					"general": [],
					"constructor": [],
				},
			}
		return {
			"Preamble": {
				"profile": "class",
				"normative_sections": [
					"Definitions",
					"Contract",
					"Derived_from",
					"Public_classes",
					"Public_methods",
					"Public_types",
					"Public_variables",
					"Public_constants",
					"Factory",
					"See_also",
				],
				"scope": ["public"],
			},
			"Definitions": {
				"ExampleTerm": {
					"variations": [],
					"text": ["..."],
				},
			},
			"Terminology": {
				"Example term": ["..."],
			},
			"Contract": {
				"general": ["MUST define the externally visible behavior of this class."],
				"constructor": ["MUST define construction requirements and guarantees."],
				"traits": [],
			},
			"Description": ["..."],
			"Derived_from": [],
			"Notes": {
				"General note": ["..."],
			},
			"Public_classes": [],
			"Class_overview": {},
			"Public_methods": [],
			"Method_overview": {},
			"Public_types": {},
			"Public_variables": {},
			"Public_constants": {},
			"Factory": {},
			"See_also": [],
		}
	if profile in {"function", "method"}:
		parameter_names = _signature_parameter_names_from_node(
			cast(ast.FunctionDef | ast.AsyncFunctionDef, node),
			drop_first_receiver=(profile == "method"),
		)
		if mode == "minimal":
			return {
				"Preamble": {
					"profile": profile,
					"normative_sections": ["Contract", "Parameters", "Returns", "Raises"],
				},
				"Contract": {
					"general": [],
				},
				"Parameters": {name: ["..."] for name in parameter_names},
				"Returns": [],
				"Raises": {},
			}
		return {
			"Preamble": {
				"profile": profile,
				"normative_sections": [
					"Definitions",
					"Contract",
					"Parameters",
					"Returns",
					"Raises",
					"See_also",
				],
				"status": "stable",
				"scope": ["public"],
			},
			"Definitions": {
				"ExampleTerm": {
					"variations": [],
					"text": ["..."],
				},
			},
			"Terminology": {
				"Example term": ["..."],
			},
			"Contract": {
				"general": [
					"MUST define the externally visible behavior of this callable."
					if profile == "function"
					else "MUST define the externally visible behavior of this method."
				],
				"requires": ["MUST define preconditions for valid input."],
				"ensures": ["MUST define postconditions for successful execution."],
				"invariants": ["MUST preserve all documented invariants across valid calls."],
			},
			"Description": ["..."],
			"Parameters": {name: ["..."] for name in parameter_names},
			"Returns": ["MUST return ..."],
			"Raises": {"BaseException": ["MUST raise if..."]},
			"Notes": {
				"General note": ["..."],
			},
			"See_also": [],
		}
	return {}


def gen_docstring(
	profile: DocstringProfile_t,
	signature: str | None = None,
	mode: DocstringMode_t = "minimal",
	indent_mode: DocstringIndentMode_t = "tab",
	json_mode: DocstringJsonMode_t = "full",
) -> dict[str, WtrlJsonNode_t]:
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
			|Must| generate a Waterloo docstring template for the requested profile.
			|Must| return the generated docstring together with a JSON snippet that represents the docstring structure and content.
			|Must| keep the JSON snippet compatible with the existing Waterloo JSON document shape in later phases.
	Parameters:
		profile:
			Target Waterloo docstring profile.
		signature:
			Optional textual signature for non-module profiles.
		mode:
			Template mode, either ``minimal`` or ``full``.
		indent_mode:
			Indentation mode for the returned docstring text, either ``tab`` or ``spc4``.
		json_mode:
			JSON output mode, either ``full`` or ``doc_only``.
	Returns:
		A dictionary with the generated ``docstring`` text and a ``json_snippet`` that represents the docstring structure and content.
	Raises:
		ValueError:
			|May| be raised if the profile requires a signature and none is given.
	"""
	if mode not in {"minimal", "full"}:
		raise ValueError(f"unknown docstring mode: {mode}")
	if json_mode not in {"full", "doc_only"}:
		raise ValueError(f"unknown JSON mode: {json_mode}")
	if profile not in {"module", "class", "function", "method"}:
		raise ValueError(f"unsupported docstring profile: {profile}")
	if profile == "module":
		node = genutil.parse_signature_fragment("module", signature or "")
	elif signature is None or not signature.strip():
		raise ValueError(f"signature is required for profile {profile}")
	else:
		node = genutil.parse_signature_fragment(profile, signature)
	if mode == "minimal":
		docstring = genutil.generate_minimal_docstring_from_node(profile, node)
	else:
		docstring = genutil.generate_full_docstring_from_node(profile, node)
	if indent_mode == "spc4":
		docstring = docstring.replace("\t", "    ")
	doc_snippet = _doc_snippet_for(profile, node, mode)
	if json_mode == "doc_only":
		json_snippet: dict[str, WtrlJsonNode_t] = doc_snippet
	else:
		signature_json = _signature_json_from_node(profile, signature, node)
		object_entry: dict[str, WtrlJsonNode_t] = {"doc": doc_snippet}
		if signature_json is not None:
			object_entry["signature"] = signature_json
		json_snippet = {"__WTRL_OBJECTS__": {"generated_docstring_template": object_entry}}
	return {
		"profile": profile,
		"signature": signature,
		"mode": mode,
		"indent_mode": indent_mode,
		"json_mode": json_mode,
		"docstring": docstring,
		"json_snippet": json_snippet,
	}
