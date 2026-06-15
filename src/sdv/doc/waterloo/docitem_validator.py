from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

from sdv.doc.waterloo.docitem_helper import explain_try_self_for_section, explain_try_self_for_subsection, render_allowed_identifiers, render_expected_identifier, render_expected_snippet, render_identifier_lines, render_source_snippet, render_deduplicated_identifiers, render_normative_section_details, render_exactly_one_identifier_details, render_normativity_keyword_details, render_overview_requires_section_details, render_name_object_consistency_details, render_listed_object_missing_details, render_exception_reference_details, render_see_also_reference_details, render_scope_relation_details, render_base_method_reference_details, render_suggestion
from sdv.doc.waterloo.docitem_docstring import *

#===== Typechecking ===========================================#
try:
	from typing import TypeAliasType  # type: ignore
except Exception:  # pragma: no cover - older Python
	TypeAliasType = None

def _is_type_alias(value: object, ann: object | None) -> bool:
	if TypeAliasType is not None and isinstance(value, TypeAliasType):
		return True
	if hasattr(value, "__supertype__"):
		return True
	if getattr(value, "__module__", "") == "typing":
		return True
# Annotation hints: TypeAlias special form may be preserved as annotation
	if ann is TypeAlias:
		return True
	if isinstance(ann, str) and ann == "TypeAlias":
		return True
# Gemini suggests:
	if str(ann).endswith("TypeAlias"):
		return True
	return False


# DocitemDocstring_t = docitem_docstring_module | docitem_docstring_class | docitem_docstring_method

#===== Get properties from docitem tree =======================#

def get_status(tr: tracer, obj: object, top: docitem_docstring_base) -> str:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
	status:
		experimental
Contract:
	general:
		|Must| check for existence of a node |type|`docitem_status` in the AST passed.
		If it exists, |must| return its string-valued content.
		If it does not exist, |must| return "stable".
Parameters:
	tr:
		Tracer
	obj:
		The object to be inspected
	top:
		The AST from parsing the object docstring.
Returns:
	The documented object status or its default.
Raises:
Notes:
	Status:
		Function may be renamed soon.
	"""
	node_preamble = top.item("Preamble")
# STA-005
	if "status" not in node_preamble.items():
		return "stable"
	node_status = node_preamble.item("status")
	entries = list(node_status.items())
	if len(entries) == 0:
		details = render_exactly_one_identifier_details("Preamble.status", entries, "module")
		raise_validation_error(tr,obj,"STA-002","Subsection 'status' has not entries.", details)
	assert len(entries) == 1
	status = entries[0]
	return status

def get_profile(top: docitem_docstring_base) -> str:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
	status:
		experimental
Contract:
	general:
		|Must| check for existence of a node |type|`docitem_preamble` in the AST passed.
		|Must| check for existence of a node |type|`docitem_profile` in the preamble node.
Parameters:
	top:
		The AST to be examined
Returns:
	|Must| return the string content of the |type|`docitem_profile` node.
Raises:
	SectionNotFoundError:
		|Must| raise if |var|`top` has not item "Preamble".
	SubsectionNotFoundError:
		|Must| raise if the Preamble node has not item "profile".
Notes:
	Status:
		Function may be renamed  soon.
	"""
	if not top.has_item("Preamble"):
		raise SectionNotFoundError(f"Section 'Preamble' not found.")
	node_preamble = top.item("Preamble")
	if not node_preamble.has_item("profile"):
		raise SubsectionNotFoundError(f"Subsection 'profile' not found.")
	node_profile = cast(docitem_profile, node_preamble.item("profile"))
	return node_profile.item_by_index(0)


def resolve_object(ref: str, current_obj: object) -> tuple[object, str]:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Definitions, Contract, Parameters, Returns, Raises
Definitions:
	Identifier:
		A string matching the regular expression ``[a-zA-Z_][a-zA-Z0-9_]*``.
	Qualified_Identifier:
		A string formed by concatenating one or more Identifiers with "." as separator.
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
	AssertionError:
		|Must| relay from |mod|`importlib` while trying to import the resolved module.
	IndexError:
		|Must| relay from |mod|`importlib` while trying to import the resolved module.
	NameError:
		|Must| relay from |mod|`importlib` while trying to import the resolved module.
	NotImplementedError:
		|Must| relay from |mod|`importlib` while trying to import the resolved module.
	PermissionError:
		|Must| relay from |mod|`importlib` while trying to import the resolved module.
	SyntaxError:
		|Must| relay from |mod|`importlib` while trying to import the resolved module.
	"""
	def _import_chain(qname: str) -> object:
		parts = qname.split(".")
		last_module_error: Exception | None = None
		for i in range(len(parts), 0, -1):
			mod_cand = ".".join(parts[:i])
# We are testing candidates here like
# * path
# * path.to
# * path.to.my
# * path.to.my.module
# If the candidate fails simply because we don't resolve correctly (ImportError/ModuleNotFoundError)
# we proceed to the next candidate. If we succeed in finding the right candidate
# there might be other errors (e.g. because the module is under development).
			try:
				mod = importlib.import_module(mod_cand)
			except ModuleNotFoundError as e:
				if i == len(parts):
					last_module_error = e
				continue
# We have a module, parts [0:i]. Now let's resolve parts[i:]
# relative to this module, by means of getattr.
			attr_parts = parts[i:]
			obj_attr: object = mod
			for p in attr_parts:
				obj_attr = getattr(obj_attr, p)
			return obj_attr
# None of the candidates worked, now that is really an import error.
		if last_module_error is not None:
			raise ImportError(f"Could not import any module prefix from {qname} (1): {last_module_error}") from last_module_error
		raise ImportError(f"Could not import any module prefix from {qname} (1)")

	last_import_error: Exception | None = None
	last_import_candidate: str | None = None
	candidates: List[str] = []
	if "." in ref:
		candidates.append(ref)
	if current_obj:
# This returns the module of the object.
		mod = inspect.getmodule(current_obj)
		if mod:
			candidates.append(f"{mod.__name__}.{ref}")
		if is_obj_class(current_obj):
			candidates.append(f"{current_obj.__module__}.{current_obj.__qualname__}.{ref}")
		elif is_obj_function(current_obj):
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
# It's important to *not* abort on AttributeError,
# but we would like to see other problems from trying to
# import the module.
		except (AssertionError,IndexError,NameError,NotImplementedError,PermissionError,SyntaxError):
			raise
# We leave this here explicitly, because it is important. An AttributeError
# is perfectly normal when trying out candidates for object resolution.
		except AttributeError as e:
			continue
		except ImportError as e:
			if last_import_error is None:
				last_import_error = e
				last_import_candidate = cand
			continue
#		except Exception as e:
#			continue
	if last_import_error is not None:
		raise ImportError(
			f"Could not resolve reference '{ref}' from context '{_qualified_object_name(current_obj)}'. "
			f"Last import failure while trying '{last_import_candidate}': {last_import_error}"
		) from last_import_error
	raise ImportError(f"Could not resolve reference '{ref}' from context '{_qualified_object_name(current_obj)}'.")

def validate_docstring_module(tr : tracer, obj: object, top : docitem_docstring_module,node_contract : docitem_map_base,node_normative_sections : docitem_list_base, _seen: Dict[object,docitem_docstring_base] | None = None) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
	scope:
		extension
Contract:
	general:
		|Must| validate the docitem tree |var|`top` against the module object |var|`obj`.
		|Must| ensure that |label|`Contract` contains sections |label|`general` and |label|`api`.
		|Must| ensure that all sections declared as normative exist.
		|Must| enforce normativity/existence consistency for |label|`Class_overview`, |label|`Function_overview`, |label|`Public_types`, |label|`Public_variables`, |label|`Public_constants`:
		|Must| collect errors and warnings in the tracer object passed.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The callable object to validate against.
	top:
		The docitem tree to validate.
	node_contract:
		The node for section |label|`Contract` already parsed by the caller.
	node_normative_sections:
		The node for section |label|`Preamble.normative_sections` already parsed by the caller.
	_seen:
		Recording objects already validated in order to avoid recursion divergence and to share parsed trees across references.
Returns:
	|Must| return |None|
Raises:
	ValidationError:
		|Must| raise if any of the validation conditions listet in |label|`general` fails.
		|Must| raise if a section exists but is not listed as normative.
		|Must| raise if a section is listed as normative but does not exist.
Notes:
	Usage:
		This function is typically not called directly. Please call |func|`validate_docstring` instead.
	Last review:
		2026-01-23
	"""
	profile = get_profile(top)
	top_scope_explicit = top.has_item("Preamble") and top.item("Preamble").has_item("scope")
#===== Preamble ===============================================#
	with traced_section(tr, "Preamble"):
	# Rule: Preamble must exist. We do not allow purely informative docstrings.
		if not top.has_item("Preamble"):
			details = {
				"found": render_missing_entry_details("Preamble", top.items(), "Preamble", profile, top_level=True)["found"],
				"expected": render_missing_entry_details("Preamble", top.items(), "Preamble", profile, top_level=True)["expected"],
				"hint": render_missing_entry_details("Preamble", top.items(), "Preamble", profile, top_level=True)["hint"],
			}
			raise_validation_error(tr,obj,"PRE-001","Section 'Preamble' does not exist.", details)
#----- status -------------------------------------------------#
		node_preamble = top.item("Preamble")
		if node_preamble.has_item("status"):
			found_items = list(node_preamble.items())
			expected_items = [item for item in found_items if item != "status"]
			details = {
				"found": render_source_snippet("Preamble", found_items),
				"expected": render_expected_snippet("Preamble", expected_items),
				"hint": explain_try_self_for_section("Preamble", profile),
			}
			raise_validation_error(tr, obj, "PRE-016", f"Subsection 'status' is not allowed for profile 'module'.", details)
  
#..... normative_sections must exist ..........................#
# checked by caller
#===== Contract must exist ====================================#
# checked by caller
#----- normative_sections entries -----------------------------#
	with traced_section(tr, "normative_sections"):
		for sec_name in node_normative_sections.items():
			if sec_name not in top.items():
				details = render_normative_section_details(sec_name, node_normative_sections.items(), profile, action="remove")
				raise_validation_error(tr,obj,"PRE-012",f"Section '{sec_name}' is marked normative but does not exist.", details)
#----- general must exist -------------------------------------#
	with traced_section(tr, "Contract"):
		if "general" not in node_contract.items():
			details = render_missing_entry_details("Contract", node_contract.items(), "general", profile)
			raise_validation_error(tr,obj,"CON-022","Section 'general' does not exist.", details)

		if "api" in node_contract.items():
			node_api = node_contract._items["api"]
			with traced_section(tr, "api"):
# Rule: each entry in api must refer to a normative section
				for ref in node_api.items():
					if ref not in node_normative_sections.items():
						details = render_normative_section_details(ref, node_normative_sections.items(), profile, action="add")
						raise_validation_error(tr,obj,"PRE-011",f"Section '{ref}' is not listed in section 'Preamble.normative_sections'.", details)
# Overviews must never be normative
	with traced_section(tr, "Preamble"):
		if "Class_overview" in node_normative_sections.items():
			details = render_normative_section_details("Class_overview", node_normative_sections.items(), profile, action="remove")
			raise_validation_error(tr,obj,"MCLO-002","Section 'Class_overview' must not be listed as normative.", details)
		if "Function_overview" in node_normative_sections.items():
			details = render_normative_section_details("Function_overview", node_normative_sections.items(), profile, action="remove")
			raise_validation_error(tr,obj,"MFNO-002","Section 'Function_overview' must not be listed as normative.", details)
#===== Classes/Functions/Methods/Public_* sections ============#
	section_normativity = [
		("Public_classes", "MPCL-002"),
		("Public_functions", "MPFN-002"),
		("Public_types", "MPTYP-002"),
		("Public_variables", "MPVAR-002"),
		("Public_constants", "MPCON-002"),
		]
	for sec_name, rule_id in section_normativity:
		with traced_section(tr, sec_name):
			if sec_name in top.items() and sec_name not in node_normative_sections.items():
				details = render_normative_section_details(sec_name, node_normative_sections.items(), profile, action="add")
				raise_validation_error(tr,obj,rule_id, f"Section '{sec_name}' exists but is not listed as normative.", details)
			if sec_name in node_normative_sections.items() and sec_name not in top.items():
				details = render_normative_section_details(sec_name, node_normative_sections.items(), profile, action="remove")
				raise_validation_error(tr,obj,"PRE-012",f"Section '{sec_name}' is marked normative but does not exist.", details)
#----- Public classes -----------------------------------------#
	with traced_section(tr, "Public_classes"):
		if "Public_classes" in top.items():
			node_pc = top._items["Public_classes"]
			for cls_name in node_pc.items():
				if not hasattr(obj, cls_name):
					details = render_listed_object_missing_details("Public_classes", cls_name, "<remove entry or implement matching class>", profile)
					raise_validation_error(tr, obj, "MPCL-004", f"Class '{cls_name}' listed in Public_classes has no matching object.", details)
				attr = getattr(obj, cls_name)
				if not is_obj_class(attr):
					details = render_name_object_consistency_details("Public_classes", node_pc.items(), profile)
					raise_validation_error(tr, obj, "MPCL-005", f"Entry '{cls_name}' is not a class.", details)
#----- Public functions ---------------------------------------#
	with traced_section(tr, "Public_functions"):
		if "Public_functions" in top.items():
			node_pf = top._items["Public_functions"]
			for func_name in node_pf.items():
				if not hasattr(obj, func_name):
					details = render_listed_object_missing_details("Public_functions", func_name, "<remove entry or implement matching object>", profile)
					raise_validation_error(tr, obj, "MPFN-004", f"Function '{func_name}' listed in Public_functions has no matching object.", details)
				attr = getattr(obj, func_name)
				if not is_obj_function(attr):
					details = render_name_object_consistency_details("Public_functions", node_pf.items(), profile)
					raise_validation_error(tr, obj, "MPFN-005", f"Entry '{func_name}' is not a function.", details)

