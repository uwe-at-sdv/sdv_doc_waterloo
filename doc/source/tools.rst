Tools
=====

This section is informative. Subsections are informative unless explicitly stated otherwise.

The reference implementation provides the command-line tool
:wtrl_cmd:`waterlint`. The error codes listed below are used by this tool.
These codes are specific to the reference implementation and do not
form part of the normative Waterloo language specification.


Error code structure
--------------------

The general structure and stability requirements for rule IDs are specified
normatively in chapter :ref:`section_meta`.
The error codes listed in this chapter follow the same basic pattern:
a mnemonic uppercase ASCII prefix, a hyphenation character, and a
three-digit numeric identifier.

Within the reference implementation, these error codes are intended to be
treated as stable external references for tooling, diagnostics, and
documentation.


:wtrl_cmd:`waterlint` error codes
---------------------------------

This section is normative.

.. rubric:: General tool errors

* [TOOL-001] -- Cannot resolve an object passed via option :wtrl_opt:`--obj`.
* [TOOL-002] -- Option :wtrl_opt:`--subsection` was given without :wtrl_opt:`--section`.
* [TOOL-003] -- The object resolved via option :wtrl_opt:`--obj` has no docstring.
* [TOOL-004] -- The section requested by :wtrl_opt:`--section` was not found during extraction.
* [TOOL-005] -- The subsection requested by :wtrl_opt:`--subsection` was not found during extraction.
* [TOOL-006] -- The input docstring cannot be parsed for extraction.
* [TOOL-007] -- The input docstring is not valid for the requested extraction operation.
* [TOOL-008] -- Invalid option combination or target selection for a generation command, for example raw output requested for more than one target object.
* [TOOL-800] -- Unspecified runtime error during analysis.
  This code is used when an unexpected exception escapes the validation process.
  The tracer diagnostic output should provide sufficient detail to identify
  the underlying cause.

.. rubric:: Commands explain-section and explain-subsection

* [XPLN-001] -- The :wtrl_cmd:`explain-section` command received a missing, invalid, or unknown section label/profile combination.
* [XPLN-002] -- The :wtrl_cmd:`explain-subsection` command received a missing, invalid, or unknown subsection label/profile combination.
* [XPLN-003] -- The :wtrl_cmd:`explain-subsection` command requires a fully qualified label in the form :wtrl_lit:`SECTION.SUBSECTION`.

The :wtrl_cmd:`waterlint explain-section` and :wtrl_cmd:`waterlint explain-subsection`
commands report argument and lookup failures through the tracer and honor
:wtrl_opt:`--out-diag` and :wtrl_opt:`--out-diag-json` like the other command-line tools.

.. rubric:: JSON processing

* [JSCH-000] -- Unspecified catch-all error during JSON processing.
* [JSCH-002] -- Cannot open the input JSON file for validation.
* [JSCH-003] -- Cannot determine the applicable schema from the input JSON file.
* [JSCH-004] -- Input is not valid JSON.
* [JSCH-005] -- Validation against the JSON Schema failed.
* [JSCH-006] -- Entry :wtrl_attr:`__WTRL_OBJECTS__.<QID>.examples` contains an invalid pointer, a missing target example, or an invalid list shape.
* [JSCH-007] -- Entry :wtrl_attr:`__WTRL_EXAMPLES__.<ID>.referenced_by` contains an invalid value or an unknown object identifier.
* [JSCH-008] -- Back-reference mismatch: an object points to an example, but the example does not list that object in :wtrl_attr:`referenced_by`.
* [JSCH-009] -- Forward-reference mismatch: an example lists an object in :wtrl_attr:`referenced_by`, but the object does not point back via :wtrl_attr:`examples`.

* [JSCH-700] -- Unspecified error during JSON rendering.
* [JSCH-800] -- Unspecified JSON schema exception.

.. rubric:: Example mapping (add-example-json)

* [AXMPL-000] -- Unspecified catch-all error during example mapping.
* [AXMPL-001] -- Invalid JSON envelope structure for input or example entries.
* [AXMPL-002] -- Mapping contains an unknown or invalid object identifier.
* [AXMPL-003] -- Mapping contains an invalid list shape or non-string example path.
* [AXMPL-004] -- Example file path, file access, base directory, or UTF-8 decoding failed.
* [AXMPL-005] -- Input or mapping file is not valid JSON.
* [AXMPL-006] -- Mapping JSON failed schema validation or schema auto-detection.

.. _rendering_html:

.. rubric:: Rendering HTML (render-html5)

