#!/usr/bin/env python3
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
		|Must| provide the typed in-memory representation and source-independent semantic checks for Waterloo Authoring JSON.
		|Must_not| resolve Python objects, inspect source files, or render physical docstring lines.
Public_classes:
	AuthoringParagraph, AuthoringListItem, AuthoringListBlock, AuthoringSection,
	AuthoringDocument, AuthoringSemanticIssue
Public_functions:
	load_authoring_document, validate_authoring_document, render_authoring_document
Public_types:
	AuthoringScalar_t:
		The scalar string value used by Authoring JSON fields.
	AuthoringTextBlock_t:
		A paragraph or nested list block in free-form Authoring JSON content.
	AuthoringSectionValue_t:
		The normalized in-memory value of one Authoring JSON section.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Final, Literal, Mapping, TypeAlias, cast

from sdv.doc.waterloo.docitem_helper import (
	CANONICAL_ORDER_OF_SECTIONS,
	SECTION_PROPERTIES,
	get_allowed_sections_for_profile,
)
from sdv.doc.waterloo.docitem_types import KEYWORDS_OF_NORMATIVITY, Profile_t


AuthoringScalar_t: TypeAlias = str
AuthoringSectionValue_t: TypeAlias = (
	AuthoringScalar_t
	| tuple[AuthoringScalar_t, ...]
	| tuple["AuthoringTextBlock_t", ...]
	| Mapping[str, tuple["AuthoringTextBlock_t", ...]]
	| "AuthoringPreamble"
	| "AuthoringContract"
)


@dataclass(frozen=True)
class AuthoringParagraph:
	"""One logical paragraph from an Authoring JSON free-text block."""

	text: str


@dataclass(frozen=True)
class AuthoringListItem:
	"""One logical list item and its optional recursively nested items."""

	text: str
	items: tuple["AuthoringListItem", ...] = ()


@dataclass(frozen=True)
class AuthoringListBlock:
	"""One ordered Authoring JSON list block."""

	items: tuple[AuthoringListItem, ...]


AuthoringTextBlock_t: TypeAlias = AuthoringParagraph | AuthoringListBlock


@dataclass(frozen=True)
class AuthoringPreamble:
	"""The fixed metadata carried by the Authoring JSON Preamble section."""

	profile: Profile_t
	normative_sections: tuple[str, ...]
	status: str | None
	scope: tuple[str, ...]


@dataclass(frozen=True)
class AuthoringContract:
	"""The fixed scalar and logical-item fields carried by Contract."""

	items: Mapping[str, str | tuple[str, ...]]


@dataclass(frozen=True)
class AuthoringSection:
	"""A top-level Waterloo section with Authoring-JSON-native content."""

	label: str
	value: AuthoringSectionValue_t


@dataclass(frozen=True)
class AuthoringDocument:
	"""Schema-valid Authoring JSON normalized into a typed, immutable document."""

	qualified_name: str
	profile: Profile_t
	signature: str | None
	sections: Mapping[str, AuthoringSection]

	def section(self, label: str) -> AuthoringSection | None:
		"""Return the section identified by label, or |None| when it is absent."""
		return self.sections.get(label)

	def section_labels(self) -> tuple[str, ...]:
		"""Return existing section labels in canonical Waterloo order."""
		return tuple(label for label in CANONICAL_ORDER_OF_SECTIONS if label in self.sections)


@dataclass(frozen=True)
class AuthoringSemanticIssue:
	"""One source-independent Authoring-JSON semantic inconsistency."""

	code: Literal[
		"profile-section",
		"preamble-profile-mismatch",
		"required-section",
		"normative-duplicate",
		"normative-missing-section",
		"normative-not-allowed",
		"normative-fixed-section",
		"normative-informative-section",
		"normative-required-section",
		"normative-keyword-missing-section",
	]
	path: str
	message: str


