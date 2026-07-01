# Python-Waterloo Lexer

_BADGES_

The `python-waterloo-lexer` package provides a Pygments lexer for Python
files that contain Waterloo docstrings.

The Waterloo Docstrings project defines a structured docstring format with explicit section semantics,
normativity rules, and multiple render targets. The project is designed so that
the same source docstring can be consumed by humans, LLM-assisted tooling, and
renderers without losing structural meaning. This lexer provides syntax
highlighting that preserves those conventions in editors, terminals, and
preview tools.

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

## Source repository

Development happens in the Waterloo repository:

- <https://github.com/uwe-at-sdv/sdv_doc_waterloo>

The repository also contains related tooling, documentation, and editor
integrations for Waterloo docstrings.

## Preview

<picture>
  <img src="https://raw.githubusercontent.com/uwe-at-sdv/sdv_doc_waterloo/ide-plugins/pygments/img/screenshot_sphinx_pygments_wtrl.png" alt="ExtensionPreview">
</picture>
