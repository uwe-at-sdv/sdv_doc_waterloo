#!/usr/bin/env python3

from __future__ import annotations
from typing import Generator,NoReturn
import sdv.doc.waterloo.docitem_helper as h

# The function does not know which rule is violated,
# but the caller has pushed it to the tracer's stack.
def some_deeper_function(tr) -> NoReturn:
	tr.add_error(tr.get_rule_on_fail(), "test", "An error from a deeper function has occurred")

def test_tracer() -> None:
	tr = h.tracer()
	# The tracer collects messages from deep inside the docitem parsing or
	# validation process. Make sure to provide a meaningful tag at each scope.
	tr.push("Path")
	tr.push("To")
	tr.push("Context")

	with h.rule_on_fail(tr, "XYZ-123"):
		some_deeper_function(tr)

	tr.pop()
	tr.pop()
	tr.pop()

	print(tr)

test_tracer()
