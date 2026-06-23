#!/usr/bin/env python3

from __future__ import annotations
import sdv.doc.waterloo.docitem_helper as h

config = h.ConfigTraversal()
config.enable_include_imported()
n = 0
for obj in h.gen_documentable_objects(h,config):
	print(h.get_obj_fully_qualified_name(obj))
	n += 1
print(f"Grand total with include_imported   : {n} objects")

config = h.ConfigTraversal()
n = 0
for obj in h.gen_documentable_objects(h,config):
	n += 1
print(f"Grand total without include_imported: {n} objects")
