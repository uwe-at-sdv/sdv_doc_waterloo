#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

class X:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract
	Contract:
		general:
		constructor:
	"""

if __name__ == "__main__":
	print(h.get_obj_docstring(X))
