from __future__ import annotations
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Final, get_type_hints, get_origin, get_args, Generator, Iterable, Iterator, List, NewType, NoReturn, Sequence, Set, Tuple, Type, TypeAlias, TypeGuard, Union, cast

from sdv.doc.waterloo.docitem_helper import *
from sdv.doc.waterloo.docitem_diagnostics import render_found_label, render_suggestion

#===== Tokenizer ==============================================#

INDENT_SCHEME_TAB : Final[int] = 0
INDENT_SCHEME_SPC4 : Final[int] = 1

def make_got_tag(subtree : DocstringSubtree,pos : int) -> str:
	if pos < 0:
		return "<implementation_error_lt_0>"
	elif pos < len(subtree):
		return str(subtree[pos])
	else:
		return "<end-of-data>"

def _indentation_details(found: str, expected: str, hint: str) -> Details:
	return {
		"found": [found],
		"expected": [expected],
		"hint": [hint],
	}

def get_num_indent(tr : tracer,line : str,indent_scheme: int) -> int:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Definitions, Contract, Parameters, Returns, Raises
		status:
			stable
	Definitions:
		TAB:
			A scheme that demands indentation by means of an integer number of tab characters (ASCII |value|`0x09`).
			For this scheme, |var|`INDENT_UNIT` is a single tab character.
		SPC4:
			A scheme that demands indentation by means of an integer multiple of four space characters (ASCII |value|`0x20`).
			For this scheme, |var|`INDENT_UNIT` consists of four space characters.
	Contract:
		general:
			|Must| accept a single line string and an indentation scheme.
			|Must| count the number of leading indentations of the input according to the scheme passed.
			|Must| accept an empty string.
	Parameters:
		tr:
			Tracer for better error messages
		line:
			A single line string.
		indent_scheme:
			A symbolic value representing one of the two possible indentation schemes |term|`TAB` or |term|`SPC4`.
	Returns:
		|Must| return the number of indentations found at the beginning of the string in units as described by the indentation scheme passed.
	Raises:
		RuntimeError:
			|Must| raise if prefix contains a mix not representable as |var|`n` repetitions of |var|`INDENT_UNIT`.
			|Must| raise if the leading white space characters (tabs or four spaces) at the beginning of the line cannot be described by the indentation scheme passed.
	"""
	if indent_scheme == INDENT_SCHEME_TAB:
		n_tab = 0
		for c in line:
			if c == "\t":
				n_tab += 1
			elif c == " ":
				raise_parsing_error(tr,"TKN-001","Inconsistent indent in docstring: space found in TAB scheme.", _indentation_details(repr(line), "TAB indentation only", "Use tabs consistently or switch the whole file to SPC4 (four spaces)."))
			else:
				break
		return n_tab
	elif indent_scheme == INDENT_SCHEME_SPC4:
		n_spaces = 0
		for c in line:
			if c == " ":
				n_spaces += 1
			elif c == "\t":
				raise_parsing_error(tr,"TKN-001","Inconsistent indent in docstring: tab found in SPC4 scheme.", _indentation_details(repr(line), "SPC4 indentation only", "Use four spaces consistently or switch the whole file to TAB."))
			else:
				break
		if n_spaces % 4 != 0:
			raise_parsing_error(tr,"TKN-002","Inconsistent indent in docstring: spaces not a multiple of 4.", _indentation_details(repr(line), "indentation in multiples of 4 spaces", "Round indentation to whole four-space steps."))
		return n_spaces // 4
	else:
		raise_parsing_error(tr,"TKN-003",f"Unknown indentation scheme: {indent_scheme}", _indentation_details(f"{indent_scheme!r}", "INDENT_SCHEME_TAB or INDENT_SCHEME_SPC4", "Pass a supported indentation scheme."))

def parse_indent_docstring(tr : tracer,text : str, session: DocSession) -> DocstringTree:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Definitions, Contract, Description, Parameters, Returns, Raises
	Definitions:
		DocstringTree:
			A value matching the following type: |type|`DocstringTree` = |type|`List`\[ |type|`Union`\[ |type|`str`, |value|`"DocstringTree"`]]
	Contract:
		general:
			|Must| generate a |term|`DocstringTree` from a docstring. In order to achieve this:
			|Must| accept a multiline string.
			|Must| remove empty lines at beginning and end of the input.
			|Must| insist on a uniform indentation scheme as definined normatively in |func|`get_num_indent`.
			|Must| strip the indentation common to all lines if there is any, where ``common`` means: common to all only non-empty lines.
			|Must| iterate over the docstring's lines and skip empty lines.
			|Must| return an empty list (= empty docstring tree) on empty input.
			|Must| maintain a state engine and update it on each incoming line.
	Description:
		This section is normative.
		The state engine consists of the following components:
		|
		1. A |term|`DocstringTree` (initial state: |value|`[]`), given by a variable |var|`target`.
		|
		2. A stack the elements of which point to |var|`target` or any subtree thereof (see recursive definition of |term|`DocstringTree`; initial state is ``[target]``), represented by a variable |var|`stack`.
		|
		3. An integer variable |var|`cur_indent` which represents the current level of indendation during line parsing.
		|
		For each incoming line, processed sequentially, the following happens:
		If the indentation level remains unchanged, the line is appended to the substree represented by the top element of |var|`stack`.
		If the indentation level increases, an empty |term|`DocstringTree` is appended to the subtree referenced by the top element of |var|`stack` and a reference to this |term|`DocstringTree` is pushed to |var|`stack`.
		If the indentation level decreases by |var|`n` indentation units, an element is popped from |var|`stack` for each of the |var|`n` indentation levels.
	Parameters:
		tr:
			Tracer for better error messages
		text:
			A multiline docstring with possibly indented lines.
		session:
			A |type|`DocSession` object for various caching tasks.
	Returns:
		|Must| return the |term|`DocstringTree` described as |var|`target` in section |label|`Description` in the state reached after parsing the entire input.
	Raises:
		RuntimeError:
			|Must| raise if indentation grows by more than 1 unit from one line to the next.
			|Must| raise if inconsistent indentation (tab vs space) is detected.
			|May| propagate exceptions from |func|`get_num_indent`.
	"""
	if session.has_parsed(text):
		return session.get_parsed(text)
	lines = text.split("\n")

