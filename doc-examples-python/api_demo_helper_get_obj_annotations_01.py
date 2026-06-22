#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h
import sys,json

def test_get_obj_annotations() -> None:
	json.dump(h.get_obj_annotations(h.get_obj_annotations),sys.stdout,indent = 4)
	print()

test_get_obj_annotations()
