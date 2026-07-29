#!/usr/bin/env python3
r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_functions
	scope:
		extension
Contract:
	general:
		|Must| provide the prototype explain-subsection command for Waterloo diagnostics.
Public_functions:
	explain_subsection_command, build_parser
Function_overview:
	explain_subsection_command:
		Render a profile-specific explanation for a fully qualified Waterloo subsection label in raw text or JSON.
	build_parser:
		Construct and return the argparse subparser for the explain-subsection command, including the required profile selector.
"""

from __future__ import annotations

import argparse

from sdv.doc.waterloo import waterlint_common as wl_common
from sdv.doc.waterloo.docitem_helper import tracer
from sdv.doc.waterloo.waterlint_explain_common import (
	build_subsection_explanation,
	_emit_explain_tracer,
	render_subsection_explanation_json,
	render_subsection_explanation_text,
)

_PROFILE_CHOICES = ("module", "class", "function", "method", "inherited_method")


def explain_subsection_command(args: argparse.Namespace) -> int:
	tr = tracer()
	tr.push("explain-subsection")
	label = getattr(args, "label", None)
	if not isinstance(label, str) or not label:
		tr.add_error("XPLN-002", "tool", "Missing required subsection label.")
		_emit_explain_tracer(tr, getattr(args, "out_diag", None), getattr(args, "out_diag_json", None), debug=bool(getattr(args, "debug", False)))
		return 1
	if "." not in label:
		tr.add_error("XPLN-003", "tool", "Subsection label must be fully qualified as SECTION.SUBSECTION.")
		_emit_explain_tracer(tr, getattr(args, "out_diag", None), getattr(args, "out_diag_json", None), debug=bool(getattr(args, "debug", False)))
		return 1
	profile = getattr(args, "profile", None)
	if profile not in _PROFILE_CHOICES:
		tr.add_error("XPLN-002", "tool", "Missing required profile.")
		_emit_explain_tracer(tr, getattr(args, "out_diag", None), getattr(args, "out_diag_json", None), debug=bool(getattr(args, "debug", False)))
		return 1
	spec = build_subsection_explanation(label, profile)
	if spec is None:
		tr.add_error("XPLN-002", "tool", f"Unknown subsection label/profile combination: {label} / {profile}")
		_emit_explain_tracer(tr, getattr(args, "out_diag", None), getattr(args, "out_diag_json", None), debug=bool(getattr(args, "debug", False)))
		return 1
	out_json = getattr(args, "out_json", None)
	out_file = getattr(args, "out_file", None)
	if out_json:
		doc = render_subsection_explanation_json(spec)
		wl_common.write_json_output(doc, out_json)
		_emit_explain_tracer(tr, getattr(args, "out_diag", None), getattr(args, "out_diag_json", None), debug=bool(getattr(args, "debug", False)))
		return 0
	txt = render_subsection_explanation_text(spec)
	wl_common.write_text_output(txt, out_file)
	_emit_explain_tracer(tr, getattr(args, "out_diag", None), getattr(args, "out_diag_json", None), debug=bool(getattr(args, "debug", False)))
	return 0


def build_parser(
	subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
	parser_parts: wl_common.ParserParts_t,
) -> argparse.ArgumentParser:
	prsr = subparsers.add_parser(
		"explain-subsection",
		help="Explain a fully qualified Waterloo subsection label for a profile (e.g. Contract.requires or Definitions.<item>)",
		parents=[parser_parts["global_opts"]],
		formatter_class=parser_parts["formatter_class"],
	)
	prsr.add_argument(
		"--label",
		required=True,
		metavar="SECTION.SUBSECTION",
		help="Fully qualified subsection label to explain, for example Contract.requires or Definitions.<item>.",
	)
	prsr.add_argument(
		"--profile",
		required=True,
		choices=list(_PROFILE_CHOICES),
		help="Docstring profile to explain the subsection for.",
	)
	prsr_out = prsr.add_mutually_exclusive_group()
	prsr_out.add_argument(
		"--out",
		dest="out_file",
		metavar="FILE",
		help="Write raw explanation text to FILE instead of stdout.",
	)
	prsr_out.add_argument(
		"--out-json",
		dest="out_json",
		metavar="FILE",
		help="Write JSON explanation to FILE and suppress raw output.",
	)
	prsr.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	return prsr
