from __future__ import annotations
from typing import Any, Callable, Dict, Final, Mapping, TYPE_CHECKING, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, Literal, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypedDict, TypeGuard, Union, cast
from enum import Enum,IntEnum

from sdv.doc.waterloo.docitem_types import (
	DocstringSubtree,
	DocstringTree,
	AnnotatableObject,
	RuleId,
	Origin,
	Details,
	Scope,
	Scopes,
	Documentable,
	WTRL_TRACER_JSON_SCHEMA_VERSION,
	RE_RULE_ID_COMPILED
	)

import re, copy
from datetime import datetime

from contextlib import contextmanager

#===== Tracing ================================================#
class tracer:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_types, Public_classes, Public_methods
	Terminology:
		rules on fail:
			Low-level functions may find a parsing or validation warning or error,
			but have no clue which rule has been violated. The |dfn|`rules on fail`
			mechanism allows the caller to pass the set of rules in question.
			The tracer provides a stack and api for these rule sets.
	Contract:
		general:
			|Must| provide a string-valued stack API for storing context data, like "which object/section/subsection are we in?".
			|Must| provide a to-string method for rendering the context.

			|Must| maintain a list of infos, where each entry is a tuple consisting of context, origin, and a free-form message.
			|Must| provide a method for adding such a info entry.
			|Must| allow to query if infos have been added.
			|Must| provide a method for clearing the list of infos.
			|Must| provide a method for rendering the list of infos as a string.
			|Must| provide a generator which allows iterating over the list of infos.

			|Must| maintain a list of warnings, where each entry is a tuple consisting of context, one Rule-ID, origin, a free-form message, and optional details.
			|Must| provide a method for adding such a warning entry.
			|Must| allow to query if warnings have been added.
			|Must| provide a method for clearing the list of warnings.
			|Must| provide a method for rendering the list of warnings as a string.
			|Must| provide a generator which allows iterating over the list of warnings.

			|Must| maintain a list of errors, where each entry is a tuple consisting of context, one Rule-ID, origin, a free-form message, and optional details.
			|Must| provide a method for adding such a error entry.
			|Must| allow to query if errors have been added.
			|Must| provide a method for clearing the list of errors.
			|Must| provide a method for rendering the list of errors as a string.
			|Must| provide a generator which allows iterating over the list of errors.

			|Must| manage a set of ignore-rule instructions

			|Must| provide a stack containing the current |dfn|`rule on fail` being validated against.
			|Must| provide an api like |func|`push...`, |func|`pop...`, |func|`get...` for the |dfn|`rule on fail` stack.

			|Must| provide a stack containing the current set of |dfn|`scopes` being validated against.
			|Must| provide an api like |func|`push...`, |func|`pop...`, |func|`get...` for the |dfn|`scopes` stack.
		constructor:
			|Must| be default-constructible.
	Public_types:
		Context:
			A list of strings built per context manager during parsing and validation.\
			Entries can be module, class or function names, or labels.
	Public_classes:
		Severity
	Class_overview:
		Severity:
			An enum with values DEBUG, INFO, WARNING, ERROR for filtering the output of the tracer.
	Public_methods:
		build_json, str_by_severity
	Method_overview:
		build_json:
			Build a JSON-serializable |type|`dict` containing the
			information in the tracer, filtered by severity and optionally enriched by metadata.
	Notes:
		Last review:
			2026-06-21
		Parameter 'details':
			The details payload is important for the MCP server, because it gives the LLM enough debugging context to interpret tracer output and decide how to react to it.
			It usually is a dict with keys "found", "expected", and "hint"; "hint" typically contains a waterlint call for retrieving more information about the affected section or subsection.
	"""
	Context: TypeAlias = List[str]
	class Severity(IntEnum):
		r"""
		Preamble:
			profile:
				class
			normative_sections:
				Contract, Derived_from
		Contract:
			general:
				|Must| define the following severity levels for filtering the tracer's output:
				|value|`DEBUG`: for debugging notes, not relevant for end-users.
				|value|`INFO`: for informational messages that are relevant for end-users but do not indicate any problems.
				|value|`WARNING`: for potential issues that should be looked at but do not necessarily indicate a failure.
				|value|`ERROR`: for definite problems that indicate a failure to meet a requirement or rule.
				|Must| assign integer values to these levels in increasing order of severity, starting with 0 for DEBUG.
			constructor:
				|Must| inherit from |type|`IntEnum`.
		Derived_from:
			IntEnum
		"""
		DEBUG		= 0,
		INFO		= 1,
		WARNING		= 2
		ERROR		= 3

	RE_ANSI_ESCAPE_SEQUENCE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")

	@classmethod
	def strip_ansi_escape_sequences(cls,s: str) -> str:
		return cls.RE_ANSI_ESCAPE_SEQUENCE.sub("", s)

	def __init__(self) -> None:
		self._names : List[str] = []
# Debugging notes
		self._debug : List[Tuple[tracer.Context,Origin,str]] = []
# Infos
		self._infos : List[Tuple[tracer.Context,Origin,str]] = []
# This is a list of warnings, where each entry consists of a RuleID and a free-form text.
		self._warnings : List[Tuple[tracer.Context,RuleId,Origin,str,Details]] = []
		self._errors : List[Tuple[tracer.Context,RuleId,Origin,str,Details]] = []
# Rules to ignore
		self._ignrules : Set[str] = set()
# Rule in case a low-level function fails. We make sure there is always a rule
# so nothing will crash, but of course we don't want to see this one.
		self._rule_on_fail : List[RuleId] = ["YYY-999"]
# The scopes for validation. Successful validation requires that rules
# SCP-### are fulfilled. The default is a set with a single element CORE
		self._scopes : List[Scopes] = [set([Scope.CORE])]

	def __str__(self) -> str:
		return self.str_by_severity(self.Severity.DEBUG)
	def _format_diagnostic_details(self, details: Details) -> str:
		lines: list[str] = []
		label_color = "\x1b[38;2;119;119;119m"
		label_reset = "\x1b[0m"
		for key in ("found", "expected"):
			value = details.get(key)
			if isinstance(value, list) and value:
				lines.append(f"\t{label_color}{key}:{label_reset}")
				for line in value:
					if isinstance(line, str):
						lines.append(f"\t\t{line}")
			elif isinstance(value, str) and value:
				lines.append(f"\t{label_color}{key}:{label_reset}")
				lines.append(f"\t\t{value}")
		hint = details.get("hint")
		if isinstance(hint, str) and hint:
			lines.append(f"\t{label_color}hint:{label_reset}")
			lines.append(f"\t\t{hint}")
		elif isinstance(hint, list) and hint:
			lines.append(f"\t{label_color}hint:{label_reset}")
			for line in hint:
				if isinstance(line, str) and line:
					lines.append(f"\t\t{line}")
		return "".join(f"{line}\n" for line in lines)
	def _format_diagnostic_line(self, kind: str, origin: Origin, context: tracer.Context, rule_id: RuleId | None, msg: str, details: Details | None = None) -> str:
		color_map = {
			"Debug": "\x1b[35m",
			"Info": "\x1b[32m",
			"Warning": "\x1b[33m",
			"Error": "\x1b[31m",
		}
		color = color_map.get(kind, "\x1b[0m")
		head = f"- {color}{kind}\x1b[0m [{origin}] - [{'->'.join(context)}]"
		if rule_id is not None:
			head += f" [Rule {rule_id}]"
		head += f" {msg}\n"
		if isinstance(details, dict) and details:
			head += self._format_diagnostic_details(details)
		return head
# Refcopy debug, infos, warnings from tr to self.
# Refcopy errors from tr to self as warnings.
# We use this e.g. in waterlint render-json.
	def append_and_defuse(self,tr: tracer) -> None:
		for msg_dbg in tr._debug:
			self._debug.append(msg_dbg)
		for msg_inf in tr._infos:
			self._infos.append(msg_inf)
		for msg_wrn in tr._warnings:
			if self.should_ignore_rule(msg_wrn[1]):
				continue
			self._warnings.append(msg_wrn)
# Defusing: errors in tr become warnings in self.
		for msg_err in tr._errors:
			if self.should_ignore_rule(msg_err[1]):
				continue
			self._warnings.append(msg_err)
# For humans
	def str_by_severity(self,severity: Severity) -> str:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| render the tracer's content as a human-readable string, filtered by severity level.
				|Must| include entries with severity level equal to or higher than the specified level.
				|Must| format entries with clear labels and context for easy understanding.
		Parameters:
			severity:
				Only include entries with this severity level or higher.
				Levels are ordered as DEBUG < INFO < WARNING < ERROR.
		Returns:
			A string representation of the tracer's content, including entries
			up to the specified severity level, formatted for human readability.
		Raises:
		Notes:
			Called by:
				This method is invoked by the __str__ method, which defaults to showing all entries (DEBUG level),
				so generally you simply call |func|`str`(tracer_instance) to get the full content
				or |func|`print`(tracer_instance) to display it. 
		"""
		t = ""
		t += "----- Tracer-----8<---------------------------------------------\n"
		if severity <= self.Severity.DEBUG:
			t += self.to_string_debug_notes()
		if severity <= self.Severity.INFO:
			t += self.to_string_infos()
		if severity <= self.Severity.WARNING:
			t += self.to_string_warnings()
		if severity <= self.Severity.ERROR:
			t += self.to_string_errors()
		t += "----- Tracer----->8---------------------------------------------\n"
		return t
	def build_json(
		self,
		severity: Severity,
		*,
		schema_version: str | None = None,
		waterloo_version: str | None = None,
		id_prefix: str | None = None,
		include_debug: bool = True,
	) -> dict[str, Any]:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| build a JSON-serializable |type|`dict` containing the tracer's data, following the WTRL Tracer JSON Schema.
				|Must| include entries up to the specified severity level.
				|Must| allow including debug notes optionally, as they may contain sensitive or verbose information.
				|Must| include schema version and optionally Waterloo version in the metadata section.
		Parameters:
			severity:
				Only include entries with this severity level or higher.
				Levels are ordered as DEBUG < INFO < WARNING < ERROR.
			schema_version:
				Specify the WTRL Tracer JSON Schema version to declare in the output. Defaults to the current version if not provided.
				This does not affect the structure of the output, which always follows the current schema.
				Including the schema version allows consumers to validate against the correct schema and maintain compatibility as the schema evolves.
				* |Must| be a string in the format |lit|`X.Y.Z` where X, Y, and Z are non-negative integers.
				* |Must| default to the current schema version if not provided.
				* |Must| be included in the output under the `__WTRL_VERSION__` metadata section.
				* |Must_not| affect the actual structure of the output, which always follows the current schema.
			waterloo_version:
				Optionally include the version of the Waterloo tool that generated the tracer data.
				* |Must| be a string in the format |lit|`X.Y.Z` where X, Y, and Z are non-negative integers.
			id_prefix:
				Optionally include a prefix for the `$id` field in the output JSON.
				* |Must| be a string if provided.
				* |May| be omitted, in which case the `$id` field will not include a prefix.
			include_debug:
				Optionally include debug notes in the output JSON.
		Returns:
			A JSON-serializable |type|`dict` containing the tracer's data structured according to the WTRL Tracer JSON Schema,
			including entries up to the specified severity level and metadata about the schema and optionally the Waterloo version.
			The return value |must| conform to JSON Schema :file:`wtrl-tracer-json-X.Y.Z.schema.json` where X.Y.Z is the declared schema version.
		Raises:
		"""
		def _lift_diagnostic_fields(entry: dict[str, Any], details: Details | None = None) -> Details:
			if not isinstance(details, dict):
				return {}
			details_payload = dict(details)
			for key in ("expected", "found", "hint"):
				if key in details_payload:
					entry[key] = details_payload.pop(key)
			return details_payload
		schema_version = WTRL_TRACER_JSON_SCHEMA_VERSION if schema_version is None else schema_version
		doc: dict[str, Any] = {
			"$schema": f"https://sci-d-vis.com/schema/wtrl-tracer-json-{schema_version}.schema.json",
			"__WTRL_VERSION__": {
				"schema": schema_version,
			},
			"__WTRL_INFO__": [],
			"__WTRL_WARNING__": [],
			"__WTRL_ERROR__": [],
		}
		if waterloo_version is not None:
			cast(dict[str, Any], doc["__WTRL_VERSION__"])["waterloo"] = waterloo_version
		if id_prefix is not None:
			doc["$id"] = f"{id_prefix}:{datetime.now().strftime('%Y%m%d%H%M%S')}"
		if include_debug and severity <= self.Severity.DEBUG:
			doc["__WTRL_DEBUG__"] = []
#----- Debug notes --------------------------------------------#
		if include_debug and severity <= self.Severity.DEBUG:
			for context,origin,msg in self.gen_debug_notes():
				dentry: dict[str, Any] = {"kind": "debug", "origin": origin, "msg": msg}
				dentry["context"] = context
				cast(list[dict[str, Any]], doc["__WTRL_DEBUG__"]).append(dentry)
#----- Infos --------------------------------------------------#
		if severity <= self.Severity.INFO:
			for context,origin,msg in self.gen_infos():
				entry: dict[str, Any] = {"kind": "info", "origin": origin, "msg": msg}
				entry["context"] = context
				cast(list[dict[str, Any]], doc["__WTRL_INFO__"]).append(entry)
#----- Warnings -----------------------------------------------#
		if severity <= self.Severity.WARNING:
			for context,rule_id,origin,msg,details in self.gen_warnings():
				entry = {"kind": "warning", "origin": origin, "rule-id": rule_id, "msg": msg}
				entry["context"] = context
				entry["details"] = _lift_diagnostic_fields(entry, details)
				cast(list[dict[str, Any]], doc["__WTRL_WARNING__"]).append(entry)
#----- Errors -------------------------------------------------#
		if severity <= self.Severity.ERROR:
			for context,rule_id,origin,msg,details in self.gen_errors():
				entry = {"kind": "error", "origin": origin, "rule-id": rule_id, "msg": msg}
				entry["context"] = context
				entry["details"] = _lift_diagnostic_fields(entry, details)
				cast(list[dict[str, Any]], doc["__WTRL_ERROR__"]).append(entry)
		return doc

#----- Context ------------------------------------------------#
	def push(self,name : str) -> None:
		self._names.append(name)
	def pop(self) -> str:
		name = self._names[-1]
		del self._names[-1]
		return name
	def has_top(self,name : str) -> bool:
		return self._names[-1] == name if len(self._names) > 0 else False
	def to_string(self) -> str:
		return "->".join(self._names)
#----- Debug --------------------------------------------------#
	def clear_debug_notes(self) -> None:
		self._debug = []
	def has_debug_notes(self) -> bool:
		return len(self._debug) > 0
	def add_debug_note(self,msg : str,origin: Origin = "tool") -> None:
		self._debug.append((copy.copy(self._names),origin,msg))
	def to_string_debug_notes(self) -> str:
		return "".join([self._format_diagnostic_line("Debug", origin, context, None, msg) for context,origin,msg in self._debug])
# Implement your own pretty printing.
	def gen_debug_notes(self) -> Generator[Tuple[tracer.Context,Origin,str],None,None]:
		for context,origin,msg in self._debug:
			yield context,origin,msg
#----- Infos --------------------------------------------------#
	def clear_infos(self) -> None:
		self._infos = []
	def has_infos(self) -> bool:
		return len(self._infos) > 0
	def add_info(self,msg : str,origin: Origin = "tool") -> None:
		self._infos.append((copy.copy(self._names),origin,msg))
	def to_string_infos(self) -> str:
		return "".join([self._format_diagnostic_line("Info", origin, context, None, msg) for context,origin,msg in self._infos])
# Implement your own pretty printing.
	def gen_infos(self) -> Generator[Tuple[tracer.Context,Origin,str],None,None]:
		for context,origin,msg in self._infos:
			yield context,origin,msg
#----- Warnings -----------------------------------------------#
	def clear_warnings(self) -> None:
		self._warnings = []
	def has_warnings(self) -> bool:
		return len(self._warnings) > 0
	def add_warning(self,rule_id : RuleId, origin: Origin, msg : str,/,details: Details | None = None) -> None:
		self._warnings.append((copy.copy(self._names),rule_id,origin,msg,details or {}))
	def to_string_warnings(self) -> str:
		return "".join([self._format_diagnostic_line("Warning", origin, context, rid, msg, details) for context,rid,origin,msg,details in self._warnings])
# Implement your own pretty printing.
	def gen_warnings(self) -> Generator[Tuple[tracer.Context,RuleId,Origin,str,Details],None,None]:
		for context,rid,origin,msg,details in self._warnings:
			yield context,rid,origin,msg,details
#----- Errors -------------------------------------------------#
	def clear_errors(self) -> None:
		self._errors = []
	def has_errors(self) -> bool:
		return len(self._errors) > 0
	def add_error(self,rule_id : RuleId, origin: Origin, msg : str,/,details: Details | None = None) -> None:
		self._errors.append((copy.copy(self._names),rule_id,origin,msg,details or {}))
	def to_string_errors(self) -> str:
		return "".join([self._format_diagnostic_line("Error", origin, context, rid, msg, details) for context,rid,origin,msg,details in self._errors])
# Implement your own pretty printing.
	def gen_errors(self) -> Generator[Tuple[tracer.Context,RuleId,Origin,str,Details],None,None]:
		for context,rid,origin,msg,details in self._errors:
			yield context,rid,origin,msg,details
#----- Ignores ------------------------------------------------#
	def clear_ignored(self) -> None:
		self._ignrules = set()
	def add_ignore_rule(self,rule : str) -> None:
		if not RE_RULE_ID_COMPILED.fullmatch(rule):
			raise RuntimeError(f"Bad rule specifier: expected 'ABC[D...]-123[4..]', got '{rule}'.")
		self._ignrules.add(rule)
	def should_ignore_rule(self,rule : str) -> bool:
		return rule in self._ignrules
	def gen_ignore_rules(self) -> Generator[str,None,None]:
		for rule in self._ignrules:
			yield rule
#----- Rules on fail ------------------------------------------#
	def clear_rule_on_fail(self) -> None:
		self._rule_on_fail = ["YYY-999"]
	def push_rule_on_fail(self,rule_id : RuleId) -> None:
		self._rule_on_fail.append(rule_id)
	def pop_rule_on_fail(self) -> None:
		del self._rule_on_fail[-1]
	def get_rule_on_fail(self) -> RuleId:
		return self._rule_on_fail[-1]
#----- Scopes -------------------------------------------------#
	def clear_scopes(self) -> None:
		self._scopes = []
	def push_scopes(self,scopes : Scopes) -> None:
		self._scopes.append(scopes)
	def pop_scopes(self) -> None:
		del self._scopes[-1]
	def get_scopes(self) -> Scopes:
		return self._scopes[-1]

@contextmanager
def traced_section(tr: tracer, name: str) -> Generator[None, None, None]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| temporarily push |var|`name` onto the tracer context unless it is already on top.
	Parameters:
		tr:
			The tracer whose context stack should be managed.
		name:
			The context name to push.
	Returns:
		A context manager yielding nothing.
	Raises:
	"""
	something_pushed = False
	if not tr.has_top(name):
		tr.push(name)
		something_pushed = True
	try:
		yield
	finally:
		if something_pushed:
			tr.pop()
@contextmanager
def rule_on_fail(tr: tracer, rule_id: RuleId) -> Generator[None, None, None]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			public
	Contract:
		general:
			|Must| temporarily push the given rule identifier onto the tracer's rule-on-fail stack.
	Parameters:
		tr:
			The tracer whose failure-rule stack should be managed.
		rule_id:
			The rule identifier to push for the duration of the context.
	Returns:
		A context manager yielding nothing.
	Raises:
	"""
	tr.push_rule_on_fail(rule_id)
	try:
		yield
	finally:
		tr.pop_rule_on_fail()
