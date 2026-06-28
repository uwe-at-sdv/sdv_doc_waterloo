from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

from sdv.doc.waterloo.docitem_tokenizer import *
from sdv.doc.waterloo.docitem_base import *
from sdv.doc.waterloo.docitem_diagnostics import explain_try_self_for_section, explain_try_self_for_subsection, render_allowed_labels, render_found_label, render_identifier_lines, render_suggestion

#===== begin section Preamble =================================#

#----- docitem class profile  ---------------------------------#
# By the profile we distinguish between docstrings for
# classes, methods, functions and mybe others.
class docitem_profile(docitem_list_of_symbols_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`profile` section, subsection of |label|`Preamble`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_of_symbols_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`profile` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "profile"
	def diagnostics_label(self) -> str:
		return "Preamble.profile"
	def parse(self,tr : tracer,refs : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a |label|`profile` section.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	refs:
		The docstring subtree to parse.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the number of items is not |value|`1`.
		|Must| raise if the item is not a string (no subtrees allowed).
		|Must| raise if the item is not an identifier.
		"""
# Validate
		if not is_list_of_str(refs):
			details: Details = {
				"found": render_found_label(None, f"{refs!r}"),
				"expected": render_suggestion(None, "a list of strings"),
				"hint": ["Use one string per entry."],
			}
			raise_parsing_error(tr,"PRE-014","expected list of strings", details)
# Only exactly one item is allowed
		if len(refs) != 1:
			details = {
				"found": render_identifier_lines("Preamble.profile", refs),
				"expected": render_suggestion("Preamble.profile", "exactly one item"),
				"hint": explain_try_self_for_subsection("Preamble.profile", "PROFILE"),
			}
			raise_parsing_error(tr,"PRE-004","Section 'Preamble.profile' must have exactly one item.", details)
# No need to set a default rule. _parse in the base class is
# a complete implementation of rules LQID-001 to LQID-005.
		super()._parse(tr, cast(DocstringSubtree,refs), docitem_list_of_symbols_base.ValuePattern.IDENTIFIER)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem class normative_sections -----------------------#

class docitem_normative_sections(docitem_list_of_symbols_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`normative_sections` section, subsection of |label|`Preamble`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_of_symbols_base
Public_methods:
	parse
Method_overview:
	parse:
		Inherited method
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "normative_sections"
	def diagnostics_label(self) -> str:
		return "Preamble.normative_sections"
	def parse(self, tr: tracer, refs: DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		inherited_method
	normative_sections:
		Contract
Contract:
	general:
		|Must| set rules-on-fail in the tracer and delegate to the base implementation.
	base:
		sdv.doc.waterloo.docitem.docitem_base.parse
		"""
# No need to set a default rule. _parse in the base class is
# a complete implementation of rules LQID-001 to LQID-005.
		super()._parse(tr, refs, docitem_list_of_symbols_base.ValuePattern.IDENTIFIER)

#----- docitem class status  ----------------------------------#
class docitem_status(docitem_list_of_symbols_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`status` section, subsection of |label|`Preamble`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_of_symbols_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`status` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "status"
	def diagnostics_label(self) -> str:
		return "Preamble.status"
	def parse(self,tr : tracer,refs : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a |label|`status` section.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	refs:
		The docstring subtree to parse.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the number of items is not |value|`1`.
		|Must| raise if the item is not a string (no subtrees allowed).
		|Must| raise if the item is not an identifier.
		"""
# Validate
		if not is_list_of_str(refs):
			details: Details = {
				"found": render_found_label(None, f"{refs!r}"),
				"expected": render_suggestion(None, "a list of strings"),
				"hint": ["Use one string per entry."],
			}
			raise_parsing_error(tr,"STA-002","expected list of strings", details)
# Only exactly one item is allowed
		if len(refs) != 1:
			details = {
				"found": render_identifier_lines("Preamble.status", refs),
				"expected": render_suggestion("Preamble.status", "exactly one item"),
				"hint": explain_try_self_for_subsection("Preamble.status", "PROFILE"),
			}
			raise_parsing_error(tr,"STA-002","Subsection 'Preamble.status' must have exactly one item.", details)
# No need to set a default rule. _parse in the base class is
# a complete implementation of rules LQID-001 to LQID-005.
		super()._parse(tr, cast(DocstringSubtree,refs), docitem_list_of_symbols_base.ValuePattern.IDENTIFIER)

	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem class scope ------------------------------------#

class docitem_scope(docitem_list_of_symbols_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`scope` section, subsection of |label|`Contract`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_of_symbols_base
Public_methods:
	parse
Method_overview:
	parse:
		Inherited method
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "scope"
	def diagnostics_label(self) -> str:
		return "Preamble.scope"
	def parse(self, tr: tracer, refs: DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		inherited_method
	normative_sections:
		Contract
Contract:
	general:
		|Must| set rules-on-fail in the tracer and delegate to the base implementation.
	base:
		sdv.doc.waterloo.docitem.docitem_base.parse
		"""
# No need to set a default rule. _parse in the base class is
# a complete implementation of rules LQID-001 to LQID-005.
		super()._parse(tr, refs, docitem_list_of_symbols_base.ValuePattern.IDENTIFIER)

#----- docitem class preamble ---------------------------------#

class docitem_preamble(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`Preamble` section.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`Preamble` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Preamble"
	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the subsections of a |label|`Preamble` section.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if a subsection is not one of the allowed ones: {profile,normative_sections}.
		"""
		pos = 0
		dispatch_map = {
			"profile":docitem_profile,
			"normative_sections":docitem_normative_sections,
			"status":docitem_status,
			"scope":docitem_scope,
			}
		while pos < len(subtree):
			with rule_on_fail(tr, "PRE-015"):
				label,pos = expect_label_identifier(tr,subtree,pos)
			if label not in dispatch_map:
				details: Details = {
					"found": render_found_label("Preamble", label),
					"expected": render_allowed_labels("Preamble", dispatch_map),
					"hint": explain_try_self_for_section("Preamble", "PROFILE"),
				}
				raise_parsing_error(tr,"PRE-015",label,details)
			items,pos = expect_list(tr,subtree,pos)
			self.add_child(tr,label, dispatch_map[label], items)
	def __str__(self) -> str:
		return " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"

#===== end section Preamble ===================================#
