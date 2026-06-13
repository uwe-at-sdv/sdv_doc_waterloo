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
	ExampleRef, ObjectSummary, ReferenceRecord, RelatedRecord, SearchObjectsFilter, SearchSectionsFilter, SearchTextFilter
Public_functions:
	matches_segment_aware_expression,
	about,
	list_roots, get_root, get_root_metadata, get_object, get_section, get_subsection, list_objects,
	get_references, search_related, get_signature, get_examples, get_example_source,
	search_objects, search_sections, search_text, gen_docstring
Function_overview:
	matches_segment_aware_expression:
		Check whether a candidate name matches a given expression, which can be either a literal match or a glob pattern.
	about:
		Return the bundled Waterloo about topic JSON for the index or one selected topic.
	list_roots:
		[MCP tool] List the configured Waterloo roots with stable identifiers.
	get_root:
		[MCP tool] Resolve one configured root by its stable identifier and return the loaded JSON document.
	get_root_metadata:
		[MCP tool] Resolve one configured root by its stable identifier and return only the compact header metadata block.
	get_object:
		[MCP tool] Resolve one object by QID inside one configured root and return the loaded object record.
	get_section:
		[MCP tool] Resolve one named section of one object inside one configured root and return the stored section value.
	get_subsection:
		[MCP tool] Resolve one named subsection of one section of one object inside one configured root and return the stored subsection value.
	get_references:
		[MCP tool] Return the structured incoming See_also references for one object using a reverse lookup map.
	search_related:
		[MCP tool] Return a compact star-shaped neighborhood around one object using the structured See_also graph.
	get_signature:
		[MCP tool] Return the stored signature block for one object without reconstructing it.
	get_examples:
		[MCP tool] Return example metadata for one object using the structured __WTRL_EXAMPLES__ data.
	get_example_source:
		[MCP tool] Return the source text for one example reference using the structured __WTRL_EXAMPLES__ data.
	search_objects:
		[MCP tool] Search for object QIDs with optional structural filters and return stable triples.
	search_sections:
		[MCP tool] Search for stored section and subsection labels with optional structural filters.
	search_text:
		[MCP tool] Search for textual content with optional structural filters and compact excerpts.
	gen_docstring:
		[MCP tool] Generate a Waterloo docstring template for a given profile and return a
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
import importlib.resources
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Literal, Mapping, cast, TypeAlias, Union

from pydantic import BaseModel, ConfigDict
from sdv.doc.waterloo import docitem_genutil as genutil

#===== Type Checking ==========================================#
# WtrlJsonNode_t captures Waterloo JSON values without recursive forward refs.
WtrlJsonNode_t: TypeAlias = Dict[str, Any] | List[Any] | str | int | float | bool | None

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
			|Must| allow the caller to omit any field by leaving it |None|.
			|Must| keep the documented fields stable for existing clients.
		constructor:
			|Must| accept the following fields:
			- root_id: Optional root identifier filter.
			- kind: Optional object kind filter.
			- scope: Optional exact scope filter.
	Notes:
		Purpose:
			This model is part of the public MCP API and is intentionally small so that it can grow additively.
	See_also:
		search_objects
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
			|Must| allow the caller to omit any field by leaving it |None|.
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
	See_also:
		search_sections
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
			|Must| allow the caller to omit any field by leaving it |None|.
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
	See_also:
		search_text
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
	See_also:
		get_references, search_related
	"""
	model_config = ConfigDict(extra="forbid")

	source_root_id: str
	source_qid: str
	source_profile: DocstringProfile_t
	is_normative: bool


class RelatedRecord(BaseModel):
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
			|Must| represent one direct related-object edge in the Waterloo MCP server.
			|Must| keep the record compact and stable so that star-shaped graph lookups can be reused directly by MCP clients.
		constructor:
			|Must| accept the following fields:
			- related_root_id: stable root identifier of the related object.
			- related_qid: fully qualified identifier of the related object.
			- related_profile: Waterloo docstring profile of the related object.
			- direction: whether the edge points away from the anchor object, back to it, or both after deduplication.
			- relation_kind: the kind of relation represented by the edge.
			- is_normative: whether the relation was recorded in a normative section.
	Notes:
		Purpose:
			This record is the canonical Waterloo representation for the first star-shaped related-object lookup.
	See_also:
		search_related, get_references
	"""
	model_config = ConfigDict(extra="forbid")

	related_root_id: str
	related_qid: str
	related_profile: DocstringProfile_t
	direction: Literal["in", "out", "in_out"]
	relation_kind: Literal["see_also"]
	is_normative: bool


