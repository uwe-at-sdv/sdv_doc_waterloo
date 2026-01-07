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
		|Must| provide node classes and parsing/validation utilities for Waterloo docstrings.
	api:
		Public_functions
		Public_classes
		Public_types
		Public_constants
Public_functions:
	parse_indent_docstring:
		The fundamental parsing function which creates docstring trees from Waterloo docstrings.
	validate_docstring_method:
		Validator for method and function docstrings
	validate_docstring_module:
		Validator for module docstrings
	validate_class_method_coverage:
		Validate mutual coverage of methods and class docstring entries.
	validate_class_coverage:
		Verify existence (and mutual coverage were applicable) of methods mentioned in the class docstring.
	validate_module_class_coverage:
		Validate mutual coverage of classes and module docstring entries.
	validate_module_function_coverage:
		Validate mutual coverage of functions and module docstring entries.
	validate_module_type_coverage:
		Verify existence of types mentioned in the module docstring.
	validate_module_constant_coverage:
		Verify existence of constants mentioned in the module docstring.
	validate_module_coverage:
		Verify existence (and mutual coverage were applicable) of classes, functions, types, constants mentioned in the module docstring.
	gen_docstrings:
		Generate profile-object-docstring triples for a tree of python objects.
Public_classes:
	docitem_base:
		The base class for all docitem classes which form the docstring tree.
	docitem_list_base:
		The base class for docitem classes managing a list of strings.
	docitem_map_base:
		The base class for docitem classes managing a map from strings to docitem nodes
	docitem_profile:
		Node class for section profile
	docitem_normative_sections:
		Node class for section normative_sections
	docitem_preamble:
		Node class for section Preamble
Public_types:
	docstring_tree:
		The type alias for docstring trees.
Public_constants:
"""

# Todo: think about Contract.import_side_fx

import sys,re
import inspect
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Generator, Iterable, Iterator, List, Tuple, Type, TypeAlias, TypeGuard, Union

docstring_tree: TypeAlias = List[Union[str , "docstring_tree"]]
docstring_subtree: TypeAlias = Union[str, List["docstring_subtree"]]

_re_ident = r"[A-Za-z_][A-Za-z0-9_]*"
_re_ident_compiled = re.compile(_re_ident)

_re_qualified_identifier = r"[A-Za-z_.][A-Za-z0-9_.]*"
_re_qualified_identifier_compiled = re.compile(_re_qualified_identifier)

_re_label = _re_qualified_identifier + ":"
_re_label_compiled = re.compile(_re_label)

#===== Typechecking ===========================================#

def is_list_of_str(val: Any) -> TypeGuard[List[str]]:
	if not isinstance(val,list):
		return False
	for item in val:
		if not isinstance(item,str):
			return False
	return True

#===== Exceptions =============================================#

def _obj_name(obj: object) -> str:
	if isinstance(obj, str):
		return obj
	if hasattr(obj, "__name__"):
		name_attr = getattr(obj, "__name__")
		return name_attr if isinstance(name_attr, str) else str(name_attr)
	return str(obj)

def raise_parsing_error(msg : str) -> None:
	raise RuntimeError(msg)

def raise_parsing_error_invalid_label(found : str,allowed : Iterable[str]) -> None:
	details : str = ""
	if found[-1] != ":":
		details = " (the colon seems to be missing)"
	raise RuntimeError(f"'{found}' is not a valid label, allowed: {{{', '.join(allowed)}}}{details}")

def raise_parsing_error_preamble_not_first(label : str) -> None:
	raise RuntimeError(f"'Preamble' must be the first section in the docstring, but found '{label}'.")

def raise_validation_error(obj: object, section : str, msg : str) -> None:
	name = _obj_name(obj)
	raise RuntimeError(f"In object '{name}', in section {section}: {msg}")

#===== Keywords ===============================================#
keywords_of_normativity = [
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
	]

#===== Tokenizer ==============================================#

def get_num_indent(line : str) -> int:
	line_tab : str = line.replace("    ","\t")
	n : int = 0
	for c in line_tab:
		if c == "\t":
			n += 1
		elif c == " ":
			raise_parsing_error("Inconsistent indent in docstring.")
		else:
			break
	return n

def parse_indent_docstring(text : str) -> docstring_tree:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Definitions:
	docstring tree:
		A docstring tree is a :cdml_type:`list` of either :cdml_type:`str` or docstring tree.
		[Informative note: an empty :cdml_type:`list` fulfills this definition.]
Contract:
	general:
		|Must| generate a docstring tree from a docstring. In order to achieve this:
		|Must| iterate over the docstring's lines and skip empty lines.
		|Must| return an empty list (= empty docstring tree) on empty input.
Parameters:
	text:
		A docstring in Waterloo format.
Returns:
	|Must| return a docstring tree, which is a 1:1 representation of the indented text by means of nested lists.
Raises:
	RuntimeError:
		|Must| raise if indentation grows by more than 1 unit from one line to the next.
		|Must| raise if inconsistent indentation is detected.
	"""
	tree : docstring_tree = []
	state : List[docstring_tree] = [tree]
	cur_pos = 0
	lines = text.split("\n")
	for line in lines:
		if line.strip() == "":
			continue
		num_indent = get_num_indent(line)
		if num_indent > cur_pos + 1:
			raise_parsing_error(f"indent jump > 1, not allowed, cur_pos: {cur_pos}, num_indent: {num_indent}, line '{line}'")
		elif num_indent > cur_pos:
			subtree : docstring_tree = []
			state[cur_pos].append(subtree)
			state.append(subtree)
			cur_pos += 1
		else:
			while cur_pos > num_indent:
				del state[cur_pos]
				cur_pos -= 1
		state[cur_pos].append(line.lstrip())
	return tree

#===== Docitem node classes ===================================#

# Helper to reduce boiler plate.
def expect_list(subtree : docstring_subtree,pos : int) -> Tuple[docstring_subtree,int]:
	if pos >= len(subtree):
		return [],pos
	if not isinstance(subtree[pos],list):
		return [],pos
	items = subtree[pos]
	pos += 1
	return items,pos

def expect_label(subtree : docstring_subtree,pos : int) -> Tuple[str,int]:
	if pos >= len(subtree):
		raise_parsing_error("missing block after label")
	if not isinstance(subtree[pos], str):
		raise_parsing_error(f"expected str, got {subtree[pos]}")
	s = subtree[pos][:-1]
	pos += 1
	assert isinstance(s,str)
	return s,pos

class docitem_base:
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
		Derived_from
		Public_methods
Definitions:
	child item:
		A string or an instance of a docitem class.