* [RHTM-001] -- General error while rendering HTML5.
* [RHTM-002] -- Invalid render-html5 output arguments or output directory state.
* [RHTM-003] -- Input JSON documents cannot be merged (inconsistent metadata, missing structure, collisions).
* [RHTM-004] -- CSS asset loading failed (built-in CSS, user-provided :wtrl_opt:`--css`, or user-provided :wtrl_opt:`--additional-css`).
* [RHTM-005] -- HTML assembly or output file writing failed.
* [RHTM-006] -- Optional preprocessing failed (currently: dropping ``Preamble`` via :wtrl_opt:`--no-render-preamble`).
* [RHTM-007] -- Custom header fragment given via :wtrl_opt:`--header-html` cannot be read.
* [RHTM-008] -- Custom header fragment given via :wtrl_opt:`--header-html` does not contain the required element :wtrl_value:`#wtrl-title`.
* [RHTM-009] -- Custom header fragment given via :wtrl_opt:`--header-html` cannot be embedded safely into the generated HTML document.
  This includes active content such as ``<script>`` and disallowed document-level elements such as
  :wtrl_tag:`html`, :wtrl_tag:`head`, :wtrl_tag:`body`, and :wtrl_tag:`main`.

.. _rendering_docker:

.. rubric:: Rendering Docker build artifacts (render-docker)

The :wtrl_cmd:`waterlint render-docker` command renders a Dockerfile together
with companion helper scripts for building and, in non-baking mode, launching
the resulting container. The generated artefacts are intended to make the
deployment of a Waterloo MCP server configuration repeatable and easy to
inspect.

* [DCKR-000] -- The command-line input is incomplete or invalid, for example because :wtrl_opt:`--in` or :wtrl_opt:`--out` is missing.
* [DCKR-001] -- The parsed configuration has an invalid structure, an unsupported transport, or an invalid root or logging field type.
* [DCKR-002] -- A referenced root file or logging configuration file does not exist.
* [DCKR-003] -- The input TOML file does not exist or could not be loaded.
* [DCKR-999] -- An unspecified error occurred while rendering Docker build artifacts.



Extension error codes
---------------------

This section is normative.

* [XTNSN-001] -- Invalid JSON input
* [XTNSN-002] -- Unsupported command
* [XTNSN-003] -- Unsupported protocol
* [XTNSN-004] -- Unsupported subcommand
* [XTNSN-005] -- JSON input type mismatch
* [XTNSN-006] -- Source fragment mismatch
* [XTNSN-007] -- Error parsing source fragment
* [XTNSN-008] -- Error parsing module file
* [XTNSN-009] -- Cannot resolve source fragment
* [XTNSN-010] -- No source file given
* [XTNSN-011] -- Line number not specified properly
* [XTNSN-012] -- Cannot qualify documented object
* [XTNSN-013] -- The selected object has no docstring.

The JSON protocol used by the VSCode editor integration is documented
separately in chapter :ref:`vscode_extension_backend`.

.. _vscode_extension_backend:

Reference: VSCode Extension Backend
----------------------------------------------------------------

This chapter is informative.

It documents the JSON protocol currently used between the VSCode editor
integration and the Python backend. The material is primarily intended
for extension developers and for debugging integration issues.


JSON protocol shape
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Python backend used by the VSCode extension returns a unified
JSON envelope for all commands.

Minimal response shape:

.. code-block:: json

	{
	  "ok": true,
	  "command": "ping",
	  "version": 1,
	  "data": { "...": "command-specific payload" },
	  "diagnostics_summary": {
	    "debug": 0,
	    "info": 0,
	    "warning": 0,
	    "error": 0
	  }
	}

Error response shape:

.. code-block:: json

	{
	  "ok": false,
	  "command": "generate_minimal_docstring_to_tmp",
	  "version": 1,
	  "error": "Unsupported subcommand",
	  "diagnostics_summary": {
	    "debug": 0,
	    "info": 0,
	    "warning": 0,
	    "error": 1
	  },
	  "diagnostics": {
	    "$schema": "https://sci-d-vis.com/schema/wtrl-tracer-json-0.1.0.schema.json",
	    "...": "full tracer document"
	  }
	}

The field :wtrl_attr:`diagnostics` is always included for :wtrl_attr:`ok` = :wtrl_value:`false`.
For successful calls, the client may request full diagnostics by setting
:wtrl_attr:`include_diagnostics` = :wtrl_value:`true` in the request.

Extension command examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Common request fields (non-:wtrl_value:`ping`)
................................................................

The following fields are accepted for all non-:wtrl_value:`ping` commands:

.. code-block:: json

	{
	  "version": 1,
	  "command": "<command-name>",
	  "kind": "module|class|function|method",
	  "source_fragment": "<python header fragment or empty string>",
	  "source_file": "<absolute or relative file path>",
	  "line": 0,
	  "include_diagnostics": false
	}

