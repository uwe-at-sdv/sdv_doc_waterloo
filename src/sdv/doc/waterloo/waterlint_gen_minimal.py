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
		|Must| provide the gen-minimal plugin for Waterloo docstring template generation.
Public_functions:
	gen_minimal_command, build_parser
Function_overview:
	gen_minimal_command:
		Build and write a minimal Waterloo docstring template.
		The current waterlint version is passed in by the main program for tracer metadata.
	build_parser:
		Construct and return the argparse subparser for the gen-minimal command.
"""

from __future__ import annotations

import argparse

from sdv.doc.waterloo import waterlint_common as wl_common
from sdv.doc.waterloo import waterlint_generate_common as gen_common


def gen_minimal_command(args: argparse.Namespace, waterlint_version: str) -> int:
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
			|Must| run the gen-minimal command implementation.
	Parameters:
		args:
			Parsed gen-minimal command line options.
		waterlint_version:
			Version string supplied by the main program for tracer metadata.
	Returns:
		|Must| return 0 on success, non-zero on validation or processing errors.
	Raises:
	"""
	return gen_common.gen_minimal_command(args, waterlint_version)


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
			|Must| construct and return the argparse subparser for the gen-minimal command.
	Parameters:
		subparsers:
			The argparse subparser registry of the main command line interface.
		parser_parts:
			Shared parser parts provided by the main program. This command uses the formatter class and the common base-directory parser.
	Returns:
		|Must| return the configured gen-minimal subparser.
	Raises:
	"""
	return gen_common.build_parser(
		subparsers,
		parser_parts,
		"gen-minimal",
		"Generate minimal Waterloo docstring skeletons.",
	)