Contract:
	general:
		|Must| provide an abstract method for parsing a docstring tree.
		|Must| provide an abstract method for accessing child items.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
Public_methods:
	parse:
		|Must| parse a docstring subtree and create child nodes accordingly.
	items:
		|Must| return an iterable over the child items.
	"""
	def parse(self,subtree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| parse a docstring subtree and create the related child items.
		|Must| raise NotImplementedError if not implemented in the derived class.
Parameters:
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
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must_not| mutate the instance (pure getter)
Parameters:
Returns:
	|Must| return an iterable over the child items.
Raises:
		"""
		raise NotImplementedError
	def has_norm_keywords(self) -> bool:
		raise NotImplementedError

class docitem_list_base(docitem_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
		Derived_from
		Public_methods
Contract:
	general:
		|Must| contain a container of :cdml_type:`str` and expose it as an iterable object.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
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
		Contract
		Parameters
		Returns
		Raises
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
	def has_norm_keywords(self) -> bool:
		for w in keywords_of_normativity:
			for item in self.items():
				if w in item:
					return True
		return False

class docitem_map_base(docitem_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
		Derived_from
		Public_methods
Contract:
	general:
		|Must| contain a map-like container from :cdml_type:`str` to :cdml_type:`docitem_base` and expose it as an iterable object.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_base
Public_methods:
	items:
		|Must_not| mutate the instance (pure getter)
	"""
	def __init__(self) -> None:
		self._items : Dict[str,docitem_base] = {}
	def items(self) -> Dict[str,docitem_base]:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must_not| mutate the instance (pure getter)
Parameters:
Returns:
	|Must| return an iterable over the child items.
Raises:
		"""
		return self._items
	def has_norm_keywords(self) -> bool:
		for label,item in self.items().items():
			if item.has_norm_keywords():
				return True
		return False

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
		Contract
		Derived_from
		Public_methods
Contract:
	general:
		|Must| represent the :cdml_label:`profile` section, subsection of :cdml_label:`Preamble`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_list_base
Public_methods:
	parse:
		|Must| be able to parse a :cdml_label:`profile` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "profile"
	def parse(self,refs : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| parse the content of a :cdml_label:`profile` section.
Parameters:
	refs:
		The docstring subtree to parse.
Returns:
	|None|
Raises:
	RuntimeError:
		|Must| raise if the number of item is not :cdml_value:`1`.
		|Must| raise if the item is not a string (no subtrees allowed).
		|Must| raise if the item is not an identifier.
		"""
# Validate
# Only exactly one item is allowed
		if len(refs) != 1:
			raise_parsing_error(f"expected exactly one item, got {refs}")
		for ref in refs:
# Only string are allowed (not list of something)
			if not isinstance(ref,str):
				raise_parsing_error(f"expected str, 'got {ref}'")
# Only identifiers are allowed.
			assert isinstance(ref,str)
			if not _re_ident_compiled.fullmatch(ref):
				raise_parsing_error(f"entry must be an identifier, got '{ref}'")
		assert is_list_of_str(refs)
		self.set_items(refs)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem class normative_sections -----------------------#

class docitem_normative_sections(docitem_list_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
		Derived_from
		Public_methods
Contract:
	general:
		|Must| represent the :cdml_label:`normative_sections` section, subsection of :cdml_label:`Preamble`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_list_base
Public_methods:
	parse:
		|Must| be able to parse a :cdml_label:`normative_sections` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Normative sections"
	def parse(self,refs : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| parse the content of a :cdml_label:`normative_sections` section.
Parameters:
	refs:
		The docstring subtree to parse.
Returns:
	|None|
Raises:
	RuntimeError:
		|Must| raise if the items are not strings (no subtrees allowed).
		|Must| raise if the items are not identifiers.
		"""
# Validate
		for ref in refs:
# Only string are allowed (not list of something)
			if not isinstance(ref,str):
				raise_parsing_error(f"expected str, 'got {ref}'")
# Only identifiers are allowed.
			assert isinstance(ref,str)
			if not _re_ident_compiled.fullmatch(ref):
				raise_parsing_error(f"entry must be an identifier, got '{ref}'")
		assert is_list_of_str(refs)
		self.set_items(refs)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem class preamble ---------------------------------#

class docitem_preamble(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract
		Derived_from
		Public_methods
Contract:
	general:
		|Must| represent the :cdml_label:`Preamble` section.
		|Must| be able to hold a map from :cdml_type:`str` to :cdml_type:`docitem_base`.
	constructor:
		|Must| be default-constructible.
	api:
		Public_methods
Derived_from:
	docitem_map_base
Public_methods:
	parse:
		|Must| be able to parse a :cdml_label:`Preamble` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Preamble"
	def parse(self,subtree : docstring_subtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| parse the subsections of a :cdml_label:`Preamble` section.
Parameters:
	subtree:
		The docstring subtree to parse.
Returns:
	|None|
Raises:
	RuntimeError:
		|Must| raise if a subsection is not one of the allowed ones: {profile,normative_sections}.
		"""
		pos = 0
		dispatch_map = {
			"profile:":docitem_profile,
			"normative_sections:":docitem_normative_sections,
			}
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dispatch_map:
				label,pos = expect_label(subtree,pos)
# Contract requires a list
				items,pos = expect_list(subtree,pos)
				self._items[label] = dispatch_map[lb]()
				self._items[label].parse(items)
			else:
				raise_parsing_error_invalid_label(lb,dispatch_map)
	def __str__(self) -> str:
		return " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"
#===== end section Preamble ===================================#

#===== begin section Contract =================================#

#----- docitem class constructor ------------------------------#

class docitem_constructor(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Constructor"
	def parse(self,subtree : docstring_subtree) -> None:
		pos = 0
		while pos < len(subtree):
# constructor requires a list of strings
			if not isinstance(subtree[pos],str):
				raise_parsing_error(f"expected str, got {subtree[pos]}")
			entry = subtree[pos]
			pos += 1
			assert isinstance(entry,str)
			self._items.append(entry)
	def __str__(self) -> str:
		return " {" + ", ".join([entry for entry in self._items]) + "}"

#----- docitem class general ----------------------------------#

class docitem_general(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "General"
	def parse(self,subtree : docstring_subtree) -> None:
		pos = 0
		while pos < len(subtree):
# general requires a list of strings
			if not isinstance(subtree[pos],str):
				raise_parsing_error(f"expected str, got {subtree[pos]}")
			entry = subtree[pos]
			pos += 1
			assert isinstance(entry,str)
			self._items.append(entry)
	def __str__(self) -> str:
		return " {" + ", ".join([entry for entry in self._items]) + "}"

#----- docitem class api --------------------------------------#

class docitem_api(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Api"
	def parse(self,refs : docstring_subtree) -> None:
# api requires a list of strings
		if not is_list_of_str(refs):
			raise_parsing_error(f"expected list, got {refs}")
# Validate
		for ref in refs:
# Only string are allowed (not list of something)
			if not isinstance(ref,str):
				raise_parsing_error(f"expected str, 'got {ref}'")
# Only identifiers are allowed.
			assert isinstance(ref,str)
			if not _re_ident_compiled.fullmatch(ref):
				raise_parsing_error(f"api entry must be an identifier, got '{ref}'")
		assert is_list_of_str(refs)
		self.set_items(refs)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem classes contract -------------------------------#

class docitem_contract_module(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Contract"
	def parse(self,subtree : docstring_subtree) -> None:
		pos = 0
		dispatch_map = {
			"general:":docitem_general,
			"api:":docitem_api,
			}
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dispatch_map:
				label,pos = expect_label(subtree,pos)
# Contract requires a list
				items,pos = expect_list(subtree,pos)
				self._items[label] = dispatch_map[lb]()
				self._items[label].parse(items)
			else:
				raise_parsing_error_invalid_label(lb,dispatch_map)
	def __str__(self) -> str:
		return self.label() + " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"

class docitem_contract_class(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Contract"
	def parse(self,subtree : docstring_subtree) -> None:
		pos = 0
		dispatch_map = {
			"general:":docitem_general,
			"constructor:":docitem_constructor,
			"api:":docitem_api,
			}
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dispatch_map:
				label,pos = expect_label(subtree,pos)
# Contract requires a list
				items,pos = expect_list(subtree,pos)
				self._items[label] = dispatch_map[lb]()
				self._items[label].parse(items)
			else:
				raise_parsing_error_invalid_label(lb,dispatch_map)
	def __str__(self) -> str:
		return self.label() + " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"

class docitem_contract_method(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Contract"
	def parse(self,subtree : docstring_subtree) -> None:
		pos = 0
		dispatch_map = {
			"general:":docitem_general,
			}
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dispatch_map:
				label,pos = expect_label(subtree,pos)
# Contract requires a list
				items,pos = expect_list(subtree,pos)
				self._items[label] = dispatch_map[lb]()
				self._items[label].parse(items)
			else:
				raise_parsing_error_invalid_label(lb,dispatch_map)
	def __str__(self) -> str:
		return self.label() + " {" + ", ".join([key + str(value) for key,value in self._items.items()]) + "}"

#===== end section Contract ===================================#

#===== begin section Derived_from =============================#

#----- docitem class derived_from -----------------------------#

class docitem_derived_from(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Derived from"
	def parse(self,bases : docstring_subtree) -> None:
# normative_sections requires a single item which is a string
		if not isinstance(bases,list):
			raise_parsing_error(f"expected str, got {bases}")
		assert is_list_of_str(bases)
		self.set_items(bases)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Derived_from ===============================#

#===== begin section Factory ==================================#

#----- docitem class factory ----------------------------------#

class docitem_factory_functions(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "factory_functions"
	def parse(self,factory_functions : docstring_subtree) -> None:
# Validate- Only qualified identifiers are allowed
		assert is_list_of_str(factory_functions)
		self.set_items(factory_functions)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

class docitem_factory(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Factory"
	def parse(self,functions : docstring_subtree) -> None:
		pos = 0
		while pos < len(functions):
# proxy: matches name regex
			if True:
				label,pos = expect_label(functions,pos)
# factory requires a list of factory function names
				items,pos = expect_list(functions,pos)
				self._items[label] = docitem_factory_functions()
				self._items[label].parse(items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Factory ====================================#

#===== begin section Public_classes ===========================#

#----- docitem class public_classes ---------------------------#

# An entry for a function in section Public classes is only a brief
# description that the class is good for. Classes must be explained
# in details outside the module documentation block.
class docitem_public_classes_entries(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "public_classes_entries"
	def parse(self,public_classes_entries : docstring_subtree) -> None:
		assert is_list_of_str(public_classes_entries)
		self.set_items(public_classes_entries)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

class docitem_public_classes(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Public classes"
	def parse(self,functions : docstring_subtree) -> None:
		pos = 0
		while pos < len(functions):
# proxy: matches name regex
			if True:
				label,pos = expect_label(functions,pos)
# public_classes requires a list of public_classes function names
				items,pos = expect_list(functions,pos)
				self._items[label] = docitem_public_classes_entries()
				self._items[label].parse(items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem class public_types ----------------------------#

# An entry for a function in section Public types is only a brief
# description that the class is good for. types must be explained
# in details outside the module documentation block.
class docitem_public_types_entries(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "public_types_entries"
	def parse(self,public_types_entries : docstring_subtree) -> None:
		assert is_list_of_str(public_types_entries)
		self.set_items(public_types_entries)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

class docitem_public_types(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Public types"
	def parse(self,functions : docstring_subtree) -> None:
		pos = 0
		while pos < len(functions):
# proxy: matches name regex
			if True:
				label,pos = expect_label(functions,pos)
# public_types requires a list of public_types function names
				items,pos = expect_list(functions,pos)
				self._items[label] = docitem_public_types_entries()
				self._items[label].parse(items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem class public_constants ----------------------------#

# An entry for a function in section Public constants is only a brief
# description that the class is good for. constants must be explained
# in details outside the module documentation block.
class docitem_public_constants_entries(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "public_constants_entries"
	def parse(self,public_constants_entries : docstring_subtree) -> None:
		assert is_list_of_str(public_constants_entries)
		self.set_items(public_constants_entries)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

class docitem_public_constants(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Public constants"
	def parse(self,functions : docstring_subtree) -> None:
		pos = 0
		while pos < len(functions):
# proxy: matches name regex
			if True:
				label,pos = expect_label(functions,pos)
# public_constants requires a list of public_constants function names
				items,pos = expect_list(functions,pos)
				self._items[label] = docitem_public_constants_entries()
				self._items[label].parse(items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Public_classes =============================#

#===== begin section Public_<callable> ========================#

#----- docitem class public_methods ---------------------------#

# An entry for a function in section Public methods is only a brief
# description what the function is good for. Functions must be explained
# in details outside the class documentation block.
class docitem_public_methods_entries(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "public_methods_entries"
	def parse(self,public_methods_entries : docstring_subtree) -> None:
		assert is_list_of_str(public_methods_entries)
		self.set_items(public_methods_entries)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

class docitem_public_methods(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Public methods"
	def parse(self,functions : docstring_subtree) -> None:
		pos = 0
		while pos < len(functions):
# proxy: matches name regex
			if True:
				label,pos = expect_label(functions,pos)
# public_methods requires a list of public_methods function names
				items,pos = expect_list(functions,pos)
				self._items[label] = docitem_public_methods_entries()
				self._items[label].parse(items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#----- docitem class public_functions ---------------------------#

class docitem_public_functions_entries(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "public_functions_entries"
	def parse(self,public_functions_entries : docstring_subtree) -> None:
		assert is_list_of_str(public_functions_entries)
		self.set_items(public_functions_entries)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

class docitem_public_functions(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Public functions"
	def parse(self,functions : docstring_subtree) -> None:
		pos = 0
		while pos < len(functions):
# proxy: matches name regex
			if True:
				label,pos = expect_label(functions,pos)
# public_functions requires a list of public_functions function names
				items,pos = expect_list(functions,pos)
				self._items[label] = docitem_public_functions_entries()
				self._items[label].parse(items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Public_<callable> ==========================#

#===== begin section Returns ==================================#

#----- docitem class returns ----------------------------------#

class docitem_returns(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Returns"
	def parse(self,items : docstring_subtree) -> None:
		assert is_list_of_str(items)
		self.set_items(items)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

#===== end section Returns ====================================#

#===== begin section Description ==============================#

#----- docitem class Description ------------------------------#

# A dscription may contain several lines. The standard rendering
# will be to concatenate them to one paragraph, the lines are
# an editing and parsing artefact.
class docitem_description(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Description"
	def parse(self,lines : docstring_subtree) -> None:
		assert is_list_of_str(lines)
		self._items = lines
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

#===== end section Description ================================#

#===== begin section Parameters ===============================#

#----- docitem class Parameters -------------------------------#

class docitem_par(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "parameter"
	def parse(self,lines : docstring_subtree) -> None:
# Validate - Only strings are allowed
		assert is_list_of_str(lines)
		self.set_items(lines)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

class docitem_parameters(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Parameters"
	def parse(self,functions : docstring_subtree) -> None:
		pos = 0
		while pos < len(functions):
# proxy: matches name regex
			if True:
				label,pos = expect_label(functions,pos)
# factory requires a list of factory function names
				items,pos = expect_list(functions,pos)
				self._items[label] = docitem_par()
				self._items[label].parse(items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Parameters =================================#

#===== begin section Raises ===================================#

#----- docitem class Raises -----------------------------------#

class docitem_exc(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "exception"
	def parse(self,parameter : docstring_subtree) -> None:
# Validate- Only qualified identifiers are allowed
		assert is_list_of_str(parameter)
		self.set_items(parameter)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

class docitem_raises(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Raises"
	def parse(self,functions : docstring_subtree) -> None:
		pos = 0
		while pos < len(functions):
# proxy: matches name regex
			if True:
# label is e.g. "RuntimeError", "RangeError",...
				label,pos = expect_label(functions,pos)
# factory requires a list of factory function names
				items,pos = expect_list(functions,pos)
				self._items[label] = docitem_exc()
				self._items[label].parse(items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Raises =====================================#

#===== begin section Usage ====================================#

#----- docitem class Usage ------------------------------------#

class docitem_usage(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Usage"
	def parse(self,lines : docstring_subtree) -> None:
# Validate
		for line in lines:
# Only string are allowed (not list of something)
			if not isinstance(line,str):
				raise_parsing_error(f"expected str, 'got {line}'")
		assert is_list_of_str(lines)
		self.set_items(lines)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Usage ======================================#

#===== begin section Definitions ==============================#

#----- docitem class Definitions ------------------------------#

class docitem_dfn(docitem_list_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "dfn"
	def parse(self,dfn : docstring_subtree) -> None:
# Validate- Only qualified identifiers are allowed
		assert is_list_of_str(dfn)
		self.set_items(dfn)
	def __str__(self) -> str:
		return " {'" + "','".join(self._items) + "'}"

class docitem_definitions(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Definitions"
	def parse(self,functions : docstring_subtree) -> None:
		pos = 0
		while pos < len(functions):
# proxy: matches name regex
			if True:
				label,pos = expect_label(functions,pos)
# factory requires a list of factory function names
				items,pos = expect_list(functions,pos)
				self._items[label] = docitem_dfn()
				self._items[label].parse(items)
	def __str__(self) -> str:
		return " {" + ",".join(self._items) + "}"

#===== end section Definitions ================================#

#===== begin Top ==============================================#

#----- docitem class docstring_class --------------------------#

class docitem_docstring_base(docitem_map_base):
	def __init__(self) -> None:
		super().__init__()
	def dispatch_map(self) -> Dict[str, Type[docitem_base]]:
		raise NotImplementedError
	def label(self) -> str:
		return "docstring"
	def parse(self,subtree : docstring_subtree) -> None:
		found_preamble = False
		pos = 0
		dmap = self.dispatch_map()
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dmap:
				if lb == "Preamble:":
					found_preamble = True
				elif not found_preamble:
					raise_parsing_error_preamble_not_first(lb)
				label,pos = expect_label(subtree,pos)
# Contract requires a list
				items,pos = expect_list(subtree,pos)
				self._items[label] = dmap[lb]()
				self._items[label].parse(items)
			else:
				raise_parsing_error_invalid_label(lb,dmap)

class docitem_docstring_preamble_only(docitem_docstring_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "docstring"
	def parse(self,subtree : docstring_subtree) -> None:
		pos = 0
		dispatch_map = {
			"Preamble:":docitem_preamble,
			}
		while pos < len(subtree):
			lb = subtree[pos]
			assert isinstance(lb,str)
			if lb in dispatch_map:
				label,pos = expect_label(subtree,pos)
# Contract requires a list
				items,pos = expect_list(subtree,pos)
				self._items[label] = dispatch_map[lb]()
				self._items[label].parse(items)
			else:
# Terminate after preamble
				break

class docitem_docstring_module(docitem_docstring_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "docstring"
	def dispatch_map(self) -> Dict[str, Type[docitem_base]]:
		return {
			"Preamble:":docitem_preamble,
			"Definitions:":docitem_definitions,
			"Contract:":docitem_contract_class,
			"Description:":docitem_description,
			"Public_functions:":docitem_public_functions,
			"Public_classes:":docitem_public_classes,
			"Public_types:":docitem_public_types,
			"Public_constants:":docitem_public_constants,
			}

class docitem_docstring_class(docitem_docstring_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "docstring"
	def dispatch_map(self) -> Dict[str, Type[docitem_base]]:
		return {
			"Preamble:":docitem_preamble,
			"Definitions:":docitem_definitions,
			"Contract:":docitem_contract_class,
			"Derived_from:":docitem_derived_from,
			"Factory:":docitem_factory,
			"Description:":docitem_description,
			"Public_methods:":docitem_public_methods,
			}

class docitem_docstring_method(docitem_docstring_base):
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "docstring"
	def dispatch_map(self) -> Dict[str, Type[docitem_base]]:
		return {
			"Preamble:":docitem_preamble,
			"Definitions:":docitem_definitions,
			"Contract:":docitem_contract_method,
			"Parameters:":docitem_parameters,
			"Returns:":docitem_returns,
			"Raises:":docitem_raises,
			"Description:":docitem_description,
			"Usage:":docitem_usage,
			}

#===== end Top ================================================#

def validate_docstring_module(obj: object, top : docitem_docstring_module,node_contract : docitem_map_base,node_normative_sections : docitem_list_base) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| validate the docitem tree :cdml_var:`top` against the module object :cdml_var:`obj`.
		|Must| ensure that :cdml_label:`Contract` contains sections :cdml_label:`general` and :cdml_label:`api`.
		|Must| ensure that all sections declared as normative exist.
		|must| (todo) ensure that all functions listed in Public_functions exist and have a valid docstring.
Parameters:
	obj:
		The callable object to validate against.
	top:
		The docitem tree to validate.
	node_contract:
		The node for section :cdml_label:`Contract` already parsed by the caller.
	node_normative_sections:
		The node for section :cdml_label:`Preamble.normative_sections` already parsed by the caller.
Returns:
	|Must| return |None|
Raises:
	"""
#===== Contract must exist ====================================#
# checked by caller
#----- general must exist -------------------------------------#
	current = "class.Contract"
	if "general" not in node_contract.items():
		raise_validation_error(obj,current,"Section 'general' does not exist.")
#----- api must exist -----------------------------------------#
	current = "class.Contract"
	if "api" not in node_contract.items():
		raise_validation_error(obj,current,"Section 'api' does not exist.")
	current = "class.Contract.api"
# Rule api-02: each entry in api must refer to a normative section
	node_api = node_contract._items["api"]
	current = "class.Contract.api"
	for ref in node_api.items():
		if ref not in node_normative_sections.items():
			raise_validation_error(obj,current,f"Section '{ref}' is not listed in section 'Preamble.normative_sections'. We have {node_normative_sections.items()}.")
#===== Public_functions must exist if normative ===============#
	current = "class"
	if "Public_functions" in node_normative_sections.items():
		if "Public_functions" not in top.items():
			raise_validation_error(obj,current,"Section 'Public_functions' is marked normative but does not exist.")

def validate_docstring_class(obj: object, top : docitem_docstring_class,node_contract : docitem_map_base,node_normative_sections : docitem_list_base) -> None:
#===== Preamble must exist ====================================#
	current = "class"
# Rule pre-01: Preamble must exist. We do not allow purely informative docstrings.
	if "Preamble" not in top.items():
		raise_validation_error(obj,current,"pre-01: Section 'Preamble' does not exist.")
	node_preamble = top._items["Preamble"]
	assert isinstance(node_preamble,docitem_map_base)
#..... profile must exist .....................................#
# checked by caller
#..... normative_sections must exist ..........................#
# checked by caller

#===== Contract must exist ====================================#
# checked by caller
#----- general, constructor must exist ------------------------#
	current = "class.Contract"
	if "general" not in node_contract.items():
		raise_validation_error(obj,current,"Section 'general' does not exist.")
	if "constructor" not in node_contract.items():
		raise_validation_error(obj,current,"Section 'constructor' does not exist.")
#----- api must exist -----------------------------------------#
	current = "class.Contract"
	if "api" not in node_contract.items():
		raise_validation_error(obj,current,"Section 'api' does not exist.")
	current = "class.Contract.api"
# Rule api-02: each entry in api must refer to a normative section
	node_api = node_contract._items["api"]
	current = "class.Contract.api"
	for ref in node_api.items():
		if ref not in node_normative_sections.items():
			raise_validation_error(obj,current,f"Section '{ref}' is not listed in section 'Preamble.normative_sections'. We have {node_normative_sections.items()}.")
#===== Derived_from must exist if normative ===================#
	current = "class"
	if "Derived_from" in node_normative_sections.items():
		if "Derived_from" not in top.items():
			raise_validation_error(obj,current,"Section 'Derived_from' is marked normative but does not exist.")
#===== Public_methods must exist if normative =================#
	current = "class"
	if "Public_methods" in node_normative_sections.items():
		if "Public_methods" not in top.items():
			raise_validation_error(obj,current,"Section 'Public_methods' is marked normative but does not exist.")

def validate_docstring_method(obj: object, top : docitem_docstring_method,node_contract : docitem_map_base,node_normative_sections : docitem_list_base) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| validate the docitem tree :cdml_var:`top` against the callable object :cdml_var:`obj`.
		|Must| ensure that :cdml_label:`Contract` contains a section :cdml_label:`general`.
		|Must| ensure that all sections declared as normative exist.
		|Must| ensure that section :cdml_label:`Parameters` exists.
		|Must| ensure that section :cdml_label:`Returns` exists.
		|Must| ensure that section :cdml_label:`Raises` exists.
		|Must| ensure that each parameter mentioned in section :cdml_label:`Parameters` is in the callable's signature.
		|Must| ensure that each parameter in the callable's signature is mentioned in section :cdml_label:`Parameters`.
Parameters:
	obj:
		The callable object to validate against.
	top:
		The docitem tree to validate.
	node_contract:
		The node for section :cdml_label:`Contract` already parsed by the caller.
	node_normative_sections:
		The node for section :cdml_label:`Preamble.normative_sections` already parsed by the caller.
Returns:
	|Must| return |None|
Raises:
	"""
	current = "method"
# Contract must have a general section.
	if "general" not in node_contract.items():
		raise_validation_error(obj,f"{current}.Contract","Section 'general' does not exist.")
# If caller marks other sections normative, ensure they exist.
	for sec in node_normative_sections.items():
		if sec == "Contract":
			continue
		if sec not in top.items():
			raise_validation_error(obj,current,f"Section '{sec}' is listed as normative but does not exist.")
#===== Parameters must exist ==================================#
	if "Parameters" not in top.items():
		raise_validation_error(obj,current,"Section 'Parameters' does not exist.")
#===== Returns must exist =====================================#
	if "Returns" not in top.items():
		raise_validation_error(obj,current,"Section 'Returns' does not exist.")
#===== Raises must exist ======================================#
	if "Raises" not in top.items():
		raise_validation_error(obj,current,"Section 'Raises' does not exist.")
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
					raise_validation_error(obj,current,f"Parameter '{p}' documented but not in signature {param_names}.")
			for p in param_names:
				if p not in doc_params:
					raise_validation_error(obj,current,f"Parameter '{p}' in signature but not documented.")

def validate_docstring(obj: object, top : docitem_docstring_base) -> None:
#===== Preamble must exist ====================================#
	current = "class"
# Rule pre-01: Preamble must exist. We do not allow purely informative docstrings.
	if "Preamble" not in top.items():
		print(top.items())
		raise_validation_error(obj,current,"pre-01: Section 'Preamble' does not exist.")
	node_preamble = top._items["Preamble"]
	assert isinstance(node_preamble,docitem_map_base)
#..... profile must exist .....................................#
# Rule pre-02: profile must exist.
	if not "profile" in node_preamble.items():
		raise_validation_error(obj,current,"pre-02: Section 'profile' does not exist.")
	node_profile = node_preamble._items["profile"]
	current = "class.Preamble.profile"
	assert isinstance(node_profile,docitem_list_base)
	if len(node_profile.items()) > 1:
		raise_validation_error(obj,current,"Only one item allowed")
	if not _re_ident_compiled.fullmatch(node_profile._items[0]):
		raise_validation_error(obj,current,"expected identifier, got '{node_profile._items[0]}'.")

	current = "class.Preamble"
# Rule pre-03: normative_sections must exist and be non-empty. Non-emptyness is implied by existence and normativity of Contract.
	if "normative_sections" not in node_preamble.items():
		raise_validation_error(obj,current,"pre-03: Section 'normative_sections' does not exist.")
	node_normative_sections =  node_preamble._items["normative_sections"]
	assert isinstance(node_normative_sections,docitem_list_base)
# Rule pre-05: each entry must point to an existing section.
	seen = set()
	for sec in node_normative_sections.items():
		if not sec in top.items():
			raise_validation_error(obj,current,f"pre-05: Entry '{sec}' does not refer to an existing section.")
		if sec in seen:
			raise_validation_error(obj,current,f"pre-03: Entry '{sec}' is duplicate.")
		seen.add(sec)
# Rule: Any section containing one of the keywords of normativity
# must be listed under normative_sections.
	for label,item in top.items().items():
		if item.has_norm_keywords():
			if label not in node_normative_sections.items():
				raise_validation_error(obj,current,f"pre-xx: Section '{label}' contains a keyword of normativity but is not listed in normative_sections.")

#===== Contract must exist ====================================#
	current = "class"
	if "Contract" not in top.items():
		raise_validation_error(obj,current,"Section 'Contract' does not exist.")
# Rule pre-04: the contract must be listed as normative
	if not "Contract" in node_normative_sections.items():
		raise_validation_error(obj,current,"Section 'Contract' must be listed under 'normative_sections'.")
	node_contract = top._items["Contract"]
	assert isinstance(node_contract,docitem_map_base)
	
# Cases
	profile = node_profile._items[0]
	if profile == "module":
		assert isinstance(top,docitem_docstring_module)
		validate_docstring_module(obj,top,node_contract,node_normative_sections)
	elif profile == "class":
		assert isinstance(top,docitem_docstring_class)
		validate_docstring_class(obj,top,node_contract,node_normative_sections)
	elif profile in ("method","function"):
		assert isinstance(top,docitem_docstring_method)
		validate_docstring_method(obj,top,node_contract,node_normative_sections)
	else:
		raise_validation_error(obj,current,f"Unknown profile: {profile}")

#----- helpers for module coverage validators -----------------#

def _parse_and_validate_module_doc(obj: ModuleType) -> docitem_docstring_module:
	doc_txt = obj.__doc__
	if not isinstance(doc_txt,str):
		raise RuntimeError(f"module {obj.__name__} has no docstring.")
	tree = parse_indent_docstring(doc_txt)
	doc_module = docitem_docstring_module()
	doc_module.parse(tree)
	validate_docstring(obj,doc_module)
	return doc_module

def _get_public_section_entries(doc_module: docitem_docstring_module, section_label: str, expected_node_type: Type[docitem_map_base]) -> set[str]:
	public: set[str] = set()
	if section_label in doc_module.items():
		node = doc_module._items[section_label]
		assert isinstance(node, expected_node_type)
		public = set(node.items().keys())
	return public

def validate_class_method_coverage(obj: type[object]) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| analyze the docstrings of the class object passed.
		|Must| ensure that each method with a valid docstring is listed in the class' :cdml_label:`Public_methods` section.
		|Must| ensure that each method listed in the class' :cdml_label:`Public_methods` section has a valid docstring.
		|Must| require a :cdml_label:`Public_methods` section when at least one method docstring exists.
		|Must| handle :cdml_value:`@staticmethod` and :cdml_value:`@classmethod` as well as inherited methods listed in :cdml_label:`Public_methods`.
Parameters:
	obj:
		The class object to be validated.
Returns:
	|None|
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
# Validate class docstring first
	if not inspect.isclass(obj):
		raise RuntimeError("validate_class_method_coverage expects a class object.")
	doc_txt = obj.__doc__
	if not isinstance(doc_txt,str):
		raise RuntimeError(f"class {obj.__name__} has no docstring.")
	tree = parse_indent_docstring(doc_txt)
	doc_class = docitem_docstring_class()
	doc_class.parse(tree)
	validate_docstring(obj,doc_class)

# Collect declared public methods from class docstring
	public_methods: set[str] = set()
	if "Public_methods" in doc_class.items():
		pm_node = doc_class._items["Public_methods"]
		assert isinstance(pm_node, docitem_public_methods)
		public_methods = set(pm_node.items().keys())

# Collect methods defined on the class (not inherited) and validate their docstrings
	valid_methods: set[str] = set()
	for name, member in obj.__dict__.items():
		func_obj: Callable[..., Any] | None
		if inspect.isfunction(member):
			func_obj = member
		elif isinstance(member, staticmethod):
			func_obj = member.__func__
		elif isinstance(member, classmethod):
			func_obj = member.__func__
		else:
			func_obj = None
		if func_obj is None:
			continue
		docm = func_obj.__doc__
		if not isinstance(docm,str):
			continue
		# Parse and validate method docstring
		tree_m = parse_indent_docstring(docm)
		doc_method = docitem_docstring_method()
		doc_method.parse(tree_m)
		validate_docstring(func_obj,doc_method)
		valid_methods.add(name)

# Rule: if the class exposes methods with valid docstrings, it must declare Public_methods
	if valid_methods and not public_methods:
		raise RuntimeError(f"class {obj.__name__}: has method docstrings but no Public_methods section.")

# Rule: every method with a valid docstring must be listed
	missing_in_public = valid_methods - public_methods
	if missing_in_public:
		raise RuntimeError(f"class {obj.__name__}: methods with docstrings not listed in Public_methods: {sorted(missing_in_public)}")

# Rule: every method listed must have a valid docstring
	for meth_name in public_methods:
		if meth_name in valid_methods:
			continue
# method might be inherited; try to resolve and validate if present
		if not hasattr(obj, meth_name):
			raise RuntimeError(f"class {obj.__name__}: method '{meth_name}' listed in Public_methods but does not exist.")
		meth_obj = getattr(obj, meth_name)
		func_obj2: Callable[..., Any] | None
		if inspect.ismethod(meth_obj):
			func_obj2 = meth_obj.__func__
		elif inspect.isfunction(meth_obj):
			func_obj2 = meth_obj
		elif isinstance(meth_obj, staticmethod):
			func_obj2 = meth_obj.__func__
		elif isinstance(meth_obj, classmethod):
			func_obj2 = meth_obj.__func__
		else:
			func_obj2 = None
		if func_obj2 is None:
			raise RuntimeError(f"class {obj.__name__}: member '{meth_name}' listed in Public_methods is not a function.")
		docm = func_obj2.__doc__
		if not isinstance(docm, str):
			raise RuntimeError(f"class {obj.__name__}: method '{meth_name}' listed in Public_methods but has no valid docstring.")
		tree_m = parse_indent_docstring(docm)
		doc_method = docitem_docstring_method()
		doc_method.parse(tree_m)
		validate_docstring("selftest-method", doc_method)

# All good
	return None

def validate_class_coverage(obj: type[object]) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| validate for method coverage by calling the specific validator.
Parameters:
	obj:
		The module class to be validated.
Returns:
	|None|
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	validate_class_method_coverage(obj)

def validate_module_class_coverage(obj: ModuleType) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| analyze the docstrings of the module object passed.
		|Must| ensure that each class with a valid docstring is listed in the class' :cdml_label:`Public_classes` section.
		|Must| ensure that each class listed in the module's :cdml_label:`Public_classes` section has a valid docstring.
		|Must| require a :cdml_label:`Public_classes` section when at least one class docstring exists.
Parameters:
	obj:
		The module object to be validated.
Returns:
	|None|
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	doc_module = _parse_and_validate_module_doc(obj)

# Collect declared public classes from module docstring
	public_classes: set[str] = _get_public_section_entries(doc_module,"Public_classes",docitem_public_classes)

# Collect classes defined in the module (not imported) and validate their docstrings
	valid_classes: set[str] = set()
	for name, member in obj.__dict__.items():
		if not isinstance(member, type):
			continue
		if getattr(member,"__module__",None) != obj.__name__:
			continue
		docc = member.__doc__
		if not isinstance(docc,str):
			continue
		tree_c = parse_indent_docstring(docc)
		doc_class = docitem_docstring_class()
		doc_class.parse(tree_c)
		validate_docstring(member,doc_class)
		valid_classes.add(name)

# Rule: if the module exposes classes with valid docstrings, it must declare Public_classes
	if valid_classes and not public_classes:
		raise RuntimeError(f"module {obj.__name__}: has class docstrings but no Public_classes section.")

# Rule: every class with a valid docstring must be listed
	missing_in_public = valid_classes - public_classes
	if missing_in_public:
		raise RuntimeError(f"module {obj.__name__}: classes with docstrings not listed in Public_classes: {sorted(missing_in_public)}")

# Rule: every class listed must have a valid docstring
	for cls_name in public_classes:
		if cls_name in valid_classes:
			continue
		if not hasattr(obj, cls_name):
			raise RuntimeError(f"module {obj.__name__}: class '{cls_name}' listed in Public_classes but does not exist.")
		cls_obj = getattr(obj, cls_name)
		if not inspect.isclass(cls_obj):
			raise RuntimeError(f"module {obj.__name__}: member '{cls_name}' listed in Public_classes is not a class.")
		doc_c2 = cls_obj.__doc__
		if not isinstance(doc_c2, str):
			raise RuntimeError(f"module {obj.__name__}: class '{cls_name}' listed in Public_classes but has no valid docstring.")
		tree_c2 = parse_indent_docstring(doc_c2)
		doc_class2 = docitem_docstring_class()
		doc_class2.parse(tree_c2)
		validate_docstring(cls_obj, doc_class2)

# All good
	return None

def validate_module_function_coverage(obj: ModuleType) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| analyze the docstrings of the module object passed.
		|Must| ensure that each function with a valid docstring is listed in the module's :cdml_label:`Public_functions` section.
		|Must| ensure that each function listed in the module's :cdml_label:`Public_functions` section has a valid docstring.
		|Must| require a :cdml_label:`Public_functions` section when at least one function docstring exists.
Parameters:
	obj:
		The module object to be validated.
Returns:
	|None|
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	doc_module = _parse_and_validate_module_doc(obj)

# Collect declared public functions from module docstring
	public_functions: set[str] = _get_public_section_entries(doc_module,"Public_functions",docitem_public_functions)

# Collect functions defined in the module (not imported) and validate their docstrings
	valid_functions: set[str] = set()
	for name, member in obj.__dict__.items():
		if not isinstance(member, FunctionType):
			continue
		if getattr(member,"__module__",None) != obj.__name__:
			continue
		docf = member.__doc__
		if not isinstance(docf,str):
			continue
		tree_f = parse_indent_docstring(docf)
		doc_func = docitem_docstring_method()
		doc_func.parse(tree_f)
		validate_docstring(member,doc_func)
		valid_functions.add(name)

# Rule: if the module exposes functions with valid docstrings, it must declare Public_functions
	if valid_functions and not public_functions:
		raise RuntimeError(f"module {obj.__name__}: has function docstrings but no Public_functions section.")

# Rule: every function with a valid docstring must be listed
	missing_in_public = valid_functions - public_functions
	if missing_in_public:
		raise RuntimeError(f"module {obj.__name__}: functions with docstrings not listed in Public_functions: {sorted(missing_in_public)}")

# Rule: every function listed must have a valid docstring
	for func_name in public_functions:
		if func_name in valid_functions:
			continue
		if not hasattr(obj, func_name):
			raise RuntimeError(f"module {obj.__name__}: function '{func_name}' listed in Public_functions but does not exist.")
		func_obj = getattr(obj, func_name)
		if not inspect.isfunction(func_obj):
			raise RuntimeError(f"module {obj.__name__}: member '{func_name}' listed in Public_functions is not a function.")
		doc_f2 = func_obj.__doc__
		if not isinstance(doc_f2, str):
			raise RuntimeError(f"module {obj.__name__}: function '{func_name}' listed in Public_functions but has no valid docstring.")
		tree_f2 = parse_indent_docstring(doc_f2)
		doc_func2 = docitem_docstring_method()
		doc_func2.parse(tree_f2)
		validate_docstring(func_obj, doc_func2)

# All good
	return None

def validate_module_type_coverage(obj: ModuleType) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| analyze the docstrings of the module object passed.
		|Must| ensure that each type listed in the module's :cdml_label:`Public_types` section exists in the module.
Parameters:
	obj:
		The module object to be validated.
Returns:
	|None|
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	doc_module = _parse_and_validate_module_doc(obj)

# Collect declared public types from module docstring
	public_types: set[str] = _get_public_section_entries(doc_module,"Public_types",docitem_public_types)

# Rule: every type listed must exist
	for type_name in public_types:
		if not hasattr(obj, type_name):
			raise RuntimeError(f"module {obj.__name__}: type '{type_name}' listed in Public_types but does not exist.")

# All good
	return None

def validate_module_constant_coverage(obj: ModuleType) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| analyze the docstrings of the module object passed.
		|Must| ensure that each constant listed in the module's :cdml_label:`Public_constants` section exists in the module.
Parameters:
	obj:
		The module object to be validated.
Returns:
	|None|
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	doc_module = _parse_and_validate_module_doc(obj)

# Collect declared public constants from module docstring
	public_constants: set[str] = _get_public_section_entries(doc_module,"Public_constants",docitem_public_constants)

# Rule: every constant listed must exist
	for const_name in public_constants:
		if not hasattr(obj, const_name):
			raise RuntimeError(f"module {obj.__name__}: constant '{const_name}' listed in Public_constants but does not exist.")

# All good
	return None

def validate_module_coverage(obj: ModuleType) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| validate for class, function, type and constant coverage by calling the specific validators.
Parameters:
	obj:
		The module object to be validated.
Returns:
	|None|
Raises:
	RuntimeError:
		|Must| raise if validation fails.
	"""
	validate_module_class_coverage(obj)
	validate_module_function_coverage(obj)
	validate_module_type_coverage(obj)
	validate_module_constant_coverage(obj)

def gen_docstrings(obj: ModuleType | type[object]) -> Generator[Tuple[str,Any,str],None,None]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract
		Parameters
		Returns
		Raises
Contract:
	general:
		|Must| iterate over all objects in :cdml_var:`obj` including :cdml_var:`obj` itself and yield triples as described in section :cdml_label:`Returns`:
		|Must| iterate the object tree like depth-first traversal, pre-order and ignore all objects with missing or invalid docstring.
Parameters:
	obj:
		The object to iterate over.
Returns:
	A generator which produces triples. Each of these triples |must| consist of the profile
	as specified in the object's docstring, the object and the docstring of the object.
Raises:
	RuntimeError:
		|Must| raise whenever parsing a docstring raises :cdml_type:`RuntimeError`.
	"""
	def _iter(o: ModuleType | type[object] | Callable[..., Any]) -> Generator[Tuple[str,Any,str],None,None]:
		doc_txt = getattr(o, "__doc__", None)
		if not isinstance(doc_txt, str):
			return
		tree = parse_indent_docstring(doc_txt)
# Extract preamble with profile agnostic docstring node.
		node_docstring_preamble = docitem_docstring_preamble_only()
		node_docstring_preamble.parse(tree)
# We ignore the static type admonition here. Existence and well-definition is guaranteed by contracts.
		profile = node_docstring_preamble.items()["Preamble"].items()["profile"].items()[0] #type: ignore[index]

		if profile is None:
			return
		elif profile == "module":
			node: docitem_docstring_base = docitem_docstring_module()
		elif profile == "class":
			node = docitem_docstring_class()
		elif profile in ("method","function"):
			node = docitem_docstring_method()
		else:
			return
		node.parse(tree)
		validate_docstring(o, node)
		yield (profile, o, doc_txt)

		if isinstance(o, ModuleType):
			for name, member in o.__dict__.items():
				if isinstance(member, type) and getattr(member, "__module__", None) == o.__name__:
					yield from _iter(member)
				elif isinstance(member, FunctionType) and getattr(member, "__module__", None) == o.__name__:
					yield from _iter(member)
		elif isinstance(o, type):
			for name, member in o.__dict__.items():
				func_obj: Callable[..., Any] | None = None
				if isinstance(member, staticmethod):
					func_obj = member.__func__
				elif isinstance(member, classmethod):
					func_obj = member.__func__
				elif isinstance(member, FunctionType):
					func_obj = member
				if func_obj is None:
					continue
				yield from _iter(func_obj)

	yield from _iter(obj)

if __name__ == "__main__":
# Real world example
	assert isinstance(validate_class_method_coverage.__doc__,str)
	tree = parse_indent_docstring(validate_class_method_coverage.__doc__)
	print(tree)
	node = docitem_docstring_method()
	node.parse(tree)
	validate_docstring(validate_class_method_coverage,node)

	assert isinstance(validate_docstring_method.__doc__,str)
	tree = parse_indent_docstring(validate_docstring_method.__doc__)
	print(tree)
	node = docitem_docstring_method()
	node.parse(tree)
	validate_docstring(validate_docstring_method,node)

	assert isinstance(parse_indent_docstring.__doc__,str)
	tree = parse_indent_docstring(parse_indent_docstring.__doc__)
	print(tree)
	node = docitem_docstring_method()
	node.parse(tree)
	validate_docstring(parse_indent_docstring,node)

# Module
	assert isinstance(__doc__,str)
	tree = parse_indent_docstring(__doc__)
	print(tree)
	node = docitem_docstring_module()
	node.parse(tree)
	validate_docstring(sys.modules[__name__],node)
	validate_module_coverage(sys.modules[__name__])
# Profile

	assert isinstance(docitem_profile.__doc__,str)
	tree = parse_indent_docstring(docitem_profile.__doc__)
	print(tree)
	node = docitem_docstring_class()
	node.parse(tree)
	validate_docstring(docitem_profile,node)
	validate_class_method_coverage(docitem_profile)

#	for d in gen_docstrings(sys.modules[__name__]):
#		print(d)