_PREAMBLE_SECTION: Final[str] = "Preamble"
_CONTRACT_SECTION: Final[str] = "Contract"
_LIST_MARKERS: Final[tuple[str, ...]] = ("*", "+", "-", "#")
_RE_UNBREAKABLE_INLINE: Final[re.Pattern[str]] = re.compile(
	r"\|[A-Za-z_]+\|`[^`]*`(?:[.,;:!?\)\]\}]+)?|https?://\S+"
)


def _expect_mapping(value: object, path: str) -> Mapping[str, object]:
	if not isinstance(value, Mapping):
		raise ValueError(f"Expected object at '{path}'.")
	return cast(Mapping[str, object], value)


def _expect_string(value: object, path: str) -> str:
	if not isinstance(value, str):
		raise ValueError(f"Expected string at '{path}'.")
	return value


def _expect_list(value: object, path: str) -> list[object]:
	if not isinstance(value, list):
		raise ValueError(f"Expected array at '{path}'.")
	return value


def _load_list_item(value: object, path: str) -> AuthoringListItem:
	item = _expect_mapping(value, path)
	text = _expect_string(item.get("text"), f"{path}.text")
	items_value = item.get("items", [])
	items = tuple(
		_load_list_item(child, f"{path}.items[{index}]")
		for index, child in enumerate(_expect_list(items_value, f"{path}.items"))
	)
	return AuthoringListItem(text=text, items=items)


def _load_text_blocks(value: object, path: str) -> tuple[AuthoringTextBlock_t, ...]:
	blocks: list[AuthoringTextBlock_t] = []
	for index, raw_block in enumerate(_expect_list(value, path)):
		block_path = f"{path}[{index}]"
		block = _expect_mapping(raw_block, block_path)
		if "paragraph" in block:
			blocks.append(AuthoringParagraph(_expect_string(block["paragraph"], f"{block_path}.paragraph")))
			continue
		if "list" in block:
			items = tuple(
				_load_list_item(raw_item, f"{block_path}.list[{item_index}]")
				for item_index, raw_item in enumerate(_expect_list(block["list"], f"{block_path}.list"))
			)
			blocks.append(AuthoringListBlock(items))
			continue
		raise ValueError(f"Expected paragraph or list block at '{block_path}'.")
	return tuple(blocks)


def _load_section_value(label: str, value: object, path: str) -> AuthoringSectionValue_t:
	if label == _PREAMBLE_SECTION:
		preamble = _expect_mapping(value, path)
		profile = _expect_string(preamble.get("profile"), f"{path}.profile")
		if profile not in {"module", "class", "function", "method", "inherited_method"}:
			raise ValueError(f"Unknown Authoring JSON profile '{profile}'.")
		normative_sections = tuple(
			_expect_string(item, f"{path}.normative_sections[{index}]")
			for index, item in enumerate(_expect_list(preamble.get("normative_sections"), f"{path}.normative_sections"))
		)
		status = _expect_string(preamble["status"], f"{path}.status") if "status" in preamble else None
		scope = tuple(
			_expect_string(item, f"{path}.scope[{index}]")
			for index, item in enumerate(_expect_list(preamble.get("scope", []), f"{path}.scope"))
		)
		return AuthoringPreamble(cast(Profile_t, profile), normative_sections, status, scope)
	if label == _CONTRACT_SECTION:
		contract = _expect_mapping(value, path)
		items: dict[str, str | tuple[str, ...]] = {}
		for key, raw_value in contract.items():
			if isinstance(raw_value, str):
				items[key] = raw_value
				continue
			items[key] = tuple(
				_expect_string(item, f"{path}.{key}[{index}]")
				for index, item in enumerate(_expect_list(raw_value, f"{path}.{key}"))
			)
		return AuthoringContract(items)
	if isinstance(value, list):
		if all(isinstance(item, str) for item in value):
			return tuple(cast(str, item) for item in value)
		return _load_text_blocks(value, path)
	if isinstance(value, str):
		return value
	section_map = _expect_mapping(value, path)
	return {
		key: _load_text_blocks(raw_value, f"{path}.{key}")
		for key, raw_value in section_map.items()
	}


