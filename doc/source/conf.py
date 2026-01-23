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
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../../package'))
#from sdv.doc.waterloo.docitem import *

sys.path.insert(0, os.path.abspath('../examples'))
#from test_docitem_class_class import X

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
	"sdv.doc.waterloo.docitem_sphinx",
	]

from sdv.doc.waterloo.docitem_sphinx import build_sphinx_nodes_full

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


def build_prolog_public_methods(ctx) -> List[nodes.Node]:
	return [nodes.rubric(text="Public methods")]

def build_prolog_method_block(ctx,parent : nodes.Node,class_obj,meth_obj : Callable) -> List[nodes.Node]:
	return ctx.parse(parent,0,f":wtrl_method_signature:`{class_obj.__name__}.{meth_obj.__name__}`")

# Need this to configure sdv.doc.waterloo.docitem_sphinx.
if 0: docitem_context_config = {
	"role_dfn": "userdef_dfn",
	"role_func": "userdef_func",
	"role_label": "userdef_label",
	"role_method": "userdef_func",
	"role_op": "userdef_op",
	"role_type": "userdef_type",
	"role_value": "userdef_value",
	"role_var": "userdef_var",
	"prolog_public_methods": "build_prolog_public_methods",
	"prolog_method_block": "build_prolog_method_block",
	}


