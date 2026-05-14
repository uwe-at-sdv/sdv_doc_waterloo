# Python-Waterloo Lexer

![Status](https://img.shields.io/badge/status-pre--release-orange)
![License](https://img.shields.io/badge/license-BSD--2--Clause-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

`python-waterloo-lexer` is a Pygments lexer for Python files that contain
Waterloo docstrings.

It can be used with `pygmentize` and other tools that load Pygments lexers via
entry points.

## What it provides

- a `python-waterloo` Pygments lexer alias
- syntax highlighting for Python files with Waterloo docstrings
- installation via PyPI, local checkout, or Git URL

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

## Terminal viewer

For a quick terminal preview, a `less` alias can be handy:

```bash
alias lessh='LESSOPEN="| pygmentize -O style=monokai %s" less -M -R'
```

Then open files with:

```bash
lessh <file.py>
```

## Project repository

Development happens in the Waterloo repository:

- <https://github.com/uwe-at-sdv/sdv_doc_waterloo>

The repository also contains related tooling, documentation, and editor
integrations for Waterloo docstrings.
