r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
Contract:
	general:
		|Must| provide functions for rendering Waterloo diagnostics snippets and hints.
Public_functions:
	explain_try_self_for_section,
	explain_try_self_for_subsection,
	render_source_snippet,
	render_expected_snippet,
	render_found_label,
	render_allowed_identifier,
	render_expected_identifier,
	render_suggestion,
	render_allowed_identifiers,
	render_identifier_lines,
	render_deduplicated_identifiers,
	render_unique_identifiers,
	render_normative_section_details,
	render_missing_entry_details,
	render_overview_requires_section_details,
	render_name_object_consistency_details,
	render_listed_object_missing_details,
	render_profile_mismatch_details,
	render_normativity_keyword_details,
	render_exception_reference_details,
	render_base_method_reference_details,
	render_exactly_one_identifier_details,
	render_parameter_signature_details,
	render_see_also_reference_details,
	render_scope_relation_details,
	render_base_method_docstring_details,
	render_definition_reference_details,
	render_inherited_definition_details,
	render_type_reference_details,
	render_constant_reference_details,
	render_named_value_reference_details,
	render_overview_missing_member_details
"""

from __future__ import annotations
from typing import Any, Iterable, Literal
from sdv.doc.waterloo.docitem_helper import (
	CANONICAL_ORDER_OF_SECTIONS,
	Scopes,
	scope_to_string
)


#===== begin render functions for verbose diagnostics ========#

#----- explain command builders ------------------------------#

def explain_try_self_for_section(label: str, profile: str) -> str:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises, See_also
	Contract:
		general:
			|Must| build the canonical self-explanation command for a section label and profile.
	Parameters:
		label:
			The section label to explain.
		profile:
			The docstring profile to use as the explain context.
	Returns:
		The canonical |cmd|`explain-section` command for the given label and profile.
	Raises:
	See_also:
		explain_try_self_for_subsection
	"""
	return f"waterlint explain-section --label {label} --profile {profile}"

def explain_try_self_for_subsection(label: str, profile: str) -> str:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises, See_also
	Contract:
		general:
			|Must| build the canonical self-explanation command for a fully qualified subsection label and profile.
	Parameters:
		label:
			The fully qualified subsection label to explain.
		profile:
			The docstring profile to use as the explain context.
	Returns:
		The canonical |cmd|`explain-subsection` command for the given label and profile.
	Raises:
	See_also:
		explain_try_self_for_section
	"""
	return f"waterlint explain-subsection --label {label} --profile {profile}"

#----- source and expected snippet renderers -----------------#

def render_source_snippet(section_label: str | None, subsections: Iterable[str] | None = None) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact section snippet with canonical subsection ordering.
	Parameters:
		section_label:
			The section label to render.
		subsections:
			The subsection labels to render under the section label. If omitted, the canonical order for the
			section is used when available.
	Returns:
		A compact list of lines that renders the section label followed by subsection placeholders.
	Raises:
	"""
	canonical = CANONICAL_ORDER_OF_SECTIONS.get(section_label) if section_label is not None else None
	if subsections is None:
		ordered = list(canonical) if canonical is not None else []
	else:
		ordered = list(subsections)
		if canonical is not None:
			order = {name: index for index, name in enumerate(canonical)}
			ordered.sort(key=lambda name: order.get(name, len(order)))
	lines = [f"{section_label}:"] if section_label is not None else []
	for subsection in ordered:
		if section_label is not None:
			lines.append(f"\t{subsection}:")
			lines.append("\t\t...")
		else:
			lines.append(f"{subsection}:")
			lines.append("\t...")
	return lines


