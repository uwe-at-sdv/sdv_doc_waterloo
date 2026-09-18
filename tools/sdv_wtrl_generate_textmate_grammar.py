#!/usr/bin/env python3
"""Generate the Waterloo TextMate grammar from its maintained template."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from sdv.doc.waterloo.docitem_helper import SECTION_PROPERTIES


PATH_IDE_PLUGINS = Path(__file__).resolve().parents[1]
PATH_SYNTAXES = PATH_IDE_PLUGINS / "vscode" / "syntaxes"
PATH_TEMPLATE = PATH_SYNTAXES / "waterloo.injection.tmLanguage.template.json"
PATH_OUTPUT = PATH_SYNTAXES / "waterloo.injection.tmLanguage.json"

RE_PLACEHOLDER = re.compile(r"\{\{(WTRL_[A-Z0-9_]+)\}\}")


def _top_level_section_labels() -> str:
	"""Return a regex alternation for all Waterloo top-level section labels."""
	labels = [label for label in SECTION_PROPERTIES if "." not in label]
	return "(?:" + "|".join(re.escape(label) for label in labels) + ")"


def _replacement_values() -> dict[str, str]:
	"""Return template replacement values; values may themselves contain placeholders."""
	return {
		"WTRL_PY_IDENTIFIER": r"[A-Za-z_][A-Za-z0-9_]*",
		"WTRL_DOCSTRING_DELIMITER": r"(?:\\\"\\\"\\\"|''')",
		"WTRL_DOCSTRING_END": r"\\s*{{WTRL_DOCSTRING_DELIMITER}}",
		"WTRL_TOP_LEVEL_SECTION_LABELS": _top_level_section_labels(),
		"WTRL_TOP_LEVEL_SECTION_END": (
			r"^(?=(?:\\1{{WTRL_TOP_LEVEL_SECTION_LABELS}}:|\\s*(?:\\\"\\\"\\\"|''')))"
		),
	}


def _expand_placeholders(template: str, replacements: dict[str, str]) -> str:
	"""Expand all placeholders recursively and reject unknown or cyclic replacements."""
	text = template
	for _ in range(len(replacements) + 1):
		match = RE_PLACEHOLDER.search(text)
		if match is None:
			return text

		unknown = sorted({name for name in RE_PLACEHOLDER.findall(text) if name not in replacements})
		if unknown:
			raise ValueError(f"Unknown TextMate template placeholder(s): {', '.join(unknown)}")
		text = RE_PLACEHOLDER.sub(lambda match: replacements[match.group(1)], text)

	remaining = ", ".join(sorted(set(RE_PLACEHOLDER.findall(text))))
	raise ValueError(f"Cyclic TextMate template placeholder(s): {remaining}")


def _backup_path(output_path: Path) -> Path:
	"""Return the UTC-timestamped backup path for an overwritten grammar file."""
	stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
	return output_path.with_name(f"waterloo.injection.tmLanguage.{stamp}.json")


def _parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--template", type=Path, default=PATH_TEMPLATE, help=f"Template path (default: {PATH_TEMPLATE}).")
	parser.add_argument("--out", type=Path, default=PATH_OUTPUT, help=f"Generated grammar path (default: {PATH_OUTPUT}).")
	return parser.parse_args()


def main() -> int:
	args = _parse_args()
	template_path = args.template.resolve()
	output_path = args.out.resolve()
	template = template_path.read_text(encoding="utf-8")
	generated = _expand_placeholders(template, _replacement_values())
	json.loads(generated)

	if output_path.exists() and output_path.read_text(encoding="utf-8") == generated:
		print(f"TextMate grammar is up to date: {output_path}")
		return 0

	output_path.parent.mkdir(parents=True, exist_ok=True)
	if output_path.exists():
		backup_path = _backup_path(output_path)
		if backup_path.exists():
			raise FileExistsError(f"Refusing to overwrite existing backup: {backup_path}")
		shutil.copy2(output_path, backup_path)
		print(f"Backed up TextMate grammar: {backup_path}")

	output_path.write_text(generated, encoding="utf-8")
	print(f"Generated TextMate grammar: {output_path}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
