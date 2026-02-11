"""
Preamble:
	profile:
		module
	normative_sections:
		Contract
		Public_classes
		Public_functions
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
Public_functions:
	is_attr_annotated, is_attr_final, get_obj_name, get_obj_path, resolve_object, get_status, get_profile, get_num_indent
	parse_indent_docstring, get_tree_of_section, get_tree_of_subsection, to_string_tree
	validate_docstring_method, validate_docstring_inherited_method, validate_docstring_class
	validate_docstring_module, validate_docstring, validate_class_class_coverage
	validate_class_method_coverage, validate_class_constant_coverage, validate_class_variable_coverage
	validate_class_coverage, validate_module_class_coverage, validate_module_function_coverage
	validate_module_type_coverage, validate_module_constant_coverage, validate_module_variable_coverage
	validate_module_coverage, gen_documentable_objects, make_docitem_tree

Function_overview:
	is_attr_annotated:
		Find out if an attribute of a class or module is annotated.
	is_attr_final:
		Find out if an attribute of a class or module is annotated as 'Final'.
	resolve_object:
		Resolve an object by its qualified identifier
	get_status:
		Extract documented object status from docitem tree
	get_profile:
		Extract documented profile from docitem tree
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
	make_docitem_tree:
		Generate a docitem tree from a docstring.
Public_classes:
	tracer
	docitem_base, docitem_list_base, docitem_map_base, docitem_free_text_entry_base
	docitem_list_of_symbols_base, docitem_profile, docitem_normative_sections, docitem_status
	docitem_preamble, docitem_constructor, docitem_general, docitem_invariants, docitem_requires
	docitem_ensures, docitem_base_to_inherit_from, docitem_api, docitem_traits, docitem_contract_module
	docitem_contract_class, docitem_contract_method, docitem_contract_inherited_method
	docitem_derived_from, docitem_factory_functions, docitem_factory, docitem_class_overview_entry
	docitem_class_overview, docitem_public_types_entry, docitem_public_types
	docitem_public_assignables_entry, docitem_public_assignables_base, docitem_method_overview_entry
	docitem_method_overview, docitem_function_overview_entry, docitem_function_overview, docitem_returns
	docitem_parameters_entry, docitem_parameters, docitem_raises_entry, docitem_raises
	docitem_definitions_entry, docitem_definitions, docitem_terminology_entry, docitem_terminology
	docitem_notes_entry, docitem_notes, docitem_description, docitem_see_also, docitem_docstring_base
	docitem_docstring_module, docitem_docstring_class, docitem_docstring_method, docitem_docstring_inherited_method
	Scope, Flavour, Format
Class_overview:
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
		Node class for section |label|`profile`
	docitem_normative_sections:
		Node class for subsection |label|`normative_sections`
	docitem_status:
		Node class for subsection |label|`status`
	docitem_preamble:
		Node class for section |label|`Preamble`
	docitem_constructor:
		Node class for subsection |label|`constructor`
	docitem_general:
		Node class for subsection |label|`general`
	docitem_invariants:
		Node class for subsection |label|`invariants`
	docitem_requires:
		Node class for subsection |label|`requires`
	docitem_ensures:
		Node class for subsection |label|`ensures`
	docitem_base_to_inherit_from:
		Node class for subsection |label|`base`
	docitem_api:
		Node class for subsection |label|`api`
	docitem_traits:
		Node class for subsection |label|`traits`
	docitem_contract_module:
		Node class for section |label|`Contract`, profile |value|`module`.
	docitem_contract_class:
		Node class for section |label|`Contract`, profile |value|`class`.
	docitem_contract_method:
		Node class for section |label|`Contract`, profile |value|`method` or |value|`function`.
	docitem_contract_inherited_method:
		Node class for section |label|`Contract`, profile |value|`inherited_method`.
	docitem_derived_from:
		Node class for section |label|`Derived_from`.
	docitem_factory_functions:
		Node class for entries in section |label|`Factory`.
	docitem_factory:
		Node class for section |label|`Factory`.
	docitem_class_overview_entry:
		Node class for entries in section |label|`Class_overview`.
	docitem_class_overview:
		Node class for section |label|`Class_overview`.
	docitem_public_types_entry:
		Node class for entries in section |label|`Public_types`.
	docitem_public_types:
		Node class for section |label|`Public_types`.
	docitem_public_assignables_entry:
		Node class for entries in section |label|`Public_constants` and |label|`Public_variables`.
	docitem_public_assignables_base:
		Node base class for sections |label|`Public_constants` and |label|`Public_variables`.
	docitem_method_overview_entry:
		Node class for entries in section |label|`Method_overview`.
	docitem_method_overview:
		Node class for section |label|`Method_overview`.
	docitem_function_overview_entry:
		Node class for entries in section |label|`Function_overview`.
	docitem_function_overview:
		Node class for section |label|`Function_overview`.
	docitem_returns:
		Node class for section |label|`Returns`.
	docitem_parameters_entry:
		Node class for a parameter description
	docitem_parameters:
		Node class for section |label|`Parameters`
	docitem_raises_entry:
		Node class for entries in section |label|`Raises`.
	docitem_raises:
		Node class for section |label|`Raises`
	docitem_definitions_entry:
		Node class for entries in section |label|`Definitions`.
	docitem_definitions:
		Node class for section |label|`Definitions`
	docitem_terminology_entry:
		Node class for entries in section |label|`Terminology`.
	docitem_terminology:
		Node class for section |label|`Terminology`
	docitem_notes_entry:
		Node class for entries in section |label|`Notes`.
	docitem_notes:
		Node class for section |label|`Notes`
	docitem_description:
		Node class for section |label|`Description`.
	docitem_see_also:
		Node class for section |label|`See_also`

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
	Documentable_t:
		Type for objects that can have a docstring.
	Scopes_t:
		Type alias for a set of scopes.
Public_constants:
	RE_IDENTIFIER:
		Regular expression for identifiers: ``[A-Za-z_][A-Za-z0-9_]*``
	RE_QUALIFIED_IDENTIFIER:
		Regular expression for qualified identifiers: ``[A-Za-z_.][A-Za-z0-9_.]*``
	KEYWORDS_OF_NORMATIVITY:
		The set of normative keywords.
	CANONICAL_ORDER_OF_SECTIONS:
		A canonical order for sections and subsection in order to reduce permutative noise for LLMs.
	SCOPE_TAG_MAP:
		Map string representations of scopes to symbolic/numeric values.
	FLAVOUR_TAG_MAP:
		Map string representations of flavours to symbolic/numeric values.
	FORMAT_TAG_MAP:
		Map string representations of output formats to symbolic/numeric values.
"""

