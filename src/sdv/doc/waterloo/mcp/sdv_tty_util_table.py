"""
Preamble:
    profile:
        module
    normative_sections:
        Definitions, Contract, Public_classes, Public_functions, Public_types, See_also
    scope:
        public
Definitions:
    ansi_escape_sequence, ansi_escape_sequences:
        Terminal control sequences used for colors and text attributes.
Terminology:
    Terminal cell width:
        The number of columns a string occupies in a monospace terminal.
Contract:
    general:
        |Must| render framed tables with multiline cells and captions.
        |Must| measure visible text by terminal cell width rather than codepoint count.
        |Must| ignore ANSI escape sequences when calculating layout.
Description:
    Render framed text tables with captions, column alignment, and multiline cells.
    The module keeps ANSI styling in cell content while using terminal display width
    for layout calculations.
Notes:
    Width calculation:
        Terminal widths are computed with wcwidth.
Public_classes:
    Align, StyleSheet, table
Class_overview:
    Align:
        Column alignment values.
    StyleSheet:
        Mutable table border style definition.
    table:
        The main table builder and renderer.
Public_functions:
    set_style, get_style
Function_overview:
    set_style:
        Set the global table border style.
    get_style:
        Return the current table border style.
Public_types:
    Style_t:
        Allowed style names.
See_also:
    sdv.tty.util.ansi
"""

# Versions:
# - 1.2.1 [2026-07-07]	Spin-off for sdv.doc.waterloo.mcp
# - 1.2.0 [2026-06-27]	Decouple from 3DE4-version. Type annotations.
# - 1.1.4 [2025-11-19]	versioning details
# - 1.1.3 [2022-12-20]	allow both import explicit or via package sdv.
# - 1.1.2 [2022-11-20]	minor changes, functionality not affected
# - 1.1.1 [2022-08-02]	minor changes, functionality not affected
# - 1.1.0 [2022-07-05]	unicode rendering
# - 1.0.0 [0000-00-00]	first version, ascii rendering

from __future__ import annotations

__version__ = "1.2.1"

import sys
import string
import re
import wcwidth
from typing import Any, Final, Iterable, Literal, Sequence
from enum import IntEnum

ANSI_ESCAPE_SEQUENCE_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def strip_ansi_escape_sequences(s: str) -> str:
	return ANSI_ESCAPE_SEQUENCE_RE.sub("", s)


def wcswidth(s: str) -> int:
	return wcwidth.wcswidth(s)

# Helpers from sdv.tty.util.ansi
def display_width(s: str) -> int:
	width = wcswidth(strip_ansi_escape_sequences(s))
	return width if width >= 0 else len(strip_ansi_escape_sequences(s))

# Backward-compatible name.
def strlen(s: str) -> int:
	return display_width(s)

#----- begin Typing ------------------------------------------#
Style_t = Literal["ascii","fancy_ascii","unicode"]