#----- Class overview -----------------------------------------#
	with traced_section(tr, "Class_overview"):
		if "Class_overview" in top.items():
			if "Public_classes" not in top.items():
				details = render_overview_requires_section_details("Class_overview", "Public_classes", profile)
				raise_validation_error(tr, obj, "MCLO-003",f"'Class_overview' requires section 'Public_classes'.", details)
			node_co = top._items["Class_overview"]
			node_pc = top._items["Public_classes"]
			for cls_name in node_co.items():
				if not hasattr(obj, cls_name):
					details = render_missing_entry_details("Class_overview", node_co.items(), cls_name, profile)
					raise_validation_error(tr, obj, "MCLO-008", f"Entry '{cls_name}' does not exist on module.", details)
				attr = getattr(obj, cls_name)
				if not is_obj_class(attr):
					details = render_name_object_consistency_details("Class_overview", node_co.items(), profile, overview_item=cls_name)
					raise_validation_error(tr, obj, "MCLO-009", f"Entry '{cls_name}' is not a class.", details)
				if not node_pc.has_item(cls_name):
					details = render_overview_missing_member_details("Class_overview", "Public_classes", node_co.items(), cls_name, profile)
					raise_validation_error(tr, obj, "MCLO-011", f"Entry '{cls_name}' is not found in section 'Public_classes'.", details)
#----- ensure SSoT principle ----------------------------------#
			for cls_name in node_co.items():
				cls_node = node_co.item(cls_name)
				if cls_node.has_norm_keywords():
					details = render_normativity_keyword_details("Class_overview", cls_name, cls_node.items(), "don't use normativity keyword, give a brief informative description instead", profile)
					raise_validation_error(tr, obj, "MCLO-007", f"Entry '{cls_name}' in Class_overview must not contain normativity keywords; content is informational only.", details)

#----- Function overview --------------------------------------#
	with traced_section(tr, "Function_overview"):
		if "Function_overview" in top.items():
			if "Public_functions" not in top.items():
				details = render_overview_requires_section_details("Function_overview", "Public_functions", profile)
				raise_validation_error(tr, obj, "MFNO-003",f"'Function_overview' requires section 'Public_functions'.", details)
			node_fo = top._items["Function_overview"]
			node_pf = top._items["Public_functions"]
			for fn_name in node_fo.items():
				if not hasattr(obj, fn_name):
					details = render_missing_entry_details("Function_overview", node_fo.items(), fn_name, profile)
					raise_validation_error(tr, obj, "MFNO-008", f"Entry '{fn_name}' does not exist on module.", details)
				attr = getattr(obj, fn_name)
				if not is_obj_function(attr):
					details = render_name_object_consistency_details("Function_overview", node_fo.items(), profile, overview_item=fn_name)
					raise_validation_error(tr, obj, "MFNO-009", f"Entry '{fn_name}' is not a function.", details)
				if not node_pf.has_item(fn_name):
					details = render_name_object_consistency_details("Function_overview", node_fo.items(), profile, overview_item=fn_name)
					raise_validation_error(tr, obj, "MFNO-011", f"Entry '{fn_name}' is not found in section 'Public_functions'.", details)
#----- ensure SSoT principle ----------------------------------#
			for fn_name in node_fo.items():
				fn_node = node_fo.item(fn_name)
				if fn_node.has_norm_keywords():
					details = render_normativity_keyword_details("Function_overview", fn_name, fn_node.items(), "don't use normativity keyword, give a brief informative description instead", profile)
					raise_validation_error(tr, obj, "MFNO-007", f"Entry '{fn_name}' in Function_overview must not contain normativity keywords; content is informational only.", details)

#----- Public types -------------------------------------------#
	with traced_section(tr, "Public_types"):
		if "Public_types" in top.items():
			node_pt = top._items["Public_types"]
			ann = get_obj_annotations(obj)
			for ty_name in node_pt.items():
				if not hasattr(obj, ty_name):
					details = render_listed_object_missing_details("Public_types", ty_name, "<remove entry or implement matching type alias>", profile)
					raise_validation_error(tr, obj, "MPTYP-005", f"Type '{ty_name}' listed in Public_types has no matching object.", details)
				attr = getattr(obj, ty_name)
				ann_val = ann.get(ty_name, None) if isinstance(ann, dict) else None
				if not _is_type_alias(attr, ann_val):
					details = render_type_reference_details("Public_types", ty_name, "<declare a TypeAlias or NewType>", profile)
					raise_validation_error(tr, obj, "MPTYP-008", f"Entry '{ty_name}' is not a TypeAlias/NewType.", details)

#----- Public variables ---------------------------------------#
	with traced_section(tr, "Public_variables"):
		if "Public_variables" in top.items():
			node_pv = top._items["Public_variables"]
			for var_name in node_pv.items():
				if not hasattr(obj, var_name):
					details = render_listed_object_missing_details("Public_variables", var_name, "<remove entry or implement matching named value>", profile)
					raise_validation_error(tr, obj, "MPVAR-005", f"Named value '{var_name}' listed in Public_variables has no matching object.", details)
				attr = getattr(obj, var_name)
				if not is_obj_named_value(attr):
					details = render_named_value_reference_details("Public_variables", var_name, "<refer to a named value, not callable/class>", "module")
					raise_validation_error(tr, obj, "MPVAR-008", f"Entry '{var_name}' must refer to a named value, not callable/class.", details)

#----- Public constants ---------------------------------------#
	with traced_section(tr, "Public_constants"):
		if "Public_constants" in top.items():
			node_pcst = top._items["Public_constants"]
			ann = get_obj_annotations(obj)
			for const_name in node_pcst.items():
				if not hasattr(obj, const_name):
					details = render_listed_object_missing_details("Public_constants", const_name, "<remove entry or implement matching named value>", profile)
					raise_validation_error(tr, obj, "MPCON-005", f"Named value '{const_name}' listed in Public_constants has no matching object.", details)
				attr = getattr(obj, const_name)
				if not is_obj_named_value(attr):
					details = render_named_value_reference_details("Public_constants", const_name, "<refer to a named value, not callable/class>", profile)
					raise_validation_error(tr, obj, "MPCON-009", f"Entry '{const_name}' must refer to a named value, not callable/class.", details)
				if const_name in ann and not is_attr_final(cast(ModuleType | type, obj), const_name):
					details = render_constant_reference_details("Public_constants", const_name, "<annotate the constant as Final; don't forget to import Final from typing>", profile)
					raise_validation_error(tr, obj, "MPCON-006", f"Constant '{const_name}' is annotated but not Final.", details)

#===== Scope Monotonicity Rules ===============================#
# Internal references from Public_classes / Public_functions must be compatible.
	top_scopes = top.scopes()
	top_scope_explicit = top.has_item("Preamble") and top.item("Preamble").has_item("scope")
#----- Public classes -----------------------------------------#
	if "Public_classes" in top.items():
		node_classes = top.item("Public_classes")
		for ref_name in node_classes.items():
			try:
				ref_obj, _ = resolve_object(ref_name, obj)
			except Exception:
# Cannot resolve object? Not good, but must be handled elsewhere.
				continue
			tr_tmp = tracer()
			doc = get_obj_docstring(ref_obj)
			if not doc:
# Class has no docstring? Do not test scope rule.
				continue
			try:
				tree = parse_indent_docstring(tr_tmp, doc)
				scopes, ref_scope_explicit = get_scopes_of_tree_var(tr_tmp, tree)
			except (ParseError, SectionNotFoundError):
# Cannot extract scope from docstring? Do not test scope rule.
				continue
			if not top.is_visible(scopes):
				details = render_scope_relation_details("module", top_scopes, top_scope_explicit, "class", scopes, ref_scope_explicit, "Public_classes", ref_name, "<reconsider the scopes of the module and the referenced class>", "module")
				raise_validation_error(tr, obj, "SCP-005", f"Reconsider the scopes of the module and the referenced class '{ref_name}'.", details)
#----- Public functions ---------------------------------------#
	if "Public_functions" in top.items():
		node_functions = top.item("Public_functions")
		for ref_name in node_functions.items():
			try:
				ref_obj, _ = resolve_object(ref_name, obj)
			except Exception:
# Cannot resolve object? Not good, but must be handled elsewhere.
				continue
			tr_tmp = tracer()
			doc = get_obj_docstring(ref_obj)
			if not doc:
# Function has no docstring? Do not test scope rule.
				continue
			try:
				tree = parse_indent_docstring(tr_tmp, doc)
				scopes, ref_scope_explicit = get_scopes_of_tree_var(tr_tmp, tree)
			except (ParseError, SectionNotFoundError):
# Cannot extract scope from docstring? Do not test scope rule.
				continue
			if not top.is_visible(scopes):
				details = render_scope_relation_details("module", top_scopes, top_scope_explicit, "function", scopes, ref_scope_explicit, "Public_functions", ref_name, "<reconsider the scopes of the module and the referenced function>", "module")
				raise_validation_error(tr, obj, "SCP-005", f"Reconsider the scopes of the module and the referenced function '{ref_name}'.", details)

def validate_docstring_class(tr : tracer, obj: object, top : docitem_docstring_class,node_contract : docitem_map_base,node_normative_sections : docitem_list_base, _seen: Dict[object,docitem_docstring_base] | None = None) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
	scope:
		extension
Contract:
	general:
		|Must| validate the docitem tree |var|`top` against the class object |var|`obj`.
		|Must| ensure that sections |label|`general`, |label|`constructor`, |label|`api` exist. 
		|Must| ensure that each section listed in |label|`api` is normative.
		|Must| ensure that subsection |label|`traits` -- if exists -- contains only allowed values and no duplicates.
		|Must| ensure that section |label|`Derived_from` exists if listed in |label|`normative_sections`.
		|Must| ensure that each entry in |label|`Derived_from` is a base class of |var|`obj`|op|`\\.`|var|`__class__`.
		|Must| enforce normativity/existence consistency for |label|`Class_overview`, |label|`Method_overview`, |label|`Public_variables`, |label|`Public_constants`:
		|Must| collect errors and warnings in the tracer object passed.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The callable object to validate against.
	top:
		The docitem tree to validate.
	node_contract:
		The node for section |label|`Contract` already parsed by the caller.
	node_normative_sections:
		The node for section |label|`Preamble.normative_sections` already parsed by the caller.
	_seen:
		Recording objects already validated in order to avoid recursion divergence and to share parsed trees across references.
Returns:
	|Must| return |None|
Raises:
	ValidationError:
		|Must| raise if any of the validation conditions listet in |label|`general` fails.
		|Must| raise if a section exists but is not listed as normative.
		|Must| raise if a section is listed as normative but does not exist.
