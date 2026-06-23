#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

def f() -> None:
	pass

if __name__ == "__main__":
	# Both deliver the same result, module 'sdv.doc.waterloo.docitem_helper'.
	print("module helper:", h.get_obj_direct_module(h))
	print("module helper function:", h.get_obj_direct_module(h.get_obj_direct_module))
	# Module __main__ seems to cause trouble, but that is a special case
	# not relevant in practice.
	print("module function f:", h.get_obj_direct_module(f))
