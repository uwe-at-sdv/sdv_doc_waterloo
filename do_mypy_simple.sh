#!/usr/bin/bash

# Highly simplified version of do_mypy.sh in order to bridge
# problems occured during refactoring git-branch 'main'.
# The script is invoked by `make html` for building the Sphinx
# document, see doc/Makefile.

# Would like to see
#set -euo pipefail

# We presuppose that the script is located on repository level.
SCRIPT_DIR=$(realpath $(dirname $0))
PATH_MYPY_INI="${SCRIPT_DIR}/mypy.ini"
PATH_SRC_DIR="${SCRIPT_DIR}/src/sdv/doc/waterloo"
PATH_CHK_OUT="${SCRIPT_DIR}/doc/source/type_checking_report.txt"
PATH_EXC_OUT="${SCRIPT_DIR}/doc/source/type_checking_exceptions.txt"
PATH_FILES_OUT="${SCRIPT_DIR}/doc/source/type_checking_files.txt"

export MYPYPATH="${SCRIPT_DIR}/src"

echo > ${PATH_CHK_OUT}

mypy --config-file "${PATH_MYPY_INI}" \
	--namespace-packages \
	--explicit-package-bases \
	--no-site-packages \
	"${PATH_SRC_DIR}" \
	> "${PATH_CHK_OUT}"
rc=$?
if [[ $rc != 0 ]]; then
# Show problems
	cat "${PATH_CHK_OUT}"
	exit $rc
fi

grep -nE '#[[:space:]]*(type: ignore(\[[^]]+\])?|pragma: no cover.*)$' "${PATH_SRC_DIR}"/*.py \
| awk -F: 'match($0, /#[[:space:]]*(type: ignore(\[[^]]+\])?|pragma: no cover.*)$/, m) { n = split($1, p, "/"); printf "%s:%s %s\n", p[n], $2, m[0] }' \
> "${PATH_EXC_OUT}"

pushd ${SCRIPT_DIR}/src > /dev/null
find sdv/doc/waterloo/ -name "*.py" > ${PATH_FILES_OUT}
popd > /dev/null
