from docutils import nodes
from docutils.parsers.rst import roles
from docutils.parsers.rst import languages
from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.parsers.rst.states import Struct
from typing import Any, Callable, Dict, Generator, Iterable, Iterator, List, Tuple, Type, TypeAlias, TypeGuard, Union

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from pathlib import Path

CONF_DIR = Path(__file__).resolve().parent
ROOT_DIR = CONF_DIR.parents[1]

sys.path.insert(0, str((ROOT_DIR / "src").resolve()))
sys.path.insert(0, str((ROOT_DIR / "doc" / "examples").resolve()))
sys.path.insert(0, str((ROOT_DIR.parents[0] / "package_ide-plugins" / "pygments").resolve()))

# -- Syntax Highlighting -----------------------------------------------------
from python_waterloo_lexer import PythonWaterlooLexer


# -- Project information -----------------------------------------------------

project = 'Waterloo Docstrings'
copyright = '2026, Uwe'
author = 'Uwe'

# The full version, including alpha/beta/rc tags
release = '0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
	"sphinx_sitemap",
	"sdv.doc.waterloo.docitem_sphinx",
	]

# For sitemap:
html_baseurl = 'https://uwe-at-sdv.github.io/sdv_doc_waterloo/'
sitemap_url_scheme = "{link}"
html_extra_path = ['google4eaebafa61e09da2.html']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# Waterloo documentation is currently English-only; disable gettext/i18n
# lookup so Sphinx does not search for locale catalogs.
language = "en"
locale_dirs = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

html_theme_options = {
# Filename rel _static/
    'logo': 'wtrl_logo_color_64x64.png',
# Display project name below logo
    'logo_name': 'false',
# Optional: center align the logo/text
    'logo_text_align': 'left',
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Keep Sphinx-level fallback values as well.
pygments_style = "gruvbox-light"
pygments_dark_style = "gruvbox-dark"

def build_prolog_method_overview(ctx) -> List[nodes.Node]:
	return [nodes.rubric(text="Public methods")]

def build_prolog_method_block(ctx,parent : nodes.Node,class_obj,meth_obj : Callable) -> List[nodes.Node]:
	return ctx.parse(parent,0,f":wtrl_method_signature:`{class_obj.__name__}.{meth_obj.__name__}`")

WTRL_PROLOG_WATERLOO = """
.. |LoII| replace:: :ref:`LoII <principles>`
.. |LoIO| replace:: :ref:`LoIO <principles>`
.. |SSoT| replace:: :ref:`SSoT <principles>`
.. |BinNorm| replace:: :ref:`BinNorm <principles>`
.. |SoSaC| replace:: :ref:`SoSaC <principles>`
.. |SCaA| replace:: :ref:`SCaA <principles>`
.. |DrPrv| replace:: :ref:`DrPrv <principles>`
.. |MVAuth| replace:: :ref:`MVAuth <principles>`
"""

_SENTINEL = "\n.. wtrl-prolog-waterloo:begin\n"

def _inject_wtrl_prolog_waterloo(app: Any, config :Any) -> None:
	current = getattr(config, "rst_prolog", "") or ""
	if not "wtrl-prolog-waterloo:begin" in current:
		config.rst_prolog = current + _SENTINEL + WTRL_PROLOG_WATERLOO + "\n.. wtrl-prolog-waterloo:end\n"
	# Force style after theme defaults were loaded (important for alabaster on older Sphinx).
	config.pygments_style = "gruvbox-light"
	if hasattr(config, "pygments_dark_style"):
		config.pygments_dark_style = "gruvbox-dark"

def setup(app: Any) -> dict[str, Any]:
	app.connect("config-inited", _inject_wtrl_prolog_waterloo)
	app.add_lexer('python', PythonWaterlooLexer)
	app.add_lexer('python-waterloo', PythonWaterlooLexer)
