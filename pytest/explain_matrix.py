#!/usr/bin/env python3
"""Print the explain-section matrix as JSON in profile-major order."""

from __future__ import annotations

import json
import sys

from sdv.doc.waterloo.waterlint_explain_common import (
	SECTION_SUBSECTIONS,
	build_section_explanation,
)


def main() -> int:
	matrix = []
	for profile in ("module", "class", "function", "method", "inherited_method"):
		profile_entry = {
			"profile": profile,
			"sections": [],
		}
		profile_map = SECTION_SUBSECTIONS
		labels = [label for label, prof_map in profile_map.items() if profile in prof_map]
		for label in labels:
			spec = build_section_explanation(label, profile)
			if spec is None:
				profile_entry["sections"].append({"label": label, "missing": True})
				continue
			profile_entry["sections"].append(
				{
					"label": label,
					"title": spec["title"],
					"body_category": spec["body_category"],
					"normativity": spec["normativity"],
					"label_kind": spec["label_kind"],
					"must_exist": spec["must_exist"],
					"available_profiles": list(spec["available_profiles"]),
					"subsections": list(spec["subsections"]),
					"body": list(spec["body"]),
					"itemization": dict(spec["itemization"]),
					"markup": dict(spec["markup"]),
					"template": list(spec["template"]),
					"hint": list(spec["hint"]),
					"try_self": spec["try_self"],
					"try_next": list(spec["try_next"]),
				}
			)
		matrix.append(profile_entry)
	json.dump({"profiles": matrix}, sys.stdout, indent=2, ensure_ascii=False)
	sys.stdout.write("\n")
	return 0


if __name__ == "__main__":
	sys.exit(main())
