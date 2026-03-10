#!/usr/bin/env python3
"""Expand Waterloo TextMate template into a JSON grammar file."""

from __future__ import annotations

import builtins
import inspect
import re
import sys
from pathlib import Path
from typing import Final

for d in Path(__file__).resolve().parents:
	d_res = d.resolve()
	if (d_res / "sdv_doc_docitem_helper.py").exists():
		sys.path.insert(0,str(d_res))
		break
import sdv_doc_docitem_helper as wtrl

#import sdv.doc.waterloo.docitem_helper as wtrl

RE_COMMENT_LINE: Final[re.Pattern[str]] = re.compile(r"^\s*#.*$")

PLACEHOLDER_END_OF_SECTION: Final[str] = "{{RE_END_OF_SECTION}}"
PLACEHOLDER_END_OF_SUBSECTION: Final[str] = "{{RE_END_OF_SUBSECTION}}"
PLACEHOLDER_BUILTIN_EXCEPTIONS: Final[str] = "{{RE_BUILTIN_EXCEPTION_CLASSES}}"
PLACEHOLDER_IDENTIFIER: Final[str] = "{{RE_IDENTIFIER}}"
PLACEHOLDER_END_OF_DOCSTRING: Final[str] = "{{RE_END_OF_DOCSTRING}}"
PLACEHOLDER_TRAIT_VALUES: Final[str] = "{{RE_TRAIT_VALUES}}"
PLACEHOLDER_STATUS_VALUES: Final[str] = "{{RE_STATUS_VALUES}}"
PLACEHOLDER_SCOPE_VALUES: Final[str] = "{{RE_SCOPE_VALUES}}"

RE_END_OF_SECTION: Final[str] = (
	r"^(?=(?:\\1(?:Preamble|Contract|Parameters|Returns|Raises|Notes|See_also|"
	r"Definitions|Terminology|Description|Derived_from|Factory|"
	r"Public_(classes|functions|methods)|(?:Class|Function|Method)_overview):|"
	r"\\s*(?:\\\"\\\"\\\"|''')))"
)

RE_END_OF_SUBSECTION: Final[str] = (
	r"^(?=(?:[ \\\t]*[A-Za-z_][A-Za-z0-9_]*:|\\s*(?:\\\"\\\"\\\"|''')))"
)
RE_IDENTIFIER: Final[str] = r"[A-Za-z_][A-Za-z0-9_]*"
RE_END_OF_DOCSTRING: Final[str] = r"(?:\\\"\\\"\\\"|''')"

RE_TRAIT_VALUES = "|".join(re.escape(v) for v in wtrl.TRAIT_TAG_MAP.keys())
RE_STATUS_VALUES = "|".join(re.escape(v) for v in wtrl.STATUS_TAG_MAP.keys())
RE_SCOPE_VALUES = "|".join(re.escape(v) for v in wtrl.SCOPE_TAG_MAP.keys())


def _collect_builtin_exception_classes() -> str:
	names: list[str] = []
	for name, obj in vars(builtins).items():
		if not inspect.isclass(obj):
			continue
		if not issubclass(obj, BaseException):
			continue
		if issubclass(obj, Warning):
			continue
		names.append(name)
	names = sorted(set(names))
	return "|".join(names)


def _expand_template_text(text: str) -> str:
	replacements = {
		PLACEHOLDER_END_OF_SECTION: RE_END_OF_SECTION,
		PLACEHOLDER_END_OF_SUBSECTION: RE_END_OF_SUBSECTION,
		PLACEHOLDER_BUILTIN_EXCEPTIONS: _collect_builtin_exception_classes(),
		PLACEHOLDER_IDENTIFIER: RE_IDENTIFIER,
		PLACEHOLDER_END_OF_DOCSTRING: RE_END_OF_DOCSTRING,
		PLACEHOLDER_TRAIT_VALUES: RE_TRAIT_VALUES,
		PLACEHOLDER_STATUS_VALUES: RE_STATUS_VALUES,
		PLACEHOLDER_SCOPE_VALUES: RE_SCOPE_VALUES,
	}
	for placeholder, value in replacements.items():
		text = text.replace(placeholder, value)
	return text


def _strip_comment_lines(text: str) -> str:
	lines = text.splitlines(keepends=True)
	return "".join(line for line in lines if not RE_COMMENT_LINE.match(line))


def _derive_output_path(path_template: Path) -> Path:
	if path_template.suffix != ".template":
		raise ValueError("Template path must end with '.template'.")
	return path_template.with_suffix("")


def main(argv: list[str]) -> int:
	if len(argv) != 2:
		print("Usage: expand_textmate_template.py <path-to-*.template>", file=sys.stderr)
		return 2

	path_template = Path(argv[1])
	if not path_template.is_file():
		print(f"Template file not found: {path_template}", file=sys.stderr)
		return 2

	try:
		path_json = _derive_output_path(path_template)
	except ValueError as err:
		print(str(err), file=sys.stderr)
		return 2

	text = path_template.read_text(encoding="utf-8")
	text = _strip_comment_lines(text)
	text = _expand_template_text(text)
	path_json.write_text(text, encoding="utf-8")

	print(str(path_json))
	return 0


if __name__ == "__main__":
	raise SystemExit(main(sys.argv))
