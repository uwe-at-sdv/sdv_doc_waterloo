#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_SRC_DIR="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
DOC_JSON_DIR="${SCRIPT_DIR}/doc-json"
DOC_JSON_OUT="${DOC_JSON_DIR}/wtrl-mcp.wtrl.core.rfc-2119.json"

mkdir -p "${DOC_JSON_DIR}"

# Render the MCP package docs from the package-local module roots.
# The resolver now prefers the local `wtrl_tools.py` in this package over any
# unrelated external module with the same bare name.
python3 -m sdv.doc.waterloo.waterlint render-json \
	--basedir "${PKG_SRC_DIR}" \
	--scope extension \
	--flavour rfc-2119 \
	--no-allow-local-paths \
	--obj sdv.doc.waterloo.mcp.wtrl_server \
	--out "${DOC_JSON_OUT}"

# Validate the generated doc-JSON immediately so chat-driven updates can be
# checked without opening the browser inspector.
python3 -m sdv.doc.waterloo.waterlint validate-json \
	--in "${DOC_JSON_OUT}"
