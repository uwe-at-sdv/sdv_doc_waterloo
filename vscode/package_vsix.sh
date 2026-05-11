#!/bin/bash
set -euo pipefail

MODE="${1:-public}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
VSCE_BIN="npx @vscode/vsce"
PATH_README_TEMPLATE="${ROOT}/README_AZURE.md"
PATH_README_TARGET="${ROOT}/README.md"

#----- begin requirements -------------------------------------#
command -v jq >/dev/null 2>&1 ||		{ echo "jq not available, install with 'sudo apt-get install jq'."; exit 1; }
command -v rsvg-convert >/dev/null 2>&1 ||	{ echo "rsvg-convert not available, install with... ask Gemini."; exit 1; }
#----- end requirements ---------------------------------------#

# package.json is the single source of truth.
VERSION=$(jq ".version" package.json | tr -d '"')
echo ${VERSION} > "VERSION"

# Update (redundant) version file.
echo "VERSION: ${VERSION}"
echo "   MODE: ${MODE}"

echo "#----- Download badges from shields.io ------------------------#"
PATH_VERSION_BADGE_SVG="img/version-badge.svg"
PATH_LOCATION_BADGE_SVG="img/location-badge.svg"
PATH_VERSION_BADGE_PNG="img/version-badge.png"
PATH_LOCATION_BADGE_PNG="img/location-badge.png"
# Download version badge. We will bake this into the vsix in order
# to display them in a robust way instead of relying on network access.
# Marketplace seems to have problems...
# UPDATE: Nope, vsix seems to expect URLS like https:// Need to do some
# research but leave the code for downloading the badges in here.
rm -f img/version-badge.svg img/version-badge.png img/location-badge.svg img/location-badge.png
curl "https://img.shields.io/badge/version-${VERSION}-blue" > "${PATH_VERSION_BADGE_SVG}"
rsvg-convert -z 3 -f png "${PATH_VERSION_BADGE_SVG}" -o "${PATH_VERSION_BADGE_PNG}"
git add "${PATH_VERSION_BADGE_SVG}"
git add "${PATH_VERSION_BADGE_PNG}"

curl "https://img.shields.io/badge/build-local_test-green" > "${PATH_LOCATION_BADGE_SVG}"
rsvg-convert -z 3 -f png "${PATH_LOCATION_BADGE_SVG}" -o "${PATH_LOCATION_BADGE_PNG}"
git add "${PATH_LOCATION_BADGE_SVG}"
git add "${PATH_LOCATION_BADGE_PNG}"
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
if ! ${VSCE_BIN} package; then
    echo "VSIX build failed in ${ROOT}." >&2
    exit 1
fi
echo "#----- Done ---------------------------------------------------#"
