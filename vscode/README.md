# Waterloo Docstrings for VS Code

![Version](https://img.shields.io/badge/version-0.1.9-blue)

VS Code Marketplace: ready

VS Code extension for Waterloo docstrings in Python.

This extension provides:

- Waterloo syntax highlighting for Python docstrings
- context menu commands for docstring generation
- context menu commands for docstring validation

## Features

The extension contributes the following commands:

- `Waterloo: Generate Minimal Docstring`
- `Waterloo: Generate Full Docstring`
- `Waterloo: Validate Docstring`

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
   - `Validate Docstring`

If generation is selected, a docstring template is inserted below the current
definition. If validation is selected, the extension reports whether the
docstring is valid.

The same commands are also available from the Command Palette under names
starting with `Waterloo:`.

## Configuration

The extension defines the following setting:

- `waterloo.showSuccessNotifications` (default: `false`)

If enabled, successful Waterloo operations show VS Code information messages.

## Included components

The extension bundles both major parts of the Waterloo tooling for VS Code:

- syntax highlighting via TextMate grammar injection
- editor commands for docstring generation and validation

## Compatibility

- License: `BSD-3-Clause`
- VS Code engine constraint: `^1.80.0`
