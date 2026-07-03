from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

from sdv.doc.waterloo.docitem_tokenizer import *
from sdv.doc.waterloo.docitem_base import *
from sdv.doc.waterloo.docitem_diagnostics import (
	explain_try_self_for_section,
	explain_try_self_for_subsection,
	render_found_label,
	render_suggestion,
)

#===== begin section Derived_from =============================#

#----- docitem class derived_from -----------------------------#

class docitem_derived_from(docitem_list_of_symbols_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`Derived_from` section.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_of_symbols_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`Derived_from` section.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Derived_from"
	def diagnostics_label(self) -> str:
		return "Derived_from"
	def parse(self,tr : tracer,bases : DocstringSubtree) -> None:
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
		super()._parse(tr, bases, docitem_list_of_symbols_base.ValuePattern.QUALIFIED_IDENTIFIER)

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
		|Must| represent the |label|`See_also` section.
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
		return "See_also"
	def diagnostics_label(self) -> str:
		return "See_also"
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
		super()._parse(tr, refs, docitem_list_of_symbols_base.ValuePattern.QUALIFIED_IDENTIFIER)

#===== end section See also ===================================#

#===== begin section Public_classes ===========================#

class docitem_public_classes(docitem_list_of_symbols_base):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Derived_from, Public_methods
	Contract:
		general:
			|Must| represent the |label|`Public_classes` section.
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
		return "Public_classes"
	def diagnostics_label(self) -> str:
		return "Public_classes"
	def parse(self, tr: tracer, refs: DocstringSubtree) -> None:
		"""
		Preamble:
			profile:
				inherited_method
			normative_sections:
				Contract
		Contract:
			general:
				|Must| delegate to |func|`_parse` in the base implementation.
				|Must| parse |var|`refs` as a list of Qualified Identifiers.
			base:
				sdv.doc.waterloo.docitem.docitem_list_of_symbols_base.parse
		Notes:
			Last review:
				2026-02-23
		"""
# No need to set a default rule. _parse in the base class is
# a complete implementation of rules LQID-001 to LQID-005.
		super()._parse(tr, refs, docitem_list_of_symbols_base.ValuePattern.QUALIFIED_IDENTIFIER)

#===== end section Public_classes =============================#

#===== begin section Public_methods ===========================#

class docitem_public_methods(docitem_list_of_symbols_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`Public_methods` section.
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
		return "Public_methods"
	def diagnostics_label(self) -> str:
		return "Public_methods"
	def parse(self, tr: tracer, refs: DocstringSubtree) -> None:
		"""
		Preamble:
			profile:
				inherited_method
			normative_sections:
				Contract
		Contract:
			general:
				|Must| delegate to |func|`_parse` in the base implementation.
				|Must| parse |var|`refs` as a list of Qualified Identifiers.
			base:
				sdv.doc.waterloo.docitem.docitem_list_of_symbols_base.parse
		Notes:
			Last review:
				2026-02-23
		"""
# No need to set a default rule. _parse in the base class is
# a complete implementation of rules LQID-001 to LQID-005.
		super()._parse(tr, refs, docitem_list_of_symbols_base.ValuePattern.QUALIFIED_IDENTIFIER)

#===== end section Public_methods =============================#

#===== begin section Public_functions =========================#

class docitem_public_functions(docitem_list_of_symbols_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`Public_functions` section.
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
		return "Public_functions"
	def diagnostics_label(self) -> str:
		return "Public_functions"
	def parse(self, tr: tracer, refs: DocstringSubtree) -> None:
		"""
		Preamble:
			profile:
				inherited_method
			normative_sections:
				Contract
		Contract:
			general:
				|Must| delegate to |func|`_parse` in the base implementation.
				|Must| parse |var|`refs` as a list of Qualified Identifiers.
			base:
				sdv.doc.waterloo.docitem.docitem_list_of_symbols_base.parse
		Notes:
			Last review:
				2026-02-23
		"""
# No need to set a default rule. _parse in the base class is
# a complete implementation of rules LQID-001 to LQID-005.
		super()._parse(tr, refs, docitem_list_of_symbols_base.ValuePattern.QUALIFIED_IDENTIFIER)

#===== end section Public_functions ===========================#

#===== begin section Factory ==================================#

#----- docitem class factory ----------------------------------#

class docitem_factory_functions(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the content of an entry in section |label|`Factory`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a list of text lines describing the factory function.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "factory_functions"

class docitem_factory(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`Factory` section.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a |label|`Factory`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Factory"
	def parse(self,tr : tracer,functions : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of section |label|`Factory`.
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
		seen: Set[str] = set()
		while pos < len(functions):
# "Factory" requires a list of factory function names
			with rule_on_fail(tr, "FAC-005"):
				label,pos = expect_label_qualified_identifier(tr,functions,pos)
				if label in seen:
					details: Details = {
						"found": render_found_label("Factory", label),
						"expected": render_suggestion("Factory", "a unique entry"),
						"hint": explain_try_self_for_section("Factory", "class"),
					}
					raise_parsing_error(tr,"FAC-008",f"Duplicate entry '{label}'.", details)
				seen.add(label)
			items,pos = expect_list(tr,functions,pos)
			with rule_on_fail(tr, "FAC-007"):
				self.add_child(tr,label, docitem_factory_functions, items)

#===== end section Factory ====================================#

#===== begin section Class_overview ===========================#

#----- docitem class class_overview ---------------------------#

# An entry for a function in section Public classes is only a brief
# description that the class is good for. Classes must be explained
# in details outside the module documentation block.
class docitem_class_overview_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the content of an entry in section |label|`Class_overview`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a list of text lines describing the public class.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "class_overview_entries"

class docitem_class_overview(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`Class_overview` section.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse the content of a section |label|`Class_overview`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Class_overview"
	def detect_partial_normativity(self,tr: tracer) -> bool:
		# True because Class_overview is always informative.
		return True
	def parse(self,tr : tracer,entries : DocstringSubtree) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| parse the content of section |label|`Class_overview`.
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
		p = self.parent()
		pos = 0
		while pos < len(entries):
			assert isinstance(p,docitem_base)
# Public_types can occur in modules and classes
			if p.is_docstring_module():
				rule_id = "MCLO-005"
			elif p.is_docstring_class():
				rule_id = "CCLO-005"
			else:
# Should never happen. Keep split placeholder mnemonic for consistency.
				rule_id = "MCLO-999"
			with rule_on_fail(tr, rule_id):
				label,pos = expect_label_identifier(tr,entries,pos)
# class_overview requires a list of class_overview function names
			items,pos = expect_list(tr,entries,pos)
			if p.is_docstring_module():
				rule_id = "MCLO-006"
			else:
				rule_id = "CCLO-006"
			with rule_on_fail(tr, rule_id):
				self.add_child(tr,label, docitem_class_overview_entry, items)

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
		|Must| represent the content of an entry in section |label|`Public_types`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a list of text lines describing the public type.
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
		|Must| represent the |label|`Public_types` section.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse the content of a section |label|`Public_types`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Public_types"
	def parse(self,tr : tracer,entries : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of section |label|`Public_types`.
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
		p = self.parent()
		pos = 0
		while pos < len(entries):
			rule_id: str
			assert isinstance(p,docitem_base)
# Public_types can occur in modules and classes
			if p.is_docstring_module():
				rule_id = "MPTYP-004"
			elif p.is_docstring_class():
				rule_id = "CPTYP-004"
			else:
# Should never happen. Keep split placeholder mnemonic for consistency.
				rule_id = "MPTYP-999"
			with rule_on_fail(tr, rule_id):
				label,pos = expect_label_identifier(tr,entries,pos)
# public_types requires a list of type names
			items,pos = expect_list(tr,entries,pos)
			if p.is_docstring_module():
				rule_id = "MPTYP-006"
			else:
				rule_id = "CPTYP-006"
			with rule_on_fail(tr, rule_id):
				self.add_child(tr,label, docitem_public_types_entry, items)

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
		|Must| represent the content of an entry in section |label|`Public_assignables`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a list of text lines describing the public assignable.
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
		|Must| represent the |label|`Public_assignables` section.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse the content of a section |label|`Public_assignables`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def parse(self,tr : tracer,entries : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of section |label|`Public_assignables`.
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
		p = self.parent()
		pos = 0
		while pos < len(entries):
			rule_id: str
			assert isinstance(p,docitem_base)
# Public_types can occur in modules and classes
			if p.is_docstring_module():
				if isinstance(self,docitem_public_variables):
					rule_id = "MPVAR-004"
				else:
					rule_id = "MPCON-004"
			elif p.is_docstring_class():
				if isinstance(self,docitem_public_variables):
					rule_id = "CPVAR-004"
				else:
					rule_id = "CPCON-004"
			else:
# Should never happen. Keep split placeholder mnemonic for consistency.
				rule_id = "MPVAR-999"
			with rule_on_fail(tr, rule_id):
				label,pos = expect_label_identifier(tr,entries,pos)
# public_assignables requires a list of public_assignables function names
			items,pos = expect_list(tr,entries,pos)
			if p.is_docstring_module():
				if isinstance(self,docitem_public_variables):
					rule_id = "MPVAR-006"
				else:
					rule_id = "MPCON-007"
			else:
				if isinstance(self,docitem_public_variables):
					rule_id = "CPVAR-006"
				else:
					rule_id = "CPCON-007"
			with rule_on_fail(tr, rule_id):
				self.add_child(tr,label, docitem_public_assignables_entry, items)

class docitem_public_constants(docitem_public_assignables_base):
	def label(self) -> str:
		return "Public_constants"
class docitem_public_variables(docitem_public_assignables_base):
	def label(self) -> str:
		return "Public_variables"

#===== end section Class_overview =============================#

#===== begin section Public_<callable> ========================#

#----- docitem class method_overview ---------------------------#

# An entry for a function in section Public methods is only a brief
# description what the function is good for. Functions must be explained
# in details outside the class documentation block.
class docitem_method_overview_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the content of an entry in section |label|`Method_overview`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a list of text lines describing the public method.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "method_overview_entries"

class docitem_method_overview(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`Method_overview` section.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse the content of a section |label|`Method_overview`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Method_overview"
	def detect_partial_normativity(self,tr: tracer) -> bool:
		# True because Method_overview is always informative.
		return True
	def parse(self,tr : tracer,entries : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| parse the content of section |label|`Method_overview`.
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
			with rule_on_fail(tr, "CMTO-005"):
				label, pos = expect_label_identifier(tr, entries, pos)
# method_overview requires a list of method_overview function names
			items, pos = expect_list(tr, entries, pos)
			with rule_on_fail(tr, "CMTO-006"):
				self.add_child(tr, label, docitem_method_overview_entry, items)

#----- docitem class function_overview ---------------------------#

class docitem_function_overview_entry(docitem_free_text_entry_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the content of an entry in section |label|`Function_overview`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a list of text lines describing the public function.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "function_overview_entries"

class docitem_function_overview(docitem_map_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the |label|`Function_overview` section.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse the content of a section |label|`Function_overview`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Function_overview"
	def detect_partial_normativity(self,tr: tracer) -> bool:
		# True because Function_overview is always informative.
		return True
	def parse(self,tr : tracer,entries : DocstringSubtree) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| parse the content of section |label|`Function_overview`.
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
			with rule_on_fail(tr, "MFNO-005"):
				label,pos = expect_label_identifier(tr,entries,pos)
# function_overview requires free-form text per function entry
			items,pos = expect_list(tr,entries,pos)
			with rule_on_fail(tr, "MFNO-006"):
				self.add_child(tr,label, docitem_function_overview_entry, items)

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
Public_methods:
	parse
Method_overview:
	parse:
		Parse a list of return descriptions.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Returns"
	def parse(self,tr : tracer,lines : DocstringSubtree) -> None:
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
			found = ["Returns:"] + [f"\t{line}" for line in to_string_tree(lines).splitlines()]
			details = {
				"found": found,
				"expected": ["<do not add subsections in section Returns>"],
				"hint": "waterlint explain-section --label Returns --profile function",
			}
			raise_parsing_error_expected_but_got(tr,"RET-005","list of strings",f"{lines}", details)
		self.set_items(lines)

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
		|Must| hold free-form descriptive text lines from a docstring section |label|`Description`.
		|Must| accept and store a list of strings.
	constructor:
		|Must| be default-constructible.
Description:
	A free-form section which informatively describes the purpose
	of a module, class or callable.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a list of description lines.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Description"
	def parse(self,tr : tracer,lines : DocstringSubtree) -> None:
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
			found = ["Description:"] + [f"\t{line}" for line in to_string_tree(lines).splitlines()]
			details = {
				"found": found,
				"expected": ["<do not add subsections in section Description>"],
				"hint": "waterlint explain-section --label Description --profile PROFILE",
			}
			raise_parsing_error_expected_but_got(tr,"DESC-004","list of strings",f"{lines}", details)
		self._items = lines

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
		|Must| represent an parameter entry in the |label|`Parameters` section.
		|Must| accept and store a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse the content of a parameter entry.
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
		|Must| represent the |label|`Parameters` section.
		|Must| accept and store a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a list of parameters
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Parameters"
	def parse(self,tr : tracer,entries : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Terminology:
	Parameter entry:
		Describes a docstring subtree consisting of a string valued identifier
		and a list of free-form description lines: |type|`str, List[str]`
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
			with rule_on_fail(tr,"PAR-006"):
				label,pos = expect_label_identifier(tr,entries,pos)
			items,pos = expect_list(tr,entries,pos)
			with rule_on_fail(tr,"PAR-007"):
				self.add_child(tr,label, docitem_parameters_entry, items)

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
		|Must| represent an exception entry in the |label|`Raises` section.
		|Must| accept and store a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse the content of an exception entry.
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
		|Must| represent the |label|`Raises` section.
		|Must| accept and store a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a list of exceptions
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Raises"
	def parse(self,tr : tracer,entries : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Terminology:
	Exception entry:
		Describes a docstring subtree consisting of a string valued qualified identifier
		and a list of free-form description lines: |type|`str, List[str]`
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
			with rule_on_fail(tr, "RAI-008"):
				label,pos = expect_label_qualified_identifier(tr,entries,pos)
# factory requires a list of factory function names
			items,pos = expect_list(tr,entries,pos)
			with rule_on_fail(tr, "RAI-005"):
				self.add_child(tr,label, docitem_raises_entry, items)

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
		|Must| represent an entry in the |label|`Definitions` section.
		|Must| accept and store a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse the content of an definition entry.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "dfn"

class docitem_inherited_defitems(docitem_list_of_symbols_base):
	"""
Preamble:
	profile:
		class
	normative_sections:
		Contract, Derived_from, Public_methods
Contract:
	general:
		|Must| represent the special entry in the |label|`Definitions` section.
		|Must| accept and store a list of identifiers.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_list_of_symbols_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse the content of an inherited defitem.
	"""
	def __init__(self) -> None:
		super().__init__()
	def parse(self,tr : tracer,defitems : DocstringSubtree) -> None:
# LQID-001: list of identifiers, each one unique.
		super()._parse(tr, defitems, docitem_list_of_symbols_base.ValuePattern.IDENTIFIER)


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
		|Must| accept and store a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible
Public_methods:
	parse
Method_overview:
	parse:
		Parse a sequence of definition entries
	"""
	def __init__(self) -> None:
		super().__init__()
		self._inherited_defitems = docitem_inherited_defitems()
# This helps us to validate DEF-018 and DEF-021.
		self._map_term_to_variations: Dict[str,List[str]] = {}
	def label(self) -> str:
		return "Definitions"
	def parse(self,tr : tracer,entries : DocstringSubtree) -> None:
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
		found_inherited = False
		pos = 0
		while pos < len(entries):
			with rule_on_fail(tr,"DEF-004"):
				label,pos = expect_label_csv_identifiers(tr,entries,pos)
# DEF-010: "_inherit" is special:
			if label == "_inherit":
				if found_inherited:
# "_inherit" only once.
					details: Details = {
						"found": render_found_label("Definitions", "_inherit"),
						"expected": render_suggestion("Definitions", "one _inherit subsection only"),
						"hint": explain_try_self_for_subsection("Definitions._inherit", "class"),
					}
					raise raise_parsing_error(tr,"PRSR-008","Duplicate subsection '_inherit'.", details)
				items,pos = expect_list(tr,entries,pos)
				with traced_section(tr, "_inherit"):
					self._inherited_defitems.parse(tr,items)
				found_inherited = True
			else:
				items,pos = expect_list(tr,entries,pos)
				with rule_on_fail(tr,"DEF-006"):
					labels = list(map(str.strip,label.split(",")))
					if not labels:
						continue
					self.add_child_multilabel(tr,labels, docitem_definitions_entry, items)
					self._map_term_to_variations[labels[0]] = labels[1:]
	def inherited(self) -> List[str]:
		return self._inherited_defitems.items()
	def terms(self) -> set[str]:
		return set(self._map_term_to_variations.keys())
	def map_term_to_variations(self) -> Dict[str, List[str]]:
		return {term: vars_ for term, vars_ in self._map_term_to_variations.items()}
# Map set of terms into set of terms and variations.
	def terms_and_variations(self,terms: set[str]) -> set[str]:
		return set(sum([list(self._map_term_to_variations[term]) for term in terms],list(self._map_term_to_variations.keys())))

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
		and a list of free-form description lines: |type|`str, List[str]`
Contract:
	general:
		|Must| represent an entry in the |label|`Terminology` section.
		|Must| accept and store a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse the content of an terminology entry.
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
	A |label|`Terminology` section describes natural language expressions informatively.
	As opposed to a |label|`Definitions` section, it is never normative and does not
	contain normativity keywords.
Contract:
	general:
		|Must| represent a terminology enrty.
		|Must| accept and store a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible
Public_methods:
	parse
Method_overview:
	parse:
		Parse a sequence of terminology entries
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Terminology"
	def detect_partial_normativity(self,tr: tracer) -> bool:
		# True because Terminology is always informative.
		return True
	def parse(self,tr : tracer,entries : DocstringSubtree) -> None:
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
			with rule_on_fail(tr, "TERM-005"):
				label,pos = expect_label(tr,entries,pos)
			items,pos = expect_list(tr,entries,pos)
			with rule_on_fail(tr,"TERM-007"):
				self.add_child(tr,label, docitem_terminology_entry, items)

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
		|Must| represent the content of an entry in section |label|`Notes`.
		|Must| be able to hold a list of strings.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_free_text_entry_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse a list of text lines of the note.
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
		|Must| represent the |label|`Notes` section.
		|Must| be able to hold a map from |type|`str` to |type|`docitem_base`.
	constructor:
		|Must| be default-constructible.
Derived_from:
	docitem_map_base
Public_methods:
	parse
Method_overview:
	parse:
		Parse the content of a section |label|`Notes`.
	"""
	def __init__(self) -> None:
		super().__init__()
	def label(self) -> str:
		return "Notes"
	def detect_partial_normativity(self,tr: tracer) -> bool:
		# True because Notes is always informative.
		return True
	def parse(self,tr : tracer,entries : DocstringSubtree) -> None:
		"""
Preamble:
	profile:
		method
	normative_sections:
		Contract, Parameters, Returns, Raises
Terminology:
	Labelled note:
		A labelled note in this context is a pair |type|`str`, |type|`List[str]`.
Contract:
	general:
		|Must| parse a sequence of labelled notes.
		|Must| interpret a missing list in a labelled note as an empty list.
Parameters:
	tr:
		The tracer for collecting diagnostics.
	entries:
		The docstring subtree to parse, a sequence of labelled notes, like [|type|`str`, |type|`List`, |type|`str`, |type|`List`,...].
Returns:
	|Must| return |None|.
Raises:
	RuntimeError:
		|Must| raise if the content cannot be interpreted as a sequence of labelled notes.
		"""
		pos = 0
		while pos < len(entries):
			with rule_on_fail(tr, "PRSR-006"):
				label,pos = expect_label(tr,entries,pos)
			if label == "":
				details: Details = {
					"found": render_suggestion(None, "empty label"),
					"expected": render_suggestion(None, "a non-empty label"),
					"hint": ["Use a non-empty label."],
				}
				raise_parsing_error(tr,"NOTE-006","Label must not be empty.", details)
			items,pos = expect_list(tr,entries,pos)
			with rule_on_fail(tr, "NOTE-007"):
				self.add_child(tr,label, docitem_notes_entry, items)