Command-specific requirements:

* :wtrl_value:`generate_minimal_docstring_to_tmp` and :wtrl_value:`generate_full_docstring_to_tmp`
	- Required: :wtrl_attr:`version`, :wtrl_attr:`command`, :wtrl_attr:`kind`, :wtrl_attr:`source_fragment`
	- Optional/ignored: :wtrl_attr:`source_file`, :wtrl_attr:`line`
* :wtrl_value:`validate_docstring`
	- Required: :wtrl_attr:`version`, :wtrl_attr:`command`, :wtrl_attr:`kind`, :wtrl_attr:`source_fragment`,
	  :wtrl_attr:`source_file`, :wtrl_attr:`line`
	- Optional: :wtrl_attr:`include_diagnostics`

Command :wtrl_value:`ping`
................................................................

Request:

.. code-block:: json

	{
	  "version": 1,
	  "command": "ping"
	}

Successful response:

.. code-block:: json

	{
	  "ok": true,
	  "command": "ping",
	  "version": 1,
	  "data": {
	    "ok": true,
	    "command": "pong",
	    "version": 1,
	    "capabilities": [
	      "generateMinimalDocstring",
	      "generateFullDocstring",
	      "validateDocstring"
	    ],
	    "sdv_doc_waterloo": {
		"file":"/path/to/sdv/doc/waterloo/module.py",
		"version":"1.2.3",
	    }
	  },
	  "diagnostics_summary": {
	    "debug": 0,
	    "info": 0,
	    "warning": 0,
	    "error": 0
	  }
	}

Command :wtrl_value:`generate_minimal_docstring_to_tmp`
................................................................

Request (function):

.. code-block:: json

	{
	  "version": 1,
	  "command": "generate_minimal_docstring_to_tmp",
	  "kind": "function",
	  "source_fragment": "def f(x: int) -> int: pass"
	}

Successful response:

.. code-block:: json

	{
	  "ok": true,
	  "command": "generate_minimal_docstring_to_tmp",
	  "version": 1,
	  "data": {
	    "kind": "function",
	    "tmp_file": "<tempdir>/waterloo-docstrings/waterloo-docstring-abc123.txt"
	  },
	  "diagnostics_summary": {
	    "debug": 0,
	    "info": 0,
	    "warning": 0,
	    "error": 0
	  }
	}

Command :wtrl_value:`generate_full_docstring_to_tmp`
................................................................

Request (method):

.. code-block:: json

	{
	  "version": 1,
	  "command": "generate_full_docstring_to_tmp",
	  "kind": "method",
	  "source_fragment": "def f(self, x: int) -> None: pass"
	}

Successful response:

.. code-block:: json

	{
	  "ok": true,
	  "command": "generate_full_docstring_to_tmp",
	  "version": 1,
	  "data": {
	    "kind": "method",
	    "tmp_file": "<tempdir>/waterloo-docstrings/waterloo-docstring-xyz456.txt"
	  },
	  "diagnostics_summary": {
	    "debug": 0,
	    "info": 0,
	    "warning": 0,
	    "error": 0
	  }
	}

Command :wtrl_value:`validate_docstring`
................................................................

Request (function):

.. code-block:: json

	{
	  "version": 1,
	  "command": "validate_docstring",
	  "kind": "function",
	  "source_fragment": "def spam() -> None: pass",
	  "source_file": "doc/examples/test_docitem_function_minimal.py",
	  "line": 2,
	  "include_diagnostics": true
	}

Successful response:

.. code-block:: json

	{
	  "ok": true,
	  "command": "validate_docstring",
	  "version": 1,
	  "data": {
	    "kind": "function",
	    "qualified_identifier": "test_docitem_function_minimal.spam"
	  },
	  "diagnostics_summary": {
	    "debug": 0,
	    "info": 1,
	    "warning": 0,
	    "error": 0
	  },
	  "diagnostics": {
	    "$schema": "https://sci-d-vis.com/schema/wtrl-tracer-json-0.1.0.schema.json",
	    "...": "full tracer document"
	  }
	}

Error response (shape):

.. code-block:: json

	{
	  "ok": false,
	  "command": "validate_docstring",
	  "version": 1,
	  "error": "Could not qualify documented object.",
	  "diagnostics_summary": {
	    "debug": 0,
	    "info": 0,
	    "warning": 0,
	    "error": 1
	  },
	  "diagnostics": {
	    "$schema": "https://sci-d-vis.com/schema/wtrl-tracer-json-0.1.0.schema.json",
	    "__WTRL_ERROR__": [
	      {
	        "rule-id": "XTNSN-012"
	      }
	    ]
	  }
	}