Notes:
	Usage:
		This function is typically not called directly. Please call |func|`validate_docstring` instead.
	Last review:
		2026-01-23
	"""
	profile = get_profile(top)
	top_scope_explicit = top.has_item("Preamble") and top.item("Preamble").has_item("scope")
#===== Preamble ===============================================#
	with traced_section(tr, "Preamble"):
# Rule: Preamble must exist. We do not allow purely informative docstrings.
		if not top.has_item("Preamble"):
			details = {
				"found": render_missing_entry_details("Preamble", top.items(), "Preamble", profile, top_level=True)["found"],
				"expected": render_missing_entry_details("Preamble", top.items(), "Preamble", profile, top_level=True)["expected"],
				"hint": render_missing_entry_details("Preamble", top.items(), "Preamble", profile, top_level=True)["hint"],
			}
			raise_validation_error(tr,obj,"PRE-001","Section 'Preamble' does not exist.", details)
#----- status -------------------------------------------------#
		node_preamble = top.item("Preamble")
		if node_preamble.has_item("status"):
			found_items = list(node_preamble.items())
			expected_items = [item for item in found_items if item != "status"]
			details = {
				"found": render_source_snippet("Preamble", found_items),
				"expected": render_expected_snippet("Preamble", expected_items),
				"hint": explain_try_self_for_section("Preamble", profile),
			}
			raise_validation_error(tr, obj, "PRE-016", f"Subsection 'status' is not allowed for profile 'class'.", details)
#..... profile must exist .....................................#
# checked by caller
#..... normative_sections must exist ..........................#
# checked by caller

#----- normative_sections entries -----------------------------#
	with traced_section(tr, "normative_sections"):
		for sec_name in node_normative_sections.items():
			if sec_name not in top.items():
				details = render_normative_section_details(sec_name, node_normative_sections.items(), profile, action="remove")
				raise_validation_error(tr,obj,"PRE-012",f"Section '{sec_name}' is marked normative but does not exist.", details)

#===== Contract must exist ====================================#
# checked by caller
#----- general, constructor must exist ------------------------#
	with traced_section(tr, "Contract"):
		if "general" not in node_contract.items():
			details = {
				"found": render_source_snippet("Contract", node_contract.items()),
				"expected": render_expected_snippet("Contract", [*node_contract.items(), "general"]),
				"hint": explain_try_self_for_subsection("Contract.general", "class"),
			}
			raise_validation_error(tr, obj, "CON-023", "Subsection 'general' does not exist.", details)
		if "constructor" not in node_contract.items():
			details = {
				"found": render_source_snippet("Contract", node_contract.items()),
				"expected": render_expected_snippet("Contract", [*node_contract.items(), "constructor"]),
				"hint": explain_try_self_for_subsection("Contract.constructor", "class"),
			}
			raise_validation_error(tr, obj, "CON-007", "Subsection 'constructor' does not exist.", details)
#----- traits -------------------------------------------------#
		if "traits" in node_contract.items():
			node_traits = node_contract._items["traits"]
			with traced_section(tr, "traits"):
				traits = list(node_traits.items())
#..... no duplicates allowed ..................................#
# This is most likely captured by the parser, but we check just in case.
				if len(traits) != len(set(traits)):
					seen_traits : set[str] = set()
					dup_trait = traits[-1] if traits else "trait"
					for name in traits:
						if name in seen_traits:
							dup_trait = name
							break
						seen_traits.add(name)
					details = {
						"found": render_identifier_lines("Contract.traits", traits),
						"expected": render_deduplicated_identifiers("Contract.traits", traits),
						"hint": explain_try_self_for_subsection("Contract.traits", "class"),
					}
					raise_validation_error(tr, obj, "LQID-004", f"Trait identifier '{dup_trait}' occurs more than once.", details)
#..... only allowed values ....................................#
				for tr_name in traits:
					if tr_name not in TRAIT_TAG_MAP:
						details = {
							"found": render_identifier_lines("Contract.traits", traits),
							"expected": render_allowed_identifiers("Contract.traits", sorted(TRAIT_TAG_MAP.keys())),
							"hint": explain_try_self_for_subsection("Contract.traits", "class"),
						}
						raise_validation_error(tr, obj, "CON-017", f"Trait '{tr_name}' is not allowed; allowed: {sorted(TRAIT_TAG_MAP.keys())}", details)
#===== Derived_from must exist if normative ===================#
	with traced_section(tr, "Derived_from"):
		normative_sections = list(node_normative_sections.items())
		if "Derived_from" in node_normative_sections.items():
			if "Derived_from" not in top.items():
				expected_sections = [item for item in normative_sections if item != "Derived_from"]
				details = {
					"found": render_identifier_lines("Preamble.normative_sections", normative_sections),
					"expected": render_deduplicated_identifiers("Preamble.normative_sections", expected_sections),
					"hint": explain_try_self_for_section("Derived_from", "class"),
				}
				raise_validation_error(tr,obj,"PRE-012","Section 'Derived_from' is marked normative but does not exist.", details)
# If Derived_from present...
		if top.has_item("Derived_from"):
			node_derived = top.item("Derived_from")
# ...must be normative.
			if "Derived_from" not in node_normative_sections.items():
				expected_sections = [*normative_sections, "Derived_from"]
				details = {
					"found": render_identifier_lines("Preamble.normative_sections", normative_sections),
					"expected": render_deduplicated_identifiers("Preamble.normative_sections", expected_sections),
					"hint": explain_try_self_for_section("Derived_from", "class"),
				}
				raise_validation_error(tr,obj,"DER-004",f"Section 'Derived_from' is not listed in section 'Preamble.normative_sections'.", details)
# ...entries must refer to direct base classes, but may do so using either
# short or qualified names. We accept the canonical name of each direct base,
# its qualname, and its fully qualified name.
			base_objs = tuple(getattr(obj, "__bases__", ()))
			base_desc = [get_obj_fully_qualified_name(b) for b in base_objs]
			base_aliases: Dict[str, set[object]] = {}
			for base_obj in base_objs:
				for alias in (
					getattr(base_obj, "__name__", ""),
					getattr(base_obj, "__qualname__", ""),
					get_obj_fully_qualified_name(base_obj),
				):
					if alias:
						base_aliases.setdefault(alias, set()).add(base_obj)
			for bname in node_derived.items():
				matches = base_aliases.get(bname, set())
				if len(matches) == 1:
					continue
				if len(matches) > 1:
					details = {
						"found": render_identifier_lines("Derived_from", [bname]),
						"expected": render_allowed_identifiers("Derived_from", base_desc),
						"hint": explain_try_self_for_subsection("Derived_from", "class"),
					}
					raise_validation_error(tr,obj,"DER-013",f"Entry '{bname}' is ambiguous; please qualify it enough to resolve one of {base_desc}.", details)
				try:
					resolved_obj, _ = resolve_object(bname, obj)
				except Exception:
					resolved_obj = None
				if resolved_obj in base_objs:
					continue
				details = {
					"found": render_identifier_lines("Derived_from", [bname]),
					"expected": render_allowed_identifiers("Derived_from", base_desc),
					"hint": explain_try_self_for_subsection("Derived_from", "class"),
				}
				raise_validation_error(tr,obj,"DER-003",f"Class '{bname}' is not a direct base; direct bases are {base_desc}.", details)
#===== Classes/Functions/Methods/Public_* sections ============#
	section_normativity = [
		("Public_classes", "CPCL-002"),
		("Public_methods", "CPMT-002"),
		("Public_types", "CPTYP-002"),
		("Public_variables", "CPVAR-002"),
		("Public_constants", "CPCON-002"),
		]
	for sec_name, rule_id in section_normativity:
		with traced_section(tr, sec_name):
			if sec_name in top.items() and sec_name not in node_normative_sections.items():
				details = render_normative_section_details(sec_name, node_normative_sections.items(), profile, action="add")
				raise_validation_error(tr,obj,rule_id, f"Section '{sec_name}' exists but is not listed as normative.", details)
			if sec_name in node_normative_sections.items() and sec_name not in top.items():
				details = render_normative_section_details(sec_name, node_normative_sections.items(), profile, action="remove")
				raise_validation_error(tr,obj,"PRE-012",f"Section '{sec_name}' is marked normative but does not exist.", details)
# Overviews must never be normative
	with traced_section(tr, "Preamble"):
		if "Class_overview" in node_normative_sections.items():
			details = render_normative_section_details("Class_overview", node_normative_sections.items(), profile, action="remove")
			raise_validation_error(tr,obj,"CCLO-002","Section 'Class_overview' must not be listed as normative.", details)
		if "Method_overview" in node_normative_sections.items():
			details = render_normative_section_details("Method_overview", node_normative_sections.items(), profile, action="remove")
			raise_validation_error(tr,obj,"CMTO-002","Section 'Method_overview' must not be listed as normative.", details)
#----- Public classes -----------------------------------------#
	with traced_section(tr, "Public_classes"):
		if "Public_classes" in top.items():
			node_pc = top._items["Public_classes"]
			for cls_name in node_pc.items():
				if not hasattr(obj, cls_name):
					details = render_listed_object_missing_details("Public_classes", cls_name, "<remove entry or implement matching nested class>", profile)
					raise_validation_error(tr, obj, "CPCL-004", f"Class '{cls_name}' listed in Public_classes has no matching object.", details)
				attr = getattr(obj, cls_name)
				if not is_obj_class(attr):
					details = render_name_object_consistency_details("Public_classes", node_pc.items(), profile)
					raise_validation_error(tr, obj, "CPCL-005", f"Entry '{cls_name}' is not a class.", details)
#----- Public methods -----------------------------------------#
	with traced_section(tr, "Public_methods"):
		if "Public_methods" in top.items():
			node_pm = top._items["Public_methods"]
			for meth_name in node_pm.items():
				if not hasattr(obj, meth_name):
					details = render_listed_object_missing_details("Public_methods", meth_name, "<remove entry or implement matching method>", profile)
					raise_validation_error(tr, obj, "CPMT-004", f"Method '{meth_name}' listed in Public_methods has no matching object.", details)
				attr = getattr(obj, meth_name)
				if not is_obj_function(attr):
					details = render_name_object_consistency_details("Public_methods", node_pm.items(), profile)
					raise_validation_error(tr, obj, "CPMT-005", f"Entry '{meth_name}' is not a method.", details)

#----- Class overview -----------------------------------------#
	with traced_section(tr, "Class_overview"):
		if "Class_overview" in top.items():
			if "Public_classes" not in top.items():
				details = render_overview_requires_section_details("Class_overview", "Public_classes", profile)
				raise_validation_error(tr, obj, "CCLO-003",f"'Class_overview' requires section 'Public_classes'.", details)
			node_co = top._items["Class_overview"]
			node_pm = top._items["Public_classes"]
			for cls_name in node_co.items():
				if not hasattr(obj, cls_name):
					details = render_missing_entry_details("Class_overview", node_co.items(), cls_name, profile)
					raise_validation_error(tr, obj, "CCLO-008", f"Entry '{cls_name}' does not exist on class.", details)
				attr = getattr(obj, cls_name)
				if not is_obj_class(attr):
					details = render_name_object_consistency_details("Class_overview", node_co.items(), profile, overview_item=cls_name)
					raise_validation_error(tr, obj, "CCLO-009", f"Entry '{cls_name}' is not a class.", details)
				if not node_pm.has_item(cls_name):
					details = render_overview_missing_member_details("Class_overview", "Public_classes", node_co.items(), cls_name, profile)
					raise_validation_error(tr, obj, "CCLO-011", f"Entry '{cls_name}' is not found in section 'Public_classes'.", details)
#----- ensure SSoT principle ----------------------------------#
			for cls_name in node_co.items():
				cls_node = node_co.item(cls_name)
				if cls_node.has_norm_keywords():
					details = render_normativity_keyword_details("Class_overview", cls_name, cls_node.items(), "don't use normativity keyword, give a brief informative description instead", profile)
					raise_validation_error(tr, obj, "CCLO-007", f"Entry '{cls_name}' in Class_overview must not contain normativity keywords; content is informational only.", details)

#----- Method overview ----------------------------------------#
	with traced_section(tr, "Method_overview"):
		if "Method_overview" in top.items():
			if "Public_methods" not in top.items():
				details = render_overview_requires_section_details("Method_overview", "Public_methods", profile)
				raise_validation_error(tr, obj, "CMTO-003",f"'Method_overview' requires section 'Public_methods'.", details)
			node_mo = top._items["Method_overview"]
			node_pm = top._items["Public_methods"]
			for m_name in node_mo.items():
				if not hasattr(obj, m_name):
					details = render_missing_entry_details("Method_overview", node_mo.items(), m_name, profile)
					raise_validation_error(tr, obj, "CMTO-008", f"Entry '{m_name}' does not exist on class.", details)
				attr = getattr(obj, m_name)
				if not is_obj_function(attr):
					details = render_name_object_consistency_details("Method_overview", node_mo.items(), profile, overview_item=m_name)
					raise_validation_error(tr, obj, "CMTO-009", f"Entry '{m_name}' is not a method.", details)
				if not node_pm.has_item(m_name):
					details = render_name_object_consistency_details("Method_overview", node_mo.items(), profile, overview_item=m_name)
					raise_validation_error(tr, obj, "CMTO-011", f"Entry '{m_name}' is not found in section 'Public_methods'.", details)
#----- ensure SSoT principle ----------------------------------#
			for m_name in node_mo.items():
				m_node = node_mo.item(m_name)
				if m_node.has_norm_keywords():
					details = render_normativity_keyword_details("Method_overview", m_name, m_node.items(), "don't use normativity keyword, give a brief informative description instead", profile)
					raise_validation_error(tr, obj, "CMTO-007", f"Entry '{m_name}' in Method_overview must not contain normativity keywords; content is informational only.", details)

#----- Public types -------------------------------------------#
	with traced_section(tr, "Public_types"):
		if "Public_types" in top.items():
			node_pt = top._items["Public_types"]
			ann = get_obj_annotations(obj)
			for ty_name in node_pt.items():
				if not hasattr(obj, ty_name):
					details = render_listed_object_missing_details("Public_types", ty_name, "<remove entry or implement matching type alias>", profile)
					raise_validation_error(tr, obj, "CPTYP-005", f"Type '{ty_name}' listed in Public_types has no matching object.", details)
				attr = getattr(obj, ty_name)
				ann_val = ann.get(ty_name, None) if isinstance(ann, dict) else None
				if not _is_type_alias(attr, ann_val):
					details = render_type_reference_details("Public_types", ty_name, "<remove entry or declare a TypeAlias or NewType>", profile)
					raise_validation_error(tr, obj, "CPTYP-008", f"Entry '{ty_name}' is not a TypeAlias/NewType.", details)

#----- Public variables ---------------------------------------#
	with traced_section(tr, "Public_variables"):
		if "Public_variables" in top.items():
			node_pv = top._items["Public_variables"]
			for var_name in node_pv.items():
				if not hasattr(obj, var_name):
					details = render_listed_object_missing_details("Public_variables", var_name, "<remove entry or implement matching named value>", profile)
					raise_validation_error(tr, obj, "CPVAR-005", f"Named value '{var_name}' listed in Public_variables has no matching object.", details)
				attr = getattr(obj, var_name)
				if not is_obj_named_value(attr):
					details = render_name_object_consistency_details("Public_variables", node_pv.items(), profile, overview_item=var_name)
					raise_validation_error(tr, obj, "CPVAR-008", f"Entry '{var_name}' must refer to a named value, not callable/class.", details)

#----- Public constants ---------------------------------------#
	with traced_section(tr, "Public_constants"):
		if "Public_constants" in top.items():
			node_pcst = top._items["Public_constants"]
			ann = get_obj_annotations(obj)
			for const_name in node_pcst.items():
				if not hasattr(obj, const_name):
					details = render_listed_object_missing_details("Public_constants", const_name, "<remove entry or implement matching named value>", profile)
					raise_validation_error(tr, obj, "CPCON-005", f"Named value '{const_name}' listed in Public_constants has no matching object.", details)
				attr = getattr(obj, const_name)
				if not is_obj_named_value(attr):
					details = render_name_object_consistency_details("Public_constants", node_pcst.items(), profile, overview_item=const_name)
					raise_validation_error(tr, obj, "CPCON-009", f"Entry '{const_name}' must refer to a named value, not callable/class.", details)
				if const_name in ann and not is_attr_final(cast(ModuleType | type, obj), const_name):
					details = render_name_object_consistency_details("Public_constants", node_pcst.items(), profile, overview_item=const_name)
					raise_validation_error(tr, obj, "CPCON-006", f"Constant '{const_name}' is annotated but not Final.", details)


#===== Scope Monotonicity Rules ===============================#
	top_scopes = top.scopes()
#----- Public classes -----------------------------------------#
	if "Public_classes" in top.items():
		node_classes = top.item("Public_classes")
		for ref_name in node_classes.items():
			try:
				ref_obj, _ = resolve_object(ref_name, obj)
			except Exception:
# Cannot resolve object? Not good, but must be handled elsewhere.
				continue
			tr_tmp = tracer()
			doc = get_obj_docstring(ref_obj)
			if not doc:
# Class has no docstring? Do not test scope rule.
				continue
			try:
				tree = parse_indent_docstring(tr_tmp, doc)
				scopes, ref_scope_explicit = get_scopes_of_tree_var(tr_tmp, tree)
			except (ParseError, SectionNotFoundError):
# Cannot extract scope from docstring? Do not test scope rule.
				continue
			if not top.is_visible(scopes):
				details = render_scope_relation_details("class", top_scopes, top_scope_explicit, "class", scopes, ref_scope_explicit, "Public_classes", ref_name, "<reconsider the scopes of the containing class and the referenced class>", "class")
				raise_validation_error(tr, obj, "SCP-005", f"Reconsider the scopes of the containing class and the referenced class '{ref_name}'.", details)
#----- Public methods ---------------------------------------#
	if "Public_methods" in top.items():
		node_methods = top.item("Public_methods")
		for ref_name in node_methods.items():
			try:
				tr.add_info(f"resolving {ref_name} in {get_obj_name(obj)}.")
				ref_obj, _ = resolve_object(ref_name, obj)
				tr.add_info(f"done.")
			except Exception as e:
				tr.add_info(f"failed.")
				print(e)
# Cannot resolve object? Not good, but must be handled elsewhere.
				continue
			tr_tmp = tracer()
			doc = get_obj_docstring(ref_obj)
			if not doc:
# Class has no docstring? Do not test scope rule.
				continue
			try:
				tree = parse_indent_docstring(tr_tmp, doc)
				scopes, ref_scope_explicit = get_scopes_of_tree_var(tr_tmp, tree)
			except (ParseError, SectionNotFoundError):
# Cannot extract scope from docstring? Do not test scope rule.
				continue
			if not top.is_visible(scopes):
				details = render_scope_relation_details("class", top_scopes, top_scope_explicit, "method", scopes, ref_scope_explicit, "Public_methods", ref_name, "<reconsider the scopes of the containing class and the referenced method>", "class")
				raise_validation_error(tr, obj, "SCP-005", f"Reconsider the scopes of the containing class and the referenced method '{ref_name}'.", details)
#----- Derived_from -------------------------------------------#
	drvd_scopes = top_scopes
	if "Derived_from" in top.items():
		node_derived_from = top.item("Derived_from")
		for base_name in node_derived_from.items():
			try:
				base_obj, _ = resolve_object(base_name, obj)
			except Exception:
# Cannot resolve object? Not good, but must be handled elsewhere.
				continue
			tr_tmp = tracer()
			doc = get_obj_docstring(base_obj)
			if not doc:
# Class has no docstring? Do not test scope rule.
				continue
			try:
				tree = parse_indent_docstring(tr_tmp, doc)
				base_scopes, base_scope_explicit = get_scopes_of_tree_var(tr_tmp, tree)
			except (ParseError, SectionNotFoundError):
# Cannot extract scope from docstring? Do not test scope rule.
				continue
			if not top.can_see(base_scopes):
				details = render_scope_relation_details("class", top_scopes, top_scope_explicit, "class", base_scopes, base_scope_explicit, "Derived_from", base_name, "<reconsider the scopes of the derived class and its base class>", "class")
				raise_validation_error(tr, obj, "SCP-009", f"Reconsider the scopes of the derived class and its base class '{base_name}'.", details)
#----- Factory ------------------------------------------------#
	with traced_section(tr, "Factory"):
		if "Factory" in top.items():
			node_factory = top.item("Factory")
			for item in node_factory.items():
				try:
					obj_factory, _ = resolve_object(item, obj)
				except Exception:
					details = {
						"found": render_identifier_lines("Factory", [item]),
						"expected": render_suggestion("Factory", "refer to an existing callable"),
						"hint": explain_try_self_for_subsection(f"'Factory.<item>'", "class"),
					}
					raise_validation_error(tr, obj, "FAC-006", f"Factory entry '{item}' does not resolve to an existing callable.", details)
# ...must be normative.
			if "Factory" not in node_normative_sections.items():
				details = render_normative_section_details("Factory", node_normative_sections.items(), profile, action="add")
				raise_validation_error(tr,obj,"FAC-009",f"Section 'Factory' is not listed as normative.", details)

def validate_docstring_method(tr : tracer, obj: Callable[..., Any], top : docitem_docstring_method,node_contract : docitem_map_base,node_normative_sections : docitem_list_base, _seen: Dict[object,docitem_docstring_base] | None = None) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
	scope:
		extension
Contract:
	general:
		|Must| validate the docitem tree |var|`top` against the callable object |var|`obj`.
		|Must| ensure that |label|`Contract` contains a section |label|`general`.
		|Must| ensure that all sections declared as normative exist.
		|Must| ensure that section |label|`Parameters` exists.
		|Must| ensure that section |label|`Returns` exists.
		|Must| ensure that section |label|`Raises` exists.
		|Must| ensure that each parameter mentioned in section |label|`Parameters` is in the callable's signature.
		|Must| ensure that each parameter in the callable's signature is mentioned in section |label|`Parameters`.
		|Must| ensure that each exception listed in section |label|`Raises` refers to an existing class.
		|Must| ensure that each exception listed in section |label|`Raises` is a subclass of |type|`BaseException`.
		|Must| resolve each exception listed in section |label|`Raises` by importing the longest module prefix and traversing remaining attributes; |must| fall back to the callable's globals, its defining module, and |value|`builtins`.
		|Must| collect warnings in the tracer object passed.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The callable object to validate against.
	top:
		The docitem tree to validate.
	node_contract:
		The node for section |label|`Contract` already parsed by the caller.
	node_normative_sections:
		The node for section |label|`Preamble.normative_sections` already parsed by the caller.
	_seen:
		Recording objects already validated in order to avoid recursion divergence and to share parsed trees across references.
Returns:
	|Must| return |None|
Raises:
	ValidationError:
		|Must| raise if any of the validation conditions listet in |label|`general` fails.
Notes:
	Usage:
		This function is typically not called directly. Please call |func|`validate_docstring` instead.
	"""
	profile = get_profile(top)
	with traced_section(tr, "method"):