class Align(IntEnum):
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_constants, See_also
		scope:
			public
	Contract:
		general:
			|Must| provide symbolic column alignment values for table rendering.
		constructor:
			|Must| be enum-like and directly usable as integer alignment values.
		traits:
			final
	Public_constants:
		COL_ALIGN_LEFT:
			Left column alignment value.
		COL_ALIGN_RIGHT:
			Right column alignment value.
	See_also:
		sdv.tty.util.table
	"""
	COL_ALIGN_LEFT = 0
	COL_ALIGN_RIGHT = 1
#----- end Typing --------------------------------------------#

#----- begin State -------------------------------------------#

class StyleSheet:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods, See_also
		scope:
			public
	Contract:
		general:
			|Must| define a mutable border style for framed tables.
		constructor:
			|Must| be default-constructible.
		traits:
			final
	Public_methods:
		set_style
	See_also:
		sdv.tty.util.table
	"""
	HOR_DASH: str = "-"
	VER_DASH: str = "|"
	LEFT_MARK: str = "+"
	RIGHT_MARK: str = "+"
	TOP_MARK: str = "+"
	BOTTOM_MARK: str = "+"
	UPPER_LEFT_MARK: str = "+"
	UPPER_RIGHT_MARK: str = "+"
	LOWER_LEFT_MARK: str = "+"
	LOWER_RIGHT_MARK: str = "+"
	CENTER_MARK: str = "+"

	def set_style(self, s: Style_t) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| update all border glyphs to match the requested style.
		Parameters:
			s:
				Named table style to apply.
		Returns:
		Raises:
			ValueError:
				Unknown style name.
		"""
		if s == "raw":
			self.HOR_DASH		= " "
			self.VER_DASH		= " "
			self.LEFT_MARK		= " "
			self.RIGHT_MARK		= " "
			self.TOP_MARK		= " "
			self.BOTTOM_MARK	= " "
			self.UPPER_LEFT_MARK	= " "
			self.UPPER_RIGHT_MARK	= " "
			self.LOWER_LEFT_MARK	= " "
			self.LOWER_RIGHT_MARK	= " "
			self.CENTER_MARK	= " "
		elif s == "fancy_ascii":
			self.HOR_DASH		= "-"
			self.VER_DASH		= "|"
			self.LEFT_MARK		= ">"
			self.RIGHT_MARK		= "<"
			self.TOP_MARK		= "v"
			self.BOTTOM_MARK		= "^"
			self.UPPER_LEFT_MARK	= "/"
			self.UPPER_RIGHT_MARK	= "\\"
			self.LOWER_LEFT_MARK	= "\\"
			self.LOWER_RIGHT_MARK	= "/"
			self.CENTER_MARK		= "+"
		elif s == "unicode":
			self.HOR_DASH		= "\u2500"
			self.VER_DASH		= "\u2502"
			self.LEFT_MARK		= "\u251c"
			self.RIGHT_MARK		= "\u2524"
			self.TOP_MARK		= "\u252c"
			self.BOTTOM_MARK		= "\u2534"
			self.UPPER_LEFT_MARK	= "\u250c"
			self.UPPER_RIGHT_MARK	= "\u2510"
			self.LOWER_LEFT_MARK	= "\u2514"
			self.LOWER_RIGHT_MARK	= "\u2518"
			self.CENTER_MARK		= "\u253c"
		elif s == "ascii":
			self.HOR_DASH		= "-"
			self.VER_DASH		= "|"
			self.LEFT_MARK		= "+"
			self.RIGHT_MARK		= "+"
			self.TOP_MARK		= "+"
			self.BOTTOM_MARK		= "+"
			self.UPPER_LEFT_MARK	= "+"
			self.UPPER_RIGHT_MARK	= "+"
			self.LOWER_LEFT_MARK	= "+"
			self.LOWER_RIGHT_MARK	= "+"
			self.CENTER_MARK		= "+"
		else:
			raise ValueError(f"Unknown style: {s}")

# Current style sheet. Set right before printing a table
# by set_style(...).
_style_sheet: StyleSheet = StyleSheet()
# The current style as string.
__style: Style_t = "ascii"
#----- end State ---------------------------------------------#

# API-function.
def set_style(s: Style_t) -> None:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| set the global table border style.
	Parameters:
		s:
			Named table style to apply.
	Returns:
	Raises:
		ValueError:
			Unknown style name.
	"""
	global _style_sheet
	_style_sheet.set_style(s)
	global __style
	__style = s

