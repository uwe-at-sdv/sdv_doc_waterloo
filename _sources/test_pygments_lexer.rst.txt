.. _test_pygments_lexer:

Test: Pygments lexer showcase
=============================

This section is informative.

In this chapter we exercise the Waterloo-aware Pygments lexer on a compact
but deliberately varied test file. The example includes ordinary Waterloo
docstrings, edge cases that stress indentation and markup handling, and a few
intentionally wrong inputs so the lexer behavior can be inspected side by side.
The goal is to show what the lexer highlights, what it leaves untouched, and
where the parser should continue to fail cleanly.


.. literalinclude:: ../examples/pytest_syntaxhl_showcase.py
	:language: python
