#!/usr/bin/bash

set -euo pipefail

SCRIPT_DIR=$(realpath $(dirname $0))
PATH_MYPY_INI=$(realpath $(dirname $0)/mypy.ini)
PATH_SRC_DIR=$(realpath $(dirname $0)/src/sdv/doc/waterloo)
PATH_CHK_OUT=$(realpath $(dirname $0)/doc/source/_static/type_checking_report.txt)
PATH_EXC_OUT=$(realpath $(dirname $0)/doc/source/_static/type_checking_exceptions.txt)

MYPYPATH="${SCRIPT_DIR}/src" mypy --config-file "${PATH_MYPY_INI}" \
	--namespace-packages \
	--explicit-package-bases \
	"${PATH_SRC_DIR}" \
	> "${PATH_CHK_OUT}"

grep -nE '#[[:space:]]*(type: ignore(\[[^]]+\])?|pragma: no cover.*)$' "${PATH_SRC_DIR}"/*.py \
| awk -F: 'match($0, /#[[:space:]]*(type: ignore(\[[^]]+\])?|pragma: no cover.*)$/, m) { n = split($1, p, "/"); printf "%s:%s %s\n", p[n], $2, m[0] }' \
> "${PATH_EXC_OUT}"
