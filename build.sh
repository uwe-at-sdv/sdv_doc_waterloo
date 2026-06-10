#!/bin/bash

#----- Reproduce this section in each build-script ------------#
set -euo pipefail
ROOT=/server/devel/sdv/privat/uwe/source/sdv_doc_waterloo
PKG_DIR="$ROOT/package"
QUALIFIED_MODULE="sdv.doc.waterloo"
SOURCE_MODULE="sdv_doc_docitem_sphinx"
WHEEL_PREFIX="sdv_doc_waterloo"
GIT_PREFIX="sdv_doc_waterloo"
source _bashrc_colors
#--------------------------------------------------------------#

#----- Parse command line -------------------------------------#
do_push=false
do_mypy=true
do_build=true
be_verbose=false
usage() {
	cat <<EOF
Usage:	$0 [options]

Options:
	-h|--help	Show this help text
	-p|--push	Commit and push after building
	-v|--verbose	Print stuff like e.g. gitignore.
	--skip-mypy	Skip static type testing with mypy.
	--skip-build	Skip building wheel.
EOF
}

while [[ $# -gt 0 ]]; do
	case "$1" in
		-h|--help)
			usage; exit 0 ;;
		-p|--push)
			do_push=true; shift ;;
		-v|--verbose)
			be_verbose=true; shift ;;
		--skip-mypy)
			do_mypy=false; shift ;;
		--skip-build)
			do_build=false; shift ;;
		--)
			shift; break ;;
		*)
			echo -e "${err:-}Unknown option: $1${reset:-}" >&2
			usage >&2; exit 1 ;;
	esac
done
#--------------------------------------------------------------#

#----- Update and gather --------------------------------------#
# Go to script directory and gather files
cd "$PKG_DIR"
log_note "update git-repo from github"
git pull

cd "$ROOT"
./gather.sh
#--------------------------------------------------------------#

#----- Validator section --------------------------------------#
if [[ "$do_mypy" == true ]]; then
# We are one below the root directory.
	cd "$ROOT"
	log_note "Running mypy..."
	mypy sdv*.py
	log_note "...done."
else
	log_warning "Skipping mypy as requested."
fi
#--------------------------------------------------------------#

#----- Build --------------------------------------------------#
cd "$PKG_DIR"

if [[ "$do_build" == true ]]; then
# Make sure our repo is up to date!
	rm -rf build dist
	rm -rf "${WHEEL_PREFIX}".egg-info

	log_note "build wheel"
	python3 -m build --wheel #> /tmp/log_"${WHEEL_PREFIX}"
	status=$?
	if [ "${status}" != "0" ]; then
		cat /tmp/log_"${WHEEL_PREFIX}"
		log_error "An error has occurred while building the wheel."
		exit 1
	fi
else
	log_warning "Skipping build as requested."
fi
#--------------------------------------------------------------#

#----- Info section -------------------------------------------#
# Extract version number from original module.
# It is important to change the directory, otherwise the interpreter
# tries to find required modules in our package subtree.
ver=$(cd ..;python3 -c "import sys;sys.path.insert(0,'.');import ${SOURCE_MODULE} as m;print(m.__version__)")
WHEEL="${WHEEL_PREFIX}-${ver}-py3-none-any.whl"
log_note "Version is ${ver}."

if [[ "$be_verbose" == true ]]; then
	log_note "git currently ignoring:"
	cat .gitignore
fi
log_note "git status:"
git status
log_note "push to github with:"
log_note "git commit -am 'bugfix'"
log_note "git push"

log_note "dist now contains:"
ls -l dist | grep -v "^total"

log_note "install with:"
log_note "pip3 install --force-reinstall --no-deps --no-index --find-links=dist dist/${WHEEL_PREFIX}-${ver}-py3-none-any.whl"
if [ ! -f "dist/${WHEEL_PREFIX}-${ver}-py3-none-any.whl" ]; then
	log_error "expected wheel not present"
fi
log_note "pip3 install --force-reinstall git+ssh://git@github.com:22/uwe-at-sdv/${GIT_PREFIX}.git"
#--------------------------------------------------------------#

#----- Commit and push to github ------------------------------#
if [[ "$do_push" == true ]]; then
# prompt for single line comment for 'commit'
	echo -e "${prmpt} You have requested a push to github."
	echo -e "${prmpt} Enter single-line comment for commit:"
	read -p "[Packaging/Bugfix]: " comment
	comment=${comment:-"Packaging/Bugfix"}
	echo -e "${note} Commit message: ${comment}"
# Anything to commit at all?
	if [[ -z "$(git status --porcelain)" ]]; then
		echo -e "${note} Nothing to commit, working tree clean."
	else
		git commit -am "$comment"
	fi
# Chatbot's push deluxe.
	current_branch="$(git rev-parse --abbrev-ref HEAD)"
	echo -e "${note} Pushing to origin/${current_branch} ..."
	git push origin "$current_branch"
fi
#--------------------------------------------------------------#
