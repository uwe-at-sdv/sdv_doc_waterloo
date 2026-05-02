# Python-Waterloo Lexer (Pygments)

This folder contains a custom lexer for Python files with Waterloo docstrings.

## Quick test (no install)

```bash
pygmentize -x \
  -l package_ide-plugins/pygments/python_waterloo_lexer.py:PythonWaterlooLexer \
  -f terminal16m \
  doc/examples/test_docitem_function_full.py
```

## Install from a local checkout

If you have cloned the repository, install the lexer package from this folder:

```bash
pip install "$REPO/package_ide-plugins/pygments"
```

If you are already in the repository root, this also works:

```bash
pip install ./package_ide-plugins/pygments
```

For development, an editable install can be convenient:

```bash
pip install -e ./package_ide-plugins/pygments
```

## Install directly from Git

If the repository is reachable by `pip`, the package can also be installed
directly from a Git URL:

```bash
pip install "git+URL#subdirectory=package_ide-plugins/pygments"
```

Replace `URL` with the repository URL, for example an HTTPS or SSH Git URL.

## Use after installation

The lexer class defines `aliases = ["python-waterloo"]`.
After installation, you can use:

```bash
pygmentize -l python-waterloo -f terminal16m <file.py>
```