# Todo: think about Contract.import_side_fx

import sys,re,pkgutil
import inspect
import importlib
import builtins
import typing
from types import FunctionType, ModuleType
from contextlib import contextmanager

try:
	from sdv_doc_docitem_docstring import *
except ImportError:
	from sdv.doc.waterloo.docitem_docstring import *

try:
	from sdv_doc_docitem_validator import *
except ImportError:
	from sdv.doc.waterloo.docitem_validator import *

__version__ = "0.1.0"

def gen_documentable_objects(obj: Documentable_t,config: ConfigTraversal = ConfigTraversal()) -> Generator[Documentable_t,None,None]:
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
		|Must| create a generator object which allows depth-first tree traversal of objects in |var|`obj`.
		|Must| first yield object |var|`obj` itself.
		|Must| yield all objects and only objects which can have a docstring.
Parameters:
	obj:
		The object (module, class, function, method) to examine.
	config:
		Controls acceptance or refusal of objects during traversal.
Returns:
	|Must| return a Generator which yields objects from tree traversal of |var|`obj`
Raises:
	"""
	_seen: Set[Documentable_t] = set()
	def _iter(o: Documentable_t,seen: Set[Documentable_t]) -> Generator[Documentable_t,None,None]:
		if o in seen:
			return
# With the seen-mechanisms each direct yield must be paired with updating `seen`.
		seen.add(o)
		yield o
		if isinstance(o, ModuleType):
			# We're in a module. There might be classes and functions:
			for name, member in list(o.__dict__.items()):
				if isinstance(member, ModuleType):
					# descend into submodules
					if not config.accept_imported_module(o,member):
						continue
					yield from _iter(member, seen)
				elif isinstance(member, type):
					# class
					if not config.accept_member_of_module(o,member):
						continue
					yield from _iter(member, seen)
				elif isinstance(member, FunctionType):
					# function
					if not config.accept_member_of_module(o,member):
						continue
					yield from _iter(member, seen)
				else:
					continue
			# Optionally walk package submodules on disk
			if config.include_imported() and config.walk_packages() and hasattr(o, "__path__"):
				for finder, mod_name, is_pkg in pkgutil.iter_modules(o.__path__, o.__name__ + "."):
					try:
						submod = importlib.import_module(mod_name)
					except Exception:
						continue
					yield from _iter(submod, seen)
		elif isinstance(o, type):
			# We're in a class. There might be classes, static functions, class methods and "normal" methods:
			for name, member in list(o.__dict__.items()):
				if isinstance(member, type):
					yield from _iter(member, seen)
				else:
					func_obj = get_func_obj_from_callable(member)
					if func_obj is None:
						continue
					yield from _iter(func_obj, seen)
		elif callable(o):
# Functions/methods are leaves for our traversal
			return
	yield from _iter(obj,_seen)
  
if __name__ == "__main__":
	tr = tracer()
	validate_module_coverage(tr,sys.modules[__name__])
	if tr.has_warnings():
		print("### WARNINGS! ###")
		print(tr.to_string_warnings())
