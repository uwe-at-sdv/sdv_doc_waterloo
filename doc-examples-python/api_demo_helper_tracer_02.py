#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h
import sys,json

# Dump a tracer as JSON for demonstration purposes.
def test_tracer() -> None:
	tr = h.tracer()
# The tracer collects messages from deep inside
# the docitem parsing or validation process.
# Make sure to provide a meaningful tag at each scope.
	tr.push("Path")
	tr.push("To")

# Demomstrate the context stack
	tr.push("Context1")
	tr.add_debug_note("A debug entry","test")
	tr.pop()

	tr.push("Context2")
	tr.add_info("An info","test")
	tr.pop()

	tr.push("Context3")
	tr.add_warning("ABC-123","test","A warning")
	tr.pop()

	tr.push("Context4")
	tr.add_error("DEF-456","test","An error")
	tr.pop()

	json.dump(tr.build_json(tr.Severity.DEBUG),sys.stdout, indent=4)
	print()

test_tracer()
