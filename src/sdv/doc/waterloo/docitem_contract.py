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

#===== begin section Contract =================================#

#----- docitem class constructor ------------------------------#

class docitem_constructor(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`constructor` section, subsection of |label|`Contract`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`constructor` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "constructor"
	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a |label|`constructor` section.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a list of strings.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the items are not strings (no subtrees allowed).
		|Must| raise if the items are not identifiers.
		"""
		pos = 0
		while pos < len(subtree):
# constructor requires a list of strings
			with rule_on_fail(tr, "CON-008"):
				entry,pos = expect_text(tr,subtree,pos)
			self._items.append(entry)
	def __str__(self) -> str:
		return " {" + ", ".join([entry for entry in self._items]) + "}"

#----- docitem class general ----------------------------------#

class docitem_general(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`general` section, subsection of |label|`Contract`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`general` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "general"
	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a |label|`general` section.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a list of strings.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the items are not strings (no subtrees allowed).
	"""
		pos = 0
		while pos < len(subtree):
# general requires a list of strings
			with rule_on_fail(tr, "CON-006"):
				entry,pos = expect_text(tr,subtree,pos)
			self._items.append(entry)
	def __str__(self) -> str:
		return " {" + ", ".join([entry for entry in self._items]) + "}"

#----- docitem class invariants -------------------------------#

class docitem_invariants(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`invariants` section, subsection of |label|`Contract`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`invariants` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "invariants"
	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an |label|`invariants` section.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a list of strings.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the items are not strings (no subtrees allowed).
		"""
		pos = 0
		while pos < len(subtree):
# invariants requires a list of strings
			with rule_on_fail(tr, "CON-026"):
				entry,pos = expect_text(tr,subtree,pos)
			self._items.append(entry)
	def __str__(self) -> str:
		return " {" + ", ".join([entry for entry in self._items]) + "}"

#----- docitem class requires -------------------------------#

class docitem_requires(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Description:
	This node represents the |label|`requires` subsection of |label|`Contract`.
	The subsection is intended to describe conditions the caller must satisfy before calling the documented function or method.
	The contents are treated as free-form text and are preserved verbatim for rendering and reporting.
Contract:
	general:
		|Must| represent the |label|`requires` section, subsection of |label|`Contract`.
		|Must| be able to hold a list of free-form text lines.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`requires` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "requires"
	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a |label|`requires` section.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a list of strings.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the items are not strings (no subtrees allowed).
		"""
		pos = 0
		while pos < len(subtree):
# requires requires a list of strings
			with rule_on_fail(tr, "CON-048"):
				entry,pos = expect_text(tr,subtree,pos)
			self._items.append(entry)
	def __str__(self) -> str:
		return " {" + ", ".join([entry for entry in self._items]) + "}"

#----- docitem class ensures -------------------------------#

class docitem_ensures(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Description:
	This node represents the |label|`ensures` subsection of |label|`Contract`.
	The subsection is intended to describe guarantees that hold after a successful call of the documented function or method.
	The contents are treated as free-form text and are preserved verbatim for rendering and reporting.
Contract:
	general:
		|Must| represent the |label|`ensures` section, subsection of |label|`Contract`.
		|Must| be able to hold a list of free-form text lines.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse an |label|`ensures` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "ensures"
	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an |label|`ensures` section.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a list of strings.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the items are not strings (no subtrees allowed).
		"""
		pos = 0
		while pos < len(subtree):
# ensures ensures a list of strings
			with rule_on_fail(tr, "CON-050"):
				entry,pos = expect_text(tr,subtree,pos)
			self._items.append(entry)
	def __str__(self) -> str:
		return " {" + ", ".join([entry for entry in self._items]) + "}"

#----- docitem class base -------------------------------------#

class docitem_base_to_inherit_from(docitem_list_of_symbols_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`base` section, subsection of |label|`Contract`.
		|Must| contain exactly one entry which matches the pattern of a Qualified Identifier.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_of_symbols_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`invariants` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "base"
	def parse(self,tr : tracer,bases : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a |label|`base` subsection
Parameters:
	tr:
		The tracer for collecting diagnostics.
	bases:
		The docstring subtree to parse, a qualified identifier referencing a method in a base class.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content is not a single string.
		|Must| raise if the string is not a qualified identifier.
		"""
# exactly one entry required (CON-040)
		if len(bases) != 1:
			raise_parsing_error_expected_but_got(tr, "CON-040", "exactly one item", f"{bases}")
# No need to set a default rule. _parse in the base class is
# a complete implementation of rules LQID-001 to LQID-005.
		super()._parse(tr, bases, docitem_list_of_symbols_base.ValuePattern.QUALIFIED_IDENTIFIER)
	def __str__(self) -> str:
		return " {" + ", ".join([entry for entry in self._items]) + "}"


#----- docitem class traits -----------------------------------#

class docitem_traits(docitem_list_of_symbols_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`traits` section, subsection of |label|`Contract`.
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
		return "traits"
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

#----- docitem classes contract -------------------------------#

class docitem_contract_module(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`Contract` section for profile |value|`module`.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`Contract` section for profile |value|`module`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Contract"
	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an |label|`Contract` section for profile |value|`module`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a set of concatenated sections.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if a section to be parsed is not one of the allowed ones: {|label|`general`,|label|`api`}.
		"""
		pos = 0
		dispatch_map = {
		 "general:":docitem_general,
		 }
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dispatch_map:
				with rule_on_fail(tr, "CON-028"):
					label,pos = expect_label(tr,subtree,pos)
# Contract requires a list
				items,pos = expect_list(tr,subtree,pos)
				self.add_child(tr,label, dispatch_map[lb], items)
			else:
				raise_parsing_error_invalid_label(tr,"CON-028",lb,dispatch_map)
	def __str__(self) -> str:
		return self.label() + " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"

class docitem_contract_class(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`contract` section for profile |value|`class`.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`contract` section for profile |value|`class`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Contract"
	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an |label|`Contract` section for profile |value|`class`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a set of concatenated sections.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if a section to be parsed is not one of the allowed ones: {|label|`general`,|label|`constructor`,|label|`api`}.
		"""
		pos = 0
		dispatch_map = {
		 "general:":docitem_general,
		 "constructor:":docitem_constructor,
		 "traits:":docitem_traits,
		 }
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dispatch_map:
				with rule_on_fail(tr, "CON-032"):
					label,pos = expect_label(tr,subtree,pos)
# Contract requires a list
				items,pos = expect_list(tr,subtree,pos)
				self.add_child(tr,label, dispatch_map[lb], items)
			else:
				raise_parsing_error_invalid_label(tr,"CON-032",lb,dispatch_map)
	def __str__(self) -> str:
		return self.label() + " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"

class docitem_contract_method(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`contract` section for profile |value|`method` or |value|`function`.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`contract` section for profile |value|`method` or |value|`function`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Contract"
	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an |label|`Contract` section for profile |value|`method` or |value|`function`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a set of concatenated sections.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if a section to be parsed is not one of the allowed ones: {|label|`general`}.
		"""
		pos = 0
		dispatch_map = {
		 "general:":docitem_general,
		 "invariants:":docitem_invariants,
		 "requires:":docitem_requires,
		 "ensures:":docitem_ensures,
		 }
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dispatch_map:
				with rule_on_fail(tr, "CON-027"):
					label,pos = expect_label(tr,subtree,pos)
# Contract requires a list
				items,pos = expect_list(tr,subtree,pos)
				self.add_child(tr,label, dispatch_map[lb], items)
			else:
				raise_parsing_error_invalid_label(tr,"CON-027",lb,dispatch_map)
	def __str__(self) -> str:
		return self.label() + " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"

class docitem_contract_inherited_method(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`contract` section for profile |value|`inherited_method`.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`contract` section for profile |value|`inherited_method`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Contract"
	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an |label|`Contract` section for profile |value|`method` or |value|`function`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a set of concatenated sections.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if a section to be parsed is not one of the allowed ones: {|label|`general`}.
		"""
		with traced_section(tr, self.__class__.__name__):
			pos = 0
			dispatch_map = {
			 "general:":docitem_general,
			 "base:":docitem_base_to_inherit_from,
			 }
			while pos < len(subtree):
				lb = subtree[pos]
				assert isinstance(lb,str)
				if lb in dispatch_map:
					with rule_on_fail(tr, "CON-035"):
						label,pos = expect_label(tr,subtree,pos)
# Contract requires a list
					items,pos = expect_list(tr,subtree,pos)
					self.add_child(tr,label, dispatch_map[lb], items)
				else:
					raise_parsing_error_invalid_label(tr,"CON-035",lb,dispatch_map)
	def __str__(self) -> str:
		return self.label() + " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"

#===== end section Contract ===================================#
