.. _test_pygments_lexer:

Test: Inline markup
===================

Pygments
--------

This section is informative.

In this chapter we exercise the Waterloo-aware Pygments lexer on a compact
but deliberately varied test file. The example includes ordinary Waterloo
docstrings, edge cases that stress indentation and markup handling, and a few
intentionally wrong inputs so the lexer behavior can be inspected side by side.
The goal is to show what the lexer highlights, what it leaves untouched, and
where the parser should continue to fail cleanly.


.. literalinclude:: ../examples/pytest_syntaxhl_showcase.py
	:language: python
	:tab-width: 4


Sphinx
------

This section is informative.

The module docstring intentionally contains a complete list of roles so that
the Sphinx renderer can be evaluated in the same spirit as the lexer showcase,
but from the rendering side. The :wtrl_label:`Notes` section contains markup
examples that are stylistically similar to the interactive HTML output, which
makes it possible to compare the rendered appearance directly. Unlike the
Python lexer, whose appearance depends on the selected theme, this chapter
lets us inspect the rendering consistency in a more controlled way.

.. wtrl_autodoc_module:: sdv.doc.waterloo.docitem_helper
