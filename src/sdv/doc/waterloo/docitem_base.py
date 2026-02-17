"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
Contract:
	general:
		|Must| provide bases classes for the Abstract Syntax Tree.
		|Should_not| be imported directly. Import |mod|`sdv.doc.waterloo.docitem` instead.
"""

from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast
from enum import IntEnum

try:
	from sdv_doc_docitem_helper import *
except ImportError:
	from sdv.doc.waterloo.docitem_helper import *

#===== Keywords ===============================================#
# By Sequence we make sure that nothing can be appended
# or removed. With List this would not be guaranteed.
# Another interesting variant would be frozenset.
KEYWORDS_OF_NORMATIVITY : Final[Sequence[str]] = (
 "|must|",
 "|Must|",
 "|must_not|",
 "|Must_not|",
 "|should|",
 "|Should|",
 "|should_not|",
 "|Should_not|",
 "|may|",
 "|May|",
# Some documentation guidelines allow these and we should not
# deliberately restrict their use, even if we don't use them ourselves.
 "|may_not|",
 "|May_not|",
 )

#===== begin base classes =====================================#

class docitem_base:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Terminology:
	child item:
		A string or an instance of a docitem class.
Contract:
	general:
		|Must| provide an abstract method for parsing a docstring tree.
		|Must| provide an abstract method for accessing child items.
	constructor:
		|Must| be default-constructible.
	traits:
		abstract
Derived_from:
Public_methods:
	parse, items
Method_overview:
	parse:
		Parse a docstring subtree and create child nodes accordingly.
	items:
		Return an iterable over the child items.
	"""
	def parse(self,tr : tracer,subtree : docstring_subtree) -> None:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Description:
			This docstring is located in the base class of all docitem
			node classes. The method is not implemented here and will
			raise an exception if it is invoked without a corresponding
			implementation in a derived class.
		Contract:
			general:
				|Must| parse a docstring subtree and create the related child items.
			requires:
				|var|`subtree` |must| be a formally correct docstring subtree\
				from a Waterloo docstring; otherwise parsing will fail.
		Parameters:
			tr:
				The tracer for collecting diagnostics.
			subtree:
				A subtree of the tree matching this instance.
		Returns:
			|None|
		Raises:
			NotImplementedError:
				|Must| raise if not implemented in the derived class.
			RuntimeError:
				|Must| raise if the subtree does not match the expected format.
				"""
		raise NotImplementedError
	def items(self) -> Iterable[str]:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
			ensures:
				|Must_not| mutate the instance (pure getter)
		Parameters:
		Returns:
			|Must| return an iterable over the child items.
		Raises:
			NotImplementedError:
				|Must| raise if not implemented in the derived class.
		"""
		raise NotImplementedError
	def item(self,name : str) -> "docitem_base":
		raise NotImplementedError
	def item_by_index(self,index : int) -> str:
		raise NotImplementedError
	def has_item(self,name : str) -> bool:
		raise NotImplementedError
	def empty(self) -> bool:
		raise NotImplementedError
	def has_norm_keywords(self) -> bool:
		raise NotImplementedError
	def has_token(self,token : str) -> bool:
		raise NotImplementedError

