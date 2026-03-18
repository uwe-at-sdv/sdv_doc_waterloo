r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Definitions, Public_classes, Public_constants
Definitions:
	Pos_Role_Substring_Triple:
		A tuple (|var|`position`, |var|`token_type`, |var|`substring`) specifying syntax highlighting:
		# |var|`position`: The starting index of the substring in the original text.
		# |var|`token_type`: A Pygments token class (from |type|`pygments.token`).
		# |var|`substring`: The text to be highlighted.
Contract:
	general:
		|Must| provide a Python module that defines the PythonWaterlooLexer class for syntax highlighting of Waterloo-docstrings.
Public_classes:
	PythonWaterlooLexer
Public_constants:
	RE_SECTION_ALLOWED_NORMATIVE:
		A regular expression pattern that matches section names allowed or mandatory\
		in the "normative_sections" subsection of the Preamble.\
		This expression is governed by the normative rules and must be kept up to date.
		Mandatory : CON-002, CON-005, CON-020, CON-034, CPCL-002, CPCON-002, CPMT-002,\
		CPTYP-002, CPVAR-002, DEF-002, DER-004, FAC-009, MPCL-002, MPCON-002, MPFN-002,\
		MPTYP-002, MPVAR-002, PAR-002, RAI-002, RET-002.
		Accepted : DESC-002, SEE-011.
		Refused : NOTE-002, PRE-002, TERM-002.
