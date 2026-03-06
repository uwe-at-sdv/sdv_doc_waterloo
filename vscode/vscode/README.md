# VS Code Minimal Waterloo Highlighting

This folder contains a minimal extension that injects one rule into Python highlighting.

## Test

Run VS Code with this extension loaded from source:

```bash
code --extensionDevelopmentPath=/server/devel/sdv/privat/uwe/source/sdv_doc_waterloo/ide-plugins/vscode
```

In VS Code, open a Python file with Waterloo docstrings and run:

- `Developer: Inspect Editor Tokens and Scopes`

The words `Preamble`, `Contract`, and `Definitions` before `:` should get the scope:

- `keyword.other.waterloo.section`
