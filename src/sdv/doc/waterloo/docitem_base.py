"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Definitions
Contract:
	general:
		|Must| provide bases classes for the Abstract Syntax Tree.
		|Should_not| be imported directly. Import |mod|`sdv.doc.waterloo.docitem` instead.
Definitions:
	Identifier:
		As defined in |mod|`sdv.doc.waterloo.docitem`.
	Qualified_Identifier:
		As defined in |mod|`sdv.doc.waterloo.docitem`.
"""

from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast
from enum import IntEnum

from sdv.doc.waterloo.docitem_helper import *

#===== Keywords ===============================================#
# By Sequence we make sure that nothing can be appended
# or removed. With List this would not be guaranteed.
# Another interesting variant would be frozenset.
KEYWORDS_OF_NORMATIVITY: Final[Sequence[str]] = (
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

RE_PARTIAL_NORMATIVITY_PATTERN_A_COMPILED: Final[Sequence[re.Pattern[str]]] = (
	re.compile(r"\|[Mm]ust\|\s+not\b"),
	re.compile(r"\|[Ss]hould\|\s+not\b"),
	)
RE_PARTIAL_NORMATIVITY_PATTERN_B_COMPILED: Final[Sequence[re.Pattern[str]]] = (
	re.compile(r"\|[Mm]ay\|\s+not\b"),
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
	def __init__(self) -> None:
		self._parent: docitem_base | None = None
	def label(self) -> str:
		return "<Unspecified>"
	def set_parent(self,p: docitem_base) -> None:
		self._parent = p
	def parent(self) -> docitem_base | None:
		return self._parent
# Identity. At some point isinstance is not convenient because
# this would require cyclic imports, which we do not want.
# This is a pragmatic workaround.
	@classmethod
	def is_docstring_module(cls) -> bool:
		return False
	@classmethod
	def is_docstring_class(cls) -> bool:
		return False

	def parse(self,tr : tracer,subtree : DocstringSubtree) -> None:
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
	def detect_partial_normativity(self,tr: tracer) -> bool:
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
	def has_item(self,name : str) -> bool:
		return name in self._items
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
	def detect_partial_normativity(self,tr: tracer) -> bool:
		ok: bool = True
		with traced_section(tr,self.label()):
			for p in RE_PARTIAL_NORMATIVITY_PATTERN_A_COMPILED:
				i = 0
				for item in self.items():
					with traced_section(tr,f"[{i}]"):
						if p.search(item):
							warn_parsing(tr,"PNB-002","Bad normativity pattern detected: one of {|must| not, |should| not}; use |must_not| or |should_not| instead.")
							ok = False
					i += 1
			for p in RE_PARTIAL_NORMATIVITY_PATTERN_B_COMPILED:
				i = 0
				for item in self.items():
					with traced_section(tr,f"[{i}]"):
						if p.search(item):
							warn_parsing(tr,"PNB-003","Bad normativity pattern detected: |may| not.")
							ok = False
					i += 1
		return ok
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

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
	def add_child(self, tr : tracer, label: str, cls: Type[docitem_base], items: DocstringSubtree) -> None:
# This is the parent label. We need to know.
		with traced_section(tr, label):
			if label in self._items:
				raise_parsing_error(tr,"PRSR-002",f"Label '{label}' appears more than once.")
# This is the only point where we create a node and add it as a child.
# All node classes which may have node-like children must be derived
# from this class. UPDATE: there's another location in add_child_multilabel.
			child = cls()
			child.set_parent(self)
			child.parse(tr,items)
			self._items[label] = child

# This method is currently used by docitem_definitions only.
	def add_child_multilabel(self, tr : tracer, labels: List[str], cls: Type[docitem_base], items: DocstringSubtree) -> None:
# This is the parent label. We need to know.
		with traced_section(tr, "{" + ",".join(labels) + "}"):
# This is the other location where we create a node.
# Since we can assign a child note to more than one item,
# the entire construction is no longer a tree.
			child = cls()
			child.set_parent(self)
			child.parse(tr,items)
			for label in labels:
				if label in self._items:
					raise_parsing_error(tr,"PRSR-002",f"Label '{label}' appears more than once.")
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
	def detect_partial_normativity(self,tr: tracer) -> bool:
		ok: bool = True
		with traced_section(tr,self.label()):
			for label,item in self.items().items():
				with traced_section(tr,f"'{label}'"):
					ok &= item.detect_partial_normativity(tr)
		return ok
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

class docitem_list_of_symbols_base(docitem_list_base):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Definitions, Public_classes, Public_methods
	Definitions:
		_inherit:
			Identifier
	Contract:
		general:
			|Must| represent a list of symbols, each matching the pattern of an |term|`Identifier`.
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
				Contract, Definitions, Public_constants
		Definitions:
			_inherit:
				Identifier, Qualified_Identifier
		Contract:
			general:
				|Must| be an Enum class.
				|Must| provide constants representing regular expressions for |term|`Identifier` and |term|`Qualified_Identifier`.
			constructor:
				|Must| inherit the constructor from |type|`int`, since the class is derived from |type|`IntEnum`.
		Public_constants:
			IDENTIFIER:
				|Must| represent the pattern of an |term|`Identifier`.
			QUALIFIED_IDENTIFIER:
				|Must| represent the pattern of a |term|`Qualified_Identifier`.
		"""
		IDENTIFIER = 1
		QUALIFIED_IDENTIFIER = 2
	def _parse(self,tr : tracer,refs : DocstringSubtree,pattern : ValuePattern) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Definitions, Parameters, Returns, Raises
		Definitions:
			_inherit:
				Identifier, Qualified_Identifier
		Contract:
			general:
				|Must| verify that the subtree passed (|var|`refs`) is a list of strings.
				|Must| parse the content the list of strings and store them as items.
				|Must| ensure each string is an |term|`Identifier` or |term|`Qualified_Identifier`, as specified by parameter |var|`pattern`.
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
			sdv.doc.waterloo.docitem_helper.RE_IDENTIFIER,
			sdv.doc.waterloo.docitem_helper.RE_QUALIFIED_IDENTIFIER
		"""
# Validate and collect
		refs_split : List[str] = []
		seen = set()
		logical_refs: List[str] = []
		details: Details
		pending = ""
		for idx, ref in enumerate(refs):
# Only strings are allowed (not list of something)
			if not isinstance(ref,str):
				raise_parsing_error_expected_but_got(tr,"LQID-001",'str', f'{ref}')
# Wraps are tolerated: commas at the end of a physical line continue the logical CSV list.
			part = ref.strip()
			if idx < len(refs) - 1 and not part.endswith(","):
				details = {
					"found": render_identifier_lines("Contract.traits", refs_split + [part]),
					"expected": render_suggestion("Contract.traits", "add a trailing comma to the wrapped line."),
					"hint": explain_try_self_for_subsection("Contract.traits", "class"),
				}
				raise_parsing_error(tr,"LQID-006","A non-final CSV line must end with a comma when the list is wrapped across multiple physical lines.",details)
			if pending:
				pending += " " + part
			else:
				pending = part
			if pending.endswith(","):
				continue
			logical_refs.append(pending)
			pending = ""
		if pending:
			logical_refs.append(pending)
		for ref in logical_refs:
# We allow a comma separated string of qualified identifiers.
# Strip due to rule LQID-003
				segments = map(str.strip,ref.split(","))
				what = "unspecified"
				if pattern == self.ValuePattern.QUALIFIED_IDENTIFIER:
					re_compiled = RE_QUALIFIED_IDENTIFIER_COMPILED
					what = "qualified identifier"
				elif pattern == self.ValuePattern.IDENTIFIER:
					re_compiled = RE_IDENTIFIER_COMPILED
					what = "identifier"
				for seg in segments:
					if seg in seen:
						details = {
							"found": render_identifier_lines("Contract.traits", refs_split + [seg]),
							"expected": render_deduplicated_identifiers("Contract.traits", refs_split + [seg]),
							"hint": explain_try_self_for_subsection("Contract.traits", "class"),
						}
						raise_parsing_error(tr, "LQID-004", f"duplicate identifier '{seg}' occurs more than once.", details)
					if not re_compiled.fullmatch(seg):
						raise_parsing_error_expected_but_got(tr,"LQID-002",what,f'{seg}')
					refs_split.append(seg)
					seen.add(seg)
# We have a flat list, rule LQID-005.
		self.set_items(refs_split)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

class docitem_free_text_entry_base(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent free-form text content for various sections.
	constructor:
		|Must| be default-constructible.
	traits:
		abstract
Derived_from:
	docitem_list_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse free-form text lines.
	"""
	def parse(self,tr : tracer,lines : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an entry in section |label|`Class_overview`, |label|`Public_types`, |label|`Public_constants`, |label|`Method_overview`, |label|`Function_overview`, |label|`Parameters`, |label|`Raises`, |label|`Definitions`, |label|`Terminology`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	lines:
		The docstring subtree to parse, a list of free-form strings representing the content of any of the sections listet in section |label|`Contract.General`.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content is not a list of strings.
		"""
# Expect list of strings
		if not is_list_of_str(lines):
			raise_parsing_error_expected_but_got(tr,tr.get_rule_on_fail(),"list of strings",f"{lines}")
# No restrictions. The content is a list of free-form text lines.
		self.set_items(lines)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

#===== end base classes =======================================#