"""
from __future__ import annotations

import sys,re
from typing import Any, Iterable, Iterator

from pygments.lexer import Lexer
from pygments.lexers.python import PythonLexer
from pygments.token import Error, Generic, Keyword, Name, String, Literal, Number, Operator


#----- Changelog ----------------------------------------------#

__version__ = "0.3.0"
# - 0.3.0 [2026-03-14]	Added handling for bullet list markers (lines starting with "-", "+", or "*")
# 			in the `highlight_line` method, treating them as keywords for syntax highlighting.
# - 0.2.0 [2026-03-10]	Added comprehensive comments and documentation to the code,
# 			explaining the purpose and functionality of each method and
# 			section of the lexer. This includes detailed descriptions
# 			of the parameters, return values, and potential exceptions
# 			for each method, as well as explanations of the regular
# 			expressions used for tokenization.
#			* Careful handling of edge cases, such as docstrings that do not
# 			conform to the expected structure or contain mixed indentation,
# 			to ensure that the lexer behaves robustly in a variety of scenarios.
# - 0.1.0 [2026-03-05]	Versioning starts now.

#----- Constants ----------------------------------------------#
RE_SECTION = re.compile(
	r"^\s*(?:"
	r"Preamble|Contract|Parameters|Returns|Raises|Notes|See_also|"
	r"Definitions|Terminology|Description|Derived_from|Factory|"
	r"Public_[A-Za-z_][A-Za-z0-9_]*|"
	r"[A-Za-z_][A-Za-z0-9_]*_overview"
	r"):\s*$"
)
RE_SECTION_CAPTURE = re.compile(
	r"^\s*("
	r"Preamble|Contract|Parameters|Returns|Raises|Notes|See_also|"
	r"Definitions|Terminology|Description|Derived_from|Factory|"
	r"Public_[A-Za-z_][A-Za-z0-9_]*|"
	r"[A-Za-z_][A-Za-z0-9_]*_overview"
	r"):\s*$"
)

RE_SECTION_ALLOWED_NORMATIVE = re.compile(
	r"^(?:"
	r"Contract|Parameters|Returns|Raises|Derived_from|"
	r"Definitions|Description|Factory|See_also|"
	r"Public_[A-Za-z_][A-Za-z0-9_]*|"
	r")$"
)
RE_SUBSECTION_QUALIFIED_IDENTIFIER = re.compile(
	r"^(\s*)([A-Za-z_][A-Za-z0-9_.]*:)(\s*)$"
)
RE_SUBSECTION_ANY = re.compile(
	r"^(\s*)(.+:)(\s*)$"
)
# Free-form sections like "Definitions" allow subdivision of
# text using a single pipe operator on a line.
RE_TEXTFLOW_MARKER = re.compile(
	r"^\s*(?:\|)\s*$"
)
RE_LIST_MARKER = re.compile(
	r"^([ \t]*)([-+*#])(\s+)(.*)$"
)

# 1: Normativity keywords
# 2: Special values
# 3,4: |ref| and argument
# 5,6: |lit| and argument
# 7,8: |var| and argument
# 9,10: |type| and argument
# 11,12: |mod| and argument
# 13,14: |value| and argument
# 15,16: |op| and argument
# 17,18: |func| and argument
# 19,20: |label| and argument
# 21,22: |attr| and argument
# 23,24: |file| and argument
# 25,26: |dfn| and argument
# 27,28: |term| and argument
# 29,30: |cmd| and argument
# 31,32: |opt| and argument
# 33,34: |tag| and argument
# 35,36: |norm| and argument
# 37,38: |var_type| and argument
# 39,40: Generic role and argument
# 41: Line connector
RE_INLINE = re.compile(
	r"(\|(?:Must|must|Must_not|must_not|Should|should|Should_not|should_not|May|may)\|)"
	r"|(\|(?:Self|None|True|False)\|)"
	r"|(\|ref\|)(`[^`]+`)"
	r"|(\|lit\|)(`[^`]+`)"
	r"|(\|var\|)(`[^`]+`)"
	r"|(\|type\|)(`[^`]+`)"
	r"|(\|mod\|)(`[^`]+`)"
	r"|(\|value\|)(`[^`]+`)"
	r"|(\|op\|)(`[^`]+`)"
	r"|(\|func\|)(`[^`]+`)"
	r"|(\|label\|)(`[^`]+`)"
	r"|(\|attr\|)(`[^`]+`)"
	r"|(\|file\|)(`[^`]+`)"
	r"|(\|dfn\|)(`[^`]+`)"
	r"|(\|term\|)(`[^`]+`)"
	r"|(\|cmd\|)(`[^`]+`)"
	r"|(\|opt\|)(`[^`]+`)"
	r"|(\|tag\|)(`[^`]+`)"
	r"|(\|norm\|)(`[^`]+`)"
	r"|(\|var_type\|)(`[^`]+`)"
	r"|(\|[A-Za-z_][A-Za-z0-9_]*\|)(`[^`]+`)"
	r"|(\\)(?=\s*(?:\n)?$)"
)
RE_REF_ARG = re.compile(r"^(.*?)\s*<([^<>]+)>\s*$")

SUBSECTIONS_WITH_FREE_FORM_LABELS = (
	"Notes",
	"Terminology"
	)

PREAMBLE_BUILTIN_SUBSECTIONS = frozenset(("profile", "normative_sections", "status", "scope"))
CONTRACT_BUILTIN_SUBSECTIONS = frozenset(("general", "constructor", "base", "traits", "invariants", "requires", "ensures"))

SECTION_LIST_TYPE_QUALIFIED = frozenset(("Public_classes", "Derived_from"))
SECTION_LIST_FUNC_QUALIFIED = frozenset(("Public_functions", "Public_methods"))
SECTION_LIST_GENERIC_QUALIFIED = frozenset(("See_also",))

SECTION_MAP_TERM_IDENTIFIER_TO_FREEFORM = frozenset(("Definitions","Terminology"))
SECTION_MAP_ANY_IDENTIFIER_TO_FREEFORM = frozenset(("Notes",))
SECTION_MAP_TYPE_IDENTIFIER_TO_FREEFORM = frozenset(("Class_overview", "Public_types"))
SECTION_MAP_FUNC_IDENTIFIER_TO_FREEFORM = frozenset(("Function_overview", "Method_overview","Factory"))
SECTION_MAP_VAR_IDENTIFIER_TO_FREEFORM = frozenset(("Public_variables", "Public_constants","Parameters"))
SECTION_MAP_FUNC_QUALIFIED = frozenset(("Factory",))
SECTION_MAP_EXCEPTION_QUALIFIED_IDENTIFIER_TO_FREEFORM = frozenset(("Raises",))

SECTIONS_WITH_SUBSECTIONS = frozenset((
	"Preamble", "Contract", "Definitions", "Terminology", "Notes", "Parameters", "Raises",
	"Factory", "Class_overview", "Function_overview", "Method_overview",
	"Public_types", "Public_variables", "Public_constants",
))

RE_PREAMBLE = re.compile(r"^\s*Preamble:\s*$")
RE_CONTRACT = re.compile(r"^\s*Contract:\s*$")

#----- Lexer --------------------------------------------------#

class PythonWaterlooLexer(PythonLexer):
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods
	Contract:
		general:
			|Must| implement a Pygments lexer class that extends the standard Python\
			lexer to provide syntax highlighting for Waterloo-docstrings.
			|Must| define a static method `analyse_text` that checks if a\
			given string looks like a Waterloo-docstring, returning a float score for lexer selection.
			|Must| implement the `get_tokens_unprocessed` method to yield\
			tokens with appropriate types for different parts of the docstring,\
			such as section headers, normative keywords, and inline markup.
			|Must| use regular expressions to identify section headers and inline markup patterns.
			|Must| ensure that the lexer can be used with Pygments for\
			syntax highlighting in various tools and editors.
			|Must| prioritize this lexer over the standard Python lexer\
			when the input text contains Waterloo-docstring patterns.
			|Must| handle edge cases gracefully, such as docstrings that\
			do not conform to the expected structure or contain mixed indentation.
			|Must| include comprehensive comments and documentation within\
			the code to explain the implementation and usage of the lexer.
			|Must| be implemented in a way that allows for easy maintenance\
			and extension in the future, such as adding support for new sections or inline markup patterns.
		constructor:
			default
	Public_methods:
		highlight_docstring,highlight_line,looks_like_waterloo_docstring,has_mixed_indentation,analyse_text,get_tokens_unprocessed
	"""
	name = "Python-Waterloo"
	aliases = ["python-waterloo"]
	filenames = ["*.py"]
	priority = 0.9

	def get_tokens_unprocessed(self, text: str) -> Iterator[tuple[int, object, str]]:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Definitions, Parameters, Returns, Raises
			scope:
				extension
		Definitions:
			_inherit:
				Pos_Role_Substring_Triple
		Description:
			This is the core tokenization method that Pygments calls to obtain syntax highlighting tokens.
			It iterates over tokens from the parent PythonLexer and intercepts docstrings (String.Doc tokens)
			to apply Waterloo-specific highlighting rules. This method is the entry point for all tokenization
			and determines the highlighting of the entire source code.
		Contract:
			general:
				|Must| analyze the provided string.
				|Must| iterate over the input lines to identify Waterloo-specific tokens.
				|Must| generate a |term|`Pos_Role_Substring_Triple` for each matching token.
				|Must| fall back to default highlighting for non-matching docstring parts.
		Parameters:
			text:
				The input text to tokenize.
		Returns:
			An iterable of |term|`Pos_Role_Substring_Triple` tuples.
		Raises:
			BaseException:
				|May| propagate from the pygments module.
		"""
		self._current_section = ""
		self._current_subsection = ""
		for index, ttype, value in super().get_tokens_unprocessed(text):
			if ttype in String.Doc:   # oder is String.Doc
				yield from self.highlight_docstring(index, value)
			else:
				yield index, ttype, value

# waterlint demands profile function because internally this
# seems to be a function make_analysator.<locals>.text_analyse.
# Not sure how this remapping works, but to satisfy waterlint
# we need to comment it with profile function, even though it is a static method.
	@staticmethod
	def analyse_text(text: str) -> float:
		"""
		Preamble:
			profile:
				function
			normative_sections:
				Contract, Parameters, Returns, Raises
		Description:
			This method is called by Pygments during lexer selection to prioritize
			the PythonWaterlooLexer over the standard PythonLexer.
			It analyzes the input text for patterns indicative of Waterloo-docstrings,
			such as the presence of "Preamble:" and "Contract:" sections, ensuring
			that files containing structured docstrings are highlighted
			appropriately by this specialized lexer.
		Contract:
			general:
				|Must| determine if the given text resembles a Waterloo-docstring.
				|Must| perform a quick check for presence of "Preamble:" and "Contract:".
				|Must| conduct a detailed line-by-line validation using regex patterns.
				|Must| return 1.0 if both sections are properly matched, otherwise 0.0.
		Parameters:
			text:
				The input text to analyze for Waterloo-docstring characteristics.
		Returns:
			A float value: 1.0 if the text is identified as a Waterloo-docstring, 0.0 otherwise.
		Raises:
			BaseException:
				|May| propagate exceptions from the |mod|`re` module.
		"""
# This is important in order to priorize our Lexer over the standard Python lexer.
# Quick check
		if "Preamble:" not in text or "Contract:" not in text:
			return 0.0
# Closer look
		found_preamble = False
		found_contract = False
		for line in text.splitlines():
			if not found_preamble:
				if "Preamble:" in line:
					if RE_PREAMBLE.match(line):
						found_preamble = True
			if not found_contract:
				if "Contract:" in line:
					if RE_CONTRACT.match(line):
						found_contract = True
			if found_preamble and found_contract:
				return 1.0
		return 0.0

	def highlight_docstring(self, base: int, text: str) -> Iterable[tuple[int, object, str]]:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Definitions, Contract, Parameters, Returns, Raises
		Definitions:
			_inherit:
				Pos_Role_Substring_Triple
		Contract:
			general:
				|Must| check if the given text looks like a Waterloo-docstring.
				|Must| if it does not look like a Waterloo-docstring, yield the entire text as a single String.Doc token.
				|Must| if it looks like a Waterloo-docstring, reset the parser state and analyze the text line by line.
				|Must| for each line, call the |func|`highlight_line` method to identify and yield tokens for that line.
		Parameters:
			base:
				The base index for token positions in the original text.
			text:
				The docstring text to analyze and tokenize.
		Returns:
			An iterable of |term|`Pos_Role_Substring_Triple` tuples for the given docstring.
		Raises:
			BaseException:
				|May| propagate exceptions from the |mod|`re` module.
				|May| propagate exceptions from the |mod|`pygments` module.
		"""
		if not self.looks_like_waterloo_docstring(text):
			yield base, String.Doc, text
			return

		# Reset parser state per docstring to avoid carry-over between unrelated docstrings.
		self._current_section = ""
		self._current_subsection = ""
		pos = 0
		while pos < len(text):
			nl = text.find("\n", pos)