def load_authoring_document(source: Mapping[str, object]) -> AuthoringDocument:
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
			|Must| normalize one schema-valid Authoring JSON mapping into an immutable\
			|class|`AuthoringDocument`.
			|Must| retain only data required by source-independent semantic validation and\
			rendering.
			|Must_not| validate the JSON Schema or source-independent Waterloo semantics.
	Parameters:
		source:
			A schema-valid raw Authoring JSON mapping.
	Returns:
		The normalized immutable |class|`AuthoringDocument`.
	Raises:
		ValueError:
			|May| be raised if a programmatic caller provides a source mapping that does not have
			the schema-required shape.
	Notes:
		Caller responsibility:
			Validate the JSON Schema before calling this function and use
			|func|`validate_authoring_document` for source-independent Waterloo semantics.
	"""
	profile = _expect_string(source.get("profile"), "profile")
	if profile not in {"module", "class", "function", "method", "inherited_method"}:
		raise ValueError(f"Unknown Authoring JSON profile '{profile}'.")
	doc = _expect_mapping(source.get("doc"), "doc")
	sections = {
		label: AuthoringSection(label, _load_section_value(label, value, f"doc.{label}"))
		for label, value in doc.items()
	}
	return AuthoringDocument(
		qualified_name=_expect_string(source.get("qualified_name"), "qualified_name"),
		profile=cast(Profile_t, profile),
		signature=_expect_string(source["signature"], "signature") if "signature" in source else None,
		sections=sections,
	)


def _preamble_value(document: AuthoringDocument, key: str) -> object | None:
	section = document.section(_PREAMBLE_SECTION)
	if section is None or not isinstance(section.value, AuthoringPreamble):
		return None
	if key == "profile":
		return section.value.profile
	if key == "normative_sections":
		return section.value.normative_sections
	if key == "status":
		return section.value.status
	if key == "scope":
		return section.value.scope
	return None


def _normative_sections(document: AuthoringDocument) -> tuple[str, ...]:
	# The schema guarantees this shape. Keeping the defensive guard makes this
	# function safe for programmatic users that construct AuthoringDocument.
	value = _preamble_value(document, "normative_sections")
	if isinstance(value, tuple) and all(isinstance(item, str) for item in value):
		return cast(tuple[str, ...], value)
	return ()


def _iter_texts(value: AuthoringSectionValue_t) -> tuple[str, ...]:
	if isinstance(value, str):
		return (value,)
	if isinstance(value, AuthoringPreamble):
		return ()
	if isinstance(value, AuthoringContract):
		texts: list[str] = []
		for item in value.items.values():
			if isinstance(item, str):
				texts.append(item)
			else:
				texts.extend(item)
		return tuple(texts)
	if isinstance(value, Mapping):
		return tuple(
			text
			for blocks in value.values()
			for block in blocks
			for text in _iter_block_texts(block)
		)
	if all(isinstance(item, str) for item in value):
		return cast(tuple[str, ...], value)
	return tuple(text for block in value for text in _iter_block_texts(cast(AuthoringTextBlock_t, block)))


def _iter_block_texts(block: AuthoringTextBlock_t) -> tuple[str, ...]:
	if isinstance(block, AuthoringParagraph):
		return (block.text,)
	texts: list[str] = []
	for item in block.items:
		texts.extend(_iter_list_item_texts(item))
	return tuple(texts)


def _iter_list_item_texts(item: AuthoringListItem) -> tuple[str, ...]:
	texts = [item.text]
	for child in item.items:
		texts.extend(_iter_list_item_texts(child))
	return tuple(texts)


def _has_normativity_keyword(value: AuthoringSectionValue_t) -> bool:
	return any(keyword in text for text in _iter_texts(value) for keyword in KEYWORDS_OF_NORMATIVITY)


def validate_authoring_document(document: AuthoringDocument) -> list[AuthoringSemanticIssue]:
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
			|Must| validate source-independent Waterloo semantics of an Authoring document.
			|Must| return every detected inconsistency as an |class|`AuthoringSemanticIssue`.
			|Must_not| resolve Python objects, inspect source files, or mutate the document.
	Parameters:
		document:
			A schema-shaped Authoring document normalized by |func|`load_authoring_document`.
	Returns:
		A list of all detected source-independent semantic issues.
	Raises:
	Notes:
		Deferred checks:
			Checks requiring resolved Python objects, such as references, annotations, and scopes,
			are deferred to |cmd|`waterlint validate`.
	"""
	issues: list[AuthoringSemanticIssue] = []
	labels = set(document.sections)
	allowed = set(get_allowed_sections_for_profile(document.profile))
	preamble_profile = _preamble_value(document, "profile")
	if preamble_profile != document.profile:
		issues.append(AuthoringSemanticIssue(
			"preamble-profile-mismatch",
			"doc.Preamble.profile",
			f"Preamble profile '{preamble_profile}' does not match root profile '{document.profile}'.",
		))

	for label in sorted(labels - {_PREAMBLE_SECTION}):
		if label not in allowed:
			issues.append(AuthoringSemanticIssue(
				"profile-section",
				f"doc.{label}",
				f"Section '{label}' is not allowed for profile '{document.profile}'.",
			))

	for label, properties in SECTION_PROPERTIES.items():
		if "." in label or properties["must_exist"] != "yes":
			continue
		if document.profile in properties["profile"] and label not in labels:
			issues.append(AuthoringSemanticIssue(
				"required-section",
				"doc",
				f"Section '{label}' is required for profile '{document.profile}'.",
			))

	normative_sections = _normative_sections(document)
	seen: set[str] = set()
	for index, label in enumerate(normative_sections):
		path = f"doc.Preamble.normative_sections[{index}]"
		if label in seen:
			issues.append(AuthoringSemanticIssue(
				"normative-duplicate", path,
				f"Section '{label}' is listed more than once as normative.",
			))
			continue
		seen.add(label)
		if label not in allowed:
			issues.append(AuthoringSemanticIssue(
				"normative-not-allowed", path,
				f"Section '{label}' is not allowed for profile '{document.profile}'.",
			))
			continue
		if label not in labels:
			issues.append(AuthoringSemanticIssue(
				"normative-missing-section", path,
				f"Normative section '{label}' does not exist in doc.",
			))
			continue
		properties = SECTION_PROPERTIES[label]
		if properties["normativity"] == "informative":
			issues.append(AuthoringSemanticIssue(
				"normative-informative-section", path,
				f"Informative section '{label}' must not be listed as normative.",
			))

	for label in labels - {_PREAMBLE_SECTION}:
		section_properties = SECTION_PROPERTIES.get(label)
		if section_properties is None or document.profile not in section_properties["profile"]:
			continue
		if section_properties["normativity"] == "normative" and label not in seen:
			issues.append(AuthoringSemanticIssue(
				"normative-required-section",
				"doc.Preamble.normative_sections",
				f"Normative section '{label}' must be listed in Preamble.normative_sections.",
			))
		if (
			section_properties["normativity"] == "can_be_both"
			and label not in seen
			and _has_normativity_keyword(document.sections[label].value)
		):
			issues.append(AuthoringSemanticIssue(
				"normative-keyword-missing-section",
				f"doc.{label}",
				f"Section '{label}' contains a normativity keyword but is not listed in Preamble.normative_sections.",
			))

	return issues


