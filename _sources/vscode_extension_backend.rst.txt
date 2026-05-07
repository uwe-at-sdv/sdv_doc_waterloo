VSCode Extension Backend
========================

This chapter is informative.

It documents the JSON protocol currently used between the VSCode editor
integration and the Python backend. The material is primarily intended
for extension developers and for debugging integration issues.


JSON protocol shape
----------------------------------------------

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
	    "$schema": "https://sci-d-vis.com/schema/wtrl-tracer-json-0.0.2.schema.json",
	    "...": "full tracer document"
	  }
	}

The field :wtrl_attr:`diagnostics` is always included for :wtrl_attr:`ok` = :wtrl_value:`false`.
For successful calls, the client may request full diagnostics by setting
:wtrl_attr:`include_diagnostics` = :wtrl_value:`true` in the request.

Extension command examples
--------------------------

Common request fields (non-:wtrl_value:`ping`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~

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
		"file":wtrl.__file__,
		"version":wtrl.__version__,
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
	    "$schema": "https://sci-d-vis.com/schema/wtrl-tracer-json-0.0.2.schema.json",
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
	    "$schema": "https://sci-d-vis.com/schema/wtrl-tracer-json-0.0.2.schema.json",
	    "__WTRL_ERROR__": [
	      {
	        "rule-id": "XTNSN-012"
	      }
	    ]
	  }
	}