# Make sure we identify the last line correctly, even without a trailing newline character
			if nl < 0:
				line = text[pos:]
				next_pos = len(text)
			else:
# The position is the character after the newline character.
				line = text[pos : nl + 1]
				next_pos = nl + 1
# We have identified a line, now find out how to highlight.
			yield from self.highlight_line(base + pos, line)
# Advance to next line.
			pos = next_pos

	def _find_subsection_match(self, stripped: str) -> re.Match[str] | None:
		if self._current_section in SUBSECTIONS_WITH_FREE_FORM_LABELS:
			return RE_SUBSECTION_ANY.match(stripped)
		return RE_SUBSECTION_QUALIFIED_IDENTIFIER.match(stripped)

	def _token_for_subsection_label(self, section: str, subsection: str) -> Any:
		if section == "Preamble":
			if subsection in PREAMBLE_BUILTIN_SUBSECTIONS:
				return Generic.Subheading
			return Error
		if section == "Contract":
			if subsection in CONTRACT_BUILTIN_SUBSECTIONS:
				return Generic.Subheading
			return Error
		if section == "Definitions":
			if subsection == "_inherit":
				return Keyword
			else:
				return Generic.Emph
		if section == "Terminology":
			return Generic.Emph
		if section in SECTION_MAP_TYPE_IDENTIFIER_TO_FREEFORM:
			return Name.Class
		if section in SECTION_MAP_FUNC_IDENTIFIER_TO_FREEFORM:
			return Name.Function
		if section in SECTION_MAP_VAR_IDENTIFIER_TO_FREEFORM:
			return Name.Variable
		if section in SECTION_MAP_FUNC_QUALIFIED:
			return Name.Function
		if section in SECTION_MAP_EXCEPTION_QUALIFIED_IDENTIFIER_TO_FREEFORM:
			return Name.Exception
		return Generic.Heading

	def _emit_subsection_line(self, base: int, line: str, match: re.Match[str]) -> Iterable[tuple[int, object, str]]:
		prefix, label, suffix = match.groups()
		self._current_subsection = label[:-1].strip()
		cur = base
		if prefix:
			yield cur, String.Doc, prefix
			cur += len(prefix)
		token = self._token_for_subsection_label(self._current_section, self._current_subsection)
		yield cur, token, label
		cur += len(label)
		if suffix:
			yield cur, String.Doc, suffix
			cur += len(suffix)
		if line.endswith("\n"):
			yield cur, String.Doc, "\n"

	def _emit_normative_sections_line(self, base: int, line: str) -> Iterable[tuple[int, object, str]]:
		stripped_no_nl = line.rstrip("\r\n")
		line_ending = line[len(stripped_no_nl):]
		cur = base

		for part in re.split(r"(,)", stripped_no_nl):
			if part == "":
				continue
			if part == ",":
				yield cur, String.Doc, part
				cur += len(part)
				continue

			leading_len = len(part) - len(part.lstrip())
			trailing_len = len(part) - len(part.rstrip())
			ident = part.strip()

			if leading_len:
				yield cur, String.Doc, part[:leading_len]
				cur += leading_len
			if ident:
				if RE_SECTION_ALLOWED_NORMATIVE.fullmatch(ident):
					yield cur, Name.Constant, ident
				else:
					yield cur, Error, ident
				cur += len(ident)
			if trailing_len:
				yield cur, String.Doc, part[-trailing_len:]
				cur += trailing_len

		if line_ending:
			yield cur, String.Doc, line_ending

	def _emit_csv_identifiers_line(self, base: int, line: str, token_for_identifier: Any) -> Iterable[tuple[int, object, str]]:
		stripped_no_nl = line.rstrip("\r\n")
		line_ending = line[len(stripped_no_nl):]
		cur = base

		for part in re.split(r"(,)", stripped_no_nl):
			if part == "":
				continue
			if part == ",":
				yield cur, String.Doc, part
				cur += len(part)
				continue

			leading_len = len(part) - len(part.lstrip())
			trailing_len = len(part) - len(part.rstrip())
			ident = part.strip()

			if leading_len:
				yield cur, String.Doc, part[:leading_len]
				cur += leading_len
			if ident:
				yield cur, token_for_identifier, ident
				cur += len(ident)
			if trailing_len:
				yield cur, String.Doc, part[-trailing_len:]
				cur += trailing_len

		if line_ending:
			yield cur, String.Doc, line_ending

	def _emit_ref_arg(self, arg_start: int, arg: str) -> Iterable[tuple[int, object, str]]:
		if len(arg) < 2 or arg[0] != "`" or arg[-1] != "`":
			yield arg_start, Error, arg
			return

		inner = arg[1:-1]
		m_ref = RE_REF_ARG.match(inner)
		if m_ref is None:
			yield arg_start, Error, arg
			return

		ref_name, ref_target = m_ref.groups()
		pos = arg_start
		yield pos, String, "`"
		pos += 1
		if ref_name:
			yield pos, Name.Namespace, ref_name
			pos += len(ref_name)
		yield pos, String, " <"
		pos += 2
		yield pos, Name.Tag, ref_target
		pos += len(ref_target)
		yield pos, String, ">`"

	def _emit_inline_line(self, base: int, line: str) -> Iterable[tuple[int, object, str]]:
		cur = 0
		for m in RE_INLINE.finditer(line):
			if m.start() > cur:
				yield base + cur, String.Doc, line[cur : m.start()]

			token_txt = m.group(0)
			if m.group(1) is not None:
				yield base + m.start(), Keyword, m.group(1)
			elif m.group(2) is not None:
				yield base + m.start(), Keyword.Constant, m.group(2)
			elif m.group(3) is not None and m.group(4) is not None:
				yield base + m.start(), Keyword, m.group(3)
				arg_start = base + m.start() + len(m.group(3))
				yield from self._emit_ref_arg(arg_start, m.group(4))
			elif m.group(5) is not None and m.group(6) is not None:   # lit
				yield base + m.start(), Keyword, m.group(5)
				yield base + m.start() + len(m.group(5)), Literal, m.group(6)
			elif m.group(7) is not None and m.group(8) is not None:   # var
				yield base + m.start(), Keyword, m.group(7)
				yield base + m.start() + len(m.group(7)), Name.Variable, m.group(8)
			elif m.group(9) is not None and m.group(10) is not None:  # type
				yield base + m.start(), Keyword, m.group(9)
				yield base + m.start() + len(m.group(9)), Name.Class, m.group(10)
			elif m.group(11) is not None and m.group(12) is not None: # mod
				yield base + m.start(), Keyword, m.group(11)
				yield base + m.start() + len(m.group(11)), Name.Namespace, m.group(12)
			elif m.group(13) is not None and m.group(14) is not None: # value
				yield base + m.start(), Keyword, m.group(13)
				yield base + m.start() + len(m.group(13)), Name.Constant, m.group(14)
			elif m.group(15) is not None and m.group(16) is not None: # op
				yield base + m.start(), Keyword, m.group(15)
				yield base + m.start() + len(m.group(15)), Operator, m.group(16)
			elif m.group(17) is not None and m.group(18) is not None: # func
				yield base + m.start(), Keyword, m.group(17)
				yield base + m.start() + len(m.group(17)), Name.Function, m.group(18)
			elif m.group(19) is not None and m.group(20) is not None: # label
				yield base + m.start(), Keyword, m.group(19)
				yield base + m.start() + len(m.group(19)), Generic.Subheading, m.group(20)
			elif m.group(21) is not None and m.group(22) is not None: # attr
				yield base + m.start(), Keyword, m.group(21)
				yield base + m.start() + len(m.group(21)), Name.Attribute, m.group(22)
			elif m.group(23) is not None and m.group(24) is not None: # file
				yield base + m.start(), Keyword, m.group(23)
				yield base + m.start() + len(m.group(23)), String.Other, m.group(24)
			elif m.group(25) is not None and m.group(26) is not None: # dfn
				yield base + m.start(), Keyword, m.group(25)
				yield base + m.start() + len(m.group(25)), Generic.Emph, m.group(26)
			elif m.group(27) is not None and m.group(28) is not None: # term
				yield base + m.start(), Keyword, m.group(27)
				yield base + m.start() + len(m.group(27)), Generic.Emph, m.group(28)
			elif m.group(29) is not None and m.group(30) is not None: # cmd
				yield base + m.start(), Keyword, m.group(29)
				yield base + m.start() + len(m.group(29)), Name.Builtin, m.group(30)
			elif m.group(31) is not None and m.group(32) is not None: # opt
				yield base + m.start(), Keyword, m.group(31)
				yield base + m.start() + len(m.group(31)), Name.Variable, m.group(32)
			elif m.group(33) is not None and m.group(34) is not None: # tag
				yield base + m.start(), Keyword, m.group(33)
				yield base + m.start() + len(m.group(33)), Name.Tag, m.group(34)
			elif m.group(35) is not None and m.group(36) is not None: # norm
				yield base + m.start(), Keyword, m.group(35)
				yield base + m.start() + len(m.group(35)), Keyword, m.group(36)
			elif m.group(37) is not None and m.group(38) is not None: # var_type
				yield base + m.start(), Keyword, m.group(37)
				yield base + m.start() + len(m.group(37)), Name.Class, m.group(38)
			elif m.group(39) is not None and m.group(40) is not None: # generic role
				yield base + m.start(), String.Doc, m.group(39)
				yield base + m.start() + len(m.group(39)), String.Doc, m.group(40)
			elif m.group(41) is not None:
				yield base + m.start(), Keyword, m.group(41)
			else:
				yield base + m.start(), Name.Constant, token_txt
			cur = m.end()

		if cur < len(line):
			yield base + cur, String.Doc, line[cur:]

	def highlight_line(self, base: int, line: str) -> Iterable[tuple[int, object, str]]:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Definitions, Contract, Parameters, Returns, Raises
		Definitions:
			_inherit:
				Pos_Role_Substring_Triple
		Contract:
			general:
				|Must| analyze the given line in the context of the current section and subsection.
				|Must| identify section headers and update the current section state.
				|Must| identify subsection headers if the current section allows subsections, and update the current subsection state.
				|Must| identify special markers such as text flow markers and apply appropriate token types.
				|Must| apply specific tokenization rules based on the current section and subsection, such as treating certain lines as lists of identifiers or free-form text.
				|Must| yield tokens with appropriate types for the identified elements in the line.
		Parameters:
			base:
				The base index for token positions in the original text.
			line:
				The line of text to analyze and tokenize.
		Returns:
			An iterable of |term|`Pos_Role_Substring_Triple` tuples for the given line.
		Raises:
			BaseException:
				|May| propagate exceptions from the |mod|`re` module.
		"""
		stripped = line.rstrip("\r\n")
# Analyze for section labels
		m_sec = RE_SECTION_CAPTURE.match(stripped)
		if m_sec is not None:
			self._current_section = m_sec.group(1)
			self._current_subsection = ""
			yield base, Generic.Heading, line
			return
# Analyze for subsection labels
		if self._current_section in SECTIONS_WITH_SUBSECTIONS:
			m = self._find_subsection_match(stripped)
			if m is not None:
				yield from self._emit_subsection_line(base, line, m)
				return
# Analyze for paragraph marker
		if RE_TEXTFLOW_MARKER.fullmatch(stripped):
			yield base, Keyword, line
			return
# Analyze for bullet list marker
		line_no_nl = line[:-1] if line.endswith("\n") else line
		m_bullet = RE_LIST_MARKER.match(line_no_nl)
		if m_bullet is not None:
			indent = m_bullet.group(1)
			marker = m_bullet.group(2)
			gap = m_bullet.group(3)
			rest = m_bullet.group(4)
			prefix_len = len(indent) + len(marker) + len(gap)
			if indent:
				yield base, String.Doc, indent
			yield base + len(indent), Keyword, marker
			if gap:
				yield base + len(indent) + len(marker), String.Doc, gap
			if rest:
				yield from self._emit_inline_line(base + prefix_len, rest)
			if line.endswith("\n"):
				yield base + len(line_no_nl), String.Doc, "\n"
			return

# Special handling of "normative_sections"
		if self._current_section == "Preamble":
			if self._current_subsection == "normative_sections":
				yield from self._emit_normative_sections_line(base, line)
				return
			elif self._current_subsection in ("status", "scope"):
				yield from self._emit_csv_identifiers_line(base, line, Name.Constant)
				return
			elif self._current_subsection == "profile":
				yield from self._emit_csv_identifiers_line(base, line, Name.Constant)
				return
			else:
				yield from self._emit_inline_line(base, line)
				return
		if self._current_section == "Contract":
			if self._current_subsection == "traits":
				yield from self._emit_csv_identifiers_line(base, line, Name.Constant)
				return
			elif self._current_subsection == "base":
				yield from self._emit_csv_identifiers_line(base, line, Name.Class)
				return
			else:
				yield from self._emit_inline_line(base, line)
				return

		if self._current_section in SECTION_LIST_TYPE_QUALIFIED:
			yield from self._emit_csv_identifiers_line(base, line, Name.Class)
			return
		if self._current_section in SECTION_LIST_FUNC_QUALIFIED:
			yield from self._emit_csv_identifiers_line(base, line, Name.Function)
			return
		if self._current_section in SECTION_LIST_GENERIC_QUALIFIED:
			yield from self._emit_csv_identifiers_line(base, line, Name.Variable)
			return
		if self._current_section in SECTION_MAP_EXCEPTION_QUALIFIED_IDENTIFIER_TO_FREEFORM:
			yield from self._emit_inline_line(base, line)
			return
		if self._current_section in SECTION_MAP_TERM_IDENTIFIER_TO_FREEFORM:
			yield from self._emit_inline_line(base, line)
			return
		if self._current_section in SECTION_MAP_ANY_IDENTIFIER_TO_FREEFORM:
			yield from self._emit_inline_line(base, line)
			return
		if self._current_section in SECTION_MAP_VAR_IDENTIFIER_TO_FREEFORM:
			yield from self._emit_inline_line(base, line)
			return
		if self._current_section in SECTION_MAP_TYPE_IDENTIFIER_TO_FREEFORM:
			yield from self._emit_inline_line(base, line)
			return
		if self._current_section in SECTION_MAP_FUNC_IDENTIFIER_TO_FREEFORM:
			yield from self._emit_inline_line(base, line)
			return
		if self._current_section in ("Returns","Description"):
			yield from self._emit_inline_line(base, line)
			return

		yield from self._emit_inline_line(base, line)

	@staticmethod
	def has_mixed_indentation(text: str) -> bool:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| check for the presence of mixed indentation in the text.
				|Must| consider a line to have mixed indentation if it contains\
				both tabs and spaces in the leading whitespace.
				|Must| consider the text to have mixed indentation if there are\
				some lines that use tabs for indentation and some lines that\
				use spaces, even if no individual line has mixed indentation.
		Parameters:
			text:
				The string to analyze for mixed indentation.
		Returns:
			|True| if the text has mixed indentation, |False| otherwise.
		Raises:
			BaseException:
				|May| propagate from module |mod|`re`.
				|May| propagate from module |mod|`sys`.
		"""
		uses_tabs = False
		uses_spaces = False
		for line in text.splitlines():
			if not line.strip():
				continue
			indent = line[: len(line) - len(line.lstrip())]
			if not indent:
				continue
			if " " in indent and "\t" in indent:
				return True
			if "\t" in indent:
				uses_tabs = True
			if " " in indent:
				uses_spaces = True
			if uses_tabs and uses_spaces:
				return True
		return False

	@staticmethod
	def looks_like_waterloo_docstring(text: str) -> bool:
		r"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
			scope:
				core
		Description:
			This method performs a heuristic analysis of the input text
			to determine if it resembles a Waterloo-docstring.
			For a full and exact validation use the tool |cmd|`waterlint` instead,
			which implements the complete set of normative rules for Waterloo-docstrings.
		Contract:
			general:
				|Must| look for the presence of a |label|`Preamble` and |label|`Contract` section (PRE-001, CON-001).
				|Must| check that the section labels match the expected format (PRSR-001, PRSR-002, PRSR-003, PRSR-004, PRSR-005).
				|Must| check that the |label|`Preamble` and |label|`Contract` sections appear in the correct order (PRE-001).
				|Must| check that there is no mixed indentation in the docstring (TKN-003).
		Parameters:
			text:
				The string to analyze
		Returns:
			|True| if the string looks like a Waterloo docstring, |False| otherwise.
		Raises:
			BaseException:
				|May| propagate from module |mod|`re`.
		"""
		found_preamble = False
		found_contract = False
		for line in text.splitlines():
			if not found_preamble and RE_PREAMBLE.match(line):
				found_preamble = True
			if not found_contract and RE_CONTRACT.match(line):
				if not found_preamble:
					return False
				found_contract = True
			if found_preamble and found_contract:
				if PythonWaterlooLexer.has_mixed_indentation(text):
					return False
				return True
		return False
