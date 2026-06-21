#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

#----- Tabular representation of SECTION_PROPERTIES -----------#
def render_as_table() -> None:
# Measured column widths
	colw = {}
# Gap between columns
	gap = 2
# Build table head
	thead = {
		"category":"Category",
		"normativity":"Normativity",
		"label_kind":"Label kind",
		"profile":"Profile",
		"must_exist":"Must exist",
		"hint":"Hint"
		}
# Do width measurement
	for label,line in ({"Label":thead} | h.SECTION_PROPERTIES).items():
		colw["label"] = max(colw["label"] if "label" in colw else 0,len(str(label)))
		for key in line:
			colw[key] = max(colw[key] if key in colw else 0,len(str(line[key])))
# Render table
	start = True
	for label,line in ({"Label":thead} | h.SECTION_PROPERTIES).items():
		if start:
			start = False
		print(label + " " * (colw["label"] - len(label) + gap),end='')
		for key in line:
			td = str(line[key])
			print(td + " " * (colw[key] - len(td) + gap),end='')
		print()

render_as_table()
