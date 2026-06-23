#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

def test_regex() -> None:
#----- References --------------------------------------------#
	print("Regex RE_WTRL_ANGLE_HTTPS_REF:", h.RE_WTRL_ANGLE_HTTPS_REF)
	wtrl_angle_https_refs_bad = [
		"<http://example.com>", "<https//example.com>", "<https:/example.com>",
		"<https:example.com>", "<https://>", "<https://example.com space>",
		"<https://example.com!>", "<https://example.com#fragment>"
	]
	wtrl_angle_https_refs_good = [
		"label <http://example.com>", "label <http://example.com/path>",
		"label <https://example.com?query=param>", "label<https://example.com#fragment>",
		"label <https://example.com:8080>", "label <https://example.com:8080/path?query=param#fragment>"
	]
	try:     
		for i in wtrl_angle_https_refs_bad:
			assert not h.RE_WTRL_ANGLE_HTTPS_REF_COMPILED.fullmatch(i), f"Angle HTTPS reference {i} should not match the regex"
		for i in wtrl_angle_https_refs_good:
			assert h.RE_WTRL_ANGLE_HTTPS_REF_COMPILED.fullmatch(i), f"Angle HTTPS reference {i} did not match the regex"
	except AssertionError as e:
		print("Failed test:", i)
		raise e

test_regex()