# Detect indentation scheme from first indented line
	indent_scheme = None
	for ln in lines:
# Skip empty lines
		if ln.strip() == "":
			continue
# Measure size of leading indent.
		prefix_len = len(ln) - len(ln.lstrip(" \t"))
		if prefix_len == 0:
			continue
# Extract indent and check for inconcistency.
		prefix = ln[:prefix_len]
		if " " in prefix and "\t" in prefix:
			raise_parsing_error(tr,"TKN-001","Mixed tabs and spaces in indent.", _indentation_details(repr(ln), "one indentation style only", "Use tabs only or spaces only in the same docstring."))
# Determine indentation scheme and leave loop.
		indent_scheme = INDENT_SCHEME_TAB if "\t" in prefix else INDENT_SCHEME_SPC4
		break
	if indent_scheme is None:
		indent_scheme = INDENT_SCHEME_SPC4

# First pass: compute indentation per line and common minimum
	indents: List[int] = []
	for ln in lines:
		if ln.strip() == "":
			continue
		indents.append(get_num_indent(tr,ln, indent_scheme))
	common_indent = min(indents) if indents else 0
# Build tree
	target : DocstringTree = []
	stack : List[DocstringTree] = [target]
	cur_indent = 0
	for line in lines:
		join_lines = False
		expect_join_lines = False
		if line.strip() == "":
			continue
# If a line ends with backslash we strongly assume the user wants to join lines.
		if line.rstrip().endswith("\\"):
			expect_join_lines = True
		num_indent_abs = get_num_indent(tr,line, indent_scheme)
		num_indent = num_indent_abs - common_indent
		if num_indent < 0:
			raise_parsing_error(tr,"TKN-999","Indentation smaller than common indent.", _indentation_details(repr(line), "indentation at least as deep as the common indent", "Remove the extra dedent or align all lines consistently."))
		elif num_indent > cur_indent + 1:
			raise_parsing_error(tr,"TKN-004",f"indent jump > 1, not allowed, cur_indent: {cur_indent}, num_indent: {num_indent}, line '{line}'", _indentation_details(repr(line), "at most one indentation step per line", "Insert intermediate structure or reduce the indent jump."))
		elif num_indent > cur_indent:
			subtree : DocstringTree = []
			stack[cur_indent].append(subtree)
			stack.append(subtree)
			cur_indent += 1
		else:
			while cur_indent > num_indent:
				del stack[cur_indent]
				cur_indent -= 1
# The case of two lines with same indentation
			if cur_indent == num_indent:
# Make sure the current stack has a line
				if len(stack[cur_indent]) > 0:
					last_line = stack[cur_indent][-1]
# We assume this is always fulfilled, but we have not proved.
					if isinstance(last_line, str):
