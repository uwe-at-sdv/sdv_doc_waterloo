#!/usr/bin/env python3

import sdv.doc.waterloo.docitem_helper as h

def test_regex() -> None:
#----- Markup with backticks ---------------------------------#
	print("Regex RE_WTRL_MARKUP_BACKTICK:", h.RE_WTRL_MARKUP_BACKTICK)
	markup_bad = [
		"|unknown|`text`", "|type|text", "type|`text`",
		"|type|`text", "|type|text`", "type|text`",
		"|type|`text` more text", "more text |type|`text`",
		"|type|`text`|type|`text`","|type| `text`",
		"|type |`text`","| type|`text`"
	]
	markup_good = [
		"|type|`int`", "|func|`my_function`", "|var|`my_variable`",
		"|attr|`my_attribute`", "|cmd|`my_command`", "|dfn|`my_definition`",
		"|file|`my_file`", "|key|`my_key`", "|label|`my_label`", "|lit|`my_literal`",
		"|mod|`my_module`", "|norm|`my_norm`", "|op|`my_operator`", "|opt|`my_option`",
		"|ref|`my_reference`", "|tag|`my_tag`", "|term|`my_term`", "|type|`my_type`",
		"|var_type|`myvar:mytype`"
	]
	try:
		for i in markup_bad:
			assert not h.RE_WTRL_MARKUP_BACKTICK_COMPILED.fullmatch(i), f"Markup {i} should not match the regex"
		for i in markup_good:
			assert h.RE_WTRL_MARKUP_BACKTICK_COMPILED.fullmatch(i), f"Markup {i} did not match the regex"
	except AssertionError as e:
		print("Failed test:", i)
		raise e

test_regex()
