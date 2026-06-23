#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

#----- Simple example, function exploring itself --------------#
def test_get_source_docstring() -> None:
	"""A simple docstring."""
	print("source docstring:", h.get_source_docstring(test_get_source_docstring))

test_get_source_docstring()
