#!/usr/bin/env python3
"""
Command line tool for validating and analyzing Waterloo docstrings.
Implementation follows the normative specification in doc/source/tools.rst.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import sys
from types import ModuleType
from typing import Any, Callable, Optional

_debug = False

# Import project modules while redirecting noisy stdout prints to stderr to
# satisfy the requirement that stdout stays clean unless explicitly written.
with contextlib.redirect_stdout(sys.stderr):
	try:
		import sdv_doc_docitem as docitem
		import sdv_doc_docitem_tokenizer as tokenizer
		from sdv_doc_docitem_helper import (
			tracer,
			ValidationError,
			ParseError,
			SectionNotFoundError,
			SubsectionNotFoundError,
		)
	except ImportError:
		import sdv.doc.waterloo.docitem as docitem
		import sdv.doc.waterloo.docitem_tokenizer as tokenizer
		from sdv.doc.waterloo.docitem_helper import (
			tracer,
			ValidationError,
			ParseError,
			SectionNotFoundError,
			SubsectionNotFoundError,
		)


def _emit_diagnostics(tr: tracer, dest: io.TextIOBase) -> None:
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
	if code == 0 and fail_on_warning and tr.has_warnings():
		code = 1
	return code


def _emit_tracer(tr: tracer, out_path: str | None) -> None:
	if out_path:
		with open(out_path, "w", encoding="utf-8") as fh:
			_emit_diagnostics(tr, fh)
	else:
		_emit_diagnostics(tr, sys.stderr)


def _read_docstring_from_file(path: str) -> str:
	with open(path, "r", encoding="utf-8") as f:
		return f.read()


def _read_docstring_from_stdin() -> str:
	return sys.stdin.read()


def _resolve_object(qname: str) -> object:
	# current_obj is not needed for fully qualified names; use None as context.
	obj, _ = docitem.resolve_object(qname, None)
	return obj


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
			obj = _resolve_object(args.obj)
# We have an object, so let's use the tracer!
			with docitem.traced_section(tr, obj.__name__):
				docitem.validate_docstring(tr, obj, None, None)
		else:
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
	except (IndexError,NameError,AssertionError):
# Implementation error
		raise
	except Exception as exc:  # pragma: no cover - defensive
		print(f"Error: {exc}", file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1

	_emit_tracer(tr, args.out_diag)
	return _final_exit_code(0, tr, args.fail_on_warning)


def _coverage_command(args: argparse.Namespace) -> int:
	tr = tracer()
	if not args.obj:
		print("Error: --obj is required for coverage.", file=sys.stderr)
		return 2
	try:
		obj = _resolve_object(args.obj)
# We have an object, so let's use the tracer!
		with docitem.traced_section(tr, obj.__name__):
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
	except (IndexError,NameError,AssertionError):
# Implementation error
		raise
	except Exception as exc:  # pragma: no cover - defensive
		print(f"Error: {exc}", file=sys.stderr)
		_emit_tracer(tr, args.out_diag)
		return 1

	_emit_tracer(tr, args.out_diag)
	return _final_exit_code(0, tr, args.fail_on_warning)


def _extract_command(args: argparse.Namespace) -> int:
	tr = tracer()
	try:
		if args.subsection and not args.section:
			print("Error: --subsection requires --section.", file=sys.stderr)
			return 2
		if args.obj:
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


def _build_parser() -> argparse.ArgumentParser:
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

	parser = argparse.ArgumentParser(prog="waterlint.py")
	subparsers = parser.add_subparsers(dest="command", required=True)

	common_validate_group = argparse.ArgumentParser(add_help=False)

	# validate
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

	# coverage
	coverage = subparsers.add_parser("coverage", help="Validate docstring coverage", parents=[global_opts])
	coverage.add_argument("--obj", required=True, metavar="QUALNAME", help="Qualified identifier of module/class")
	coverage.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

	# extract
	extract = subparsers.add_parser("extract", help="Extract docstring sections", parents=[global_opts])
	eg = extract.add_mutually_exclusive_group()
	eg.add_argument("--obj", metavar="QUALNAME", help="Qualified identifier of module/class/function/method")
	eg.add_argument("--in", dest="input_file", metavar="FILE", help="Read docstring text from file")
	extract.add_argument("--section", metavar="SECTION", help="Section label to extract")
	extract.add_argument("--subsection", metavar="SUBSECTION", help="Subsection label to extract (requires --section)")
	extract.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")

	return parser


def main(argv: Optional[list[str]] = None) -> int:
	parser = _build_parser()
	args = parser.parse_args(argv)
	global _debug
	_debug = args.debug

	if args.command == "validate":
		return _validate_command(args)
	if args.command == "coverage":
		return _coverage_command(args)
	if args.command == "extract":
		return _extract_command(args)
	return 1


if __name__ == "__main__":
	sys.exit(main())
