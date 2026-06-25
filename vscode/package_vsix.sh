#!/bin/bash
set -euo pipefail

MODE="${1:-public}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
PATH_README_TEMPLATE="${ROOT}/templates/README_AZURE.template.md"
PATH_README_TARGET="${ROOT}/README.md"

#----- begin requirements -------------------------------------#
command -v jq >/dev/null 2>&1 || { echo "jq not available, install with 'sudo apt-get install jq'."; exit 1; }
#----- end requirements ---------------------------------------#

#----- begin ensure vsce --------------------------------------#
echo "${ROOT}/node_modules/.bin/vsce"
if [[ -x "${ROOT}/node_modules/.bin/vsce" ]]; then
    VSCE_BIN="${ROOT}/node_modules/.bin/vsce"
elif command -v vsce >/dev/null 2>&1; then
    VSCE_BIN="$(command -v vsce)"
else
    echo "VSCE build tool not found. Install @vscode/vsce locally or put 'vsce' on PATH." >&2
    exit 1
fi
#----- end ensure vsce ----------------------------------------#

cd "${ROOT}"

# package.json is the single source of truth.
VERSION=$(jq ".version" package.json | tr -d '"')
printf '%s\n' "${VERSION}" > "VERSION"

# Update (redundant) version file.
echo "VERSION: ${VERSION}"
echo "   MODE: ${MODE}"

# Select badge file for local or public presentation.
case "${MODE}" in
    local)
        BADGES="${ROOT}/templates/README_BADGES_LOCAL.template.md"
        ;;
    public)
        BADGES="${ROOT}/templates/README_BADGES_PUBLIC.template.md"
        ;;
    *)
        echo "Usage: $0 [local|public]" >&2
        exit 2
        ;;
esac

backup="$(mktemp)"
saw_target=0
backup_ok=0

cleanup() {
    if [[ "${backup_ok}" -eq 1 ]]; then
        mv -f "${backup}" "${PATH_README_TARGET}"
    elif [[ "${saw_target}" -eq 0 ]]; then
        rm -f "${PATH_README_TARGET}"
    fi
    rm -f "${backup}"
}

# Do not cleanup, since we need to verify README.md
#trap cleanup EXIT

if [[ -f "${PATH_README_TARGET}" ]]; then
    saw_target=1
    cp -f "${PATH_README_TARGET}" "${backup}"
    backup_ok=1
else
    : > "${backup}"
fi

echo "#----- Building README.md from template -----------------------#"
echo "Using badge file '$BADGES'."
python3 - "${PATH_README_TEMPLATE}" "${BADGES}" "${PATH_README_TARGET}" "${VERSION}" <<'PY'
from pathlib import Path
import sys

template = Path(sys.argv[1]).read_text(encoding="utf-8")
badges = Path(sys.argv[2]).read_text(encoding="utf-8").rstrip("\n")
target = Path(sys.argv[3])
version = sys.argv[4]
target.write_text(template.replace("_BADGES_", badges, 1).replace("_VERSION_",version), encoding="utf-8")
PY
echo "README.md: $(wc -c < "${PATH_README_TARGET}") bytes"
echo "#----- Done ---------------------------------------------------#"

rm -f "${ROOT}"/waterloo-docstrings-*.vsix

echo "#----- Building VSIX package ----------------------------------#"
if ! "${VSCE_BIN}" package; then
    echo "VSIX build failed in ${ROOT}." >&2
    exit 1
fi

echo "#----- Done ---------------------------------------------------#"
