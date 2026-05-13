# Changelog

Format:

- VERSION [YYYY-MM-DD]: Summary.

- 0.4.4 [2026-05-13]:
  - Modified README_PYPI.md
- 0.4.3 [2026-05-05]:
  - Clean handling of Windows line ending "\r\n".
- 0.4.2 [2026-05-03]:
  - Minor changes in packaging;
- 0.4.1 [2026-05-03]:
  - Minor changes in packaging; prepare for PyPI.
- 0.4.0 [2026-03-25]:
  - Refactoring "Definitions": Labels are now CSV-lists of identifiers.
- 0.3.0 [2026-03-14]:
  - Added handling for bullet list markers (lines starting with "-", "+", or "*")
    in the `highlight_line` method, treating them as keywords for syntax highlighting.
- 0.2.0 [2026-03-10]:
  - Added comprehensive comments and documentation to the code,
    explaining the purpose and functionality of each method and
    section of the lexer. This includes detailed descriptions
    of the parameters, return values, and potential exceptions
    for each method, as well as explanations of the regular
    expressions used for tokenization.
  - Careful handling of edge cases, such as docstrings that do not
    conform to the expected structure or contain mixed indentation,
    to ensure that the lexer behaves robustly in a variety of scenarios.
- 0.1.0 [2026-03-05]:
  - Versioning starts now.