class ExampleRef(BaseModel):
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
			|Must| represent one example reference in the Waterloo MCP server.
			|Must| keep the reference compact and stable so that lookup results can be reused directly by MCP clients.
		constructor:
			|Must| accept the following fields:
			- root_id: stable root identifier of the object that owns the example reference.
			- example_path: canonical path inside __WTRL_EXAMPLES__.
			- title: optional human-readable name.
			- lang: language tag of the example payload.
			- size: raw octet size of the example payload.
	Notes:
		Purpose:
			This record is the canonical Waterloo representation for structured example lookups.
	See_also:
		get_examples, get_example_source
	"""
	model_config = ConfigDict(extra="forbid")

	root_id: str
	example_path: str
	title: str | None = None
	lang: str
	size: int


class ObjectSummary(BaseModel):
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
			|Must| represent one inventory row for one Waterloo object in the MCP server.
			|Must| keep the record compact and stable so that clients can decide quickly whether they need to drill down further.
		constructor:
			|Must| accept the following fields:
			- qid: fully qualified object identifier.
			- profile: Waterloo docstring profile if the object has a docstring, otherwise |None|.
			- kind: always meaningful Waterloo object kind.
			- scope: canonical Waterloo scope name, defaulting to |value|`public`.
			- status: Waterloo status name if present, otherwise |None|.
			- has_doc: whether a docstring is present.
			- has_examples: whether example references are present.
			- has_see_also: whether the docstring contains structured |lit|`See_also` references.
	Notes:
		Purpose:
			This record is the canonical Waterloo representation for root-level object inventories.
	See_also:
		list_objects, get_object
	"""
	model_config = ConfigDict(extra="forbid")

	qid: str
	profile: str | None = None
	kind: SearchObjectKind_t
	scope: str = "public"
	status: str | None = None
	has_doc: bool = False
	has_examples: bool = False
	has_see_also: bool = False


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

# Return the loaded JSON as the generic Waterloo node type.
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


def _doc_profile_or_none(object_record: Mapping[str, object]) -> str | None:
	doc = object_record.get("doc", {})
	if isinstance(doc, Mapping):
		preamble = doc.get("Preamble", {})
		if isinstance(preamble, Mapping):
			profile = str(preamble.get("profile", "")).strip().lower()
			if profile in {"module", "class", "function", "method", "inherited_method"}:
				return profile
	return None


def _doc_profile(object_record: Mapping[str, object]) -> str:
	return _doc_profile_or_none(object_record) or "module"


def _doc_scope(object_record: Mapping[str, object]) -> str:
	doc = object_record.get("doc", {})
	if isinstance(doc, Mapping):
		preamble = doc.get("Preamble", {})
		if isinstance(preamble, Mapping):
			scope_data = preamble.get("scope")
			if isinstance(scope_data, str):
				scope = scope_data.strip().lower()
				if scope:
					return scope
			if isinstance(scope_data, list):
				for item in scope_data:
					scope = str(item).strip().lower()
					if scope:
						return scope
	return "public"


def _doc_status(object_record: Mapping[str, object]) -> str | None:
	doc = object_record.get("doc", {})
	if isinstance(doc, Mapping):
		preamble = doc.get("Preamble", {})
		if isinstance(preamble, Mapping):
			status = str(preamble.get("status", "")).strip().lower()
			if status:
				return status
	return None


def _has_doc(object_record: Mapping[str, object]) -> bool:
	doc = object_record.get("doc", {})
	return isinstance(doc, Mapping) and isinstance(doc.get("Preamble"), Mapping)


def _has_examples(object_record: Mapping[str, object]) -> bool:
	examples = object_record.get("examples")
	return isinstance(examples, list) and any(str(item).strip() for item in examples)


def _has_see_also(object_record: Mapping[str, object]) -> bool:
	return bool(_doc_see_also_refs(object_record))


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