#===== Preamble ===============================================#
		with traced_section(tr, "Preamble"):
			node_preamble = top.item("Preamble")
#----- status -------------------------------------------------#
			with traced_section(tr, "status"):

				if "status" not in node_preamble.items():
					status = "stable"
				else:
					node_status = node_preamble.item("status")
					entries = list(node_status.items())
					if len(entries) != 1:
						details = render_exactly_one_identifier_details("Preamble.status", entries, profile)
						raise_validation_error(tr,obj,"STA-002","Subsection 'status' must have exactly one entry.", details)
					status = entries[0]
# Won't trigger most likely; handled during parsing.
				if not RE_IDENTIFIER_COMPILED.fullmatch(status):
					details = {
						"found": render_identifier_lines("Preamble.status", [status]),
						"expected": render_expected_identifier("Preamble.status", "identifier"),
						"hint": explain_try_self_for_subsection("Preamble.status", profile),
					}
					raise_validation_error(tr,obj,"STA-003","Subsection 'status' must be an Identifier.", details)
				if status not in STATUS_TAG_MAP:
					details = {
						"found": render_identifier_lines("Preamble.status", [status]),
						"expected": render_allowed_identifier("Preamble.status", sorted(STATUS_TAG_MAP.keys())),
						"hint": explain_try_self_for_subsection("Preamble.status", profile),
					}
					raise_validation_error(tr, obj, "STA-004", f"Status '{status}' is not allowed; allowed: {sorted(STATUS_TAG_MAP.items())}", details)
#===== Contract ===============================================#
# Contract must have a general section.
	with traced_section(tr, "Contract"):
		if "general" not in node_contract.items():
			details = render_missing_entry_details("Contract", node_contract.items(), "general", profile)
			raise_validation_error(tr,obj,"CON-024","Section 'general' does not exist.", details)
		# If caller marks other sections normative, ensure they exist.
		for sec in node_normative_sections.items():
			if sec == "Contract":
				continue
			if sec not in top.items():
				details = render_normative_section_details(sec, node_normative_sections.items(), profile, action="remove")
				raise_validation_error(tr,obj,"PRE-012",f"Section '{sec}' is listed as normative but does not exist.", details)
#===== Parameters must exist ==================================#
		with traced_section(tr, "Parameters"):
			if "Parameters" not in top.items():
				details = render_missing_entry_details("Document.sections", top.items(), "Parameters", profile, top_level=True)
				raise_validation_error(tr,obj,"PAR-001","Section 'Parameters' does not exist.", details)
#----- Must be normative --------------------------------------#
			if "Parameters" not in node_normative_sections.items():
				details = render_normative_section_details("Parameters", node_normative_sections.items(), profile, action="add")
				raise_validation_error(tr,obj,"PAR-002",f"Section 'Parameters' is not listed as normative.", details)
#----- Must match signature -----------------------------------#
			with traced_section(tr,get_obj_name(obj)):
				try:
					sig = inspect.signature(obj)
				except (TypeError, ValueError):
					sig = None
				if sig is not None:
					param_names = [p for p in sig.parameters if p not in ("self","cls")]
					doc_params = list(top.item("Parameters").items())
					for p in doc_params:
						if p in ("self","cls"):
							continue
						if p not in param_names:
							details = render_parameter_signature_details("Parameters", doc_params, [q for q in doc_params if q != p], profile)
							raise_validation_error(tr,obj,"PAR-005",f"Parameter '{p}' documented but not in signature {param_names}.", details)
					for p in param_names:
						if p not in doc_params:
							details = render_parameter_signature_details("Parameters", doc_params, doc_params + [p], profile)
							raise_validation_error(tr,obj,"PAR-004",f"Parameter '{p}' in signature but not documented.", details)
#===== Returns must exist =====================================#
		with traced_section(tr, "Returns"):
			if "Returns" not in top.items():
				details = render_missing_entry_details("Document.sections", top.items(), "Returns", profile, top_level=True)
				raise_validation_error(tr,obj,"RET-001","Section 'Returns' does not exist.", details)
#----- Must be normative --------------------------------------#
			if "Returns" not in node_normative_sections.items():
				details = render_normative_section_details("Returns", node_normative_sections.items(), profile, action="add")
				raise_validation_error(tr,obj,"RET-002",f"Section 'Returns' is not listed as normative.", details)
			node_returns = top.item("Returns")
#----- Must be list of strings --------------------------------#
# Not likely to trigger since this is captured somewhere else. We leave this here for completenes.
			if not isinstance(node_returns,docitem_list_base):
				details = {
					"found": render_source_snippet("Returns", node_returns.items()),
					"expected": [],
					"hint": explain_try_self_for_section("Returns", profile),
				}
				raise_validation_error(tr,obj,"RET-005",f"Section 'Returns' must not contain subsections.", details)
#----- Must match annotation ----------------------------------#
# Extract return annotation.
			ret_ann: object = inspect.Signature.empty
			try:
				hints_ret = get_type_hints(obj, include_extras=True)
				ret_ann = hints_ret.get("return", inspect.Signature.empty)
			except Exception:
				try:
					ret_ann = inspect.signature(obj).return_annotation
				except Exception:
					ret_ann = inspect.Signature.empty

			if ret_ann is not inspect.Signature.empty:
				joined = " ".join(node_returns.items())
# Rule RET-010 says treat volations as warnings.
#----- Use tokens for True and False if applicable ------------#
# Simple test please! Do not dig for bool in complex annonation types.
				if ret_ann == bool:
					if "|True|" not in joined and "|False|" not in joined:
						warn_validation(tr, obj, "RET-004", "Returns content should indicate a truthy/falsy outcome using the tokens |True| or |False|..")
#----- Use tokens for self and None if applicable ------------#
# Rule RET-008 says: test RET-006 only if annotated and seems to contain non-tokens.
				if get_obj_name(ret_ann) in ("None", "NoneType"):
					if "None" in joined and "|None|" not in joined:
						warn_validation(tr, obj, "RET-006", "Return value 'None' should be written in tokenized form as |None|.")
# Rule RET-009 says: test RET-007 only if annotated and seems to contain non-tokens.
				if get_obj_name(ret_ann) in ("Self",):
					if ("self" in joined or "Self" in joined) and "|Self|" not in joined:
						warn_validation(tr, obj, "RET-007", "Return value 'self' should be written in tokenized form as |Self|.")

#===== Raises must exist ======================================#
		with traced_section(tr, "Raises"):
			if "Raises" not in top.items():
				details = render_missing_entry_details("Document.sections", top.items(), "Raises", profile, top_level=True)
				raise_validation_error(tr,obj,"RAI-001","Section 'Raises' does not exist.", details)
#----- Must be normative --------------------------------------#
			if "Raises" not in node_normative_sections.items():
				details = render_normative_section_details("Raises", node_normative_sections.items(), profile, action="add")
				raise_validation_error(tr,obj,"RAI-002",f"Section 'Raises' is not listed as normative.", details)
#----- Must reference existing exception classes --------------#
			node_raises = top._items["Raises"]
			assert isinstance(node_raises, docitem_raises)
			for exc_name in node_raises.items().keys():
				try:
# Try to resolve the exception class name
					exc_obj, _ = resolve_object(exc_name, obj)
				except Exception:
# Yet, if that fails it might still be a built-in.
					if hasattr(builtins, exc_name):
						exc_obj = getattr(builtins, exc_name)
					else:
						exc_obj = None
				exc_cls = exc_obj if is_obj_class(exc_obj) else None
				if exc_cls is None or not is_obj_class(exc_cls):
					details = render_exception_reference_details(exc_name, profile, expected_kind="qualified identifier")
					raise_validation_error(tr,obj,"RAI-004", f"Exception '{exc_name}' listed in Raises does not refer to an existing class.", details)
				if not issubclass(exc_cls, BaseException):
					details = render_exception_reference_details(exc_name, profile, expected_kind="subclass of BaseException")
					raise_validation_error(tr,obj,"RAI-007", f"Exception '{exc_name}' is not a subclass of BaseException.", details)

def validate_docstring_inherited_method(tr : tracer, obj: object, top : docitem_docstring_inherited_method,node_contract : docitem_map_base,node_normative_sections : docitem_list_base, _seen: Dict[object,docitem_docstring_base] | None = None) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
	scope:
		extension
Contract:
	general:
		|Must| validate the docitem tree |var|`top` against the callable object |var|`obj`.
		|Must| ensure that |label|`Contract` contains a section |label|`general`.
		|Must| ensure that all sections declared as normative exist.
		|Must| ensure that each parameter mentioned in section |label|`Parameters` is in the callable's signature.
		|Must| ensure that each parameter in the callable's signature is mentioned in section |label|`Parameters`.
		|Must| ensure that each exception listed in section |label|`Raises` refers to an existing class.
		|Must| ensure that each exception listed in section |label|`Raises` is a subclass of |type|`BaseException`.
		|Must| resolve each exception listed in section |label|`Raises` by importing the longest module prefix and traversing remaining attributes; |must| fall back to the callable's globals, its defining module, and |value|`builtins`.
		|Must| collect warnings in the tracer object passed.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The callable object to validate against.
	top:
		The docitem tree to validate.
	node_contract:
		The node for section |label|`Contract` already parsed by the caller.
	node_normative_sections:
		The node for section |label|`Preamble.normative_sections` already parsed by the caller.
	_seen:
		Recording objects already validated in order to avoid recursion divergence and to share parsed trees across references.
Returns:
	|Must| return |None|
Raises:
	ValidationError:
		|Must| raise if any of the validation conditions listet in |label|`general` fails.
Notes:
	Usage:
		This function is typically not called directly. Please call |func|`validate_docstring` instead.
	Last review:
		Docstring and function are INCOMPLETE!
	"""
	profile = get_profile(top)
	top_scope_explicit = top.has_item("Preamble") and top.item("Preamble").has_item("scope")
	with traced_section(tr, "inherited_method"):
#===== Contract ===============================================#
# Contract must have a general section.
		with traced_section(tr, "Contract"):
			if "general" not in node_contract.items():
				details = render_missing_entry_details("Contract", node_contract.items(), "general", profile)
				raise_validation_error(tr,obj,"CON-036","Section 'general' does not exist.", details)
			# If caller marks other sections normative, ensure they exist.
			for sec in node_normative_sections.items():
				if sec == "Contract":
					continue
				if sec not in top.items():
					details = render_normative_section_details(sec, node_normative_sections.items(), profile, action="remove")
					raise_validation_error(tr,obj,"PRE-012",f"Section '{sec}' is listed as normative but does not exist.", details)
# Special for inherited methods.
			if "base" not in node_contract.items():
				details = render_missing_entry_details("Contract", node_contract.items(), "base", profile)
				raise_validation_error(tr,obj,"CON-039","Section 'base' does not exist.", details)
			with traced_section(tr, "base"):
				node_base = node_contract.item("base")
				base_items = list(node_base.items())
				if not isinstance(node_base, docitem_base_to_inherit_from):
#					details = render_base_method_reference_details([], "<well-formed Contract.base section>", "inherited_method")
# We assume that this is the correct form, but the error is caught during parsing. We keep this here for completeness.
					details = {
						"found": render_identifier_lines("Contract.base", base_items),
						"expected": render_suggestion("Contract.base", "well-formed Contract.base section"),
						"hint": explain_try_self_for_section("Contract.base", profile),
					}
					raise_validation_error(tr,obj,"CON-040","Section 'base' malformed.", details)
				if len(base_items) != 1:
#					details = render_base_method_reference_details(list(base_items), "<exactly one qualified identifier>", "inherited_method")
					details = {
						"found": render_identifier_lines("Contract.base", base_items),
						"expected": render_suggestion("Contract.base", "exactly one qualified identifier"),
						"hint": explain_try_self_for_subsection("Contract.base", "inherited_method"),
					}
					raise_validation_error(tr,obj,"CON-040","Section 'base' must contain exactly one qualified identifier.", details)
				base_ref = next(iter(base_items))
				if not isinstance(base_ref, str) or not RE_QUALIFIED_IDENTIFIER_COMPILED.fullmatch(base_ref):
# This is unlikely to trigger since this is captured during parsing as LQID-002, but we keep this here for completeness.
#					details = render_base_method_reference_details([base_ref], "<qualified identifier>", "inherited_method")
					details = {
						"found": render_identifier_lines("Contract.base", [base_ref]),
						"expected": render_suggestion("Contract.base", "qualified identifier referring to a base method"),
						"hint": explain_try_self_for_subsection("Contract.base", "inherited_method"),
					}
					raise_validation_error(tr,obj,"CON-041",f"Entry '{base_ref}' is not a qualified identifier.", details)
				try:
					base_obj, _ = resolve_object(base_ref, obj)
				except Exception as exc:
#					details = render_base_method_reference_details([base_ref], "<refer to a resolvable base method>", "inherited_method")
					details = {
						"found": render_identifier_lines("Contract.base", [base_ref]),
						"expected": render_suggestion("Contract.base", "qualified identifier referring to a base method"),
						"hint": explain_try_self_for_subsection("Contract.base", "inherited_method"),
					}
					raise_validation_error(tr,obj,"CON-042",f"Base method '{base_ref}' cannot be resolved: {exc}", details)
				if not (is_obj_function(base_obj)):
#					details = render_base_method_reference_details([base_ref], "<refer to a function or method>", "inherited_method")
					details = {
						"found": render_identifier_lines("Contract.base", [base_ref]),
						"expected": render_suggestion("Contract.base", "refer to a function or method"),
						"hint": explain_try_self_for_subsection("Contract.base", "inherited_method"),
					}
					raise_validation_error(tr,obj,"CON-042",f"Base reference '{base_ref}' is not a function or method.", details)
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
					if base_owner_cls is None or owner_cls is None or not is_obj_class(base_owner_cls) or not is_obj_class(owner_cls) or not issubclass(owner_cls, base_owner_cls):
						details = {
							"found": render_identifier_lines("Contract.base", [base_ref]),
							"expected": render_suggestion("Contract.base", "refer to a base method defined on a base class of the documented class"),
							"hint": explain_try_self_for_subsection("Contract.base", "inherited_method"),
						}
						raise_validation_error(tr,obj,"CON-043",f"Base method '{base_ref}' is not defined on a base class of '{owner_class_name}'.", details)
				# CON-044: names must match
				method_name = getattr(obj, "__name__", None)
				base_name = getattr(base_obj, "__name__", None)
				assert isinstance(base_name, str)
				if method_name != base_name:
					details = {
						"found": render_identifier_lines("Contract.base", [base_name]),
						"expected": render_suggestion("Contract.base", "make the base method name match the derived method name"),
						"hint": explain_try_self_for_subsection("Contract.base", "inherited_method"),
					}
					raise_validation_error(tr,obj,"CON-044",f"Base method name '{base_name}' does not match '{method_name}'.", details)
				# CON-045: referenced method must have a valid docstring.
				if not get_obj_docstring(base_obj):
					details = {
						"found": render_identifier_lines("Contract.base", [base_name]),
						"expected": render_suggestion("Contract.base", "implement a Waterloo docstring in base method"),
						"hint": explain_try_self_for_subsection("Contract.base", "inherited_method"),
					}
					raise_validation_error(tr,obj,"CON-045",f"Base method name '{base_name}' does not have a docstring.", details)
				try:
					top_base_obj = make_docitem_tree_from_object(tr,base_obj)
					validate_docstring(tr,base_obj,top_base_obj)
				except ParseError:
					details = {
						"found": render_identifier_lines("Contract.base", [base_name]),
						"expected": render_suggestion("Contract.base", "implement a Waterloo docstring in base method"),
						"hint": explain_try_self_for_subsection("Contract.base", "inherited_method"),
					}
					raise_validation_error(tr,obj,"CON-045",f"Base method '{base_name}': Validation raises a ParseError.", details)
				except ValidationError:
					details = {
						"found": render_identifier_lines("Contract.base", [base_name]),
						"expected": render_suggestion("Contract.base", "implement a Waterloo docstring in base method"),
						"hint": explain_try_self_for_subsection("Contract.base", "inherited_method"),
					}
					raise_validation_error(tr,obj,"CON-045",f"Base method '{base_name}': Validation raises a ValidationError.", details)
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
					sig_base = inspect.signature(base_obj)
					sig_obj = inspect.signature(cast(Callable[..., Any], obj))
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
							warn_validation(tr,obj,"CON-046",f"Parameter '{name}' type differs between base method and override.")
# COmpare return types
					if sig_base.return_annotation is not inspect._empty and sig_obj.return_annotation is not inspect._empty:
						if base_hints.get("return") != obj_hints.get("return"):
							warn_validation(tr,obj,"CON-046","Return type differs between base method and override.")
#===== Scope Monotonicity Rules ===============================#
	top_scopes = top.scopes()
#----- Contract.base ------------------------------------------#
	drvd_scopes = top_scopes
	if "base" in node_contract.items():
		node_base = node_contract.item("base")
		for base_name in node_base.items():
			try:
				base_obj, _ = resolve_object(base_name, obj)
			except Exception:
# Cannot resolve object? Not good, but must be handled elsewhere.
				continue
			tr_tmp = tracer()
			doc = get_obj_docstring(base_obj)
			if not doc:
# Class has no docstring? Do not test scope rule.
				continue
			try:
				tree = parse_indent_docstring(tr_tmp, doc)
				base_scopes, base_scope_explicit = get_scopes_of_tree_var(tr_tmp, tree)
			except (ParseError, SectionNotFoundError):
# Cannot extract scope from docstring? Do not test scope rule.
				continue
			if not top.can_see(base_scopes):
				details = render_scope_relation_details("inherited_method", top_scopes, top_scope_explicit, "method", base_scopes, base_scope_explicit, "Contract.base", base_name, "<reconsider the scopes of the derived method and its base method>", "inherited_method")
				raise_validation_error(tr, obj, "SCP-008", f"Reconsider the scopes of the derived method and its base method '{base_name}'.", details)


#===== helpers for See_also resolution ========================#

def _qualified_object_name(obj: object) -> str:
	if is_obj_module(obj):
		return obj.__name__
	mod_name = getattr(obj, "__module__", None)
	qual_name = getattr(obj, "__qualname__", None)
	if isinstance(mod_name, str) and isinstance(qual_name, str):
		return f"{mod_name}.{qual_name}"
	name = getattr(obj, "__name__", None)
	if isinstance(name, str):
		return name
	return str(obj)

#def _get_public_section_entries(top: docitem_docstring_base, section_label: str, expected_node_type: Type[docitem_map_base]) -> set[str]:
#	public: set[str] = set()
#	if section_label in top.items():
#		node = top._items[section_label]
#		assert isinstance(node, expected_node_type)
#		public = set(node.items().keys())
#	return public

def _get_public_section_entries2(top: docitem_docstring_base, section_label: str, expected_node_type: Type[docitem_list_base]) -> set[str]:
	public: set[str] = set()
	if section_label in top.items():
		node = top._items[section_label]
		assert isinstance(node, expected_node_type)
		public = set(node.items())
	return public

r"""
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
	scope:
		public
Contract:
	general:
		|Must| validate the docitem tree |var|`top` against the object |var|`obj` if |var|`top` is not |None|.
		|Must| analyze the docstring of |var|`obj` and create a docitem tree if |var|`top` is |None|.
		|Must| ensure that section |label|`Preamble` exists.
		|Must| ensure that subsection |label|`profile` exists in section |label|`Preamble`.
		|Must| ensure that subsection |label|`profile` contains exactly one item.
		|Must| ensure that the item in subsection |label|`profile` is an identifier.
		|Must| ensure that the item in subsection |label|`profile` is one of the allowed profiles.
		|Must| ensure that the item in subsection |label|`profile` matches the object type.
		|Must| ensure that subsection |label|`normative_sections` exists in section |label|`Preamble`.
		|Must| ensure that each item in subsection |label|`normative_sections` refers to an existing section.
		|Must| ensure that no item in subsection |label|`normative_sections` appears more than once.
		|Must| ensure that each section which contains at least one of the normativity keywords is listed under |label|`normative_sections`, unless the section is explicitly declared informative by the active profile/template.
		|Must| ensure that section |label|`Contract` exists.
		|Must| ensure that section |label|`Contract` is listed in subsection |label|`normative_sections`.

		|Must| ensure that section |label|`Definitions` --provided it exists-- is listed in subsection |label|`normative_sections`, regardless of whether it contains normativity keywords.
		|Must| look for ocurrences of token |lit|`\\|term\\|\\`<Identifier>\\`` in the docitem tree and ensure that the referenced term is defined in section |label|`Definitions`.

		|Must| ensure that section |label|`Terminology` --provided it exists-- is considered informative and NOT listed in subsection |label|`normative_sections`.
		|Must| enforce profile related tests depending on the profile and call one of the validators |func|`validate_docstring_*`.

		|Must| examine section |label|`See_also` if it exists.
		|Must| ensure the existence of each item listed in |label|`See_also`.
		|Must| ensure that each item listed in |label|`See_also` has a valid docstring.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The object to validate against (module, class or callable).
	top:
		The docitem tree to validate.
	_seen:
		Recording objects already validated in order to avoid recursion divergence and to share parsed trees across references.