def get_style() -> Style_t:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| return the current global table border style.
	Parameters:
	Returns:
		The current table style name.
	Raises:
	"""
	global __style
	return __style
# Conservative
set_style("ascii")


class cell:
# text must be printable. If text is a table instance,
# margins are stripped of the table are stripped for
# a better look.
	def __init__(self, t: table, col: int, text: Any) -> None:
		self._table = t
# This cell is in column:
		self._col = col
		if isinstance(text,table):
# Tables are inserted without margin.
			self._lines = text.str_no_margin().split("\n")
		else:
# Split string at CR and add margin to each segment. 'list' for python 2 and 3.
			self._lines = list(map(lambda l:" " + l + " ",str(text).split("\n")))

		self._h_min = len(self._lines)
		self._lens = []
		for line in self._lines:
			self._lens.append(strlen(line))
# Minimum requirement of this cell
		self._w_min = max(self._lens)
		self._w = self._w_min
	def __str__(self):
		if self._table._i_clir < self._h_min:
			if self._col in self._table._col_align and self._table._col_align[self._col] == Align.COL_ALIGN_LEFT:
				return  self._lines[self._table._i_clir] + (" " * (self._w - self._lens[self._table._i_clir]))
			else:
				return  (" " * (self._w - self._lens[self._table._i_clir])) + self._lines[self._table._i_clir]
		else:
			return " " * self._w
		
class row:
	def __init__(self, table: table) -> None:
		self._table = table
		self._cells: list[cell] = []
		self._w = 0
		self._h = 0
	def cell(self, col: int, text: Any) -> None:
		self._cells.append(cell(self._table,col,text))
	def num_cols(self) -> int:
		return len(self._cells)
	def done(self) -> None:
# Cells can require different heights. The row adopts
# the maximum of these heights as its own height.
		self._h = 0
		heights = list(map(lambda c:c._h_min,self._cells))
		if len(heights) > 0:
			self._h = max(heights)
	def __str__(self):
		sht = _style_sheet
		s = sht.VER_DASH
		for c in self._cells:
			s += str(c) + sht.VER_DASH
		return s
class sep:
	def __init__(self, table: table, i_row: int) -> None:
		self._table = table
		self._i_row = i_row
		self._h = 1
	def __str__(self) -> str:
		sht = _style_sheet
		with_center_marks = False
# Check if sep is surrounded by rows. If this is the case,
# "+"-marks are printed as intersections of lines.
		if self._i_row - 1 >= 0:
			if isinstance(self._table._rows[self._i_row - 1],row):
				with_center_marks = True
		if self._i_row + 1 < len(self._table._rows):
			if isinstance(self._table._rows[self._i_row + 1],row):
				with_center_marks = True
		s = ""

		if self._i_row - 1 < 0:
			left_mark = sht.UPPER_LEFT_MARK
			right_mark = sht.UPPER_RIGHT_MARK
			center_mark = sht.TOP_MARK
		elif self._i_row + 1 >= len(self._table._rows):
			left_mark = sht.LOWER_LEFT_MARK
			right_mark = sht.LOWER_RIGHT_MARK
			center_mark = sht.BOTTOM_MARK
		else:
			left_mark = sht.LEFT_MARK
			right_mark = sht.RIGHT_MARK
# exists
			if not isinstance(self._table._rows[self._i_row + 1],row):
				center_mark = sht.BOTTOM_MARK
# exists
			elif not isinstance(self._table._rows[self._i_row - 1],row):
				center_mark = sht.TOP_MARK
			else:
				center_mark = sht.CENTER_MARK

		if with_center_marks:
			start = True
			for i in self._table._col_info:
				if start:
					start = False
					s += left_mark
				else:
					s += center_mark
				s += sht.HOR_DASH * i
			s += right_mark
		else:
			if len(self._table._col_info) > 0:
				for i in range(len(self._table._col_info)):
					s += (left_mark if i == 0 else sht.HOR_DASH)
					s += sht.HOR_DASH * self._table._col_info[i]
				s += right_mark
			else:
# If there are no rows and only captions draw at least a reasonable boundary.
# By this rule we can also get a well-defined empty table representation.
				s += left_mark + sht.HOR_DASH * max(0,self._table._w - 2)
				s += right_mark
		return s

class caption:
	def __init__(self, table: table, text: Any) -> None:
		self._table = table
		self._h = 1
# By 'list' we make it work in both python 2 and 3.
		self._lines = list(map(lambda l:" " + l + " ",str(text).split("\n")))
		self._h_min = len(self._lines)
		self._lens = []
		for line in self._lines:
			self._lens.append(strlen(line))
# Minimum requirement of this cell
		self._w_min = max(self._lens)
		self._w = self._w_min
	def __str__(self):
		sht = _style_sheet
		s = sht.VER_DASH
		if self._table._i_clir < self._h_min:
# If there is space around a caption line, we'll center the text.
			spc = self._w - self._lens[self._table._i_clir]
			spc_left = int(spc / 2)
			spc_right = spc - spc_left
			s += " " * spc_left + self._lines[self._table._i_clir] + " " * spc_right
		else:
			s += " " * self._w
		s += sht.VER_DASH
		return s

class table:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Public_methods, See_also
		scope:
			public
	Contract:
		general:
			|Must| render framed tables with captions, aligned columns, and multiline cells.
			|Must| measure visible text by terminal cell width rather than codepoint count.
			|Must| ignore ANSI escape sequences when calculating layout.
		constructor:
			|Must| create an empty table with a leading separator row.
		traits:
			final
	Notes:
		Width calculation:
			Terminal widths are computed with wcwidth.
	Public_methods:
		col_align,
		caption,
		row,
		rows,
		sep,
		done,
		__str__,
		str_no_margin
	See_also:
		sdv.tty.util.ansi
	"""
	def __init__(self) -> None:
		self._done = False
		self._num_cols = 0
		self._rows: list[Any] = []
		self._col_align: dict[int, int] = {}
		self.sep()
