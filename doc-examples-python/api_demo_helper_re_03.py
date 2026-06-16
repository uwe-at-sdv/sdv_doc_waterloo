#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

def test_regex() -> None:
#----- [Qualified] Identifier ---------------------------------#
	print("Regex RE_IDENTIFIER:",h.RE_IDENTIFIER)
	print("Regex RE_QUALIFIED_IDENTIFIER:",h.RE_QUALIFIED_IDENTIFIER)
	identifiers_bad = [
		"a@b.c", "1abc", "abc-1",
		"abc.1", "abc..def", ".abc",
		"abc.", "abc.def.", "abc..def",
		"abc.def..ghi", "abc.def.ghi."
	]
	identifiers_good = [
		"uvw_xyz",
		"_sdv_doc_item",
		"a_b_c_d"
	]
	qualified_identifiers_good = [
		"uvw_xyz",
		"sdv.doc.item",
		"a_b.c_d"
		"_._._"
	]
	try:
		for i in identifiers_bad:
			assert not h.RE_IDENTIFIER_COMPILED.fullmatch(i), f"Identifier {i} should not match the regex"
			assert not h.RE_QUALIFIED_IDENTIFIER_COMPILED.fullmatch(i), f"Qualified identifier {i} should not match the regex"
		for i in identifiers_good:
			assert h.RE_IDENTIFIER_COMPILED.fullmatch(i), f"Identifier {i} did not match the regex"
		for i in qualified_identifiers_good:
			assert h.RE_QUALIFIED_IDENTIFIER_COMPILED.fullmatch(i), f"Qualified identifier {i} did not match the regex"
	except AssertionError as e:
		print("Failed test:", i)
		raise e

test_regex()