def matches_segment_aware_expression(candidate: str, expression: str) -> bool:
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
			|Must| check whether a candidate name matches a given expression.
			|Must| support literal matches and glob patterns with wildcards |lit|`*` |lit|`?` |lit|`[]` including negated character classes |lit|`[!... ]`.
			|Must| match wildcard expressions against the whole candidate, the tail after the last dot, and each individual dot-separated segment.
			|Must| treat the expression as a literal match if it does not contain any glob wildcard characters.
			|Must| match literal expressions against the whole candidate and against the tail after the last dot.
			|Must| allow the following wildcards in glob patterns:
			- |lit|`*` matches any sequence of characters, including dots.
			- |lit|`?` matches any single character.
			- |lit|`[abc]` matches any single character in the set.
			- |lit|`[!abc]` matches any single character not in the set.
	Parameters:
		candidate:
			The candidate name to check, for example |lit|`package.module.Class.method` or |lit|`Parameters`.
		expression:
			The expression to match against, which can be either a literal string or a glob pattern.
	Returns:
		|True| if the candidate matches the expression according to the rules above, |False| otherwise.
	Raises:
	Notes:
		Implementation:
			The implementation uses the fnmatch module for wildcard expressions and first
			checks the whole candidate, then the tail after the last dot, and finally each
			individual dot-separated segment. Literal expressions are checked against the
			whole candidate and the tail only.
	"""
	if any(ch in expression for ch in "*?[]"):
		if fnmatch.fnmatchcase(candidate, expression):
			return True
		tail = candidate.split(".")[-1]
		if fnmatch.fnmatchcase(tail, expression):
			return True
		return any(fnmatch.fnmatchcase(part, expression) for part in candidate.split("."))
	if candidate == expression:
		return True
	if candidate.endswith(f".{expression}"):
		return True
	return candidate.split(".")[-1] == expression


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


def _load_root_context(root_id: str, roots: list[Mapping[str, WtrlJsonNode_t]]) -> tuple[int, Mapping[str, WtrlJsonNode_t], Path, dict[str, WtrlJsonNode_t]]:
	idx, root_data = _get_root_record(root_id, roots)
	root_path = _canonical_root_path(str(root_data.get("path", "")))
	document = _read_json_document(str(root_path))
	if not isinstance(document, dict):
		raise ValueError(f"Root document must be a JSON object: {root_id}")
	return idx, root_data, root_path, document


def _about_resource_name(topic: str | None) -> str:
	if topic is None:
		return "mcp_about.json"
	topic_key = topic.strip()
	if not topic_key:
		raise ValueError("about topic must not be empty")
	return f"mcp_about_{topic_key.replace('.', '_')}.json"


def about(topic: str | None = None) -> dict[str, WtrlJsonNode_t]:
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
			|Must| load one Waterloo about help topic from the bundled package resources.
			|Must| return the index response when |var|`topic` is |None|.
			|Must| derive the resource file name from the requested topic key.
			|Must| keep the help text file backed by the package resources so it can be edited without code changes.
	Parameters:
		topic:
			Optional help topic key such as |lit|`waterlint.command`, |lit|`waterloo.structure`, or |lit|`waterloo.markup`.
			If omitted, the index response is returned.
	Returns:
		The parsed Waterloo about JSON document for the requested topic or the index response.
	Raises:
		FileNotFoundError:
			|May| raise if the about text file is missing from the package resources.
		ValueError:
			|May| raise if |var|`topic` is empty.
		json.JSONDecodeError:
			|May| raise if the about text file is not valid JSON.
	"""
	resource_name = _about_resource_name(topic)
	resource = importlib.resources.files("sdv.doc.waterloo.mcp.tool_about").joinpath(resource_name)
	return cast(dict[str, WtrlJsonNode_t], json.loads(resource.read_text(encoding="utf-8")))


def _doc_normative_sections(object_record: Mapping[str, object]) -> set[str]:
	doc = object_record.get("doc", {})
	if not isinstance(doc, Mapping):
		return set()
	preamble = doc.get("Preamble", {})
	if not isinstance(preamble, Mapping):
		return set()
	sections = preamble.get("normative_sections", [])
	if not isinstance(sections, list):
		return set()
	return {str(section).strip() for section in sections if str(section).strip()}


def _doc_see_also_refs(object_record: Mapping[str, object]) -> list[str]:
	doc = object_record.get("doc", {})
	if not isinstance(doc, Mapping):
		return []
	see_also = doc.get("See_also")
	if not isinstance(see_also, list):
		return []
	return [str(item).strip() for item in see_also if str(item).strip()]


def _resolve_related_targets(
	ref: str,
	source_root_id: str,
	source_qid: str,
	qids_to_roots: Mapping[str, set[str]],
) -> list[tuple[str, str]]:
	candidates: list[str] = []
	if "." in ref:
		candidates.append(ref)
	if "." in source_qid:
		candidates.append(f"{source_qid.rsplit('.', 1)[0]}.{ref}")
	else:
		candidates.append(f"{source_qid}.{ref}")
	candidates.append(ref)

	resolved: list[tuple[str, str]] = []
	seen_candidates: set[str] = set()
	for cand in candidates:
		if cand in seen_candidates:
			continue
		seen_candidates.add(cand)
		root_ids = qids_to_roots.get(cand)
		if not root_ids:
			continue
		if source_root_id in root_ids:
			resolved.append((source_root_id, cand))
			continue
		if len(root_ids) == 1:
			root_id = next(iter(root_ids))
			resolved.append((root_id, cand))
	return resolved


def _get_root_record(root_id: str, roots: list[Mapping[str, WtrlJsonNode_t]]) -> tuple[int, Mapping[str, WtrlJsonNode_t]]:
	return _find_root_by_id(roots, root_id)


