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
		|Must| provide the prototype explain-section command for Waterloo diagnostics.
Public_functions:
	explain_section_command, build_parser
Function_overview:
	explain_section_command:
		Render a prototype explanation for a Waterloo section label in raw text or JSON.
	build_parser:
		Construct and return the argparse subparser for the explain-section command.
"""

from __future__ import annotations

import argparse
import json
import sys

from sdv.doc.waterloo import waterlint_common as wl_common
from sdv.doc.waterloo.waterlint_explain_common import get_section_explanation, render_explanation_json, render_explanation_text


def explain_section_command(args: argparse.Namespace) -> int:
	label = getattr(args, "label", None)
	if not isinstance(label, str) or not label:
		print("Missing required section label.", file=sys.stderr)
		return 1
	spec = get_section_explanation(label)
	if spec is None:
		print(f"Unknown section label: {label}", file=sys.stderr)
		return 1
	out_json = getattr(args, "out_json", None)
	out_file = getattr(args, "out_file", None)
	if out_json:
		doc = render_explanation_json(spec)
		with open(out_json, "w", encoding="utf-8") as fh:
			json.dump(doc, fh, indent=4, ensure_ascii=False)
			fh.write("\n")
		return 0
	txt = render_explanation_text(spec)
	if out_file:
		with open(out_file, "w", encoding="utf-8") as fh:
			fh.write(txt)
	else:
		sys.stdout.write(txt)
	return 0


def build_parser(
	subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
	parser_parts: wl_common.ParserParts_t,
) -> argparse.ArgumentParser:
	prsr = subparsers.add_parser(
		"explain-section",
		help="Explain the structure of a Waterloo section",
		parents=[parser_parts["global_opts"]],
		formatter_class=parser_parts["formatter_class"],
	)
	prsr.add_argument("--label", required=True, metavar="LABEL", help="Section label to explain.")
	prsr_out = prsr.add_mutually_exclusive_group()
	prsr_out.add_argument("--out", dest="out_file", metavar="FILE", help="Write raw explanation text to FILE instead of stdout.")
	prsr_out.add_argument("--out-json", dest="out_json", metavar="FILE", help="Write JSON explanation to FILE and suppress raw output.")
	prsr.add_argument("--debug", action="store_true", help="Emit debugging data to stderr (reserved)")
	return prsr
