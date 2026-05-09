#!/bin/bash
set -euo pipefail

MODE="${1:-public}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
VSCE_BIN="npx @vscode/vsce"
TEMPLATE="${ROOT}/README_AZURE.md"
TARGET="${ROOT}/README.md"
VERSION=$(jq ".version" package.json | tr -d '"')

echo ${VERSION} > "VERSION"

# Update (redundant) version file.
echo "VERSION: ${VERSION}"

PATH_VERSION_BADGE_SVG="img/version-${VERSION}-blue.svg"
# Download version badge. We will bake this into the vsix in order
# to display them in a robust wat instead of relying on network access.
# Marketplace seems to have problems...
echo "#----- Download badges from shields.io ------------------------#"
rm img/version-*.*.*-*.svg
curl "https://img.shields.io/badge/version-${VERSION}-blue" > "${PATH_VERSION_BADGE_SVG}"
git add "${PATH_VERSION_BADGE_SVG}"
echo "#----- Done ---------------------------------------------------#"

# Select badge file for local or public presentation.
case "${MODE}" in
    local)
        BADGES="${ROOT}/README_BADGES_LOCAL.md"
        ;;
    public)
        BADGES="${ROOT}/README_BADGES_PUBLIC.md"
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
        mv -f "${backup}" "${TARGET}"
    elif [[ "${saw_target}" -eq 0 ]]; then
        rm -f "${TARGET}"
    fi
    rm -f "${backup}"
}

# Do not cleanup, since we need to verify README.md
#trap cleanup EXIT

if [[ -f "${TARGET}" ]]; then
    saw_target=1
    cp -f "${TARGET}" "${backup}"
    backup_ok=1
else
    : > "${backup}"
fi

echo "#----- Building README.md from template -----------------------#"
python3 - "${TEMPLATE}" "${BADGES}" "${TARGET}" "${VERSION}" <<'PY'
from pathlib import Path
import sys

template = Path(sys.argv[1]).read_text(encoding="utf-8")
badges = Path(sys.argv[2]).read_text(encoding="utf-8").rstrip("\n")
target = Path(sys.argv[3])
version = sys.argv[4]
target.write_text(template.replace("_BADGES_", badges, 1).replace("_VERSION_",version), encoding="utf-8")
PY
echo "README.md: $(wc -c < "${TARGET}") bytes"
echo "#----- Done ---------------------------------------------------#"

rm -f "${ROOT}"/waterloo-docstrings-*.vsix

#if [[ -x "${ROOT}/node_modules/.bin/vsce" ]]; then
#    VSCE_BIN="${ROOT}/node_modules/.bin/vsce"
#elif command -v vsce >/dev/null 2>&1; then
#    VSCE_BIN="$(command -v vsce)"
#else
#    echo "VSCE build tool not found. Install @vscode/vsce locally or put 'vsce' on PATH." >&2
#    exit 1
#fi

echo "#----- Building VSIX package ----------------------------------#"
if ! ${VSCE_BIN} package; then
    echo "VSIX build failed in ${ROOT}." >&2
    exit 1
fi
echo "#----- Done ---------------------------------------------------#"