def _find_root_by_id(roots: list[Mapping[str, WtrlJsonNode_t]], root_id: str) -> tuple[int, Mapping[str, WtrlJsonNode_t]]:
	for idx, root_data in enumerate(roots):
		path_text = str(root_data.get("path", "")).strip()
		if path_text and _root_id_for_path(path_text) == root_id:
			return idx, root_data
	raise ValueError(f"Unknown root_id: {root_id}")


def list_roots(roots: list[Mapping[str, WtrlJsonNode_t]]) -> list[dict[str, WtrlJsonNode_t]]:
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
			|Must| return one dictionary per root entry with the following mandatory attributes:
			- |attr|`root_id`: stable hash of the canonical absolute root path.
			- |attr|`root_index`: zero-based index in the input list.
			- |attr|`label`: human-readable root label from configuration, or derived from path name.
			- |attr|`kind`: root kind from configuration or derived from filesystem classification.
			- |attr|`path`: canonical absolute path as a string.
			- |attr|`enabled`: boolean indicating whether the root is active.
	Parameters:
		roots:
			The list of root configurations to process.
	Returns:
		A list of dictionaries, each with the mandatory attributes described above.
	Raises:
	"""
	out: list[dict[str, WtrlJsonNode_t]] = []
	for idx, root_data in enumerate(roots):
		root = _canonical_root_path(str(root_data.get("path", "")))
		out.append(_root_summary(idx, root_data, root))
	return out


def get_root_metadata(root_id: str, roots: list[Mapping[str, WtrlJsonNode_t]]) -> dict[str, WtrlJsonNode_t]:
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
			|Must| resolve a configured root by its canonical root identifier and return only the compact header metadata block without the full JSON document body.
	Parameters:
		root_id:
			The canonical root identifier derived from the canonical absolute root path.
		roots:
			The list of configured root entries.
	Notes:
		Parameters:
			MCP callers only pass ``root_id``; the server injects the root list internally.
		Example:
			``get_root_metadata(root_id="...")``
	Returns:
		A dictionary describing the root and containing only the compact header metadata fields from the loaded JSON document.
	Raises:
		ValueError:
			|May| raise if the root identifier is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	See_also:
		list_roots, get_root
	"""
	idx, root_data, root_path, document = _load_root_context(root_id, roots)
	return {
		**_root_summary(idx, root_data, root_path),
		"__WTRL_VERSION__": document.get("__WTRL_VERSION__", {}),
		"__WTRL_META__": document.get("__WTRL_META__", {}),
		"__WTRL_ROLES__": document.get("__WTRL_ROLES__", {}),
		"__WTRL_SCOPES__": document.get("__WTRL_SCOPES__", {}),
	}


def get_root(root_id: str, roots: list[Mapping[str, WtrlJsonNode_t]]) -> dict[str, WtrlJsonNode_t]:
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
	Notes:
		Parameters:
			MCP callers only pass ``root_id``; the server injects the root list internally.
		Example:
			``get_root(root_id="...")``
	Returns:
		A dictionary describing the root and containing the parsed JSON document.
	Raises:
		ValueError:
			|May| raise if the root identifier is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	See_also:
		list_roots, get_root_metadata
	"""
	idx, root_data, root_path, document = _load_root_context(root_id, roots)
	return {**_root_summary(idx, root_data, root_path), "document": document}


def get_object(root_id: str, qid: str, roots: list[Mapping[str, WtrlJsonNode_t]]) -> dict[str, WtrlJsonNode_t]:
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
	Notes:
		Parameters:
			MCP callers only pass ``root_id`` and ``qid``; the server injects the root list internally.
		Example:
			``get_object(root_id="...", qid="...")``
	Returns:
		A dictionary describing the root, the requested QID, and the stored object record.
	Raises:
		ValueError:
			|May| raise if the root identifier or QID is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	See_also:
		get_root, get_section, list_objects
	"""
	idx, root_data, root_path, document = _load_root_context(root_id, roots)
	objects = document.get("__WTRL_OBJECTS__", {})
	if not isinstance(objects, Mapping):
		raise ValueError(f"Unknown qid: {qid}")
	object_record = objects.get(qid)
	if object_record is None:
		raise ValueError(f"Unknown qid: {qid}")
	return {**_root_summary(idx, root_data, root_path), "qid": qid, "object": object_record}


def get_section(root_id: str, qid: str, section: str, roots: list[Mapping[str, WtrlJsonNode_t]]) -> dict[str, WtrlJsonNode_t]:
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
	Notes:
		Parameters:
			MCP callers only pass ``root_id``, ``qid`` and ``section``; the server injects the root list internally.
		Example:
			``get_section(root_id="...", qid="...", section="...")``
	Returns:
		A dictionary describing the root, the requested QID, the requested section, and the stored section value.
	Raises:
		ValueError:
			|May| raise if the root identifier, QID, or section name is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	See_also:
		get_object, get_subsection, search_sections
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


