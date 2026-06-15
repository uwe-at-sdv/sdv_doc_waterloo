#!/usr/bin/env python3

r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_constants
Contract:
	general:
		|Must| demonstrate that Public_constants entries should be Final.
Public_constants:
	MyConstant:
		Not Final
"""

MyConstant: int = 1
