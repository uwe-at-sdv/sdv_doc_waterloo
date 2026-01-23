"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
		Public_functions
		Public_classes
		Public_types
		Public_constants
Contract:
	general:
		|Must| provide node classes and parsing/validation utilities for Waterloo docstrings. In detail:
		|Must| provide a node class for each type of section and subsection in a Waterloo docstring.
		|Must| provide an appropriate base class hierarchy with a single base class as root of this hierarchy.
		|Must| be able to represent any valid docstring by a single node which is the root of a tree of nodes.
		|Must| provide validator functions for docstrings for modules, classes and callables.
		|Must| provide functions for verifying coverage where applicable.
	api:
		Public_functions
		Public_classes
		Public_types
		Public_constants
Public_functions:
	is_annotated:
		Find out if an attribute of a class or module is annotated.
	is_final:
		Find out if an attribute of a class or module is annotated as 'Final'.
	resolve_object:
		Resolve an object by its qualified identifier
	get_num_indent:
		Count number of leading indent units of a string.
	parse_indent_docstring:
		The fundamental parsing function which creates docstring trees from Waterloo docstrings.
	get_tree_of_section:
		Get tree assigned to a section label from a docstring tree.
	get_tree_of_subsection:
		Get tree assigned to a subsection label from a docstring tree.
	to_string_tree:
		Render docstring to string
	validate_docstring_method:
		Validator for method and function docstrings
	validate_docstring_inherited_method:
		Validator for inherited method docstrings
	validate_docstring_class:
		Validator for class docstrings
	validate_docstring_module:
		Validator for module docstrings
	validate_docstring:
		Validator for docstrings for generic objects.
	validate_class_class_coverage:
		Validate mutual coverage of nested classes and class docstring entries.
	validate_class_method_coverage:
		Validate mutual coverage of methods and class docstring entries.
	validate_class_constant_coverage:
		Verify constant existence and 'Final' annotation.
	validate_class_variable_coverage:
		Verify variable existence.
	validate_class_coverage:
		Verify existence (and mutual coverage were applicable) of methods mentioned in the class docstring.
	validate_module_class_coverage:
		Validate mutual coverage of classes and module docstring entries.
	validate_module_function_coverage:
		Validate mutual coverage of functions and module docstring entries.
	validate_module_type_coverage:
		Verify existence of types mentioned in the module docstring.
	validate_module_constant_coverage:
		Verify constant existence and 'Final' annotation.
	validate_module_variable_coverage:
		Verify variable existence.
	validate_module_coverage:
		Verify existence (and mutual coverage were applicable) of classes, functions, types, constants mentioned in the module docstring.
	gen_documentable_objects:
		Iterate over objects which may have a docstring.
	has_docstring:
		Find out whether a module, class, function, or method has a docstring.
	make_docitem_tree:
		Generate a docitem tree from a docstring.
Public_classes:
	tracer:
		Context and helper for exceptions and warnings.
	docitem_base:
		The base class for all docitem classes which form the docstring tree.
	docitem_list_base:
		The base class for docitem classes managing a list of strings.
	docitem_map_base:
		The base class for docitem classes managing a map from strings to docitem nodes
	docitem_free_text_entry_base:
		The base class for nodes which consist of free-text string.
	docitem_list_of_symbols_base:
		The base class for nodes which contein a list of identifiers.
	docitem_profile:
		Node class for section :wtrl_label:`profile`
	docitem_normative_sections:
		Node class for subsection :wtrl_label:`normative_sections`
	docitem_preamble:
		Node class for section :wtrl_label:`Preamble`
	docitem_constructor:
		Node class for subsection :wtrl_label:`constructor`
	docitem_general:
		Node class for subsection :wtrl_label:`general`
	docitem_invariants:
		Node class for subsection :wtrl_label:`invariants`
	docitem_base_to_inherit_from:
		Node class for subsection :wtrl_label:`base`
	docitem_api:
		Node class for subsection :wtrl_label:`api`
	docitem_traits:
		Node class for subsection :wtrl_label:`traits`
	docitem_contract_module:
		Node class for section :wtrl_label:`Contract`, profile :wtrl_value:`module`.
	docitem_contract_class:
		Node class for section :wtrl_label:`Contract`, profile :wtrl_value:`class`.
	docitem_contract_method:
		Node class for section :wtrl_label:`Contract`, profile :wtrl_value:`method` or :wtrl_value:`function`.
	docitem_contract_inherited_method:
		Node class for section :wtrl_label:`Contract`, profile :wtrl_value:`inherited_method`.
	docitem_derived_from:
		Node class for section :wtrl_label:`Derived_from`.
	docitem_factory_functions:
		Node class for entries in section :wtrl_label:`Factory`.
	docitem_factory:
		Node class for section :wtrl_label:`Factory`.
	docitem_public_classes_entry:
		Node class for entries in section :wtrl_label:`Public_classes`.
	docitem_public_classes:
		Node class for section :wtrl_label:`Public_classes`.
	docitem_public_types_entry:
		Node class for entries in section :wtrl_label:`Public_types`.
	docitem_public_types:
		Node class for section :wtrl_label:`Public_types`.
	docitem_public_assignables_entry:
		Node class for entries in section :wtrl_label:`Public_constants` and :wtrl_label:`Public_variables`.
	docitem_public_assignables_base:
		Node base class for sections :wtrl_label:`Public_constants` and :wtrl_label:`Public_variables`.
	docitem_public_methods_entry:
		Node class for entries in section :wtrl_label:`Public_methods`.
	docitem_public_methods:
		Node class for section :wtrl_label:`Public_methods`.
	docitem_public_functions_entry:
		Node class for entries in section :wtrl_label:`Public_functions`.
	docitem_public_functions:
		Node class for section :wtrl_label:`Public_functions`.
	docitem_returns:
		Node class for section :wtrl_label:`Returns`.
	docitem_parameters_entry:
		Node class for a parameter description
	docitem_parameters:
		Node class for section :wtrl_label:`Parameters`
	docitem_raises_entry:
		Node class for entries in section :wtrl_label:`Raises`.
	docitem_raises:
		Node class for section :wtrl_label:`Raises`
	docitem_definitions_entry:
		Node class for entries in section :wtrl_label:`Definitions`.
	docitem_definitions:
		Node class for section :wtrl_label:`Definitions`
	docitem_terminology_entry:
		Node class for entries in section :wtrl_label:`Terminology`.
	docitem_terminology:
		Node class for section :wtrl_label:`Terminology`
	docitem_notes_entry:
		Node class for entries in section :wtrl_label:`Notes`.
	docitem_notes:
		Node class for section :wtrl_label:`Notes`
	docitem_description:
		Node class for section :wtrl_label:`Description`.
	docitem_see_also:
		Node class for section :wtrl_label:`See_also`

	docitem_docstring_base:
		Base class for docstring nodes
	docitem_docstring_module:
		Node class for a module docstring
	docitem_docstring_class:
		Node class for a class docstring
	docitem_docstring_method:
		Node class for a function or method docstring
	docitem_docstring_inherited_method:
		Node class for an inherited method docstring
Public_types:
	docstring_tree:
		The type alias for docstring trees.
Public_constants:
	RE_IDENTIFIER:
		Regular expression for identifiers: ``[A-Za-z_][A-Za-z0-9_]*``
	RE_QUALIFIED_IDENTIFIER:
		Regular expression for qualified identifiers: ``[A-Za-z_.][A-Za-z0-9_.]*``
	KEYWORDS_OF_NORMATIVITY:
		The set of normative keywords.
"""

# Todo: think about Contract.import_side_fx

import sys,re
import inspect
import importlib
import builtins
import typing
from types import FunctionType, ModuleType
from contextlib import contextmanager
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Tuple, Type, TypeAlias, TypeGuard, Union

try:
	from sdv_doc_docitem_helper import *
except ImportError:
	from sdv.doc.waterloo.docitem_helper import *

try:
	from sdv_doc_docitem_validator import *
except ImportError:
	from sdv.doc.waterloo.docitem_validator import *

try:
	from sdv_doc_docitem_tokenizer import *
except ImportError:
	from sdv.doc.waterloo.docitem_tokenizer import *

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
# These two might be uncommon, but in our opinion it is a logical
# consequence of the principle of machine-verifiable normativity.
# A section can be declared as "normative", and validators must
# be able to check whether or not the section is listed in
# subsection `Preamble.normative_sections`.
	)

#===== Docitem node classes ===================================#

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
	parse:
		|Must| parse a docstring subtree and create child nodes accordingly.
	items:
		|Must| return an iterable over the child items.
	"""
	def parse(self,tr : tracer,subtree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse a docstring subtree and create the related child items.
		|Must| raise NotImplementedError if not implemented in the derived class.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		A subtree of the tree matching this instance.
Returns:
	None
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
		|Must_not| mutate the instance (pure getter)
Parameters:
Returns:
	|Must| return an iterable over the child items.
Raises:
		"""
		raise NotImplementedError
	def item(self,name : str) -> "docitem_base":
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
		|Must| contain a container of :wtrl_type:`str` and expose it as an iterable object.
	constructor:
		|Must| be default-constructible.
	traits:
		abstract
Derived_from:
	docitem_base
Public_methods:
	items:
		|Must_not| mutate the instance (pure getter)
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
		|Must| contain a map-like container from :wtrl_type:`str` to :wtrl_type:`docitem_base` and expose it as an iterable object.
	constructor:
		|Must| be default-constructible.
	traits:
		abstract
Derived_from:
	docitem_base
Public_methods:
	items:
		|Must_not| mutate the instance (pure getter)
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
		Contract, Public_methods
Contract:
	general:
		|Must| represent a list of symbols, each matching the pattern of an identifier.
	constructor:
		|Must| Be default-constructible
	traits:
		abstract
Public_methods:
	parse:
		Parse a list of symbols.
	"""
	def parse(self,tr : tracer,refs : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a :wtrl_label:`normative_sections` section, in detail:
		|Must| accept a sequence of strings, where each string represents a section or a comma-separated list of sections.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	refs:
		The docstring subtree to parse.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the items are not strings (no subtrees allowed).
		|Must| raise if the items (after splitting the CSV) are not identifiers.
		"""
# Validate and collect
		refs_split : List[str] = []
		for ref in refs:
# Only string are allowed (not list of something)
			if not isinstance(ref,str):
				raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'str', f'{ref}')
# We allow a comma separated string of qualified identifiers.
			segments = map(str.strip,ref.split(","))
			for seg in segments:
				if not RE_QUALIFIED_IDENTIFIER_COMPILED.fullmatch(seg):
					raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'identifier',f'{seg}')
				refs_split.append(seg)
		self.set_items(refs_split)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== begin section Preamble =================================#

#----- docitem class profile  ---------------------------------#
# By the profile we distinguish between docstrings for
# classes, methods, functions and mybe others.
class docitem_profile(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`profile` section, subsection of :wtrl_label:`Preamble`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_list_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`profile` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "profile"
	def parse(self,tr : tracer,refs : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a :wtrl_label:`profile` section.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	refs:
		The docstring subtree to parse.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the number of item is not :wtrl_value:`1`.
		|Must| raise if the item is not a string (no subtrees allowed).
		|Must| raise if the item is not an identifier.
		"""
# Validate
		if not is_list_of_str(refs):
			raise_parsing_error_expected_but_got(tr,["PRE-014"],'str','list')
# Only exactly one item is allowed
		if len(refs) != 1:
			raise_parsing_error_expected_but_got(tr,["PRE-004"],'exactly one item',f'{refs}')
		with rules_on_fail(tr, ["PRE-014"]):
			for ref in refs:
# Only string are allowed (not list of something) - not sure how to provoke
				if not isinstance(ref,str):
					raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'str', f'{ref}')
# Only identifiers are allowed.
				if not RE_IDENTIFIER_COMPILED.fullmatch(ref):
					raise_parsing_error_expected_but_got(tr,["PRE-014"],"identifier",f'{ref}')
		self.set_items(refs)
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
		|Must| represent the :wtrl_label:`normative_sections` section, subsection of :wtrl_label:`Preamble`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_of_symbols_base
Public_methods:
	parse:
		Inherited method
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "normative_sections"
	def parse(self, tr: tracer, refs: docstring_subtree) -> None:
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
		sdv.doc.waterloo.docitem.docitem_list_of_symbols_base.parse
		"""
# Entries must match identifier syntax per PRE-014.
		with rules_on_fail(tr, ["PRE-014"]):
			super().parse(tr, refs)

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
		|Must| represent the :wtrl_label:`Preamble` section.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`Preamble` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Preamble"
	def parse(self,tr : tracer,subtree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the subsections of a :wtrl_label:`Preamble` section.
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
			}
		while pos < len(subtree):
			with rules_on_fail(tr, ["PRE-015"]):
				label,pos = expect_label_identifier(tr,subtree,pos)
			if label not in dispatch_map:
				raise_parsing_error_invalid_label(tr,["PRE-015"],label,dispatch_map)
			items,pos = expect_list(tr,subtree,pos)
			self.add_child(tr,label, dispatch_map[label], items)
	def __str__(self) -> str:
		return " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"
#===== end section Preamble ===================================#

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
		|Must| represent the :wtrl_label:`constructor` section, subsection of :wtrl_label:`Contract`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_list_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`constructor` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "constructor"
	def parse(self,tr : tracer,subtree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a :wtrl_label:`constructor` section.
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
			with rules_on_fail(tr, ["CON-008"]):
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
		|Must| represent the :wtrl_label:`general` section, subsection of :wtrl_label:`Contract`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_list_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`general` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "general"
	def parse(self,tr : tracer,subtree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a :wtrl_label:`general` section.
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
			with rules_on_fail(tr, ["CON-006"]):
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
		|Must| represent the :wtrl_label:`invariants` section, subsection of :wtrl_label:`Contract`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_list_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`invariants` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "invariants"
	def parse(self,tr : tracer,subtree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a :wtrl_label:`invariants` section.
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
			with rules_on_fail(tr, ["CON-026"]):
				entry,pos = expect_text(tr,subtree,pos)
			self._items.append(entry)
	def __str__(self) -> str:
		return " {" + ", ".join([entry for entry in self._items]) + "}"

#----- docitem class base -------------------------------------#

class docitem_base_to_inherit_from(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`base` section, subsection of :wtrl_label:`Contract`.
		|Must| contain exactly one entry which matches the pattern of a Qualified Identifier.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`invariants` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "base"
	def parse(self,tr : tracer,bases : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of a :wtrl_label:`base` subsection
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
		with traced_section(tr, self.__class__.__name__):
			# exactly one entry required (CON-040)
			if len(bases) != 1:
				raise_parsing_error_expected_but_got(tr, ["CON-040"], "exactly one item", f"{bases}")
			base = bases[0]
			if not isinstance(base, str):
				raise_parsing_error_expected_but_got(tr, ["CON-041"], "qualified identifier", f"{base}")
			if not RE_QUALIFIED_IDENTIFIER_COMPILED.fullmatch(base):
				raise_parsing_error_expected_but_got(tr, ["CON-041"], "qualified identifier", f"{base}")
			self.set_items([base])
	def __str__(self) -> str:
		return " {" + ", ".join([entry for entry in self._items]) + "}"

#----- docitem class api --------------------------------------#

class docitem_api(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`api` section, subsection of :wtrl_label:`Contract`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_list_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`api` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "api"
	def parse(self,tr : tracer,refs : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an :wtrl_label:`api` section.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	refs:
		The docstring subtree to parse, a list of identifiers.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the items are not identifiers.
		"""
		# CON-010: api entries must list sections (identifiers).
		with rules_on_fail(tr, ["CON-010"]):
# api requires a list of strings
			if not is_list_of_str(refs):
				raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'list', f'{refs}')