# Total width
		self._w = 0
# current line in row while printing
		self._i_clir = 0
	def col_align(self, col: int, align: int) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| store the alignment for the given column.
		Parameters:
			col:
				Column index to configure, starting at 0.
			align:
				Alignment value for the column.
		Returns:
		Raises:
		"""
		self._col_align[col] = align
	def caption(self, text: Any) -> table:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| append a centered caption row to the table.
		Parameters:
			text:
				Caption text, possibly multiline.
		Returns:
		Raises:
		"""
		self._rows.append(caption(self,text))
		return self
	def row(self, *args: Any) -> table:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| append one table row with one cell per argument.
		Parameters:
			args:
				Cell contents for the new row.
		Returns:
		Raises:
		"""
		if isinstance(args,tuple):
			pass
		self._num_cols = max(self._num_cols,len(args))
		r = row(self)
		i_col = 0
		for arg in args:
			r.cell(i_col,arg)
			i_col += 1
		r.done()
		self._rows.append(r)
		return self
# Insert many rows at one
	def rows(self, r: Iterable[Sequence[Any]]) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| append each provided sequence as a table row.
		Parameters:
			r:
				Iterable of row sequences.
		Returns:
		Raises:
		"""
		for row in r:
			self.row(*row)
	def sep(self) -> table:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| append a separator row to the table.
		Parameters:
		Returns:
		Raises:
		"""
		self._rows.append(sep(self,len(self._rows)))
		return self
	def done(self) -> None:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| finalize table geometry before rendering.
				|Must| be safe to call repeatedly.
				|Must| be called implicitly by __str__ and str_no_margin when needed.
		Parameters:
		Returns:
		Raises:
		"""
# Terminating separator
		self.sep()
# Make all rows have same number of cells
		for r in self._rows:
			if isinstance(r,row):
				for i_col in range(r.num_cols(),self._num_cols):
					r.cell(i_col,"")
# Find out widths of columns
		self._col_info = [0] * self._num_cols
		for i_col in range(len(self._col_info)):
			self._col_info[i_col] = max(map(lambda r:r._cells[i_col]._w_min,[r for r in self._rows if isinstance(r,row)]))
# Find out total width: col widths + 1 for each vertical col seperator + 1 for initial vertical bar.
		self._w = sum(self._col_info) + self._num_cols + 1
# Blow up captions to correct size
		w_max = 0
		for r in self._rows:
			if isinstance(r,caption):
				w_max = max(w_max,r._w,self._w - 2)
		for r in self._rows:
			if isinstance(r,caption):
				r._w = w_max

# Rethink table width due to long captions. "2+" for initial and final vertical bar.
		w_old = self._w
		cap_widths = list(map(lambda r:2 + r._w,[r for r in self._rows if isinstance(r,caption)]))
		if len(cap_widths) > 0:
			self._w = max(self._w,*cap_widths)
# Blow up column infos due to long captions.
		delta_w = self._w - w_old
		while delta_w > 0:
			if len(self._col_info) > 0:
				for i in range(len(self._col_info)):
					self._col_info[i] += 1
					delta_w -= 1
					if delta_w <= 0:
						break
			else:
				delta_w = 0
# Blow up cells to correct size
		for r in self._rows:
			if isinstance(r,row):
				for c in r._cells:
					c._w = self._col_info[c._col]
				
	def __str__(self) -> str:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| render the complete table as a newline-separated string.
				|Must| finalize the table implicitly when needed.
		Parameters:
		Returns:
			The rendered table.
		Raises:
		"""
		if self._done is False:
			self.done()
			self._done = True
		s = ""
		for r in self._rows:
			for i_line in range(r._h):
				self._i_clir = i_line
				s += str(r) + "\n"
		return s

	def str_no_margin(self) -> str:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| render the table body without the outer margin columns.
				|Must| finalize table geometry before rendering.
		Parameters:
		Returns:
			The rendered table body without outer margins.
		Raises:
		"""
		if self._done is False:
			self.done()
			self._done = True
		s = []
		for r in self._rows[1:-1]:
			for i_line in range(r._h):
				self._i_clir = i_line
				s.append(str(r)[1:-1])
		return "\n".join(s)


if __name__ == '__main__':
	print("sdv.tty.table:",__version__)
