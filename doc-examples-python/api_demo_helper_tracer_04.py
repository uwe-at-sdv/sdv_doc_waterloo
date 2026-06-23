#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

def test_tracer() -> None:
	tr = h.tracer()

	with h.traced_section(tr, "Path"):
		with h.traced_section(tr, "To"):
			with h.traced_section(tr, "Context"):
				try:
					h.raise_has_no_docstring(tr, "ABC-123", test_tracer)
				except Exception:
					pass
				try:
					h.raise_parsing_error(tr, "ABC-123", "A message", {
						"found": "this",
						"expected": "that",
						"hint": "consult waterlint",
						})
				except Exception:
					pass
				try:
					h.raise_parsing_error_expected_but_got(tr, "ABC-123", "that", "this")
				except Exception:
					pass
				try:
					h.raise_parsing_error_invalid_label(tr, "ABC-123", "Conforming_to:", ["Preamble", "Contract"])
				except Exception:
					pass
				try:
					h.raise_validation_error(tr, test_tracer, "ABC-123", "A message", {
						"found": "wrong section",
						"expected": "right section",
						"hint": "waterlint explain-section --label <section> --profile <profile>",
						})
				except Exception:
					pass
				try:
					h.raise_validation_error_expected_but_got(tr, test_tracer, "ABC-123", "that", "this")
				except Exception:
					pass
	print(tr)

test_tracer()
