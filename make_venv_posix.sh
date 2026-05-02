#!/bin/bash

# This script creates a python venv and installs packages
# required for creating and compiling waterloo docstrings,
# including pygmentize for syntax highlighting and the waterloo
# sphinx-extension.

# Using this venv you can set up your own Waterloo documentation
# project with output in HTML/Sphinx, HTML/Interactive or JSON.

set -euo pipefail

PYTHON_VERSION=$(python3 --version)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | awk "{print \$2}" | cut -d '.' -f 1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | awk "{print \$2}" | cut -d '.' -f 2)

# Define path to log and initialize as empty.
PATH_TO_LOG="/tmp/make_venv.log"
: > "${PATH_TO_LOG}"

if [ "${USER}" = "uwe" ] && [ -n "${INSIDE_SDV:-}" ]; then
# works now for developer with ssh access
	PROTOCOL="ssh"
else
# will work after release for everyone
	PROTOCOL="https"
fi

DIR_VENV=venv-${PYTHON_MAJOR}.${PYTHON_MINOR}-wtrl

echo "Building python virtual environment in directory ${DIR_VENV}"
echo "In case of problems see log in ${PATH_TO_LOG}"

rm -rf "${DIR_VENV}"
python3 -m venv "${DIR_VENV}"

source "${DIR_VENV}/bin/activate"

echo "upgrading pip"
pip install --upgrade pip >> "${PATH_TO_LOG}" 2>&1

echo "installing sphinx"
pip -q install sphinx >> "${PATH_TO_LOG}" 2>&1

if [ "${PROTOCOL}" == "https" ]; then
	echo "installing python module sdv.doc.waterloo"
	pip -q install "git+https://github.com/uwe-at-sdv/sdv_doc_waterloo.git@main" >> "${PATH_TO_LOG}" 2>&1
	echo "installing waterloo pygments lexer"
	pip -q install "git+https://github.com/uwe-at-sdv/sdv_doc_waterloo.git@ide-plugins#subdirectory=pygments" >> "${PATH_TO_LOG}" 2>&1
elif [ "${PROTOCOL}" == "ssh" ]; then
	echo "installing python module sdv.doc.waterloo"
	pip -q install "git+ssh://git@github.com/uwe-at-sdv/sdv_doc_waterloo.git@main" >> "${PATH_TO_LOG}" 2>&1
	echo "installing waterloo pygments lexer"
	pip -q install "git+ssh://git@github.com/uwe-at-sdv/sdv_doc_waterloo.git@ide-plugins#subdirectory=pygments" >> "${PATH_TO_LOG}" 2>&1
fi

echo "----------------------------------------------------------------"
echo "When using bash, activate with source ${DIR_VENV}/bin/activate"
echo "For other shells please consult venv documentation"
echo "waterlint version $(waterlint version) now installed."
