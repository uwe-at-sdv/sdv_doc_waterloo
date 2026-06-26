# Waterloo Docstrings for VS Code

_BADGES_

> [!NOTE]
> This extension is currently in a test phase.
>
> Functionality, command names, schema integration and generated
> docstring structures may still change.
>
> The extension is currently published primarily for development,
> testing and interoperability experiments with the Waterloo backend.
>
> Installation is currently recommended mainly for testers and
> developers already working with Waterloo docstrings.

<picture>
  <source srcset="https://minifl.de/sdv_doc_waterloo/img/screencast_final.gif" type="image/gif">
  <img src="https://minifl.de/sdv_doc_waterloo/img/screencast_final_fallback.png" alt="ExtensionPreview">
</picture>

The Waterloo Docstrings project defines a structured docstring format with
explicit section semantics, normativity rules, and multiple render targets.
The same source docstring can be consumed by humans, LLM-assisted tooling, and
renderers without losing structural meaning.

This extension adds VS Code support for Waterloo docstrings in Python. It
provides syntax highlighting, docstring generation and validation commands, and
an MCP server that can help Copilot and other MCP clients inspect Waterloo
docstrings more effectively.

## Source and release

The extension source and release workflow are tied to the GitHub repository:

- `https://github.com/uwe-at-sdv/sdv_doc_waterloo`

This GitHub repository is the public source of truth for the extension and is
the repository used for the Trusted Publisher workflow on the Marketplace.

## Requirements

To use the extension, install the Waterloo Python package that provides the
backend and shared schema data:

- `sdv.doc.waterloo`

Install it from PyPI:

```bash
pip install sdv-doc-waterloo
```

If you want the Sphinx extension and related extras, install:

```bash
pip install "sdv-doc-waterloo[sphinx]"
```

The package can also be installed from the GitHub repository during active
development, but PyPI is the default release channel now.

This extension provides:

- Waterloo syntax highlighting for Python docstrings
- context menu support for docstring generation
- context menu support for docstring validation
- an MCP server for Copilot and other MCP clients

## Features

The extension contributes the following commands:

- `Waterloo: Generate Minimal Docstring`
- `Waterloo: Generate Full Docstring`
- `Waterloo: Save and Validate Docstring`

In Python files, these commands are also available from the editor context
menu under:

- `Waterloo`

The menu appears when the current line is a supported location, such as:

- a function definition
- a class definition
- a module docstring position

## Quick tutorial

1. Open a Python file that contains a function or class definition.
2. Place the cursor on the corresponding `def` or `class` line.
3. Open the editor context menu and select `Waterloo`.
4. Choose one of the following actions:
   - `Generate Minimal Docstring`
   - `Generate Full Docstring`
   - `Save and Validate Docstring`

If generation is selected, a docstring template is inserted below the current
definition. If validation is selected, the extension reports whether the
docstring is valid.

The same commands are also available from the Command Palette under names
starting with `Waterloo:`.

## Configuration

The extension defines the following setting:

- `waterloo.showSuccessNotifications` (default: `false`)

If enabled, successful Waterloo operations show VS Code information messages.

## Known issues

No known issues at the moment. Please report problems on GitHub.

## Included components

The extension bundles both major parts of the Waterloo tooling for VS Code:

- syntax highlighting via TextMate grammar injection
- editor commands for docstring generation and validation

## Compatibility

- License: `BSD-2-Clause`
- VS Code engine constraint: `^1.115.0`
