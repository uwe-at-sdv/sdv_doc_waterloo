# Python-Waterloo Lexer

`python-waterloo-lexer` is a Pygments lexer for Python files that contain
Waterloo docstrings.

It can be used with `pygmentize` and other tools that load Pygments lexers via
entry points.

## Installation

```bash
pip install python-waterloo-lexer
```

## Quick test

After installation, the lexer is available under the alias
`python-waterloo`.

```bash
pygmentize -l python-waterloo -f terminal16m <file.py>
```

You can also check whether Pygments lists the lexer:

```bash
pygmentize -L lexers | grep -i waterloo || true
```

## Project repository

Development happens in the Waterloo repository:

- <https://github.com/uwe-at-sdv/sdv_doc_waterloo>

The repository also contains related tooling, documentation, and editor
integrations for Waterloo docstrings.