def get_subsection(root_id: str, qid: str, section: str, subsection: str, roots: list[Mapping[str, WtrlJsonNode_t]]) -> dict[str, WtrlJsonNode_t]:
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
	Notes:
		Parameters:
			MCP callers only pass ``root_id``, ``qid``, ``section`` and ``subsection``; the server injects the root list internally.
		Example:
			``get_subsection(root_id="...", qid="...", section="...", subsection="...")``
	Returns:
		A dictionary describing the root, the requested QID, the requested section, the requested subsection, and the stored subsection value.
	Raises:
		ValueError:
			|May| raise if the root identifier, QID, section name, or subsection name is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	See_also:
		get_section, get_object
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


def list_objects(root_id: str, roots: list[Mapping[str, WtrlJsonNode_t]]) -> list[ObjectSummary]:
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
			|Must| return a compact inventory of all objects in one configured root.
			|Must| keep the inventory deterministic by sorting rows by QID.
			|Must| derive the public-facing scope field from the docstring when present and default it to |value|`public` otherwise.
			|Must| leave the status field empty unless the docstring explicitly provides one.
	Parameters:
		root_id:
			The canonical root identifier derived from the canonical absolute root path.
		roots:
			The list of configured root entries.
	Notes:
		Parameters:
			MCP callers only pass ``root_id``; the server injects the root list internally.
		Example:
			``list_objects(root_id="...")``
	Returns:
		A list of ObjectSummary records, one per object in the configured root.
	Raises:
		ValueError:
			|May| raise if the root identifier is unknown or the root document does not contain a usable object table.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	See_also:
		get_object, search_objects
	"""
	_, _, _, document = _load_root_context(root_id, roots)
	objects = document.get("__WTRL_OBJECTS__", {})
	if not isinstance(objects, Mapping):
		raise ValueError(f"Unknown root_id: {root_id}")
	summaries: list[ObjectSummary] = []
	for qid, object_record in sorted(objects.items(), key=lambda item: str(item[0])):
		if not isinstance(object_record, Mapping):
			continue
		summaries.append(
			ObjectSummary(
				qid=str(qid),
				profile=_doc_profile_or_none(object_record),
				kind=cast(SearchObjectKind_t, _object_kind(document, str(qid), object_record)),
				scope=_doc_scope(object_record),
				status=_doc_status(object_record),
				has_doc=_has_doc(object_record),
				has_examples=_has_examples(object_record),
				has_see_also=_has_see_also(object_record),
			)
		)
	return summaries


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
			|Must| return an empty list when the reverse map has no entry for the requested root/QID pair.
	Parameters:
		reference_index:
			The reverse lookup map built by the server at startup.
		root_id:
			The canonical root identifier of the object whose incoming references should be returned.
		qid:
			The fully qualified identifier of the object whose incoming references should be returned.
		normative_only:
			Whether to keep only references recorded from a normative See_also section.
	Notes:
		Parameters:
			MCP callers only pass ``root_id``, ``qid`` and optionally ``normative_only``;
			the server injects ``reference_index`` internally.
		Example:
			``get_references(root_id="...", qid="...")``
	Returns:
		A list of incoming structured See_also reference records.
	Raises:
	See_also:
		search_related, get_object
	"""
	records = reference_index.get((root_id, qid), [])
	records = [
		record if isinstance(record, ReferenceRecord) else ReferenceRecord.model_validate(record)
		for record in records
	]
	if normative_only:
		records = [record for record in records if record.is_normative]
	return records


