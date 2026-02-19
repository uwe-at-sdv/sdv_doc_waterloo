from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

try:
	from sdv_doc_docitem_tokenizer import *
except ImportError:
	from sdv.doc.waterloo.docitem_tokenizer import *

try:
	from sdv_doc_docitem_base import *
except ImportError:
	from sdv.doc.waterloo.docitem_base import *

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
			raise_parsing_error_expected_but_got(tr,"PRE-014",'str','list')
# Only exactly one item is allowed
		if len(refs) != 1:
			raise_parsing_error_expected_but_got(tr,"PRE-004",'exactly one item',f'{refs}')
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
			raise_parsing_error_expected_but_got(tr,"STA-002",'str','list')
# Only exactly one item is allowed
		if len(refs) != 1:
			raise_parsing_error_expected_but_got(tr,"STA-002",'exactly one item',f'{refs}')
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
				raise_parsing_error_invalid_label(tr,"PRE-015",label,dispatch_map)
			items,pos = expect_list(tr,subtree,pos)
			self.add_child(tr,label, dispatch_map[label], items)
	def __str__(self) -> str:
		return " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"

#===== end section Preamble ===================================#