def _tokenize_for_wrapping(text: str) -> tuple[str, ...]:
	"""Split text into words while retaining Waterloo roles and URLs as units."""
	tokens: list[str] = []
	position = 0
	for match in _RE_UNBREAKABLE_INLINE.finditer(text):
		tokens.extend(part.group() for part in re.finditer(r"\S+", text[position:match.start()]))
		tokens.append(match.group())
		position = match.end()
	tokens.extend(part.group() for part in re.finditer(r"\S+", text[position:]))
	return tuple(tokens)


def _wrap_logical_text(text: str, available_width: int, *, continuation: bool) -> list[str]:
	if available_width < 2:
		raise ValueError("Rendering width leaves no room for text.")
	tokens = _tokenize_for_wrapping(text)
	if not tokens:
		return [""]

	def pack(line_width: int) -> list[str]:
		lines: list[str] = []
		line = ""
		for token in tokens:
			candidate = token if not line else f"{line} {token}"
			if line and len(candidate) > line_width:
				lines.append(line)
				line = token
			else:
				line = candidate
		if line:
			lines.append(line)
		return lines

	lines = pack(available_width)
	if continuation and len(lines) > 1:
		lines = pack(available_width - 1)
		return [f"{line}\\" if index < len(lines) - 1 else line for index, line in enumerate(lines)]
	return lines