def search_related(
	reference_index: Mapping[tuple[str, str], list[ReferenceRecord]],
	qids_to_roots: Mapping[str, set[str]],
	root_id: str,
	qid: str,
	roots: list[Mapping[str, WtrlJsonNode_t]],
	normative_only: bool = False,
) -> list[RelatedRecord]:
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
			|Must| return the direct star-shaped neighborhood around one object using the structured See_also graph.
			|Must| use only structured See_also relations and stay separate from full-text search.
			|Must| keep the first version centered on one anchor object, deduplicate matching neighbors,\
			and collapse the direct relation direction to in, out, or in_out.
			|Must| return an empty list when the anchor object has no related neighbors in the structured graph.
	Parameters:
		reference_index:
			The reverse lookup map built by the server at startup.
		qids_to_roots:
			The map from canonical QID to the set of root identifiers that contain that QID.
		root_id:
			The canonical root identifier of the anchor object whose neighborhood should be returned.
		qid:
			The fully qualified identifier of the anchor object whose neighborhood should be returned.
		roots:
			The list of configured root entries.
		normative_only:
			Whether to keep only relations recorded from a normative See_also section.
	Notes:
		Parameters:
			MCP callers only pass ``root_id``, ``qid`` and optionally ``normative_only``;
			the server injects ``reference_index``, ``qids_to_roots`` and ``roots`` internally.
		Example:
			``search_related(root_id="...", qid="...")``
	Returns:
		A list of RelatedRecord records for the anchor object's direct neighborhood with deduplicated neighbor entries.
	Raises:
		ValueError:
			|May| raise if the root identifier is unknown, the QID is unknown, or the loaded object is not a supported Waterloo profile.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	See_also:
		get_references, get_object
	"""
	_, _, _, document = _load_root_context(root_id, roots)
	objects = document.get("__WTRL_OBJECTS__", {})
	if not isinstance(objects, Mapping):
		raise ValueError(f"Unknown qid: {qid}")
	object_record = objects.get(qid)
	if not isinstance(object_record, Mapping):
		raise ValueError(f"Unknown qid: {qid}")
	anchor_profile = _doc_profile(object_record)
	if anchor_profile not in {"module", "class", "function", "method"}:
		raise ValueError(f"Unknown qid: {qid}")
	anchor_refs = _doc_see_also_refs(object_record)
	anchor_is_normative = "See_also" in _doc_normative_sections(object_record)

	root_context_cache: dict[str, tuple[int, Mapping[str, WtrlJsonNode_t], Path, dict[str, WtrlJsonNode_t]]] = {
		root_id: (0, {}, Path(), document),
	}

	def _load_object_record(target_root_id: str, target_qid: str) -> Mapping[str, object] | None:
		context = root_context_cache.get(target_root_id)
		if context is None:
			context = _load_root_context(target_root_id, roots)
			root_context_cache[target_root_id] = context
		_, _, _, target_document = context
		target_objects = target_document.get("__WTRL_OBJECTS__", {})
		if not isinstance(target_objects, Mapping):
			return None
		target_record = target_objects.get(target_qid)
		if isinstance(target_record, Mapping):
			return target_record
		return None

	related: list[RelatedRecord] = []
	related_map: dict[tuple[str, str, str, str], dict[str, bool | set[str]]] = {}

	def _related_key(related_root_id: str, related_qid: str, related_profile: str, relation_kind: str) -> tuple[str, str, str, str]:
		return (related_root_id, related_qid, related_profile, relation_kind)

	def _add_related(
		related_root_id: str,
		related_qid: str,
		related_profile: str,
		direction: str,
		is_normative: bool,
	) -> None:
		key = _related_key(related_root_id, related_qid, related_profile, "see_also")
		entry = related_map.setdefault(
			key,
			{
				"directions": set(),
				"is_normative": False,
			},
		)
		directions = entry["directions"]
		if isinstance(directions, set):
			directions.add(direction)
		entry["is_normative"] = bool(entry["is_normative"]) or is_normative

	if not normative_only or anchor_is_normative:
		for ref in anchor_refs:
			for related_root_id, related_qid in _resolve_related_targets(ref, root_id, qid, qids_to_roots):
				target_record = _load_object_record(related_root_id, related_qid)
				if target_record is None:
					continue
				related_profile = _doc_profile(target_record)
				if related_profile not in {"module", "class", "function", "method"}:
					continue
				_add_related(
					related_root_id=related_root_id,
					related_qid=related_qid,
					related_profile=related_profile,
					direction="out",
					is_normative=anchor_is_normative,
				)

	for record in reference_index.get((root_id, qid), []):
		record = record if isinstance(record, ReferenceRecord) else ReferenceRecord.model_validate(record)
		if normative_only and not record.is_normative:
			continue
		_add_related(
			related_root_id=record.source_root_id,
			related_qid=record.source_qid,
			related_profile=record.source_profile,
			direction="in",
			is_normative=record.is_normative,
		)

	for related_root_id, related_qid, related_profile, relation_kind in sorted(related_map):
		entry = related_map[(related_root_id, related_qid, related_profile, relation_kind)]
		directions = entry["directions"]
		if not isinstance(directions, set):
			continue
		direction = "in_out" if {"in", "out"}.issubset(directions) else ("out" if "out" in directions else "in")
		is_normative = bool(entry["is_normative"])
		related_record = RelatedRecord(
			related_root_id=related_root_id,
			related_qid=related_qid,
			related_profile=cast(DocstringProfile_t, related_profile),
			direction=cast(Literal["in", "out", "in_out"], direction),
			relation_kind=cast(Literal["see_also"], relation_kind),
			is_normative=is_normative,
		)
		if normative_only and not related_record.is_normative:
			continue
		related.append(related_record)

	related.sort(
		key=lambda record: (
			record.related_root_id,
			record.related_qid,
			0 if record.direction == "out" else 1 if record.direction == "in_out" else 2,
			record.relation_kind,
			record.related_profile,
			0 if record.is_normative else 1,
		)
	)
	return related


def get_signature(root_id: str, qid: str, roots: list[Mapping[str, WtrlJsonNode_t]]) -> dict[str, WtrlJsonNode_t]:
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
			|Must| return the stored signature block for one object together with its root and profile metadata.
			|Must| preserve the stored signature block verbatim, including additional fields such as decorators.
	Parameters:
		root_id:
			The canonical root identifier derived from the canonical absolute root path.
		qid:
			The fully qualified identifier of the requested object inside the loaded Waterloo JSON document.
		roots:
			The list of configured root entries.
	Notes:
		Parameters:
			MCP callers only pass ``root_id`` and ``qid``; the server injects the root list internally.
		Example:
			``get_signature(root_id="...", qid="...")``
	Returns:
		A dictionary with ``root_id``, ``qid``, ``profile`` and ``signature``.
	Raises:
		ValueError:
			|May| raise if the root identifier or QID is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	See_also:
		get_object, search_sections
	"""
	idx, root_data, root_path, document = _load_root_context(root_id, roots)
	objects = document.get("__WTRL_OBJECTS__", {})
	if not isinstance(objects, Mapping):
		raise ValueError(f"Unknown qid: {qid}")
	object_record = objects.get(qid)
	if not isinstance(object_record, Mapping):
		raise ValueError(f"Unknown qid: {qid}")
	profile = _doc_profile(object_record)
	return {
		**_root_summary(idx, root_data, root_path),
		"qid": qid,
		"profile": profile,
		"signature": cast(WtrlJsonNode_t, object_record.get("signature")),
	}


