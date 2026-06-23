#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

def test_regex() -> None:
#----- Rule IDs -----------------------------------------------#
	print("Regex RE_RULE_ID:", h.RE_RULE_ID)
	rule_ids_bad = [
		"AB-12", "AB-123", "AB-1234",
		"ABC-12", "ABCD-12",
	]
	rule_ids_good = [
		"ABC-123", "ABC-1234",
		"ABCD-123", "ABCD-1234",
		"ABCDE-123", "ABCDE-1234",
	]
	try:
		for rule_id in rule_ids_bad:
			assert not h.RE_RULE_ID_COMPILED.match(rule_id), f"Rule ID {rule_id} should not match the regex"
			# print(f"Match {rule_id}:", h.RE_RULE_ID_COMPILED.match(rule_id))
		for rule_id in rule_ids_good:
			assert h.RE_RULE_ID_COMPILED.match(rule_id), f"Rule ID {rule_id} did not match the regex"
	except AssertionError as e:
		print("Failed test:", rule_id)
		raise e

test_regex()
