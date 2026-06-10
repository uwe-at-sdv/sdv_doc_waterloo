#!/bin/bash

set -euo pipefail
ROOT="/server/devel/sdv/privat/uwe/source/sdv_doc_waterloo"
echo "ROOT: $ROOT"
PKG_MAIN_DIR="$ROOT/package_main"
PKG_DOC_DIR="$ROOT/package_gh-pages"
PKG_IDE_DIR="$ROOT/package_ide-plugins"
PKG_DOC_JSON_DIR="$PKG_MAIN_DIR/src/sdv/doc/waterloo/doc-json"
SRC_DIR="$PKG_MAIN_DIR/src"
TRGDIR="$SRC_DIR/sdv/doc/waterloo"

rm -rf   "${SRC_DIR}"
mkdir -p "${TRGDIR}"

# Sphinx styles
mkdir -p "${TRGDIR}"/_static

# Copy gather.sh and build.sh to git-controlled area
cp "$ROOT/gather.sh"	"$PKG_MAIN_DIR/"

# Mypy stuff
cp -a "$ROOT"/mypy.ini	"${PKG_MAIN_DIR}"
touch			"${TRGDIR}/py.typed"

#===== Branch main ============================================#
# docs at package root
if [ -f "$ROOT"/ARCHITECTURE.md ]; then cp -a "$ROOT"/ARCHITECTURE.md "$PKG_MAIN_DIR/"; fi
if [ -f "$ROOT"/TESTS.md ]; then cp -a "$ROOT"/TESTS.md "$PKG_MAIN_DIR/"; fi

# Core modules
cd $ROOT
cp -a sdv_doc_docitem.py					"${TRGDIR}/docitem.py"
cp -a sdv_doc_docitem_base.py					"${TRGDIR}/docitem_base.py"
cp -a sdv_doc_docitem_contract.py				"${TRGDIR}/docitem_contract.py"
cp -a sdv_doc_docitem_convert.py				"${TRGDIR}/docitem_convert.py"
cp -a sdv_doc_docitem_docstring.py				"${TRGDIR}/docitem_docstring.py"
cp -a sdv_doc_docitem_genutil.py				"${TRGDIR}/docitem_genutil.py"
cp -a sdv_doc_docitem_helper.py					"${TRGDIR}/docitem_helper.py"
cp -a sdv_doc_docitem_preamble.py				"${TRGDIR}/docitem_preamble.py"
cp -a sdv_doc_docitem_sections.py				"${TRGDIR}/docitem_sections.py"
cp -a sdv_doc_docitem_sphinx.py					"${TRGDIR}/docitem_sphinx.py"
cp -a sdv_doc_docitem_tokenizer.py				"${TRGDIR}/docitem_tokenizer.py"
cp -a sdv_doc_docitem_validator.py				"${TRGDIR}/docitem_validator.py"
cp -a waterlint_render_html5.py					"${TRGDIR}/waterlint_render_html5.py"
cp -a waterlint.py						"${TRGDIR}/waterlint.py"
cp -a doc/source/_static/alabaster_waterloo.css			"${TRGDIR}/_static/alabaster_waterloo.css"
cp -a doc/source/_static/common_styles.css			"${TRGDIR}/_static/common_styles.css"

# Put __init__.py where it belongs.
rm -f "$SRC_DIR/sdv/__init__.py"
rm -f "$SRC_DIR/sdv/doc/__init__.py"
rm -f "$SRC_DIR/sdv/doc/waterloo/__init__.py"

cp -a "$ROOT"/main/README.md		"${PKG_MAIN_DIR}/"

# Version
cp -a "$ROOT"/main/VERSION		"${PKG_MAIN_DIR}/"
cp -a "$ROOT"/main/CHANGELOG		"${PKG_MAIN_DIR}/"
cp -a "$ROOT"/main/docs			"${PKG_MAIN_DIR}/"

# Logo for github. README.md expects it there.
cp -a "$ROOT"/img/wtrl_logo.svg		main/docs/

# Documentation for LLMs
rm -rf					"${PKG_DOC_JSON_DIR}"
mkdir -p				"${PKG_DOC_JSON_DIR}"
cp -a doc-json/*.json			"${PKG_DOC_JSON_DIR}/"

# Schemata are needed at runtime and must be part
# of the distribution (sdv_doc_waterloo-#.#.#.tar.gz)
rm -rf					"${TRGDIR}/schema"
cp -a "$ROOT/schema" 			"${TRGDIR}/schema"

# Additional JavaScript code. These are data in the sense
# that they are read by waterlint for subcommand render-html5,
# so they must be part of the installation of sdv.doc.waterloo.
rm -rf					"${TRGDIR}/js"
cp -a "$ROOT/js" 			"${TRGDIR}/js"

# JSON-examples
rm -rf					"${PKG_MAIN_DIR}/examples-json"
cp -a "$ROOT/examples-json" 		"${PKG_MAIN_DIR}/examples-json"

# Stylesheets for render-html5
rm -rf					"${TRGDIR}/css"
cp -a "$ROOT/css" 			"${TRGDIR}/css"

# Pytests
#cp -a pytest_*.py			"${PKG_MAIN_DIR}/pytest/"

# Logo
rm -rf					"${PKG_MAIN_DIR}/img"
mkdir -p				"${PKG_MAIN_DIR}/img"
cp -a "$ROOT"/img/wtrl_logo*.png 	"${PKG_MAIN_DIR}/img"


#===== Branch ide-plugins =====================================#
cp -a ide-plugins/pygments					"${PKG_IDE_DIR}/"
cp -a ide-plugins/vscode					"${PKG_IDE_DIR}/"
# These are version cnd changelog for the ide-plugins-branch as a whole.
# pygments and vscode extension have their own version and changelog.
cp -a ide-plugins/VERSION					"${PKG_IDE_DIR}/"
cp -a ide-plugins/CHANGELOG					"${PKG_IDE_DIR}/"
# Logo
cp -a img/wtrl_logo_128x128.png					"${PKG_IDE_DIR}/vscode/img/"

python3 ide-plugins/pygments/python_waterloo_lexer.py >		"${PKG_IDE_DIR}/pygments/VERSION"

#===== Branch gh-pages ========================================#
# Documentation
rm -rf				"${PKG_DOC_DIR}/*"
cp -a doc/build/html/*		"${PKG_DOC_DIR}/"