# Validate
			for ref in refs:
# Only string are allowed (not list of something)
				if not isinstance(ref,str):
					raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'str', f'{ref}')
# Only identifiers are allowed.
				assert isinstance(ref,str)
				if not RE_IDENTIFIER_COMPILED.fullmatch(ref):
					raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'identifier',f'{ref}')
			assert is_list_of_str(refs)
			self.set_items(refs)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

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
		|Must| represent the :wtrl_label:`traits` section, subsection of :wtrl_label:`Contract`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_list_of_symbols_base
Public_methods:
	parse:
		Inherited method
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "traits"
	def parse(self, tr: tracer, refs: docstring_subtree) -> None:
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
		sdv.doc.waterloo.docitem.docitem_list_of_symbols_base.parse
		"""
		# Traits must be identifiers (CON-015).
		with rules_on_fail(tr, ["CON-015"]):
			super().parse(tr, refs)

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
		|Must| represent the :wtrl_label:`Contract` section for profile :wtrl_value:`module`.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`Contract` section for profile :wtrl_value:`module`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Contract"
	def parse(self,tr : tracer,subtree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an :wtrl_label:`Contract` section for profile :wtrl_value:`module`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a set of concatenated sections.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if a section to be parsed is not one of the allowed ones: {:wtrl_label:`general`,:wtrl_label:`api`}.
		"""
		pos = 0
		dispatch_map = {
			"general:":docitem_general,
			"api:":docitem_api,
			}
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dispatch_map:
				with rules_on_fail(tr, ["CON-028"]):
					label,pos = expect_label(tr,subtree,pos)
