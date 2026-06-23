#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

def test_regex() -> None:
#----- CSV Identifiers ---------------------------------------#
	print("Regex RE_CSV_IDENTIFIERS:", h.RE_CSV_IDENTIFIERS)
	csv_identifiers_bad = [
		"abc,,def", "abc, ,def", "abc,def,", ",abc,def",
		"abc,def,123", "abc,def,ghi!", "abc,def,ghi jkl"
	]
	csv_identifiers_good = [
		"uvw_xyz",
		"uvw_xyz,abc_def",
		"uvw_xyz,abc_def,ghi_jkl"
	]
	try:
		for i in csv_identifiers_bad:
			assert not h.RE_CSV_IDENTIFIERS_COMPILED.fullmatch(i), f"CSV Identifiers {i} should not match the regex"
		for i in csv_identifiers_good:
			assert h.RE_CSV_IDENTIFIERS_COMPILED.fullmatch(i), f"CSV Identifiers {i} did not match the regex"
	except AssertionError as e:
		print("Failed test:", i)
		raise e

test_regex()
