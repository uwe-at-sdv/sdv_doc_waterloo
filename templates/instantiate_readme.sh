#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "$0")" && pwd)
repo_dir=$(cd "${script_dir}/.." && pwd)
target=${1:-GITHUB}
version=$(
python3 - "${repo_dir}" <<'PY'
from pathlib import Path
import re
import sys

docitem = Path(sys.argv[1]) / "src" / "sdv" / "doc" / "waterloo" / "docitem.py"
match = re.search(r'^__version__\s*=\s*"([^"]+)"', docitem.read_text(), re.M)
if not match:
	raise SystemExit("Could not determine sdv-doc-waterloo version.")
print(match.group(1))
PY
)

case "${target}" in
	GITHUB)
		readme_template="${script_dir}/README_GITHUB.template.md"
		target_badges_template="${script_dir}/README_BADGES_GITHUB.template.md"
		;;
	PYPI)
		readme_template="${script_dir}/README_PYPI.template.md"
		target_badges_template="${script_dir}/README_BADGES_PYPI.template.md"
		;;
	*)
		echo "Usage: $0 [GITHUB|PYPI]" >&2
		exit 2
		;;
esac

badges=$(cat "${target_badges_template}")

python3 - "$readme_template" "$repo_dir/README.md" "$version" "$badges" <<'PY'
from pathlib import Path
import sys

template_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])
version = sys.argv[3]
badges = sys.argv[4]

text = template_path.read_text()
text = text.replace("_VERSION_", version)
text = text.replace("_BADGES_", badges.replace("_VERSION_", version).rstrip("\n"))
out_path.write_text(text)
PY
