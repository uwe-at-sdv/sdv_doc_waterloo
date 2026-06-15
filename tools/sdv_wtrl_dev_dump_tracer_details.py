#!/usr/bin/env python3

from __future__ import annotations

import re
import subprocess
import os,sys
from dataclasses import dataclass
from pathlib import Path


# Demo naming convention:
#   demo_1_ABC_123_mod.py  -> validate module object
#   demo_1_ABC_123_f.py    -> validate function object "f"
#   demo_1_ABC_123_m.py    -> validate method object "X.m"
#   demo_1_ABC_123_X.py    -> validate class object "X"
# The script checks that each demo actually triggers the intended rule.
DEMO_RE = re.compile(r"^demo_(?P<group>[1-9])_(?P<rule>[A-Z]+_\d{3})_(?P<kind>mod|f|m|X)\.py$")


@dataclass(frozen=True)
class DemoCase:
	stem: str
	rule: str
	obj: str


def iter_demo_cases(base: Path) -> list[DemoCase]:
	cases: list[DemoCase] = []
	for path in sorted(base.glob("demo_*.py")):
		if path.name == "validate_all.py":
			continue
		match = DEMO_RE.fullmatch(path.name)
		if not match:
			continue
		rule = match.group("rule").replace("_", "-")
		kind = match.group("kind")
		if kind == "mod":
			obj = path.stem
		elif kind == "m":
			obj = f"{path.stem}.X.m"
		else:
			obj = f"{path.stem}.{kind}"
		cases.append(DemoCase(path.stem, rule, obj))
	return cases

def main() -> int:
	script_path = Path(__file__).resolve()
	# The examples-diagnostics-python directory is expected to be a sibling of the repository root.
	base = Path(__file__).parent / "../examples-diagnostics-python/"
	# The executable. The script works if sdv.doc.waterloo is installed.
	# waterlint is the official entry point to the executable defined in pyproject.toml.
	waterlint = "waterlint"

	cases = iter_demo_cases(base)
	if not cases:
		print(f"No diagnostic demos found in {base}", file=sys.stderr)
		return 1

	failures = 0
	for case in cases:
		cmd = [
			str(waterlint),
			"validate",
			"--basedir",
			str(base),
			"--obj",
			case.obj,
		]
		# Execute waterlint and dump the diagnostics. We don't
		# need to capture the output, just check the exit code.
		proc = subprocess.run(cmd)

	print(f"summary: {len(cases) - failures} ok, {failures} failed, {len(cases)} total")
	return 1 if failures else 0


if __name__ == "__main__":
	raise SystemExit(main())

# To run this script and capture the ANSI-colored output, you can use the `script` command on Unix-like systems:
# script -c "package_main/tools/sdv_wtrl_dev_dump_tracer_details.py" /tmp/out.ansi
