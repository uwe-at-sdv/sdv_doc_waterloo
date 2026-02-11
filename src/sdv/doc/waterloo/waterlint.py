#!/usr/bin/env python3
"""
Command line tool for validating and analyzing Waterloo docstrings.
Implementation follows the normative specification in doc/source/tools.rst.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import io
import importlib.util
import sys,inspect
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Optional, Tuple, cast

import json

from jsonpointer import JsonPointerException, resolve_pointer
from jsonschema import Draft202012Validator

_debug = False

# Import project modules while redirecting noisy stdout prints to stderr to
# satisfy the requirement that stdout stays clean unless explicitly written.
with contextlib.redirect_stdout(sys.stderr):
	try:
		import sdv_doc_docitem as docitem
		import sdv_doc_docitem_convert as cvrt
		import sdv_doc_docitem_tokenizer as tokenizer
		from sdv_doc_docitem_helper import (
			tracer,
			get_obj_name,
			ValidationError,
			ParseError,
			SectionNotFoundError,
			SubsectionNotFoundError,
			SCOPE_TAG_MAP,
		)
	except ImportError:
		import sdv.doc.waterloo.docitem as docitem		# type: ignore[no-redef]
		import sdv.doc.waterloo.docitem_convert as cvrt		# type: ignore[no-redef]
		import sdv.doc.waterloo.docitem_tokenizer as tokenizer	# type: ignore[no-redef]
		from sdv.doc.waterloo.docitem_helper import (		# type: ignore[no-redef]
			tracer,
			get_obj_name,
			ValidationError,
			ParseError,
			SectionNotFoundError,
			SubsectionNotFoundError,
			SCOPE_TAG_MAP,
		)

#===== Constants ==============================================#

#----- Add subcommands here -----------------------------------#
WTRL_JSON_SCHEMA_VERSION = "0.0.1"
SUBCOMMANDS = ("validate","coverage","extract","validate-json","render-json")

#===== Helper =================================================#

def _emit_diagnostics(tr: tracer, dest: io.TextIOBase) -> None:
	for msg in tr.gen_infos():
		print(f"Info: {msg}", file=dest)
	for rule_ids, msg in tr.gen_errors():
		rule_txt = ""
		if rule_ids:
			rule_txt = f"[Rules: {', '.join(rule_ids)}] "
		print(f"Error: {rule_txt}{msg}", file=dest)
	for rule_ids, msg in tr.gen_warnings():
		rule_txt = ""
		if rule_ids:
			rule_txt = f"[Rules: {', '.join(rule_ids)}] "
		print(f"Warning: {rule_txt}{msg}", file=dest)
	if _debug:
		for msg in tr.gen_infos():
			print(f"Info: {msg}", file=dest)


def _final_exit_code(base_code: int, tr: tracer, fail_on_warning: bool) -> int:
	code = base_code
	if tr.has_errors():
		code = 1
	if code == 0 and fail_on_warning and tr.has_warnings():
		code = 1
	return code


def _emit_tracer(tr: tracer, out_path: str | None) -> None:
	if out_path:
		with open(out_path, "w", encoding="utf-8") as fh:
			_emit_diagnostics(tr, fh)
	else:
		_emit_diagnostics(tr, sys.stderr) # type: ignore[arg-type]


def _load_json(path: str | None) -> cvrt.WtrlJsonNode_t:
	if path:
		with open(path, "r", encoding="utf-8") as fh:
			return cast(cvrt.WtrlJsonNode_t, json.load(fh))
	return cast(cvrt.WtrlJsonNode_t, json.load(sys.stdin))


def _safe_module_docstring(modname: str) -> str | None:
	try:
		spec = importlib.util.find_spec(modname)
		if spec is None or spec.origin is None or spec.origin == "built-in":
			return None
		path = Path(spec.origin)
		if not path.is_file():
			return None
		src = path.read_text(encoding="utf-8")
		mod_ast = ast.parse(src)
		return ast.get_docstring(mod_ast)
	except Exception:
		return None


def _validate_json_against_schema(tr: tracer, doc: cvrt.WtrlJsonNode_t, schema_path: str) -> None:
	schema = _load_json(schema_path)
	validator = Draft202012Validator(schema)
	errors = sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
	for e in errors:
		path_txt = "/".join(str(p) for p in e.path) or "<root>"
		tr.add_error(["JSCH-001"], f"{path_txt}: {e.message}")


def _check_toc_pointers_json(tr: tracer, doc: cvrt.WtrlJsonNode_t, toc_key: str, rule_id: str) -> None:
	if not isinstance(doc, dict):
		tr.add_error([rule_id], f"document is not a dict, so cannot be valid.")
		return
	toc = doc.get(toc_key, {})
	if not isinstance(toc, dict):
		tr.add_error([rule_id], f"{toc_key} is not an object")
		return
	for name, ptr in toc.items():
		if not isinstance(ptr, str):
			tr.add_error([rule_id], f"{toc_key}.{name}: pointer is not a string")
			continue
		try:
			resolve_pointer(doc, ptr)
		except JsonPointerException as exc:
			tr.add_error([rule_id], f"{toc_key}.{name}: {ptr} -> {exc}")


def _read_docstring_from_file(path: str) -> str:
	with open(path, "r", encoding="utf-8") as f:
		return f.read()


def _read_docstring_from_stdin() -> str:
	return sys.stdin.read()


def _resolve_object(qname: str) -> object:
	# current_obj is not needed for fully qualified names; use None as context.
	obj, _ = docitem.resolve_object(qname, None)
	return obj


def _apply_basedir(basedir: str | None, qname: str | None) -> None:
	if not qname:
		return
# No basedir passed? Done.
	if not basedir:
		return
# Resolve basedir to absolute path.
	base_abs = basedir if basedir.startswith("/") else str((Path.cwd() / basedir).resolve())
# Not a dir? Error.
	if not Path(base_abs).is_dir():
		raise RuntimeError(f"basedir is not a directory: {basedir}")
# Update sys.path with basedir, so that we have a chance to find the module.
	if base_abs not in sys.path:
		sys.path.insert(0, base_abs)

# Yet we need more tricks...
# The main problem is to enforce that qname is really imported
# from the path specified in basedir, not from a local installation
# in ~/.local or from a system installation in /usr/local.
	parts = qname.split(".")
	prefixes: list[str] = []
	for i in range(1, len(parts) + 1):
		pfx = ".".join(parts[:i])
		pfx_path = Path(base_abs, *parts[:i])
		if pfx_path.is_dir():
			prefixes.append(pfx)
		else:
			break
# Example: For --obj sdv.doc.waterloo.docitem, prefixes is ['sdv', 'sdv.doc', 'sdv.doc.waterloo']

# Iterate over the prefixes.
	for pfx in prefixes:
# Combine with the basedir and make a path from the prefixes.
		pfx_path = Path(base_abs, *pfx.split("."))
		if pfx in sys.modules:
			mod = sys.modules[pfx]
			if hasattr(mod, "__path__"):
				paths = list(mod.__path__)
				if str(pfx_path) not in paths:
					paths.insert(0, str(pfx_path))
					mod.__path__ = paths
			continue
		spec = importlib.util.spec_from_loader(pfx, loader=None, origin="namespace")
		if spec is None:
			continue
		mod = importlib.util.module_from_spec(spec)
		mod.__path__ = [str(pfx_path)]
		sys.modules[pfx] = mod

#===== Validate ===============================================#

def _validate_command(args: argparse.Namespace) -> int:
	tr = tracer()
	if getattr(args, "ignore", None):
		for rule in args.ignore.split():
			try:
				tr.add_ignore_rule(rule)
			except RuntimeError as exc:
				print(f"Error: {exc}", file=sys.stderr)
				return 2
	try:
		if args.obj:
			_apply_basedir(getattr(args, "basedir", None), args.obj)
			obj = _resolve_object(args.obj)
# We have an object, so let's use the tracer!
			with docitem.traced_section(tr, get_obj_name(obj)):
				docitem.validate_docstring(tr, obj, None, None)
		else:
# Read from file or stdin.
			if args.input_file:
				doc_txt = _read_docstring_from_file(args.input_file)
			else:
				doc_txt = _read_docstring_from_stdin()

# Structural check only: parse docstring; semantic validation needs --obj.
			di_node : docitem.docitem_base = docitem.make_docitem_tree(tr,doc_txt)
			print(
				"Note: no --obj provided, performed structural parse only.",
				file=sys.stderr,
			)
# Check these first, otherwise RuntimeError will shadow some of them.
	except (ImportError,IndexError,NameError,AssertionError,NotImplementedError,AttributeError):
# Implementation error
		raise
	except ValidationError as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1
	except ParseError as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1
	except RuntimeError as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1
	except Exception as exc:  # pragma: no cover - defensive
		print(f"Error: {exc}", file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1

	_emit_tracer(tr, args.out_diag)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Coverage ===============================================#

def _coverage_command(args: argparse.Namespace) -> int:
	tr = tracer()
	if not args.obj:
		print("Error: --obj is required for coverage.", file=sys.stderr)
		return 2
	try:
		_apply_basedir(getattr(args, "basedir", None), args.obj)
		obj = _resolve_object(args.obj)
# We have an object, so let's use the tracer!
		with docitem.traced_section(tr, get_obj_name(obj)):
			if isinstance(obj, ModuleType):
				docitem.validate_module_coverage(tr, obj)
			elif isinstance(obj, type):
				docitem.validate_class_coverage(tr, obj)
			elif callable(obj):
				print("Error: coverage for callables is not supported.", file=sys.stderr)
				return 1
			else:
				print("Error: --obj must resolve to module or class for coverage.", file=sys.stderr)
				return 1
# Check these first, otherwise RuntimeError will shadow some of them.
	except (IndexError,NameError,AssertionError,NotImplementedError,AttributeError):
# Implementation error
		raise
	except ValidationError as exc:
		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1
	except ParseError as exc:
		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1
	except RuntimeError as exc:
		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1
	except Exception as exc:  # pragma: no cover - defensive
		print(f"Error: {exc}", file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1

	_emit_tracer(tr, args.out_diag)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Extract ================================================#

def _extract_command(args: argparse.Namespace) -> int:
	tr = tracer()
	try:
		if args.subsection and not args.section:
			print("Error: --subsection requires --section.", file=sys.stderr)
			return 2
		if args.obj:
			_apply_basedir(getattr(args, "basedir", None), args.obj)
			obj = _resolve_object(args.obj)
			doc_txt = getattr(obj, "__doc__", None)
			if not isinstance(doc_txt, str):
				print("Error: resolved object has no docstring.", file=sys.stderr)
				return 1
		elif args.input_file:
			doc_txt = _read_docstring_from_file(args.input_file)
		else:
			doc_txt = _read_docstring_from_stdin()

		tree = tokenizer.parse_indent_docstring(tr, doc_txt)

		if args.section:
			if args.subsection:
				subtree = tokenizer.get_tree_of_subsection(tr, tree, args.section, args.subsection)
				out = tokenizer.to_string_tree(subtree)
			else:
				subtree = tokenizer.get_tree_of_section(tr, tree, args.section)
				out = tokenizer.to_string_tree(subtree)
		else:
			out = tokenizer.to_string_tree(tree)

		sys.stdout.write(out)
	except (SectionNotFoundError, SubsectionNotFoundError) as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1
	except ValidationError as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1
	except ParseError as exc:
#		print(str(exc), file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1
	except Exception as exc:  # pragma: no cover - defensive
		print(f"Error: {exc}", file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1

	_emit_tracer(tr, args.out_diag)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Validate JSON ==========================================#

def _validate_json_command(args: argparse.Namespace) -> int:
	tr = tracer()
	try:
		doc = _load_json(getattr(args, "input_file", None))
		_validate_json_against_schema(tr, doc, args.schema)
		_check_toc_pointers_json(tr, doc, "__WTRL_TOC_MODULES__", "JPTR-001")
		_check_toc_pointers_json(tr, doc, "__WTRL_TOC_CLASSES__", "JPTR-002")
		_check_toc_pointers_json(tr, doc, "__WTRL_TOC_CALLABLES__", "JPTR-003")
	except (IndexError, NameError, AssertionError, NotImplementedError, AttributeError):
		raise
	except Exception as exc:  # pragma: no cover - defensive
		tr.add_error(["JSCH-001"], str(exc))
		_emit_tracer(tr, args.out_diag)
		return 1

	_emit_tracer(tr, args.out_diag)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Render JSON ============================================#

def _render_json_command(args: argparse.Namespace) -> int:
	def _collect_public_members(tree: docitem.docitem_base,label: str) -> list[str]:
		"""Extract unqualified type names from Public_types section (if present)."""
		try:
			if not tree.has_item(label):
				return []
			node = tree.item(label)
			items = [str(it).strip() for it in node.items() if str(it).strip()]
			return items
		except Exception as e:
			return []
	tr = tracer()
#----- Security note: local paths -----------------------------#
	if getattr(args, "allow_local_paths", True):
		tr.add_info("Result JSON contains local filesystem paths; disable with --no-allow-local-paths.")
	try:
		flavour_str = args.flavour
		flavour = cvrt.flavour_tag_map.get(flavour_str)

		if not args.obj:
			print("Error: --obj is required for render-json.", file=sys.stderr)
			return 2

		modules: list[ModuleType] = []
		for qname in args.obj:
			_apply_basedir(getattr(args, "basedir", None), qname)
			mod_obj = _resolve_object(qname)
			if not isinstance(mod_obj, ModuleType):
				print(f"Error: --obj must resolve to modules for render-json (got {qname}).", file=sys.stderr)
				return 2
			modules.append(mod_obj)

#----- Object traversal and config
		config = docitem.ConfigTraversal()
		if args.include_imported:
			config.enable_include_imported()
		config.disable_walk_packages()
#----- Filter by scope ----------------------------------------#
		objs: list[object] = []
		for mod in modules:
			objs.extend(docitem.gen_documentable_objects(mod, config))
# Use from argparse if available, otherwise fall back to "core" (maximimum output).
		scope_str: str = args.scope
		scope_filter = SCOPE_TAG_MAP.get(scope_str)

#----- Build version, legend and table of contents ------------#
		tree_full: dict[str, Any] = {}
		tree_full["$schema"] = "https://json-schema.org/draft/2020-12/schema"
		tree_full["$id"] = f"https://sci-d-vis.com/schema/wtrl-json-{WTRL_JSON_SCHEMA_VERSION}.schema.json"
		
#..... VERSION ................................................#
		tree_full["__WTRL_VERSION__"] = {
			"waterloo": docitem.__version__,
			"schema": WTRL_JSON_SCHEMA_VERSION,
			}
#..... META ...................................................#
		now = datetime.now().astimezone()
		date_time: str = now.isoformat(timespec='seconds')
		tree_full["__WTRL_META__"] = {
			"generated_at": date_time,
			"generator": "waterlint",
			"scope":scope_str,
			"flavour":flavour_str
			}
#..... Content ................................................#
		tree_full["__WTRL_ROLES__"] = cvrt.to_node_legend_json()
		tree_full["__WTRL_TOC_MODULES__"] = {}
		tree_full["__WTRL_TOC_CLASSES__"] = {}
		tree_full["__WTRL_TOC_CALLABLES__"] = {}
		tree_full["__WTRL_TOC_TYPES__"] = {}
		tree_full["__WTRL_TOC_VARIABLES__"] = {}
		tree_full["__WTRL_TOC_CONSTANTS__"] = {}
		tree_full["__WTRL_OBJECTS__"] = {}

		nonaggregate_member_sections: list[Tuple[str,str]] = [
			("Public_types","__WTRL_TOC_TYPES__"),
			("Public_variables","__WTRL_TOC_VARIABLES__"),
			("Public_constants","__WTRL_TOC_CONSTANTS__")
			]
# Statistics
		num_modules_skipped_no_doc = 0
		num_modules_skipped_invalid = 0
		num_classes_skipped_no_doc = 0
		num_classes_skipped_invalid = 0
		num_callables_skipped_no_doc = 0
		num_callables_skipped_invalid = 0
		num_unknown_skipped_no_doc = 0
		num_unknown_skipped_invalid = 0
		num_modules_rendered = 0
		num_classes_rendered = 0
		num_callables_rendered = 0

#----- Seen, counted, visited ---------------------------------#
		objects_counted: set[str] = set()
		modules_used: set[str] = set()
		modules_rendered: set[str] = set()
		public_members_rendered: set[str] = set()

#----- Iterate over scope-filtered objects --------------------#
		for o in objs:
			doc_txt = docitem.get_obj_docstring(o)
			if not doc_txt or not str(doc_txt).strip():
# No docstring or empty docstring
				if cvrt.is_obj_module(o):
					num_modules_skipped_no_doc += 1
				elif cvrt.is_obj_class(o):
					num_classes_skipped_no_doc += 1
				elif cvrt.is_obj_function(o):
					num_callables_skipped_no_doc += 1
				else:
					num_unknown_skipped_no_doc += 1
				continue
			tr_obj = tracer()
			try:
# Build docstring tree from docstring.
				tree_parsed = docitem.parse_indent_docstring(tr_obj, doc_txt)
				tree = docitem.make_docitem_tree_from_docstring_tree(tr_obj, tree_parsed)
			except docitem.ParseError:
# Invalid docstring -> skip
				if cvrt.is_obj_module(o):
					num_modules_skipped_invalid += 1
				elif cvrt.is_obj_class(o):
					num_classes_skipped_invalid += 1
				elif cvrt.is_obj_function(o):
					num_callables_skipped_invalid += 1
				else:
					num_unknown_skipped_invalid += 1
				continue
			if not cast(Any, tree).is_visible(set([scope_filter])):
				continue
# All entries are based on the qualified name, which is delivered by our helper.
			qname = docitem.get_obj_name(o)
			if getattr(o, "__module__", None):
				qname = f"{o.__module__}.{qname}"
# Collect nonaggregate public members for this object (module or class).
			for sec_label,toc_label in nonaggregate_member_sections:
				for mem_name in _collect_public_members(tree,sec_label):
					mem_qname = f"{qname}.{mem_name}"
					if mem_qname not in public_members_rendered:
						public_members_rendered.add(mem_qname)
						tree_full[toc_label][mem_qname] = f"/__WTRL_OBJECTS__/{mem_qname}"
# The docstring subsection of a type is an array of logical lines. We render them as a list in JSON.
						mem_doc = tree.item(sec_label).item(mem_name).items()
						tree_full["__WTRL_OBJECTS__"].setdefault(mem_qname, {"doc": mem_doc})
#..... begin properties .......................................#
# We're still in the nonaggregate case! Properties fall in this category.
# Extract and check if it is a property
						prop_obj = inspect.getattr_static(o, mem_name)
						if isinstance(prop_obj, property):
# Extract method objects
							objs_meth_prop: list[Tuple[Callable[...,Any],str]] = []
# Check for existence, just to be sure. Insert only if it is a method object.
							for attr_name in ("fget", "fset", "fdel"):
								meth = getattr(prop_obj, attr_name)
								if meth is not None:
									objs_meth_prop.append((meth,qname + "." + mem_name + "." + attr_name))
# Iterate over {fget, fset, fdel}, if available.
							for obj_prop_meth,qname_prop_meth in objs_meth_prop:
								doc_prop_meth = docitem.get_obj_docstring(obj_prop_meth)
								if not doc_prop_meth or not str(doc_prop_meth).strip():
# No docstring or empty docstring
									num_callables_skipped_no_doc += 1
								tr_prop_meth_obj = tracer()
								try:
# Build docstring tree from docstring.
									tree_prop_meth = docitem.parse_indent_docstring(tr_prop_meth_obj, doc_prop_meth)
									node_prop_meth = docitem.make_docitem_tree_from_docstring_tree(tr_prop_meth_obj, tree_parsed)
								except docitem.ParseError:
# Invalid docstring -> skip
									num_callables_skipped_invalid += 1
									continue

								tree_full["__WTRL_TOC_CALLABLES__"][qname_prop_meth] = f"/__WTRL_OBJECTS__/{qname_prop_meth}"
								tree_sig_prop_meth = cvrt.to_node_signature_json(obj_prop_meth)
# Count callable safely as rendered.
								if qname_prop_meth not in objects_counted:
									num_callables_rendered += 1
									objects_counted.add(qname_prop_meth)
# Docstring handling: same for modules, classes, and callables.
								tree_doc = cvrt.to_node_docstring_tree_json(tree_prop_meth, flavour)
								entry_prop_meth = tree_sig_prop_meth | {"doc": tree_doc}
								tree_full["__WTRL_OBJECTS__"][qname_prop_meth] = entry_prop_meth
#..... end properties .........................................#


			# toc + signature
			tree_sig: dict[str, cvrt.WtrlJsonNode_t] = {}
# Regular cases for the object from traversal
			if cvrt.is_obj_module(o):
				modules_used.add(docitem.get_obj_name(o))
				tree_full["__WTRL_TOC_MODULES__"][qname] = f"/__WTRL_OBJECTS__/{qname}"
# Store path if we allow this (security issue b/c local file system structure is unveiled).
				tree_full["__WTRL_OBJECTS__"][qname] = {"path": docitem.get_obj_path(o)} if args.allow_local_paths else {}
# Count module safely as rendered.
				if qname not in modules_rendered:
					modules_rendered.add(qname)
				if qname not in objects_counted:
					num_modules_rendered += 1
					objects_counted.add(qname)
			elif cvrt.is_obj_class(o):
				tree_full["__WTRL_TOC_CLASSES__"][qname] = f"/__WTRL_OBJECTS__/{qname}"
				ctor = getattr(o, "__init__", None)
				if callable(ctor):
					tree_sig = cvrt.to_node_signature_json(cast(Callable[..., Any], ctor))
# Count class safely as rendered.
				if qname not in objects_counted:
					num_classes_rendered += 1
					objects_counted.add(qname)
			elif cvrt.is_obj_function(o):
				tree_full["__WTRL_TOC_CALLABLES__"][qname] = f"/__WTRL_OBJECTS__/{qname}"
				tree_sig = cvrt.to_node_signature_json(o)
# Count callable safely as rendered.
				if qname not in objects_counted:
					num_callables_rendered += 1
					objects_counted.add(qname)
# Docstring handling: same for modules, classes, and callables.
			tree_doc = cvrt.to_node_docstring_tree_json(tree_parsed, flavour)
			entry = tree_sig | {"doc": tree_doc}
			if args.allow_local_paths and isinstance(o, ModuleType):
				entry = {"path": docitem.get_obj_path(o)} | entry
			tree_full["__WTRL_OBJECTS__"][qname] = entry

#----- begin modules referred to by objects from traversal ----#
# We would like to see each module referred to by any of the rendered objects
# in the module TOC ans __WTRL_OBJECTS__ section. So, extract module and keep in mind.
			modname = docitem.get_obj_name(o) if isinstance(o, ModuleType) else getattr(o, "__module__", None)
			if modname:
				modules_used.add(modname)
# Add referred module name to TOC.
				jsnode_toc_modules:dict[str, cvrt.WtrlJsonNode_t] = tree_full["__WTRL_TOC_MODULES__"]
				if modname not in jsnode_toc_modules:
					jsnode_toc_modules[modname] = f"/__WTRL_OBJECTS__/{modname}"
# Add referred module name to __WTRL_OBJECTS__, with empty "doc" node.
				if modname not in tree_full["__WTRL_OBJECTS__"]:
					entry: dict[str, cvrt.WtrlJsonNode_t] = {}
# We already know the path to the module.
					if args.allow_local_paths:
						entry["path"] = docitem.get_obj_path(sys.modules.get(modname))
# Leave empty, fill later after AST analysis.
					entry["doc"] = {}
					tree_full["__WTRL_OBJECTS__"][modname] = entry
#----- end modules referred to by objects from traversal ------#
# End of object loop.

#----- begin modules referred to by objects from traversal ----#
		# ensure all referenced modules appear in TOC/OBJECTS
		for modname in sorted(modules_used):
			if modname not in modules_rendered:
				entry2: dict[str, cvrt.WtrlJsonNode_t] = cast(dict[str, cvrt.WtrlJsonNode_t],tree_full["__WTRL_OBJECTS__"].get(modname, {}))
				if args.allow_local_paths and "path" not in entry2:
					entry2["path"] = docitem.get_obj_path(sys.modules.get(modname))
# Various attempts to get the module docstring.
				mod_doc = None
				mod_obj = sys.modules.get(modname)
				if mod_obj is not None:
					mod_doc = docitem.get_obj_docstring(mod_obj)
# Scan python AST in order to get module docstring!
				if not mod_doc:
					mod_doc = _safe_module_docstring(modname)
				if mod_doc:
					try:
						tr_tmp = tracer()
						mod_tree_parsed = docitem.parse_indent_docstring(tr_tmp, mod_doc)
						mod_tree = docitem.make_docitem_tree_from_docstring_tree(tr_tmp, mod_tree_parsed)
# Render module docstring if the module is visible for the given scope; otherwise render stub.
						if cast(Any, mod_tree).is_visible(set([scope_filter])):
							entry2["doc"] = cvrt.to_node_docstring_tree_json(mod_tree_parsed, flavour)
						else:
							entry2["doc"] = {}
# In both cases consider module as done.
						if modname not in modules_rendered:
							modules_rendered.add(modname)
# Count referenced module safely as rendered.
							if modname not in objects_counted:
								num_modules_rendered += 1
								objects_counted.add(modname)
# Collect nonaggregate public members for this object (module).
						for sec_label,toc_label in nonaggregate_member_sections:
							for mem_name in _collect_public_members(mod_tree,sec_label):
# The qualified name is constructed from the module name and the member name.
								mem_qname = f"{modname}.{mem_name}"
								if mem_qname not in public_members_rendered:
									public_members_rendered.add(mem_qname)
									tree_full[toc_label][mem_qname] = f"/__WTRL_OBJECTS__/{mem_name}"
# The docstring subsection of a type is an array of logical lines. We render them as a list in JSON.
									mem_doc = mod_tree.item(sec_label).item(mem_name).items()
									tree_full["__WTRL_OBJECTS__"].setdefault(mem_qname, {"doc": mem_doc})
					except Exception:
						entry2["doc"] = {}
				else:
					entry2["doc"] = {}
				tree_full["__WTRL_OBJECTS__"][modname] = entry2
#----- end modules referred to by objects from traversal ------#

#----- Store diagnostics. Don't change without updating pytest #
		tr.add_info(f"Num modules skipped (no docstring / invalid)  : {num_modules_skipped_no_doc} / {num_modules_skipped_invalid}.")
		tr.add_info(f"Num classes skipped (no docstring / invalid)  : {num_classes_skipped_no_doc} / {num_classes_skipped_invalid}.")
		tr.add_info(f"Num callables skipped (no docstring / invalid): {num_callables_skipped_no_doc} / {num_callables_skipped_invalid}.")
		tr.add_info(f"Num <unknown> skipped (no docstring / invalid): {num_unknown_skipped_no_doc} / {num_unknown_skipped_invalid}.")
		tr.add_info(f"Num modules rendered  : {num_modules_rendered}.")
		tr.add_info(f"Num classes rendered  : {num_classes_rendered}.")
		tr.add_info(f"Num callables rendered: {num_callables_rendered}.")

#----- Dump JSON result ---------------------------------------#
		if args.out_file:
			with open(args.out_file, "w", encoding="utf-8") as fh:
				json.dump(tree_full, fh, indent=4)
		else:
			json.dump(tree_full, sys.stdout, indent=4)
			sys.stdout.write("\n")
#----- Catch implementation bugs ------------------------------#
	except (IndexError, NameError, AssertionError, NotImplementedError, AttributeError, TypeError):
		raise
#----- Catch errors from rendering JSON -----------------------#
	except Exception as exc:  # pragma: no cover - defensive
		tr.add_error(["JSCH-001"], str(exc))
		_emit_tracer(tr, args.out_diag)
		return 1

	_emit_tracer(tr, args.out_diag)
	return _final_exit_code(0, tr, args.fail_on_warning)

#===== Help topic  ============================================#

def _help_validate() -> None:
	print("Validate a docstring.")

def _help_coverage() -> None:
	print("Check for documentation coverage of a module or class.")

def _help_extract() -> None:
	print("Extract some portion of a docstring.")

def _help_validate_json() -> None:
	print("Validate a Waterloo JSON document against the published JSON Schema.")

def _help_render_json() -> None:
	print("Render Waterloo objects (module) to Waterloo JSON.")

def _help_topic_command(args: argparse.Namespace) -> int:
	global parser
	assert parser._subparsers is not None
	for action in parser._subparsers._actions:
		if isinstance(action, argparse._SubParsersAction):
			for cmd, subp in action.choices.items():
				if cmd == args.topic:
					print(f"\nSubcommand '{cmd}':")
					subp.print_help()
#----- Add subcommands here -----------------------------------#
					if cmd == "validate":
						_help_validate()
					if cmd == "coverage":
						_help_coverage()
					if cmd == "extract":
						_help_extract()
					if cmd == "validate-json":
						_help_validate_json()
					if cmd == "render-json":
						_help_render_json()
					exit(0)
			allowed = "'" + "', '".join(SUBCOMMANDS) + "'"
			print(f"Command '{args.topic}' not found. Try one of {allowed}.",file=sys.stderr)
	return 0

parser: argparse.ArgumentParser

#===== Build parser ===========================================#

def _build_parser() -> argparse.ArgumentParser:
#----- Main parser --------------------------------------------#
	global parser
	parser = argparse.ArgumentParser(prog="waterlint.py")
	subparsers = parser.add_subparsers(dest="command", required=True)
	parser.add_argument(
		"--help-all",
		action="store_true",
		help="Show help including subcommand details.",
		)

#----- Reusable parsers ---------------------------------------#
	global_opts = argparse.ArgumentParser(add_help=False)
	global_opts.add_argument(
		"--fail-on-warning",
		action="store_true",
		help="Treat warnings as errors (affects exit code).",
	)
	global_opts.add_argument(
		"--out-diag",
		metavar="PATH",
		help="Write tracer diagnostics (errors/warnings) to PATH instead of stderr.",
	)

	common_validate_group = argparse.ArgumentParser(add_help=False)
	common_validate_group.add_argument(
		"--basedir",
		metavar="DIR",
		help="Base directory for resolving objects passed to --obj.",
	)

#----- help-topic ---------------------------------------------#
	help_topic = subparsers.add_parser("help", help="Help on specific topic, e.g. help --topic validate")
	help_topic.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	help_topic.add_argument("--topic", dest="topic", metavar="TOPIC")

#----- validate -----------------------------------------------#
	validate = subparsers.add_parser("validate", help="Validate docstrings", parents=[common_validate_group, global_opts])
	vg = validate.add_mutually_exclusive_group()
	vg.add_argument("--obj", metavar="QUALNAME", help="Qualified identifier of module/class/function/method")
	vg.add_argument("--in", dest="input_file", metavar="FILE", help="Read docstring text from file")
	validate.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	validate.add_argument(
		"--ignore",
		metavar="RULES",
		help="Whitespace-separated list of Rule-IDs to ignore for warnings.",
	)

#----- coverage -----------------------------------------------#
	coverage = subparsers.add_parser("coverage", help="Validate docstring coverage", parents=[global_opts])
	coverage.add_argument(
		"--basedir",
		metavar="DIR",
		help="Base directory for resolving objects passed to --obj.",
	)
	coverage.add_argument("--obj", required=True, metavar="QUALNAME", help="Qualified identifier of module/class")
	coverage.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- extract ------------------------------------------------#
	extract = subparsers.add_parser("extract", help="Extract docstring sections", parents=[global_opts])
	eg = extract.add_mutually_exclusive_group()
	eg.add_argument("--obj", metavar="QUALNAME", help="Qualified identifier of module/class/function/method")
	eg.add_argument("--in", dest="input_file", metavar="FILE", help="Read docstring text from file")
	extract.add_argument(
		"--basedir",
		metavar="DIR",
		help="Base directory for resolving objects passed to --obj.",
	)
	extract.add_argument("--section", metavar="SECTION", help="Section label to extract")
	extract.add_argument("--subsection", metavar="SUBSECTION", help="Subsection label to extract (requires --section)")
	extract.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- validate-json ------------------------------------------#
	validate_json = subparsers.add_parser("validate-json", help="Validate Waterloo JSON output", parents=[global_opts])
	validate_json.add_argument("--in", dest="input_file", metavar="FILE", help="Read JSON from file (default: stdin)")
	validate_json.add_argument("--schema", required=True, metavar="FILE", help="Path to JSON Schema file.")
	validate_json.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

#----- render-json --------------------------------------------#
	render_json = subparsers.add_parser("render-json", help="Render module to Waterloo JSON", parents=[global_opts])
	render_json.add_argument(
		"--obj",
		required=True,
		nargs="+",
		metavar="MODULE",
		help="One or more qualified module names to render (merged).",
	)
	render_json.add_argument("--basedir", metavar="DIR", help="Base directory for resolving --obj.")
	render_json.add_argument("--out", dest="out_file", metavar="FILE", help="Write JSON to FILE instead of stdout.")
	render_json.add_argument("--flavour", choices=["raw","rfc-2119","markdown"], default="rfc-2119", help="Normativity keyword flavour (default: rfc-2119).")
	render_json.add_argument(
		"--scope",
		choices=sorted(SCOPE_TAG_MAP.keys()),
		default="core",
		help="Render only objects visible in the given scope (default: core).",
	)
	render_json.add_argument("--include-imported", dest="include_imported", action="store_true", default=True, help="Include imported members and submodules (default).")
	render_json.add_argument("--no-include-imported", dest="include_imported", action="store_false", help="Do not include imported members/submodules.")
	render_json.add_argument("--allow-local-paths", dest="allow_local_paths", action="store_true", default=True, help="Include filesystem paths in JSON (default).")
	render_json.add_argument("--no-allow-local-paths", dest="allow_local_paths", action="store_false", help="Omit filesystem paths in JSON.")
	render_json.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

	return parser


def main(argv: Optional[list[str]] = None) -> int:
	parser = _build_parser()
	if argv is None:
		argv = sys.argv[1:]
	if "--help-all" in argv:
		parser.print_help()
		assert parser._subparsers is not None
		for action in parser._subparsers._actions:
			if isinstance(action, argparse._SubParsersAction):
				for cmd, subp in action.choices.items():
					print(f"\nSubcommand '{cmd}':")
					subp.print_help()
		return 0

	args = parser.parse_args(argv)
	global _debug
	_debug = args.debug

#----- Add subcommands here -----------------------------------#
	if args.command == "validate":
		return _validate_command(args)
	if args.command == "coverage":
		return _coverage_command(args)
	if args.command == "extract":
		return _extract_command(args)
	if args.command == "validate-json":
		return _validate_json_command(args)
	if args.command == "render-json":
		return _render_json_command(args)
	if args.command == "help":
		return _help_topic_command(args)
	return 1


if __name__ == "__main__":
	sys.exit(main())