def _append_logical_text(
	lines: list[str],
	text: str,
	*,
	indent_unit: str,
	indentation: int,
	width: int,
	first_prefix: str = "",
	continuation: bool = False,
) -> None:
	prefix = indent_unit * indentation
	wrapped = _wrap_logical_text(text, width - len(prefix) - len(first_prefix), continuation=continuation)
	for index, line in enumerate(wrapped):
		lines.append(f"{prefix}{first_prefix if index == 0 else ''}{line}")


def _append_list_item(
	lines: list[str],
	item: AuthoringListItem,
	*,
	depth: int,
	indent_unit: str,
	indentation: int,
	width: int,
) -> None:
	if depth >= len(_LIST_MARKERS):
		raise ValueError(f"Authoring JSON list nesting exceeds {len(_LIST_MARKERS)} Waterloo marker levels.")
	_append_logical_text(
		lines, item.text, indent_unit=indent_unit, indentation=indentation, width=width,
		first_prefix=f"{_LIST_MARKERS[depth]} ", continuation=True,
	)
	for child in item.items:
		_append_list_item(
			lines, child, depth=depth + 1, indent_unit=indent_unit,
			indentation=indentation, width=width,
		)


def _append_text_blocks(
	lines: list[str],
	blocks: tuple[AuthoringTextBlock_t, ...],
	*,
	indent_unit: str,
	indentation: int,
	width: int,
) -> None:
	for block_index, block in enumerate(blocks):
		if block_index:
			lines.append(f"{indent_unit * indentation}|")
		if isinstance(block, AuthoringParagraph):
			_append_logical_text(
				lines, block.text, indent_unit=indent_unit, indentation=indentation, width=width,
			)
		else:
			for item in block.items:
				_append_list_item(
					lines, item, depth=0, indent_unit=indent_unit,
					indentation=indentation, width=width,
				)


def _append_text_map(
	lines: list[str],
	value: Mapping[str, tuple[AuthoringTextBlock_t, ...]],
	*,
	indent_unit: str,
	indentation: int,
	width: int,
) -> None:
	for label, blocks in value.items():
		lines.append(f"{indent_unit * indentation}{label}:")
		_append_text_blocks(
			lines, blocks, indent_unit=indent_unit, indentation=indentation + 1, width=width,
		)


def _append_preamble(
	lines: list[str],
	preamble: AuthoringPreamble,
	*,
	indent_unit: str,
	indentation: int,
	width: int,
) -> None:
	values: tuple[tuple[str, str | tuple[str, ...] | None], ...] = (
		("profile", preamble.profile),
		("normative_sections", preamble.normative_sections),
		("status", preamble.status),
		("scope", preamble.scope),
	)
	for label, value in values:
		if value is None or value == ():
			continue
		lines.append(f"{indent_unit * indentation}{label}:")
		_append_logical_text(
			lines, ", ".join(value) if isinstance(value, tuple) else value,
			indent_unit=indent_unit, indentation=indentation + 1, width=width, continuation=True,
		)