# Make sure the string on top has at least one characters
						if len(last_line) > 0:
# Check for the join symbol, that is space and backslash.
							if last_line.rstrip().endswith("\\"):
# Plan the line join
								join_lines = True
		if not join_lines:
#			if expect_join_lines:
# We are not amused about the trailing backslash, but not totally grumpy either.
#				print("LAST_LINE:", last_line)
#				warn_parsing(tr,"TKN-007","Line ends with backslash but is not followed by another line.")
# No join: normal appending
			content = line.strip()
			stack[cur_indent].append(content)
		else:
# Do the join.
			content = line.strip()
			last_line = stack[cur_indent][-1]
# We know it's as string, so let's chill mypy here.
			assert isinstance(last_line,str)
			stack[cur_indent][-1] = last_line[:-1].rstrip() + " " + content
# To be revised. Most likely ok.
		if "\t" in content:
			warn_parsing(tr,"TKN-009",'Line contains inner TABs. Please connect lines with escaped \\ or use a raw string notation like r"""..."""')
	session.remember_parsed(text, target)
	return target

def expect_list(tr : tracer,subtree : DocstringSubtree,pos : int) -> Tuple[DocstringSubtree,int]:
	if pos >= len(subtree):
		return [],pos
	if not isinstance(subtree[pos],list):
		return [],pos
	items = subtree[pos]
	pos += 1
	return items,pos

def expect_label(tr : tracer,subtree : DocstringSubtree,pos : int) -> Tuple[str,int]:
	cur = pos
	if pos >= len(subtree):
		details: Details = {
			"found": render_found_label(None, "<end-of-data>"),
			"expected": render_suggestion(None, "a section or subsection label ending with ':'"),
			"hint": ["Add ':' to the label."],
		}
		raise_parsing_error_expected_but_got(tr,tr.get_rule_on_fail(),"label","end of data", details)
	if not isinstance(subtree[pos], str):
		details = {
			"found": render_found_label(None, make_got_tag(subtree,cur)),
			"expected": render_suggestion(None, "a string label"),
			"hint": ["Use a string token, not a nested list."],
		}
		raise_parsing_error_expected_but_got(tr,tr.get_rule_on_fail(),'str', f'{make_got_tag(subtree,cur)}', details)
	if subtree[pos] == "":
		details = {
			"found": render_found_label(None, '""'),
			"expected": render_suggestion(None, "a non-empty label ending with ':'"),
			"hint": ["Use a non-empty label."],
		}
		raise_parsing_error(tr,"PRSR-002",f"empty label, not clear how this can happen at all.", details)
# Important! Easy to forget...
	if subtree[pos][-1] != ":":
		details = {
			"found": render_found_label(None, make_got_tag(subtree,cur)),
			"expected": render_suggestion(None, "a section or subsection label ending with ':'"),
			"hint": ["Append ':' to the label."],
		}
		raise_parsing_error(tr,"PRSR-003",f"missing colon in section or subsection label: expected a label ending with ':', but found '{make_got_tag(subtree,cur)}'.", details)
	s = subtree[pos][:-1]
	pos += 1
	assert isinstance(s,str)
	return s,pos

def expect_label_identifier(tr : tracer,subtree : DocstringSubtree,pos : int) -> Tuple[str,int]:
	cur = pos
	s,pos = expect_label(tr,subtree,pos)
	if not RE_IDENTIFIER_COMPILED.fullmatch(s):
		details = {
			"found": render_found_label(None, make_got_tag(subtree,cur)),
			"expected": render_suggestion(None, "an identifier"),
			"hint": ["Use a plain identifier."],
		}
		raise_parsing_error_expected_but_got(tr,tr.get_rule_on_fail(),'identifier', f'{make_got_tag(subtree,cur)}', details)
	return s,pos

def expect_label_qualified_identifier(tr : tracer,subtree : DocstringSubtree,pos : int) -> Tuple[str,int]:
	cur = pos
	s,pos = expect_label(tr,subtree,pos)
	if not RE_QUALIFIED_IDENTIFIER_COMPILED.fullmatch(s):
		details = {
			"found": render_found_label(None, make_got_tag(subtree,cur)),
			"expected": render_suggestion(None, "a qualified identifier"),
			"hint": ["Use a dot-separated name."],
		}
		raise_parsing_error_expected_but_got(tr,tr.get_rule_on_fail(),'qualified identifier', f'{make_got_tag(subtree,cur)}', details)
	return s,pos