Returns:
	|Must| return |None|
Raises:
	ValidationError:
		|Must| raise if any of the validation conditions listet in |label|`general` fails.
Notes:
	Usage:
		This function should be pretty easy to use, if you leave out parameter |var|`top`.
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
		if not get_obj_docstring(obj):
			raise_has_no_docstring(tr,"DOC-001",obj)
		try:
			top = make_docitem_tree_from_object(tr,obj)
		except Exception as e:
			raise
	_seen[obj] = top
# Log some debug info
	tr.add_info(f"validating '{get_obj_name(obj)}'")
	profile = get_profile(top)
	try:
		top_scopes = top.scopes()
	except Exception:
		top_scopes = set()
	top_scope_explicit = top.has_item("Preamble") and top.item("Preamble").has_item("scope")
  
	with traced_section(tr, f"{get_obj_name(obj)}"):
#===== Preamble must exist ====================================#
# Preamble must exist. We do not allow purely informative docstrings.
		if "Preamble" not in top.items():
			details = {
				"found": render_missing_entry_details("Preamble", top.items(), "Preamble", profile, top_level=True)["found"],
				"expected": render_missing_entry_details("Preamble", top.items(), "Preamble", profile, top_level=True)["expected"],
				"hint": render_missing_entry_details("Preamble", top.items(), "Preamble", profile, top_level=True)["hint"],
			}
			raise_validation_error(tr,obj,"PRE-001","Section 'Preamble' does not exist.", details)
		node_preamble = top.item("Preamble")
		with traced_section(tr, f"Preamble"):
#..... profile must exist .....................................#
# Profile must exist.
			if not "profile" in node_preamble.items():
				details = render_missing_entry_details("Preamble", node_preamble.items(), "profile", profile)
				raise_validation_error(tr,obj,"PRE-003","Section 'profile' does not exist.", details)
# Here we know it exists.
			node_profile = node_preamble.item("profile")
			with traced_section(tr, "profile"):
				assert isinstance(node_profile,docitem_list_base)
				if len(node_profile.items()) == 0:
					details = render_exactly_one_identifier_details("Preamble.profile", node_profile.items(), profile)
					raise_validation_error(tr,obj,"PRE-004","Section 'profile' must have exactly one item.", details)
				if len(node_profile.items()) > 1:
					details = render_exactly_one_identifier_details("Preamble.profile", node_profile.items(), profile)
					raise_validation_error(tr,obj,"PRE-004","Section 'profile' must have exactly one item.", details)
			if not RE_IDENTIFIER_COMPILED.fullmatch(profile):
				details = {
					"found": render_identifier_lines("Preamble.profile", [profile]),
					"expected": render_expected_identifier("Preamble.profile", "identifier"),
					"hint": explain_try_self_for_subsection("Preamble.profile", profile),
				}
				raise_validation_error(tr,obj,"PRE-014",f"Expected identifier, got '{profile}'.", details)
# For the current version we tighten this rule
			if not profile in ("module","class","function","method","inherited_method"):
				details = {
					"found": render_identifier_lines("Preamble.profile", [profile]),
					"expected": render_allowed_identifier("Preamble.profile", ("module","class","function","method","inherited_method")),
					"hint": explain_try_self_for_subsection("Preamble.profile", profile),
				}
				raise_validation_error(tr,obj,"PRE-005",f"Expected one of {{'module','class','function','method','inherited_method'}}, got '{profile}'.", details)
# The profile must match the object type. At this point it has already been
# tested most likely, but we leave the code here for saftey.
			check_profile_matches_object(tr, profile, obj)

# Normative_sections must exist and be non-empty. Non-emptyness is implied by existence and normativity of Contract.
		with traced_section(tr, "normative_sections"):
			if "normative_sections" not in node_preamble.items():
				details = {
					"found": ["Preamble:", "\t<no normative_sections>"],
					"expected": ["Preamble:", "\tnormative_sections:", "\t\tContract <more section labels, comma separated>"],
					"hint": explain_try_self_for_subsection("Preamble.normative_sections", profile),
				}
				raise_validation_error(tr,obj,"PRE-006","Section 'normative_sections' does not exist.", details)
# Here we know it exists.
			node_normative_sections: docitem_list_base = cast(docitem_list_base, node_preamble.item("normative_sections"))
# Chill mypy. We know it's a docitem_list_base.
			assert isinstance(node_normative_sections,docitem_list_base)
			normative_sections = list(node_normative_sections.items())
		seen = set()
		for sec in node_normative_sections.items():
# Each entry must point to an existing section.
			if not sec in top.items():
				details = render_normative_section_details(sec, normative_sections, profile, action="remove")
				raise_validation_error(tr,obj,"PRE-012",f"Entry '{sec}' does not refer to an existing section.", details)
#					if sec in seen:
#						raise_validation_error(tr,obj,"LQID-004","Entry '{sec}' is duplicate.")
			seen.add(sec)
# Handle the meta case here:
		if "Preamble" in node_normative_sections.items():
			details = render_normative_section_details("Preamble", node_normative_sections.items(), profile, action="remove")
			raise_validation_error(tr,obj,"PRE-002","Section 'Preamble' must not list itself as normative.", details)
		with traced_section(tr, "scope"):
			if "scope" in node_preamble.items():
				node_scope = node_preamble.item("scope")
				for s in node_scope.items():
					if s not in SCOPE_TAG_MAP:
						details = {
							"found": render_identifier_lines("Preamble.scope", [s]),
							"expected": render_allowed_identifiers("Preamble.scope", SCOPE_TAG_MAP.keys()),
							"hint": explain_try_self_for_subsection("Preamble.scope", profile),
						}
						raise_validation_error(tr, obj, "SCP-003", f"Scope tag '{s}' is not allowed.", details)

# Rule: Any section containing one of the keywords of normativity
# must be listed under normative_sections.
		for label,item in top.items().items():
# We explicitly exclude section which must not appear,
# so that specific section rules below trigger.
			if label in ("Notes","Class_overview","Function_overview","Method_overview","Terminology"):
				continue
			if item.has_norm_keywords():
				if label not in node_normative_sections.items():
					details = render_normative_section_details(label, node_normative_sections.items(), profile, action="add")
					raise_validation_error(tr,obj,"PRE-013",f"Section '{label}' contains a keyword of normativity but is not listed in normative_sections.", details)
#===== Contract must exist ====================================#
		with traced_section(tr, "Contract"):
			if "Contract" not in top.items():
				details = render_missing_entry_details("Preamble", top.items().keys(), "Contract", profile, top_level=True)
				raise_validation_error(tr,obj,"CON-001","Section 'Contract' does not exist.", details)
# Rule pre-04: the contract must be listed as normative
			if not "Contract" in node_normative_sections.items():
				details = render_normative_section_details("Contract", node_normative_sections.items(), profile, action="add")
				raise_validation_error(tr,obj,"CON-002","Section 'Contract' must be listed under 'normative_sections'.", details)
			node_contract = top._items["Contract"]
# Chill mypy. We know it's a docitem_map_base.
			assert isinstance(node_contract,docitem_map_base)
 
#===== If Definitions exists it must be normative =============#
		with traced_section(tr, "Definitions"):
			if "Definitions" in top.items():
				node_definitions: docitem_definitions | None = cast(docitem_definitions,top._items["Definitions"])
# Chill mypy
				assert isinstance(node_definitions, docitem_map_base)
				if not "Definitions" in node_normative_sections.items():
					details = render_normative_section_details("Definitions", node_normative_sections.items(), profile, action="add")
					raise_validation_error(tr,obj,"DEF-002","Section 'Definitions' exists but is not normative.",details)
# Regular and inherited defitems.
				current_object_terms_and_variations = set(node_definitions.items().keys())
				current_object_inherited_terms = set(node_definitions.inherited())
# Required for DEF-022
				inherited_terms_and_variations = set()
				if current_object_inherited_terms:
					if profile == "module":
						details = render_inherited_definition_details(current_object_inherited_terms, profile, expected_text="<remove subsection '_inherit' from a module docstring>", use_section_hint=True)
						raise_validation_error(tr,obj,"DEF-011","Subsection '_inherited' is not allowed in a module docstring.",details)
					warn_validation(tr,obj,"VLII-001","Use of subsection '_inherited' violates the LoII principle.")
# DEF-014/015/018: inherited definitions must come from the direct module.
					direct_module = get_obj_direct_module(obj)
					if direct_module is None:
						details = render_inherited_definition_details(current_object_inherited_terms, profile, expected_text="<refer to a resolvable direct module with a valid Waterloo docstring>")
						raise_validation_error(tr,obj,"DEF-014","Subsection '_inherited' requires a resolvable direct module with valid docstring.",details)
					with traced_section(tr, "_inherited"):
						tr_tmp = tracer()
						try:
							mod_doc_top = validate_docstring(tr_tmp, direct_module, _seen=_seen)
						except Exception as e:
							details = render_inherited_definition_details(current_object_inherited_terms, profile, expected_text="<implement a Waterloo docstring in the direct module>")
							raise_validation_error(tr,obj,"DEF-014",f"Direct module '{get_obj_name(direct_module)}' has no valid docstring: {e}",details)
# Chill mypy.
						assert isinstance(mod_doc_top, docitem_docstring_base)
						if "Definitions" not in mod_doc_top.items():
							details = render_inherited_definition_details(current_object_inherited_terms, profile, expected_text="<add a Definitions section to the direct module>")
							raise_validation_error(tr,obj,"DEF-015",f"Direct module '{get_obj_name(direct_module)}' has no section 'Definitions'.",details)
						mod_definitions = cast(docitem_definitions, mod_doc_top.item("Definitions"))
# Chill mypy.
						assert isinstance(mod_definitions, docitem_definitions)
						module_terms = mod_definitions.terms()
						missing = current_object_inherited_terms - module_terms
						if missing:
							details = render_inherited_definition_details(sorted(missing), profile, expected_text="<inherit only terms that exist in the direct module>")
							raise_validation_error(tr,obj,"DEF-018",f"Inherited defitems not found in direct module terms: {missing}.",details)
# Extract terms and variations of module for the given set of inherited terms.
						inherited_terms_and_variations = mod_definitions.terms_and_variations(current_object_inherited_terms)
# Regular and inherited must be disjoint.
				names_in_both = set.intersection(current_object_terms_and_variations,current_object_inherited_terms)
				if len(names_in_both ) > 0:
					details = render_inherited_definition_details(sorted(names_in_both), profile, expected_text="<remove duplicated terms from Definitions or _inherit>")
					raise_validation_error(tr,obj,"DEF-017",f"Inherited defitems are redefined in section 'Definitions': {names_in_both}.",details)
# Defitem content should not be empty.
				for name in current_object_terms_and_variations:
					node_defitem = node_definitions.item(name)
					if node_defitem.empty():
						warn_validation(tr,obj,"DEF-009","Definition item content should not be empty.")
			else:
				node_definitions = None
# Regular and inherited terms and variations.
				current_object_terms_and_variations = set()
				current_object_inherited_terms = set()
# Ensure each referenced term appears in section `Definitions` either directly or by inheritance.
			term_refs = _collect_term_refs(top)
			if term_refs:
				if node_definitions is None:
					details = render_definition_reference_details(sorted(term_refs), profile, missing_definitions=True)
					raise_validation_error(tr,obj,"DEF-007", "Token |term| is used but section 'Definitions' is missing.",details)
				for term in term_refs:
# Test term reference against 1. terms directly defined in the object and 2. (DEF-022) terms and variations inherited from the module.
					if term not in (current_object_terms_and_variations | inherited_terms_and_variations):
						details = render_definition_reference_details(term, profile, missing_definitions=False)
						raise_validation_error(tr,obj,"DEF-008", f"Token |term|`{term}` references an undefined term.",details)

#===== Terminology must NOT be normative ======================#
		with traced_section(tr, "Terminology"):
			if "Terminology" in top.items():
				if "Terminology" in node_normative_sections.items():
					details = render_normative_section_details("Terminology", node_normative_sections.items(), profile, action="remove")
					raise_validation_error(tr,obj,"TERM-002","Section 'Terminology ' marked as normative in Preamble.", details)
				node_terminology = top.item("Terminology")
# Defitem content should not be empty.
				for name in node_terminology.items():
					node_term = node_terminology.item(name)
					if node_term.empty():
						warn_validation(tr,obj,"TERM-008","Term content should not be empty.")
					if node_term.has_norm_keywords():
						details = render_normativity_keyword_details("Terminology", name, node_term.items(), "don't use normativity keyword, describe terms informatively", profile)
						raise_validation_error(tr, obj, "TERM-003",f"Term content has normativity keywords; content is informational only.", details)

#===== If See_also exists, more tests apply ===================#
		with traced_section(tr, "See_also"):
# Section may exist, SEE-001.
			if "See_also" in top.items():
				node_see_also = top._items["See_also"]
				for item_see_also in node_see_also.items():
