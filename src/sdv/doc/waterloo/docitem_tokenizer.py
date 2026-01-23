try:
	from sdv_doc_docitem_helper import *
except ImportError:
	from sdv.doc.waterloo.docitem_helper import *

RE_IDENTIFIER : Final[str] = r"[A-Za-z_][A-Za-z0-9_]*"
RE_IDENTIFIER_COMPILED : Final[re.Pattern[str]] = re.compile(RE_IDENTIFIER)

RE_QUALIFIED_IDENTIFIER : Final[str] = r"[A-Za-z_.][A-Za-z0-9_.]*"
RE_QUALIFIED_IDENTIFIER_COMPILED : Final[re.Pattern[str]] = re.compile(RE_QUALIFIED_IDENTIFIER)

RE_LABEL : Final[str] = RE_QUALIFIED_IDENTIFIER + ":"
RE_LABEL_COMPILED : Final[re.Pattern[str]] = re.compile(RE_LABEL)

#===== Tokenizer ==============================================#

INDENT_SCHEME_TAB : Final[int] = 0
INDENT_SCHEME_SPC4 : Final[int] = 1

def make_got_tag(subtree : docstring_subtree,pos : int) -> str:
	if pos < 0:
		return "<implementation_error_lt_0>"
	elif pos < len(subtree):
		return str(subtree[pos])
	else:
		return "<end-of-data>"

