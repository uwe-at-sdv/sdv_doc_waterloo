#!/usr/bin/env python3
"""Regression fixture for inherited methods whose base lives in another module."""

from pytest_good_inheritance import X


class Y(X):
	def spam(self) -> None:
		"""
Preamble:
	profile:
		inherited_method
	normative_sections:
		Contract
Contract:
	general:
		|Must| specialize the behavior defined by the imported base method.
	base:
		pytest_good_inheritance.X.spam
		"""
		pass
