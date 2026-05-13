# Waterloo Docstrings for VS Code - TEST PHASE, DO NOT INSTALL

![Version](https://img.shields.io/badge/version-0.1.18-blue)
![Source](https://img.shields.io/badge/source-GitHub-181717?logo=github)
![Marketplace](https://img.shields.io/badge/VS%20Code-Marketplace-brightgreen)

![ExtensionPreview](https://minifl.de/sdv_doc_waterloo/img/screencast_final_fallback.png)

[Animated demo GIF](https://minifl.de/sdv_doc_waterloo/img/screencast_final.gif)

VS Code extension for Waterloo docstrings in Python.

## Source and release

The extension source and release workflow are tied to the GitHub repository:

- `https://github.com/uwe-at-sdv/sdv_doc_waterloo`

This GitHub presence is the public source of truth for the extension and is
the repository used for the Trusted Publisher workflow on the Marketplace.

## Requirements

To use the extension, install the Waterloo Python package that provides the
backend and shared schema data:

- `sdv.doc.waterloo`

You can install it from the GitHub repository or, once the public release is
available, from PyPI.

This extension provides:

- Waterloo syntax highlighting for Python docstrings
- context menu commands for docstring generation
- context menu commands for docstring validation

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

- License: `BSD-3-Clause`
- VS Code engine constraint: `^1.80.0`