def _append_contract(
	lines: list[str],
	contract: AuthoringContract,
	*,
	indent_unit: str,
	indentation: int,
	width: int,
) -> None:
	for label in CANONICAL_ORDER_OF_SECTIONS[_CONTRACT_SECTION] or ():
		value = contract.items.get(label)
		if value is None:
			continue
		lines.append(f"{indent_unit * indentation}{label}:")
		properties = SECTION_PROPERTIES[f"Contract.{label}"]
		items: tuple[str, ...]
		if isinstance(value, tuple) and properties["category"] == "LIST_OF_IDENTIFIERS":
			items = (", ".join(value),)
		else:
			items = value if isinstance(value, tuple) else (value,)
		for item in items:
			_append_logical_text(
				lines, item, indent_unit=indent_unit, indentation=indentation + 1,
				width=width, continuation=True,
			)


def render_authoring_document(
	document: AuthoringDocument,
	*,
	indent_unit: Literal["TAB", "SPC4"] = "TAB",
	indentation: int = 0,
	width: int = 88,
) -> str:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a semantically validated |class|`AuthoringDocument` as Waterloo\
			docstring content.
			|Must| preserve the document's canonical section order and the semantic content of\
			its sections.
			|Must| return raw docstring content without Python string delimiters or source-file\
			updates.
			|Must| terminate the returned content with exactly one newline character.
			|May| wrap logical text lines using Waterloo continuation backslashes when necessary\
			to respect |var|`width`.
	Description:
		This renderer is the final content-only step of the Authoring JSON workflow. It assumes
		that schema and semantic validation have already completed successfully.
	Parameters:
		document:
			The semantically validated Authoring document to render.
		indent_unit:
			The Waterloo indentation unit: |lit|`TAB` for tab characters or |lit|`SPC4` for groups
			of four spaces.
		indentation:
			The number of |var|`indent_unit` levels placed before every rendered top-level
			section.
		width:
			The maximum preferred physical-line width used while wrapping logical text.
	Returns:
		Waterloo docstring content ready to be placed between Python string delimiters.
	Raises:
		ValueError:
			|May| be raised if |var|`indentation` is negative, |var|`width` is too small, or the
			requested width leaves no room below the section indentation.
	Notes:
		Whitespace:
			The returned content uses only the selected indentation unit. Callers that embed it in
			Python source remain responsible for surrounding quote delimiters.
	"""
	if indentation < 0:
		raise ValueError("Indentation must not be negative.")
	if width < 8:
		raise ValueError("Rendering width must be at least 8.")
	unit = "\t" if indent_unit == "TAB" else "    "
	if len(unit) * (indentation + 2) >= width:
		raise ValueError("Rendering width leaves no room below the section indentation.")

	lines: list[str] = []
	for section_label in document.section_labels():
		section = document.sections[section_label]
		lines.append(f"{unit * indentation}{section_label}:")
		if isinstance(section.value, AuthoringPreamble):
			_append_preamble(lines, section.value, indent_unit=unit, indentation=indentation + 1, width=width)
		elif isinstance(section.value, AuthoringContract):
			_append_contract(lines, section.value, indent_unit=unit, indentation=indentation + 1, width=width)
		elif isinstance(section.value, str):
			_append_logical_text(lines, section.value, indent_unit=unit, indentation=indentation + 1, width=width, continuation=True)
		elif isinstance(section.value, Mapping):
			_append_text_map(lines, section.value, indent_unit=unit, indentation=indentation + 1, width=width)
		elif all(isinstance(item, str) for item in section.value):
			_append_logical_text(
				lines, ", ".join(cast(tuple[str, ...], section.value)),
				indent_unit=unit, indentation=indentation + 1, width=width, continuation=True,
			)
		else:
			_append_text_blocks(
				lines, cast(tuple[AuthoringTextBlock_t, ...], section.value),
				indent_unit=unit, indentation=indentation + 1, width=width,
			)
	return "\n".join(lines) + "\n"
