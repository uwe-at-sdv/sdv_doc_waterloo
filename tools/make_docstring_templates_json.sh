#!/bin/bash

set -euo pipefail

DIR_SCRIPT=$(realpath "$(dirname "$0")")
PATH_PKG_MAIN=$(realpath "${DIR_SCRIPT}/..")
PATH_TEMPLATES_JSON="${PATH_PKG_MAIN}/templates-json"
PATH_IN_PYTHON="${PATH_TEMPLATES_JSON}/in_python"
PATH_OUT_PYTHON="${PATH_TEMPLATES_JSON}/out_python"

TMP_DIR=$(mktemp -d)
trap 'rm -rf "${TMP_DIR}"' EXIT

mkdir -p "${PATH_OUT_PYTHON}"

generate_docstring() {
	local mode="$1"
	local obj="$2"
	local out="$3"

	waterlint "gen-${mode}" \
		--out-diag /dev/null \
		--basedir "${PATH_IN_PYTHON}" \
		--obj "${obj}" \
		--out "${out}"
}

render_python_module() {
	local out="$1"
	local doc_module="$2"
	local doc_x="$3"
	local doc_x_m="$4"
	local doc_f="$5"

	python3 - "${PATH_IN_PYTHON}/module.py" "${out}" "${doc_module}" "${doc_x}" "${doc_x_m}" "${doc_f}" <<'PY'
from pathlib import Path
import sys

path_template = Path(sys.argv[1])
path_out = Path(sys.argv[2])
path_docs = {
	"DOC_MODULE": Path(sys.argv[3]),
	"DOC_X": Path(sys.argv[4]),
	"DOC_X_M": Path(sys.argv[5]),
	"DOC_F": Path(sys.argv[6]),
}


def indent_docstring(text: str, indent: str) -> str:
	return "\n".join(indent + line if line else indent for line in text.rstrip("\n").splitlines())


source = path_template.read_text(encoding="utf-8")
for placeholder, path_doc in path_docs.items():
	token = f'"""{placeholder}"""'
	pos = source.find(token)
	if pos < 0:
		raise RuntimeError(f"missing placeholder {placeholder} in {path_template}")
	line_start = source.rfind("\n", 0, pos) + 1
	indent = source[line_start:pos]
	source = source.replace(indent + token, indent_docstring(path_doc.read_text(encoding="utf-8"), indent), 1)

path_out.write_text(source, encoding="utf-8")
PY
}

generate_docstring minimal module   "${TMP_DIR}/minimal.DOC_MODULE.py"
generate_docstring minimal module.X "${TMP_DIR}/minimal.DOC_X.py"
generate_docstring minimal module.f "${TMP_DIR}/minimal.DOC_F.py"
generate_docstring minimal module.X.m "${TMP_DIR}/minimal.DOC_X_M.py"

generate_docstring full module   "${TMP_DIR}/full.DOC_MODULE.py"
generate_docstring full module.X "${TMP_DIR}/full.DOC_X.py"
generate_docstring full module.f "${TMP_DIR}/full.DOC_F.py"
generate_docstring full module.X.m "${TMP_DIR}/full.DOC_X_M.py"

render_python_module \
	"${PATH_OUT_PYTHON}/minimal_docstring_templates.py" \
	"${TMP_DIR}/minimal.DOC_MODULE.py" \
	"${TMP_DIR}/minimal.DOC_X.py" \
	"${TMP_DIR}/minimal.DOC_X_M.py" \
	"${TMP_DIR}/minimal.DOC_F.py"

render_python_module \
	"${PATH_OUT_PYTHON}/full_docstring_templates.py" \
	"${TMP_DIR}/full.DOC_MODULE.py" \
	"${TMP_DIR}/full.DOC_X.py" \
	"${TMP_DIR}/full.DOC_X_M.py" \
	"${TMP_DIR}/full.DOC_F.py"

waterlint validate --basedir "${PATH_OUT_PYTHON}" --obj minimal_docstring_templates
waterlint validate --basedir "${PATH_OUT_PYTHON}" --obj minimal_docstring_templates.X
waterlint validate --basedir "${PATH_OUT_PYTHON}" --obj minimal_docstring_templates.f
waterlint validate --basedir "${PATH_OUT_PYTHON}" --obj minimal_docstring_templates.X.m

