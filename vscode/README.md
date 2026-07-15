# Waterloo Docstrings for VS Code

![License](https://img.shields.io/badge/license-BSD--2--Clause-blue)
![Version](https://img.shields.io/badge/version-0.3.0-orange)
[![GitHub](https://img.shields.io/badge/GitHub-sdv_doc_waterloo-181717?logo=github)](https://github.com/uwe-at-sdv/sdv_doc_waterloo)

VS Code extension for Waterloo docstrings in Python.

This package provides:

- Waterloo syntax highlighting for roles such as `class`, `pkg`, `url`, and
  `var_type` (TextMate injection into `source.python`; `var_type` is rendered
  as a variable/type pair)
- context menu commands for docstring generation and validation
- Python backend bridge used by the extension commands
- an MCP server under `sdv.doc.waterloo.mcp` in the `main` branch at
  `src/sdv/doc/waterloo/mcp`, which can help Copilot and other MCP clients
  inspect Waterloo docstrings

## Preview

<picture>
  <source srcset="https://raw.githubusercontent.com/uwe-at-sdv/sdv_doc_waterloo/ide-plugins/vscode/img/screencast_final.gif" type="image/gif">
  <img src="https://raw.githubusercontent.com/uwe-at-sdv/sdv_doc_waterloo/ide-plugins/vscode/img/screencast_final_fallback.png" alt="ExtensionPreview">
</picture>

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

## Clone the correct branch

The plugin sources live on branch `ide-plugins`. If you want to work from a
fresh checkout, clone that branch explicitly:

HTTPS:
```bash
git clone --branch ide-plugins --single-branch https://github.com/uwe-at-sdv/sdv_doc_waterloo.git
cd sdv_doc_waterloo/vscode
```
SSH:
```bash
git clone --branch ide-plugins --single-branch git@github.com:uwe-at-sdv/sdv_doc_waterloo.git
cd sdv_doc_waterloo/vscode
```

## Build VSIX

From this directory:

```bash
npm install --save-dev @vscode/vsce
./package_vsix.sh
```

This creates a file like:

```text
waterloo-docstrings-<version>.vsix
```

The script updates the generated VSCode package files, but it does not stage,
commit, or push. Use `publish.sh` for the release workflow, or stage the
changes manually when building this branch directly.

The build requires a local `vsce` installation on `PATH` or in
`node_modules/.bin`.

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

For quick local testing without packaging a VSIX, start VS Code from this
directory:

```bash
code --extensionDevelopmentPath="$(pwd)"
```

This launches an Extension Development Host and loads the extension directly
from the source tree.

## Available Commands

- `Waterloo: Generate Minimal Docstring`
- `Waterloo: Generate Full Docstring`
- `Waterloo: Save and Validate Docstring`
- `Waterloo: Save and Check Coverage of Docstring`

The context menu appears for Python when the backend is available and the current line matches a supported location (`def`, `class`, or module docstring position).

## Quick tutorial

After launching the Extension Development Host, open the example file from the
repository root, for example in a separate terminal:

```bash
code examples-python/example_function_full.py
```

Then try the following:

1. Place the cursor on the function header `def test()`.
2. Open the editor context menu and select `Waterloo -> Save and Validate Docstring`.
3. A confirmation message such as `Waterloo: Validation passed for example_function_full.test.` should appear near the bottom of the editor window.
4. Delete the docstring of function `test`.
5. Place the cursor again on the function header `def test()`.
6. Open the editor context menu and select `Waterloo -> Generate Full Docstring`.
7. A docstring template should appear directly below the function header.

The same commands are also available from the Command Palette under names
starting with `Waterloo:`.

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

## Notes

- This package is licensed under `BSD-2-Clause`.
- Tested against VS Code engine constraint from `package.json` (`^1.115.0`).
- Before publishing to a public registry, update `repository.url` in `package.json`.
