#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

def test_tracer() -> None:
	tr = h.tracer()

	with h.traced_section(tr, "Path"):
		with h.traced_section(tr, "To"):
			with h.traced_section(tr, "Context"):
				h.warn_parsing(tr, "ABC-123", "A warning raised during parsing")
	with h.traced_section(tr, "Other"):
		with h.traced_section(tr, "Path"):
			h.warn_validation(tr, "ABC-123", "A warning raised during validation")

	print(tr)

test_tracer()
