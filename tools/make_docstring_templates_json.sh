#!/bin/bash

set -euo pipefail

DIR_SCRIPT=$(realpath $(dirname $0))
PATH_PKG_MAIN=$(realpath ${DIR_SCRIPT}/..)
PATH_TEMPLATES_JSON="${PATH_PKG_MAIN}/templates-json"

waterlint render-json --basedir "${PATH_TEMPLATES_JSON}/in_python" --obj minimal_docstring_templates --out-dir "${PATH_TEMPLATES_JSON}/in" --out-diag /dev/null --out-diag-json "${PATH_TEMPLATES_JSON}/wtrl.minimal.log"
waterlint render-json --basedir "${PATH_TEMPLATES_JSON}/in_python" --obj full_docstring_templates    --out-dir "${PATH_TEMPLATES_JSON}/in" --out-diag /dev/null --out-diag-json "${PATH_TEMPLATES_JSON}/wtrl.full.log"

echo "Python stubs written to"
echo "* ${PATH_TEMPLATES_JSON}/in"
echo "Waterlint logs written to"
echo "* ${PATH_TEMPLATES_JSON}/wtrl.minimal.log"
echo "* ${PATH_TEMPLATES_JSON}/wtrl.full.log"

jq '{__WTRL_OBJECTS__: {"minimal_docstring_templates":     .__WTRL_OBJECTS__."minimal_docstring_templates"}}'     ${PATH_TEMPLATES_JSON}/in/minimal_docstring_templates.wtrl.core.rfc-2119.json > ${PATH_TEMPLATES_JSON}/out/minimal_docstring_templates.json
jq '{__WTRL_OBJECTS__: {"minimal_docstring_templates.X":   .__WTRL_OBJECTS__."minimal_docstring_templates.X"}}'   ${PATH_TEMPLATES_JSON}/in/minimal_docstring_templates.wtrl.core.rfc-2119.json > ${PATH_TEMPLATES_JSON}/out/minimal_docstring_templates.X.json
jq '{__WTRL_OBJECTS__: {"minimal_docstring_templates.f":   .__WTRL_OBJECTS__."minimal_docstring_templates.f"}}'   ${PATH_TEMPLATES_JSON}/in/minimal_docstring_templates.wtrl.core.rfc-2119.json > ${PATH_TEMPLATES_JSON}/out/minimal_docstring_templates.f.json
jq '{__WTRL_OBJECTS__: {"minimal_docstring_templates.X.m": .__WTRL_OBJECTS__."minimal_docstring_templates.X.m"}}' ${PATH_TEMPLATES_JSON}/in/minimal_docstring_templates.wtrl.core.rfc-2119.json > ${PATH_TEMPLATES_JSON}/out/minimal_docstring_templates.X.m.json

jq '{__WTRL_OBJECTS__: {"full_docstring_templates":        .__WTRL_OBJECTS__."full_docstring_templates"}}'        ${PATH_TEMPLATES_JSON}/in/full_docstring_templates.wtrl.core.rfc-2119.json > ${PATH_TEMPLATES_JSON}/out/full_docstring_templates.json
jq '{__WTRL_OBJECTS__: {"full_docstring_templates.X":      .__WTRL_OBJECTS__."full_docstring_templates.X"}}'      ${PATH_TEMPLATES_JSON}/in/full_docstring_templates.wtrl.core.rfc-2119.json > ${PATH_TEMPLATES_JSON}/out/full_docstring_templates.X.json
jq '{__WTRL_OBJECTS__: {"full_docstring_templates.f":      .__WTRL_OBJECTS__."full_docstring_templates.f"}}'      ${PATH_TEMPLATES_JSON}/in/full_docstring_templates.wtrl.core.rfc-2119.json > ${PATH_TEMPLATES_JSON}/out/full_docstring_templates.f.json
jq '{__WTRL_OBJECTS__: {"full_docstring_templates.X.m":    .__WTRL_OBJECTS__."full_docstring_templates.X.m"}}'    ${PATH_TEMPLATES_JSON}/in/full_docstring_templates.wtrl.core.rfc-2119.json > ${PATH_TEMPLATES_JSON}/out/full_docstring_templates.X.m.json

echo "Output written to"
echo "* ${PATH_TEMPLATES_JSON}/out"