def get_num_indent(tr : tracer,line : str,indent_scheme: int) -> int:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Definitions, Contract, Parameters, Returns, Raises
	Definitions:
		TAB:
			A scheme that demands indentation by means of an integer number of tab characters (ASCII :wtrl_value:`0x09`).
			For this scheme, :wtrl_var:`INDENT_UNIT` is a single tab character.
		SPC4:
			A scheme that demands indentation by means of an integer multiple of four space characters (ASCII :wtrl_value:`0x20`).
			For this scheme, :wtrl_var:`INDENT_UNIT` consists of four space characters.
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
		|Must| return the number of indentations found at the beginning of the string in units as decribed by the indentation scheme passed.
	Raises:
		RuntimeError:
			|Must| raise if prefix contains a mix not representable as :wtrl_var:`n` repetitions of :wtrl_var:`INDENT_UNIT`.
			|Must| raise if the white space characters (greedy match of tab or space) at the beginning of the line cannot be described by the indentation scheme passed.
	"""
	if indent_scheme == INDENT_SCHEME_TAB:
		n_tab = 0
		for c in line:
			if c == "\t":
				n_tab += 1
			elif c == " ":
				raise_parsing_error(tr,["TKN-001"],"Inconsistent indent in docstring: space found in TAB scheme.")
			else:
				break
		return n_tab
	elif indent_scheme == INDENT_SCHEME_SPC4:
		n_spaces = 0
		for c in line:
			if c == " ":
				n_spaces += 1
			elif c == "\t":
				raise_parsing_error(tr,["TKN-001"],"Inconsistent indent in docstring: tab found in SPC4 scheme.")
			else:
				break
		if n_spaces % 4 != 0:
			raise_parsing_error(tr,["TKN-002"],"Inconsistent indent in docstring: spaces not a multiple of 4.")
		return n_spaces // 4
	else:
		raise_parsing_error(tr,["TKN-003"],f"Unknown indentation scheme: {indent_scheme}")

def parse_indent_docstring(tr : tracer,text : str) -> docstring_tree:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Definitions
		Contract
		Description
		Parameters
		Returns
		Raises
Definitions:
	DocstringTree:
		A value matching the following type: :wtrl_type:`docstring_tree` = :wtrl_type:`List`\[ :wtrl_type:`Union`\[ :wtrl_type:`str`, :wtrl_value:`"docstring_tree"`]]
Contract:
	general:
		|Must| generate a |term|`DocstringTree` from a docstring. In order to achieve this:
		|Must| accept a multiline string.
		|Must| remove empty lines at beginning and end of the input.
		|Must| insist on a uniform indentation scheme as definined normatively in :wtrl_func:`get_num_indent`.
		|Must| strip the indentation common to all lines if there is any, where ``common`` means: common to all only non-empty lines.
		|Must| iterate over the docstring's lines and skip empty lines.
		|Must| return an empty list (= empty docstring tree) on empty input.
		|Must| maintain a state engine and update it on each incoming line.
Description:
	This section is normative.
	The state engine consists of the following components:
	|
	1. A |term|`DocstringTree` (initial state: :wtrl_value:`[]`), given by a variable :wtrl_var:`target`.
	|
	2. A stack the elements of which point to :wtrl_var:`target` or any subtree thereof (see recursive definition of |term|`DocstringTree`; initial state is ``[target]``), represented by a variable :wtrl_var:`stack`.
	|
	3. An integer variable :wtrl_var:`cur_indent` which represents the current level of indendation during line parsing.
	|
	For each incoming line, processed sequentially, the following happens:
	If the indentation level remains unchanged, the line is appended to the substree represented by the top element of :wtrl_var:`stack`.
	If the indentation level increases, an empty |term|`DocstringTree` is appended to the subtree referenced by the top element of :wtrl_var:`stack` and a reference to this |term|`DocstringTree` is pushed to :wtrl_var:`stack`.
	If the indentation level decreases by :wtrl_var:`n` indentation units, an element is popped from :wtrl_var:`stack` for each of the :wtrl_var:`n` indentation levels.
Parameters:
	tr:
		Tracer for better error messages
	text:
		A multiline docstring with possibly indented lines.
Returns:
	|Must| return the |term|`DocstringTree` described as :wtrl_var:`target` in section :wtrl_label:`Description` in the state reached after parsing the entire input.
Raises:
	RuntimeError:
		|Must| raise if indentation grows by more than 1 unit from one line to the next.
		|Must| raise if inconsistent indentation (tab vs space) is detected.
		|May| propagate exceptions from :wtrl_func:`get_num_indent`.
	"""
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
			raise_parsing_error(tr,["TKN-001"],"Mixed tabs and spaces in indent.")
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
	target : docstring_tree = []
	stack : List[docstring_tree] = [target]
	cur_indent = 0
	for line in lines:
		if line.strip() == "":
			continue
		num_indent_abs = get_num_indent(tr,line, indent_scheme)
		num_indent = num_indent_abs - common_indent
		if num_indent < 0:
			raise_parsing_error(tr,["TKN-999"],"Indentation smaller than common indent.")
		elif num_indent > cur_indent + 1:
			raise_parsing_error(tr,["TKN-004"],f"indent jump > 1, not allowed, cur_indent: {cur_indent}, num_indent: {num_indent}, line '{line}'")
		elif num_indent > cur_indent:
			subtree : docstring_tree = []
			stack[cur_indent].append(subtree)
			stack.append(subtree)
			cur_indent += 1
		else:
			while cur_indent > num_indent:
				del stack[cur_indent]
				cur_indent -= 1
		content = line.strip()
		stack[cur_indent].append(content)
	return target

def expect_list(tr : tracer,subtree : docstring_subtree,pos : int) -> Tuple[docstring_subtree,int]:
	if pos >= len(subtree):
		return [],pos
	if not isinstance(subtree[pos],list):
		return [],pos
	items = subtree[pos]
	pos += 1
	return items,pos

def expect_label(tr : tracer,subtree : docstring_subtree,pos : int) -> Tuple[str,int]:
	cur = pos
	if pos >= len(subtree):
		raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),"label","end of data")
	if not isinstance(subtree[pos], str):
		raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'str', f'{make_got_tag(subtree,cur)}')
	if subtree[pos] == "":
		raise_parsing_error(tr,["PRSR-002"],f"empty label, not clear how this can happen at all.")
# Important! Easy to forget...
	if subtree[pos][-1] != ":":
		raise_parsing_error(tr,["PRSR-003"],f"missing colon after {make_got_tag(subtree,cur)}.")
	s = subtree[pos][:-1]
	pos += 1
	assert isinstance(s,str)
	return s,pos

def expect_label_identifier(tr : tracer,subtree : docstring_subtree,pos : int) -> Tuple[str,int]:
	cur = pos
	s,pos = expect_label(tr,subtree,pos)
	if not RE_IDENTIFIER_COMPILED.fullmatch(s):
		raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'identifier', f'{make_got_tag(subtree,cur)}')
	return s,pos