# Entries must be Qualified Identifiers
					if not RE_QUALIFIED_IDENTIFIER_COMPILED.fullmatch(item_see_also):
						details = render_see_also_reference_details(item_see_also, "<identifier or qualified identifier>", profile)
						raise_validation_error(tr,obj,"SEE-002", f"See_also reference '{item_see_also}' is not a (Qualified) Identifier.", details)
					try:
						target_obj, target_name = resolve_object(item_see_also, obj)
					except Exception as e:
						if "See_also" in node_normative_sections.items():
							details = render_see_also_reference_details(item_see_also, "<refer to an existing public object>", profile)
							raise_validation_error(tr,obj,"SEE-004", f"See_also reference '{item_see_also}' cannot be resolved: {e} ('See_also' is normative).", details)
						else:
							warn_validation(tr,obj,"SEE-003", f"See_also reference '{item_see_also}' cannot be resolved: {e} (informative section).")
							continue
					if target_obj is obj:
						details = render_see_also_reference_details(item_see_also, "<do not refer to the documented object itself>", profile)
						raise_validation_error(tr,obj,"SEE-005", f"See_also reference '{item_see_also}' must not refer to the object itself.", details)
					if target_obj in _seen:
						continue
					doc = get_obj_docstring(target_obj)
					if not doc:
						is_builtin = inspect.isbuiltin(target_obj) or getattr(target_obj, "__module__", "") == "builtins"
						is_documentable = is_obj_documentable(target_obj)
						is_normative_target = "See_also" in node_normative_sections.items() and (is_obj_module(target_obj) or is_obj_class(target_obj) or is_obj_function(target_obj)) and not is_builtin
						if is_normative_target:
							details = render_see_also_reference_details(item_see_also, "<refer to a documented object with a valid Waterloo docstring>", profile)
							raise_validation_error(tr,obj,"SEE-008", f"See_also reference '{item_see_also}' has no valid docstring ('See_also' is normative).", details)
						if is_documentable:
# No docstring at all: warn unless normative handling above escalated already.
							details = render_see_also_reference_details(item_see_also, "<refer to a documented object>", profile)
							warn_validation(tr,obj,"SEE-006", f"See_also reference '{item_see_also}' has no docstring.", details)
					else:
# Note that we do not validate built-ins! SEE-010
						if (is_obj_module(target_obj) or is_obj_class(target_obj) or is_obj_function(target_obj)):
							is_builtin = inspect.isbuiltin(target_obj) or getattr(target_obj, "__module__", "") == "builtins"
							if is_builtin:
								continue
#===== Scope Monotonicity Rules ===============================#
# Try to parse the target docstring to obtain its scopes; treat parse failures as "no valid docstring".
							tr_tmp = tracer()
							try:
								tree = parse_indent_docstring(tr_tmp, doc)
								target_scopes, target_scope_explicit = get_scopes_of_tree_var(tr_tmp, tree)
							except (ParseError, SectionNotFoundError):
								if  "See_also" in node_normative_sections.items():
									tr.add_info("Rule SEE-009 applies","validation")
									details = render_see_also_reference_details(item_see_also, "<refer to a documented object with a valid Waterloo docstring>", profile)
									raise_validation_error(tr,obj,"SEE-008", f"See_also reference '{item_see_also}' has no valid docstring ('See_also' is normative).", details)
								else:
									details = render_see_also_reference_details(item_see_also, "<refer to a documented object with a valid Waterloo docstring>", profile)
									warn_validation(tr,obj,"SEE-007", f"See_also reference '{item_see_also}' has no valid docstring (informative section).", details)
								continue
# Scope monotonicity for See_also references (SCP-006 / SCP-007)
							if "See_also" in node_normative_sections.items():
								if not top.can_see(target_scopes):
									details = render_scope_relation_details(profile, top_scopes, top_scope_explicit, "referenced object", target_scopes, target_scope_explicit, "See_also", item_see_also, "<reconsider the scopes of the referenced object and the referencing object>", profile)
									raise_validation_error(tr,obj,"SCP-006", f"Reconsider the scopes of the referenced object and the referencing object '{item_see_also}'.", details)
							else:
								if not top.can_see(target_scopes):
									details = render_scope_relation_details(profile, top_scopes, top_scope_explicit, "referenced object", target_scopes, target_scope_explicit, "See_also", item_see_also, "<reconsider the scopes of the referenced object and the referencing object>", profile)
									warn_validation(tr,obj,"SCP-007", f"Reconsider the scopes of the referenced object and the referencing object '{item_see_also}'.", details)
#===== Notes ==================================================#
		with traced_section(tr, "Notes"):
			if "Notes" in top.items():
				if "Notes" in node_normative_sections.items():
					details = render_normative_section_details("Notes", node_normative_sections.items(), profile, action="remove")
					raise_validation_error(tr,obj,"NOTE-002","Section 'Notes' marked as normative in Preamble.", details)
				node_notes = top.item("Notes")
# Content should not be empty.
				for name in node_notes.items():
					with traced_section(tr, name):
						node_note = node_notes.item(name)
						if node_note.empty():
							warn_validation(tr,obj,"NOTE-009","Note content should not be empty.")
						if node_note.has_norm_keywords():
							details = render_normativity_keyword_details("Notes", name, node_note.items(), "don't use normativity keyword; consider moving relevant content to the Contract section", profile)
							raise_validation_error(tr, obj, "NOTE-003",f"Note content must not contain normativity keywords; content is informational only.", details)
# Cases
		profile = get_profile(top)
		if profile == "module":
			assert isinstance(top,docitem_docstring_module)
			validate_docstring_module(tr,obj,top,node_contract,node_normative_sections)
		elif profile == "class":
			assert isinstance(top,docitem_docstring_class)
			validate_docstring_class(tr,obj,top,node_contract,node_normative_sections)
		elif profile in ("method","function"):
			assert isinstance(top,docitem_docstring_method)
			validate_docstring_method(tr,cast(Callable[..., Any],obj),top,node_contract,node_normative_sections)
		elif profile == "inherited_method":
			assert isinstance(top,docitem_docstring_inherited_method)
			validate_docstring_inherited_method(tr,obj,top,node_contract,node_normative_sections)
		else:
			details = {
				"found": render_identifier_lines("Preamble.profile", [profile]),
				"expected": render_allowed_identifier("Preamble.profile", ("module","class","function","method","inherited_method")),
				"hint": explain_try_self_for_subsection("Preamble.profile", profile),
			}
			raise_validation_error(tr,obj,"PRE-005",f"Unknown profile: {profile}", details)
#===== Scope Monotonicity Rules ===============================#
# internal references introduced by Classes, Methods, Functions, Public_* and Derived_from / inherited_method
# are validated in their respective validators; see markers in those functions.
#===== Partial Normativity Detection ==========================#
# May add warnings for breach of PNB-rules.
	top.detect_partial_normativity(tr)

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
		|Must| analyze nested classes documented in |label|`Public_classes`.
		|Must| ensure that each entry in |label|`Public_classes` resolves to a nested class with a valid docstring.
		|Should| ensure that each nested class with a valid docstring is listed in section |label|`Public_classes`.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The class object to be validated.
	doc_class:
		Already parsed class docstring tree for |var|`obj`.
Returns:
	|Must| return |None|.
Raises:
	TypeError:
		|Must| raise if |var|`obj` is not a class object.
	ValidationError:
		|Must| raise if validation fails.
Notes:
	Last review:
		2026-02-04
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not is_obj_class(obj):
			raise TypeError("validate_class_class_coverage expects a class object.")
		if not isinstance(doc_class, docitem_docstring_class):
			raise TypeError("doc_class must be a docitem_docstring_class instance")
# Collect declared public nested classes from class docstring
		public_classes: set[str] = _get_public_section_entries2(doc_class,"Public_classes",docitem_public_classes)
# Validate nested class docstrings (defined directly on the class)
		valid_classes: set[str] = set()
		classes_with_valid_docstring: set[str] = set()
# Iterate over referred objects (__dict__)
		for name_of_member, member in obj.__dict__.items():
# Ignore members which are not class (like constants, variables, type aliases).
			if not is_obj_class(member):
				continue
# Ignore members from other modules.
			if getattr(member, "__module__", None) != getattr(obj, "__module__", None):
				continue
# Get docstring. Ignore member if there is none.
			doc = get_obj_docstring(member)
			if not doc:
				continue
# Determine validity for warning purposes
			try:
				tmp_tr = tracer()
				validate_docstring(tmp_tr, member)
				classes_with_valid_docstring.add(name_of_member)
			except Exception:
				pass
# Validate only if class is listed
			if name_of_member in public_classes:
# Push member name_of_member to tracer.
				with traced_section(tr, name_of_member):
					try:
# Validate and collect messages from lower levels
						validate_class_coverage(tr, member)
						valid_classes.add(name_of_member)
					except Exception:
# Add message from higher level for clarity (should-level rule).
						warn_validation(tr,obj,"CPCL-007",f"class '{name_of_member}' listed in Public_classes but has no valid docstring.")
# Validate entries listed in Public_classes
		with traced_section(tr, "Public_classes"):
# Rule: every class with a valid docstring should be listed
			missing_in_public = classes_with_valid_docstring - public_classes
			for name in missing_in_public:
				warn_validation(tr,obj,"CPCL-006",f"Class '{name}' has a docstring but is not listed in Public_classes: {sorted(missing_in_public)}")
			for name in public_classes:
				if not hasattr(obj, name):
					details = render_name_object_consistency_details("Public_classes", public_classes, "class")
					raise_validation_error(tr,obj,"CPCL-004",f"Class '{name}' listed in Public_classes but does not exist.", details)
				cls_obj = getattr(obj, name)
				if not is_obj_class(cls_obj):
					details = render_name_object_consistency_details("Public_classes", public_classes, "class")
					raise_validation_error(tr,obj,"CPCL-005",f"Member '{name}' listed in Public_classes is not a class.", details)
				doc_c2 = get_obj_docstring(cls_obj)
				if not doc_c2.strip():
					warn_validation(tr,obj,"CPCL-007",f"Class '{name}' is listed in Public_classes but has no valid docstring.")
# Important: Coverage means to descend recursively.
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
		|Must| analyze methods documented in |label|`Public_methods`.
		|Must| ensure that each entry in |label|`Public_methods` resolves to a method with a valid docstring.
		|Should| ensure that each method with a valid docstring is listed in section |label|`Public_methods`.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The class object to be validated.
	doc_class:
		Already parsed class docstring tree for |var|`obj`.
Returns:
	|Must| return |None|.
Raises:
	TypeError:
		|Must| raise if |var|`obj` is not a class object.
		|Must| raise if |var|`doc_class` is not a |type|`docitem_docstring_class`.
	ValidationError:
		|Must| raise if validation fails.
Notes:
	Last review:
		2026-02-04
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not is_obj_class(obj):
			raise TypeError("validate_class_method_coverage expects a class object.")
		if not isinstance(doc_class, docitem_docstring_class):
			raise TypeError("doc_class must be a docitem_docstring_class instance")
# Collect declared public methods from class docstring
		public_methods: set[str] = _get_public_section_entries2(doc_class,"Public_methods",docitem_public_methods)
# Collect methods defined on the class (not inherited) and validate their docstrings
		valid_methods: set[str] = set()
		methods_with_valid_docstring: set[str] = set()
# Iterate over referred objects (__dict__)
		for name_of_member, member in obj.__dict__.items():
			func_obj: Callable[..., Any] | None = get_func_obj_from_callable(member)
# Ignore members which are not functions.
			if func_obj is None or not is_obj_function(func_obj):
				continue
# Ignore methods not defined here.
			if getattr(func_obj, "__qualname__", "").split(".")[0] != obj.__name__:
				continue
# Get docstring. Ignore member if there is none.
			doc = get_obj_docstring(func_obj)
			if not doc:
				continue
# Determine validity for warning purposes
			try:
				tmp_tr = tracer()
				validate_docstring(tmp_tr, func_obj)
				methods_with_valid_docstring.add(name_of_member)
			except Exception:
				pass
# Validate only if method is listed
			if name_of_member in public_methods:
# Push member name to tracer.
				with traced_section(tr, func_obj.__name__):
					try:
# Validate and collect messages from lower levels
						validate_docstring(tr,func_obj, None, None)
						valid_methods.add(name_of_member)
					except Exception:
# Add message from higher level for clarity (should-level rule).
						warn_validation(tr,obj,"CPMT-007",f"class {get_obj_name(obj)}: method '{name_of_member}' listed in Public_methods but has no valid docstring.")

# Rule: if the class exposes methods with valid docstrings, it should declare Public_methods
		with traced_section(tr, "Public_methods"):
# Rule: every method with a valid docstring should be listed
			missing_in_public = methods_with_valid_docstring - public_methods
			for name_of_member in missing_in_public:
				warn_validation(tr,obj,"CPMT-006",f"Class {obj.__name__}: method '{name_of_member}' has a docstring but is not listed in Public_methods.")
# Rule: every method listed should have a valid docstring (warn)
			for name_of_member in public_methods:
				if name_of_member in valid_methods:
					continue
# method might be inherited; try to resolve and validate if present
				if not hasattr(obj, name_of_member):
					details = render_name_object_consistency_details("Public_methods", public_methods, "class")
					raise_validation_error(tr,obj,"CPMT-004",f"Method '{name_of_member}' listed in Public_methods but does not exist.", details)
				meth_obj = getattr(obj, name_of_member)
				func_obj2: Callable[..., Any] | None = get_func_obj_from_callable(meth_obj)
				if func_obj2 is None or not is_obj_function(func_obj2):
					details = render_name_object_consistency_details("Public_methods", public_methods, "class")
					raise_validation_error(tr,obj,"CPMT-005",f"Member '{name_of_member}' listed in Public_methods is not a method.", details)
				docm2 = get_obj_docstring(func_obj2)
				if not docm2.strip():
					warn_validation(tr,obj,"CPMT-007",f"Class {get_obj_name(obj)}: method '{name_of_member}' is listed in Public_methods but has no valid docstring.")
					continue
				validate_docstring(tr,func_obj2, None, None)

def validate_class_type_coverage(tr : tracer,obj: type[object], doc_class: docitem_docstring_class) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze the docstrings of the class object passed.
		|Must| ensure that each type listed in the class's |label|`Public_types` section exists in the class.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The class object to be validated.
	doc_class:
		Already parsed class docstring tree for |var|`obj`.
Returns:
	|Must| return |None|.
