from __future__ import annotations

import re
from typing import Iterable, Iterator

from pygments.lexer import Lexer
from pygments.lexers.python import PythonLexer
from pygments.token import Generic, Keyword, Name, String, Literal


RE_SECTION = re.compile(
	r"^\s*(?:"
	r"Preamble|Contract|Parameters|Returns|Raises|Notes|See_also|"
	r"Definitions|Terminology|Description|Derived_from|Factory|"
	r"Public_[A-Za-z_][A-Za-z0-9_]*|"
	r"[A-Za-z_][A-Za-z0-9_]*_overview"
	r"):\s*$"
)
RE_SUBSECTION = re.compile(
	r"^(\s*)([A-Za-z_][A-Za-z0-9_.]*:)(\s*)$"
)

# 1: Normativity keywords
# 2: Special values
# 3,4: Semantic role and argument
RE_INLINE = re.compile(
	r"(\|(?:Must|must|Must_not|must_not|Should|should|Should_not|should_not|May|may)\|)"
	r"|(\|(?:Self|None|True|False)\|)"
	r"|(\|ref\|)(`[^`]+`)"
	r"|(\|[A-Za-z_][A-Za-z0-9_]*\|)(`[^`]+`)"
)
RE_REF_ARG = re.compile(r"^(.*?)\s*<([^<>]+)>\s*$")


class PythonWaterlooLexer(PythonLexer):
	"""
	Python lexer with lightweight Waterloo-docstring highlighting.

	Usage (without installation):
		pygmentize -x -l package_ide-plugins/pygmentize/python_waterloo_lexer.py:PythonWaterlooLexer file.py
	"""

	name = "Python-Waterloo"
	aliases = ["python-waterloo"]
	filenames = ["*.py"]

	def get_tokens_unprocessed(self, text: str) -> Iterator[tuple[int, object, str]]:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Definitions, Parameters, Returns, Raises
		Definitions:
			Pos_Role_Substring_Triple:
				A tuple containing the specification the caller needs for
				assigning syntax highlighting to a substring. If the components
				of the tuple are addressed by [...], [0] represents the
				position of the substring in the original string, [1] is a class object
				representing the semantic class to be assigned, as defined in |mod|`pygments.token`.
				[2] is substring to be highlighted.
		Contract:
			general:
				|Must| analyze the string passed.
				|Must| iterate over the lines of the input and look for waterloo specific tokens.
				|Must| generate a |term|`Pos_Role_Substring_Triple` for each matching waterloo specific token found.
				|Must| fall back to the default highlighting for docstrings where no waterloo token matches,
		Parameters:
			text:
				The string to analyze
		Returns:
			An iterable over |term|`Pos_Role_Substring_Triple`-s.
		Raises:
			BaseException:
				|May| propagate from module |mod|`pygments`.	
		"""
		for index, ttype, value in super().get_tokens_unprocessed(text):
			if ttype in String.Doc:   # oder is String.Doc
				yield from self._highlight_docstring(index, value)
			else:
				yield index, ttype, value

	@staticmethod
	def analyse_text(text: str) -> float:
		if "Preamble:" in text and "Contract:" in text:
			return 0.25
		if "|Must|" in text or "|Should|" in text:
			return 0.15
		return 0.0

	def _highlight_docstring(self, base: int, text: str) -> Iterable[tuple[int, object, str]]:
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
			yield from self._highlight_line(base + pos, line)
# Advance to next line.
			pos = next_pos

	def _highlight_line(self, base: int, line: str) -> Iterable[tuple[int, object, str]]:
		stripped = line.rstrip("\n")
# Analyze for section labels
		if RE_SECTION.match(stripped):
			yield base, Generic.Emph, line
			return
# Analyze for subsection labels
		m = RE_SUBSECTION.match(stripped)
		if m is not None:
			prefix, label, suffix = m.groups()
			cur = base
			if prefix:
				yield cur, String.Doc, prefix
				cur += len(prefix)
# Special subsection Definitions._inherit.
			if label == "_inherit:":
				yield cur, Keyword, label
			else:
				yield cur, Generic.Heading, label
			cur += len(label)
			if suffix:
				yield cur, String.Doc, suffix
				cur += len(suffix)
			if line.endswith("\n"):
				yield cur, String.Doc, "\n"
			return

		cur = 0
		for m in RE_INLINE.finditer(line):
# Default for everything before the first token or between two tokens.
			if m.start() > cur:
				yield base + cur, String.Doc, line[cur : m.start()]
			token_txt = m.group(0)
# Group 1: Normativity keywords
			if m.group(1) is not None:
				yield base + m.start(), Keyword, m.group(1)
# Group 2: Special values
			elif m.group(2) is not None:
				yield base + m.start(), Keyword.Constant, m.group(2)
# Groups 3 and 4: Semantic role 'ref' and argument
			elif m.group(3) is not None and m.group(4) is not None:
				yield base + m.start(), Keyword, m.group(3)
				arg = m.group(4)
				arg_start = base + m.start() + len(m.group(3))
				if len(arg) >= 2 and arg[0] == "`" and arg[-1] == "`":
					inner = arg[1:-1]
					m_ref = RE_REF_ARG.match(inner)
					if m_ref is not None:
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
					else:
						yield arg_start, Name.Tag, arg
				else:
					yield arg_start, Name.Tag, arg
# Groups 5 and 6: Semantic role and argument
			elif m.group(5) is not None and m.group(6) is not None:
				yield base + m.start(), Keyword, m.group(5)
				yield base + m.start() + len(m.group(5)), Literal, m.group(6)
			else:
				yield base + m.start(), Name.Constant, token_txt
			cur = m.end()

# Fall back to default docstring role.
		if cur < len(line):
			yield base + cur, String.Doc, line[cur:]