def expect_label_qualified_identifier(tr : tracer,subtree : docstring_subtree,pos : int) -> Tuple[str,int]:
	cur = pos
	s,pos = expect_label(tr,subtree,pos)
	if not RE_QUALIFIED_IDENTIFIER_COMPILED.fullmatch(s):
		raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'qualified identifier', f'{make_got_tag(subtree,cur)}')
	return s,pos

def expect_text(tr : tracer,subtree : docstring_subtree,pos : int) -> Tuple[str,int]:
	cur = pos
	if pos >= len(subtree):
		raise_parsing_error(tr,["PRSR-004"],"missing block after label")
	if not isinstance(subtree[pos],str):
		raise_parsing_error_expected_but_got(tr,tr.get_rules_on_fail(),'str', f'{make_got_tag(subtree,cur)}')
	s = subtree[pos]
	pos += 1
	assert isinstance(s,str)
	return s,pos

def get_tree_of_section(tr : tracer,tree : docstring_tree,sec : str) -> docstring_subtree:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| iterate over the given docitem tree and read the label (:wtrl_var:`label`) and subtree pairs.
		|Must| interpret :wtrl_var:`sec` as section label (without trailing colon), try to match :wtrl_var:`label` against :wtrl_var:`sec` and return the subtree on success.
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
		|May| propagate exceptions from :wtrl_func:`expect_label`
		|May| propagate exceptions from :wtrl_func:`expect_list`
	"""
	pos = 0
	while pos < len(tree):
		label,pos = expect_label_identifier(tr,tree,pos)
		subtree,pos = expect_list(tr,tree,pos)
		if label == sec:
			return subtree
	raise SectionNotFoundError(f"Section '{sec}' not found.")

def get_tree_of_subsection(tr : tracer,tree : docstring_tree,sec : str,subsec : str) -> docstring_subtree:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| iterate over the given docitem tree and read the label (:wtrl_var:`label`) and subtree pairs.
		|Must| interpret :wtrl_var:`sec` as section label (without trailing colon), try to match :wtrl_var:`label` against :wtrl_var:`sec`. On successful match:
		|Must| iterate over the subtree and read the label (:wtrl_var:`sublabel`) and subtree pairs.
		|Must| interpret :wtrl_var:`subsec` as subsection label (without trailing colon), try to match the :wtrl_var:`sublabel` against :wtrl_var:`subsec` and return the subtree on success.
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
		|May| propagate exceptions from :wtrl_func:`expect_label`
		|May| propagate exceptions from :wtrl_func:`expect_list`
	"""
	pos = 0
	while pos < len(tree):
		with rules_on_fail(tr,["PRSR-005"]):
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

def get_profile_of_tree(tr : tracer,tree : docstring_tree) -> str:
	if not tree:
		return ""
	t = get_tree_of_subsection(tr,tree,"Preamble","profile")
	if len(t) == 0:
		raise NoContentError("get_profile_of_tree")
	return str(t[0])

def get_profile_of_tree_nothrow(tr : tracer,tree : docstring_tree) -> str:
	try:
		return get_profile_of_tree(tr,tree)
	except:
		return ""

def to_string_tree(tree : docstring_subtree,indent_scheme : int = INDENT_SCHEME_TAB,indent : int = 0) -> str:
	"""
Preamble:
	profile:
		function
	normative_sections:
		Contract, Parameters, Returns, Raises
Contract:
	general:
		|Must| render the docstring tree to a string, using the indentation scheme passed.
		|Must| generate a watrloo docstring, provided the input is a docstring tree from a waterloo docstring.
Parameters:
	tree:
		The docstring tre to render
	indent_scheme:
		The indentation scheme to use, |must| be one of { :wtrl_value:`INDENT_SCHEME_TAB`, :wtrl_value:`INDENT_SCHEME_SPC4` }
	indent:
		Current indent level (recursive function). |May| be used for providing an overall indentation by the caller.
Returns:
	|Must| return the rendered string.
Raises:
Description:
	This function is helpful for idempotence tests.
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