def _example_key_from_path(example_path: str) -> str:
	prefix = "/__WTRL_EXAMPLES__/"
	if not example_path.startswith(prefix):
		raise ValueError(f"MCPS-006 unknown example reference: {example_path}")
	key = example_path[len(prefix) :]
	if not key:
		raise ValueError(f"MCPS-006 unknown example reference: {example_path}")
	return key


def _example_ref_from_entry(root_id: str, example_path: str, example_entry: Mapping[str, object]) -> ExampleRef:
	lang = str(example_entry.get("lang", "")).strip()
	if not lang:
		raise ValueError(f"Example entry is missing lang: {example_path}")
	code = example_entry.get("code", "")
	if isinstance(code, str):
		size = len(code.encode("utf-8"))
	else:
		size = len(str(code).encode("utf-8"))
	title_value = example_entry.get("title")
	title = str(title_value).strip() if isinstance(title_value, str) and title_value.strip() else None
	return ExampleRef(
		root_id=root_id,
		example_path=example_path,
		title=title,
		lang=lang,
		size=size,
	)


def get_examples(
	root_id: str,
	qid: str,
	roots: list[Mapping[str, WtrlJsonNode_t]],
) -> list[ExampleRef]:
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
			|Must| return structured example metadata for one QID from the configured roots.
			|Must| return an empty list if the object exists but has no examples.
			|Must| treat the example paths as canonical references inside __WTRL_EXAMPLES__.
	Parameters:
		root_id:
			The canonical root identifier derived from the canonical absolute root path.
		qid:
			The fully qualified identifier of the requested object inside the loaded Waterloo JSON document.
		roots:
			The list of configured root entries.
	Notes:
		Parameters:
			MCP callers only pass ``root_id`` and ``qid``; the server injects the root list internally.
		Example:
			``get_examples(root_id="...", qid="...")``
	Returns:
		A list of ExampleRef records for the object.
	Raises:
		ValueError:
			|May| raise if the root identifier or QID is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	See_also:
		get_example_source, get_object
	"""
	_, _, _, document = _load_root_context(root_id, roots)
	objects = document.get("__WTRL_OBJECTS__", {})
	if not isinstance(objects, Mapping):
		raise ValueError(f"Unknown qid: {qid}")
	object_record = objects.get(qid)
	if not isinstance(object_record, Mapping):
		raise ValueError(f"Unknown qid: {qid}")
	example_paths = object_record.get("examples", [])
	if not isinstance(example_paths, list) or not example_paths:
		return []
	example_entries = document.get("__WTRL_EXAMPLES__", {})
	if not isinstance(example_entries, Mapping):
		return []
	examples: list[ExampleRef] = []
	for raw_path in example_paths:
		if not isinstance(raw_path, str):
			continue
		example_path = raw_path.strip()
		if not example_path:
			continue
		key = _example_key_from_path(example_path)
		example_entry = example_entries.get(key)
		if not isinstance(example_entry, Mapping):
			continue
		examples.append(_example_ref_from_entry(root_id, example_path, example_entry))
	return examples


def _example_source_entry(root_id: str, example_path: str, roots: list[Mapping[str, WtrlJsonNode_t]]) -> Mapping[str, object]:
	_, _, _, document = _load_root_context(root_id, roots)
	example_entries = document.get("__WTRL_EXAMPLES__", {})
	if not isinstance(example_entries, Mapping):
		raise ValueError(f"MCPS-006 unknown example reference: {example_path}")
	key = _example_key_from_path(example_path)
	example_entry = example_entries.get(key)
	if not isinstance(example_entry, Mapping):
		raise ValueError(f"MCPS-006 unknown example reference: {example_path}")
	return example_entry


def get_example_source(
	root_id: str,
	example_path: str,
	roots: list[Mapping[str, WtrlJsonNode_t]],
) -> str:
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
			|Must| return the raw source text for one canonical example reference.
			|Must| treat the example path as a canonical path inside __WTRL_EXAMPLES__.
	Parameters:
		root_id:
			The canonical root identifier derived from the canonical absolute root path.
		example_path:
			The canonical example path returned by get_examples.
		roots:
			The list of configured root entries.
	Notes:
		Parameters:
			MCP callers only pass ``root_id`` and ``example_path``; the server injects the root list internally.
		Example:
			``get_example_source(root_id="...", example_path="/__WTRL_EXAMPLES__/sha256_...")``
	Returns:
		The raw example source text.
	Raises:
		ValueError:
			|May| raise if the root identifier is unknown or if the example reference is unknown.
		FileNotFoundError:
			|May| raise if the configured root path no longer exists.
		json.JSONDecodeError:
			|May| raise if the root file is not valid JSON.
	See_also:
		get_examples
	"""
	example_entry = _example_source_entry(root_id, example_path, roots)
	code = example_entry.get("code")
	if not isinstance(code, str):
		raise ValueError(f"MCPS-006 unknown example reference: {example_path}")
	return code