# Contract requires a list
				items,pos = expect_list(tr,subtree,pos)
				self.add_child(tr,label, dispatch_map[lb], items)
			else:
				raise_parsing_error_invalid_label(tr,["CON-028"],lb,dispatch_map)
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
		|Must| represent the :wtrl_label:`contract` section for profile :wtrl_value:`class`.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`contract` section for profile :wtrl_value:`class`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Contract"
	def parse(self,tr : tracer,subtree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an :wtrl_label:`Contract` section for profile :wtrl_value:`class`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a set of concatenated sections.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if a section to be parsed is not one of the allowed ones: {:wtrl_label:`general`,:wtrl_label:`constructor`,:wtrl_label:`api`}.
		"""
		pos = 0
		dispatch_map = {
			"general:":docitem_general,
			"constructor:":docitem_constructor,
			"api:":docitem_api,
			"traits:":docitem_traits,
			}
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dispatch_map:
				with rules_on_fail(tr, ["CON-032"]):
					label,pos = expect_label(tr,subtree,pos)
# Contract requires a list
				items,pos = expect_list(tr,subtree,pos)
				self.add_child(tr,label, dispatch_map[lb], items)
			else:
				raise_parsing_error_invalid_label(tr,["CON-032"],lb,dispatch_map)
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
		|Must| represent the :wtrl_label:`contract` section for profile :wtrl_value:`method` or :wtrl_value:`function`.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`contract` section for profile :wtrl_value:`method` or :wtrl_value:`function`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Contract"
	def parse(self,tr : tracer,subtree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an :wtrl_label:`Contract` section for profile :wtrl_value:`method` or :wtrl_value:`function`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a set of concatenated sections.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if a section to be parsed is not one of the allowed ones: {:wtrl_label:`general`}.
		"""
		pos = 0
		dispatch_map = {
			"general:":docitem_general,
			"invariants:":docitem_invariants,
			}
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dispatch_map:
				with rules_on_fail(tr, ["CON-027"]):
					label,pos = expect_label(tr,subtree,pos)
# Contract requires a list
				items,pos = expect_list(tr,subtree,pos)
				self.add_child(tr,label, dispatch_map[lb], items)
			else:
				raise_parsing_error_invalid_label(tr,["CON-027"],lb,dispatch_map)
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
		|Must| represent the :wtrl_label:`contract` section for profile :wtrl_value:`inherited_method`.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`contract` section for profile :wtrl_value:`inherited_method`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Contract"
	def parse(self,tr : tracer,subtree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an :wtrl_label:`Contract` section for profile :wtrl_value:`method` or :wtrl_value:`function`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	subtree:
		The docstring subtree to parse, a set of concatenated sections.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if a section to be parsed is not one of the allowed ones: {:wtrl_label:`general`}.
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
					with rules_on_fail(tr, ["CON-035"]):
						label,pos = expect_label(tr,subtree,pos)
# Contract requires a list
					items,pos = expect_list(tr,subtree,pos)
					self.add_child(tr,label, dispatch_map[lb], items)
				else:
					raise_parsing_error_invalid_label(tr,["CON-035"],lb,dispatch_map)
	def __str__(self) -> str:
		return self.label() + " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"

#===== end section Contract ===================================#

#===== begin section Derived_from =============================#

#----- docitem class derived_from -----------------------------#

class docitem_derived_from(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`Derived_from` section.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`Derived_from` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Derived_from"
	def parse(self,tr : tracer,bases : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an :wtrl_label:`Derived_from`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	bases:
		The docstring subtree to parse, a list of strings representing base classes.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content is not a list of strings.
		|Must| raise if any of the strings is not a qualified identifier.
		"""
		with rules_on_fail(tr, ["DER-002"]):
			if not is_list_of_str(bases):
				raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'str', f'{bases}')
			assert is_list_of_str(bases)
# This must be a list of qualified identifiers.
			for base in bases:
				if not RE_QUALIFIED_IDENTIFIER_COMPILED.fullmatch(base):
					raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'qualified identifier', f'{base}')
			self.set_items(bases)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Derived_from ===============================#

#===== begin section See also =================================#

#----- docitem class see_also ---------------------------------#

class docitem_see_also(docitem_list_of_symbols_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`See_also` section.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_of_symbols_base
Public_methods:
	parse:
		Inherited method
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "See_also"
	def parse(self, tr: tracer, refs: docstring_subtree) -> None:
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
		sdv.doc.waterloo.docitem.docitem_list_of_symbols_base.parse
		"""
		# See_also entries must be identifiers; treat parse failures under SEE-005.
		with rules_on_fail(tr, ["SEE-005"]):
			super().parse(tr, refs)

#===== end section Derived_from ===============================#

#===== begin section Factory ==================================#

#----- docitem class factory ----------------------------------#

class docitem_factory_functions(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the content of an entry in section :wtrl_label:`Factory`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_list_base
Public_methods:
	parse:
		|Must| be able to parse a list of text lines describing the factory function.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "factory_functions"
	def parse(self,tr : tracer,factory_functions : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an entry in section :wtrl_label:`Factory`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	factory_functions:
		The docstring subtree to parse, a list of strings representing factory functions.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content is not a list of strings.
		"""
		with rules_on_fail(tr, ["FAC-007"]):
# Expect list of strings
			if not is_list_of_str(factory_functions):
				raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),"list of strings",f"{factory_functions}")
# No restrictions. The content is a list of free-form text lines.
			self.set_items(factory_functions)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

class docitem_factory(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`Factory` section.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse a :wtrl_label:`Factory`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Factory"
	def parse(self,tr : tracer,functions : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of section :wtrl_label:`Factory`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	functions:
		The docstring subtree to parse, a list of factory function sections.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content is not a set of factory function sections. In detail:
		|Must| raise if the content is not a sequence of pairs label / list of strings.
		"""
		pos = 0
		while pos < len(functions):
# proxy: matches name regex
			if True:
				with rules_on_fail(tr, ["FAC-005"]):
					label,pos = expect_label(tr,functions,pos)
# factory requires a list of factory function names
				items,pos = expect_list(tr,functions,pos)
				self.add_child(tr,label, docitem_factory_functions, items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Factory ====================================#

#===== begin section Public_classes ===========================#

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
	parse:
		Parse free-form text lines.
	"""
	def parse(self,tr : tracer,lines : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of an entry in section :wtrl_label:`Public_classes`, :wtrl_label:`Public_types`, :wtrl_label:`Public_constants`, :wtrl_label:`Public_methods`, :wtrl_label:`Public_functions`, :wtrl_label:`Parameters`, :wtrl_label:`Raises`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	lines:
		The docstring subtree to parse, a list of free-form strings representing the content of any of the sections listet in section :wtrl_label:`Contract.General`.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content is not a list of strings.
		"""
# Expect list of strings
		if not is_list_of_str(lines):
			raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),"list of strings",f"{lines}")
# No restrictions. The content is a list of free-form text lines.
		self.set_items(lines)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"


#----- docitem class public_classes ---------------------------#

# An entry for a function in section Public classes is only a brief
# description that the class is good for. Classes must be explained
# in details outside the module documentation block.
class docitem_public_classes_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the content of an entry in section :wtrl_label:`Public_classes`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse:
		|Must| be able to parse a list of text lines describing the public class.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "public_classes_entries"

class docitem_public_classes(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`Public_classes` section.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse the content of a section :wtrl_label:`Public_classes`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Public_classes"
	def parse(self,tr : tracer,entries : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of section :wtrl_label:`Public_classes`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	entries:
		The docstring subtree to parse, a list of public class entries.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content is not a set of public class entries. In detail:
		|Must| raise if the content is not a sequence of pairs label / list of strings.
		"""
		pos = 0
		while pos < len(entries):
# proxy: matches name regex
			if True:
				with rules_on_fail(tr, ["PCL-010"]):
					label,pos = expect_label(tr,entries,pos)
# public_classes requires a list of public_classes function names
				items,pos = expect_list(tr,entries,pos)
				self.add_child(tr,label, docitem_public_classes_entry, items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem class public_types ----------------------------#

# An entry for a function in section Public types is only a brief
# description that the class is good for. types must be explained
# in details outside the module documentation block.
class docitem_public_types_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the content of an entry in section :wtrl_label:`Public_types`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse:
		|Must| be able to parse a list of text lines describing the public type.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "public_types_entries"

class docitem_public_types(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`Public_types` section.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse the content of a section :wtrl_label:`Public_types`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Public_types"
	def parse(self,tr : tracer,entries : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of section :wtrl_label:`Public_types`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	entries:
		The docstring subtree to parse, a list of public type entries.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content is not a set of public type entries. In detail:
		|Must| raise if the content is not a sequence of pairs label / list of strings.
		"""
		pos = 0
		while pos < len(entries):
# proxy: matches name regex
			if True:
				with rules_on_fail(tr, ["PTY-004"]):
					label,pos = expect_label(tr,entries,pos)
# public_types requires a list of public_types function names
				items,pos = expect_list(tr,entries,pos)
				self.add_child(tr,label, docitem_public_types_entry, items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem class public_constants ----------------------------#

# An entry for a function in section Public assignables is only a brief
# description that the class is good for. assignables must be explained
# in details outside the module documentation block.
class docitem_public_assignables_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the content of an entry in section :wtrl_label:`Public_assignables`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse:
		|Must| be able to parse a list of text lines describing the public assignable.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "public_assignables_entries"

class docitem_public_assignables_base(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`Public_assignables` section.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse the content of a section :wtrl_label:`Public_assignables`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def parse(self,tr : tracer,entries : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of section :wtrl_label:`Public_assignables`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	entries:
		The docstring subtree to parse, a list of public assignable entries.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content is not a set of public assignable entries. In detail:
		|Must| raise if the content is not a sequence of pairs label / list of strings.
		"""
		pos = 0
		while pos < len(entries):
# proxy: matches name regex
			if True:
				with rules_on_fail(tr, ["PVAR-004"]):
					label,pos = expect_label(tr,entries,pos)
# public_assignables requires a list of public_assignables function names
				items,pos = expect_list(tr,entries,pos)
				self.add_child(tr,label, docitem_public_assignables_entry, items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

class docitem_public_constants(docitem_public_assignables_base):
	def label(self) -> str:
		return "Public_constants"
class docitem_public_variables(docitem_public_assignables_base):
	def label(self) -> str:
		return "Public_variables"

#===== end section Public_classes =============================#

#===== begin section Public_<callable> ========================#

#----- docitem class public_methods ---------------------------#

# An entry for a function in section Public methods is only a brief
# description what the function is good for. Functions must be explained
# in details outside the class documentation block.
class docitem_public_methods_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the content of an entry in section :wtrl_label:`Public_methods`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse:
		|Must| be able to parse a list of text lines describing the public method.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "public_methods_entries"

class docitem_public_methods(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`Public_methods` section.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse the content of a section :wtrl_label:`Public_methods`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Public_methods"
	def parse(self,tr : tracer,entries : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of section :wtrl_label:`Public_methods`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	entries:
		The docstring subtree to parse, a list of public method entries.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content is not a set of public method entries. In detail:
		|Must| raise if the content is not a sequence of pairs label / list of strings.
		"""
		pos = 0
		while pos < len(entries):
# proxy: matches name regex
			if True:
				with rules_on_fail(tr, ["PMET-010"]):
					label,pos = expect_label(tr,entries,pos)
# public_methods requires a list of public_methods function names
				items,pos = expect_list(tr,entries,pos)
				self.add_child(tr,label, docitem_public_methods_entry, items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem class public_functions ---------------------------#

class docitem_public_functions_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the content of an entry in section :wtrl_label:`Public_functions`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse:
		|Must| be able to parse a list of text lines describing the public function.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "public_functions_entries"

class docitem_public_functions(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`Public_functions` section.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse the content of a section :wtrl_label:`Public_functions`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Public_functions"
	def parse(self,tr : tracer,entries : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of section :wtrl_label:`Public_functions`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	entries:
		The docstring subtree to parse, a list of public function entries.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content is not a set of public function entries. In detail:
		|Must| raise if the content is not a sequence of pairs label / list of strings.
		"""
		pos = 0
		while pos < len(entries):
# proxy: matches name regex
			if True:
				with rules_on_fail(tr, ["PFN-004"]):
					label,pos = expect_label(tr,entries,pos)
# public_functions requires a list of public_functions function names
				items,pos = expect_list(tr,entries,pos)
				self.add_child(tr,label, docitem_public_functions_entry, items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Public_<callable> ==========================#

#===== begin section Returns ==================================#

#----- docitem class returns ----------------------------------#

class docitem_returns(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Public_methods
Contract:
	general:
		|Must| store the list of return value descriptions for a callable's docstring.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Public_methods:
	parse:
		Parse a list of return descriptions.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Returns"
	def parse(self,tr : tracer,lines : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| accept a list of return descriptions.
		|Must| raise if the input is not a list of strings.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	lines:
		A free-form text describing the return value.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if validation fails.
		"""
# Expect list of strings
		if not is_list_of_str(lines):
			raise_parsing_error_expected_but_got(tr,["RET-005"],"list of strings",f"{lines}")
		self.set_items(lines)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

#===== end section Returns ====================================#

#===== begin section Description ==============================#

#----- docitem class Description ------------------------------#

# A dscription may contain several lines. The standard rendering
# will be to concatenate them to one paragraph, the lines are
# an editing and parsing artefact.
class docitem_description(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| hold free-form descriptive text lines from a docstring section :wtrl_label:`Description`.
		|Must| accept and store a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Description:
	A free-form section which informatively describes the purpose
	of a module, class or callable.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse:
		Parse a list of description lines.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Description"
	def parse(self,tr : tracer,lines : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| accept a list of description lines.
		|Must| raise if the input is not a list of strings.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	lines:
		The description lines.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if validation fails.
		"""
# Expect list of strings
		if not is_list_of_str(lines):
			raise_parsing_error_expected_but_got(tr,["DESC-004"],"list of strings",f"{lines}")
		self._items = lines
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

#===== end section Description ================================#

#===== begin section Parameters ===============================#

#----- docitem class Parameters -------------------------------#

class docitem_parameters_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent an parameter entry in the :wtrl_label:`Parameters` section.
		|Must| accept and store a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse:
		Parse a the content of a parameter entry.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "parameter"

class docitem_parameters(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`Parameters` section.
		|Must| accept and store a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		Parse a list of parameters
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Parameters"
	def parse(self,tr : tracer,entries : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Terminology:
	Parameter entry:
		Describes a docstring subtree consisting of a string valued identifier
		and a list of free-form description lines: :wtrl_type:`str, List[str]`
Contract:
	general:
		|Must| accept a list of parameter entries.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	entries:
		A docstring subtree representing a list of parameter entries.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if parsing the sequence of parameter entries fails.
		"""
		pos = 0
		while pos < len(entries):
			with rules_on_fail(tr,["PAR-006"]):
				label,pos = expect_label_identifier(tr,entries,pos)
			items,pos = expect_list(tr,entries,pos)
			self.add_child(tr,label, docitem_parameters_entry, items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Parameters =================================#

#===== begin section Raises ===================================#

#----- docitem class Raises -----------------------------------#

class docitem_raises_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent an exception entry in the :wtrl_label:`Raises` section.
		|Must| accept and store a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse:
		Parse a the content of an exception entry.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "exception"

class docitem_raises(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`Raises` section.
		|Must| accept and store a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		Parse a list of exceptions
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Raises"
	def parse(self,tr : tracer,entries : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Terminology:
	Exception entry:
		Describes a docstring subtree consisting of a string valued qualified identifier
		and a list of free-form description lines: :wtrl_type:`str, List[str]`
Contract:
	general:
		|Must| accept a sequence of exception entries.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	entries:
		A sequence of exception entries,
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if parsing fails.
		"""
		pos = 0
		while pos < len(entries):
# label is e.g. "RuntimeError", "RangeError",... but could also be a class
# in a different module, therefore we allow qualified identifiers.
			with rules_on_fail(tr, ["RAI-008"]):
				label,pos = expect_label_qualified_identifier(tr,entries,pos)
# factory requires a list of factory function names
			items,pos = expect_list(tr,entries,pos)
			self.add_child(tr,label, docitem_raises_entry, items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Raises =====================================#

#===== begin section Definitions and Terminology ==============#

#----- docitem class Definitions ------------------------------#

class docitem_definitions_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent an entry in the :wtrl_label:`Definitions` section.
		|Must| accept and store a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse:
		Parse a the content of an definition entry.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "dfn"

class docitem_definitions(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Public_methods
Contract:
	general:
		|Must| represent a definition enrty.
		|Must| accept and store a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible
	api:
		Public_methods
Public_methods:
	parse:
		Parse a sequence of definition entries
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Definitions"
	def parse(self,tr : tracer,entries : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| accept a sequence of definition entries.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	entries:
		A sequence of definition entries.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if parsing fails.
		"""
		pos = 0
		while pos < len(entries):
			with rules_on_fail(tr,["DEF-004"]):
				label,pos = expect_label_identifier(tr,entries,pos)
			items,pos = expect_list(tr,entries,pos)
			self.add_child(tr,label, docitem_definitions_entry, items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem class Terminology ------------------------------#

class docitem_terminology_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Terminology:
	Terminology entry:
		Describes a docstring subtree consisting of a string valued qualified identifier
		and a list of free-form description lines: :wtrl_type:`str, List[str]`
Contract:
	general:
		|Must| represent an entry in the :wtrl_label:`Terminology` section.
		|Must| accept and store a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse:
		Parse a the content of an terminology entry.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "term"

class docitem_terminology(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Public_methods
Description:
	A :wtrl_label:`Terminology` section describes natural language expressions informatively.
	As opposed to a :wtrl_label:`Definitions` section, it is never normative and does not
	contain normativity keywords.
Contract:
	general:
		|Must| represent a terminology enrty.
		|Must| accept and store a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible
	api:
		Public_methods
Public_methods:
	parse:
		Parse a sequence of terminology entries
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Terminology"
	def parse(self,tr : tracer,entries : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| accept a sequence of terminology entries.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	entries:
		A sequence of terminology entries.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if parsing fails.
		"""
		pos = 0
		while pos < len(entries):
			with rules_on_fail(tr, ["TERM-005"]):
				label,pos = expect_label(tr,entries,pos)
			items,pos = expect_list(tr,entries,pos)
			self.add_child(tr,label, docitem_terminology_entry, items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Definitions and Terminology ================#

#----- docitem class notes -----------------------------------#

class docitem_notes_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the content of an entry in section :wtrl_label:`Notes`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse:
		|Must| be able to parse a list of text lines of the note.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "notes_entries"

class docitem_notes(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the :wtrl_label:`Notes` section.
		|Must| be able to hold a map from :wtrl_type:`str` to :wtrl_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse the content of a section :wtrl_label:`Notes`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Notes"
	def parse(self,tr : tracer,entries : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Terminology:
	Labelled note:
		A labelled note in this context is a pair :wtrl_type:`str`, :wtrl_type:`List[str]`.
Contract:
	general:
		|Must| parse a sequence of labelled notes.
		|Must| interpret a missing list in a labelled note as an empty list.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	entries:
		The docstring subtree to parse, a sequence of labelled notes, like [:wtrl_type:`str`, :wtrl_type:`List`, :wtrl_type:`str`, :wtrl_type:`List`,...].
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content cannot be interpreted as a sequence of labelled notes.
		"""
		pos = 0
		while pos < len(entries):
			with rules_on_fail(tr, ["PRSR-006"]):
				label,pos = expect_label(tr,entries,pos)
			items,pos = expect_list(tr,entries,pos)
			self.add_child(tr,label, docitem_notes_entry, items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== begin Top ==============================================#

#----- docitem class docstring_class --------------------------#

class docitem_docstring_base(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent a docstring.
		|Must| accept sections as defined in the derived classes.
	constructor:
		|Must| be default-constructible
	traits:
		abstract
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		Parse a docstring tree.
	"""
	def __init__(self) -> None:
		super().__init__()
	def dispatch_map(self) -> Dict[str, Type[docitem_base]]:
		raise NotImplementedError
	def label(self) -> str:
		return "docstring"
	def parse(self,tr : tracer,tree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| accept a complete docstring tree according to the map returned by the derived class' method :wtrl_func:`dispatch_map`.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	tree:
		The docstring tree
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if :wtrl_label:`Preamble` is not the first section found.
		|Must| raise if an invalid section label is found.
		|Must| raise if parsing any of the sections fails.
	NotImplementedError:
		|Must| raise if not invoked for an instance of a derived class.
	"""
		found_preamble = False
		pos = 0
		dmap = self.dispatch_map()
		while pos < len(tree):
# Section labels must be identifiers.
			with rules_on_fail(tr, ["PRSR-005"]):
				label,pos = expect_label_identifier(tr,tree,pos)
			if label in dmap:
				if label == "Preamble":
					found_preamble = True
				elif not found_preamble:
					raise_parsing_error(tr,["PRE-001"],"Preamble is not first.")
				items,pos = expect_list(tr,tree,pos)
				self.add_child(tr,label, dmap[label], items)
			else:
# Choose profile-specific rule for unexpected sections.
				if isinstance(self, docitem_docstring_module):
					rule_ids = ["DOC-003"]
				elif isinstance(self, docitem_docstring_class):
					rule_ids = ["DOC-004"]
				else:
					rule_ids = ["DOC-005"]
				raise_parsing_error_invalid_label(tr,rule_ids,label,dmap)

class docitem_docstring_module(docitem_docstring_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Factory, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the docstring for profile :wtrl_value:`module`.
		|Must| provide a map from :wtrl_type:`str` to :wtrl_type:`Type[docitem_base]` which assigns a docitem class constructor to each allowed section label.
	constructor:
		|Must| be default-constructible
Factory:
	make_docitem_tree:
		|Must| accept a tracer and a docstring, read the profile and generate the AST from it. See docstring of function.
Derived_from:
	docitem_docstring_base
Public_methods:
	dispatch_map:
		Return the forementioned map from label to constructor.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "docstring"
	def dispatch_map(self) -> Dict[str, Type[docitem_base]]:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| return a map from the set of allowed section labels (including the trailing colon) to the constructor of the class representing the section.
		|Must| provide label/constructor pairs for at least the folowing sections: { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Contract`, :wtrl_label:`Description`, :wtrl_label:`Public_functions`, :wtrl_label:`Public_classes`, :wtrl_label:`Public_types`, :wtrl_label:`Public_constants`}
Parameters:
Returns:
	The dict as described in :wtrl_label:`Contract`.
Raises:
		"""
		return {
			"Preamble":docitem_preamble,
			"Definitions":docitem_definitions,
			"Terminology":docitem_terminology,
			"Contract":docitem_contract_module,
			"Description":docitem_description,
			"Notes":docitem_notes,
			"See_also":docitem_see_also,
			"Public_classes":docitem_public_classes,
			"Public_functions":docitem_public_functions,
			"Public_types":docitem_public_types,
			"Public_constants":docitem_public_constants,
			"Public_variables":docitem_public_variables,
			}

class docitem_docstring_class(docitem_docstring_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Factory, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the docstring for profiles  :wtrl_value:`class`.
		|Must| provide a map from :wtrl_type:`str` to :wtrl_type:`Type[docitem_base]` which assigns a docitem class constructor to each allowed section label.
	constructor:
		|Must| be default-constructible
Factory:
	make_docitem_tree:
		|Must| accept a tracer and a docstring, read the profile and generate the AST from it. See docstring of function.
Derived_from:
	docitem_docstring_base
Public_methods:
	dispatch_map:
		Return the forementioned map from label to constructor.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "docstring"
	def dispatch_map(self) -> Dict[str, Type[docitem_base]]:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| return a map from the set of allowed section labels (including the trailing colon) to the constructor of the class representing the section.
		|Must| provide label/constructor pairs for at least the folowing sections: { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Contract`, :wtrl_label:`Derived_from`, :wtrl_label:`Factory`, :wtrl_label:`Description`, :wtrl_label:`Public_classes`, :wtrl_label:`Public_methods`, :wtrl_label:`Public_types`, :wtrl_label:`Public_constants`}
Parameters:
Returns:
	The dict as described in :wtrl_label:`Contract`.
Raises:
		"""
		return {
			"Preamble":docitem_preamble,
			"Definitions":docitem_definitions,
			"Terminology":docitem_terminology,
			"Contract":docitem_contract_class,
			"Derived_from":docitem_derived_from,
			"Factory":docitem_factory,
			"Description":docitem_description,
			"Notes":docitem_notes,
			"See_also":docitem_see_also,
			"Public_classes":docitem_public_classes,
			"Public_methods":docitem_public_methods,
			"Public_types":docitem_public_types,
			"Public_constants":docitem_public_constants,
			"Public_variables":docitem_public_variables,
			}

class docitem_docstring_method(docitem_docstring_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Factory, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the docstring for profiles  :wtrl_value:`function` and :wtrl_value:`method`.
		|Must| provide a map from :wtrl_type:`str` to :wtrl_type:`Type[docitem_base]` which assigns a docitem class constructor to each allowed section label.
	constructor:
		|Must| be default-constructible
Factory:
	make_docitem_tree:
		|Must| accept a tracer and a docstring, read the profile and generate the AST from it. See docstring of function.
Derived_from:
	docitem_docstring_base
Public_methods:
	dispatch_map:
		Return the forementioned map from label to constructor.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "docstring"
	def dispatch_map(self) -> Dict[str, Type[docitem_base]]:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| return a map from the set of allowed section labels (including the trailing colon) to the constructor of the class representing the section.
		|Must| provide label/constructor pairs for at least the folowing sections: { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Contract`, :wtrl_label:`Parameters`, :wtrl_label:`Returns`, :wtrl_label:`Raises`, :wtrl_label:`Description`}
Parameters:
Returns:
	The dict as described in :wtrl_label:`Contract`.
Raises:
		"""
		return {
			"Preamble":docitem_preamble,
			"Definitions":docitem_definitions,
			"Terminology":docitem_terminology,
			"Contract":docitem_contract_method,
			"Parameters":docitem_parameters,
			"Returns":docitem_returns,
			"Raises":docitem_raises,
			"Description":docitem_description,
			"Notes":docitem_notes,
			"See_also":docitem_see_also,
			}

class docitem_docstring_inherited_method(docitem_docstring_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Factory, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the docstring for profile  :wtrl_value:`inherited_method`.
		|Must| provide a map from :wtrl_type:`str` to :wtrl_type:`Type[docitem_base]` which assigns a docitem class constructor to each allowed section label.
	constructor:
		|Must| be default-constructible
Factory:
	make_docitem_tree:
		|Must| accept a tracer and a docstring, read the profile and generate the AST from it. See docstring of function.
Derived_from:
	docitem_docstring_base
Public_methods:
	dispatch_map:
		Return the forementioned map from label to constructor.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "docstring"
	def dispatch_map(self) -> Dict[str, Type[docitem_base]]:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| return a map from the set of allowed section labels (including the trailing colon) to the constructor of the class representing the section.
		|Must| provide label/constructor pairs for at least the folowing sections: { :wtrl_label:`Preamble`, :wtrl_label:`Definitions`, :wtrl_label:`Terminology`, :wtrl_label:`Contract`, :wtrl_label:`Parameters`, :wtrl_label:`Returns`, :wtrl_label:`Raises`, :wtrl_label:`Description`}
Parameters:
Returns:
	The dict as described in :wtrl_label:`Contract`.
Raises:
		"""
		return {
			"Preamble":docitem_preamble,
			"Definitions":docitem_definitions,
			"Terminology":docitem_terminology,
			"Contract":docitem_contract_inherited_method,
			"Description":docitem_description,
			"Notes":docitem_notes,
			"See_also":docitem_see_also,
			}


def make_docitem_tree(tr : tracer, doc_txt : str) -> docitem_docstring_base:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| accept a :wtrl_type:`tracer` instance and a string as parameters.
		|Must| try to parse the string as waterloo docstring and create a docstring tree.
		|Must| determine the profile from the docstring tree and create the appropriate docitem node class.
		|Must| call the docitem node's method :wtrl_func:`parse` and create an Abstract Syntax Tree.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	doc_txt:
		The docstring to parse
Returns:
	|Must| return the docitem node instance containing the AST
Raises:
	ParseError:
		|Must| raise if docstring is empty.
		|Must| raise if section :wtrl_label:`Preamble` is not found.
		|Must| raise if subsection :wtrl_label:`Preamble.profile` is not found.
		|Must| raise if subsection :wtrl_label:`Preamble.profile` does not contain exactly one item.
		|Must| raise if the content of subsection :wtrl_label:`Preamble.profile` is not an identifier..
		|Must| raise if subsection :wtrl_label:`Preamble.profile` does not contain a valid profile.
	BaseException:
		|Must_not| propagate exceptions from :wtrl_type:`get_profile_of_tree`.
		|May| propagate exceptions from method :wtrl_func:`parse_indent_docstring`.
		|May| propagate exceptions from method :wtrl_type:`docitem_docstring_base`. :wtrl_func:`parse`.
Notes:
	Drift:
		Last check on 2026-01-22
	"""
	tree = parse_indent_docstring(tr, doc_txt)
# Extract profile
	if tree == []:
		raise_parsing_error(tr,["DOC-007"],"Empty docstring.")
	try:
		profile = get_profile_of_tree(tr,tree)
	except SectionNotFoundError:
		raise_parsing_error(tr,["PRE-001"],"Section 'Preamble' not found.")
	except SubsectionNotFoundError:
		raise_parsing_error(tr,["PRE-003"],"Subection 'Preamble.profile' not found.")
	except NoContentError:
		raise_parsing_error(tr,["PRE-004"],"Section 'Preamble.profile' must have exactly one item.")
	except Exception as exc:
		raise
#		raise_parsing_error(tr,["UNSP-999"],f"get_profile_of_tree: Unspecified error, check implementation: {exc}.")
# This looks redundant because later we directly check for allowed profiles, but
# we should check the rules in certain order so that behaviour remains predictible.
	if not RE_IDENTIFIER_COMPILED.fullmatch(profile):
		raise_parsing_error(tr,["PRE-014"],"'Preamble.profile' must be an identifier.")
# Now we know the profile is an identifier.
	di_node : docitem_docstring_base
	if profile == "module":
		di_node = docitem_docstring_module()
	elif profile == "class":
		di_node =  docitem_docstring_class()
	elif profile in ("function","method"):
		di_node = docitem_docstring_method()
	elif profile == "inherited_method":
		di_node = docitem_docstring_inherited_method()
	else:
		raise_parsing_error(tr,["PRE-005"],f"invalid profile: '{profile}'")
	di_node.parse(tr,tree)
	return di_node

#===== end Top ================================================#

def validate_docstring_module(tr : tracer, obj: object, top : docitem_docstring_module,node_contract : docitem_map_base,node_normative_sections : docitem_list_base) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| validate the docitem tree :wtrl_var:`top` against the module object :wtrl_var:`obj`.
		|Must| ensure that :wtrl_label:`Contract` contains sections :wtrl_label:`general` and :wtrl_label:`api`.
		|Must| ensure that all sections declared as normative exist.
		|Must| enforce normativity/existence consistency for :wtrl_label:`Public_classes`, :wtrl_label:`Public_functions`, :wtrl_label:`Public_types`, :wtrl_label:`Public_variables`, :wtrl_label:`Public_constants`:
		|Must| collect errors and warnings in the tracer object passed.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The callable object to validate against.
	top:
		The docitem tree to validate.
	node_contract:
		The node for section :wtrl_label:`Contract` already parsed by the caller.
	node_normative_sections:
		The node for section :wtrl_label:`Preamble.normative_sections` already parsed by the caller.
Returns:
	|Must| return |None|
Raises:
	RuntimeError:
		|Must| raise if any of the validation conditions listet in :wtrl_label:`general` fails.
		|Must| raise if a section exists but is not listed as normative.
		|Must| raise if a section is listed as normative but does not exist.
Notes:
	Usage:
		This function is typically not called directly. Please call :wtrl_func:`validate_docstring` instead.
	Drift:
		Last check on 2026-01-23
	"""
#===== Contract must exist ====================================#
# checked by caller
#----- general must exist -------------------------------------#
	with traced_section(tr, "Contract"):
		if "general" not in node_contract.items():
			raise_validation_error(tr,obj,["CON-022"],"Section 'general' does not exist.")

		if "api" in node_contract.items():
			node_api = node_contract._items["api"]
			with traced_section(tr, "api"):
# Rule: each entry in api must refer to a normative section
				for ref in node_api.items():
					if ref not in node_normative_sections.items():
						raise_validation_error(tr,obj,["PRE-011"],f"Section '{ref}' is not listed in section 'Preamble.normative_sections'. We have {node_normative_sections.items()}.")
#===== Public_* sections: normativity / existence checks ======#
	with traced_section(tr, "Public_*"):
		section_normativity = [
			("Public_classes", "PCL-002"),
			("Public_functions", "PFN-002"),
			("Public_types", "PTY-002"),
			("Public_variables", "PVAR-002"),
			("Public_constants", "PCON-002"),
		]
		for sec_name, rule_id in section_normativity:
			if sec_name in top.items() and sec_name not in node_normative_sections.items():
				raise_validation_error(tr,obj,[rule_id], f"Section '{sec_name}' exists but is not listed as normative.")
			if sec_name in node_normative_sections.items() and sec_name not in top.items():
				raise_validation_error(tr,obj,["PRE-012"],f"Section '{sec_name}' is marked normative but does not exist.")

def validate_docstring_class(tr : tracer, obj: object, top : docitem_docstring_class,node_contract : docitem_map_base,node_normative_sections : docitem_list_base) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| validate the docitem tree :wtrl_var:`top` against the class object :wtrl_var:`obj`.
		|Must| ensure that sections :wtrl_label:`general`, :wtrl_label:`constructor`, :wtrl_label:`api` exist. 
		|Must| ensure that each section listed in :wtrl_label:`api` is normative.
		|Must| ensure that subsection :wtrl_label:`traits` -- if exists -- contains only allowed values and no duplicates.
		|Must| ensure that section :wtrl_label:`Derived_from` exists if listed in :wtrl_label:`normative_sections`.
		|Must| ensure that each entry in :wtrl_label:`Derived_from` is a base class of :wtrl_var:`obj`:wtrl_op:`\.`:wtrl_var:`__class__`.
		|Must| enforce normativity/existence consistency for :wtrl_label:`Public_classes`, :wtrl_label:`Public_methods`, :wtrl_label:`Public_variables`, :wtrl_label:`Public_constants`:
		|Must| collect errors and warnings in the tracer object passed.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The callable object to validate against.
	top:
		The docitem tree to validate.
	node_contract:
		The node for section :wtrl_label:`Contract` already parsed by the caller.
	node_normative_sections:
		The node for section :wtrl_label:`Preamble.normative_sections` already parsed by the caller.
Returns:
	|Must| return |None|
Raises:
	RuntimeError:
		|Must| raise if any of the validation conditions listet in :wtrl_label:`general` fails.
		|Must| raise if a section exists but is not listed as normative.
		|Must| raise if a section is listed as normative but does not exist.
Notes:
	Usage:
		This function is typically not called directly. Please call :wtrl_func:`validate_docstring` instead.
	Drift:
		Last check on 2026-01-23
	"""
#===== Preamble must exist ====================================#
	with traced_section(tr, "Preamble"):
# Rule: Preamble must exist. We do not allow purely informative docstrings.
		if "Preamble" not in top.items():
			raise_validation_error(tr,obj,["PRE-001"],"Section 'Preamble' does not exist.")
		node_preamble = top._items["Preamble"]
#..... profile must exist .....................................#
# checked by caller
#..... normative_sections must exist ..........................#
# checked by caller

#===== Contract must exist ====================================#
# checked by caller
#----- general, constructor must exist ------------------------#
	with traced_section(tr, "Contract"):
		if "general" not in node_contract.items():
			raise_validation_error(tr,obj,["CON-023"],"Section 'general' does not exist.")
		if "constructor" not in node_contract.items():
			raise_validation_error(tr,obj,["CON-007"],"Section 'constructor' does not exist.")

		if "api" in node_contract.items():
			node_api = node_contract._items["api"]
			with traced_section(tr, "api"):
# Rule: each entry in api must refer to a normative section
				for ref in node_api.items():
					if ref not in node_normative_sections.items():
						raise_validation_error(tr,obj,["PRE-011"],f"Section '{ref}' is not listed in section 'Preamble.normative_sections'. We have {node_normative_sections.items()}.")
		if "traits" in node_contract.items():
			node_traits = node_contract._items["traits"]
			with traced_section(tr, "traits"):
				traits = list(node_traits.items())
				if len(traits) != len(set(traits)):
					raise_validation_error(tr, obj, ["CON-016"], "Trait identifiers must not occur more than once.")
				allowed_traits = {"final", "abstract"}
				for tr_name in traits:
					if tr_name not in allowed_traits:
						raise_validation_error(tr, obj, ["CON-017"], f"Trait '{tr_name}' is not allowed; allowed: {sorted(allowed_traits)}")
#===== Derived_from must exist if normative ===================#
	with traced_section(tr, "Derived_from"):
		if "Derived_from" in node_normative_sections.items():
			if "Derived_from" not in top.items():
				raise_validation_error(tr,obj,["PRE-012"],"Section 'Derived_from' is marked normative but does not exist.")
# If Derived_from present, entries must refer to direct base classes
		if "Derived_from" in top.items():
			base_names = [b.__name__ for b in getattr(obj, "__bases__", ())]
			node_derived = top._items["Derived_from"]
			for bname in node_derived.items():
				if bname not in base_names:
					raise_validation_error(tr,obj,["DER-003"],f"Class '{bname}' is not a direct base; direct bases are {base_names}.")
#===== Public_* sections: normativity / existence checks ------#
	with traced_section(tr, "Public_*"):
		section_normativity = [
			("Public_classes", "PCL-008"),
			("Public_methods", "PMET-002"),
			("Public_variables", "PVAR-008"),
			("Public_constants", "PCON-009"),
		]
		for sec_name, rule_id in section_normativity:
			if sec_name in top.items() and sec_name not in node_normative_sections.items():
				raise_validation_error(tr,obj,[rule_id], f"Section '{sec_name}' exists but is not listed as normative.")
			if sec_name in node_normative_sections.items() and sec_name not in top.items():
				raise_validation_error(tr,obj,["PRE-012"],f"Section '{sec_name}' is marked normative but does not exist.")

def validate_docstring_method(tr : tracer, obj: object, top : docitem_docstring_method,node_contract : docitem_map_base,node_normative_sections : docitem_list_base) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| validate the docitem tree :wtrl_var:`top` against the callable object :wtrl_var:`obj`.
		|Must| ensure that :wtrl_label:`Contract` contains a section :wtrl_label:`general`.
		|Must| ensure that all sections declared as normative exist.
		|Must| ensure that section :wtrl_label:`Parameters` exists.
		|Must| ensure that section :wtrl_label:`Returns` exists.
		|Must| ensure that section :wtrl_label:`Raises` exists.
		|Must| ensure that each parameter mentioned in section :wtrl_label:`Parameters` is in the callable's signature.
		|Must| ensure that each parameter in the callable's signature is mentioned in section :wtrl_label:`Parameters`.
		|Must| ensure that each exception listed in section :wtrl_label:`Raises` refers to an existing class.
		|Must| ensure that each exception listed in section :wtrl_label:`Raises` is a subclass of :wtrl_type:`BaseException`.
		|Must| resolve each exception listed in section :wtrl_label:`Raises` by importing the longest module prefix and traversing remaining attributes; |must| fall back to the callable's globals, its defining module, and :wtrl_value:`builtins`.
		|Must| collect warnings in the tracer object passed.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The callable object to validate against.
	top:
		The docitem tree to validate.
	node_contract:
		The node for section :wtrl_label:`Contract` already parsed by the caller.
	node_normative_sections:
		The node for section :wtrl_label:`Preamble.normative_sections` already parsed by the caller.
Returns:
	|Must| return |None|
Raises:
	RuntimeError:
		|Must| raise if any of the validation conditions listet in :wtrl_label:`general` fails.
Notes:
	Usage:
		This function is typically not called directly. Please call :wtrl_func:`validate_docstring` instead.
	"""
	with traced_section(tr, "method"):
#===== Contract ===============================================@
# Contract must have a general section.
		with traced_section(tr, "Contract"):
			if "general" not in node_contract.items():
				raise_validation_error(tr,obj,["CON-024"],"Section 'general' does not exist.")
# If caller marks other sections normative, ensure they exist.
			for sec in node_normative_sections.items():
				if sec == "Contract":
					continue
				if sec not in top.items():
					raise_validation_error(tr,obj,["PRE-012"],f"Section '{sec}' is listed as normative but does not exist.")
#===== Parameters must exist ==================================#
		with traced_section(tr, "Parameters"):
			if "Parameters" not in top.items():
				raise_validation_error(tr,obj,["PAR-001"],"Section 'Parameters' does not exist.")
#===== Returns must exist =====================================#
		with traced_section(tr, "Returns"):
			if "Returns" not in top.items():
				raise_validation_error(tr,obj,["RET-001"],"Section 'Returns' does not exist.")
# Check rule RET-004 here: encourage explicit truthy/falsey markers
			else:
				node_returns = top._items["Returns"]
				ret_ann: object = inspect.Signature.empty
				try:
					hints_ret = get_type_hints(obj, include_extras=True)
					ret_ann = hints_ret.get("return", inspect.Signature.empty)
				except Exception:
					if callable(obj):
						try:
							ret_ann = inspect.signature(obj).return_annotation
						except Exception:
							ret_ann = inspect.Signature.empty
					else:
						ret_ann = inspect.Signature.empty
				if returns_bool(ret_ann):
					joined = " ".join(node_returns.items())
					if "|True|" not in joined and "|False|" not in joined:
						warn_validation(tr, obj, ["RET-004"], "Returns should mention truthy/falsey outcome using tokens |True| or |False|.")
# Check rule RET-004 here

#===== Raises must exist ======================================#
		with traced_section(tr, "Raises"):
			if "Raises" not in top.items():
				raise_validation_error(tr,obj,["RAI-001"],"Section 'Raises' does not exist.")
#===== Parameters must match signature ========================#
		if inspect.isfunction(obj) or inspect.ismethod(obj):
			try:
				sig = inspect.signature(obj)
			except (TypeError, ValueError):
				sig = None
			if sig is not None:
				param_names = [p for p in sig.parameters if p not in ("self","cls")]
				doc_params = list(top._items["Parameters"].items())
				for p in doc_params:
					if p not in param_names:
						raise_validation_error(tr,obj,["PAR-005"],f"Parameter '{p}' documented but not in signature {param_names}.")
				for p in param_names:
					if p not in doc_params:
						raise_validation_error(tr,obj,["PAR-004"],f"Parameter '{p}' in signature but not documented.")
#===== Raises must reference existing exception classes =======#
			with traced_section(tr, "Raises"):
				node_raises = top._items["Raises"]
				assert isinstance(node_raises, docitem_raises)
				for exc_name in node_raises.items().keys():
					try:
						exc_obj, _ = resolve_object(exc_name, obj)
					except Exception:
						if hasattr(builtins, exc_name):
							exc_obj = getattr(builtins, exc_name)
						else:
							exc_obj = None
					exc_cls = exc_obj if inspect.isclass(exc_obj) else None
					if exc_cls is None or not inspect.isclass(exc_cls):
						raise_validation_error(tr,obj,["RAI-004"], f"Exception '{exc_name}' listed in Raises does not refer to an existing class.")
					if not issubclass(exc_cls, BaseException):
						raise_validation_error(tr,obj,["RAI-007"], f"Exception '{exc_name}' is not a subclass of BaseException.")

def validate_docstring_inherited_method(tr : tracer, obj: object, top : docitem_docstring_inherited_method,node_contract : docitem_map_base,node_normative_sections : docitem_list_base) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| validate the docitem tree :wtrl_var:`top` against the callable object :wtrl_var:`obj`.
		|Must| ensure that :wtrl_label:`Contract` contains a section :wtrl_label:`general`.
		|Must| ensure that all sections declared as normative exist.
		|Must| ensure that each parameter mentioned in section :wtrl_label:`Parameters` is in the callable's signature.
		|Must| ensure that each parameter in the callable's signature is mentioned in section :wtrl_label:`Parameters`.
		|Must| ensure that each exception listed in section :wtrl_label:`Raises` refers to an existing class.
		|Must| ensure that each exception listed in section :wtrl_label:`Raises` is a subclass of :wtrl_type:`BaseException`.
		|Must| resolve each exception listed in section :wtrl_label:`Raises` by importing the longest module prefix and traversing remaining attributes; |must| fall back to the callable's globals, its defining module, and :wtrl_value:`builtins`.
		|Must| collect warnings in the tracer object passed.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The callable object to validate against.
	top:
		The docitem tree to validate.
	node_contract:
		The node for section :wtrl_label:`Contract` already parsed by the caller.
	node_normative_sections:
		The node for section :wtrl_label:`Preamble.normative_sections` already parsed by the caller.
Returns:
	|Must| return |None|
Raises:
	RuntimeError:
		|Must| raise if any of the validation conditions listet in :wtrl_label:`general` fails.
Notes:
	Usage:
		This function is typically not called directly. Please call :wtrl_func:`validate_docstring` instead.
	Drift:
		Docstring and function are INCOMPLETE!
	"""
	with traced_section(tr, "inherited_method"):
#===== Contract ===============================================@
# Contract must have a general section.
		with traced_section(tr, "Contract"):
			if "general" not in node_contract.items():
				raise_validation_error(tr,obj,["CON-036"],"Section 'general' does not exist.")
# If caller marks other sections normative, ensure they exist.
			for sec in node_normative_sections.items():
				if sec == "Contract":
					continue
				if sec not in top.items():
					raise_validation_error(tr,obj,["PRE-012"],f"Section '{sec}' is listed as normative but does not exist.")
# Special for inherited methods.
			if "base" not in node_contract.items():
				raise_validation_error(tr,obj,["CON-039"],"Section 'base' does not exist.")
			with traced_section(tr, "base"):
				node_base = node_contract.item("base")
				if not isinstance(node_base, docitem_base_to_inherit_from):
					raise_validation_error(tr,obj,["CON-040"],"Section 'base' malformed.")
				base_items = node_base.items()
				if len(base_items) != 1:
					raise_validation_error(tr,obj,["CON-040"],"Section 'base' must contain exactly one entry.")
				base_ref = next(iter(base_items))
				if not isinstance(base_ref, str) or not RE_QUALIFIED_IDENTIFIER_COMPILED.fullmatch(base_ref):
					raise_validation_error(tr,obj,["CON-041"],f"Entry '{base_ref}' is not a qualified identifier.")
				try:
					base_obj, _ = resolve_object(base_ref, obj)
				except Exception as exc:
					raise_validation_error(tr,obj,["CON-042"],f"Base method '{base_ref}' cannot be resolved: {exc}")
				if not (inspect.isfunction(base_obj) or inspect.ismethod(base_obj)):
					raise_validation_error(tr,obj,["CON-042"],f"Base reference '{base_ref}' is not a function or method.")
# CON-043: base_obj must belong to a base class of the documented class.
				base_qname = getattr(base_obj, "__qualname__", "")
				base_owner_name = base_qname.rsplit(".", 1)[0] if "." in base_qname else ""
				owner_name = getattr(obj, "__qualname__", "")
				owner_class_name = owner_name.rsplit(".", 1)[0] if "." in owner_name else ""
				base_owner_cls = None
				owner_cls = None
				mod_obj = inspect.getmodule(obj)
				if base_owner_name and mod_obj:
					try:
						base_owner_cls = resolve_object(f"{mod_obj.__name__}.{base_owner_name}", obj)[0]
					except Exception:
						base_owner_cls = None
				if owner_class_name and mod_obj:
					try:
						owner_cls = resolve_object(f"{mod_obj.__name__}.{owner_class_name}", obj)[0]
					except Exception:
						owner_cls = None
				if base_owner_cls is None or owner_cls is None or not inspect.isclass(base_owner_cls) or not inspect.isclass(owner_cls) or not issubclass(owner_cls, base_owner_cls):
					raise_validation_error(tr,obj,["CON-043"],f"Base method '{base_ref}' is not defined on a base class of '{owner_class_name}'.")
# CON-044: names must match
				method_name = getattr(obj, "__name__", None)
				base_name = getattr(base_obj, "__name__", None)
				if method_name != base_name:
					raise_validation_error(tr,obj,["CON-044"],f"Base method name '{base_name}' does not match '{method_name}'.")
# CON-045: referenced method must have a valid docstring.
				if base_obj.__doc__ is None:
					raise_validation_error(tr,obj,["CON-045"],f"Base method name '{base_name}' does not have a docstring.")
				try:
					top_base_obj = make_docitem_tree(tr,base_obj.__doc__)
					validate_docstring(tr,base_obj,top_base_obj)
				except ParseError:
					raise_validation_error(tr,obj,["CON-045"],f"Base method '{base_name}': Validation raises a ParseError.")
				except ValidationError:
					raise_validation_error(tr,obj,["CON-045"],f"Base method '{base_name}': Validation raises a ValidationError.")
# CON-046: see what we can do - this won't be perfect.
				try:
					base_hints = get_type_hints(base_obj)
				except Exception:
					base_hints = None
				try:
					obj_hints = get_type_hints(obj)
				except Exception:
					obj_hints = None
				if base_hints and obj_hints:
					sig_base = inspect.signature(typing.cast(Callable[..., Any], base_obj))
					sig_obj = inspect.signature(typing.cast(Callable[..., Any], obj))
# Compare parameter types
					for name, base_param in sig_base.parameters.items():
						if name not in sig_obj.parameters:
							continue
						obj_param = sig_obj.parameters[name]
						base_ann = base_param.annotation
						obj_ann = obj_param.annotation
						if base_ann is inspect._empty or obj_ann is inspect._empty:
							continue
						if base_hints.get(name) != obj_hints.get(name):
							warn_validation(tr,obj,["CON-046"],f"Type of parameter '{name}' differs between base method and override.")
# COmpare return types
					if sig_base.return_annotation is not inspect._empty and sig_obj.return_annotation is not inspect._empty:
						if base_hints.get("return") != obj_hints.get("return"):
							warn_validation(tr,obj,["CON-046"],"Return type differs between base method and override.")


#===== helpers for See_also resolution ========================#

def _qualified_object_name(obj: object) -> str:
	if inspect.ismodule(obj):
		return obj.__name__
	mod_name = getattr(obj, "__module__", None)
	qual_name = getattr(obj, "__qualname__", None)
	if isinstance(mod_name, str) and isinstance(qual_name, str):
		return f"{mod_name}.{qual_name}"
	name = getattr(obj, "__name__", None)
	if isinstance(name, str):
		return name
	return str(obj)

def _get_public_section_entries(top: docitem_docstring_base, section_label: str, expected_node_type: Type[docitem_map_base]) -> set[str]:
	public: set[str] = set()
	if section_label in top.items():
		node = top._items[section_label]
		assert isinstance(node, expected_node_type)
		public = set(node.items().keys())
	return public


def resolve_object(ref: str, current_obj: object) -> tuple[object, str]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Definitions, Contract, Parameters, Returns, Raises
Definitions:
	Identifier:
		An Identifier is a string matching the regular expression ``[a-zA-Z_][a-zA-Z0-9_]*``.
	Qualified_Identifier:
		A Qualified Identifier is a string formed by concatenating one or more Identifiers with "." as separator.
	Public_object:
		An object that is importable as a module attribute or as an attribute of an object reachable from an importable module.
	Resolved_reference:
		A pair (obj, qname) where qname is a candidate reference string that was successfully resolved and obj is the resulting Python object.
Contract:
	general:
		|Must| attempt to resolve ref (an |term|`Identifier` or |term|`Qualified_Identifier`) to an existing |term|`Public_object`.
		|Must| return the first successfully resolved candidate together with the exact candidate string that succeeded.
		|Must| treat a ref containing "." as already qualified and try it directly before any context-derived qualification.
		|Must| for an unqualified ref, construct resolution candidates from current_obj in the following order where applicable:
		|Must| (1) <module_of_current_obj>.<ref> if the module of current_obj can be determined,
		|Must| (2) <current_obj.__module__>.<current_obj.__qualname__>.<ref> if current_obj is a class,
		|Must| (3) <current_obj.__module__>.<enclosing_qualname_prefix>.<ref> if current_obj is a function nested in a qualname path,
		|Must| and finally (4) ref as last fallback.
		|Must| skip duplicate candidate strings while preserving the candidate order.
		|Must| resolve a candidate by importing the longest importable module prefix of the candidate and then applying getattr for each remaining "."-separated attribute component.
		|Must| raise ImportError if none of the candidates can be resolved.
Parameters:
	ref:
		Reference string to resolve. It may be an Identifier (unqualified) or a Qualified Identifier (contains ".").
	current_obj:
		Context object that determines which qualified candidates are tried for an unqualified ref.
Returns:
	|Must| return a |term|`Resolved_reference`.
Raises:
	ImportError:
		|Must| raise if ref cannot be resolved via any candidate derived from current_obj and the fallback candidate ref.
		|Must| raise if a candidate contains an attribute chain that cannot be traversed (missing attribute) or if no module prefix of the candidate can be imported.
	"""
	def _import_chain(qname: str) -> object:
		parts = qname.split(".")
		for i in range(len(parts), 0, -1):
			mod_cand = ".".join(parts[:i])
			try:
				mod = importlib.import_module(mod_cand)
			except ImportError:
				continue
			attr_parts = parts[i:]
			obj_attr: object = mod
			for p in attr_parts:
				obj_attr = getattr(obj_attr, p)
			return obj_attr
		raise ImportError(f"Could not import any module prefix from {qname} (1)")

	candidates: List[str] = []
	if "." in ref:
		candidates.append(ref)
	else:
		mod = inspect.getmodule(current_obj)
		if mod:
			candidates.append(f"{mod.__name__}.{ref}")
		if inspect.isclass(current_obj):
			candidates.append(f"{current_obj.__module__}.{current_obj.__qualname__}.{ref}")
		elif inspect.isfunction(current_obj):
			qual = getattr(current_obj, "__qualname__", "")
			if "." in qual:
				prefix = qual.rsplit(".", 1)[0]
				candidates.append(f"{current_obj.__module__}.{prefix}.{ref}")
	candidates.append(ref)

	seen: set[str] = set()
	for cand in candidates:
		if cand in seen:
			continue
		seen.add(cand)
		try:
			obj = _import_chain(cand)
			return obj, cand
		except SyntaxError:
			raise
		except PermissionError:
			raise
		except Exception as e:
			continue
	raise ImportError(f"Could not resolve reference '{ref}' from context '{_qualified_object_name(current_obj)}'.")

"""
Collect all occurrences of tokens of the form |term|`Identifier` in a docitem tree.
"""
def _collect_term_refs(node: docitem_base) -> set[str]:
	refs: set[str] = set()
	if isinstance(node, docitem_list_base):
		for item in node.items():
			for m in re.finditer(r"\|term\|\`([A-Za-z_][A-Za-z0-9_]*)\`", item):
				refs.add(m.group(1))
	if isinstance(node, docitem_map_base):
		for child in node.items().values():
			refs.update(_collect_term_refs(child))
	return refs


def validate_docstring(tr : tracer,obj: object, top : docitem_docstring_base | None = None, _seen: Dict[object,docitem_docstring_base] | None = None) -> docitem_docstring_base:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises, See_also
Contract:
	general:
		|Must| validate the docitem tree :wtrl_var:`top` against the object :wtrl_var:`obj` if :wtrl_var:`top` is not |None|.
		|Must| analyze the docstring of :wtrl_var:`obj` and create a docitem tree if :wtrl_var:`top` is |None|.
		|Must| ensure that section :wtrl_label:`Preamble` exists.
		|Must| ensure that section :wtrl_label:`profile` exists in section :wtrl_label:`Preamble`.
		|Must| ensure that section :wtrl_label:`profile` contains exactly one item.
		|Must| ensure that the item in section :wtrl_label:`profile` is an identifier.
		|Must| ensure that the item in section :wtrl_label:`profile` is one of the allowed profiles.
		|Must| ensure that section :wtrl_label:`normative_sections` exists in section :wtrl_label:`Preamble`.
		|Must| ensure that each item in section :wtrl_label:`normative_sections` refers to an existing section.
		|Must| ensure that no item in section :wtrl_label:`normative_sections` appears more than once.
		|Must| ensure that each section which contains at least one of the normativity keywords is listed under :wtrl_label:`normative_sections`, unless the section is explicitly declared informative by the active profile/template.
		|Must| ensure that section :wtrl_label:`Contract` exists.
		|Must| ensure that section :wtrl_label:`Contract` is listed in section :wtrl_label:`normative_sections`.

		|Must| ensure that section :wtrl_label:`Definitions` --provided it exists-- is listed in section :wtrl_label:`normative_sections`, regardless of whether it contains normativity keywords.
		|Must| look for ocurrences of token :wtrl_lit:`\|term\|\`<Identifier>\`` in the docitem tree and ensure that the referenced term is defined in section :wtrl_label:`Definitions`.

		|Must| ensure that section :wtrl_label:`Terminology` --provided it exists-- is considered informative and NOT listed in section :wtrl_label:`normative_sections`.
		|Must| enforce profile related tests depending on the profile and call one of the validators :wtrl_func:`validate_docstring_*`.

		|Must| examine section :wtrl_label:`See_also` if it exists.
		|Must| ensure the existence of each item listed in :wtrl_label:`See_also`.
		|Must| ensure that each item listed in :wtrl_label:`See_also` has a valid docstring.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The object to validate against (module, class or callable).
	top:
		The docitem tree to validate.
	_seen:
		Recording objects alreading validated in order to avoid recursion divergence.
Returns:
	|Must| return |None|
Raises:
	RuntimeError:
		|Must| raise if any of the validation conditions listet in :wtrl_label:`general` fails.
Notes:
	Usage:
		This function should be pretty easy to use, if you leave out parameter :wtrl_var:`top`.
		You simply pass the object, the docstring of which you would like to validate.
		Note, however, that this function only validates for inner consistency of the
		the docstring, it does not validate for coverage (i.e. check existence and docstrings
		of all objects inside the class)
See_also:
	validate_class_coverage, validate_module_coverage
	"""
# validate_docstring is called recursively in coverage validations,
# therefore we must make sure not to run into infinite recusrsion.
	if _seen is None:
		_seen = {}
	if obj in _seen:
		return _seen[obj]
	if top == None:
		if obj.__doc__ is None:
			raise_has_no_docstring(tr,["DOC-001"],obj)
		top = make_docitem_tree(tr,obj.__doc__)
	_seen[obj] = top
# Log some debug info
	tr.add_info(f"validating '{get_obj_name(obj)}'")
		
#===== Preamble must exist ====================================#
	with traced_section(tr, "Preamble"):
# Rule pre-01: Preamble must exist. We do not allow purely informative docstrings.
		if "Preamble" not in top.items():
			raise_validation_error(tr,obj,["PRE-001"],"Section 'Preamble' does not exist.")
		node_preamble = top._items["Preamble"]
#..... profile must exist .....................................#
# Rule pre-02: profile must exist.
		if not "profile" in node_preamble.items():
			raise_validation_error(tr,obj,["PRE-003"],"Section 'profile' does not exist.")
# Here we know it exists.
		node_profile = node_preamble.item("profile")
		with traced_section(tr, "profile"):
			assert isinstance(node_profile,docitem_list_base)
# Rule pre-xx
			if len(node_profile.items()) > 1:
				raise_validation_error(tr,obj,["PRE-004"],"Only one item allowed")
# Rule pre-xx
			if not RE_IDENTIFIER_COMPILED.fullmatch(node_profile._items[0]):
				raise_validation_error(tr,obj,["PRE-014"],"expected identifier, got '{node_profile._items[0]}'.")
# For the current version we tighten this rule
			if not node_profile._items[0] in ("module","class","function","method","inherited_method"):
				raise_validation_error(tr,obj,["PRE-005"],f"expected one of {{'module','class','function','method','inherited_method'}}, got '{node_profile._items[0]}'.")

# Rule pre-03: normative_sections must exist and be non-empty. Non-emptyness is implied by existence and normativity of Contract.
		with traced_section(tr, "normative_sections"):
			if "normative_sections" not in node_preamble.items():
				raise_validation_error(tr,obj,["PRE-006"],"Section 'normative_sections' does not exist.")
# Here we know it exists.
			node_normative_sections =  node_preamble.item("normative_sections")
# Chill mypy. We know it's a docitem_list_base.
			assert isinstance(node_normative_sections,docitem_list_base)
			seen = set()
			for sec in node_normative_sections.items():
# Rule pre-05: each entry must point to an existing section.
				if not sec in top.items():
					raise_validation_error(tr,obj,["PRE-012"],f"Entry '{sec}' does not refer to an existing section.")
# Rule pre-xx
				if sec in seen:
					raise_validation_error(tr,obj,["PRE-009"],"Entry '{sec}' is duplicate.")
				seen.add(sec)
# Rule: Any section containing one of the keywords of normativity
# must be listed under normative_sections.
		for label,item in top.items().items():
			if item.has_norm_keywords():
				if label not in node_normative_sections.items():
					raise_validation_error(tr,obj,["PRE-013"],f"Section '{label}' contains a keyword of normativity but is not listed in normative_sections.")

# Determine profile once for later checks
	profile = node_profile._items[0]

#===== Contract must exist ====================================#
	with traced_section(tr, "Contract"):
		if "Contract" not in top.items():
			rule = "CON-001"
			if profile == "class":
				rule = "CON-004"
			elif profile in ("method","function"):
				rule = "CON-019"
			raise_validation_error(tr,obj,[rule],"Section 'Contract' does not exist.")
# Rule pre-04: the contract must be listed as normative
		if not "Contract" in node_normative_sections.items():
			rule = "CON-002"
			if profile == "class":
				rule = "CON-005"
			elif profile in ("method","function"):
				rule = "CON-020"
			raise_validation_error(tr,obj,[rule],"Section 'Contract' must be listed under 'normative_sections'.")
		node_contract = top._items["Contract"]
# Chill mypy. We know it's a docitem_map_base.
		assert isinstance(node_contract,docitem_map_base)
	
#===== If Definitions exists it must be normative =============#
	with traced_section(tr, "Definitions"):
		if "Definitions" in top.items():
			node_definitions = top._items["Definitions"]
# Chill mypy
			assert isinstance(node_definitions, docitem_map_base)
			if not "Definitions" in node_normative_sections.items():
				raise_validation_error(tr,obj,["DEF-002"],"Section 'Definitions' exists but is not normative.")
			def_names = set(node_definitions.items().keys())
# Defitem content should not be empty.
			for name in def_names:
				node_defitem = node_definitions.item(name)
				if node_defitem.empty():
					warn_validation(tr,obj,["DEF-009"],"Defitem content should not be empty.")
		else:
			node_definitions = None
			def_names = set()
# Ensure each reference term appears in section `Definitions`.
		term_refs = _collect_term_refs(top)
		if term_refs:
			if node_definitions is None:
				raise_validation_error(tr,obj,["DEF-007"], "Token |term| is used but section 'Definitions' is missing.")
			for term in term_refs:
				if term not in def_names:
					raise_validation_error(tr,obj,["DEF-008"], f"Token |term|`{term}` references an undefined term.")


#===== If Terminology exists it must NOT be normative =========#
	with traced_section(tr, "Terminology"):
		if "Terminology" in top.items():
			if "Terminology" in node_normative_sections.items():
				raise_validation_error(tr,obj,["TERM-002"],"Section 'Terminology ' must not be normative.")
			node_terminology = top.item("Terminology")
# Defitem content should not be empty.
			for name in node_terminology.items():
				node_term = node_terminology.item(name)
				if node_term.empty():
					warn_validation(tr,obj,["TERM-008"],"Term content should not be empty.")
# Cases
	profile = node_profile._items[0]
	if profile == "module":
		assert isinstance(top,docitem_docstring_module)
		validate_docstring_module(tr,obj,top,node_contract,node_normative_sections)
	elif profile == "class":
		assert isinstance(top,docitem_docstring_class)
		validate_docstring_class(tr,obj,top,node_contract,node_normative_sections)
	elif profile in ("method","function"):
		assert isinstance(top,docitem_docstring_method)
		validate_docstring_method(tr,obj,top,node_contract,node_normative_sections)
	elif profile == "inherited_method":
		assert isinstance(top,docitem_docstring_inherited_method)
		validate_docstring_inherited_method(tr,obj,top,node_contract,node_normative_sections)
	else:
		raise_validation_error(tr,obj,["PRE-005"],f"Unknown profile: {profile}")
#===== If See_also exists, more tests apply ===================#
	with traced_section(tr, "See_also"):
		if "See_also" in top.items():
			node_see_also = top._items["See_also"]
			for item_see_also in node_see_also.items():
				try:
					target_obj, target_name = resolve_object(item_see_also, obj)
				except Exception as e:
					rules = ["SEE-004"] if "See_also" in node_normative_sections.items() else ["SEE-003"]
					raise_validation_error(tr,obj,rules, f"See_also reference '{item_see_also}' cannot be resolved: {e}.")
				if target_obj is obj:
					raise_validation_error(tr,obj,["SEE-005"], f"See_also reference '{item_see_also}' must not refer to the object itself.")
				if target_obj in _seen:
					continue
				if not isinstance(getattr(target_obj, "__doc__", None), str):
					raise_validation_error(tr,obj,["SEE-006"], f"See_also reference '{item_see_also}' has no docstring.")
				validate_docstring(tr,target_obj, None, _seen)
	return top

def validate_class_class_coverage(tr : tracer,obj: type[object], doc_class: docitem_docstring_class) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze nested classes documented in :wtrl_label:`Public_classes`.
		|Must| ensure that each entry in :wtrl_label:`Public_classes` resolves to a class with a valid docstring.
		|Should| list each class with a valid docstring in section :wtrl_label:`Public_classes`.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The class object to be validated.
	doc_class:
		Already parsed class docstring tree for :wtrl_var:`obj`.
Returns:
	|Must| return |None|.
Raises:
	TypeError:
		|Must| raise if :wtrl_var:`obj` is not a class object.
	RuntimeError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, obj.__name__):
		if not inspect.isclass(obj):
			raise TypeError("validate_class_class_coverage expects a class object.")
		if not isinstance(doc_class, docitem_docstring_class):
			raise TypeError("doc_class must be a docitem_docstring_class instance")
# Collect declared public classes from class docstring
		public_classes: set[str] = _get_public_section_entries(doc_class,"Public_classes",docitem_public_classes)
# Validate nested class docstrings (defined directly on the class)
		valid_classes: set[str] = set()
		classes_with_valid_docstring: set[str] = set()
		for name, member in obj.__dict__.items():
			if not isinstance(member, type):
				continue
			if getattr(member, "__module__", None) != getattr(obj, "__module__", None):
				continue
			doc = member.__doc__
			if not isinstance(doc, str):
				continue
# Determine validity for warning purposes
			try:
				tmp_tr = tracer()
				validate_docstring(tmp_tr, member)
				classes_with_valid_docstring.add(name)
			except Exception:
				pass
# Validate only if class is listed (PCL-023)
			if member.__name__ in public_classes:
# Push member name to tracer.
				with traced_section(tr, member.__name__):
					try:
# Validate and collect messages from lower levels
						validate_class_coverage(tr, member)
						valid_classes.add(name)
					except Exception:
# Add message from higher level for clarity.
						raise_validation_error(tr,obj,["PCL-020"],f"class '{name}' listed in Public_classes but has no valid docstring.")

# Validate entries listed in Public_classes
		with traced_section(tr, "Public_classes"):
# Rule: every class with a valid docstring should be listed
			missing_in_public = classes_with_valid_docstring - public_classes
			for name in missing_in_public:
				warn_validation(tr,obj,["PCL-021"],f"class '{name}' with docstring not listed in Public_classes: {sorted(missing_in_public)}")
			for name in public_classes:
				if not hasattr(obj, name):
					raise_validation_error(tr,obj,["PCL-018"],f"class '{name}' listed in Public_classes but does not exist.")
				cls_obj = getattr(obj, name)
				if not inspect.isclass(cls_obj):
					raise_validation_error(tr,obj,["PCL-019"],f"member '{name}' listed in Public_classes is not a class.")
				doc_c2 = cls_obj.__doc__
				if not isinstance(doc_c2, str):
					raise_validation_error(tr,obj,["PCL-020"],f"class '{name}' listed in Public_classes but has no valid docstring.")
				validate_class_coverage(tr,cls_obj)

def validate_class_method_coverage(tr : tracer,obj: type[object], doc_class: docitem_docstring_class) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze the docstrings of the class object passed.
		|Must| ensure that each method listed in the class' :wtrl_label:`Public_methods` section has a valid docstring.
		|Must| handle :wtrl_value:`@staticmethod` and :wtrl_value:`@classmethod` as well as inherited methods listed in :wtrl_label:`Public_methods`.
		|Should| list each method with a valid docstring in the class' :wtrl_label:`Public_methods` section.
		|Should| declare a section :wtrl_label:`Public_methods` when at least one method docstring exists.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The class object to be validated.
	doc_class:
		Already parsed class docstring tree for :wtrl_var:`obj`.
Returns:
	|Must| return |None|.
Raises:
	TypeError:
		|Must| raise if :wtrl_var:`obj` is not a class object.
	RuntimeError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, obj.__name__):
		if not inspect.isclass(obj):
			raise TypeError("validate_class_method_coverage expects a class object.")
		if not isinstance(doc_class, docitem_docstring_class):
			raise TypeError("doc_class must be a docitem_docstring_class instance")

# Collect declared public methods from class docstring
		public_methods: set[str] = _get_public_section_entries(doc_class,"Public_methods",docitem_public_methods)

# Collect methods defined on the class (not inherited) and validate their docstrings
		valid_methods: set[str] = set()
		methods_with_valid_docstring: set[str] = set()
		for name, member in obj.__dict__.items():
			func_obj: Callable[..., Any] | None = get_func_obj_from_callable(member)
			if func_obj is None:
				continue
# __doc__ is always there, but can be None.
			docm : str | None = func_obj.__doc__
			if not isinstance(docm,str):
				continue
# Determine validity for warning purposes
			try:
				tmp_tr = tracer()
				validate_docstring(tmp_tr, func_obj)
				methods_with_valid_docstring.add(name)
			except Exception:
				pass
# Validate only if method is listed (PMET-011)
			if member.__name__ in public_methods:
# Push member name to tracer.
				with traced_section(tr, func_obj.__name__):
					try:
# Validate and collect messages from lower levels
						validate_docstring(tr,func_obj, None, None)
						valid_methods.add(name)
					except Exception:
# Add message from higher level for clarity.
						raise_validation_error(tr,obj,["PMET-010"],f"class {obj.__name__}: method '{name}' listed in Public_methods but has no valid docstring.")

# Rule: if the class exposes methods with valid docstrings, it must declare Public_methods
		with traced_section(tr, "Public_methods"):
# Rule: every method with a valid docstring should be listed
			missing_in_public = methods_with_valid_docstring - public_methods
			for name in missing_in_public:
				warn_validation(tr,obj,["PMET-008"],f"class {obj.__name__}: method '{name}' with docstring not listed in Public_methods.")
# Rule: every method listed must have a valid docstring
			for name in public_methods:
				if name in valid_methods:
					continue
# method might be inherited; try to resolve and validate if present
				if not hasattr(obj, name):
					raise_validation_error(tr,obj,["PMET-009"],f"method '{name}' listed in Public_methods but does not exist.")
				meth_obj = getattr(obj, name)
				func_obj2: Callable[..., Any] | None = get_func_obj_from_callable(meth_obj)
				if func_obj2 is None:
					raise_validation_error(tr,obj,["PMET-009"],f"member '{name}' listed in Public_methods is not a function.")
				docm = func_obj2.__doc__
				if not isinstance(docm, str):
					raise_validation_error(tr,obj,["PMET-010"],f"method '{name}' listed in Public_methods but has no valid docstring.")
				validate_docstring(tr,func_obj2, None, None)
# All good
		return None

def validate_class_constant_coverage(tr : tracer,obj: type[object], doc_class: docitem_docstring_class) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze the docstrings of the class object passed.
		|Must| ensure that each constant listed in :wtrl_label:`Public_constants` exists.
		|Must| ensure that each constant listed in :wtrl_label:`Public_constants` is annotated as :wtrl_type:`Final` or not annotated at all.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The class object to be validated.
	doc_class:
		Already parsed class docstring tree for :wtrl_var:`obj`.
Returns:
	|Must| return |None|.
Raises:
	TypeError:
		|Must| raise if :wtrl_var:`obj` is not a class object.
	RuntimeError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, obj.__name__):
		if not inspect.isclass(obj):
			raise TypeError("validate_class_method_coverage expects a class object.")
		if not isinstance(doc_class, docitem_docstring_class):
			raise TypeError("doc_class must be a docitem_docstring_class instance")

# Collect declared public constants from class docstring
		public_constants: set[str] = set()
		if "Public_constants" in doc_class.items():
			pc_node = doc_class._items["Public_constants"]
			assert isinstance(pc_node, docitem_public_methods)
			public_constants = set(pc_node.items().keys())
# Make sure all constants are annotated as Final.
		for con in public_constants:
			if is_annotated(obj,con):
				if not is_final(obj,con):
					raise_validation_error(tr,obj,["PCON-022"],f"class {obj.__name__}: constant '{con}' listed in Public_constants but is not annotated as 'Final'.")
# All good
		return None

def validate_class_variable_coverage(tr : tracer,obj: type[object], doc_class: docitem_docstring_class) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze the docstrings of the class object passed.
		|Must| ensure that each variable listed in :wtrl_label:`Public_variables` exists.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The class object to be validated.
	doc_class:
		Already parsed class docstring tree for :wtrl_var:`obj`.
Returns:
	|Must| return |None|.
Raises:
	TypeError:
		|Must| raise if :wtrl_var:`obj` is not a class object.
	RuntimeError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, obj.__name__):
		if not inspect.isclass(obj):
			raise TypeError("validate_class_method_coverage expects a class object.")
		if not isinstance(doc_class, docitem_docstring_class):
			raise TypeError("doc_class must be a docitem_docstring_class instance")

# Collect declared public variables from class docstring
		public_variables: set[str] = set()
		if "Public_variables" in doc_class.items():
			pv_node = doc_class._items["Public_variables"]
			assert isinstance(pv_node, docitem_public_methods)
			public_variables = set(pv_node.items().keys())
# Rule: every variable listed must exist
		with traced_section(tr, "Public_variables"):
			for const_name in public_variables:
				if not hasattr(obj, const_name):
					raise_validation_error(tr,obj,["PVAR-021"],f"class {obj.__name__}: variable '{const_name}' listed in Public_variables but does not exist.")
# Make sure all variables are annotated as Final.
				if is_annotated(obj,const_name):
					if not is_final(obj,const_name):
						raise_validation_error(tr,obj,["PVAR-022"],f"class {obj.__name__}: variable '{const_name}' listed in Public_variables but is not annotated as 'Final'.")
# All good
		return None

def validate_module_class_coverage(tr : tracer,obj: ModuleType, doc_module: docitem_docstring_module) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze the docstrings of the module object passed.
		|Must| ensure that each class with a valid docstring is listed in the class' :wtrl_label:`Public_classes` section.
		|Must| ensure that each class listed in the module's :wtrl_label:`Public_classes` section has a valid docstring.
		|Should| declare a section :wtrl_label:`Public_classes` when at least one class docstring exists.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The module object to be validated.
	doc_module:
		Already parsed module docstring tree for :wtrl_var:`obj`.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, obj.__name__):
		if not inspect.ismodule(obj):
			raise TypeError("validate_module_class_coverage expects a module object.")
		if not isinstance(doc_module, docitem_docstring_module):
			raise TypeError("doc_module must be a docitem_docstring_module instance")
# Collect declared public classes from module docstring
		public_classes: set[str] = _get_public_section_entries(doc_module,"Public_classes",docitem_public_classes)
# Collect classes defined in the module (not imported) and validate their docstrings
		valid_classes: set[str] = set()
		classes_with_valid_docstring: set[str] = set()
		for name, member in obj.__dict__.items():
			if not isinstance(member, type):
				continue
			if getattr(member,"__module__",None) != obj.__name__:
				continue
			doc = member.__doc__
			if not isinstance(doc,str):
				continue
# Determine validity for warning purposes
			try:
				tmp_tr = tracer()
				validate_docstring(tmp_tr,member)
				classes_with_valid_docstring.add(name)
			except Exception:
				pass
# Validate only if class is listed PCL-022)
			if member.__name__ in public_classes:
# Push member name to tracer.
				with traced_section(tr, member.__name__):
					try:
# Validate and collect messages from lower levels
						validate_class_coverage(tr,member)
						valid_classes.add(name)
					except Exception:
# Add message from higher level for clarity.
						raise_validation_error(tr,obj,["PCL-017"],f"class '{name}' listed in Public_classes but has no valid docstring.")

# Rule: classes with docstrings should be listed in Public_classes
		with traced_section(tr, "Public_classes"):
# Rule: every class with a valid docstring should be listed
			missing_in_public = classes_with_valid_docstring - public_classes
			for name in missing_in_public:
				warn_validation(tr,obj,["PCL-014"],f"class with docstring '{name}' not listed in Public_classes.")

# Validate entries listed in Public_classes
		with traced_section(tr, "Public_classes"):
# Rule: every class listed in Public_classes must have a valid docstring
			for name in public_classes:
				if not hasattr(obj, name):
					raise_validation_error(tr,obj,["PCL-015"],f"class '{name}' listed in Public_classes but does not exist.")
				cls_obj = getattr(obj, name)
				if not inspect.isclass(cls_obj):
					raise_validation_error(tr,obj,["PCL-016"],f"member '{name}' listed in Public_classes is not a class.")
				doc_c2 = cls_obj.__doc__
				if not isinstance(doc_c2, str):
					raise_validation_error(tr,obj,["PCL-017"],f"class '{name}' listed in Public_classes but has no valid docstring.")
# Important: Coverage means to descend recursively.
				validate_class_coverage(tr,cls_obj)
# All good
		return None

def validate_module_function_coverage(tr : tracer,obj: ModuleType, doc_module: docitem_docstring_module) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze the docstrings of the module object passed.
		|Must| ensure that each function with a valid docstring is listed in the module's :wtrl_label:`Public_functions` section.
		|Must| ensure that each function listed in the module's :wtrl_label:`Public_functions` section has a valid docstring.
		|Should| declare a section :wtrl_label:`Public_functions` when at least one function docstring exists.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The module object to be validated.
	doc_module:
		Already parsed module docstring tree for :wtrl_var:`obj`.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, obj.__name__):
		if not inspect.ismodule(obj):
			raise TypeError("validate_module_function_coverage expects a module object.")
		if not isinstance(doc_module, docitem_docstring_module):
			raise TypeError("doc_module must be a docitem_docstring_module instance")

# Collect declared public functions from module docstring
		public_functions: set[str] = _get_public_section_entries(doc_module,"Public_functions",docitem_public_functions)

# Collect functions defined in the module (not imported) and validate their docstrings
		valid_functions: set[str] = set()
		functions_with_valid_docstring: set[str] = set()
		for name, member in obj.__dict__.items():
			if not isinstance(member, FunctionType):
				continue
			if getattr(member,"__module__",None) != obj.__name__:
				continue
# __doc__ is always there, but can be None.
			docf = member.__doc__
			if not isinstance(docf,str):
				continue
# Determine validity for warning purposes
			try:
				tmp_tr = tracer()
				validate_docstring(tmp_tr,member)
				functions_with_valid_docstring.add(name)
			except Exception:
				pass
# Validate only if function is listed (PFN-011)
			if name in public_functions:
# Push member name to tracer.
				with traced_section(tr, member.__name__):
					try:
# Validate and collect messages from lower levels
						validate_docstring(tr,member, None, None)
						valid_functions.add(name)
					except:
# Add message from higher level for clarity.
						raise_validation_error(tr,obj,["PFN-010"],f"function '{name}' listed in Public_functions but has no valid docstring.")

		with traced_section(tr, "Public_functions"):
# Rule: every function with a valid docstring should be listed
			missing_in_public = functions_with_valid_docstring - public_functions
			for name in missing_in_public:
				warn_validation(tr,obj,["PFN-008"],f"module {obj.__name__}: function '{name}' with docstring not listed in Public_functions.")
# Rule: every function listed must have a valid docstring
			for name in public_functions:
				if name in valid_functions:
					continue
				if not hasattr(obj, name):
					raise_validation_error(tr,obj,["PFN-009"],f"function '{name}' listed in Public_functions but does not exist.")
				func_obj = getattr(obj, name)
				if not inspect.isfunction(func_obj):
					raise_validation_error(tr,obj,["PFN-010"],f"member '{name}' listed in Public_functions is not a function.")
				doc_f2 = func_obj.__doc__
				if not isinstance(doc_f2, str):
					raise_validation_error(tr,obj,["PFN-010"],f"function '{name}' listed in Public_functions but has no docstring.")
				validate_docstring(tr,func_obj, None, None)
# All good
		return None

def validate_module_type_coverage(tr : tracer,obj: ModuleType, doc_module: docitem_docstring_module) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze the docstrings of the module object passed.
		|Must| ensure that each type listed in the module's :wtrl_label:`Public_types` section exists in the module.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The module object to be validated.
	doc_module:
		Already parsed module docstring tree for :wtrl_var:`obj`.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, obj.__name__):
		if not isinstance(doc_module, docitem_docstring_module):
			raise TypeError("doc_module must be a docitem_docstring_module instance")
# Collect declared public types from module docstring
		public_types: set[str] = _get_public_section_entries(doc_module,"Public_types",docitem_public_types)
# Rule: every type listed must exist
		with traced_section(tr, "Public_types"):
			for type_name in public_types:
				if not hasattr(obj, type_name):
					raise_validation_error(tr,obj,["PTY-007"],f"module {obj.__name__}: type '{type_name}' listed in Public_types but does not exist.")
# All good
	return None

def validate_module_constant_coverage(tr : tracer,obj: ModuleType, doc_module: docitem_docstring_module) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze the docstrings of the module object passed.
		|Must| ensure that each constant listed in the module's :wtrl_label:`Public_constants` section exists in the module.
		|Must| ensure that each constant listed in the module's :wtrl_label:`Public_constants` is either annotated as :wtrl_type:`Final` or not annotated at all.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The module object to be validated.
	doc_module:
		Already parsed module docstring tree for :wtrl_var:`obj`.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, obj.__name__):
		if not isinstance(doc_module, docitem_docstring_module):
			raise TypeError("doc_module must be a docitem_docstring_module instance")
# Collect declared public constants from module docstring
		public_constants: set[str] = _get_public_section_entries(doc_module,"Public_constants",docitem_public_constants)
# Rule: every constant listed must exist
		with traced_section(tr, "Public_constants"):
			for const_name in public_constants:
				if not hasattr(obj, const_name):
					raise_validation_error(tr,obj,["PCON-015"],f"module {obj.__name__}: constant '{const_name}' listed in Public_constants but does not exist.")
# Make sure all constants are annotated as Final.
				if is_annotated(obj,const_name):
					if not is_final(obj,const_name):
						raise_validation_error(tr,obj,["PCON-016"],f"module {obj.__name__}: constant '{const_name}' listed in Public_constants but is not annotated as 'Final'.")
# All good
	return None

def validate_module_variable_coverage(tr : tracer,obj: ModuleType, doc_module: docitem_docstring_module) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze the docstrings of the module object passed.
		|Must| ensure that each variable listed in the module's :wtrl_label:`Public_variables` section exists in the module.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The module object to be validated.
	doc_module:
		Already parsed module docstring tree for :wtrl_var:`obj`.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, obj.__name__):
		if not isinstance(doc_module, docitem_docstring_module):
			raise TypeError("doc_module must be a docitem_docstring_module instance")
# Collect declared public variables from module docstring
		public_variables: set[str] = _get_public_section_entries(doc_module,"Public_variables",docitem_public_variables)
# Rule: every variable listed must exist
		with traced_section(tr, "Public_variables"):
			for const_name in public_variables:
				if not hasattr(obj, const_name):
					raise_validation_error(tr,obj,["PVAR-013"],f"module {obj.__name__}: variable '{const_name}' listed in Public_variables but does not exist.")
# Make sure all variables are annotated as Final.
				if is_annotated(obj,const_name):
					if not is_final(obj,const_name):
						raise_validation_error(tr,obj,["PVAR-014"],f"module {obj.__name__}: variable '{const_name}' listed in Public_variables but is not annotated as 'Final'.")
# All good
	return None

#===== Coverage Frontend ======================================#

def validate_class_coverage(tr : tracer,obj: type[object]) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| validate for method coverage by calling the specific validator.
		|Must| validate for class coverage by calling the specific validator.
		|Must| validate for constant coverage by calling the specific validator.
		|Must| validate for variable coverage by calling the specific validator.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The class object to be validated.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| propagate exceptions from subordinate coverage validators.
Notes:
	todo:
		Missing: class-type-coverage.
	"""
	with traced_section(tr, obj.__name__):
		if not inspect.isclass(obj):
			raise TypeError(f"{obj.__class__.__name__} is not a class object")
		top = validate_docstring(tr,obj)
		assert isinstance(top, docitem_docstring_class)
		validate_class_class_coverage(tr,obj, top)
		validate_class_method_coverage(tr,obj, top)
		validate_class_constant_coverage(tr,obj, top)
		validate_class_variable_coverage(tr,obj, top)

def validate_module_coverage(tr : tracer,obj: ModuleType) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| validate for class, function, type, constant, and variable coverage by calling the specific coverage validators.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The module object to be validated.
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, obj.__name__):
		if not inspect.ismodule(obj):
			raise TypeError(f"{obj.__class__.__name__} is not a module object")
		top = validate_docstring(tr,obj)
		assert isinstance(top, docitem_docstring_module)
		validate_module_class_coverage(tr,obj, top)
		validate_module_function_coverage(tr,obj, top)
		validate_module_type_coverage(tr,obj, top)
		validate_module_constant_coverage(tr,obj, top)
		validate_module_variable_coverage(tr,obj, top)

def gen_documentable_objects(obj: ModuleType | type[object] | Callable[..., Any]) -> Generator[ModuleType | type[object] | Callable[..., Any],None,None]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| create a generator object which allows depth-first tree traversal of objects in :wtrl_var:`obj`.
		|Must| first yield object :wtrl_var:`obj` itself.
		|Must| yield all objects and only objects which can have a docstring.
Parameters:
	obj:
		The object (module, class, function, method) to examine.
Returns:
	|Must| return a Generator which yields objecta from tree traversal of :wtrl_var:`obj`
Raises:
	"""
	def _iter(o: ModuleType | type[object] | Callable[..., Any]) -> Generator[ModuleType | type[object] | Callable[..., Any],None,None]:
		yield o
		if isinstance(o, ModuleType):
# We're in a module. There might be classes and functions:
			for name, member in o.__dict__.items():
# It is not sufficient to distinguish the member by type,
# we also need to make sure, the object is from module o,
# and not imported, so we check if the objects module coincides with o's name.
# Otherwise recursion would dive arbitrarily deep into the imported hierarchy.
				if isinstance(member, type) and getattr(member, "__module__", None) == o.__name__:
# class
					yield from _iter(member)
				elif isinstance(member, FunctionType) and getattr(member, "__module__", None) == o.__name__:
# functions
					yield from _iter(member)
				else:
# Other objects
					continue
		elif isinstance(o, type):
# We're in a class. There might be classes, static functions, class methods and "normal" methods:
			for name, member in o.__dict__.items():
				func_obj: Callable[..., Any] | None = None
				if isinstance(member,type):
# class
					yield from _iter(member)
				else:
# callables
					func_obj = get_func_obj_from_callable(member)
					if func_obj is None:
						continue
					yield from _iter(func_obj)
		elif callable(o):
# Functions/methods are leaves for our traversal
			return
	yield from _iter(obj)
		
if __name__ == "__main__":
	tr = tracer()
	validate_module_coverage(tr,sys.modules[__name__])
	if tr.has_warnings():
		print("### WARNINGS! ###")
		print(tr.to_string_warnings())
