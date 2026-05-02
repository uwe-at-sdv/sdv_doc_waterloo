# Waterloo Docstrings for VS Code

VS Code extension for Waterloo docstrings in Python.

This package provides:

- Waterloo syntax highlighting (TextMate injection into `source.python`)
- context menu commands for docstring generation and validation
- Python backend bridge used by the extension commands

## Clone the correct branch

The plugin sources live on branch `ide-plugins`. If you want to work from a
fresh checkout, clone that branch explicitly:

```bash
git clone --branch ide-plugins --single-branch \
  git@github.com:uwe-at-sdv/sdv_doc_waterloo.git
cd sdv_doc_waterloo/vscode
```

## Build VSIX

From this directory:

```bash
npx @vscode/vsce package
```

This creates a file like:

```text
waterloo-docstrings-<version>.vsix
```

## Install VSIX

From this directory:

```bash
code --install-extension ./waterloo-docstrings-<version>.vsix --force
```

Uninstall:

```bash
code --uninstall-extension local.waterloo-docstrings
```

## Run from source

For quick local testing without packaging a VSIX:

```bash
code --extensionDevelopmentPath="$(pwd)"
```

Then open a Python file and use:

- right-click editor context menu -> `Waterloo`
- or Command Palette commands starting with `Waterloo:`

This launches an Extension Development Host and loads the extension directly
from the source tree.

## Available Commands

- `Waterloo: Generate Minimal Docstring`
- `Waterloo: Generate Full Docstring`
- `Waterloo: Validate Docstring`

The context menu appears for Python when the backend is available and the current line matches a supported location (`def`, `class`, or module docstring position).

## Configuration

Extension setting:

- `waterloo.showSuccessNotifications` (default: `false`)

If set to `true`, successful operations show VS Code information messages.

## What the VSIX contains

The VSIX bundles both major parts of this extension:

- Waterloo syntax highlighting via TextMate grammar injection
- editor commands for docstring generation and validation

## Files

- `extension.js` - VS Code entry point and UI wiring
- `extension_waterloo_commands.py` - backend command dispatcher
- `funcdef_parser.py` - parser helpers for function/class headers
- `syntaxes/waterloo.injection.tmLanguage.json` - TextMate grammar
- `tools/select_grammar.py` - switch stable/experimental grammar variants

## Notes

- This package is licensed under `BSD-3-Clause`.
- Tested against VS Code engine constraint from `package.json` (`^1.80.0`).
- Before publishing to a public registry, update `repository.url` in `package.json`.