def search_objects(
	expression: str,
	roots: list[Mapping[str, WtrlJsonNode_t]],
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
	Notes:
		Parameters:
			MCP callers only pass ``expression`` and optionally ``filter``; the server injects the root list internally.
		Example:
			``search_objects(expression="...")``
	Returns:
		A list of triples ``(root_id, qid, kind)`` for matching objects.
	Raises:
		FileNotFoundError:
			|May| raise if a configured root path no longer exists while the search is being evaluated.
		json.JSONDecodeError:
			|May| raise if a root file is not valid JSON while the search is being evaluated.
	See_also:
		list_objects, search_sections, search_text
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
			if not matches_segment_aware_expression(str(qid), expression):
				continue
			matches.append((current_root_id, str(qid), kind))
	return matches


def search_sections(
	expression: str,
	roots: list[Mapping[str, WtrlJsonNode_t]],
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
	Notes:
		Parameters:
			MCP callers only pass ``expression`` and optionally ``filter``; the server injects the root list internally.
		Example:
			``search_sections(expression="...")``
	Returns:
		A list of dictionaries describing matching section or subsection labels together with their object and root location.
	Raises:
		FileNotFoundError:
			|May| raise if a configured root path no longer exists while the search is being evaluated.
		json.JSONDecodeError:
			|May| raise if a root file is not valid JSON while the search is being evaluated.
	See_also:
		get_section, get_subsection, search_objects
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
			if qid_filter is not None and not matches_segment_aware_expression(str(qid), qid_filter):
				continue
			if use_scope_filter and scope_filter is not None and scope_filter not in _object_scopes(object_record):
				continue
			doc = object_record.get("doc", {})
			if not isinstance(doc, Mapping):
				continue
			root_summary = _root_summary(idx, root_data, root_path)
			for section_name, section_value in doc.items():
				if matches_segment_aware_expression(str(section_name), expression):
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
						if matches_segment_aware_expression(str(subsection_name), expression):
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
	roots: list[Mapping[str, WtrlJsonNode_t]],
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
	Notes:
		Parameters:
			MCP callers only pass ``terms`` and optionally ``filter``; the server injects the root list internally.
		Example:
			``search_text(terms=["..."])``
	Returns:
		A list of dictionaries describing matching text locations together with their object and root location, plus a compact excerpt.
	Raises:
		FileNotFoundError:
			|May| raise if a configured root path no longer exists while the search is being evaluated.
		json.JSONDecodeError:
			|May| raise if a root file is not valid JSON while the search is being evaluated.
	See_also:
		search_sections, search_objects
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
			if qid_filter is not None and not matches_segment_aware_expression(qid_text, qid_filter):
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
		FileNotFoundError:
			|May| be raised if the generator needs to resolve a profile-specific source and the configured root path no longer exists.
		json.JSONDecodeError:
			|May| be raised if a profile-specific source has invalid JSON content.
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
