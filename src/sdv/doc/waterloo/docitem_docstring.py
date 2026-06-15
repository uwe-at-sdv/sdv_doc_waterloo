from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

from sdv.doc.waterloo.docitem_tokenizer import *
from sdv.doc.waterloo.docitem_helper import (
	explain_try_self_for_section,
	explain_try_self_for_subsection,
	render_allowed_identifier,
	render_deduplicated_identifiers,
	render_expected_identifier,
	render_expected_snippet,
	render_identifier_lines,
	render_missing_entry_details,
	render_normative_section_details,
	render_source_snippet,
)

# Import section modules
from sdv.doc.waterloo.docitem_sections import *
from sdv.doc.waterloo.docitem_preamble import *
from sdv.doc.waterloo.docitem_contract import *


#===== begin Docstring ========================================#

class docitem_docstring_base(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
	scope:
		public
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
	parse, scopes, is_visible, can_see, is_scope_compatible
Method_overview:
	parse:
		Parse a docstring tree.
	"""
	def __init__(self) -> None:
		super().__init__()
	def dispatch_map(self) -> Dict[str, Type[docitem_base]]:
		raise NotImplementedError
	def label(self) -> str:
		return "docstring"
	def scopes(self) -> Scopes:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
			scope:
				extension
		Contract:
			general:
				|Must| return the scopes assigned to the object in subsection |label|`Preamble.scope`.
				|Must| fall back to the default value, if there is no subsection |label|`scope` in |label|`Preamble`.
				|Must| use {|value|`core`} as default value, i.e. a set with a single element.
			requires:
				|self| |must| represent a formally correct Abstract Syntax Tree.
		Parameters:
		Returns:
			A set of enum values representing the scopes of the documented object.
		Raises:
			SectionNotFoundError:
				|Must| raise if the tree has no |label|`Preamble`.
		"""
		if not self.has_item("Preamble"):
			raise SectionNotFoundError("Preamble")
		node_preamble = self.item("Preamble")
# Default value is core as set with a single element
		if not node_preamble.has_item("scope"):
			return set([Scope.PUBLIC])
		node_scope = node_preamble.item("scope")
		return set([SCOPE_TAG_MAP[s] for s in node_scope.items()])

	def is_visible(self,sc_query: Scopes) -> bool:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
			scope:
				extension
		Contract:
			general:
				|Must| test visibility of the documented object against a set of scopes passed.\
				Visibility is given if the object has a scope with a value less than at least one\
				scope in the set passed.
			requires:
				Requirements of method |func|`scopes` apply.
		Parameters:
			sc_query:
				The set of scopes to test visibility against.
		Returns:
			|Must| return |True| iff there exists s_obj in the object's scope set and\
			s_query in |var|`sc_query` such that s_obj <= s_query.

		Raises:
			SectionNotFoundError:
				|May| propagate from |func|`scopes`.
		"""
		scopes_obj = self.scopes()
		return any(s_obj <= s_query for s_query in sc_query for s_obj in scopes_obj)

	def can_see(self,sc_query: Scopes) -> bool:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| test whether at least one scope in |var|`sc_query` is at least as public as\
				at least one scope in |self|.
				This is the visibility relation used for upward references: a referenced object\
				|must| be at least as public as the referencing object.
			requires:
				Requirements of method |func|`scopes` apply.
		Parameters:
			sc_query:
				The set of scope values of the referenced object.
		Returns:
			|True| iff there exists s_query in |var|`sc_query` and s_self in |self|.scopes()\
			such that s_query <= s_self.
		Raises:
			SectionNotFoundError:
				|May| propagate from |func|`scopes`.
		"""
		scopes_obj = self.scopes()
		return any(s_query <= s_obj for s_query in sc_query for s_obj in scopes_obj)

	def is_scope_compatible(self,obj_trg : docitem_docstring_base) -> bool:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
			scope:
				extension
		Contract:
			general:
				|Must| test whether at least one scope in the referenced object |var|`obj_trg`\
				is at least as public as at least one scope in |self|.
				This is the scope-compatibility relation used for reference edges:\
				the referenced object |must| be at least as public as |self|.
			requires:
				Requirements of method |func|`scopes` apply,\
				for both |self| and |var|`obj_trg`.
		Parameters:
			obj_trg:
				The embedded, referenced or otherwise dependent object.
		Returns:
			|True| if scopes are compatible, else |False|.
		Raises:
			SectionNotFoundError:
				|May| propagate from |func|`scopes`.
		"""
		scopes_src = self.scopes()
		scopes_trg = obj_trg.scopes()
		return any(s_src <= s_trg for s_src in scopes_src for s_trg in scopes_trg)

	def get_scope_text(self) -> str:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| return the documented object's scopes as a comma-separated, lowercase string.
				|Must| return |"undefined"| if the tree is malformed enough to prevent scope detection, or if the scope section is missing.
			requires:
				|Self| |must| represent a formally correct Abstract Syntax Tree.
		Parameters:
		Returns:
			The documented object's scopes as a comma-separated, lowercase string, or |"undefined"| if the
			tree is malformed enough to prevent scope detection, or if the scope section is missing.
		Raises:
		"""
		try:
			scopes = self.scopes()
		except Exception:
			return "undefined"
		if not scopes:
			return "undefined"
		try:
			items = []
			for sc in sorted(scopes, key=lambda s: getattr(s, "value", 0)):
				name = getattr(sc, "name", None)
				items.append(str(name).lower() if isinstance(name, str) else str(sc).lower())
			return ",".join(items) if items else "undefined"
		except Exception:
			return "undefined"
		
	def parse(self,tr : tracer,tree : DocstringSubtree) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| accept a complete docstring tree according to the map returned by the derived class' method |func|`dispatch_map`.
		Parameters:
			tr:
				The tracer for collecting diagnostics.
			tree:
				The docstring tree
		Returns:
			|Must| return |None|.
		Raises:
			RuntimeError:
				|Must| raise if |label|`Preamble` is not the first section found.
				|Must| raise if an invalid section label is found.
				|Must| raise if parsing any of the sections fails.
			NotImplementedError:
				|Must| raise if not invoked for an instance of a derived class.
		"""
		found_preamble = False
		pos = 0
		dmap = self.dispatch_map()
# Duplicate section labels are an error.
		seen = set()
		while pos < len(tree):
# Section labels must be identifiers.
			with rule_on_fail(tr, "PRSR-005"):
				label,pos = expect_label_identifier(tr,tree,pos)
			if label in dmap:
				if label == "Preamble":
					found_preamble = True
				elif not found_preamble:
					details = {
						"found": render_suggestion("", "No Preamble"),
						"expected": ["Preamble:","\tprofile:","\t\t...","\tnormative_sections:","\t\t...","\t..."],
						"hint": explain_try_self_for_section("Preamble", "PROFILE"),
					}
					raise_parsing_error(tr,"PRE-001","Preamble is not first.", details)
				items,pos = expect_list(tr,tree,pos)
				if label in seen:
					raise_parsing_error(tr,"PRSR-007",f"Duplicate label '{label}'.")
				seen.add(label)
				self.add_child(tr,label, dmap[label], items)
			else:
# Choose profile-specific rule for unexpected sections.
				if isinstance(self, docitem_docstring_module):
					rule_ids = "DOC-003"
				elif isinstance(self, docitem_docstring_class):
					rule_ids = "DOC-004"
				elif isinstance(self, docitem_docstring_method):
					rule_ids = "DOC-005"
				elif isinstance(self, docitem_docstring_inherited_method):
					rule_ids = "DOC-006"
				else:
					rule_ids = "DOC-999"
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
		|Must| represent the docstring for profile |value|`module`.
		|Must| provide a map from |type|`str` to |type|`Type[docitem_base]` which assigns a docitem class constructor to each allowed section label.
	constructor:
		|Must| be default-constructible
Factory:
	make_docitem_tree:
		|Must| accept a tracer and a docstring, read the profile and generate the AST from it. See docstring of function.
Derived_from:
	docitem_docstring_base
Public_methods:
	dispatch_map
Method_overview:
	dispatch_map:
		Return the forementioned map from label to constructor.
	"""
	def __init__(self) -> None:
		super().__init__()
	@classmethod
	def is_docstring_module(cls) -> bool:
		return True
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
		|Must| provide label/constructor pairs for at least the folowing sections: { |label|`Preamble`, |label|`Definitions`, |label|`Terminology`, |label|`Contract`, |label|`Description`, |label|`Function_overview`, |label|`Class_overview`, |label|`Public_types`, |label|`Public_constants`}
Parameters:
Returns:
	The dict as described in |label|`Contract`.
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
		 "Class_overview":docitem_class_overview,
		 "Function_overview":docitem_function_overview,
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
		|Must| represent the docstring for profiles  |value|`class`.
		|Must| provide a map from |type|`str` to |type|`Type[docitem_base]` which assigns a docitem class constructor to each allowed section label.
	constructor:
		|Must| be default-constructible
Factory:
	make_docitem_tree:
		|Must| accept a tracer and a docstring, read the profile and generate the AST from it. See docstring of function.
Derived_from:
	docitem_docstring_base
Public_methods:
	dispatch_map
Method_overview:
	dispatch_map:
		Return the forementioned map from label to constructor.
	"""
	def __init__(self) -> None:
		super().__init__()
	@classmethod
	def is_docstring_class(cls) -> bool:
		return True
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
		|Must| provide label/constructor pairs for at least the folowing sections: { |label|`Preamble`, |label|`Definitions`, |label|`Terminology`, |label|`Contract`, |label|`Derived_from`, |label|`Factory`, |label|`Description`, |label|`Class_overview`, |label|`Method_overview`, |label|`Public_types`, |label|`Public_constants`}
Parameters:
Returns:
	The dict as described in |label|`Contract`.
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
		 "Class_overview":docitem_class_overview,
		 "Method_overview":docitem_method_overview,
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
		|Must| represent the docstring for profiles  |value|`function` and |value|`method`.
		|Must| provide a map from |type|`str` to |type|`Type[docitem_base]` which assigns a docitem class constructor to each allowed section label.
	constructor:
		|Must| be default-constructible
Factory:
	make_docitem_tree:
		|Must| accept a tracer and a docstring, read the profile and generate the AST from it. See docstring of function.
Derived_from:
	docitem_docstring_base
Public_methods:
	dispatch_map
Method_overview:
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
		|Must| provide label/constructor pairs for at least the folowing sections: { |label|`Preamble`, |label|`Definitions`, |label|`Terminology`, |label|`Contract`, |label|`Parameters`, |label|`Returns`, |label|`Raises`, |label|`Description`}
Parameters:
Returns:
	The dict as described in |label|`Contract`.
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
		|Must| represent the docstring for profile  |value|`inherited_method`.
		|Must| provide a map from |type|`str` to |type|`Type[docitem_base]` which assigns a docitem class constructor to each allowed section label.
	constructor:
		|Must| be default-constructible
Factory:
	make_docitem_tree:
		|Must| accept a tracer and a docstring, read the profile and generate the AST from it. See docstring of function.
Derived_from:
	docitem_docstring_base
Public_methods:
	dispatch_map
Method_overview:
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
		|Must| provide label/constructor pairs for at least the folowing sections: { |label|`Preamble`, |label|`Definitions`, |label|`Terminology`, |label|`Contract`, |label|`Parameters`, |label|`Returns`, |label|`Raises`, |label|`Description`}
Parameters:
Returns:
	The dict as described in |label|`Contract`.
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

def make_docitem_tree_from_docstring_tree(tr : tracer, tree : DocstringTree) -> docitem_docstring_base:
# Extract profile
	if tree == []:
		raise_parsing_error(tr,"DOC-007","Empty docstring.")
	try:
		profile = get_profile_of_tree(tr,tree)
	except SectionNotFoundError:
		details = {
			"found": render_suggestion("","No Preamble"),
			"expected": ["Preamble:","\tprofile:","\t\t...","\tnormative_sections:","\t\t...","\t..."],
			"hint": explain_try_self_for_section("Preamble","PROFILE"),
		}
		raise_parsing_error(tr,"PRE-001","Section 'Preamble' not found.", details)
	except SubsectionNotFoundError:
		details = {
			"found": ["Preamble:", "\t<no profile>"],
			"expected": ["Preamble:", "\tprofile:", f"\t\t<one of {{{', '.join(CANONICAL_ORDER_OF_PROFILES)}}}>"],
			"hint": ["waterlint explain-subsection --label Preamble.profile --profile PROFILE"],
		}
		raise_parsing_error(tr,"PRE-003","Subsection 'Preamble.profile' not found.", details)
	except NoContentError:
		details = {
			"found": render_identifier_lines("Preamble.profile", []),
			"expected": ["Preamble:", "\tprofile:", f"\t\t<one of {{{', '.join(CANONICAL_ORDER_OF_PROFILES)}}}>"],
			"hint": ["waterlint explain-subsection --label Preamble.profile --profile PROFILE"],
		}
		raise_parsing_error(tr,"PRE-004","Section 'Preamble.profile' must have exactly one item.", details)
	except Exception as exc:
		raise
# This looks redundant because later we directly check for allowed profiles, but
# we should check the rules in certain order so that behaviour remains predictible.
	if not RE_IDENTIFIER_COMPILED.fullmatch(profile):
		details = {
			"found": render_identifier_lines("Preamble.profile", [profile]),
			"expected": render_expected_identifier("Preamble.profile", "identifier"),
			"hint": ["waterlint explain-subsection --label Preamble.profile --profile PROFILE"],
		}
		raise_parsing_error(tr,"PRE-014","'Preamble.profile' must be an identifier.", details)
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
		allowed_profiles = ("module","class","function","method","inherited_method")
		details = {
			"found": render_identifier_lines("Preamble.profile", [profile]),
			"expected": render_allowed_identifier("Preamble.profile", allowed_profiles),
			"hint": ["waterlint explain-subsection --label Preamble.profile --profile PROFILE"],
		}
		raise_parsing_error(tr,"PRE-005",f"invalid profile: '{profile}'", details)
	di_node.parse(tr,tree)
	return di_node

def make_docitem_tree(tr : tracer, doc_txt : str) -> docitem_docstring_base:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| accept a |type|`tracer` instance and a string as parameters.
		|Must| try to parse the string as waterloo docstring and create a docstring tree.
		|Must| determine the profile from the docstring tree and create the appropriate docitem node class.
		|Must| call the docitem node's method |func|`parse` and create an Abstract Syntax Tree.
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
		|Must| raise if section |label|`Preamble` is not found.
		|Must| raise if subsection |label|`Preamble.profile` is not found.
		|Must| raise if subsection |label|`Preamble.profile` does not contain exactly one item.
		|Must| raise if the content of subsection |label|`Preamble.profile` is not an identifier..
		|Must| raise if subsection |label|`Preamble.profile` does not contain a valid profile.
	BaseException:
		|Must_not| propagate exceptions from |type|`get_profile_of_tree`.
		|May| propagate exceptions from method |func|`parse_indent_docstring`.
		|May| propagate exceptions from method |type|`docitem_docstring_base`. |func|`parse`.
Notes:
	Last review:
		2026-01-22
	"""
	tree = parse_indent_docstring(tr, doc_txt)
	return make_docitem_tree_from_docstring_tree(tr, tree)

def check_profile_matches_object(tr: tracer, profile: str, obj: object) -> None:
	if is_obj_module(obj):
		if profile != "module":
			details = render_profile_mismatch_details(get_obj_name(obj), "module", profile, "<use profile module>", profile)
			raise_validation_error(tr, obj, "PRE-017", f"profile is '{profile}' but '{get_obj_name(obj)}' is a module.", details)
	elif is_obj_class(obj):
		if profile != "class":
			details = render_profile_mismatch_details(get_obj_name(obj), "class", profile, "<use profile class>", "PROFILE")
			raise_validation_error(tr, obj, "PRE-018", f"profile is '{profile}' but '{get_obj_name(obj)}' is a class.", details)
	else:
		if profile not in {"function", "method", "inherited_method"}:
			warn_validation(tr, obj, "PRE-020", f"profile 'inherited_method' might be appropriate, cannot decide at this location in code.")
			details = render_profile_mismatch_details(get_obj_name(obj), "function or method", profile, "<use profile function, method or inherited_method>", profile)
			raise_validation_error(tr, obj, "PRE-019", f"profile is '{profile}' but '{get_obj_name(obj)}' is a function or method.", details)
		is_method_like = isinstance(obj, property) or is_obj_method_like(obj)
		if is_method_like:
			if profile not in {"method", "inherited_method"}:
				details = render_profile_mismatch_details(get_obj_name(obj), "method-like", profile, "<use profile method or inherited_method>", profile)
				raise_validation_error(tr, obj, "PRE-019", f"profile is '{profile}' but '{get_obj_name(obj)}' is method-like.", details)
		else:
			if profile != "function":
				details = render_profile_mismatch_details(get_obj_name(obj), "function", profile, "<use profile function>", profile)
				raise_validation_error(tr, obj, "PRE-019", f"profile is '{profile}' but '{get_obj_name(obj)}' is a function.", details)

def make_docitem_tree_from_object(tr: tracer, obj: object) -> docitem_docstring_base:
	tree = parse_indent_docstring(tr, get_obj_docstring(obj))
# We test **carefully** if the profile exists and matches. We skip the
# test if the profile cannot be determined, in order to not shadow other
# error messages like DOC-007.
	try:
		profile = get_profile_of_tree(tr,tree)
		if profile != "":
			check_profile_matches_object(tr,profile,obj)
# The profile must match the object type.
	except Exception:
		pass
	return make_docitem_tree_from_docstring_tree(tr, tree)

#===== end Docstring ==========================================#
