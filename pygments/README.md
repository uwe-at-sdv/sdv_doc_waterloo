# Python-Waterloo Lexer (Pygments)

This folder contains a custom lexer for Python files with Waterloo docstrings.

## Quick test (no install)

```bash
pygmentize -x \
  -l package_ide-plugins/pygmentize/python_waterloo_lexer.py:PythonWaterlooLexer \
  -f terminal16m \
  doc/examples/test_docitem_function_full.py
```

## Optional alias after installation

The lexer class defines `aliases = ["python-waterloo"]`.
If you later package/install it as a Pygments plugin, you can use:

```bash
pygmentize -l python-waterloo -f terminal16m <file.py>
```
