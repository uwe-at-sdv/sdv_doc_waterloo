#!/usr/bin/bash

# Highly simplified version of do_mypy.sh in order to bridge
# problems occured during refactoring git-branch 'main'.
# The script is invoked by `make html` for building the Sphinx
# document, see doc/Makefile.

set -euo pipefail

# We presuppose that the script is located on repository level.
SCRIPT_DIR=$(realpath $(dirname $0))
PATH_MYPY_INI="${SCRIPT_DIR}/mypy.ini"
PATH_SRC_DIR="${SCRIPT_DIR}/src/sdv/doc/waterloo"
PATH_CHK_OUT="${SCRIPT_DIR}/doc/source/type_checking_report.txt"
PATH_EXC_OUT="${SCRIPT_DIR}/doc/source/type_checking_exceptions.txt"

MYPYPATH="${SCRIPT_DIR}/src" mypy --config-file "${PATH_MYPY_INI}" \
	--namespace-packages \
	--explicit-package-bases \
	"${PATH_SRC_DIR}" \
	> "${PATH_CHK_OUT}"

grep -nE '#[[:space:]]*(type: ignore(\[[^]]+\])?|pragma: no cover.*)$' "${PATH_SRC_DIR}"/*.py \
| awk -F: 'match($0, /#[[:space:]]*(type: ignore(\[[^]]+\])?|pragma: no cover.*)$/, m) { n = split($1, p, "/"); printf "%s:%s %s\n", p[n], $2, m[0] }' \
> "${PATH_EXC_OUT}"
