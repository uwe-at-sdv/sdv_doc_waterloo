#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

def test_tracer() -> None:
	tr = h.tracer()
	# The tracer collects messages from deep inside the docitem parsing or
	# validation process. Provide a meaningful tag at each scope.
	tr.push("Path")
	tr.push("To")
	tr.push("Context")

	# Add messages with the expected argument order.
	tr.add_debug_note("A debug entry","test")
	tr.add_info("An info","test")
	# Pass rule id, origin, message.
	tr.add_warning("ABC-123","test","A warning")
	tr.add_error("DEF-456","test","An error")

	print(tr)

test_tracer()