def expect_label_csv_identifiers(tr : tracer,subtree : DocstringSubtree,pos : int) -> Tuple[str,int]:
	cur = pos
	s,pos = expect_label(tr,subtree,pos)
	if not RE_CSV_IDENTIFIERS_COMPILED.fullmatch(s):
		details = {
			"found": render_found_label(None, make_got_tag(subtree,cur)),
			"expected": render_suggestion(None, "a comma-separated list of identifiers"),
			"hint": ["Separate items with commas."],
		}
		raise_parsing_error_expected_but_got(tr,tr.get_rule_on_fail(),'comma-separated list of identifiers', f'{make_got_tag(subtree,cur)}', details)
	return s,pos

def expect_text(tr : tracer,subtree : DocstringSubtree,pos : int) -> Tuple[str,int]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| accept a docstring subtree and a position |var|`pos` in the subtree.
			|Must| check that the subtree has a string at position |var|`pos`.
	Parameters:
		tr:
			Tracer for providing context and collecting warnings
		subtree:
			The docstring subtree to be examined
		pos:
			The position in the subtree to start examining
	Returns:
		A tuple containing the string at the current position and the next position
	Raises:
		ParseError:
			|Must| raise if the subtree does not have a string at position |var|`pos`.
	Notes:
		Call sites:
			This function is invoked by the subsection parsers for subsections
			|label|`Contract.general`, |label|`Contract.requires`, |label|`Contract.ensures`,
			|label|`Contract.invariants`, and |label|`Contract.constructor`.
	"""
	cur = pos
	if pos >= len(subtree):
		details: Details = {
			"found": render_found_label(None, "<end-of-data>"),
			"expected": render_suggestion(None, "a text block after the label"),
			"hint": ["Add an indented block after the label."],
		}
		raise_parsing_error(tr,"PRSR-004","missing block after label", details)
	if not isinstance(subtree[pos],str):
		details = {
			"found": render_found_label(None, make_got_tag(subtree,cur)),
			"expected": render_suggestion(None, "a text line"),
			"hint": ["Use a plain string line, not a nested list."],
		}
		raise_parsing_error_expected_but_got(tr,tr.get_rule_on_fail(),'str', f'{make_got_tag(subtree,cur)}', details)
	s = subtree[pos]
	pos += 1
	assert isinstance(s,str)
	return s,pos

def get_tree_of_section(tr : tracer,tree : DocstringTree,sec : str) -> DocstringSubtree:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| iterate over the given docitem tree and read the label (|var|`label`) and subtree pairs.
			|Must| interpret |var|`sec` as section label (without trailing colon), try to match |var|`label` against |var|`sec` and return the subtree on success.
	Parameters:
		tr:
			Tracer for providing context and collecting warnings
		tree:
			The docitem tree to be examined
		sec:
			The section label to search for.
	Returns:
		|Must| return the subtree of the found section.
	Raises:
		SectionNotFoundError:
			|Must| raise if the section is not found.
		BaseException:
			|May| propagate exceptions from |func|`expect_label`
			|May| propagate exceptions from |func|`expect_list`
	"""
	pos = 0
	while pos < len(tree):
		label,pos = expect_label_identifier(tr,tree,pos)
		subtree,pos = expect_list(tr,tree,pos)
		if label == sec:
			return subtree
	raise SectionNotFoundError(f"Section '{sec}' not found.")