def render_expected_snippet(section_label: str | None, subsections: Iterable[str] | None = None) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render the canonical expected snippet for a section.
	Parameters:
		section_label:
			The section label to render.
		subsections:
			The subsection labels to render under the section label.
	Returns:
		The canonical expected section snippet as a list of lines.
	Raises:
	"""
	return render_source_snippet(section_label, subsections)


def _render_section_block(section_label: str | None, subsection_label: str | None, body_lines: Iterable[str]) -> list[str]:
	if section_label is not None:
		lines = [f"{section_label}:"]
		indent0 = "\t"
	else:
		lines = []
		indent0 = ""
	if subsection_label is not None:
		lines.append(f"\t{subsection_label}:")
		indent = indent0 + "\t"
	else:
		indent = indent0 + ""
	lines.extend(f"{indent}{line}" for line in body_lines)
	return lines


def _split_qualified_label(label: str) -> tuple[str | None, str | None]:
	if not label:
		return None, None
	if "." in label:
		section_label, subsection_label = label.split(".", 1)
		return section_label, subsection_label
	return label, None


def render_found_label(section_label: str | None, label: str) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact found snippet for a section label and an optional subsection label.
	Parameters:
		section_label:
			The outer section label to render.
		label:
			The found subsection label to render below the section label.
	Returns:
		A compact list of lines that states the found section or subsection.
	Raises:
	"""
	if not section_label:
		return [label]
	return _render_section_block(section_label, None, [label])