waterlint validate --basedir "${PATH_OUT_PYTHON}" --obj full_docstring_templates
waterlint validate --basedir "${PATH_OUT_PYTHON}" --obj full_docstring_templates.X
waterlint validate --basedir "${PATH_OUT_PYTHON}" --obj full_docstring_templates.f
waterlint validate --basedir "${PATH_OUT_PYTHON}" --obj full_docstring_templates.X.m

waterlint render-json --basedir "${PATH_OUT_PYTHON}" --obj minimal_docstring_templates --out-dir "${PATH_TEMPLATES_JSON}/in" --out-diag /dev/null --out-diag-json "${PATH_TEMPLATES_JSON}/wtrl.minimal.log"
waterlint render-json --basedir "${PATH_OUT_PYTHON}" --obj full_docstring_templates    --out-dir "${PATH_TEMPLATES_JSON}/in" --out-diag /dev/null --out-diag-json "${PATH_TEMPLATES_JSON}/wtrl.full.log"

echo "Python stubs written to"
echo "* ${PATH_OUT_PYTHON}"
echo "JSON walk inputs written to"
echo "* ${PATH_TEMPLATES_JSON}/in"
echo "Waterlint logs written to"
echo "* ${PATH_TEMPLATES_JSON}/wtrl.minimal.log"
echo "* ${PATH_TEMPLATES_JSON}/wtrl.full.log"

jq '{__WTRL_OBJECTS__: {"minimal_docstring_templates":     .__WTRL_OBJECTS__."minimal_docstring_templates"}}'     "${PATH_TEMPLATES_JSON}/in/minimal_docstring_templates.wtrl.core.rfc-2119.json" > "${PATH_TEMPLATES_JSON}/out/minimal_docstring_templates.json"
jq '{__WTRL_OBJECTS__: {"minimal_docstring_templates.X":   .__WTRL_OBJECTS__."minimal_docstring_templates.X"}}'   "${PATH_TEMPLATES_JSON}/in/minimal_docstring_templates.wtrl.core.rfc-2119.json" > "${PATH_TEMPLATES_JSON}/out/minimal_docstring_templates.X.json"
jq '{__WTRL_OBJECTS__: {"minimal_docstring_templates.f":   .__WTRL_OBJECTS__."minimal_docstring_templates.f"}}'   "${PATH_TEMPLATES_JSON}/in/minimal_docstring_templates.wtrl.core.rfc-2119.json" > "${PATH_TEMPLATES_JSON}/out/minimal_docstring_templates.f.json"
jq '{__WTRL_OBJECTS__: {"minimal_docstring_templates.X.m": .__WTRL_OBJECTS__."minimal_docstring_templates.X.m"}}' "${PATH_TEMPLATES_JSON}/in/minimal_docstring_templates.wtrl.core.rfc-2119.json" > "${PATH_TEMPLATES_JSON}/out/minimal_docstring_templates.X.m.json"

jq '{__WTRL_OBJECTS__: {"full_docstring_templates":        .__WTRL_OBJECTS__."full_docstring_templates"}}'        "${PATH_TEMPLATES_JSON}/in/full_docstring_templates.wtrl.core.rfc-2119.json" > "${PATH_TEMPLATES_JSON}/out/full_docstring_templates.json"
jq '{__WTRL_OBJECTS__: {"full_docstring_templates.X":      .__WTRL_OBJECTS__."full_docstring_templates.X"}}'      "${PATH_TEMPLATES_JSON}/in/full_docstring_templates.wtrl.core.rfc-2119.json" > "${PATH_TEMPLATES_JSON}/out/full_docstring_templates.X.json"
jq '{__WTRL_OBJECTS__: {"full_docstring_templates.f":      .__WTRL_OBJECTS__."full_docstring_templates.f"}}'      "${PATH_TEMPLATES_JSON}/in/full_docstring_templates.wtrl.core.rfc-2119.json" > "${PATH_TEMPLATES_JSON}/out/full_docstring_templates.f.json"
jq '{__WTRL_OBJECTS__: {"full_docstring_templates.X.m":    .__WTRL_OBJECTS__."full_docstring_templates.X.m"}}'    "${PATH_TEMPLATES_JSON}/in/full_docstring_templates.wtrl.core.rfc-2119.json" > "${PATH_TEMPLATES_JSON}/out/full_docstring_templates.X.m.json"

echo "Output written to"
echo "* ${PATH_TEMPLATES_JSON}/out"