def get_tree_of_subsection(tr : tracer,tree : DocstringTree,sec : str,subsec : str) -> DocstringSubtree:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| iterate over the given docitem tree and read the label (|var|`label`) and subtree pairs.
			|Must| interpret |var|`sec` as section label (without trailing colon), try to match |var|`label` against |var|`sec`. On successful match:
			|Must| iterate over the subtree and read the label (|var|`sublabel`) and subtree pairs.
			|Must| interpret |var|`subsec` as subsection label (without trailing colon), try to match the |var|`sublabel` against |var|`subsec` and return the subtree on success.
	Parameters:
		tr:
			Tracer for providing context and collecting warnings
		tree:
			The docitem tree to be examined
		sec:
			The section label to search for.
		subsec:
			The subsection label to search for.
	Returns:
		|Must| return the subtree of the found subsection.
	Raises:
		SectionNotFoundError:
			|Must| raise if the section is not found.
		SubsectionNotFoundError:
			|Must| raise if the subsection is not found.
		BaseException:
			|May| propagate exceptions from |func|`expect_label`
			|May| propagate exceptions from |func|`expect_list`
	"""
	pos = 0
	while pos < len(tree):
		with rule_on_fail(tr,"PRSR-005"):
			label,pos = expect_label_identifier(tr,tree,pos)
		subtree,pos = expect_list(tr,tree,pos)
		if label == sec:
			subpos = 0
			while subpos < len(subtree):
				sublabel,subpos = expect_label(tr,subtree,subpos)
				subitems,subpos = expect_list(tr,subtree,subpos)
				if sublabel == subsec:
					return subitems
			raise SubsectionNotFoundError(f"Subsection '{subsec}' not found in section '{sec}'.")
	raise SectionNotFoundError(f"Section '{sec}' not found.")

def get_profile_of_tree(tr : tracer,tree : DocstringTree) -> str:
	if not tree:
		return ""
	t = get_tree_of_subsection(tr,tree,"Preamble","profile")
	if len(t) == 0:
		raise NoContentError("get_profile_of_tree")
	return str(t[0])

def get_profile_of_tree_nothrow(tr : tracer,tree : DocstringTree) -> str:
	try:
		return get_profile_of_tree(tr,tree)
	except:
		return ""

def get_scopes_of_tree(tr : tracer,tree : DocstringTree) -> Scopes:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| extract the |label|`Preamble` from the docstring tree.
			|Must| extract the |label|`scope` from the |label|`Preamble`.
			|Must| return the default if |label|`scope` is not present or empty.
	Parameters:
		tr:
			Tracer for providing context and collecting warnings
		tree:
			The docitem tree to be examined
	Returns:
		|Must| return the set of scopes found, or the default., which is a set\
		containing a single element |value|`PUBLIC`.
	Raises:
		SectionNotFoundError:
			|Must| raise if there is no |label|`Preamble`
	"""
	scopes, _ = get_scopes_of_tree_var(tr, tree)
	return scopes


def get_scopes_of_tree_var(tr : tracer,tree : DocstringTree) -> tuple[Scopes, bool]:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| extract the |label|`Preamble` from the docstring tree.
			|Must| extract the |label|`scope` from the |label|`Preamble`.
			|Must| return the default if |label|`scope` is not present or empty.
			|Must| additionally return whether the scope was declared explicitly.
	Parameters:
		tr:
			Tracer for providing context and collecting warnings
		tree:
			The docitem tree to be examined
	Returns:
		|Must| return a tuple |var|`(scopes, explicit)` where |var|`scopes` is the set of scopes found,
		and |var|`explicit` is |True| iff subsection |label|`Preamble.scope` is present.
	Raises:
		SectionNotFoundError:
			|Must| raise if there is no |label|`Preamble`
	"""
	if not tree:
		return set([Scope.PUBLIC]), False
	try:
		scopes = get_tree_of_subsection(tr,tree,"Preamble","scope")
# No Preamble.
	except SectionNotFoundError:
		raise
# Preamble exists, but scope does not
	except SubsectionNotFoundError:
		return set([Scope.PUBLIC]), False
# scope exists but is empty
	if len(scopes) == 0:
		return set([Scope.PUBLIC]), True
# Ensured by parser.
	assert is_list_of_str(scopes)
	return set([scope_tag_map[s] for s in scopes if s in scope_tag_map]), True

def to_string_tree(tree : DocstringSubtree,indent_scheme : int = INDENT_SCHEME_TAB,indent : int = 0) -> str:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| render the docstring tree to a string, using the indentation scheme passed.
		|Must| generate a waterloo docstring, provided the input is a docstring tree from a waterloo docstring.
Parameters:
	tree:
		The docstring tre to render
	indent_scheme:
		The indentation scheme to use, |must| be one of { |value|`INDENT_SCHEME_TAB`, |value|`INDENT_SCHEME_SPC4` }
	indent:
		Current indent level (recursive function). |May| be used for providing an overall indentation by the caller.
Returns:
	|Must| return the rendered string.
Raises:
Description:
	This function is helpful for idempotence tests.
	It is invoked e.g. in `waterlint extract` in order to extract
	sections or subsections from a docstring.
	"""
	indent_unit = "\t" if indent_scheme == INDENT_SCHEME_TAB else "    "
	doc = ""
	if isinstance(tree,str):
		doc += indent_unit * indent + tree + "\n"
	else:
		for item in tree:
			if isinstance(item,str):
				doc += indent_unit * indent + item + "\n"
			elif isinstance(item,list):
				doc += to_string_tree(item,indent_scheme,indent + 1)
# Unreachable by static type checking.
#			else: ...
	return doc