def render_allowed_identifier(label: str, identifiers: Iterable[str]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact snippet for a subsection that expects one identifier.
	Parameters:
		label:
			The subsection label to render.
		identifiers:
			The allowed identifier values.
	Returns:
		A compact list of lines that states the allowed identifier values in one line.
	Raises:
	"""
	section_label, subsection_label = _split_qualified_label(label)
	items = list(dict.fromkeys(identifiers))
	if not items:
		items = ["..."]
	return _render_section_block(section_label, subsection_label, [f"<one of: {{ {', '.join(items)} }}>"])


def render_expected_identifier(label: str, expected_kind: Literal["identifier", "qualified identifier"]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render the expected syntax for a single identifier-like value.
	Parameters:
		label:
			The subsection label to render.
		expected_kind:
			Use identifier or qualified identifier to describe the expected syntax class.
	Returns:
		A compact list of lines that states the expected syntax in the Waterloo snippet format.
	Raises:
	"""
	section_label, subsection_label = _split_qualified_label(label)
	return _render_section_block(section_label, subsection_label, [f"<{expected_kind}>"])

def render_suggestion(label: str | None, suggestion: str) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a suggestion snippet for a section or subsection in order to fix the docstring.
			|Must| add angle brackets around the suggestion to indicate that it is a placeholder for the actual content.
		requires:
			The suggestion |should| be a brief and concise plain single line text.
	Parameters:
		label:
			The section or subsection label (as qualified name) to render.
			An empty label means the suggestion is not bound to a specific section or subsection.
		suggestion:
			A brief suggestion of what the section or subsection could be or contain.
	Returns:
		A compact list of lines that states the suggested section or subsection in one line.
	Raises:
	"""
	if not label:
		return [f"<{suggestion}>"]
	section_label, subsection_label = _split_qualified_label(label)
	return _render_section_block(section_label, subsection_label, [f"<{suggestion}>"])

def render_allowed_identifiers(label: str, identifiers: Iterable[str]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact snippet for a subsection that expects a list of identifiers.
	Parameters:
		label:
			The subsection label to render.
		identifiers:
			The allowed identifier values.
	Returns:
		A compact list of lines that states the allowed identifier values in one line.
	Raises:
	"""
	section_label, subsection_label = _split_qualified_label(label)
	items = list(dict.fromkeys(identifiers))
	if not items:
		items = ["..."]
	return _render_section_block(section_label, subsection_label, [f"<some of: {{ {', '.join(items)} }}>"])

def render_allowed_labels(section_label: str | None, allowed: Iterable[str]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact snippet for a section that expects one of a fixed set of labels.
	Parameters:
		section_label:
			The section label to render.
		allowed:
			The allowed labels.
	Returns:
		A compact list of lines that states the allowed labels in one line.
	Raises:
	"""
	items = list(dict.fromkeys(allowed))
	if not items:
		items = ["..."]
	allowed_text = '", "'.join(items)
	return _render_section_block(section_label, None, [f"<some of: {{ {allowed_text} }}>"])


def render_identifier_lines(label: str, identifiers: Iterable[str]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render the found identifiers of a list-valued subsection in a compact form.
	Parameters:
		label:
			The subsection label to render.
		identifiers:
			The identifier values exactly as found.
	Returns:
		A compact list of lines that states the identifier values in one line without semantic normalization.
	Raises:
	"""
	section_label, subsection_label = _split_qualified_label(label)
	items = list(identifiers)
	if not items:
		items = ["..."]
	return _render_section_block(section_label, subsection_label, [", ".join(items)])


def render_deduplicated_identifiers(label: str, identifiers: Iterable[str]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact snippet for a subsection after removing duplicate identifiers.
	Parameters:
		label:
			The subsection label to render.
		identifiers:
			The identifier values with duplicates removed while preserving the first occurrence order.
	Returns:
		A compact list of lines that states the deduplicated identifier values in one line.
	Raises:
	"""
	section_label, subsection_label = _split_qualified_label(label)
	items = list(dict.fromkeys(identifiers))
	if not items:
		items = ["..."]
	lines = [f"{section_label}:"]
	if subsection_label is not None:
		lines.append(f"\t{subsection_label}:")
		lines.append(f"\t\t{', '.join(items)}")
	else:
		lines.append(f"\t{', '.join(items)}")
	return lines


def render_unique_identifiers(label: str, identifiers: Iterable[str]) -> list[str]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render a compact snippet for a subsection that requires unique identifiers.
	Parameters:
		label:
			The subsection label to render.
		identifiers:
			The canonical identifier values.
	Returns:
		A compact list of lines that states the canonical identifier values and mentions uniqueness.
	Raises:
	"""
	lines = render_deduplicated_identifiers(label, identifiers)
	section_label, subsection_label = _split_qualified_label(label)
	if subsection_label is not None:
		lines.append("\t\t(each identifier may occur at most once)")
	else:
		lines.append("\t(each identifier may occur at most once)")
	return lines

#----- diagnostics renderers for specific validation cases ---#

def render_normative_section_details(section_label: str, normative_sections: Iterable[str], profile: str, *, action: Literal["add", "remove"]) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for normative section membership checks.
	Parameters:
		section_label:
			The section label that should be added to or removed from the normative section set.
		normative_sections:
			The current normative section labels.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
		action:
			Either |value|`add` when the section should be present, or |value|`remove` when it should be absent.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	current = list(normative_sections)
	if action == "add":
		expected = [*current, section_label]
	else:
		expected = [item for item in current if item != section_label]
	return {
		"found": render_identifier_lines("Preamble.normative_sections", current),
		"expected": render_deduplicated_identifiers("Preamble.normative_sections", expected),
		"hint": explain_try_self_for_section(section_label, profile),
	}


def render_missing_entry_details(container_label: str, current_entries: Iterable[str], missing_entry: str, profile: str, *, top_level: bool = False) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a missing entry in a section-like container.
	Parameters:
		container_label:
			The section label that contains the missing entry.
		current_entries:
			The currently present entry labels in the container.
		missing_entry:
			The entry label that should be added.
		profile:
			The docstring profile used for the |cmd|`explain-*` hint.
		top_level:
			Use a top-level list rendering when the container itself is the document root rather than a nested section.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	current = list(current_entries)
	found = [e for e in current for e in (e, "\t...")]
	expected = [e for e in [*current, missing_entry] for e in (e, "\t...")]
	if top_level:
		# This is a special marker case for the document root level, which is not rendered
		# with a section header and therefore needs a custom label in the snippets and hints.
		return {
			"found": found,
			"expected": expected,
			"hint": explain_try_self_for_section(missing_entry, profile),
		}
	return {
		"found": render_source_snippet(container_label, current),
		"expected": render_expected_snippet(container_label, expected),
		"hint": explain_try_self_for_subsection(f"{container_label}.{missing_entry}", profile),
	}


def render_overview_requires_section_details(overview_label: str, required_section: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render compact validation details for overview sections that require a normative companion section.
	Parameters:
		overview_label:
			The overview section label, such as |label|`Class_overview`.
		required_section:
			The normative section that must be added, such as |label|`Public_classes`.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": [f"{overview_label}", "\t..."],
		"expected": [f"<add normative section {required_section}>"],
		"hint": explain_try_self_for_section(required_section, profile),
	}


def render_name_object_consistency_details(label: str, current_entries: Iterable[str], profile: str, *, overview_item: str | None = None) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render compact validation details for name/object consistency checks.
	Parameters:
		label:
			The section label to render.
		current_entries:
			The current raw entries from the section.
		profile:
			The docstring profile used for the hint.
		overview_item:
			If provided, render an overview entry instead of a flat identifier list.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	if overview_item is None:
		return {
			"found": render_identifier_lines(label, current_entries),
			"expected": ["<check name/object consistency>"],
			"hint": explain_try_self_for_section(label, profile),
		}
	return {
		"found": render_source_snippet(label, [overview_item]),
		"expected": ["<check name/object consistency>"],
		"hint": explain_try_self_for_subsection(f"'{label}.<item>'", profile),
	}


def render_listed_object_missing_details(label: str, member_name: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render compact validation details for a listed object that has no matching runtime object.
	Parameters:
		label:
			The section label to render.
		member_name:
			The listed entry name that has no matching object.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet(label, [member_name]),
		"expected": [expected_text],
		"hint": explain_try_self_for_section(label, profile),
	}


def render_profile_mismatch_details(object_name: str, object_kind: str, current_profile: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| render compact validation details for a profile mismatch.
	Parameters:
		object_name:
			The documented object name.
		object_kind:
			The detected object kind such as module, class, function or method-like.
		current_profile:
			The profile found in the docstring.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	expected_text = expected_text.strip()
	if expected_text.startswith("<") and expected_text.endswith(">") and len(expected_text) >= 2:
		expected_text = expected_text[1:-1].strip()
	return {
		"found": [
			"Preamble",
			"\tprofile:",
			f"\t\t{current_profile}",
		],
		"expected": render_suggestion("Preamble.profile", expected_text),
		"hint": explain_try_self_for_subsection("Preamble.profile", profile),
	}


def render_normativity_keyword_details(section_label: str, entry_name: str, current_lines: Iterable[str], suggestion: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for an entry that must not contain normativity keywords.
	Parameters:
		section_label:
			The overview section label, such as |label|`Class_overview`.
		entry_name:
			The entry label that violates the rule.
		current_lines:
			The raw lines found in the entry.
		suggestion:
			A brief informative replacement suggestion for the entry.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	found_lines = list(current_lines)
	if not found_lines:
		found_lines = ["..."]
	return {
		"found": [f"{section_label}:", f"\t{entry_name}:"] + [f"\t\t{line}" for line in found_lines],
		"expected": [f"{section_label}:", f"\t{entry_name}:", f"\t\t<{suggestion}>"],
		"hint": explain_try_self_for_section(section_label, profile),
	}


def render_exception_reference_details(exception_name: str, profile: str, *, expected_kind: Literal["qualified identifier", "subclass of BaseException"]) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a Raises entry that must resolve to an exception class.
	Parameters:
		exception_name:
			The exception entry name found in the Raises section.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
		expected_kind:
			Either |value|`qualified identifier` or |value|`subclass of BaseException`.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	if expected_kind == "qualified identifier":
		expected = ["<check for typos or qualify properly>"]
	else:
		expected = ["<refer to an Exception class derived from BaseException>"]
	return {
		"found": render_source_snippet("Raises", [exception_name]),
		"expected": expected,
		"hint": explain_try_self_for_subsection("Raises.<item>", profile),
	}


def render_base_method_reference_details(current_entries: Iterable[str], expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a Contract.base reference problem.
	Parameters:
		current_entries:
			The current raw entries found in Contract.base.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	current = [str(item) for item in current_entries]
	expected_text = expected_text.strip()
	if expected_text.startswith("<") and expected_text.endswith(">") and len(expected_text) >= 2:
		expected_text = expected_text[1:-1].strip()
	return {
		"found": render_source_snippet("Contract.base", current),
		"expected": render_suggestion("Contract.base", expected_text),
		"hint": [f"waterlint explain-subsection --label Contract.base --profile {profile}"],
	}


def render_exactly_one_identifier_details(label: str, current_entries: Iterable[str], profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a subsection that must contain exactly one identifier.
	Parameters:
		label:
			The qualified subsection label to render in the snippets and hint.
		current_entries:
			The current raw entries from the subsection.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	current = list(current_entries)
	return {
		"found": render_identifier_lines(label, current),
		"expected": render_expected_identifier(label, "identifier"),
		"hint": explain_try_self_for_subsection(label, profile),
	}


def render_parameter_signature_details(section_label: str, current_entries: Iterable[str], expected_entries: Iterable[str], profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a parameter/signature mismatch.
	Parameters:
		section_label:
			The label to render in the snippets.
		current_entries:
			The current raw parameter entries.
		expected_entries:
			The corrected parameter entries to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	current = list(current_entries)
	expected = list(expected_entries)
	return {
		"found": render_source_snippet(section_label, current),
		"expected": render_expected_snippet(section_label, expected),
		"hint": explain_try_self_for_section(section_label, profile),
	}


def render_see_also_reference_details(reference: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a See_also reference mismatch.
	Parameters:
		reference:
			The raw reference text as found in the See_also section.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-section` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet("See_also", [reference]),
		"expected": [expected_text],
		"hint": [f"waterlint explain-section --label See_also --profile {profile}"],
	}


def render_scope_relation_details(
	containing_kind: str,
	containing_scopes: Scopes,
	is_containing_scope_explicit: bool,
	contained_kind: str,
	contained_scopes: Scopes,
	is_contained_scope_explicit: bool,
	section_label: str,
	reference: str,
	expected_text: str,
	profile: str,
) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a scope monotonicity violation.
	Parameters:
		containing_kind:
			The kind of the containing object, such as module or class.
		containing_scopes:
			The scopes of the containing object.
		is_containing_scope_explicit:
			Whether the containing object declared its scope explicitly.
		contained_kind:
			The kind of the contained object, such as function, class, or method.
		contained_scopes:
			The scopes of the contained object.
		is_contained_scope_explicit:
			Whether the contained object declared its scope explicitly.
		section_label:
			The section label to render.
		reference:
			The offending reference as found in the source section.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	def _render_scope_block(kind: str, scopes: Scopes, is_explicit: bool, *, name: str | None = None) -> list[str]:
		scope_values = ", ".join(scope_to_string[scope] for scope in sorted(scopes, key=lambda s: getattr(s, "value", 0)))
		scope_state = "<explicit>" if is_explicit else "<implicit>"
		label = f"<in docstring of {kind}>" if name is None else f"<in docstring of {kind} '{name}'>"
		return [label, "Preamble:", "\tscope:", f"\t\t{scope_values} {scope_state}"]

	return {
		"found": _render_scope_block(containing_kind, containing_scopes, is_containing_scope_explicit)
					+ render_source_snippet(section_label, [reference])
					+ _render_scope_block(contained_kind, contained_scopes, is_contained_scope_explicit, name=reference),
		"expected": [expected_text],
		"hint": [f"waterlint explain-subsection --label Preamble.scope --profile {profile}"],
	}


def render_base_method_docstring_details(base_name: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a base-method docstring problem.
	Parameters:
		base_name:
			The base method name found in Contract.base.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_identifier_lines("Contract.base", [base_name]),
		"expected": ["<implement a Waterloo docstring in base method>"],
		"hint": [f"waterlint explain-subsection --label Contract.base --profile {profile}"],
	}


def render_definition_reference_details(references: str | Iterable[str], profile: str, *, missing_definitions: bool) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a term reference problem in Definitions.
	Parameters:
		references:
			The term reference or term references found in the docstring body.
		profile:
			The docstring profile used for the |cmd|`explain-section` or |cmd|`explain-subsection` hint.
		missing_definitions:
			Whether the Definitions section itself is missing.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	if isinstance(references, str):
		current = [references]
	else:
		current = [str(reference) for reference in references]
	if missing_definitions:
		return {
			"found": render_identifier_lines("term refs", sorted(dict.fromkeys(current))),
			"expected": ["<add normative section Definitions>"],
			"hint": explain_try_self_for_section("Definitions", profile),
		}
	return {
		"found": render_identifier_lines("term", current[:1] if current else ["..."]),
		"expected": ["<define term in Definitions>"],
		"hint": explain_try_self_for_subsection("Definitions.<item>", profile),
	}


def render_inherited_definition_details(current_inherited_terms: Iterable[str], profile: str, *, expected_text: str, use_section_hint: bool = False) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for an inherited Definitions problem.
	Parameters:
		current_inherited_terms:
			The inherited definition terms found in the current object.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		use_section_hint:
			Whether the hint should point to the section-level |cmd|`explain-section` entry instead of the
			subsection-level inherited definition entry.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	current = list(dict.fromkeys(str(term) for term in current_inherited_terms))
	if use_section_hint:
		hint = explain_try_self_for_section("Definitions", profile)
	else:
		hint = explain_try_self_for_subsection("Definitions._inherit", profile)
	return {
		"found": render_identifier_lines("Definitions._inherit", current if current else ["..."]),
		"expected": [expected_text],
		"hint": hint,
	}


def render_type_reference_details(label: str, type_name: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a Public_types reference problem.
	Parameters:
		label:
			The subsection label to render.
		type_name:
			The type entry name found in the subsection.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet(label, [type_name]),
		"expected": [expected_text],
		"hint": explain_try_self_for_subsection(f"'{label}.<item>'", profile),
	}


def render_constant_reference_details(label: str, const_name: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a Public_constants reference problem.
	Parameters:
		label:
			The subsection label to render.
		const_name:
			The constant entry name found in the subsection.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet(label, [const_name]),
		"expected": [expected_text],
		"hint": explain_try_self_for_subsection(f"'{label}.<item>'", profile),
	}


def render_named_value_reference_details(label: str, name: str, expected_text: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for a Public_variables reference problem.
	Parameters:
		label:
			The subsection label to render.
		name:
			The variable entry name found in the subsection.
		expected_text:
			The minimal correction or instruction to show in the expected snippet.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet(label, [name]),
		"expected": [expected_text],
		"hint": explain_try_self_for_subsection(f"'{label}.<item>'", profile),
	}


def render_overview_missing_member_details(overview_label: str, public_label: str, current_entries: Iterable[str], missing_name: str, profile: str) -> dict[str, Any]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| build standardized validation details for an overview entry that is missing from its matching Public_* section.
	Parameters:
		overview_label:
			The overview section label, such as |label|`Class_overview`.
		public_label:
			The matching public section label, such as |label|`Public_classes`.
		current_entries:
			The current raw entries from the overview section.
		missing_name:
			The entry name that is missing from the public section.
		profile:
			The docstring profile used for the |cmd|`explain-subsection` hint.
	Returns:
		A details dictionary with |attr|`found`, |attr|`expected`, and |attr|`hint`.
	Raises:
	"""
	return {
		"found": render_source_snippet(overview_label, [missing_name] + [str(item) for item in current_entries if str(item) != missing_name]),
		"expected": [f"<add {missing_name} to {public_label}>"],
		"hint": explain_try_self_for_subsection(f"'{public_label}.<item>'", profile),
	}

#===== end render functions for verbose diagnostics ==========#