class docitem_list_base(docitem_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| contain a container of |type|`str` and expose it as an iterable object.
	constructor:
		|Must| be default-constructible.
	traits:
		abstract
Derived_from:
	docitem_base
Public_methods:
	items
Method_overview:
	items:
		Access to the string list
	"""
	def __init__(self) -> None:
		self._items : List[str] = []
	def set_items(self,items : List[str]) -> None:
		self._items = items
	def items(self) -> List[str]:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must_not| mutate the instance (pure getter)
Parameters:
Returns:
	|Must| return the forementioned container of strings.
Raises:
Description:
		"""
		return self._items
	def item_by_index(self,index : int) -> str:
		return self._items[index]
	def empty(self) -> bool:
		return len(self._items) == 0
	def has_norm_keywords(self) -> bool:
		for w in KEYWORDS_OF_NORMATIVITY:
			for item in self.items():
				if w in item:
					return True
		return False
	def has_token(self,token : str) -> bool:
		for item in self.items():
			if token in item:
				return True
		return False

class docitem_map_base(docitem_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| contain a map-like container from |type|`str` to |type|`docitem_base` and expose it as an iterable object.
	constructor:
		|Must| be default-constructible.
	traits:
		abstract
Derived_from:
	docitem_base
Public_methods:
	items
Method_overview:
	items:
		Access to the item-node map
	"""
	def __init__(self) -> None:
		self._items : Dict[str,docitem_base] = {}
	def add_child(self, tr : tracer, label: str, cls: Type[docitem_base], items: docstring_subtree) -> None:
# This is the parent label. We need to know.
		with traced_section(tr, label):
			if label in self._items:
				raise_parsing_error(tr,["PRSR-002"],f"Label '{label}' appears more than once.")
			child = cls()
			child.parse(tr,items)
			self._items[label] = child
	def items(self) -> Dict[str,docitem_base]:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must_not| mutate the instance (pure getter)
Parameters:
Returns:
	|Must| return an iterable over the child items.
Raises:
		"""
		return self._items
	def item(self,name : str) -> docitem_base:
		return self._items[name]
	def has_item(self,name : str) -> bool:
		return name in self._items
	def has_norm_keywords(self) -> bool:
		for label,item in self.items().items():
			if item.has_norm_keywords():
				return True
		return False
	def has_token(self,token : str) -> bool:
		for label,item in self.items().items():
			if item.has_token(token):
				return True
		return False

class docitem_list_of_symbols_base(docitem_list_base):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_classes, Public_methods
	Contract:
		general:
			|Must| represent a list of symbols, each matching the pattern of an identifier.
		constructor:
			|Must| Be default-constructible
		traits:
			abstract
	Public_classes:
		ValuePattern
	Class_overview:
		ValuePattern:
			Enum type for selecting the regex to match against.
	Public_methods:
		_parse
	Method_overview:
		_parse:
			Parse a list of symbols.
	"""
	class ValuePattern(IntEnum):
		"""
		Preamble:
			profile:
				class
			normative_sections:
				Contract, Public_constants
		Contract:
			general:
				|Must| be an Enum class.
				|Must| provide constants representing regular expressions for Identifier and Qualified Identifier.
			constructor:
				|Must| inherit the constructor from |type|`int`, since the class is derived from |type|`IntEnum`.
		Public_constants:
			IDENTIFIER:
				|Must| represent the pattern of an Identifier.
			QUALIFIED_IDENTIFIER:
				|Must| represent the pattern of a Qualified Identifier.
		"""
		IDENTIFIER = 1
		QUALIFIED_IDENTIFIER = 2
	def _parse(self,tr : tracer,refs : docstring_subtree,pattern : ValuePattern) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| verify that the subtree passed (|var|`refs`) is a list of strings.
				|Must| parse the content the list of strings and store them as items.
				|Must| ensure each string is an Identifier or Qualified Identifier, as specified by parameter |var|`pattern`.
		Parameters:
			tr:
				The tracer for collecting diagnostics.
			refs:
				The docstring subtree to parse.
			pattern:
				Specifies the pattern to match strings against, |var|`RE_IDENTIFIER` or |var|`RE_QUALIFIED_IDENTIFIER`.
		Returns:
			|Must| return |None|.
		Raises:
			ParseError:
				|Must| raise if the items are not strings (no subtrees allowed).
				|Must| raise if the items (after splitting the CSV) are not (Qualified) Identifiers.
		See_also:
			sdv.doc.waterloo.docitem_helper.RE_IDENTIFIER
			sdv.doc.waterloo.docitem_helper.RE_QUALIFIED_IDENTIFIER
		"""
# Validate and collect
		refs_split : List[str] = []
		seen = set()
		for ref in refs:
# Only string are allowed (not list of something)
			if not isinstance(ref,str):
				raise_parsing_error_expected_but_got(tr,["LQID-001"],'str', f'{ref}')
# We allow a comma separated string of qualified identifiers.
# Strip due to rule LQID-003
			segments = map(str.strip,ref.split(","))
			if pattern == self.ValuePattern.QUALIFIED_IDENTIFIER:
				re_compiled = RE_QUALIFIED_IDENTIFIER_COMPILED
			elif pattern == self.ValuePattern.IDENTIFIER:
				re_compiled = RE_IDENTIFIER_COMPILED
			for seg in segments:
				if seg in seen:
					raise_parsing_error(tr, ["LQID-004"], f"duplicate entry {seg}.")
				if not RE_QUALIFIED_IDENTIFIER_COMPILED.fullmatch(seg):
					raise_parsing_error_expected_but_got(tr,["LQID-002"],'[qualified] identifier',f'{seg}')
				refs_split.append(seg)
				seen.add(seg)
# We have a flat list, rule LQID-005.
		self.set_items(refs_split)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end base classes =======================================#
