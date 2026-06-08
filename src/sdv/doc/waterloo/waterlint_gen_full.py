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
		|Must| provide the gen-full plugin for Waterloo docstring template generation.
Public_functions:
	gen_full_command, build_parser
Function_overview:
	gen_full_command:
		Build and write a full Waterloo docstring template.
		The current waterlint version is passed in by the main program for tracer metadata.
	build_parser:
		Construct and return the argparse subparser for the gen-full command.
"""

from __future__ import annotations

import argparse

from sdv.doc.waterloo import waterlint_common as wl_common
from sdv.doc.waterloo import waterlint_generate_common as gen_common


def gen_full_command(args: argparse.Namespace, waterlint_version: str) -> int:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| run the gen-full command implementation.
	Parameters:
		args:
			Parsed gen-full command line options.
			|must| provide the attributes expected by this command:
			* |attr|`obj`: one or more qualified object names passed via repeated |opt|`--obj`; each group |must| contain at least one object name.
			* |attr|`fail_on_warning` |must| be present because the common generator uses it for the exit code.
			* |attr|`out_diag` and |attr|`out_diag_json` |may| be present as optional tracer-diagnostics targets.
			* |attr|`basedir` |may| be present to resolve object names relative to a base directory.
			* |attr|`recursive`, |attr|`missing_only`, |attr|`format`, |attr|`out_file`, |attr|`indent`, and |attr|`debug` |may| be present as generation controls.
		waterlint_version:
			Version string supplied by the main program for tracer metadata.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	"""
	return gen_common.gen_full_command(args, waterlint_version)


def build_parser(
	subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
	parser_parts: wl_common.ParserParts_t,
) -> argparse.ArgumentParser:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
		scope:
			extension
	Contract:
		general:
			|Must| construct and return the argparse subparser for the gen-full command.
	Parameters:
		subparsers:
			The argparse subparser registry of the main command line interface.
		parser_parts:
			Shared parser parts provided by the main program. This command uses the formatter class and the common base-directory parser.
	Returns:
		|Must| return the configured gen-full subparser.
	Raises:
	"""
	return gen_common.build_parser(
		subparsers,
		parser_parts,
		"gen-full",
		"Generate full Waterloo docstring skeletons.",
	)