Raises:
	ValidationError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not isinstance(doc_class, docitem_docstring_class):
			raise TypeError("doc_class must be a docitem_docstring_class instance")
# Collect declared public types from class docstring
# checked at validation
#		public_types: set[str] = _get_public_section_entries(doc_class,"Public_types",docitem_public_types)
# Rule: every type listed must exist
#		with traced_section(tr, "Public_types"):
#			for type_name in public_types:
#				if not hasattr(obj, type_name):
#					raise_validation_error(tr,obj,"CPTYP-005",f"Class {obj.__name__}: type '{type_name}' listed in Public_types but does not exist.")

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
		|Must| ensure that each constant listed in |label|`Public_constants` exists.
		|Must| ensure that each constant listed in |label|`Public_constants` is annotated as |type|`Final` or not annotated at all.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The class object to be validated.
	doc_class:
		Already parsed class docstring tree for |var|`obj`.
Returns:
	|Must| return |None|.
Raises:
	TypeError:
		|Must| raise if |var|`obj` is not a class object.
	ValidationError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not is_obj_class(obj):
			raise TypeError("validate_class_method_coverage expects a class object.")
		if not isinstance(doc_class, docitem_docstring_class):
			raise TypeError("doc_class must be a docitem_docstring_class instance")

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
		|Must| ensure that each variable listed in |label|`Public_variables` exists.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The class object to be validated.
	doc_class:
		Already parsed class docstring tree for |var|`obj`.
Returns:
	|Must| return |None|.
Raises:
	TypeError:
		|Must| raise if |var|`obj` is not a class object.
	ValidationError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not is_obj_class(obj):
			raise TypeError("validate_class_method_coverage expects a class object.")
		if not isinstance(doc_class, docitem_docstring_class):
			raise TypeError("doc_class must be a docitem_docstring_class instance")

# Collect declared public variables from class docstring
		public_variables: set[str] = set()
		if "Public_variables" in doc_class.items():
			pv_node = doc_class._items["Public_variables"]
			assert isinstance(pv_node, docitem_public_variables)
			public_variables = set(pv_node.items().keys())

def validate_module_class_coverage(tr : tracer,obj: ModuleType, doc_module: docitem_docstring_module) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze classes documented in |label|`Public_classes`.
		|Must| ensure that each entry in |label|`Public_classes` resolves to a class with a valid docstring.
		|Should| ensure that each class with a valid docstring is listed in section |label|`Public_classes`.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The module object to be validated.
	doc_module:
		Already parsed module docstring tree for |var|`obj`.
Returns:
	|Must| return |None|.
Raises:
	ValidationError:
		|Must| raise if validation fails.
Notes:
	Last review:
		2026-02-04
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not is_obj_module(obj):
			raise TypeError("validate_module_class_coverage expects a module object.")
		if not isinstance(doc_module, docitem_docstring_module):
			raise TypeError("doc_module must be a docitem_docstring_module instance")
# Collect declared public classes from module docstring
		public_classes: set[str] = _get_public_section_entries2(doc_module,"Public_classes",docitem_public_classes)
# Collect classes defined in the module (not imported) and validate their docstrings
		valid_classes: set[str] = set()
		classes_with_valid_docstring: set[str] = set()
# Iterate over referred objects (__dict__)
		for name_of_member, member in obj.__dict__.items():
# Ignore members which are not class (like constants, variables, type aliases).
			if not is_obj_class(member):
				continue
			if getattr(member,"__module__",None) != obj.__name__:
				continue
# Get docstring. Ignore member if there is none.
			doc = get_obj_docstring(member)
			if not doc:
				continue
			# Determine validity for warning purposes
			try:
				tmp_tr = tracer()
				validate_docstring(tmp_tr,member)
				if not tmp_tr.has_errors():
					classes_with_valid_docstring.add(name_of_member)
			except Exception:
				pass
# Validate only if class is listed
			if name_of_member in public_classes:
# Push member name_of_member to tracer.
				with traced_section(tr, name_of_member):
					try:
# Validate and collect messages from lower levels
						validate_class_coverage(tr,member)
						valid_classes.add(name_of_member)
					except Exception:
# Add message from higher level for clarity (should-level rule).
						warn_validation(tr,obj,"MPCL-007",f"class '{name_of_member}' listed in Public_classes but has no valid docstring.")

# Rule: classes with docstrings should be listed in Public_classes
		with traced_section(tr, "Public_classes"):
			missing_in_public = classes_with_valid_docstring - public_classes
			for name_of_member in missing_in_public:
				warn_validation(tr,obj,"MPCL-006",f"Class '{name_of_member}' has a docstring but is not listed in Public_classes.")
# Validate entries listed in Public_classes
			for name_of_member in public_classes:
				if not hasattr(obj, name_of_member):
					details = render_name_object_consistency_details("Public_classes", public_classes, "module")
					raise_validation_error(tr,obj,"MPCL-004",f"Class '{name_of_member}' listed in Public_classes but does not exist.", details)
				cls_obj = getattr(obj, name_of_member)
				if not is_obj_class(cls_obj):
					details = render_name_object_consistency_details("Public_classes", public_classes, "module")
					raise_validation_error(tr,obj,"MPCL-005",f"Member '{name_of_member}' listed in Public_classes is not a class.", details)
				doc_c2 = get_obj_docstring(cls_obj)
				if not doc_c2.strip():
					warn_validation(tr,obj,"MPCL-007",f"Class '{name_of_member}' listed in Public_classes but has no valid docstring.")
					continue
# Important: Coverage means to descend recursively.
				validate_class_coverage(tr,cls_obj)

def validate_module_function_coverage(tr : tracer,obj: ModuleType, doc_module: docitem_docstring_module) -> None:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| analyze functions documented in |label|`Public_functions`.
		|Must| ensure that each entry in |label|`Public_functions` resolves to a function with a valid docstring.
		|Should| ensure that each function with a valid docstring is listed in section |label|`Public_functions`.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The module object to be validated.
	doc_module:
		Already parsed module docstring tree for |var|`obj`.
Returns:
	|Must| return |None|.
Raises:
	TypeError:
		|Must| raise if |var|`obj` is not a module object.
		|Must| raise if |var|`doc_module` is not a |type|`docitem_docstring_module`.
	ValidationError:
		|Must| raise if validation fails.
Notes:
	Last review:
		2026-02-04
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not is_obj_module(obj):
			raise TypeError("validate_module_function_coverage expects a module object.")
		if not isinstance(doc_module, docitem_docstring_module):
			raise TypeError("doc_module must be a docitem_docstring_module instance")
# Collect declared public functions from module docstring
		public_functions: set[str] = _get_public_section_entries2(doc_module,"Public_functions",docitem_public_functions)
# Collect functions defined in the module (not imported) and validate their docstrings
		valid_functions: set[str] = set()
		functions_with_valid_docstring: set[str] = set()
# Iterate over referred objects (__dict__)
		for name_of_member, member in obj.__dict__.items():
# Ignore members which are not functions.
			if not is_obj_function(member):
				continue
			if getattr(member,"__module__",None) != obj.__name__:
				continue
# Get docstring. Ignore member if there is none.
			doc = get_obj_docstring(member)
			if not doc:
				continue
# Determine validity for warning purposes
			try:
				tmp_tr = tracer()
				validate_docstring(tmp_tr,member)
				functions_with_valid_docstring.add(name_of_member)
			except Exception:
				pass
# Validate only if function is listed
			if name_of_member in public_functions:
# Push member name to tracer.
				with traced_section(tr, name_of_member):
					try:
# Validate and collect messages from lower levels
						validate_docstring(tr,member, None, None)
						valid_functions.add(name_of_member)
					except Exception:
# Add message from higher level for clarity (should-level rule).
						warn_validation(tr,obj,"MPFN-007",f"Module {obj.__name__}: function '{name_of_member}' is listed in Public_functions but has no valid docstring.")

		with traced_section(tr, "Public_functions"):
# Rule: every function with a valid docstring should be listed
			missing_in_public = functions_with_valid_docstring - public_functions
			for name_of_member in missing_in_public:
				warn_validation(tr,obj,"MPFN-006",f"Module {obj.__name__}: function '{name_of_member}' has a docstring but is not listed in Public_functions.")
# Rule: every function listed should have a valid docstring (warn)
			for name_of_member in public_functions:
				if name_of_member in valid_functions:
					continue
				if not hasattr(obj, name_of_member):
					details = render_listed_object_missing_details("Public_functions", name_of_member, "<remove entry or implement matching object>", "module")
					raise_validation_error(tr,obj,"MPFN-004",f"Function '{name_of_member}' listed in Public_functions has no matching object.", details)
				func_obj = getattr(obj, name_of_member)
				if not is_obj_function(func_obj):
					details = render_name_object_consistency_details("Public_functions", public_functions, "module")
					raise_validation_error(tr,obj,"MPFN-005",f"Member '{name_of_member}' listed in Public_functions is not a function.", details)
				doc_f2 = get_obj_docstring(func_obj)
				if not doc_f2.strip():
					warn_validation(tr,obj,"MPFN-007",f"Module {obj.__name__}: function '{name_of_member}' is listed in Public_functions but has no valid docstring.")
					continue
				validate_docstring(tr,func_obj, None, None)

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
		|Must| ensure that each type listed in the module's |label|`Public_types` section exists in the module.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The module object to be validated.
	doc_module:
		Already parsed module docstring tree for |var|`obj`.
Returns:
	|Must| return |None|.
Raises:
	ValidationError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not isinstance(doc_module, docitem_docstring_module):
			raise TypeError("doc_module must be a docitem_docstring_module instance")
# Collect declared public types from module docstring
# checked elseqhere
#		public_types: set[str] = _get_public_section_entries(doc_module,"Public_types",docitem_public_types)
# Rule: every type listed must exist
#		with traced_section(tr, "Public_types"):
#			for type_name in public_types:
#				if not hasattr(obj, type_name):
#					raise_validation_error(tr,obj,"MPTYP-005",f"Module {obj.__name__}: type '{type_name}' listed in Public_types but does not exist.")

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
		|Must| ensure that each constant listed in the module's |label|`Public_constants` section exists in the module.
		|Must| ensure that each constant listed in the module's |label|`Public_constants` is either annotated as |type|`Final` or not annotated at all.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The module object to be validated.
	doc_module:
		Already parsed module docstring tree for |var|`obj`.
Returns:
	|Must| return |None|.
Raises:
	ValidationError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not isinstance(doc_module, docitem_docstring_module):
			raise TypeError("doc_module must be a docitem_docstring_module instance")
# Collect declared public constants from module docstring
# checked elsewhere
#		public_constants: set[str] = _get_public_section_entries(doc_module,"Public_constants",docitem_public_constants)
# Rule: every constant listed must exist
#		with traced_section(tr, "Public_constants"):
#			for const_name in public_constants:
#				if not hasattr(obj, const_name):
#					raise_validation_error(tr,obj,"MPCON-005",f"Module {obj.__name__}: constant '{const_name}' listed in Public_constants but does not exist.")
# Make sure all constants are annotated as Final.
#				if is_attr_annotated(obj,const_name):
#					if not is_attr_final(obj,const_name):
#						raise_validation_error(tr,obj,"MPCON-006",f"Module {obj.__name__}: constant '{const_name}' listed in Public_constants but is not annotated as 'Final'.")

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
		|Must| ensure that each variable listed in the module's |label|`Public_variables` section exists in the module.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The module object to be validated.
	doc_module:
		Already parsed module docstring tree for |var|`obj`.
Returns:
	|Must| return |None|.
Raises:
	ValidationError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not isinstance(doc_module, docitem_docstring_module):
			raise TypeError("doc_module must be a docitem_docstring_module instance")
# Collect declared public variables from module docstring
# checked elsewhere
#		public_variables: set[str] = _get_public_section_entries(doc_module,"Public_variables",docitem_public_variables)
# Rule: every variable listed must exist
#		with traced_section(tr, "Public_variables"):
#			for const_name in public_variables:
#				if not hasattr(obj, const_name):
#					raise_validation_error(tr,obj,"MPVAR-005",f"Module {obj.__name__}: variable '{const_name}' listed in Public_variables but does not exist.")
# Make sure all variables are annotated as Final.
#				if is_attr_annotated(obj,const_name):
#					if is_attr_final(obj,const_name):
#						raise_validation_error(tr,obj,"MPVAR-009",f"Module {obj.__name__}: variable '{const_name}' listed in Public_variables but is annotated as 'Final'.")

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
		|Must| validate for class, method, type, constant, and variable coverage by calling the specific coverage validators.
Parameters:
	tr:
		Tracer for providing context and collecting warnings.
	obj:
		The class object to be validated.
Returns:
	|Must| return |None|.
Raises:
	ValidationError:
		|Must| propagate exceptions from subordinate coverage validators.
Notes:
	todo:
		Missing: class-type-coverage.
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not is_obj_class(obj):
			raise TypeError(f"{obj.__class__.__name__} is not a class object")
		top = validate_docstring(tr,obj)
		assert isinstance(top, docitem_docstring_class)
		validate_class_class_coverage(tr,obj, top)
		validate_class_method_coverage(tr,obj, top)
		validate_class_type_coverage(tr,obj, top)
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
	ValidationError:
		|Must| raise if validation fails.
	"""
	with traced_section(tr, get_obj_name(obj)):
		if not is_obj_module(obj):
			raise TypeError(f"{obj.__class__.__name__} is not a module object")
		top = validate_docstring(tr,obj)
		assert isinstance(top, docitem_docstring_module)
		validate_module_class_coverage(tr,obj, top)
		validate_module_function_coverage(tr,obj, top)
		validate_module_type_coverage(tr,obj, top)
		validate_module_constant_coverage(tr,obj, top)
		validate_module_variable_coverage(tr,obj, top)
