# Python-Waterloo Lexer (Pygments)

This folder contains a custom Pygments lexer for Python files with Waterloo docstrings.

> **Branch note (`ide-plugins`)**
>
> The Pygments lexer package lives on the `ide-plugins` branch. Installation from Git must
> reference `@ide-plugins` (see below). General repository documentation is in `@main/README.md`.

## Prerequisites

- Python >= 3.10
- `pip`
- `pygmentize` (provided by the `Pygments` package)

## Clone the correct branch

The plugin sources live on branch `ide-plugins`. If you want to work from a
fresh checkout, clone that branch explicitly:

HTTPS:
```bash
git clone --branch ide-plugins --single-branch https://github.com/uwe-at-sdv/sdv_doc_waterloo.git
cd sdv_doc_waterloo
```
SSH:
```bash
git clone --branch ide-plugins --single-branch git+ssh://git@github.com/uwe-at-sdv/sdv_doc_waterloo.git
cd sdv_doc_waterloo
```

## Quick test (no install)

Run `pygmentize` directly against the lexer source file (no packaging/install needed):

Dark terminal theme:
```bash
pygmentize -x \
  -l pygments/python_waterloo_lexer.py:PythonWaterlooLexer -f terminal16m -O style=monokai \
  examples-python/example_function_full.py
```
Light terminal theme:
```bash
pygmentize -x \
  -l pygments/python_waterloo_lexer.py:PythonWaterlooLexer -f terminal16m -O style=friendly \
  examples-python/example_function_full.py
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

### Sanity check (after install)

The lexer should be discoverable by its alias:

```bash
pygmentize -l python-waterloo -f terminal16m examples-python/example_function_full.py
```

Tip: You can also check whether Pygments lists the lexer:

```bash
pygmentize -L lexers | grep -i waterloo || true
```

## Install directly from Git

If the repository is reachable by `pip`, the package can also be installed
directly from a Git URL.

**Important:** The `@ide-plugins` ref is required because this package is maintained on that branch.

HTTPS:
```bash
pip install "git+https://github.com/uwe-at-sdv/sdv_doc_waterloo.git@ide-plugins#subdirectory=pygments"
```
SSH:
```bash
pip install "git+ssh://git@github.com/uwe-at-sdv/sdv_doc_waterloo.git@ide-plugins#subdirectory=pygments"
```
