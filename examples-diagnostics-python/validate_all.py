#!/usr/bin/env python3

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


# Demo naming convention:
#   demo_ABC_123_mod.py  -> validate module object
#   demo_ABC_123_f.py    -> validate function object "f"
#   demo_ABC_123_m.py    -> validate method object "X.m"
#   demo_ABC_123_X.py    -> validate class object "X"
# The script checks that each demo actually triggers the intended rule.
DEMO_RE = re.compile(r"^demo_(?P<rule>[A-Z]+_\d{3})_(?P<kind>mod|f|m|X)\.py$")


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
	base = script_path.parent
	repo_root = script_path.parents[2]
	waterlint = repo_root / "venv-3.14-wtrl" / "bin" / "waterlint"

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
		proc = subprocess.run(cmd, capture_output=True, text=True)
		output = (proc.stdout or "") + (proc.stderr or "")
		ok = proc.returncode != 0 and f"[Rule {case.rule}]" in output and "DOC-001" not in output
		status = "OK" if ok else "FAIL"
		print(f"{status} {case.stem} -> {case.obj} (rule {case.rule})")
		if not ok:
			failures += 1
			if output.strip():
				print(output.rstrip())
		elif "found:" in output:
			# Keep the tracer body visible for successful matches.
			for line in output.rstrip().splitlines():
				if "[Rule " in line or "\tfound:" in line or "\texpected:" in line or "\thint:" in line:
					print(line)

	print(f"summary: {len(cases) - failures} ok, {failures} failed, {len(cases)} total")
	return 1 if failures else 0


if __name__ == "__main__":
	raise SystemExit(main())
