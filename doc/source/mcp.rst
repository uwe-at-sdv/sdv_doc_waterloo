Model Context Protocol
======================

The Waterloo MCP-Server
-----------------------

The purpose of the MCP-server is to provide a simple, standardized way
for LLM-agents to access and query Waterloo documents in JSON format.
While the plain JSON document is already sufficient for many use cases,
the MCP server additionally enables efficient access to very large
documentation artifacts that would otherwise burden the agent's context window.
The MCP-server is implemented as a simple HTTP server that listens for JSON-RPC requests and responds
with JSON data. The server can be easily integrated with LLM-agents that support JSON-RPC.

Executable and configuration
----------------------------

There is a pre-defined configuration file for the MCP-server in the Waterloo package,
located at :wtrl_file:`etc/wtrl_mcp.http.toml`.
Once the Waterloo package is installed, the MCP-server can be started by running e.g. the following command in the terminal:

.. code-block:: bash

	wtrl_mcp --config etc/wtrl_mcp.http.toml

If the argument to :wtrl_cmd:`--config` is an absolute path, it is used as is.
If it is a relative path, :wtrl_cmd:`wtrl_mcp` first looks for the file relative
to the current working directory and then relative to the installed Waterloo
package root. Therefore the usual package-local configuration path is prefixed
with ``etc/``. If neither candidate exists, the server reports a clear
configuration error and exits.

Tools
-----

The MCP-server supports the following tools:

.. list-table::
	:header-rows: 1
	:widths: 24 76

	* - Tool name
	  - What the tool does
	* - :wtrl_cmd:`list_roots`
	  - List configured Waterloo data roots.
	* - :wtrl_cmd:`get_root`
	  - Read one configured Waterloo data root by ``root_id``.
	* - :wtrl_cmd:`get_object`
	  - Read one Waterloo object by ``qid`` from a configured root.
	* - :wtrl_cmd:`get_section`
	  - Read one stored section of one Waterloo object.
	* - :wtrl_cmd:`get_subsection`
	  - Read one stored subsection of one Waterloo object.
	* - :wtrl_cmd:`search_objects`
	  - Search Waterloo objects by expression and structural filters.
	* - :wtrl_cmd:`search_sections`
	  - Search Waterloo section and subsection labels by expression and structural filters.
	* - :wtrl_cmd:`search_text`
	  - Search Waterloo text content by terms and structural filters.
	* - :wtrl_cmd:`gen_docstring`
	  - Generate a Waterloo docstring template for a given profile, with optional signature, template mode, and indentation mode.

Typical agent workflow
----------------------

The lookup-oriented tools are meant to be used in a simple progression:

1. :wtrl_cmd:`list_roots` to discover available roots.
2. :wtrl_cmd:`search_objects` to find candidate objects and obtain stable ``root_id`` / ``qid`` pairs.
3. :wtrl_cmd:`get_section` or :wtrl_cmd:`get_subsection` to inspect the relevant contract, notes, or other structured sections.
4. :wtrl_cmd:`search_sections` when the agent wants to find section or subsection labels rather than object names.
5. :wtrl_cmd:`search_text` when the agent wants to search the actual content text with a small set of terms.

In practice this means that the agent can start with a vague name, narrow it
down to a canonical target, and then inspect the exact Waterloo text that
describes the object.


Using the MCP-server in VSCode
------------------------------

[Last tested with VSCode 1.115.0 on 2026-05-31]

With transport :wtrl_lit:`streamable-http`, the MCP-server is added to VSCode by:

	:wtrl_key:`Shift+Ctrl+P` and :wtrl_lit:`MCP: Open User Configuration`

The code to be added should look like

.. code-block:: json

	{
	    "servers": {
	    	"waterloo-docs": {
	        	"type": "http",
	        	"url": "http://127.0.0.1:13316/mcp"
	     	}
	    }
	}
	
where the :wtrl_attr:`url` is the URL of the MCP server. Use the host and port
from the running server configuration, and make sure the URL matches the
configured :wtrl_lit:`streamable-http` endpoint. The MCP server must be
running and accessible at that URL for the integration to work. As a smoke
test, open the MCP panel in VSCode and see whether it connects successfully.
Then ask Copilot to run :wtrl_cmd:`list_roots` and check whether it returns the
expected list of documents.


Server error messages
---------------------

This section is normative.

The MCP implementation currently returns textual tool errors through the
FastMCP transport path. The Waterloo-specific error payload classes are kept
as a draft in :wtrl_file:`mcp/wtrl_error.py`, but the wire-level structure is
not normative yet.

The current lookup-oriented rule family is:

* [MCPS-001] -- unknown or missing ``root_id``.
* [MCPS-002] -- unknown ``qid``.
* [MCPS-003] -- unknown section name.
* [MCPS-004] -- unknown subsection name.
* [MCPS-005] -- root document too large for the ``get_root`` guardrail.

The current implementation already prefixes tool error messages with these
rule labels. A later version may map them more directly to structured
JSON-RPC error payloads if the MCP SDK exposes a better hook for that.
