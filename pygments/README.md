# Python-Waterloo Lexer (Pygments)

This folder contains a custom lexer for Python files with Waterloo docstrings.

## Clone the correct branch

The plugin sources live on branch `ide-plugins`. If you want to work from a
fresh checkout, clone that branch explicitly:

```bash
git clone --branch ide-plugins --single-branch \
  git@github.com:uwe-at-sdv/sdv_doc_waterloo.git
cd sdv_doc_waterloo
```

## Quick test (no install)

```bash
pygmentize -x \
  -l pygments/python_waterloo_lexer.py:PythonWaterlooLexer \
  -f terminal16m \
  doc/examples/test_docitem_function_full.py
```

## Install from a local checkout

If you have cloned the repository, install the lexer package from this folder:

```bash
pip install ./pygments
```

For development, an editable install can be convenient:

```bash
pip install -e ./pygments
```

## Install directly from Git

If the repository is reachable by `pip`, the package can also be installed
directly from a Git URL:

```bash
pip install "git+URL@ide-plugins#subdirectory=pygments"
```

Replace `URL` with the repository URL, for example an HTTPS or SSH Git URL.

## Use after installation

The lexer class defines `aliases = ["python-waterloo"]`.
After installation, you can use:

```bash
pygmentize -l python-waterloo -f terminal16m <file.py>
```
